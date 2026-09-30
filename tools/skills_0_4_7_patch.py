"""Derive SkyySkills/build_skyyskills_0.4.7.py from the LIVE generated SkyySkills/build_skyyskills_0.4.6.py (= the tools/deploy_set.py SET
pin; 0.4.6 was derived by tools/skills_0_4_6_patch.py from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run skills_0_4_5 or older
patches). Same style as skills_0_4_6_patch.py: rep(old, new) / cut(a, b, new) with asserted single anchors, newline-agnostic; 0.4.6
stays untouched and its CRLF line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_7_patch.py   then   python SkyySkills/build_skyyskills_0.4.7.py   (NO --deploy: coordinated deploy)

0.4.7 = THE VANILLA UI PASS for the three SkyySkills pages (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for
them to look and feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 7, 8c, 12, 13;
research/Skyy-UI-Inventory.md 5.20 + batch B3). LOOK-ONLY RESTYLE on the shared kit tools/skyyui.py (1.4):
  - the generated script imports skyyui as SUI and calls SUI.verify() before anything else (every vanilla value the pages use is
    proven against Assets.zip, read-only, at every build) and puts SUI.kit_id() into the ready log line;
  - one Python block (SKILLS PAGE BLOCK) builds the markup of SkillsPage (/skills and its Top 10 view), StatsPage and OverallPage from
    kit calls when the BUILD runs; the Java the kit emits gets a name (SK_*_JAVA / ST_*_JAVA / OV_*_JAVA) and is interpolated into the
    three build() f-strings as {..._JAVA} (the f-string recipe of tools/acc_0_4_5_patch.py; never re-parsed by Python, asserted
    verbatim). The three build() methods keep every statement of 0.4.6 that is not markup word for word (asserted below: data reads,
    the class-row / legacy / max-level rules, the fill maths, every b.set text expression, all 8 event bindings with their EventData
    and order); only the appends changed.
  - the three pages share ONE look (the Skills family: /skills <-> Stats <-> Overall, and Trees / Exploration link back to /skills):
    the vanilla PLAIN window (@Container: ContainerHeaderNoRunes title bar in the 15 px Secondary title style, ContainerPatch body,
    padding 17 - the vanilla list-page frame, and the frame the 0.4.6 Overall page already used), vanilla wells (#000000(0.15)) for
    lists / info boxes, vanilla list rows (#101925(0.55)), the vanilla progress track #1a2030, Secondary buttons for navigation
    (Overall / Tree / Stats / Top 10 / Skill tree; row actions = small Secondary like WorldEventListRow #ActionA), Back = Secondary +
    the cancel sound, footers right-aligned without LayoutMode Right (button_row(used= / left_margin=)). Skill colours stay (data
    colours: the skill name, the XP bar fill); UI_PAGE_COLORS lists them (the only data colours a page may show), UI_DATA_COLORS =
    UI_PAGE_COLORS + UI_CHAT_COLORS (the chat line colours) for the kit lint.
  - texts reach the pages through b.set (never parsed as markup), so names show their commas again: the 0.4.6 safe() blanking of
    , : ; " { } is no longer applied to page texts (SkillsPage.safe stays, unused by the page now - the class is otherwise unchanged).
    The 3-space indent 0.4.6 put in front of every boost line is left out (the lines sit in a well now).
  Page by page (all 960 wide; every body filled exactly, a fixed height per slot and a spacer where a part is off, so nothing moves):
  - SkillsPage (/skills) 960 x 786 (was 640 x 690): title bar SKILLS; a well with "Overall Level n - average x of k skills" (18 px row
    name) + the OVERALL button; a list well with the 9 skill rows (vanilla row panel 62 px - Acrobatics 82 -, 40 px item icon, the
    skill name + level 18 px bold in the skill colour, the XP bar 10 px in the skill colour on the vanilla track, the progress line
    15 px, the Acrobatics bonus line in info blue, then TREE (when SkyyTrees has that tree; a blank of its width when SkyyTrees runs
    without it) and STATS as small Secondary row actions); the hint line as a grey caption. Top 10 view: title bar TOP 10 - <SKILL>;
    RANK / PLAYER / LEVEL / XP column heads over a list well of up to 10 table rows (column_spec + column_row; your own row in white
    bold), "Nobody has any XP yet." inside the well, the rank line, BACK right-aligned.
  - StatsPage 960 x 848 (was 960 x 795): title bar = the skill name; "<Skill> - level n of 100" 32 px in the skill colour, the XP
    line, the 600 px bar, the "not a <class> right now" note (vanilla warning yellow), BOOSTS RIGHT NOW / LEVEL n+1 ADDS heads over
    two wells of up to 7 lines, the how-to caption (wraps, 3 lines), < BACK / TOP 10 / SKILL TREE right-aligned.
  - OverallPage 960 x 689 (was 960 x 795, already partly vanilla): the same look moved onto the kit - title bar OVERALL LEVEL, "Level n
    of 100" 32 px, the average line, the 600 px bar in the vanilla progress colours, SKILLS THAT COUNT / BOOSTS RIGHT NOW / OVERALL LEVEL
    n+1 ADDS heads over wells, the how-to caption, BACK right-aligned. Its own VAN_* style strings, the client-folder texture check and
    the HEAD / PANEL / TITLE / BTN fields are gone (the kit proves every value against Assets.zip instead); the button now has the
    vanilla sounds.
  KIT-GAPs (composed here from kit calls, tools/skyyui.py unchanged): (1) a list row with a second action and extra lines in its text
  column (the XP bar, the Acrobatics line): static_row has one action and centres only name + sub, so the rows use static_row's
  geometry from panel("row") + group() + item_icon + Appends.text + stat_bar + row_action; (2) a row look picked at runtime for a
  table row (your own leaderboard row): choose() of two column_row kinds; (3) a well with an uppercase section head over it (the
  settingHead kind + panel("well")) - the kit has section() / subtitle() at 13 / 15 px only.
  REVIEW FIXES (2026-09-29, the review of 0.4.7; still 0.4.7 - it was never deployed, the SET pin is 0.4.6):
  - ONE source for the /skills rows: SKILL_ROW_SLOTS, ACRO_SLOT and COMBAT_SLOT are Python values defined before SkillDefs;
    SkillDefs.ROW_SLOTS and SkillDefs.ACROBATICS are formatted from them (the same Java text as 0.4.6 - SkillDefs stays
    byte-identical) and the look block's list-well budget (SK_ROW_SLOTS / SK_LIST_H) reads the same list and asserts exactly one
    82 px Acrobatics row. A later patch that adds or reorders a row moves the budget with it (and the fixed page-size assert stops
    the build until the page is re-budgeted) instead of leaving a stale 613 px well that the extra row overflows.
  - the boost lines (Stats BOOSTS RIGHT NOW / LEVEL n+1 ADDS, Overall BOOSTS RIGHT NOW / OVERALL LEVEL n+1 ADDS: st_line) get the
    vanilla ShrinkTextToFit with a 15 px floor (fs(12), the kit's readable small size). The Acrobatics "Skill tree: ..." line with
    every node measures 897-957 px at 18 px for real SkyyTrees 0.2.4 node values (1091 px with 3-decimal values) against 910 px of
    room, and a SkyyCooking / SkyyExploration hook line has no length limit: such a line now shrinks inside its well instead of
    running past the well edge (0.4.6 had the same limit). A line that fits is drawn exactly as before. Vanilla plain labels shrink
    the same way (PlaySoundPage, ParticleSpawnPage, PortalDeviceSummon #Title0), and every kit button on these pages already
    carries the property (the base probe gate these pages wait for anyway). KIT-GAP (4): label() has no shrink= option, so
    st_line swaps the kind's own text_style(...) for the kit's text_style(..., shrink=15) (asserted: exactly that style, once).
  - not changed (look-only contract; the review agrees): no footer Close (it needs a new handleDataEvent branch + EventData);
    SkillsPage.safe() stays unused and the Back labels stay 'Back' / '< Back' - both for the next non-restyle Skills version. The
    deploy gate (probe pages base1-3 + base4 in a SkyyUiProbe 0.2 before the pin moves) is the coordinator's, not this patch's.
  REVIEW 2 FIXES (2026-09-29, the second review of 0.4.7; still 0.4.7, the jar bytes are unchanged by them):
  - st_state's footer-width sample check compared against a whole conditional expression (`used == a if tree else b` is
    `(used == a) if tree else b`), so the no-tree Stats footer was never checked; it now compares against the conditional value and
    also asserts that ST_NAV_GAP + the footer width = the body width (the footer is right-aligned exactly).
  - the data colours are split: UI_PAGE_COLORS (the 16 skill colours = SkillDefs.COLORS, asserted) is the only data-colour set the
    harness allows in page markup; UI_CHAT_COLORS (Message.color of chat lines) only joins them in UI_DATA_COLORS for the kit lint,
    so a chat colour that slipped into page markup now fails the harness.
  - not changed (look-only contract / an in-game judgement): the 7-line Stats wells, the 55 px Top 10 rows and the 62 / 82 px row
    actions stay as budgeted until Skyy has seen them next to the vanilla pages; no footer Close (as above).
  KIT-GAP (5): the kit's proven-property table records key names, not values - `HorizontalAlignment: Start` (the Top 10 column
  heads: column_spec(...).heads() in the kit's section style; vanilla CommandListPage uses it) passes SUI.assert_proven by its key although no deployed Skyy
  page has shown that value yet; it rides on the base4 probe page (SkyyUiProbe 0.2).
Everything else (commands, aliases, permissions, config keys + rows, files, bridge keys, the leaderboard data, every handleDataEvent,
every other class) is byte-identical to 0.4.6 - asserted below (KEEP blocks) and by SkyySkills/test_skyyskills_0.4.7.py (bytecode).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.6.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.7.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.6"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
# the source must be the generated 0.4.6 of the EDITED lineage (Skyy's ab75b6c edits carried through skills_0_4_6_patch.py)
assert 'VERSION = "0.4.6"' in s and "derived from the EDITED 0.4.5 by tools/skills_0_4_6_patch.py" in s, "not the live generated 0.4.6"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 8, "0.4.6 has 8 event bindings (SkillsPage 4, StatsPage 3, OverallPage 1), found %d" % len(BIND0)


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def cut(a, b, new=""):
    """replace everything from anchor a (included) up to anchor b (kept) with new; returns the text that was cut"""
    global s
    assert s.count(a) == 1, "cut start count %d: %s" % (s.count(a), a[:120])
    assert s.count(b) == 1, "cut end count %d: %s" % (s.count(b), b[:120])
    i, j = s.index(a), s.index(b)
    assert i < j, "cut anchors out of order: %s / %s" % (a[:60], b[:60])
    old = s[i:j]
    s = s[:i] + new + s[j:]
    return old


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source (for unchanged-block asserts)"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical (everything but the docstring head, VERSION, the kit import, the three page
# looks and the ready log line)
KEEP = [block('import sys, os, json, zipfile\n', 'import skyycfg as CFG'),
        block('HERE = os.path.dirname(os.path.abspath(__file__))\nJ = B.start()', '# ================= /skills page (inline'),
        block('page.addField(CtField.make("public int view;", page))', 'page.addMethod(CtNewMethod.make(f"""\npublic void build('),
        block('# ================= StatsPage (0.3)', 'spg.addMethod(CtNewMethod.make(f"""\npublic static void line('),
        block('spg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(', '# ================= OverallPage (0.4.6)'),
        block('opg.addConstructor(CtNewConstructor.make(f"""\npublic OverallPage(', '# a label in the page body; every dynamic text'),
        block('opg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(', '  getLogger().at(java.util.logging.Level.INFO).log("[SkyySkills] {VERSION} ready'),
        block('  {PKG}.SkillStore.regSetting("skills.xpGain"', 'jar = os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)')]
