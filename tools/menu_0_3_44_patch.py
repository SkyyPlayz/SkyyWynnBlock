"""Derive SkyyMenu/build_skyymenu_0.3.44.py from the LIVE SkyyMenu 0.3.43 (python tools/menu_0_3_44_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_43_patch.py -> 0.3.43 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.44. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.43 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.44.py is its own file.

0.3.44 (2026-10-22) = UI ROUND R1 PART A (research/UI-Queue-Spec.md items 2 + 6; full round with SkyyHud 0.3.35 + SkyyQuests 0.4.3).
  Skyy (2026-10-22): "they were able to tie the menu to Left alt" + "their quest menu uses double crouch to expand to bigger or shrink" +
  popup "Fold the quest tracker (Recommended)" + "work through your whole list."
  1. DOUBLE-TAP CROUCH = A CHOICE (Settings > General, the row "Double-tap crouch"): Fold quest tracker | Open the menu | Nothing. ONE
     detector (MenuHotkey.step, unchanged: two crouch presses within menu.hotkeyGapMs while standing on the ground, the cooldown); on fire
     HotkeyOpen asks the player's choice: Fold = SkyyHud 0.3.35's hud:fn:questFold apply(Object[] { UUID, "toggle" }) on the world thread -
     TRUE = folded / unfolded, done (HotkeyOpen.FOLDED); missing / FALSE (an older SkyyHud, no SkyyQuests) = the Menu opens exactly as
     0.3.43 (FOLD_FELL), so the gesture never silently dies. Open the menu = 0.3.43. Nothing = nothing (the old switch OFF).
     STORAGE (no file is rewritten): the old switch menu.hotkey stays (OFF = Nothing; settings:fn:get / set keep working for it) + a new
     own-choice key menu.crouchfold (true = Fold, false = Open the menu), written only when the player clicks the row.
     THE DEFAULT CHANGE (PROJECT-RULES 4, the "untouched default only" rule, as a read-time mapping instead of a file migration): a player
     with no menu.crouchfold line gets: menu.hotkey OFF (own or server default) -> Nothing (kept); an OWN menu.hotkey=true line (the player
     chose ON in /settings before 0.3.44) -> Open the menu (their choice kept); the untouched default (no menu.hotkey line) -> Fold quest
     tracker (Skyy's new default) - or, fix pass 2, the SERVER default when the owner set one: Server Setup -> Menu row "Double-tap
     crouch default: fold quests" (menu.crouchDefault, ON = Fold / OFF = Open the menu; the menu.crouchfold line of
     settings-defaults.properties, the menu.tooltipsDefault pattern; "Nothing" for everyone stays menu.hotkey OFF in the defaults table).
     So an owner whose players should keep opening the Menu sets it OFF. No player file is rewritten and no file changes until the
     owner edits that row (the kit versions + logs it then), so there is nothing to snapshot or undo; Reset all returns to the server
     default; rolling back to 0.3.43 reads every file exactly as before (menu.crouchfold is ignored).
     DEVIATION from PROJECT-RULES 4 (one-time file migration with History snapshot / Undo / run-once marker): deliberate - nothing is
     rewritten, the new default is a read-time mapping that only applies to players with no own line (the same effect, no file risk).
     Crouch-cast guard: NOT built - SkyyClasses publishes no class:lastcast:<uuid> (spec 13.2: "else the guard is dropped"); a double tap
     that is part of two crouch-casts only folds / unfolds the tracker (cosmetic).
  2. BRIDGE FLAGS for SkyyHud (plain Strings, the SoundSw publication: at join, on every change of the three keys, Reset all, the 30 s
     sweep, removed when the player leaves / at shutdown): menu:walkkey:<uuid> = "1" while the Walk key opens the Menu (Server Setup
     menu.walkKey on AND the player's menu.walkmenu on) else "0" (SkyyHud's Keys widget shows ALT - Menu only on "1");
     menu:crouch:<uuid> = "fold" / "menu" / "off" (the folded tracker's hint row).
  3. STATS BY SOURCE (Skills > Your Stats; spec item 6, Skyy's four power sources): the stat rows of Main and Combat are TABLE rows -
     Stat | Base | Gear | Charms | Pets | Trees | Class | Total (a caption header row under each section head; cells 16 bold End-aligned:
     a part that helps green #7ee08a, one that costs red #ff7a7a, nothing a dim "-" #7f93a6, Base of Health / Mana / Stamina white
     #d6e4ee (an absolute value); Total bold gold #e8c25a - Style Guide 15). Rows that are not split by source (Speed, Jump Height, Fall
     Damage, Mana Regen, Health Regen, the element groups, Fortune, Wisdom) keep their words in a text row (name | where it comes from |
     total) - the same Total column. A Sources legend closes the list; its last line says Total is the listed parts only (SkyyGear's
     Skill Trees 3 combat rows and the Rebirth damage / defence % are applied but not published yet).
     VERIFIED before splitting (spec 13.1): gear:stats:<uuid> does NOT include Charms / Pets / Trees - SkyyGear 0.3.38's GearTick publishes
     GearStats.totalsInv(u, inv, false) (withExtra false: gear:extra, pets:stats, GearV3.combat and Weapon Tempering are added only for
     combat). So Gear = gear:stats, Charms = gear:extra (SkyyAccessories), Pets = pets:stats (summed, floored per stat as SkyyGear does),
     Trees = gear:extras:<uuid> (SkyyTrees' posts) ONLY while SkyyGear lists "gear:extras" in tree:reads:SkyyGear (else SkyyGear does not
     apply them - not shown). Health / Mana / Stamina from the EntityStatMap MAX additive modifiers by key: skyygear_ Gear, skyyacc_
     Charms, skyypet_ Pets, skyytree_ + skyyskill_rebirth (the Rebirth Nexus) Trees, skyyskill_class Class, the rest Base (the game,
     armour, Overall / skill levels, base Mana). Defense: the skill Defense (skill:def) in Base. Class Weapon Damage: the class skill's
     level part in Base, the class balance in Class.
  No new command, permission, page, system or saved-data format; ONE new Server Setup row (menu.crouchDefault, fix pass 2). ROLLBACK to 0.3.43: safe (the gesture opens the Menu again,
  menu.crouchfold lines are ignored, the flags simply stay unread / are not published).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.43.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.44.py"))
assert P.has('VERSION = "0.3.43"\n') and P.has("tools/menu_0_3_43_patch.py") and P.has("WALK_COOLED") and not P.has("menu.crouchfold"), \
    "not the generated SkyyMenu 0.3.43 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.44: UI round R1 part A (notes: tools/menu_0_3_44_patch.py): double-tap crouch = a choice (Fold quest tracker via SkyyHud's
       hud:fn:questFold - the default for untouched players - / Open the menu / Nothing); the menu:walkkey / menu:crouch bridge flags;
       Your Stats by source (Base / Gear / Charms / Pets / Trees / Class / Total).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.44.py.
''')
P.rep('VERSION = "0.3.43"\n', 'VERSION = "0.3.44"\n')

# ================================================================================================ 1: the choice row (texts + storage keys)
P.rep('''                  "Your Walk key (Alt) or double-tap crouch - open the menu (/settings)",   # 0.3.42
''', '''                  "Your Walk key (Alt) opens the menu, double-tap crouch folds quests (/settings)",   # 0.3.42; 0.3.44
''')
P.rep('''    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
''', '''    # 0.3.44 (Skyy popup 2026-10-22 "Fold the quest tracker (Recommended)"): the row is a CHOICE now - SettingsPage draws three buttons
    ("menu.hotkey",          "general",     "Double-tap crouch",            "Tap crouch twice quickly while standing: fold the quest tracker, open the Menu, or nothing", "SkyyMenu"),
''')
P.rep('''WALK_SW_KEY = "menu.walkmenu"   # 0.3.42: the Walk key (Alt) player switch (MenuHotkey.walkStep / HotkeyOpen)
''', '''WALK_SW_KEY = "menu.walkmenu"   # 0.3.42: the Walk key (Alt) player switch (MenuHotkey.walkStep / HotkeyOpen)
CFOLD_KEY = "menu.crouchfold"   # 0.3.44: the double-tap crouch choice's own key (true = Fold quest tracker, false = Open the menu; no row of its own)
KEY_FLAG, CROUCH_FLAG = "menu:walkkey:", "menu:crouch:"   # 0.3.44: + <uuid> on the bridge for SkyyHud ("1"/"0"; "fold"/"menu"/"off")
QFOLD_FN = "hud:fn:questFold"   # 0.3.44: SkyyHud 0.3.35's fold function (apply(Object[] { UUID, "toggle" }) -> Boolean)
''')
P.rep('''     "Most time between the two crouch presses that open the SkyWynn Menu (double-tap crouch).",
''', '''     "Most time between the two presses of the double-tap crouch (fold the tracker or open the Menu).",
''')
P.rep('''     "Least time between two menu opens by double-tap crouch, per player.",
''', '''     "Least time between two double-tap crouches that fold the tracker or open the Menu, per player.",
''')
# the choice row's markup (kit buttons; the ON / OFF looks Skyy approved for the selected one)
P.rep('''SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]
''', '''# 0.3.44: the double-tap crouch CHOICE row: three buttons instead of ON / OFF (the selected one green, Nothing red), the name / help column
# narrower by the extra width
STG_CH_LABELS = ["Fold quest tracker", "Open the menu", "Nothing"]
STG_CH_W = 230
STG_TXTC_W = STG_TXT_W - (3 * STG_CH_W + 2 * 10 - (120 + 10 + 120))
UI_S["STXTCB"] = " { Anchor: (Width: %d, Height: 52); LayoutMode: Top; }" % STG_TXTC_W
UI_SARR["SCHB"] = [' { Anchor: (Width: %d, Height: 52); Text: "%s"; %s }' % (STG_CH_W, t_, SUI.theme_button_style("secondary", "normal", theme="sky"))
                   for t_ in STG_CH_LABELS]
UI_SARR["SCHSELB"] = [' { Anchor: (Width: %d, Height: 52); Text: "%s"; ' % (STG_CH_W, t_) + (OFF_SEL if i_ == 2 else ON_SEL) + " }"
                      for i_, t_ in enumerate(STG_CH_LABELS)]
assert 14 + STG_TXTC_W + 3 * STG_CH_W + 2 * 10 == 14 + STG_TXT_W + 120 + 10 + 120 and STG_TXTC_W >= 600, "0.3.44: the choice row fits a settings row"
assert all(SUI.text_width(t_, 17, bold=True, upper=True) <= STG_CH_W - 24 for t_ in STG_CH_LABELS), "0.3.44: a choice label is too wide"
assert SUI.text_width([k for k in SET_KNOWN if k[0] == "menu.hotkey"][0][3], 15) <= STG_TXTC_W - 8, "0.3.44: the choice row's help line fits"
SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]
''')
P.rep('''F(dat, "public static final String WALK_SW_KEY = %s;" % jstr(WALK_SW_KEY))        # 0.3.42
''', '''F(dat, "public static final String WALK_SW_KEY = %s;" % jstr(WALK_SW_KEY))        # 0.3.42
F(dat, "public static final String CFOLD_KEY = %s;" % jstr(CFOLD_KEY))            # 0.3.44
F(dat, "public static final String KEY_FLAG = %s;" % jstr(KEY_FLAG))              # 0.3.44
F(dat, "public static final String CROUCH_FLAG = %s;" % jstr(CROUCH_FLAG))        # 0.3.44
F(dat, "public static final String QFOLD_FN = %s;" % jstr(QFOLD_FN))              # 0.3.44
F(dat, "public static final String[] STG_CH_LABELS = %s;" % jarr(STG_CH_LABELS))  # 0.3.44
''')

# ================================================================================================ 2: the choice + the flags (SoundSw = the publisher)
P.rep('''M(ssw, r"""
public static void pub(java.util.UUID u) {
  if (u == null) return;
  try {
    boolean b = on(u);''', '''# 0.3.44: the double-tap crouch choice (0 Fold quest tracker, 1 Open the menu, 2 Nothing) - the player's own menu.crouchfold wins; without
# it: menu.hotkey OFF (own or server default) = Nothing, an OWN menu.hotkey=true (chosen ON before 0.3.44) = Open the menu (kept), the
# untouched default = the server default menu.crouchfold line (fix pass 2), else Fold (Skyy 2026-10-22). Reads only (no file is written).
M(ssw, r"""
public static int crouchChoice(java.util.UUID u) {
  if (u == null) return 2;
  Boolean on = @PKG@.SetStore.get(u, @PKG@.MenuData.HOTKEY_KEY);
  if (on != null && !on.booleanValue()) return 2;
  Boolean f = @PKG@.SetStore.own(u, @PKG@.MenuData.CFOLD_KEY);
  if (f != null) return f.booleanValue() ? 0 : 1;
  Boolean own = @PKG@.SetStore.own(u, @PKG@.MenuData.HOTKEY_KEY);
  if (own != null && own.booleanValue()) return 1;
  Boolean sd = @PKG@.SetReg.def(@PKG@.MenuData.CFOLD_KEY);   // fix pass 2: the server default (Server Setup menu.crouchDefault)
  if (sd != null) return sd.booleanValue() ? 0 : 1;
  return 0;
}""")
M(ssw, r"""
public static boolean walkOn(java.util.UUID u) {
  if (u == null || !@PKG@.MenuCfg.WALK_KEY) return false;
  Boolean on = @PKG@.SetStore.get(u, @PKG@.MenuData.WALK_SW_KEY);
  return on == null || on.booleanValue();
}""")
M(ssw, r"""
public static boolean watched(String key) {
  return @PKG@.MenuData.SOUNDS_KEY.equals(key) || @PKG@.MenuData.HOTKEY_KEY.equals(key) || @PKG@.MenuData.WALK_SW_KEY.equals(key)
      || @PKG@.MenuData.CFOLD_KEY.equals(key);
}""")
# the two SkyyHud flags (plain Strings): menu:walkkey:<uuid> "1" / "0", menu:crouch:<uuid> "fold" / "menu" / "off"
M(ssw, r"""
public static void flags(java.util.UUID u) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.MenuUtil.bridge();
    String kk = @PKG@.MenuData.KEY_FLAG + u.toString();
    String ck = @PKG@.MenuData.CROUCH_FLAG + u.toString();
    // fix pass 2: the IO sweep and a world-thread click both publish - re-read after the puts, so a stale put never wins (as the sound flag)
    for (int i = 0; i < 3; i++) {
      String w = walkOn(u) ? "1" : "0";
      int c = crouchChoice(u);
      String cs = c == 0 ? "fold" : (c == 1 ? "menu" : "off");
      b.put(kk, w);
      b.put(ck, cs);
      int c2 = crouchChoice(u);
      String cs2 = c2 == 0 ? "fold" : (c2 == 1 ? "menu" : "off");
      if (w.equals(walkOn(u) ? "1" : "0") && cs.equals(cs2)) break;
    }
  } catch (Throwable t) { }
}""")
M(ssw, r"""
public static void pub(java.util.UUID u) {
  if (u == null) return;
  flags(u);   // 0.3.44
  try {
    boolean b = on(u);''')
P.rep('''public static void forget(java.util.UUID u) {
  if (u == null) return;
  PUB.remove(u);
  try { @PKG@.MenuUtil.bridge().remove(key(u)); } catch (Throwable t) { }
}""")''', '''public static void forget(java.util.UUID u) {
  if (u == null) return;
  PUB.remove(u);
  try { @PKG@.MenuUtil.bridge().remove(key(u)); } catch (Throwable t) { }
  try { @PKG@.MenuUtil.bridge().remove(@PKG@.MenuData.KEY_FLAG + u.toString()); @PKG@.MenuUtil.bridge().remove(@PKG@.MenuData.CROUCH_FLAG + u.toString()); } catch (Throwable t) { }   // 0.3.44
}""")''')
P.rep('''    if (r == 2) { saveSoon(k); if (@PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25
    if (r != 3) { if (r == 1 && @PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return r; }''', '''    if (r == 2) { saveSoon(k); if (@PKG@.SoundSw.watched(key)) @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25; 0.3.44: + the hotkey keys
    if (r != 3) { if (r == 1 && @PKG@.SoundSw.watched(key)) @PKG@.SoundSw.pub(u); return r; }''')

# ---- HotkeyOpen: the crouch fire asks the choice; Fold = hud:fn:questFold, missing / FALSE = the Menu as before
P.rep('''F(hko, "public static volatile long WALK_COOLED = 0L;")     # 0.3.43: a queued Walk open inside the cooldown - dropped silently
''', '''F(hko, "public static volatile long WALK_COOLED = 0L;")     # 0.3.43: a queued Walk open inside the cooldown - dropped silently
F(hko, "public static volatile long FOLDED = 0L;")          # 0.3.44: double-tap crouches that folded / unfolded the quest tracker
F(hko, "public static volatile long FOLD_FELL = 0L;")       # 0.3.44: ... that fell back to opening the Menu (no hud:fn:questFold / FALSE)
''')
P.rep('''M(hko, r"""
public static boolean isDead(@ST@ st, @REF@ r) {''', '''# 0.3.44: SkyyHud's hud:fn:questFold "toggle" (TRUE = done); missing / FALSE / an error = false (the caller opens the Menu instead)
M(hko, r"""
public static boolean fold(java.util.UUID u) {
  if (u == null) return false;
  try {
    Object f = @PKG@.MenuUtil.bridge().get(@PKG@.MenuData.QFOLD_FN);
    if (!(f instanceof java.util.function.Function)) return false;
    return Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "toggle" }));
  } catch (Throwable t) { return false; }
}""")
M(hko, r"""
public static boolean isDead(@ST@ st, @REF@ r) {''')
P.rep('''    if (this.walk) { if (!wantedWalk(this.pr.getUuid())) return; }
    else if (!wanted(this.pr.getUuid())) return;
    if (this.walk && @PKG@.MenuHotkey.cooling''', '''    if (this.walk) { if (!wantedWalk(this.pr.getUuid())) return; }
    else if (!wanted(this.pr.getUuid())) return;
    if (!this.walk) {   // 0.3.44: the double-tap crouch choice
      int ch = @PKG@.SoundSw.crouchChoice(this.pr.getUuid());
      if (ch == 2) return;
      if (ch == 0) {
        if (fold(this.pr.getUuid())) { FOLDED = FOLDED + 1L; return; }
        FOLD_FELL = FOLD_FELL + 1L;
      }
    }
    if (this.walk && @PKG@.MenuHotkey.cooling''')
P.rep('''    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it (or press your Walk key (Alt), or double-tap crouch - switches in /settings) to open''',
      '''    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it (or press your Walk key (Alt) - double-tap crouch folds your quest tracker, both in /settings) to open''')

# ---- the Settings row: three buttons for menu.hotkey, the click saves the choice
P.rep('''    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    String row = "#SkyyStgRow" + r;''', '''    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    boolean ch3 = @PKG@.MenuData.HOTKEY_KEY.equals(key);    // 0.3.44: the double-tap crouch CHOICE row
    String row = "#SkyyStgRow" + r;''')
P.rep('''    b.appendInline(row, "Group #SkyyStgTxt" + r + @PKG@.MenuData.UI_STXTB);''',
      '''    b.appendInline(row, "Group #SkyyStgTxt" + r + (ch3 ? @PKG@.MenuData.UI_STXTCB : @PKG@.MenuData.UI_STXTB));''')
P.rep('''    b.appendInline(row, "TextButton #SkyyStgOn" + r + (on ? @PKG@.MenuData.UI_SONSELB : @PKG@.MenuData.UI_SONB));
    b.appendInline(row, @PKG@.MenuData.UI_SSP10);
    b.appendInline(row, "TextButton #SkyyStgOff" + r + (on ? @PKG@.MenuData.UI_SOFFB : @PKG@.MenuData.UI_SOFFSELB));''', '''    if (ch3) {
      int cv = @PKG@.SoundSw.crouchChoice(u);
      for (int c = 0; c < 3; c++) {
        if (c > 0) b.appendInline(row, @PKG@.MenuData.UI_SSP10);
        b.appendInline(row, "TextButton #SkyyStgCh" + r + "n" + c + (c == cv ? @PKG@.MenuData.UI_SCHSELB[c] : @PKG@.MenuData.UI_SCHB[c]));
        ev.addEventBinding(@BT@.Activating, "#SkyyStgCh" + r + "n" + c, sevd("sch" + r + "n" + c));
      }
    } else {
      b.appendInline(row, "TextButton #SkyyStgOn" + r + (on ? @PKG@.MenuData.UI_SONSELB : @PKG@.MenuData.UI_SONB));
      b.appendInline(row, @PKG@.MenuData.UI_SSP10);
      b.appendInline(row, "TextButton #SkyyStgOff" + r + (on ? @PKG@.MenuData.UI_SOFFB : @PKG@.MenuData.UI_SOFFSELB));
    }''')
P.rep('''    b.set("#SkyyStgDesc" + r + ".Text", @PKG@.MenuUtil.clip(desc, 150));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOn" + r, sevd("son" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOff" + r, sevd("soff" + r));''', '''    b.set("#SkyyStgDesc" + r + ".Text", @PKG@.MenuUtil.clip(desc, ch3 ? 100 : 150));
    if (!ch3) {
      ev.addEventBinding(@BT@.Activating, "#SkyyStgOn" + r, sevd("son" + r));
      ev.addEventBinding(@BT@.Activating, "#SkyyStgOff" + r, sevd("soff" + r));
    }''')
P.rep('''    for (int r = 0; r < this.rowKeys.length; r++) {
      boolean hitOn = data.indexOf("\\"son" + r + "\\"") >= 0;''', '''    for (int r = 0; r < this.rowKeys.length; r++) {   // 0.3.44: the choice row's three buttons
      for (int c = 0; c < 3; c++) {
        if (data.indexOf("\\"sch" + r + "n" + c + "\\"") < 0) continue;
        String ck = this.rowKeys[r];
        if (ck == null || !@PKG@.MenuData.HOTKEY_KEY.equals(ck)) { rebuild(); return; }
        if (!@PKG@.SetReg.may(u, ck)) { this.status = @PKG@.MenuData.SET_TXT_GONE; rebuild(); return; }
        int ok = @PKG@.SetStore.set(u, ck, c != 2, false);
        if (ok == 1 && c != 2) ok = @PKG@.SetStore.set(u, @PKG@.MenuData.CFOLD_KEY, c == 0, false);
        this.status = ok == 1 ? "Double-tap crouch: " + @PKG@.MenuData.STG_CH_LABELS[c] + " - saved." : @PKG@.MenuData.SET_TXT_BROKEN;
        rebuild();
        return;
      }
    }
    for (int r = 0; r < this.rowKeys.length; r++) {
      boolean hitOn = data.indexOf("\\"son" + r + "\\"") >= 0;''')

# ---- fix pass 2 (critic: owners could not pick the default): Server Setup -> Menu "Double-tap crouch default: fold quests" = the
# menu.crouchfold line of settings-defaults.properties (ON = Fold quest tracker, OFF = Open the menu), the menu.tooltipsDefault pattern
CROUCH_DEF_LABEL = "Double-tap crouch default: fold quests"
CROUCH_DEF_HELP = "Players who never chose: ON folds the quest tracker, OFF opens the Menu. Each can pick in /settings."
assert len(CROUCH_DEF_LABEL) <= 40 and len(CROUCH_DEF_HELP) <= 100, "0.3.44: the crouch default row's texts fit the kit"
P.rep('''    ("settings.defaults", "Player settings defaults", "settings", "table", "", "", "", "text;none;Default", "", "live",
''', '''    ("menu.crouchDefault", %s, "settings", "bool", "true", "", "", "", "", "live",     # 0.3.44 fix pass 2
     %s,
     "custom:SetDefCfg@settings-defaults.properties:menu.crouchfold"),
    ("settings.defaults", "Player settings defaults", "settings", "table", "", "", "", "text;none;Default", "", "live",
''' % (repr(CROUCH_DEF_LABEL).replace("'", '"'), repr(CROUCH_DEF_HELP).replace("'", '"')))
P.rep('''       "# Only switches of installed, updated mods show up in game. Menu hover tooltips OFF for everyone: menu.tooltips=false"]
''', '''       "# Only switches of installed, updated mods show up in game. Menu hover tooltips OFF for everyone: menu.tooltips=false",
       "# Double-tap crouch for players who never chose (0.3.44): menu.crouchfold=true folds the quest tracker, false opens the Menu"]
''')
P.rep('''public static String customGet(String key) {
  if ("menu.tooltipsDefault".equals(key)) {''', '''public static String customGet(String key) {
  if ("menu.crouchDefault".equals(key)) {   // 0.3.44 fix pass 2
    Object cv = @PKG@.SetReg.ADMIN.get(@PKG@.MenuData.CFOLD_KEY);
    if (cv instanceof Boolean && !((Boolean) cv).booleanValue()) return "false";
    return "true";
  }
  if ("menu.tooltipsDefault".equals(key)) {''')
P.rep('''public static Object[] customSet(String key, String value) {
  if ("menu.tooltipsDefault".equals(key)) {''', '''public static Object[] customSet(String key, String value) {
  if ("menu.crouchDefault".equals(key)) {   // 0.3.44 fix pass 2
    boolean con = !"false".equals(value);
    @PKG@.SetReg.adminPut(@PKG@.MenuData.CFOLD_KEY, Boolean.valueOf(con));
    return new Object[] { "ok", con ? "true" : "false", null, new String[] { @PKG@.MenuData.CFOLD_KEY, con ? "true" : "false" } };
  }
  if ("menu.tooltipsDefault".equals(key)) {''')
P.rep('''  if (!"menu.tooltipsDefault".equals(key) || vals == null) return null;
  Object v = vals.get(@PKG@.MenuData.TIPS_KEY);''', '''  String fk = "menu.tooltipsDefault".equals(key) ? @PKG@.MenuData.TIPS_KEY : ("menu.crouchDefault".equals(key) ? @PKG@.MenuData.CFOLD_KEY : null);   // 0.3.44
  if (fk == null || vals == null) return null;
  Object v = vals.get(fk);''')

# ================================================================================================ 3: Your Stats by source
P.rep('''ST_NOTES = [
    "Health, Mana, Stamina: your max now. Base = the game's own part and armor.",''', '''ST_NOTES = [
    "Your max right now, split by where it comes from (Sources at the bottom).",     # 0.3.44''')
P.rep('''ST_NAME_W, ST_VAL_W, ST_MID_W = 300, 200, 30
''', '''ST_NAME_W, ST_VAL_W, ST_MID_W = 300, 200, 30
# 0.3.44 BY SOURCE (research/UI-Queue-Spec.md 6): Stat | Base | Gear | Charms | Pets | Trees | Class | Total - six cells + the total
ST_COLS = ["Base", "Gear", "Charms", "Pets", "Trees", "Class"]
ST_CELL_GAP, ST_TOT_W, ST_CELL_FS, ST_COLH_H, ST_COLH_FS = 6, 180, 16, 26, 15
ST_GOOD, ST_BAD, ST_DIM, ST_ABS, ST_GOLD = "#7ee08a", "#ff7a7a", "#7f93a6", "#d6e4ee", "#e8c25a"     # ui-data: Style Guide 15 (stat value green / red, minor dim, stat name, level gold)
ST_LEGEND = [("Base", "the game, your armour's base and your skill levels"),
             ("Gear", "your held weapon or tool and the armour you wear"),
             ("Charms", "your Void Charms"),
             ("Pets", "your active pets"),
             ("Trees", "skill and class trees, and the Rebirth Nexus"),
             ("Class", "your class's own bonuses")]
ST_LEGEND_HEAD = ("Sources", "Four power sources: tool or weapon + gear + charms + pets.")
# fix pass (critic: the gold Total can be lower than the real stat): SkyyGear's Skill Trees 3 combat rows and the Rebirth damage / defence %
# are applied but not published, so the legend says so (always - they are missing even while SkyyGear reads gear:extras)
ST_LEGEND_TOTAL = ("Total", "the parts above; some tree and Rebirth bonuses are not counted yet")
assert [n for n, _t in ST_LEGEND] == ST_COLS and all(len(n) + len(t) + 2 <= 79 for n, t in ST_LEGEND + [ST_LEGEND_TOTAL]) and len(ST_LEGEND_HEAD[1]) <= 79
''')
P.rep('''    # one stat row: name | total (right-aligned) | gap | where it comes from; a section head: the section name | its note
    row_w = IW - 2 * SUI.WELL_LIST_PAD - 24
    src_w = row_w - ST_NAME_W - ST_VAL_W - ST_MID_W
    rid = J("i", "0")
    rows = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "rowName", w=ST_NAME_W, h=ST_ROW_H, size=ST_NAME_FS, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatV" + rid, "", "rowName", w=ST_VAL_W - 8, h=ST_ROW_H, size=ST_VAL_FS, align="End")),
            ("SkyyStatR" + rid, SUI.spacer(w=ST_MID_W, h=ST_ROW_H)),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "rowSub", w=src_w, h=ST_ROW_H, size=ST_SRC_FS))]
''', '''    # 0.3.44 BY SOURCE: a TEXT row = name | gap | where it comes from (the six cells' width) | gap | total; a TABLE row = name | 6 x (gap +
    # cell) | gap | total; a COLUMN HEADER row = the same columns in caption 15. A section head: the section name | its note
    row_w = IW - 2 * SUI.WELL_LIST_PAD - 24
    cell_w = (row_w - (ST_NAME_W + 8) - 7 * ST_CELL_GAP - ST_TOT_W) // 6
    src_w = 6 * cell_w + 5 * ST_CELL_GAP
    assert cell_w >= 150 and 8 + ST_NAME_W + 7 * ST_CELL_GAP + 6 * cell_w + ST_TOT_W <= row_w, "0.3.44: the by-source columns fit a row"

    def table_parts(ri, ki, cc):
        R = "SkyyStatR" + ri
        gap = SUI.spacer(w=ST_CELL_GAP, h=ST_ROW_H)
        name = SUI.label("SkyyStatN" + ri, "", "rowName", w=ST_NAME_W, h=ST_ROW_H, size=ST_NAME_FS, anchor={"left": 8})
        tot = SUI.label("SkyyStatV" + ri, "", "bold", w=ST_TOT_W, h=ST_ROW_H, size=ST_VAL_FS, col=ST_GOLD, align="End")
        text = [("SkyyStatList", SUI.group(R, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})), (R, name), (R, gap),
                (R, SUI.label("SkyyStatS" + ri, "", "rowSub", w=src_w, h=ST_ROW_H, size=ST_SRC_FS)), (R, gap), (R, tot)]
        trow = [("SkyyStatList", SUI.group(R, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})), (R, name)]
        tcell = [(R, gap), (R, SUI.label("SkyyStatC" + ri + "n" + ki, "", "rowName", w=cell_w, h=ST_ROW_H, size=ST_CELL_FS, col=cc,
                                         bold=True, align="End"))]
        ttot = [(R, gap), (R, tot)]
        hgap = SUI.spacer(w=ST_CELL_GAP, h=ST_COLH_H)
        colh = [("SkyyStatList", SUI.group(R, "Left", h=ST_COLH_H, anchor={"bottom": ST_ROW_GAP})),
                (R, SUI.label("SkyyStatN" + ri, "", "caption", w=ST_NAME_W, h=ST_COLH_H, size=ST_COLH_FS, anchor={"left": 8}))]
        ccell = [(R, hgap), (R, SUI.label("SkyyStatC" + ri + "n" + ki, "", "caption", w=cell_w, h=ST_COLH_H, size=ST_COLH_FS, align="End"))]
        ctot = [(R, hgap), (R, SUI.label("SkyyStatV" + ri, "", "caption", w=ST_TOT_W, h=ST_COLH_H, size=ST_COLH_FS, align="End"))]
        return text, trow, tcell, ttot, colh, ccell, ctot
    rid = J("i", "0")
    rows, tb_row, tb_cell, tb_tot, tb_colh, tb_ccell, tb_ctot = table_parts(rid, J("ck", "0"), J("cc", ST_GOOD))
''')
P.rep('''    chk.extend(rows)
    hc = SUI.Appends(''', '''    chk.extend(rows)
    # 0.3.44: one table row ("t") and one column header row ("c") with all six cells, the same checks
    for _tag, (_head, _cell, _tail) in (("t", (1, 2, 3)), ("c", (4, 5, 6))):
        _pp = table_parts(_tag, "0", ST_GOOD)
        chk.extend(_pp[_head])
        for _k in range(6):
            chk.extend(table_parts(_tag, str(_k), (ST_GOOD, ST_BAD, ST_DIM, ST_ABS, ST_GOOD, ST_DIM)[_k])[_cell])
        chk.extend(_pp[_tail])
    hc = SUI.Appends(''')
P.rep('''    for _t in ("1,000,000,000%", "999,999,999,999", "Level 100", "+1,000,000,000%"):
        assert SUI.text_width(_t, ST_VAL_FS, bold=True) <= ST_VAL_W - 8, "stat total too wide: " + _t
    return sh, rows, head, foot, cap, src_w, left
''', '''    for _t in ("1,000,000,000%", "999,999,999,999", "Level 100", "+1,000,000,000%"):
        assert SUI.text_width(_t, ST_VAL_FS, bold=True) <= ST_TOT_W - 8, "stat total too wide: " + _t     # 0.3.44: the Total column
    for _t in ("+1,000,000%", "-999,999", "+12.5%"):
        assert SUI.text_width(_t, ST_CELL_FS, bold=True) <= cell_w - 8, "0.3.44: stat cell too wide: " + _t
    for _t in ST_COLS + ["Total"]:
        assert SUI.text_width(_t, ST_COLH_FS) <= cell_w - 8, "0.3.44: column head too wide: " + _t
    return sh, rows, head, foot, cap, src_w, left, (tb_row, tb_cell, tb_tot, tb_colh, tb_ccell, tb_ctot), cell_w
''')
P.rep('''ST_SH, ST_ROW_MK, ST_HEAD_MK, ST_FOOT_MK, ST_CAP_MK, ST_SRC_W, ST_LEFT = stats_page()
''', '''ST_SH, ST_ROW_MK, ST_HEAD_MK, ST_FOOT_MK, ST_CAP_MK, ST_SRC_W, ST_LEFT, ST_TBL_MK, ST_CELL_W = stats_page()
''')
P.rep('''ST_HEAD_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in ST_HEAD_MK)
''', '''ST_HEAD_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in ST_HEAD_MK)
# 0.3.44: the table row (TROW + 6 x TCELL + TTOT) and the column header row (COLH + 6 x CCELL + CTOT); Java names i, ck (cell), cc (colour)
ST_TROW_JAVA, ST_TCELL_JAVA, ST_TTOT_JAVA, ST_COLH_JAVA, ST_CCELL_JAVA, ST_CTOT_JAVA = [
    "\\n".join(SUI.java_append(p, mk) for p, mk in _parts) for _parts in ST_TBL_MK]
_ind = lambda src, n: "\\n".join(" " * n + ln for ln in src.split("\\n"))
''')
# the page build: column header rows, table rows, text rows
P.rep('''  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    if (r[0] == null) {
""" + "\\n".join("      " + ln for ln in ST_HEAD_JAVA.split("\\n")) + r"""''', '''  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    if (r[0] == null && r[1] == null) {      // 0.3.44: a column header row (Stat | Base .. Class | Total)
""" + _ind(ST_COLH_JAVA, 6) + r"""
      for (int ck = 0; ck < 6; ck++) {
""" + _ind(ST_CCELL_JAVA, 8) + r"""
        b.set("#SkyyStatC" + i + "n" + ck + ".Text", @PKG@.StatsCalc.COLS[ck]);
      }
""" + _ind(ST_CTOT_JAVA, 6) + r"""
      b.set("#SkyyStatN" + i + ".Text", @PKG@.StatsCalc.COL_STAT);
      b.set("#SkyyStatV" + i + ".Text", @PKG@.StatsCalc.COL_TOTAL);
      continue;
    }
    if (r[0] != null && r.length >= 9) {     // 0.3.44: a by-source TABLE row (name, total, "", 6 cells)
""" + _ind(ST_TROW_JAVA, 6) + r"""
      for (int ck = 0; ck < 6; ck++) {
        String cc = @PKG@.StatsCalc.cellCol(r[3 + ck], ck);
""" + _ind(ST_TCELL_JAVA, 8) + r"""
        b.set("#SkyyStatC" + i + "n" + ck + ".Text", r[3 + ck]);
      }
""" + _ind(ST_TTOT_JAVA, 6) + r"""
      b.set("#SkyyStatN" + i + ".Text", r[0]);
      b.set("#SkyyStatV" + i + ".Text", r[1]);
      continue;
    }
    if (r[0] == null) {
""" + "\\n".join("      " + ln for ln in ST_HEAD_JAVA.split("\\n")) + r"""''')

# ---- StatsCalc: the columns
P.rep('''F(scl, "public static final int ROWS = %d;" % ST_ROWS)
''', '''F(scl, "public static final int ROWS = %d;" % ST_ROWS)
F(scl, "public static final String[] COLS = %s;" % jarr(ST_COLS))                               # 0.3.44
F(scl, 'public static final String COL_STAT = "Stat";')
F(scl, 'public static final String COL_TOTAL = "Total";')
F(scl, "public static final String[] LEG_N = %s;" % jarr([n for n, _t in ST_LEGEND]))
F(scl, "public static final String[] LEG_T = %s;" % jarr([t for _n, t in ST_LEGEND]))
F(scl, "public static final String[] LEG_HEAD = %s;" % jarr(list(ST_LEGEND_HEAD)))
F(scl, "public static final String[] LEG_TOTAL = %s;" % jarr(list(ST_LEGEND_TOTAL)))   # fix pass: the Total caveat
''')
SC_HELP = r'''# ---- 0.3.44 BY SOURCE helpers: a cell = "-" (nothing, |v| < 0.05) or the signed value + unit; its colour from the text (Style Guide 15:
# + green, - red, "-" dim, an absolute number white); a table row = String[9] { name, total, "", Base, Gear, Charms, Pets, Trees, Class }
M(scl, r"""
public static String cellOf(double v, String unit) {
  if (Math.abs(v) < 0.05) return "-";
  return signed(v) + (unit == null ? "" : unit);
}""")
M(scl, r"""
public static String cellCol(String t, int k) {
  if (t == null || t.length() == 0 || "-".equals(t)) return "@DIM@";
  if (t.startsWith("+")) return "@GOOD@";
  if (t.startsWith("-")) return "@BAD@";
  return "@ABS@";
}""".replace("@DIM@", ST_DIM).replace("@GOOD@", ST_GOOD).replace("@BAD@", ST_BAD).replace("@ABS@", ST_ABS))
M(scl, r"""
public static void trow(java.util.ArrayList rows, String name, String total, String[] cells) {
  String[] r = new String[9];
  r[0] = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(name == null ? "" : name), 32);
  r[1] = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(total == null ? "" : total), 24);
  r[2] = "";
  for (int k = 0; k < 6; k++) r[3 + k] = (cells != null && k < cells.length && cells[k] != null) ? @PKG@.MenuUtil.clip(cells[k], 16) : "-";
  rows.add(r);
}""")
M(scl, r"""
public static void tparts(java.util.ArrayList rows, String name, String unit, double base, double gear, double charms, double pets, double trees, double cls) {
  String u = unit == null ? "" : unit;
  String[] c = new String[] { cellOf(base, u), cellOf(gear, u), cellOf(charms, u), cellOf(pets, u), cellOf(trees, u), cellOf(cls, u) };
  trow(rows, name, num(base + gear + charms + pets + trees + cls) + u, c);
}""")
# pets:stats:<uuid> (SkyyPets: Map String -> Number) summed per stat, each total floored and capped +-1,000,000 - SkyyGear's own reading
# (GearStats.parsePets), so the Pets column is what SkyyGear applies
M(scl, r"""
public static java.util.HashMap petsKv(java.util.UUID u) {
  java.util.HashMap m = new java.util.HashMap();
  Object o = u == null ? null : br().get("pets:stats:" + u.toString());
  if (!(o instanceof java.util.Map)) return m;
  try {
    java.util.Iterator it = new java.util.ArrayList(((java.util.Map) o).entrySet()).iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getKey() instanceof String) || !(e.getValue() instanceof Number)) continue;
      double v = ((Number) e.getValue()).doubleValue();
      if (Double.isNaN(v) || Double.isInfinite(v)) continue;
      String k = ((String) e.getKey()).trim();
      m.put(k, Double.valueOf(get(m, k) + v));
    }
  } catch (Throwable t) { }
  java.util.Iterator ks = new java.util.ArrayList(m.keySet()).iterator();
  while (ks.hasNext()) {
    String k = (String) ks.next();
    double v = Math.floor(get(m, k) + 0.000000001);
    if (v > 1000000.0) v = 1000000.0;
    if (v < -1000000.0) v = -1000000.0;
    m.put(k, Double.valueOf(v));
  }
  return m;
}""")
M(scl, r"""
public static boolean listed(Object o, String key) {
  if (!(o instanceof String) || key == null || key.length() == 0) return false;
  String[] p = ((String) o).split(",");
  for (int i = 0; i < p.length; i++) if (p[i].trim().equals(key)) return true;
  return false;
}""")
# gear:extras:<uuid> (SkyyTrees: Map source -> "str:N,...") - counted ONLY while SkyyGear lists "gear:extras" in tree:reads:SkyyGear (else
# SkyyGear does not apply them and SkyyTrees marks the nodes "coming")
M(scl, r"""
public static java.util.HashMap treesKv(java.util.UUID u) {
  java.util.HashMap m = new java.util.HashMap();
  if (u == null || !listed(br().get("tree:reads:SkyyGear"), "gear:extras")) return m;
  Object o = br().get("gear:extras:" + u.toString());
  if (!(o instanceof java.util.Map)) return m;
  try {
    java.util.Iterator it = new java.util.ArrayList(((java.util.Map) o).values()).iterator();
    while (it.hasNext()) {
      java.util.HashMap one = kv(it.next());
      java.util.Iterator ks = one.keySet().iterator();
      while (ks.hasNext()) { String k = (String) ks.next(); m.put(k, Double.valueOf(get(m, k) + get(one, k))); }
    }
  } catch (Throwable t) { }
  return m;
}""")
M(scl, r"""
public static java.util.HashMap plus(java.util.HashMap a, java.util.HashMap b) {
  java.util.HashMap m = new java.util.HashMap();
  java.util.Iterator it = a.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); m.put(k, Double.valueOf(get(a, k))); }
  it = b.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); m.put(k, Double.valueOf(get(m, k) + get(b, k))); }
  return m;
}""")
# a Health / Mana / Stamina MAX modifier's column: 1 Gear, 2 Charms, 3 Pets, 4 Trees (+ the Rebirth Nexus), 5 Class, 0 Base (skill levels);
# -1 = not ours (the game / armour: Base too, as the rest)
M(scl, r"""
public static int col(String key) {
  if (key == null) return -1;
  if (key.startsWith("skyygear_")) return 1;
  if (key.startsWith("skyyacc_")) return 2;
  if (key.startsWith("skyypet_")) return 3;
  if (key.startsWith("skyytree_") || key.startsWith("skyyskill_rebirth")) return 4;
  if (key.startsWith("skyyskill_class")) return 5;
  if (key.startsWith("skyyskill_")) return 0;
  return -1;
}""")
'''
P.rep('''# ---- Health / Mana / Stamina: the max the player has right now, split by the MAX modifiers' key prefixes (every Skyy mod names its own)
''', SC_HELP + '''# ---- Health / Mana / Stamina: the max the player has right now, split by the MAX modifiers' key prefixes (every Skyy mod names its own)
''')
P.rep('''  float max = v.getMax();
  double[] grp = new double[GROUPS.length];
  double known = 0.0;
  java.util.Map mods = v.getModifiers();''', '''  float max = v.getMax();
  double[] grp = new double[GROUPS.length];
  double known = 0.0;
  double[] cs = new double[6];     // 0.3.44: Base, Gear, Charms, Pets, Trees, Class
  double ck = 0.0;
  java.util.Map mods = v.getModifiers();''')
P.rep('''      int gi = group(String.valueOf(k));
      if (gi < 0) continue;
      double a = (double) sm.getAmount();
      if (Double.isNaN(a) || Double.isInfinite(a)) continue;
      grp[gi] = grp[gi] + a;
      known = known + a;
    }
  }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < grp.length; i++) part(sb, GROUPS[i], grp[i], "");
  return new String[] { num((double) max), sb.toString(), num((double) max - known) };''', '''      int gi = group(String.valueOf(k));
      int ci = col(String.valueOf(k));
      if (gi < 0 && ci < 1) continue;
      double a = (double) sm.getAmount();
      if (Double.isNaN(a) || Double.isInfinite(a)) continue;
      if (gi >= 0) { grp[gi] = grp[gi] + a; known = known + a; }
      if (ci >= 1) { cs[ci] = cs[ci] + a; ck = ck + a; }
    }
  }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < grp.length; i++) part(sb, GROUPS[i], grp[i], "");
  cs[0] = (double) max - ck;
  return new String[] { num((double) max), sb.toString(), num((double) max - known),
      num(cs[0]), cellOf(cs[1], ""), cellOf(cs[2], ""), cellOf(cs[3], ""), cellOf(cs[4], ""), cellOf(cs[5], "") };''')
P.rep('''  if (e == null) { add(rows, name, "-", "not read - click Refresh"); return; }
  String src = e[1];''', '''  if (e == null) { add(rows, name, "-", "not read - click Refresh"); return; }
  if (e.length >= 9) { trow(rows, name, e[0], new String[] { e[3], e[4], e[5], e[6], e[7], e[8] }); return; }   // 0.3.44
  String src = e[1];''')
# gearRow / defRow / classDamage -> the table versions (same callers: mainTab / combatTab below)
P.rep('''M(scl, r"""
public static void gearRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, boolean gearOn, String key) {
  int k = gi(key);
  if (k < 0) return;
  double gv = get(g, key);
  double av = get(a, key);
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av) + GU[k], sb.toString());
}""")''', '''# 0.3.44: a gear stat as a by-source TABLE row: Base (the skill Defense for "def"), Gear (gear:stats), Charms (gear:extra), Pets (pets:stats),
# Trees (gear:extras while SkyyGear reads it), Class 0; without SkyyGear (and no Base) the old text row
M(scl, r"""
public static void gearT(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, java.util.HashMap p, java.util.HashMap x, boolean gearOn, String key, double base) {
  int k = gi(key);
  if (k < 0) return;
  if (!gearOn && Math.abs(base) < 0.05) { add(rows, GL[k], "-", "SkyyGear is not on this server"); return; }
  tparts(rows, GL[k], GU[k], base, get(g, key), get(a, key), get(p, key), get(x, key), 0.0);
}""")''')
P.rep('''M(scl, r"""
public static void defRow(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap g, java.util.HashMap a, boolean gearOn) {
  double sv = skillDef(u);
  if (!(sv > 0.0)) { gearRow(rows, g, a, gearOn, "def"); return; }
  int k = gi("def");
  if (k < 0) return;
  boolean gs = cfgOn("SkyyGear", "part.stats", true);
  double gv = gs ? get(g, "def") : 0.0;
  double av = gs ? get(a, "def") : 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  part(sb, "Skills", sv, GU[k]);
  if (!gs) sb.append(sb.length() == 0 ? "gear stats off" : ", gear stats off");
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av + sv) + GU[k], sb.toString());
}""")''', '''# 0.3.44: Defense - the skill Defense (skill:def) in Base; with SkyyGear's part.stats "false" SkyySkills counts the skill Defense alone, so
# the gear / charm / pet / tree parts are then left out (as 0.3.12's row did)
M(scl, r"""
public static void defT(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap g, java.util.HashMap a, java.util.HashMap p, java.util.HashMap x, boolean gearOn) {
  double sv = skillDef(u);
  if (sv > 0.0 && !cfgOn("SkyyGear", "part.stats", true)) {
    java.util.HashMap e = new java.util.HashMap();
    gearT(rows, e, e, e, e, true, "def", sv);
    return;
  }
  gearT(rows, g, a, p, x, gearOn, "def", sv);
}""")''')
P.rep('''  double cb = skillDmg(u);
  if (!(cb >= 0.05)) {
    add(rows, "Class Weapon Damage", signed(lvl * rate * 100.0) + "%", cs + " level " + (int) lvl + ", with your class weapons");
    return;
  }
  double lp = lvl * rate * 100.0;
  StringBuilder sb = new StringBuilder();
  sb.append(cs).append(" level ").append((int) lvl);
  if (Math.abs(lp) >= 0.05) sb.append(' ').append(signed(lp)).append('%');
  part(sb, "Class balance", cb, "%");
  add(rows, "Class Weapon Damage", signed(lp + cb) + "%", sb.toString());
}""")''', '''  double cb = skillDmg(u);
  tparts(rows, "Class Weapon Damage", "%", lvl * rate * 100.0, 0.0, 0.0, 0.0, 0.0, cb >= 0.05 ? cb : 0.0);   // 0.3.44: level part Base, balance Class
}""")''')
P.rep('''public static void mainTab(java.util.ArrayList rows, java.util.UUID u, Object[] vit) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  vitalRow(rows, "Health", vit, 0);
  vitalRow(rows, "Mana", vit, 1);
  vitalRow(rows, "Stamina", vit, 2);
  defRow(rows, u, g, a, gearOn);   // 0.3.12: + the skill Defense (skill:def:<uuid>); without it = gearRow(.., "def")
  gearRow(rows, g, a, gearOn, "str");
  gearRow(rows, g, a, gearOn, "cc");
  gearRow(rows, g, a, gearOn, "cd");
  gearRow(rows, g, a, gearOn, "mp");''', '''public static void mainTab(java.util.ArrayList rows, java.util.UUID u, Object[] vit) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  java.util.HashMap p = petsKv(u);      // 0.3.44
  java.util.HashMap x = treesKv(u);     // 0.3.44
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  vitalRow(rows, "Health", vit, 0);
  vitalRow(rows, "Mana", vit, 1);
  vitalRow(rows, "Stamina", vit, 2);
  defT(rows, u, g, a, p, x, gearOn);   // 0.3.12: + the skill Defense (skill:def:<uuid>); 0.3.44: by source
  gearT(rows, g, a, p, x, gearOn, "str", 0.0);
  gearT(rows, g, a, p, x, gearOn, "cc", 0.0);
  gearT(rows, g, a, p, x, gearOn, "cd", 0.0);
  gearT(rows, g, a, p, x, gearOn, "mp", 0.0);''')
P.rep('''  add(rows, "Health Regen", hr[0], hr[1]);
  gearRow(rows, g, a, gearOn, "stam");
}""")''', '''  add(rows, "Health Regen", hr[0], hr[1]);
  gearT(rows, g, a, p, x, gearOn, "stam", 0.0);
}""")''')
P.rep('''public static void combatTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  gearRow(rows, g, a, gearOn, "dmg");
  gearRow(rows, g, a, gearOn, "chg");
  gearRow(rows, g, a, gearOn, "tdmg");
  groupRow(rows, g, a, ELEM_K, ELEM_S, ELEM_U, "Elemental Damage", true);      // 0.3.43: with SkyyGear's "%"
  groupRow(rows, g, a, RAW_K, RAW_S, RAW_U, "Raw Elemental Damage", false);
  gearRow(rows, g, a, gearOn, "lsteal");
  gearRow(rows, g, a, gearOn, "msteal");
  gearRow(rows, g, a, gearOn, "hpr");
  gearRow(rows, g, a, gearOn, "hprp");''', '''public static void combatTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  java.util.HashMap p = petsKv(u);      // 0.3.44
  java.util.HashMap x = treesKv(u);     // 0.3.44
  java.util.HashMap ax = plus(plus(a, p), x);   // 0.3.44: the element groups count charms + pets + trees too (their words stay per element)
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  gearT(rows, g, a, p, x, gearOn, "dmg", 0.0);
  gearT(rows, g, a, p, x, gearOn, "chg", 0.0);
  gearT(rows, g, a, p, x, gearOn, "tdmg", 0.0);
  groupRow(rows, g, ax, ELEM_K, ELEM_S, ELEM_U, "Elemental Damage", true);      // 0.3.43: with SkyyGear's "%"
  groupRow(rows, g, ax, RAW_K, RAW_S, RAW_U, "Raw Elemental Damage", false);
  gearT(rows, g, a, p, x, gearOn, "lsteal", 0.0);
  gearT(rows, g, a, p, x, gearOn, "msteal", 0.0);
  gearT(rows, g, a, p, x, gearOn, "hpr", 0.0);
  gearT(rows, g, a, p, x, gearOn, "hprp", 0.0);''')
P.rep('''  for (int t = 0; t < 3 && t < TABS.length; t++) {
    java.util.ArrayList rs = rows(u, t, vit);
    out.add(new String[] { null, TABS[t], t < NOTES.length ? NOTES[t] : "" });
    for (int i = 0; i < rs.size(); i++) out.add(rs.get(i));
  }
  return out;''', '''  for (int t = 0; t < 3 && t < TABS.length; t++) {
    java.util.ArrayList rs = rows(u, t, vit);
    out.add(new String[] { null, TABS[t], t < NOTES.length ? NOTES[t] : "" });
    boolean tbl = false;     // 0.3.44: a column header row under a section that has by-source rows
    for (int i = 0; i < rs.size(); i++) if (((String[]) rs.get(i)).length >= 9) tbl = true;
    if (tbl) out.add(new String[] { null, null, "" });
    for (int i = 0; i < rs.size(); i++) out.add(rs.get(i));
  }
  out.add(new String[] { null, LEG_HEAD[0], LEG_HEAD[1] });     // 0.3.44: the Sources legend
  for (int k = 0; k < LEG_N.length; k++) add(out, LEG_N[k], "", LEG_T[k]);
  add(out, LEG_TOTAL[0], "", LEG_TOTAL[1]);     // fix pass: not every bonus is listed yet
  return out;''')

assert P.s.count("gearRow(") == 0 and P.s.count("defRow(") == 0, "0.3.44: every gear row is a table row"
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.44 adds no system / command"
P.finish()