# /skills rows: 9 rows, Acrobatics once (the list well is budgeted for 8 rows of 62 px + the 82 px Acrobatics row)
assert s.count('ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 13, 3 };') == 1
assert s.count("defs.addField(CtField.make(\"public static final int ACROBATICS = 4;\", defs))") == 1
# review fix: ONE Python source for the /skills rows + the Acrobatics / class-row slots - SkillDefs.ROW_SLOTS / ACROBATICS are
# formatted from it (the same Java text: asserted here and by the harness bytecode step) and the look block's budget reads it
_ROWS_046 = [0, 1, 2, 10, 11, 12, 4, 13, 3]
assert "{ %s }" % ", ".join(str(x) for x in _ROWS_046) == "{ 0, 1, 2, 10, 11, 12, 4, 13, 3 }"
SLOT_FIX = [
    ('defs.addField(CtField.make("public static final int ACROBATICS = 4;", defs))',
     'defs.addField(CtField.make("public static final int ACROBATICS = %d;" % ACRO_SLOT, defs))'),
    ('''# /skills rows (3 = the class row: the current class's weapon skill, or the "choose a class" row)
defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 13, 3 };", defs))''',
     '''# /skills rows (3 = the class row: the current class's weapon skill, or the "choose a class" row) - 0.4.7: from SKILL_ROW_SLOTS
defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { %s };" % ", ".join(str(x) for x in SKILL_ROW_SLOTS), defs))'''),
    ('def jarr(xs): return "new String[] { "', '''# 0.4.7: the /skills row order, the Acrobatics slot and the class-row slot as ONE set of Python values - formatted into
# SkillDefs.ROW_SLOTS / ACROBATICS below (the same Java text as 0.4.6) AND read by the SKILLS PAGES LOOK block (the /skills list-well
# height budget SK_ROW_SLOTS / SK_LIST_H: one 62 px row per slot, the Acrobatics row 82 px), so the rows and the budget cannot drift
SKILL_ROW_SLOTS = %s
ACRO_SLOT, COMBAT_SLOT = 4, 3
assert SLOT_NAMES[ACRO_SLOT] == "Acrobatics" and SLOT_NAMES[COMBAT_SLOT] == "Combat", (ACRO_SLOT, COMBAT_SLOT)
assert SKILL_ROW_SLOTS.count(ACRO_SLOT) == 1 and SKILL_ROW_SLOTS.count(COMBAT_SLOT) == 1 and len(set(SKILL_ROW_SLOTS)) == len(SKILL_ROW_SLOTS)
def jarr(xs): return "new String[] { "''' % _ROWS_046),
]
for _o, _n in SLOT_FIX:
    rep(_o, _n)

# ================================================================================================ docstring / version / kit import
rep('''"""SkyySkills 0.4.6 - build script (derived from the EDITED 0.4.5 by tools/skills_0_4_6_patch.py - edit the patch, not this file;
0.4.5 was derived''', '''"""SkyySkills 0.4.7 - build script (derived from the generated 0.4.6 by tools/skills_0_4_7_patch.py - edit the patch, not this file;
0.4.6 was derived from the EDITED 0.4.5 by tools/skills_0_4_6_patch.py; 0.4.5 was derived''')
rep('''0.4.6: BASE MANA + OVERALL LEVEL (research/Overall-Level-Spec.md) + Skyy's 2026-09-25 locks''', '''0.4.7: THE VANILLA LOOK for /skills (+ Top 10), the Stats page and the Overall page (Skyy 2026-09-28: "the new goal for any and all UI
  added in the game is for them to look and feel vanilla"; research/Vanilla-UI-Style-Guide.md; full notes in tools/skills_0_4_7_patch.py).
  ONLY THE LOOK CHANGED:
  - the pages are built from the shared kit tools/skyyui.py when this script runs (SUI.verify() first proves every style value,
    texture and sound against Assets.zip, read-only); the kit id is in the ready log line.
  - one look for the Skills family: the vanilla plain window (title bar + ContainerPatch body), wells for lists and info boxes, vanilla
    list rows, the vanilla progress track, Secondary buttons (Back with the cancel sound), footers right-aligned. /skills 960 x 786,
    Stats 960 x 848, Overall 960 x 689; skill colours stay on the skill name and the XP bar. Top 10 = a RANK / PLAYER / LEVEL / XP table.
  - every element id of 0.4.6, every event binding + EventData (skstatov, sktree<slot>, skstat<slot>, skback, stback, sttop, sttree,
    ovback), every text (the same Java expressions; b.set, so commas show again), the leaderboard data, the Overall / class-row / legacy
    / max-level rules and every handleDataEvent are 0.4.6's; nothing else in the jar changed (commands, config, files, bridge keys).
  - review fixes: the boost lines shrink to fit their well (vanilla ShrinkTextToFit, 15 px floor) instead of running past its edge;
    the /skills rows (SkillDefs.ROW_SLOTS / ACROBATICS) and the list-well height budget come from ONE Python list (SKILL_ROW_SLOTS).
0.4.6: BASE MANA + OVERALL LEVEL (research/Overall-Level-Spec.md) + Skyy's 2026-09-25 locks''')
rep('VERSION = "0.4.6"\n', 'VERSION = "0.4.7"\n')
rep('''import skyycfg as CFG   # 0.4.3: the admin config registry kit (tools/CONFIG-CONTRACT.md), generated into this jar
''', '''import skyycfg as CFG   # 0.4.3: the admin config registry kit (tools/CONFIG-CONTRACT.md), generated into this jar
import skyyui as SUI    # 0.4.7: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()            # proves every vanilla value / texture / sound the pages use against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()   # "skyyui <version> <blob12>" - in the ready log line
''')
rep('log("[SkyySkills] {VERSION} ready - /skills;', 'log("[SkyySkills] {VERSION} ready ({KIT_ID}) - /skills;')

# ================================================================================================ the old page code (cut, kept lines checked)
OLD_SK = cut('page.addMethod(CtNewMethod.make(f"""\npublic void build(', "# ================= StatsPage (0.3)", "@@SKBUILD@@\n")
OLD_ST = cut('spg.addMethod(CtNewMethod.make(f"""\npublic static void line(', 'spg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(',
             "@@STBUILD@@\n")
OLD_OVHEAD = cut("# ================= OverallPage (0.4.6)", 'opg.addConstructor(CtNewConstructor.make(f"""\npublic OverallPage(', "@@OVHEAD@@\n")
OLD_OV = cut("# a label in the page body; every dynamic text goes through b.set (safe for any character)\nopg.addMethod(",
             'opg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(', "@@OVBUILD@@\n")
OLD_BARW = cut("BARW = 400\n", 'page.addField(CtField.make("public int view;", page))', "@@SKLOOK@@\n")
assert OLD_BARW == "BARW = 400\n", OLD_BARW
for _v in ("VAN_HEAD", "VAN_PANEL", "VAN_TITLE", "VAN_BTN", "_VAN_TEX", "OVBARW = 600"):
    assert _v in OLD_OVHEAD, _v
# the Java lines of 0.4.6's three build() methods that 0.4.7 keeps VERBATIM (state, rules, fill maths, b.set texts, bindings)
KEEP_SK = [
    "  java.util.UUID u = this.playerRef.getUuid();",
    "  long[] d = {PKG}.SkillStore.data(u);",
    "  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{",
    "    int cs = {PKG}.SkillClass.slot(u);",
    "    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;",
    "    int[] osc = {PKG}.Overall.sums(u, d);",
    '    b.set("#SkyySkOv.Text", "Overall Level " + {PKG}.Overall.level(osc) + "  -  average " + {PKG}.Overall.avg({PKG}.Overall.tenths(osc)) + " of " + osc[1] + " skills");',
    '    ev.addEventBinding({BT}.Activating, "#SkyySkOvStat", {EVD}.of("a", "skstatov"));',
    "    boolean trees = {PKG}.SkillBonus.treesOn();",
    "    for (int i = 0; i < rows.length; i++) {{",
    "      int sl = rows[i];",
    "      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;",
    "      if (classRow && cs >= 0) sl = cs;",
    "      long total = d[sl];",
    "      int lv = {PKG}.SkillDefs.levelOf(total);",
    "      long cur = {PKG}.SkillDefs.intoLevel(total);",
    "      long need = {PKG}.SkillDefs.needFor(total);",
    "      int fill = need > 0L ? (int) ((long) bw * cur / need) : bw;",
    "      if (fill < 0) fill = 0;",
    "      if (fill > bw) fill = bw;",
    '      String prog = need > 0L ? ({PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1)) : ("MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP");',
    "      String col = {PKG}.SkillDefs.COLORS[sl];",
    '      String title = {PKG}.SkillDefs.LABELS[sl] + "  " + lv;',
    "      if (classRow) {{",
    '        if (cs >= 0) title = {PKG}.SkillClass.skillName(u, cs) + "  " + lv;',
    "        else {{",
    '          title = "Class skill - choose a class with /class";',
    '          prog = total > 0L ? "Old Combat XP (level " + lv + ") moves to the first class you choose" : "Your combat skill is your class skill";',
    "          fill = 0;",
    "      boolean acroRow = sl == {PKG}.SkillDefs.ACROBATICS;",
    "      if (acroRow) {{",
    '        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));',
    "      if (trees) {{",
    "        if ({PKG}.SkillBonus.treeAvailable(sl)) {{",
    '          ev.addEventBinding({BT}.Activating, "#SkyySkTree" + i, {EVD}.of("a", "sktree" + sl));',
    "        }} else {{",
    '      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));',
    "    return;",
    "  int s = this.view;",
    "  java.util.ArrayList rows = {PKG}.SkillTop.all(s);",
    "  int n = rows.size() < 10 ? rows.size() : 10;",
    "  for (int i = 0; i < n; i++) {{",
    "    Object[] e = (Object[]) rows.get(i);",
    "    long x = ((Long) e[1]).longValue();",
    "    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);",
    "  int rank = {PKG}.SkillTop.rankOf(rows, u);",
    '  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));',
]
KEEP_ST = [
    "  java.util.UUID u = this.playerRef.getUuid();",
    "  long[] d = {PKG}.SkillStore.data(u);",
    "  int s = this.slot;",
    "  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;",
    "  int cs = {PKG}.SkillClass.slot(u);",
    "  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;",
    "  long total = d[s];",
    "  int lv = {PKG}.SkillDefs.levelOf(total);",
    "  long cur = {PKG}.SkillDefs.intoLevel(total);",
    "  long need = {PKG}.SkillDefs.needFor(total);",
    "  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};",
    "  if (fill < 0) fill = 0;",
    "  if (fill > {STBARW}) fill = {STBARW};",
    "  boolean legacy = s == {PKG}.SkillDefs.COMBAT;",
    "  if (legacy) fill = 0;",
    "  String col = {PKG}.SkillDefs.COLORS[s];",
    '  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);',
    '  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);',
    "  String sub;",
    '  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";',
    '  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";',
    '  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";',
    '  b.set("#SkyyStSub.Text", sub);',
    "  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{",
    "    String cn = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];",
    '    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";',
    "  java.util.ArrayList now = lines(u, s, lv, false);",
    "  if (!legacy) {{",
    "    if (need > 0L) {{",
    "      java.util.ArrayList nx = lines(u, s, lv, true);",
    "  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;",
    '  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));',
    '  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));',
    "  if (tree != null) {{",
    '    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));',
]
KEEP_OV = [
    "  java.util.UUID u = this.playerRef.getUuid();",
    "  long[] d = {PKG}.SkillStore.data(u);",
    "  int[] sc = {PKG}.Overall.sums(u, d);",
    "  int lv = {PKG}.Overall.level(sc);",
    "  int t = {PKG}.Overall.tenths(sc);",
    "  boolean max = lv >= {PKG}.SkillDefs.MAX;",
    "  int fill = max ? {OVBARW} : (t % 10) * ({OVBARW} / 10);",
    "  if (fill < 0) fill = 0;",
    "  if (fill > {OVBARW}) fill = {OVBARW};",
    '  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";',
    "  java.util.ArrayList now = {PKG}.Overall.nowLines(u, lv);",
    "    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv);",
    '  ev.addEventBinding({BT}.Activating, "#SkyyOvBack", {EVD}.of("a", "ovback"));',
]
for _old, _keep in ((OLD_SK, KEEP_SK), (OLD_ST, KEEP_ST), (OLD_OV, KEEP_OV)):
    _ol = _old.split(LF)
    for _ln in _keep:
        assert _ol.count(_ln) == 1, "0.4.6 build() line not found exactly once: " + _ln
# the text expressions 0.4.6 passed to its markup (inline after safe(), or to line() / wrapLine()) - 0.4.7 b.sets the SAME expressions
OLD_TEXTS = [
    (OLD_SK, 'safe(title)'), (OLD_SK, 'safe(prog)'), (OLD_SK, 'Text: \\\\"Skills\\\\"'),
    (OLD_SK, 'safe("Top 10 - " + {PKG}.SkillDefs.LABELS[s])'), (OLD_SK, 'Nobody has any XP yet.'),
    (OLD_SK, 'String line = (i + 1) + ".   " + e[0] + "     Level " + {PKG}.SkillDefs.levelOf(x) + "     " + {PKG}.SkillDefs.fmt(x) + " XP";'),
    (OLD_SK, 'safe(rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + {PKG}.SkillDefs.levelOf(d[s]) + " - " + {PKG}.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet")'),
    (OLD_SK, 'Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins'),
    (OLD_ST, '"You are not " + art + cn + " right now - these boosts work while you are one"'),
    (OLD_ST, 'legacy ? "Your combat" : "Boosts right now (level " + lv + ")"'),
    (OLD_ST, '"   " + (String) now.get(i)'), (OLD_ST, '"Level " + (lv + 1) + " adds"'), (OLD_ST, '"   " + (String) nx.get(i)'),
    (OLD_ST, '"Max level reached - nothing more to unlock"'), (OLD_ST, 'how(s)'),
    (OLD_OV, '"Level " + lv + " of " + {PKG}.SkillDefs.MAX'), (OLD_OV, '"Skills that count (" + sc[1] + ")"'),
    (OLD_OV, '{PKG}.Overall.listText(u, d)'), (OLD_OV, '"Boosts right now"'), (OLD_OV, '"   " + (String) now.get(i)'),
    (OLD_OV, '"Max Overall Level reached"'), (OLD_OV, '"Overall Level " + (lv + 1) + " adds"'), (OLD_OV, '"   " + (String) nx.get(i)'),
    (OLD_OV, '"The Overall Level is the average of the skills above, rounded down - level any of them to raise it. Other classes\' skills never count (a new class is a new profile)."'),
]
for _old, _t in OLD_TEXTS:
    assert _old.count(_t) == 1, "0.4.6 page text expression not found exactly once: " + _t

# ================================================================================================ the new look block (runs at BUILD time)
NEW_LOOK = r'''# ================= SKILLS PAGES LOOK (0.4.7): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 7, 8c, 12 and 13 (the LIST page recipe). The sk_* / st_* / ov_* functions build the markup
# of /skills (+ its Top 10 view), the Stats page and the Overall page from kit calls; the Java the kit emits gets a name (SK_*_JAVA,
# ST_*_JAVA, OV_*_JAVA) and is interpolated into the three build() f-strings below as {..._JAVA}: interpolated text is never re-parsed
# by Python, so the kit's Java string literals reach javassist exactly as the kit wrote them (no brace doubling, no escaping).
# Proven properties only (LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour backgrounds, the kit's
# textures and sounds, Wrap): no FlexWeight, no LayoutMode Center / Right / Full, no WrapMaxLines / LetterSpacing, nothing UNVERIFIED
# (SUI.assert_proven on every sample state below). Every page body is filled exactly: each part has a fixed height, a spacer stands in
# for a part that is off (no note, no next level, no Tree), so nothing moves between states.
# ---- SKILLS PAGE BLOCK START (SkyySkills/test_skyyskills_0.4.7.py builds every page state with the 0.4.6 and 0.4.7 jars)
UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS   # the 16 skill / class colours (= SkillDefs.COLORS): the ONLY data colours a page may
#   show (the skill name + the XP bar); SkyySkills/test_skyyskills_0.4.7.py allows exactly these (+ kit colours) in page markup
UI_CHAT_COLORS = ["#ffb080", "#ffe08a", "#9fd8ff", "#a8e8c0", "#b8f0a0", "#ffc800", "#c8b070", "#a0f0e0", "#9fe0a0"]   # chat lines only
#   (Message.color) - never on a page; listed so the kit lint (tools/ci/lint.py) knows them
UI_DATA_COLORS = UI_PAGE_COLORS + UI_CHAT_COLORS   # what tools/ci/lint.py reads (page + chat data colours)
assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"
assert not set(c.lower() for c in UI_CHAT_COLORS) & set(c.lower() for c in SLOT_COLORS), "a chat colour is also a skill colour"
_SK_LF = chr(10)
_SK_COL = SLOT_COLORS[0]              # the colour sample of a runtime skill colour (SkillDefs.COLORS[sl]): Mining
# ---- sizes (every page 960 wide; the plain window: 38 px title bar + padding 17)
SK_W = 960
SK_IN_W = SK_W - 2 * SUI.CONTENT_PAD                                   # 926: the body's inner width
SK_LIST_IN = SK_IN_W - 2 * SUI.WELL_LIST_PAD                           # 918: a row inside a list well
SK_ACT_W = SUI.ROW_ACTION_W                                            # 92: TREE / STATS (WorldEventListRow #ActionA, small Secondary)
SK_ACT = 4 + SK_ACT_W                                                  # an action + its 4 px gap
SK_ROW_PAD, SK_ICON, SK_ICON_BOX = 8, 40, 52                           # static_row's geometry: padding 8, a 40 px icon in a 52 px box
SK_NAME_H, SK_PROG_H = SUI.fs(14) + 6, SUI.fs(12) + 5                  # 24 + 20: the kit's row text heights (18 px bold, 15 px)
SK_XP_H, SK_XP_M = 10, 2                                               # the XP bar (10 px as in 0.4.6) and its 2 px margins
SK_TEXT_H = SK_NAME_H + SK_XP_M + SK_XP_H + SK_XP_M + SK_PROG_H        # 58
SK_TEXT_TOP = 2
SK_ROW_H = SK_TEXT_H + 2 * SK_TEXT_TOP                                 # 62: a skill row
SK_ACRO_H = SK_ROW_H + SK_PROG_H                                       # 82: the Acrobatics row (+ its bonus line)
SK_PANEL_W = {True: SK_LIST_IN - 2 * SK_ACT, False: SK_LIST_IN - SK_ACT}   # the row panel: 726 with the TREE column, 822 without
SK_TEXT_W = dict((k, v - 2 * SK_ROW_PAD - SK_ICON_BOX) for k, v in SK_PANEL_W.items())   # 658 / 754
SK_XP_W = dict((k, v - 8) for k, v in SK_TEXT_W.items())                # 650 / 746: the XP bar (fill maths: bw)
SK_ROW_SLOTS = SKILL_ROW_SLOTS                                         # = SkillDefs.ROW_SLOTS (formatted from the same list): 9 rows
assert SK_ROW_SLOTS.count(ACRO_SLOT) == 1, "the list well budgets exactly ONE 82 px Acrobatics row (SK_ACRO_H)"
SK_LIST_H = 2 * SUI.WELL_LIST_PAD + sum((SK_ACRO_H if sl == ACRO_SLOT else SK_ROW_H) + SUI.ROW_GAP for sl in SK_ROW_SLOTS)   # 613: one
#   slot of each row's height (+ its gap) per SkillDefs.ROW_SLOTS entry - SkillsPage.build() gives the Acrobatics row 82 px, the rest 62
SK_OV_H, SK_OV_M = SUI.BTN_H + 2 * SUI.WELL_PAD, 8                     # the Overall well (60) + 8 under it
SK_OV_LABEL_W = SK_IN_W - 2 * SUI.WELL_PAD - SUI.BTN_MIN_W - 8          # 730
SK_HINT_H, SK_HINT_M = SUI.fs(12) + 10, 8                              # the caption line under the list
SK_BODY_H = SK_OV_H + SK_OV_M + SK_LIST_H + SK_HINT_M + SK_HINT_H       # 714
SK_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + SK_BODY_H                    # 786
SK_HINT = "Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins"
# Top 10 view (the same window): column heads + a list well of table rows + the rank line + the footer
SK_TOP_HEAD_H, SK_TOP_ROW_H = 30, 55
SK_RANK_H, SK_RANK_M = 30, 8
SK_FOOT_H = SUI.BTN_H + 8                                              # a button row: 44 + its top 8
SK_TOP_LIST_H = SK_BODY_H - SK_TOP_HEAD_H - (SK_RANK_M + SK_RANK_H) - SK_FOOT_H   # 594: the well takes the rest
SK_TOP_SPEC = SUI.column_spec([("Rank", 100), ("Player", 444), ("Level", 150), ("XP", 200)], avail=SK_LIST_IN, pad_left=12)
# Stats page: fixed slots (title, XP line, bar, note, now / next wells of 7 lines, how-to, footer)
ST_TITLE_H, ST_SUB_H = 42, 28                                          # the 32 px display line, the 16 px XP line
SK_BIG_BAR_W, ST_BAR_M = 600, 6                                        # the 600 px bar (= STBARW / OVBARW, asserted there; 18 high) + margins
ST_NOTE_H, ST_SEP_H = 28, 1 + 2 * SUI.SEP_MARGIN                        # the note slot, a content separator (17)
ST_HEAD_H, ST_HEAD_B, ST_HEAD_T = SUI.fs(14) + 10, 4, 10               # an uppercase section head (28) + 4 under it (+ 10 over the 2nd)
ST_LINE_H, ST_LINES = 28, 7                                            # a boost line (18 px) and at most 7 per list (0.4.6)
ST_LINE_MIN = SUI.fs(12)                                               # 15: a boost line longer than its well shrinks to this floor
ST_BOX_H = ST_LINES * ST_LINE_H + 2 * SUI.WELL_PAD                      # 212: one list well
ST_HOW_H = 64                                                          # the how-to caption: 3 lines of 15 px (1.364 em)
STATS_W = SK_W
ST_BODY = (ST_TITLE_H + ST_SUB_H + (18 + 2 * ST_BAR_M) + ST_NOTE_H + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + ST_BOX_H
           + (ST_HEAD_T + ST_HEAD_H + ST_HEAD_B) + ST_BOX_H + ST_SEP_H + ST_HOW_H + SK_FOOT_H)                 # 776
STATS_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + ST_BODY                   # 848
ST_NAV_GAP = {True: SK_IN_W - (3 * SUI.BTN_MIN_W + 2 * 6), False: SK_IN_W - (2 * SUI.BTN_MIN_W + 6)}   # the footer's left padding
# Overall page: the same slots with 3 / 2 lines and the wrapped list of counted skills
OV_LIST_H = 76                                                         # the counted skills: up to 3 wrapped 18 px lines
OV_NOW_N, OV_NEXT_N = 3, 2                                             # 0.4.6: at most 3 boost lines, 2 next-level lines
OV_HOW_H = 44                                                          # the how-to caption: 2 lines of 15 px
OV_BODY = (ST_TITLE_H + ST_SUB_H + (18 + 2 * ST_BAR_M) + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + (OV_LIST_H + 2 * SUI.WELL_PAD)
           + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + (OV_NOW_N * ST_LINE_H + 2 * SUI.WELL_PAD)
           + (ST_HEAD_T + ST_HEAD_H + ST_HEAD_B) + (OV_NEXT_N * ST_LINE_H + 2 * SUI.WELL_PAD) + ST_SEP_H + OV_HOW_H + SK_FOOT_H)   # 617
OV_W, OV_H = SK_W, SUI.TITLE_H + 2 * SUI.CONTENT_PAD + OV_BODY          # 960 x 689
OV_HOW = ("The Overall Level is the average of the skills above, rounded down - level any of them to raise it. Other classes' skills "
          "never count (a new class is a new profile).")
assert (SK_H, STATS_H, OV_H) == (786, 848, 689) and SK_LIST_H == 613 and SK_TOP_LIST_H == 594, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)
assert SK_TEXT_W == {True: 658, False: 754}, SK_TEXT_W
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "the Top 10 well holds its 10 rows"
assert SK_ACT_W - 2 * SUI.BTN_SMALL_PAD >= SUI.text_width("Stats", 14, True, upper=True), "STATS fits the small row action"


def sk_shell():
    """/skills (both views): the plain window SkyySkF (960 x 786); 0.4.6's root #SkyySkills is the body. The title is set at runtime:
    SKILLS on the overview, TOP 10 - <SKILL> on the leaderboard view (0.4.6's two title labels)."""
    title = SUI.J('this.view < 0 || this.view >= ' + PKG + '.SkillDefs.N ? "Skills" : "Top 10 - " + ' + PKG + '.SkillDefs.LABELS[this.view]',
                  "Skills")
    return SUI.page_shell("SkyySkF", SK_W, SK_H, title, kind="plain", body_id="SkyySkills")


def sk_overview(ap, body):
    """The overview's static parts: the Overall well (#SkyySkOvRow: #SkyySkOv + the OVERALL button #SkyySkOvStat), the list well
    #SkyySkList (the rows go in there) and the hint caption. #SkyySkOv's text is b.set by the kept 0.4.6 line."""
    ap.add(body, SUI.panel("SkyySkOvRow", "well", h=SK_OV_H, layout="Left", anchor={"bottom": SK_OV_M}))
    ap.add("SkyySkOvRow", SUI.label("SkyySkOv", "", "rowName", w=SK_OV_LABEL_W, h=SUI.BTN_H))
    ap.add("SkyySkOvRow", SUI.button("SkyySkOvStat", "Overall", "secondary", anchor={"left": 8}))
    ap.add(body, SUI.list_well("SkyySkList", w=SK_IN_W, h=SK_LIST_H))
    ap.text(body, "SkyySkHint", SK_HINT, "caption", h=SK_HINT_H, align="Center", anchor={"top": SK_HINT_M})


def sk_row(i, rh, pw, tw, bw, fill, col, icon, title, prog):
    """One skill row #SkyySkRow<i> in #SkyySkList (i = an id suffix: SUI.J("i") in the build, digits in the checks): the vanilla row
    panel #SkyySkRow<i>P (static_row's geometry: padding 8, the 40 px item icon #SkyySkRow<i>Ic in a 52 px box), the text column
    #SkyySkTxt<i> (0.4.6's id) with the name #SkyySkRow<i>Nm (18 px bold, the skill colour), the XP bar #SkyySkBar<i> (0.4.6's id;
    the vanilla track, the fill in the skill colour, no fill Group at 0) and the progress line #SkyySkRow<i>Pg (15 px). The row
    actions come after (sk_tree / sk_tree_gap / sk_stat). Texts: title / prog = b.set values."""
    ap = SUI.Appends()
    r, t = "SkyySkRow" + i, "SkyySkTxt" + i
    ap.add("SkyySkList", SUI.group(r, "Left", h=rh, anchor={"bottom": SUI.ROW_GAP}))
    ap.add(r, SUI.panel(r + "P", "row", w=pw, h=rh, layout="Left", pad={"left": SK_ROW_PAD, "right": SK_ROW_PAD}))
    ap.add(r + "P", SUI.group(r + "Ib", None, w=SK_ICON_BOX, h=rh))
    top = SUI.J("(rh - %d) / 2" % SK_ICON, str((SK_ROW_H - SK_ICON) // 2)) if SUI.has_j(rh) else (rh - SK_ICON) // 2
    ap.add(r + "Ib", SUI.item_icon(r + "Ic", icon, SK_ICON, anchor={"left": 0, "top": top}))
    ap.add(r + "P", SUI.group(t, "Top", w=tw, h=rh, pad={"top": SK_TEXT_TOP}))
    ap.text(t, r + "Nm", title, "rowName", h=SK_NAME_H, col=col)
    bar = SUI.stat_bar("SkyySkBar" + i, bw, SK_XP_H, fill, col=col, anchor={"top": SK_XP_M, "bottom": SK_XP_M})
    ap.add(t, bar.choose() if SUI.has_j(fill) else bar.pick())
    ap.text(t, r + "Pg", prog, "rowSub", h=SK_PROG_H)
    return ap


def sk_bonus(i):
    """The Acrobatics row's bonus line #SkyySkBonus (0.4.6's id; info blue, 15 px) under the progress line; its text is b.set by the
    kept 0.4.6 line (Acro.bonusText)."""
    return SUI.Appends([("SkyySkTxt" + i, SUI.label("SkyySkBonus", "", "rowSub", h=SK_PROG_H, col="info"))])


def sk_tree(i, rh):
    return SUI.Appends([("SkyySkRow" + i, SUI.row_action("SkyySkTree" + i, "Tree", w=SK_ACT_W, h=rh))])


def sk_tree_gap(i, rh):
    """SkyyTrees runs but has no tree for this skill: a blank as wide as TREE, so STATS lines up (0.4.6: an empty 70 px label)."""
    return SUI.Appends([("SkyySkRow" + i, SUI.group(None, None, w=SK_ACT_W, h=rh, anchor={"left": 4}))])


def sk_stat(i, rh):
    return SUI.Appends([("SkyySkRow" + i, SUI.row_action("SkyySkStat" + i, "Stats", w=SK_ACT_W, h=rh))])


def sk_top(ap, body):
    """The Top 10 view's static parts: RANK / PLAYER / LEVEL / XP heads (vanilla section labels over the columns) and the list
    well #SkyySkTop."""
    ap.add(body, SK_TOP_SPEC.heads("SkyySkTopHead", outside=SUI.WELL_LIST_PAD))
    ap.add(body, SUI.list_well("SkyySkTop", w=SK_IN_W, h=SK_TOP_LIST_H))


def sk_top_row(i, me, cells):
    """One leaderboard row #SkyySkTopRow<i> (a vanilla table row, cells C0-C3 under the heads; texts b.set); your own row (me) in
    white bold: a J("me") picks it at runtime (both looks create the same ids and set the same texts)."""
    mine = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="strong")
    other = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="default")
    if SUI.has_j(me):
        return SUI.choose(me, mine, other)
    return mine if me else other


def sk_top_empty():
    ap = SUI.Appends()
    ap.text("SkyySkTop", "SkyySkTopNone", "Nobody has any XP yet.", "caption", h=30, anchor={"left": 8})
    return ap


def sk_top_foot(ap, body, rank_text):
    """The rank line #SkyySkRank (b.set) and the footer #SkyySkNav (0.4.6's id) with BACK #SkyySkBack right-aligned."""
    ap.text(body, "SkyySkRank", rank_text, "default", h=SK_RANK_H, align="Center", anchor={"top": SK_RANK_M})
    ap.add(body, SUI.button_row("SkyySkNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyySkNav", SUI.button("SkyySkBack", "Back", "secondary", sound="cancel"))


def _sk_head(ap, parent, ident, text, top=0, col=None):
    """An uppercase section head over a well (18 px bold #96a9be: the settingHead kind; KIT-GAP 3)."""
    anc = {"bottom": ST_HEAD_B}
    if top:
        anc["top"] = top
    kw = {"h": ST_HEAD_H, "anchor": anc}
    if col is not None:
        kw["col"] = col
    if text:
        ap.text(parent, ident, text, "settingHead", **kw)
    else:
        ap.add(parent, SUI.label(ident, "", "settingHead", **kw))


def _sk_bar_row(ap, parent, row_id, bar_id, fill, col=None):
    """A centred 600 px bar (STBARW / OVBARW) on the vanilla track: row #row_id (LayoutMode Left, Padding Left centres it) + the
    stat_bar #bar_id (no fill Group at 0)."""
    ap.add(parent, SUI.group(row_id, "Left", h=18, anchor={"top": ST_BAR_M, "bottom": ST_BAR_M},
                             pad={"left": SUI.centre_margin(SK_IN_W, SK_BIG_BAR_W)}))
    kw = {"col": col} if col is not None else {}
    bar = SUI.stat_bar(bar_id, SK_BIG_BAR_W, 18, fill, **kw)
    ap.add(row_id, bar.choose() if SUI.has_j(fill) else bar.pick())


def st_shell(name):
    """The Stats page: the plain window SkyyStF (960 x 848), the title bar = the skill name; 0.4.6's root #SkyySkStats is the body."""
    return SUI.page_shell("SkyyStF", STATS_W, STATS_H, name, kind="plain", body_id="SkyySkStats")


def st_top(ap, body):
    """#SkyyStTitle (32 px in the skill colour), #SkyyStSub (the XP line) and the bar row #SkyyStBarRow - texts b.set by kept lines."""
    ap.add(body, SUI.label("SkyyStTitle", "", "display", h=ST_TITLE_H, align="Center", col=SUI.J("col", _SK_COL)))
    ap.add(body, SUI.label("SkyyStSub", "", "default", h=ST_SUB_H, align="Center"))
    ap.add(body, SUI.group("SkyyStBarRow", "Left", h=18, anchor={"top": ST_BAR_M, "bottom": ST_BAR_M},
                           pad={"left": SUI.centre_margin(SK_IN_W, SK_BIG_BAR_W)}))


def st_bar(fill):
    """The 600 px XP bar #SkyyStBar in #SkyyStBarRow (the vanilla track, the fill in the skill colour; no fill Group at 0)."""
    bar = SUI.stat_bar("SkyyStBar", SK_BIG_BAR_W, 18, fill, col=SUI.J("col", _SK_COL))
    return SUI.Appends([("SkyyStBarRow", bar.choose() if SUI.has_j(fill) else bar.pick())])


def st_note():
    """#SkyyStNote: 'You are not a Mage right now - ...' (bold, the vanilla warning yellow, centred); b.set by the kept expression."""
    return SUI.Appends([("SkyySkStats", SUI.label("SkyyStNote", "", "bold", h=ST_NOTE_H, align="Center", col="warning"))])


def st_note_gap():
    return SUI.Appends([("SkyySkStats", SUI.spacer(h=ST_NOTE_H))])


def st_mid(ap, body):
    """The separator, the BOOSTS RIGHT NOW head #SkyyStNowHd and its well #SkyyStNowBox."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyStNowHd", "")
    ap.add(body, SUI.panel("SkyyStNowBox", "well", h=ST_BOX_H))


def st_line(parent, ident, text, col):
    """One boost line (18 px, the setting kind) in a well: the text b.set. The vanilla ShrinkTextToFit with a 15 px floor (vanilla
    plain labels do it on PlaySoundPage / ParticleSpawnPage / PortalDeviceSummon #Title0): a line longer than the well (the
    Acrobatics "Skill tree:" line with every node, a long SkyyCooking / SkyyExploration hook line) shrinks instead of running past
    the well edge; a line that fits is drawn exactly as before. KIT-GAP 4: label() has no shrink= option, so the kind's own style
    (the kit's text_style with the setting kind's values) is swapped for the kit's text_style(..., shrink=ST_LINE_MIN), asserted once."""
    ap = SUI.Appends()
    ap.text(parent, ident, text, "setting", h=ST_LINE_H, col=col)
    par, mk = ap[-1]
    vs, _kc, kb, ku, ka, kw, ki, _where = SUI.LABELS["setting"]
    plain = "Style: %s; " % SUI.text_style(SUI.fs(vs), col, bold=kb, upper=ku, italic=ki, halign=ka, valign="Center", wrap=kw)
    shrunk = "Style: %s; " % SUI.text_style(SUI.fs(vs), col, bold=kb, upper=ku, italic=ki, halign=ka, valign="Center", wrap=kw,
                                            shrink=ST_LINE_MIN)
    assert isinstance(mk, str) and mk.count(plain) == 1 and "ShrinkTextToFit" in shrunk, (plain, mk)
    ap[-1] = (par, mk.replace(plain, shrunk))
    return ap


def st_next_head(ap, body, text="", col=None):
    """The LEVEL n+1 ADDS head #SkyyStNextHd (10 px over it)."""
    _sk_head(ap, body, "SkyyStNextHd", text, top=ST_HEAD_T, col=col)


def st_how(ap, body, text):
    """The separator and the how-to caption #SkyyStHow (wraps; b.set)."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyStHow", text, "caption", h=ST_HOW_H, wrap=True)


def st_nav(ap, body, gap):
    """The footer #SkyyStNav right-aligned (its left padding = the room the buttons leave: gap = an int or J()) with < BACK and TOP 10;
    SKILL TREE is appended by st_tree when that skill has a tree."""
    ap.add(body, SUI.button_row("SkyyStNav", align="right", left_margin=gap))
    ap.add("SkyyStNav", SUI.button("SkyyStBack", "< Back", "secondary", sound="cancel"))
    ap.add("SkyyStNav", SUI.button("SkyyStTop", "Top 10", "secondary", anchor={"left": 6}))


def st_tree():
    return SUI.Appends([("SkyyStNav", SUI.button("SkyyStTree", "Skill tree", "secondary", anchor={"left": 6}))])


def ov_shell():
    """The Overall page: the plain window, 0.4.6's ids kept for every frame part (root #SkyyOvPage, title bar #SkyyOvHead, title
    #SkyyOvHeadTxt, body #SkyyOvBody)."""
    return SUI.page_shell("SkyyOvF", OV_W, OV_H, "Overall Level", kind="plain", root_id="SkyyOvPage", bar_id="SkyyOvHead",
                          title_id="SkyyOvHeadTxt", body_id="SkyyOvBody")


def ov_top(ap, body, title, sub, fill, count_text, list_text):
    """Level line, average line, the bar, the SKILLS THAT COUNT head + the counted skills in a well."""
    ap.text(body, "SkyyOvTitle", title, "display", h=ST_TITLE_H, align="Center")
    ap.text(body, "SkyyOvSub", sub, "default", h=ST_SUB_H, align="Center")
    _sk_bar_row(ap, body, "SkyyOvBarRow", "SkyyOvBar", fill)
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyOvSkHd", count_text)
    ap.add(body, SUI.panel("SkyyOvSkBox", "well", h=OV_LIST_H + 2 * SUI.WELL_PAD))
    ap.text("SkyyOvSkBox", "SkyyOvSk", list_text, "setting", h=OV_LIST_H, col="white", wrap=True)
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyOvNowHd", "Boosts right now")
    ap.add(body, SUI.panel("SkyyOvNowBox", "well", h=OV_NOW_N * ST_LINE_H + 2 * SUI.WELL_PAD))


def ov_next(ap, body, text, col=None, box=True):
    """The OVERALL LEVEL n+1 ADDS head #SkyyOvNextHd and its well #SkyyOvNextBox (box=False: a spacer of its height - max level)."""
    _sk_head(ap, body, "SkyyOvNextHd", text, top=ST_HEAD_T, col=col)
    h = OV_NEXT_N * ST_LINE_H + 2 * SUI.WELL_PAD
    ap.add(body, SUI.panel("SkyyOvNextBox", "well", h=h) if box else SUI.spacer(h=h))


def ov_foot(ap, body):
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyOvHow", OV_HOW, "caption", h=OV_HOW_H, wrap=True)
    ap.add(body, SUI.button_row("SkyyOvNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyyOvNav", SUI.button("SkyyOvBack", "Back", "secondary", sound="cancel"))


def _sk_java(ap, prefix, indent, known=()):
    """The Java statements of one Appends (appends, then its b.set lines), checked first, indented for a build() source."""
    SUI.check_page(ap, prefix, known_parents=[SUI.render(k) for k in known])
    SUI.assert_proven(ap)
    return _SK_LF.join(indent + ln for ln in ap.java("b").split(_SK_LF))


def _sk_shell_java(sh, prefix, indent):
    SUI.check_page(sh.appends, prefix)
    SUI.assert_proven(sh)
    return _SK_LF.join(indent + ln for ln in sh.java("b").split(_SK_LF))


# ---- the Java pieces (J() = a local of the build() below; samples = what the checks read)
_I = SUI.J("i", "0")
_RH = SUI.J("rh", str(SK_ROW_H))
SK_SH = sk_shell()
SK_SHELL_JAVA = _sk_shell_java(SK_SH, "SkyySk", "  ")
_ap = SUI.Appends()
sk_overview(_ap, "SkyySkills")
SK_OVERVIEW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkills"])
SK_ROW_JAVA = _sk_java(sk_row(_I, _RH, SUI.J("pw", str(SK_PANEL_W[True])), SUI.J("tw", str(SK_TEXT_W[True])),
                              SUI.J("bw", str(SK_XP_W[True])), SUI.J("fill", "320"), SUI.J("col", _SK_COL),
                              SUI.J(PKG + ".SkillDefs.ICONS[sl]", "Tool_Pickaxe_Iron"), SUI.J("title", "Mining  12"),
                              SUI.J("prog", "1234 / 5000 XP to level 13")), "SkyySk", "      ", known=["SkyySkList"])
SK_BONUS_JAVA = _sk_java(sk_bonus(_I), "SkyySk", "        ", known=["SkyySkTxt" + _I])
SK_TREE_JAVA = _sk_java(sk_tree(_I, _RH), "SkyySk", "          ", known=["SkyySkRow" + _I])
SK_TREE_GAP_JAVA = _sk_java(sk_tree_gap(_I, _RH), "SkyySk", "          ", known=["SkyySkRow" + _I])
SK_STAT_JAVA = _sk_java(sk_stat(_I, _RH), "SkyySk", "      ", known=["SkyySkRow" + _I])
_ap = SUI.Appends()
sk_top(_ap, "SkyySkills")
SK_TOP_JAVA = _sk_java(_ap, "SkyySk", "  ", known=["SkyySkills"])
SK_TOP_EMPTY_JAVA = _sk_java(sk_top_empty(), "SkyySk", "    ", known=["SkyySkTop"])
_row = sk_top_row(_I, SUI.J("me"), [SUI.J('(i + 1) + "."', "1."), SUI.J("e[0]", "Skyy"),
                                     SUI.J('"Level " + ' + PKG + '.SkillDefs.levelOf(x)', "Level 12"),
                                     SUI.J(PKG + '.SkillDefs.fmt(x) + " XP"', "12.3k XP")])
_ap = SUI.Appends()
_ap.add("SkyySkTop", _row)
SK_TOP_ROW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkTop"])
_ap = SUI.Appends()
sk_top_foot(_ap, "SkyySkills", SUI.J('rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + ' + PKG
                                     + '.SkillDefs.levelOf(d[s]) + " - " + ' + PKG + '.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet"',
                                     "Your rank #1 of 3 - level 12 - 12.3k XP"))
SK_TOP_FOOT_JAVA = _sk_java(_ap, "SkyySk", "  ", known=["SkyySkills"])
ST_SH = st_shell(SUI.J("name", "Mining"))
ST_SHELL_JAVA = _sk_shell_java(ST_SH, "SkyyS", "  ")
_ap = SUI.Appends()
st_top(_ap, "SkyySkStats")
ST_TOP_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_BAR_JAVA = _sk_java(st_bar(SUI.J("fill", "300")), "SkyyS", "  ", known=["SkyyStBarRow"])
ST_NOTE_JAVA = _sk_java(st_note(), "SkyyS", "    ", known=["SkyySkStats"])
ST_NOTE_GAP_JAVA = _sk_java(st_note_gap(), "SkyyS", "    ", known=["SkyySkStats"])
_ap = SUI.Appends()
st_mid(_ap, "SkyySkStats")
ST_MID_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_NOW_JAVA = _sk_java(st_line("SkyyStNowBox", "SkyyStNow" + _I, SUI.J("(String) now.get(i)", "+5 max Health"), "white"), "SkyyS",
                       "    ", known=["SkyyStNowBox"])
_ap = SUI.Appends()
st_next_head(_ap, "SkyySkStats")
_ap.add("SkyySkStats", SUI.panel("SkyyStNextBox", "well", h=ST_BOX_H))
ST_NEXT_HD_JAVA = _sk_java(_ap, "SkyyS", "      ", known=["SkyySkStats"])
ST_NEXT_JAVA = _sk_java(st_line("SkyyStNextBox", "SkyyStNext" + _I, SUI.J("(String) nx.get(i)", "+0.1 max Health"), "buttonText"),
                        "SkyyS", "        ", known=["SkyyStNextBox"])
_ap = SUI.Appends()
st_next_head(_ap, "SkyySkStats", "Max level reached - nothing more to unlock", col="gold")
_ap.add("SkyySkStats", SUI.spacer(h=ST_BOX_H))
ST_MAX_JAVA = _sk_java(_ap, "SkyyS", "      ", known=["SkyySkStats"])
ST_LEGACY_GAP_JAVA = _sk_java(SUI.Appends([("SkyySkStats", SUI.spacer(h=ST_HEAD_T + ST_HEAD_H + ST_HEAD_B + ST_BOX_H))]), "SkyyS", "    ",
                              known=["SkyySkStats"])
_ap = SUI.Appends()
st_how(_ap, "SkyySkStats", SUI.J("how(s)", "Earn XP by mining stone and ores - rarer ores pay more"))
ST_HOW_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
_ap = SUI.Appends()
st_nav(_ap, "SkyySkStats", SUI.J("tree != null ? %d : %d" % (ST_NAV_GAP[True], ST_NAV_GAP[False]), str(ST_NAV_GAP[True])))
ST_NAV_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_TREE_JAVA = _sk_java(st_tree(), "SkyyS", "    ", known=["SkyyStNav"])
OV_SH = ov_shell()
OV_SHELL_JAVA = _sk_shell_java(OV_SH, "SkyyOv", "  ")
_ap = SUI.Appends()
ov_top(_ap, "SkyyOvBody", SUI.J('"Level " + lv + " of " + ' + PKG + '.SkillDefs.MAX', "Level 12 of 100"), SUI.J("sub", "Average of your skills 12.4"),
       SUI.J("fill", "240"), SUI.J('"Skills that count (" + sc[1] + ")"', "Skills that count (9)"),
       SUI.J(PKG + ".Overall.listText(u, d)", "Mining 14 - Foraging 9 - Farming 3"))
OV_TOP_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])
OV_NOW_JAVA = _sk_java(st_line("SkyyOvNowBox", "SkyyOvNow" + _I, SUI.J("(String) now.get(i)", "+6 max Health"), "white"), "SkyyOv", "    ",
                       known=["SkyyOvNowBox"])
_ap = SUI.Appends()
ov_next(_ap, "SkyyOvBody", "Max Overall Level reached", col="gold", box=False)
OV_MAX_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])
_ap = SUI.Appends()
ov_next(_ap, "SkyyOvBody", SUI.J('"Overall Level " + (lv + 1) + " adds"', "Overall Level 13 adds"))
OV_NEXT_HD_JAVA = _sk_java(_ap, "SkyyOv", "    ", known=["SkyyOvBody"])
OV_NEXT_JAVA = _sk_java(st_line("SkyyOvNextBox", "SkyyOvNext" + _I, SUI.J("(String) nx.get(i)", "+0.5 max Health"), "buttonText"), "SkyyOv",
                        "      ", known=["SkyyOvNextBox"])
_ap = SUI.Appends()
ov_foot(_ap, "SkyyOvBody")
OV_FOOT_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])


# ---- build-time check of whole sample states: the pieces put together the way the build() methods emit them, with concrete values
def _sk_whole(parts, prefix, body, inner_h, lists=()):
    whole = SUI.Appends()
    for p in parts:
        whole += p
    SUI.check_page(whole, prefix)
    SUI.assert_proven(whole)
    left = SUI.fit([SUI.used_height(whole, body)], inner_h, body)
    assert left == 0, "#%s is not filled exactly: %d px left" % (body, left)
    for lid, lh in lists:
        SUI.fit([SUI.used_height(whole, lid)], lh - 2 * SUI.WELL_LIST_PAD, lid)
    return whole


def sk_state_overview(trees, rows):
    """rows = [(slot, title, prog, fill, tree)]; trees = SkyyTrees running."""
    sh = sk_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    sk_overview(ap, sh.body)
    ap.sets.append(("SkyySkOv", "Text", "Overall Level 12  -  average 12.4 of 9 skills"))
    parts.append(ap)
    for i, (sl, title, prog, fill, tree) in enumerate(rows):
        acro = sl == ACRO_SLOT
        rh = SK_ACRO_H if acro else SK_ROW_H
        parts.append(sk_row(str(i), rh, SK_PANEL_W[trees], SK_TEXT_W[trees], SK_XP_W[trees], fill, SLOT_COLORS[sl], SLOT_ICONS[sl], title,
                            prog))
        if acro:
            b = sk_bonus(str(i))
            b.sets.append(("SkyySkBonus", "Text", "Speed 5%   Jump 0.3 blocks   Fall damage -10%"))
            parts.append(b)
        if trees:
            parts.append(sk_tree(str(i), rh) if tree else sk_tree_gap(str(i), rh))
        parts.append(sk_stat(str(i), rh))
    whole = _sk_whole(parts, "SkyySk", sh.body, sh.inner_h, [("SkyySkList", SK_LIST_H)])
    for i in range(len(rows)):
        assert SUI.used_width(whole, "SkyySkRow%d" % i) == SK_LIST_IN, "row %d is %d px of %d" % (i, SUI.used_width(whole, "SkyySkRow%d" % i),
                                                                                            SK_LIST_IN)
    return whole


def sk_state_top(rows, me_at, rank_text):
    sh = sk_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    sk_top(ap, sh.body)
    parts.append(ap)
    if not rows:
        parts.append(sk_top_empty())
    for i, (nm, lv, xp) in enumerate(rows[:10]):
        a = SUI.Appends()
        a.add("SkyySkTop", sk_top_row(str(i), i == me_at, ["%d." % (i + 1), nm, "Level %d" % lv, xp + " XP"]))
        parts.append(a)
    ap = SUI.Appends()
    sk_top_foot(ap, sh.body, rank_text)
    parts.append(ap)
    return _sk_whole(parts, "SkyySk", sh.body, sh.inner_h, [("SkyySkTop", SK_TOP_LIST_H)])


def st_state(name, fill, note, now, nxt, legacy, maxed, tree):
    sh = st_shell(name)
    parts = [sh.appends]
    ap = SUI.Appends()
    st_top(ap, sh.body)
    ap.sets += [("SkyyStTitle", "Text", name + " - level 12 of 100"), ("SkyyStSub", "Text", "1.2k / 5k XP to level 13  (3.8k to go)")]
    parts += [ap, st_bar(fill)]
    if note:
        n = st_note()
        n.sets.append(("SkyyStNote", "Text", "You are not a Mage right now - these boosts work while you are one"))
        parts.append(n)
    else:
        parts.append(st_note_gap())
    ap = SUI.Appends()
    st_mid(ap, sh.body)
    ap.sets.append(("SkyyStNowHd", "Text", "Boosts right now (level 12)"))
    parts.append(ap)
    for i, t in enumerate(now[:ST_LINES]):
        parts.append(st_line("SkyyStNowBox", "SkyyStNow%d" % i, t, "white"))
    if legacy:
        parts.append(SUI.Appends([(sh.body, SUI.spacer(h=ST_HEAD_T + ST_HEAD_H + ST_HEAD_B + ST_BOX_H))]))
    elif maxed:
        ap = SUI.Appends()
        st_next_head(ap, sh.body, "Max level reached - nothing more to unlock", col="gold")
        ap.add(sh.body, SUI.spacer(h=ST_BOX_H))
        parts.append(ap)
    else:
        ap = SUI.Appends()
        st_next_head(ap, sh.body)
        ap.add(sh.body, SUI.panel("SkyyStNextBox", "well", h=ST_BOX_H))
        ap.sets.append(("SkyyStNextHd", "Text", "Level 13 adds"))
        parts.append(ap)
        for i, t in enumerate(nxt[:ST_LINES]):
            parts.append(st_line("SkyyStNextBox", "SkyyStNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    st_how(ap, sh.body, "Earn XP by mining stone and ores - rarer ores pay more")
    st_nav(ap, sh.body, ST_NAV_GAP[bool(tree)])
    parts.append(ap)
    if tree:
        parts.append(st_tree())
    whole = _sk_whole(parts, "SkyyS", sh.body, sh.inner_h, [("SkyyStNowBox", ST_BOX_H + 2 * SUI.WELL_LIST_PAD - 2 * SUI.WELL_PAD)])
    nav_want = 3 * SUI.BTN_MIN_W + 12 if tree else 2 * SUI.BTN_MIN_W + 6     # < BACK / TOP 10 (/ SKILL TREE) + their 6 px gaps
    assert SUI.used_width(whole, "SkyyStNav") == nav_want, (tree, SUI.used_width(whole, "SkyyStNav"), nav_want)
    assert ST_NAV_GAP[bool(tree)] + nav_want == SK_IN_W, "the footer's left padding right-aligns it in the body"
    return whole


def ov_state(maxed, now, nxt):
    sh = ov_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    ov_top(ap, sh.body, "Level 12 of 100", "Average of your skills 12.4 - Overall Level 13 at an average of 13.0", 0 if maxed else 240,
           "Skills that count (9)", "Mining 14 - Foraging 9 - Farming 3 - Acrobatics 20 - Alchemy 1 - Smithing 2 - Cooking 0 - Exploration 5 "
           "- Divinity 18 (your class)")
    parts.append(ap)
    for i, t in enumerate(now[:OV_NOW_N]):
        parts.append(st_line("SkyyOvNowBox", "SkyyOvNow%d" % i, t, "white"))
    ap = SUI.Appends()
    if maxed:
        ov_next(ap, sh.body, "Max Overall Level reached", col="gold", box=False)
    else:
        ov_next(ap, sh.body, "Overall Level 13 adds")
    parts.append(ap)
    if not maxed:
        for i, t in enumerate(nxt[:OV_NEXT_N]):
            parts.append(st_line("SkyyOvNextBox", "SkyyOvNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    ov_foot(ap, sh.body)
    parts.append(ap)
    return _sk_whole(parts, "SkyyOv", sh.body, sh.inner_h)


_rows9 = [(sl, "Class skill - choose a class with /class", "Your combat skill is your class skill", 0, False) if sl == COMBAT_SLOT
          else (sl, SLOT_LABELS[sl] + "  12", "1.2k / 5k XP to level 13", 200, sl in (0, 1, 2, 12)) for sl in SK_ROW_SLOTS]
_sk_checked = [sk_state_overview(True, _rows9), sk_state_overview(False, _rows9),
               sk_state_top([("Skyy", 40, "1.2m"), ("Alex, the 2nd", 12, "12.3k"), ("Sam (profile 2)", 1, "55")], 0,
                            "Your rank #1 of 3 - level 40 - 1.2m XP"),
               sk_state_top([("P%d" % n, 50 - n, "%dk" % (99 - n)) for n in range(12)], -1, "Your rank #11 of 12 - level 39 - 88k XP"),
               sk_state_top([], -1, "You are not ranked yet"),
               st_state("Mining", 300, False, ["+0.25% chance to double the drops of mined blocks"] * 7, ["+0.005% chance"] * 7, False, False, True),
               st_state("Fury", 0, True, ["+1 max Health"], ["+0.2% damage with Berserker weapons"], False, False, False),
               st_state("Combat", 0, False, ["No class yet - choose one with /class to start leveling combat"], [], True, False, False),
               st_state("Cooking", 600, False, ["Food you cook gets stronger"], [], False, True, True),
               ov_state(False, ["+6 max Health (0.5 per Overall Level)", "+2.4 max Mana (0.2 per Overall Level)", "Base Mana 10"],
                        ["+0.5 max Health", "+0.2 max Mana"]),
               ov_state(True, ["+50 max Health (0.5 per Overall Level)"], [])]
print("skills pages: /skills %d x %d, Stats %d x %d, Overall %d x %d on %s - %d sample states checked (check_page, assert_proven, heights)"
      % (SK_W, SK_H, STATS_W, STATS_H, OV_W, OV_H, KIT_ID, len(_sk_checked)))
# ---- SKILLS PAGE BLOCK END
'''
rep("@@SKLOOK@@\n", NEW_LOOK)

NEW_SK_BUILD = r'''SK_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  // 0.4.7: the plain vanilla window (title SKILLS / TOP 10 - <SKILL>), body = 0.4.6's root #SkyySkills - kit markup
{SK_SHELL_JAVA}
  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{
    int cs = {PKG}.SkillClass.slot(u);
    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;
    int[] osc = {PKG}.Overall.sums(u, d);
    // the Overall well + OVERALL button, the list well, the hint caption
{SK_OVERVIEW_JAVA}
    b.set("#SkyySkOv.Text", "Overall Level " + {PKG}.Overall.level(osc) + "  -  average " + {PKG}.Overall.avg({PKG}.Overall.tenths(osc)) + " of " + osc[1] + " skills");
    ev.addEventBinding({BT}.Activating, "#SkyySkOvStat", {EVD}.of("a", "skstatov"));
    boolean trees = {PKG}.SkillBonus.treesOn();
    int pw = trees ? {SK_PANEL_W[True]} : {SK_PANEL_W[False]};
    int tw = trees ? {SK_TEXT_W[True]} : {SK_TEXT_W[False]};
    int bw = trees ? {SK_XP_W[True]} : {SK_XP_W[False]};
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;
      if (classRow && cs >= 0) sl = cs;
      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(total);
      long cur = {PKG}.SkillDefs.intoLevel(total);
      long need = {PKG}.SkillDefs.needFor(total);
      int fill = need > 0L ? (int) ((long) bw * cur / need) : bw;
      if (fill < 0) fill = 0;
      if (fill > bw) fill = bw;
      String prog = need > 0L ? ({PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1)) : ("MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP");
      String col = {PKG}.SkillDefs.COLORS[sl];
      String title = {PKG}.SkillDefs.LABELS[sl] + "  " + lv;
      if (classRow) {{
        if (cs >= 0) title = {PKG}.SkillClass.skillName(u, cs) + "  " + lv;
        else {{
          title = "Class skill - choose a class with /class";
          prog = total > 0L ? "Old Combat XP (level " + lv + ") moves to the first class you choose" : "Your combat skill is your class skill";
          fill = 0;
        }}
      }}
      boolean acroRow = sl == {PKG}.SkillDefs.ACROBATICS;
      int rh = acroRow ? {SK_ACRO_H} : {SK_ROW_H};
      // the row: panel, icon, name, XP bar, progress line (texts b.set)
{SK_ROW_JAVA}
      if (acroRow) {{
{SK_BONUS_JAVA}
        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));
      }}
      if (trees) {{
        if ({PKG}.SkillBonus.treeAvailable(sl)) {{
{SK_TREE_JAVA}
          ev.addEventBinding({BT}.Activating, "#SkyySkTree" + i, {EVD}.of("a", "sktree" + sl));
        }} else {{
{SK_TREE_GAP_JAVA}
        }}
      }}
{SK_STAT_JAVA}
      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));
    }}
    return;
  }}
  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);
  // the column heads + the list well
{SK_TOP_JAVA}
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) {{
{SK_TOP_EMPTY_JAVA}
  }}
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
{SK_TOP_ROW_JAVA}
  }}
  int rank = {PKG}.SkillTop.rankOf(rows, u);
  // the rank line + the footer (BACK)
{SK_TOP_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}"""
for _piece in (SK_SHELL_JAVA, SK_OVERVIEW_JAVA, SK_ROW_JAVA, SK_BONUS_JAVA, SK_TREE_JAVA, SK_TREE_GAP_JAVA, SK_STAT_JAVA, SK_TOP_JAVA,
               SK_TOP_EMPTY_JAVA, SK_TOP_ROW_JAVA, SK_TOP_FOOT_JAVA):
    assert _piece in SK_BUILD_SRC, "kit Java changed on its way into the build() source"   # the f-string recipe: verbatim
page.addMethod(CtNewMethod.make(SK_BUILD_SRC, page))
'''
rep("@@SKBUILD@@\n", NEW_SK_BUILD)

NEW_ST_BUILD = r'''assert STBARW == SK_BIG_BAR_W, "the Stats bar is the 600 px bar the look block budgets"
ST_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;
  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;
  int cs = {PKG}.SkillClass.slot(u);
  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;
  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(total);
  long cur = {PKG}.SkillDefs.intoLevel(total);
  long need = {PKG}.SkillDefs.needFor(total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};
  if (fill < 0) fill = 0;
  if (fill > {STBARW}) fill = {STBARW};
  boolean legacy = s == {PKG}.SkillDefs.COMBAT;
  if (legacy) fill = 0;
  String col = {PKG}.SkillDefs.COLORS[s];
  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);
  // 0.4.7: the plain vanilla window (title = the skill name), body = 0.4.6's root #SkyySkStats; the title, XP line and bar row
{ST_SHELL_JAVA}
{ST_TOP_JAVA}
  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);
  String sub;
  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";
  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";
  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";
  b.set("#SkyyStSub.Text", sub);
{ST_BAR_JAVA}
  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{
    String cn = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];
    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";
{ST_NOTE_JAVA}
    b.set("#SkyyStNote.Text", "You are not " + art + cn + " right now - these boosts work while you are one");
  }} else {{
{ST_NOTE_GAP_JAVA}
  }}
  // the separator, BOOSTS RIGHT NOW + its well
{ST_MID_JAVA}
  b.set("#SkyyStNowHd.Text", legacy ? "Your combat" : "Boosts right now (level " + lv + ")");
  java.util.ArrayList now = lines(u, s, lv, false);
  for (int i = 0; i < now.size() && i < {ST_LINES}; i++) {{
{ST_NOW_JAVA}
  }}
  if (!legacy) {{
    if (need > 0L) {{
{ST_NEXT_HD_JAVA}
      b.set("#SkyyStNextHd.Text", "Level " + (lv + 1) + " adds");
      java.util.ArrayList nx = lines(u, s, lv, true);
      for (int i = 0; i < nx.size() && i < {ST_LINES}; i++) {{
{ST_NEXT_JAVA}
      }}
    }} else {{
{ST_MAX_JAVA}
    }}
  }} else {{
{ST_LEGACY_GAP_JAVA}
  }}
  // the separator + the how-to caption, the footer (< BACK, TOP 10, SKILL TREE when that skill has a tree)
{ST_HOW_JAVA}
  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;
{ST_NAV_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
  if (tree != null) {{
{ST_TREE_JAVA}
    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
}}"""
for _piece in (ST_SHELL_JAVA, ST_TOP_JAVA, ST_BAR_JAVA, ST_NOTE_JAVA, ST_NOTE_GAP_JAVA, ST_MID_JAVA, ST_NOW_JAVA, ST_NEXT_HD_JAVA, ST_NEXT_JAVA,
               ST_MAX_JAVA, ST_LEGACY_GAP_JAVA, ST_HOW_JAVA, ST_NAV_JAVA, ST_TREE_JAVA):
    assert _piece in ST_BUILD_SRC, "kit Java changed on its way into the build() source"
spg.addMethod(CtNewMethod.make(ST_BUILD_SRC, spg))
'''
rep("@@STBUILD@@\n", NEW_ST_BUILD)

rep("@@OVHEAD@@\n", '''# ================= OverallPage (0.4.6): the Overall Level page (research/Overall-Level-Spec.md 2.8.2 / 4.7) =================
# 0.4.7: its vanilla look (0.4.6: hand-copied style strings + a client-folder texture check) comes from the shared kit now - the
# SKILLS PAGES LOOK block above (ov_* functions, OV_*_JAVA pieces); every value is proven against Assets.zip by SUI.verify().
OVBARW = 600
assert OVBARW == SK_BIG_BAR_W, "the Overall bar is the 600 px bar the look block budgets"
''')

NEW_OV_BUILD = r'''OV_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int[] sc = {PKG}.Overall.sums(u, d);
  int lv = {PKG}.Overall.level(sc);
  int t = {PKG}.Overall.tenths(sc);
  boolean max = lv >= {PKG}.SkillDefs.MAX;
  int fill = max ? {OVBARW} : (t % 10) * ({OVBARW} / 10);
  if (fill < 0) fill = 0;
  if (fill > {OVBARW}) fill = {OVBARW};
  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";
  // 0.4.7: the plain vanilla window (0.4.6's ids), the level + average lines, the bar, SKILLS THAT COUNT, BOOSTS RIGHT NOW - kit markup
{OV_SHELL_JAVA}
{OV_TOP_JAVA}
  java.util.ArrayList now = {PKG}.Overall.nowLines(u, lv);
  for (int i = 0; i < now.size() && i < {OV_NOW_N}; i++) {{
{OV_NOW_JAVA}
  }}
  if (max) {{
{OV_MAX_JAVA}
  }} else {{
{OV_NEXT_HD_JAVA}
    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv);
    for (int i = 0; i < nx.size() && i < {OV_NEXT_N}; i++) {{
{OV_NEXT_JAVA}
    }}
  }}
  // the separator, the how-to caption, the footer (BACK)
{OV_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyOvBack", {EVD}.of("a", "ovback"));
}}"""
for _piece in (OV_SHELL_JAVA, OV_TOP_JAVA, OV_NOW_JAVA, OV_MAX_JAVA, OV_NEXT_HD_JAVA, OV_NEXT_JAVA, OV_FOOT_JAVA):
    assert _piece in OV_BUILD_SRC, "kit Java changed on its way into the build() source"
opg.addMethod(CtNewMethod.make(OV_BUILD_SRC, opg))
'''
rep("@@OVBUILD@@\n", NEW_OV_BUILD)

# ================================================================================================ self-checks on the generated script
new_lines = s.split(LF)
_blk = s.split("# ---- SKILLS PAGE BLOCK START")[1].split("# ---- SKILLS PAGE BLOCK END")[0]
_sk_src = block('SK_BUILD_SRC = f"""', 'page.addMethod(CtNewMethod.make(SK_BUILD_SRC, page))')
_st_src = block('ST_BUILD_SRC = f"""', 'spg.addMethod(CtNewMethod.make(ST_BUILD_SRC, spg))')
_ov_src = block('OV_BUILD_SRC = f"""', 'opg.addMethod(CtNewMethod.make(OV_BUILD_SRC, opg))')
for _src, _keep in ((_sk_src, KEEP_SK), (_st_src, KEEP_ST), (_ov_src, KEEP_OV)):
    _nl = _src.split(LF)
    for _ln in _keep:
        assert _nl.count(_ln) == 1, "0.4.7 build() lost a kept 0.4.6 line: " + _ln
# the same text expressions, now b.set (in a build() source or as a kit J() in the look block)
for _t in ('SUI.J("title", ', 'SUI.J("prog", ', '? "Skills" : "Top 10 - " + \' + PKG + \'.SkillDefs.LABELS[this.view]', '"Nobody has any XP yet."',
           'SUI.J(\'(i + 1) + "."\'', 'SUI.J("e[0]", ', 'SUI.J(\'"Level " + \' + PKG + \'.SkillDefs.levelOf(x)\'', 'SUI.J(PKG + \'.SkillDefs.fmt(x) + " XP"\'',
           'rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + \' + PKG', 'SK_HINT = "Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins"',
           'SUI.J("(String) now.get(i)", ', 'SUI.J("(String) nx.get(i)", ', '"Max level reached - nothing more to unlock"', 'SUI.J("how(s)", ',
           'SUI.J(\'"Level " + lv + " of " + \' + PKG + \'.SkillDefs.MAX\'', 'SUI.J(\'"Skills that count (" + sc[1] + ")"\'', 'SUI.J(PKG + ".Overall.listText(u, d)", ',
           '"Boosts right now"', '"Max Overall Level reached"', 'SUI.J(\'"Overall Level " + (lv + 1) + " adds"\'', 'OV_HOW = ("The Overall Level is the average'):
    assert _t in _blk, "0.4.7 dropped a 0.4.6 page text: " + _t
for _t in ('b.set("#SkyyStNote.Text", "You are not " + art + cn + " right now - these boosts work while you are one");',
           'b.set("#SkyyStNowHd.Text", legacy ? "Your combat" : "Boosts right now (level " + lv + ")");',
           'b.set("#SkyyStNextHd.Text", "Level " + (lv + 1) + " adds");'):
    assert _st_src.count(_t) == 1, "0.4.7 dropped a 0.4.6 Stats text: " + _t
assert OLD_OV.count("Other classes' skills never count (a new class is a new profile).") == 1 and \
    "Other classes' skills \"\n          \"never count (a new class is a new profile).\")" in _blk, "the Overall how-to text"
# every binding line of 0.4.6, in the same order
assert [ln.strip() for ln in new_lines if "ev.addEventBinding(" in ln] == [ln.strip() for ln in BIND0], "event bindings changed"
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
for k in KEEP:
    for _o, _n in SLOT_FIX:     # the one planned change inside a KEEP block: the slot values formatted from SKILL_ROW_SLOTS
        k = k.replace(_o, _n)
    assert k in s, "a block that must stay 0.4.6's changed: %s" % k[:80]
assert sum(1 for k in KEEP for _o, _n in SLOT_FIX if _o in k) == len(SLOT_FIX), "every SLOT_FIX edit sits in a KEEP block"
assert "acro = sl == 4" not in s and "SK_ROW_SLOTS = [" not in s and "SK_ROW_SLOTS = SKILL_ROW_SLOTS" in s, "the look block reads the one list"
# no 0.4.6 custom look left in the page code (colours of the old dark-blue pages, the green button triple, the old VAN_* strings)
_pages = s.split("# ================= /skills page (inline")[1].split("# ================= 0.4.3 ADMIN CONFIG")[0]
for c in ("#0b1524", "#27463a", "#3b6b54", "#172a22", "#dcffe8", "#142030", "#22324a", "#e6fff0", "#b8c8d8", "#d8c0ff", "#7f94a8",
          "#9fb8cc", "#e6f0ff", "#c9dff0", "#dfe8f0", "#bfe8c8", "TextButtonStyle(Default: (Background: #", "String bs = ", "VAN_", "HEAD + ",
          "TexturePath", "appendInline(\"#SkyySkills\", \"Label", "Label {{ Anchor"):
    assert c not in _pages, "0.4.6 custom look left: " + c
assert _pages.count("appendInline(") == 0, "every append of the three pages comes from the kit now"
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("# ---- SKILLS PAGE BLOCK START") < s.index("SK_BUILD_SRC = f") < s.index("ST_BUILD_SRC = f") < s.index("OV_BUILD_SRC = f")
assert s.index('public static String safe(String t)') < s.index("SK_BUILD_SRC = f") < s.index("# ================= StatsPage (0.3)"), \
    "javassist: SkillsPage.build keeps its place (after safe, before the other pages and its handleDataEvent)"
assert s.index("public static String how(int s)") < s.index("ST_BUILD_SRC = f") < s.index('spg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent('), \
    "javassist: StatsPage.build after lines / how, before handleDataEvent"
assert s.index("OV_BUILD_SRC = f") < s.index('opg.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(') < \
    s.index('page.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent('), "the page handlers keep their order"
assert "{KIT_ID}" in s and 'VERSION = "0.4.7"' in s and "@@" not in s
assert all(ord(ch) < 128 for ch in s), "the build script stays ASCII"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.6
print("wrote", dst, "(%d lines; 0.4.6 had %d)" % (s.count(LF), OLD.count(LF)))
