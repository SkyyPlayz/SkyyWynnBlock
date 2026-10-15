"""Derive SkyyMenu/build_skyymenu_0.3.25.py from the LIVE SkyyMenu 0.3.24 (python tools/menu_0_3_25_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_24_patch.py -> 0.3.24 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.25. The harness SkyyMenu/test_skyymenu_0.3.25.py is its own file.

0.3.25 (2026-10-14) = SEARCH BARS + THE PER-PLAYER SOUND SWITCH + THE SHARDS ADMIN BUTTONS. Skyy 2026-10-14 ~18:30: "regarding 1. i want
the setting and the server setting page to have a search bar, to easily find settings." and, picking from the main session's list incl.
"3. Shards buttons on the Admin page" and "6. Sound pass rounds 2-4 ... plus a per-player sound switch": "do 1. 3. 6. 7. 8. and 9."
  1. SERVER SETUP SEARCH (/modconfig, the box that was there since 0.3): 0.3 - 0.3.24 only FILTERED THE MOD LIST (a mod row with "Hits: a,
     b, c", Open jumped to the first hit; the setting KEY was never searched). Now a search (2+ letters; every word must appear) lists the
     SETTINGS themselves across every mod on the config registry: one row per matching setting - its label, then "<page title> > <tab> -
     <key> - <help>" - plus one row per matching tab ("Tab: <name>") and the mod row itself when the mod's name matches. "Go to" on a
     setting opens that mod on the right tab and page (an advanced row switches "show advanced" on) where it can be edited at once; on a
     tab row it opens that tab. Mods not running / needing a newer SkyyMenu / not on the registry are still matched by name only (their
     rows cannot be read). hitsOf / firstHit (the in-mod jump) now match the key too.
  2. SETTINGS SEARCH (/settings, this mod's page): a search box under the hint line (the kit text field, tools/skyyui.py text_field) +
     Search + Clear (Enter searches too). A search lists every setting the player may change, from EVERY tab, matching label, help text,
     key or the tab's header (every word must appear); each result's second line starts with its tab name and keeps its ON / OFF buttons,
     so a result is changed right there. Clicking a tab leaves the search. Page 930 -> 980 px high (still fits 1080).
     A typed search box value travels in every click (drafts survive any click); the action is read with MenuUtil.jstr, so text typed into
     the box can never be mistaken for a click.
  3. PER-PLAYER SOUND SWITCH (task contract - used by the sound rounds running now, DO NOT CHANGE): /settings General -> "Mod sounds"
     (key menu.sounds, SkyyMenu's own switch, ON by default, saved per player in Skyy_SkyyMenu/settings/<uuid>.properties like every switch;
     a server default in settings-defaults.properties works too). Published on the shared bridge as
         settings:sounds:<uuid>  = java.lang.Boolean   (absent or TRUE = sounds on, FALSE = muted)
     at join (after the settings preload), on every change (the page, settings:fn:set, Reset all), every 30 s for each online player
     (SeenTick: picks up a changed server default) and removed when the player leaves (MenuQuit + SeenTick) and at shutdown.
  4. SHARDS ADMIN BUTTONS (Players tab; SkyyShards 0.3 made /shardadmin sub-commands - tools/... build_skyyshards_0.3.py):
       Give Farming Shard   /shardadmin give <player>      danger (press twice) - hands out a new Farming Shard item
       Shard info           /shardadmin info <player>
       Clear shard portal   /shardadmin unplace <player>   danger (press twice) - clears the Farming Shard portal record
       Unload shard world   /shardadmin unload <player>
     (other shard kinds / totems: type the chat command - one button line takes either a player or the Text box, not both.)
     The 0.3.23 harness check "/shardadmin give <player> is refused by the engine" is inverted in the 0.3.25 harness (it parses now).
  Saved data: none new (menu.sounds is one more line in the existing per-player settings file). ROUND_PINS = {}. Rollback to 0.3.24: safe
  (the menu.sounds line stays in the files and is ignored; settings:sounds:<uuid> is no longer published = sounds on for everyone).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.24.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.25.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.24"' in s and "0.3.24: SOUND PASS ROUND 1" in s and "SoundSw" not in s, "not the generated 0.3.24 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.24: SOUND PASS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.25: SEARCH BARS + THE SOUND SWITCH + THE SHARDS ADMIN BUTTONS (notes: tools/menu_0_3_25_patch.py): Server Setup's search lists the
       matching SETTINGS of every mod (label / help / key, every word; "Go to" opens the mod on that tab + page); /settings gets a search
       box over every tab (results keep their ON / OFF buttons); the player switch menu.sounds ("Mod sounds", ON) published as
       settings:sounds:<uuid> = Boolean on the bridge (absent / TRUE = on); Admin page Players: + Give Farming Shard / Shard info / Clear
       shard portal / Unload shard world (SkyyShards 0.3 sub-commands). No new saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.25.py.
0.3.24: SOUND PASS''')
rep('VERSION = "0.3.24"\n', 'VERSION = "0.3.25"\n')

# ---------------------------------------------------------------------------------------------------------------- 3. the sound switch (data)
rep('''    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
]''', '''    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
    # 0.3.25: the per-player sound switch (Skyy 2026-10-14 "do ... 6."): published as settings:sounds:<uuid> = Boolean (SoundSw)
    ("menu.sounds",          "general",     "Mod sounds",                   "Sounds the SkyWynn mods play for you (quests, bank, pets) - OFF mutes them for you only", "SkyyMenu"),
]''')
rep('''HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
''', '''HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
SOUNDS_KEY = "menu.sounds"      # 0.3.25: the per-player sound switch (SoundSw -> bridge settings:sounds:<uuid>)
SOUNDS_BRIDGE = "settings:sounds:"   # 0.3.25: + <uuid> = java.lang.Boolean (absent or TRUE = on, FALSE = muted) - the sound rounds' contract
''')
rep('''    "GONE":   "You can no longer change that setting.",      # 0.3.3: a stale click on a row whose permission node the player lost
}''', '''    "GONE":   "You can no longer change that setting.",      # 0.3.3: a stale click on a row whose permission node the player lost
    # 0.3.25: the search box
    "SHORT":  "Type at least 2 letters to search.",
    "FIND":   "Results from every tab - click ON or OFF to change one, a tab to leave the search, or Clear.",
    "NOFIND": "Nothing matches - try other words, or click Clear.",
}''')
rep('''F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
''', '''F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
F(dat, "public static final String SOUNDS_KEY = %s;" % jstr(SOUNDS_KEY))          # 0.3.25
F(dat, "public static final String SOUNDS_BRIDGE = %s;" % jstr(SOUNDS_BRIDGE))    # 0.3.25
assert SOUNDS_KEY in [k[0] for k in OWN_SETTINGS] and SOUNDS_BRIDGE == "settings:sounds:", "0.3.25: the sound switch is SkyyMenu's own (ON by default); the bridge key is the task contract"
''')

# ---------------------------------------------------------------------------------------------------------------- 2. settings page markup
rep('''SPW, SPH = 1120, 930
''', '''SPW, SPH = 1120, 980            # 0.3.25: 930 -> 980 (the search row)
SFIND_H, SFIND_BTN = 52, 150    # 0.3.25: the search row height, its Search / Clear button width
SFIND_W = SPW - 40 - 2 * SFIND_BTN - 2 * 10
''')
rep('''    "SCLOSE":    'TextButton #SkyyStgClose { Anchor: (Width: 170, Height: 50); Text: "Close"; ' + SBS + " }",
}''', '''    "SCLOSE":    'TextButton #SkyyStgClose { Anchor: (Width: 170, Height: 50); Text: "Close"; ' + SBS + " }",
    # 0.3.25: the search row - the kit text field (tools/skyyui.py text_field, the OpsPage Text box) + Search + Clear in the page's buttons
    "SFINDROW":  "Group #SkyyStgFindRow { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 2); }" % SFIND_H,
    "SFIND":     SUI.text_field("SkyyStgFindBox", "SkyyStgFind", w=SFIND_W, h=SFIND_H - 4, placeholder="Search every tab by name or words",
                                max_length=40, size=19),
    "SFINDGO":   'TextButton #SkyyStgFindGo { Anchor: (Width: %d, Height: %d); Text: "Search"; ' % (SFIND_BTN, SFIND_H - 4) + SBS + " }",
    "SFINDCLR":  'TextButton #SkyyStgFindClr { Anchor: (Width: %d, Height: %d); Text: "Clear"; ' % (SFIND_BTN, SFIND_H - 4) + SBS + " }",
    "SSP10F":    'Label { Anchor: (Width: 10, Height: %d); Text: ""; }' % (SFIND_H - 4),
}''')
rep('''_stall = 2 * 14 + 3 + 48 + 26 + 58 + 58 + 8 + 40 + SET_ROWS * 67 + 26 + 30 + 62
''', '''_stall = 2 * 14 + 3 + 48 + 26 + SFIND_H + 58 + 58 + 8 + 40 + SET_ROWS * 67 + 26 + 30 + 62   # 0.3.25: + the search row
assert SFIND_W >= 600 and SFIND_W + 2 * SFIND_BTN + 2 * 10 <= SPW - 40, "0.3.25: the search row is wider than the Settings page"
''')

# ---------------------------------------------------------------------------------------------------------------- 2. settings page fields
rep('''for f in ("public int cat;", "public int pageNo;", "public String status;", "public long armedAt;", "public String[] rowKeys;",
          "public boolean drained;"):
    F(spg, f)''', '''for f in ("public int cat;", "public int pageNo;", "public String status;", "public long armedAt;", "public String[] rowKeys;",
          "public boolean drained;", "public String search;", "public String findDraft;", "public int[] findTabs;"):   # 0.3.25: + the search
    F(spg, f)''')
rep('''  this.rowKeys = new String[@PKG@.MenuData.SET_ROWS];
  this.drained = false;
}""")''', '''  this.rowKeys = new String[@PKG@.MenuData.SET_ROWS];
  this.drained = false;
  this.search = "";
  this.findDraft = "";
  this.findTabs = new int[0];
}""")''')

# ---------------------------------------------------------------------------------------------------------------- 2. settings page search
SPG_FIND = r'''# 0.3.25: the search (Skyy 2026-10-14 "a search bar, to easily find settings"): every word of the query must appear in the setting's key,
# label, help text or its tab's SHORT name (case ignored). Fix round 2: the short name (SET_TAB "Coins"), not the long header (SET_HEAD
# "General (party, guild, teleports, menu)"), so a header word like "party" no longer lists every row of that tab. Only rows the player may change (the visible ones) are searched.
M(spg, r"""
public static boolean words(String hay, String q) {
  if (hay == null || q == null) return false;
  String h = hay.toLowerCase();
  String[] ws = q.trim().toLowerCase().split("\\s+");
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    if (ws[i].length() == 0) continue;
    if (h.indexOf(ws[i]) < 0) return false;
    n++;
  }
  return n > 0;
}""")
M(spg, r"""
public String[] found(Object[] vis, String q) {
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  for (int i = 0; i < vis.length; i++) {
    String[] vk = (String[]) vis[i];
    String head = i < @PKG@.MenuData.SET_TAB.length ? @PKG@.MenuData.SET_TAB[i] : "";
    for (int k = 0; k < vk.length; k++) {
      Object[] d = @PKG@.SetReg.info(vk[k]);
      String hay = vk[k] + " " + head + (d == null ? "" : " " + String.valueOf(d[2]) + " " + String.valueOf(d[5]));
      if (!words(hay, q)) continue;
      ks.add(vk[k]);
      ts.add(Integer.valueOf(i));
    }
  }
  int[] t = new int[ts.size()];
  for (int j = 0; j < t.length; j++) t[j] = ((Integer) ts.get(j)).intValue();
  this.findTabs = t;
  return (String[]) ks.toArray(new String[0]);
}""")
# every click carries the search box (drafts survive any click); "@" built from a char (the build script's token check)
M(spg, r"""
public @EVD@ sevd(String a) {
  return @EVD@.of("a", a).append(String.valueOf((char) 64) + "Find", "#SkyyStgFind.Value");
}""")
'''
rep('''M(spg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!this.drained)''', SPG_FIND + '''M(spg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!this.drained)''')

# the build method: one segment (its bindings all carry the box; search mode)
_b0 = s.index('public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  if (!this.drained)')
_b1 = s.index('  b.set("#SkyyStgStatus.Text", stt);\n}""")', _b0) + len('  b.set("#SkyyStgStatus.Text", stt);\n}""")')
_bold = s[_b0:_b1]
_bnew = _bold
assert _bnew.count('@EVD@.of("a", ') == 8, _bnew.count('@EVD@.of("a", ')
_bnew = _bnew.replace('@EVD@.of("a", ', 'sevd(')


def brep(old, new):
    global _bnew
    assert _bnew.count(old) == 1, "build anchor: " + old[:100]
    _bnew = _bnew.replace(old, new, 1)


brep('''  String[] keys = (String[]) vis[this.cat];
''', '''  String q = this.search == null ? "" : this.search.trim();
  boolean find = q.length() >= 2;
  String[] keys = find ? found(vis, q) : (String[]) vis[this.cat];
''')
brep('''  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHINT);
''', '''  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHINT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SFINDROW);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFIND);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDGO);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDCLR);
  String fd = this.findDraft == null ? "" : this.findDraft;
  if (fd.length() > 0) b.set("#SkyyStgFind.Value", fd);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindGo", sevd("sfind"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindClr", sevd("sfclr"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStgFind", sevd("sfind"), false);
''')
brep('''    if (narrow) b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSELN[i] : @PKG@.MenuData.UI_STABN[i]);
    else b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);''',
     '''    boolean sel = i == this.cat && !find;
    if (narrow) b.appendInline(par, sel ? @PKG@.MenuData.UI_STABSELN[i] : @PKG@.MenuData.UI_STABN[i]);
    else b.appendInline(par, sel ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);''')
brep('''    b.set("#SkyyStgDesc" + r + ".Text", d == null ? "" : String.valueOf(d[5]));''',
     '''    String desc = d == null ? "" : String.valueOf(d[5]);
    if (find && k < this.findTabs.length) {
      String own = d == null || d[0] == null ? "SkyyMenu" : String.valueOf(d[0]);
      desc = @PKG@.MenuData.SET_TAB[this.findTabs[k]] + ("SkyyMenu".equals(own) ? "" : " (" + own + ")") + ": " + desc;
    }
    b.set("#SkyyStgDesc" + r + ".Text", @PKG@.MenuUtil.clip(desc, 104));''')
brep('''    b.set("#SkyyStgEmpty.Text", @PKG@.MenuData.SET_TXT_EMPTY);''',
     '''    b.set("#SkyyStgEmpty.Text", find ? @PKG@.MenuData.SET_TXT_NOFIND : @PKG@.MenuData.SET_TXT_EMPTY);''')
brep('''  b.set("#SkyyStgHead.Text", @PKG@.MenuData.SET_HEAD[this.cat] + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (pages > 1 ? "   -   page " + (this.pageNo + 1) + " of " + pages : ""));
  b.set("#SkyyStgAlways.Text", @PKG@.MenuData.SET_ALWAYS[this.cat]);''',
     '''  String head = find ? "Search \\"" + @PKG@.MenuUtil.clip(q, 30) + "\\"" : @PKG@.MenuData.SET_HEAD[this.cat];
  b.set("#SkyyStgHead.Text", head + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (pages > 1 ? "   -   page " + (this.pageNo + 1) + " of " + pages : ""));
  b.set("#SkyyStgAlways.Text", find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat]);''')
rep(_bold, _bnew)

# the click handler: the box value first (then the action alone, so typed text can never look like a click), Search / Clear, a tab leaves
rep('''    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (data.indexOf("\\"sclose\\"") >= 0) {''', '''    if (data == null) return;
    String fk = String.valueOf((char) 64) + "Find";
    if (data.indexOf("\\"" + fk + "\\"") >= 0) {
      this.findDraft = @PKG@.MenuUtil.jstr(data, fk, 40);
      data = "{\\"a\\":\\"" + @PKG@.MenuUtil.jstr(data, "a", 24) + "\\"}";
    }
    java.util.UUID u = this.playerRef.getUuid();
    if (data.indexOf("\\"sclose\\"") >= 0) {''')
rep('''    for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) {
      if (data.indexOf("\\"stab" + i + "\\"") >= 0) { this.cat = i; this.pageNo = 0; this.status = ""; rebuild(); return; }
    }''', '''    if (data.indexOf("\\"sfind\\"") >= 0) {
      String q = this.findDraft == null ? "" : this.findDraft.trim();
      if (q.length() == 1) { this.status = @PKG@.MenuData.SET_TXT_SHORT; rebuild(); return; }
      this.search = q;
      this.pageNo = 0;
      this.status = "";
      rebuild();
      return;
    }
    if (data.indexOf("\\"sfclr\\"") >= 0) { this.search = ""; this.findDraft = ""; this.pageNo = 0; this.status = ""; rebuild(); return; }
    for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) {
      if (data.indexOf("\\"stab" + i + "\\"") >= 0) { this.cat = i; this.pageNo = 0; this.status = ""; this.search = ""; this.findDraft = ""; rebuild(); return; }
    }''')

# ---------------------------------------------------------------------------------------------------------------- 3. SoundSw
rep('''snt  = mk("SoundTest")       # 0.3.24: /soundtest - the list + the 2D play (sound pass round 1)
''', '''snt  = mk("SoundTest")       # 0.3.24: /soundtest - the list + the 2D play (sound pass round 1)
ssw  = mk("SoundSw")         # 0.3.25: the per-player sound switch on the bridge (settings:sounds:<uuid>)
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, pl)''',
    '''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, ssw, pl)''')
SOUNDSW = r'''# ================= 0.3.25 SoundSw: the player switch menu.sounds on the shared bridge (the sound rounds' contract) =================
# settings:sounds:<uuid> = java.lang.Boolean: TRUE = on, FALSE = muted; ABSENT = on (a player SkyyMenu has not seen, or one who left).
# The value = SetStore.get (own choice, else the server default, else ON). Published at join (SetLoadTask / MenuReady), on every change
# (SetStore.set / resetAll - the page, settings:fn:set), every 30 s for the online players (SeenTick: a changed server default) and
# removed when a player leaves (MenuQuit, SeenTick) and at shutdown. PUB = the uuids this mod published (so it removes only its own keys).
F(ssw, "public static final java.util.concurrent.ConcurrentHashMap PUB = new java.util.concurrent.ConcurrentHashMap();")
M(ssw, r"""
public static String key(java.util.UUID u) {
  return @PKG@.MenuData.SOUNDS_BRIDGE + u.toString();
}""")
M(ssw, r"""
public static boolean on(java.util.UUID u) {
  Boolean v = @PKG@.SetStore.get(u, @PKG@.MenuData.SOUNDS_KEY);
  return v == null || v.booleanValue();
}""")
# Fix round 2: pub runs on SkyyMenu-IO (sweep, SetLoadTask) AND the world thread (SetStore.set from the page / settings:fn:set). A sweep
# that read ON just before the player clicked OFF could put its stale TRUE after the click's FALSE. Lock-free fix (no lock: on() may read
# the player's file on the IO thread, and the world thread must never wait on that): after every put, read again and put again if the
# value changed meanwhile - whichever thread puts last has read the value AFTER its own previous put, so the last put is the current one.
M(ssw, r"""
public static void pub(java.util.UUID u) {
  if (u == null) return;
  try {
    boolean b = on(u);
    for (int i = 0; i < 4; i++) {
      Boolean v = b ? Boolean.TRUE : Boolean.FALSE;
      PUB.put(u, v);
      @PKG@.MenuUtil.bridge().put(key(u), v);
      boolean again = on(u);
      if (again == b) return;
      b = again;
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not publish the sound switch of " + u + ": " + t); }
}""")
# MenuReady (world thread): publish only when the player's settings are already in memory (no disk read here); else SetLoadTask does
M(ssw, r"""
public static void ready(java.util.UUID u) {
  if (u != null && @PKG@.SetStore.VALS.containsKey(u.toString())) pub(u);
}""")
M(ssw, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  PUB.remove(u);
  try { @PKG@.MenuUtil.bridge().remove(key(u)); } catch (Throwable t) { }
}""")
# SeenTick (SkyyMenu-IO, every 30 s): drop the players who left, refresh the online ones. Fix round: SeenTick's own snapshot is
# taken BEFORE its disk work (retryDirty, flushes, loadAdmin), so a player who joined meanwhile (and was published by ready()) would
# be forgotten = un-muted for up to 30 s. sweep therefore takes a FRESH player list (live) right before it forgets anyone; only when
# that list cannot be read does it fall back to SeenTick's snapshot. sweepWith(snapshot, fresh) is the testable core.
M(ssw, r"""
public static java.util.HashSet live() {
  java.util.HashSet h = new java.util.HashSet();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr != null && pr.isValid()) h.add(pr.getUuid());
    }
  } catch (Throwable t) { return null; }
  return h;
}""")
M(ssw, r"""
public static void sweepWith(java.util.Set online, java.util.Set fresh) {
  java.util.Set base = fresh != null ? fresh : online;
  if (base == null) return;
  java.util.ArrayList ks = new java.util.ArrayList(PUB.keySet());
  for (int i = 0; i < ks.size(); i++) {
    Object o = ks.get(i);
    if (!base.contains(o)) forget((java.util.UUID) o);
  }
  java.util.Iterator it = base.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof java.util.UUID) pub((java.util.UUID) o);
  }
}""")
M(ssw, r"""
public static void sweep(java.util.Set online) {
  sweepWith(online, live());
}""")
M(ssw, r"""
public static void clearAll() {
  java.util.ArrayList ks = new java.util.ArrayList(PUB.keySet());
  for (int i = 0; i < ks.size(); i++) forget((java.util.UUID) ks.get(i));
}""")

'''
rep('''# ---- SetSaveTask: the 500 ms delayed save (saveNow writes the NEWEST map, so several quick clicks give one write)
''', SOUNDSW + '''# ---- SetSaveTask: the 500 ms delayed save (saveNow writes the NEWEST map, so several quick clicks give one write)
''')
rep('''    if (load(k) == null) return 0;
    int r = setMem(k, key, val, onlyIfUnset);
    if (r == 2) { saveSoon(k); return 1; }
    if (r != 3) return r;''', '''    if (load(k) == null) return 0;
    int r = setMem(k, key, val, onlyIfUnset);
    if (r == 2) { saveSoon(k); if (@PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25
    if (r != 3) { if (r == 1 && @PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return r; }''')
rep('''    int r = resetMem(k, keep);
    if (r == 2) { saveSoon(k); return 1; }
    if (r != 3) return r;''', '''    int r = resetMem(k, keep);
    if (r == 2) { saveSoon(k); @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25
    if (r != 3) { if (r == 1) @PKG@.SoundSw.pub(u); return r; }''')
rep('''    @PKG@.SetStore.load(this.k);
    @PKG@.Tips.migrate(this.u);''', '''    @PKG@.SetStore.load(this.k);
    @PKG@.SoundSw.pub(this.u);   // 0.3.25
    @PKG@.Tips.migrate(this.u);''')
rep('''    @PKG@.SetLoadTask.preload(pr);
    @PKG@.MenuLayout.preload(pr.getUuid());''', '''    @PKG@.SetLoadTask.preload(pr);
    @PKG@.SoundSw.ready(pr.getUuid());   // 0.3.25
    @PKG@.MenuLayout.preload(pr.getUuid());''')
rep('''    @PKG@.SetReg.loadAdmin(false);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }''', '''    @PKG@.SetReg.loadAdmin(false);
    @PKG@.SoundSw.sweep(online);   // 0.3.25
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }''')
rep('''    @PKG@.Given.forget(pr.getUuid());
    @PKG@.PageGuard.JOINS.remove(pr.getUuid());''', '''    @PKG@.Given.forget(pr.getUuid());
    @PKG@.PageGuard.JOINS.remove(pr.getUuid());
    @PKG@.SoundSw.forget(pr.getUuid());   // 0.3.25''')
rep('''  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
''', '''  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
  try { @PKG@.SoundSw.clearAll(); } catch (Throwable t) { }   // 0.3.25
''')

# ---------------------------------------------------------------------------------------------------------------- 1. Server Setup search
rep('''          "public boolean locked;", "public boolean jumpHit;", "public String[] listMods;", "public String[] listReload;", "public String[] tKeys;",''',
    '''          "public boolean locked;", "public boolean jumpHit;", "public String[] listMods;", "public String[] listReload;", "public String[] tKeys;",
          "public String[] listJump;", "public int jumpRow;",   # 0.3.25: a search result's target (r<row> / c<tab>), the row to show''')
rep('''  this.listMods = new String[@MD@.ADM_LROWS];
  this.listReload = new String[@MD@.ADM_LROWS];
''', '''  this.listMods = new String[@MD@.ADM_LROWS];
  this.listReload = new String[@MD@.ADM_LROWS];
  this.listJump = new String[@MD@.ADM_LROWS];
  this.jumpRow = -1;
''')
ADM_FIND = r'''# 0.3.25: a setting matches when EVERY word of the search is in its key, label or help text (case ignored)
M(apg, r"""
public static boolean words(String hay, String q) {
  if (hay == null || q == null) return false;
  String h = hay.toLowerCase();
  String[] ws = q.trim().toLowerCase().split("\\s+");
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    if (ws[i].length() == 0) continue;
    if (h.indexOf(ws[i]) < 0) return false;
    n++;
  }
  return n > 0;
}""")
M(apg, r"""
public static boolean rowHit(Object[] r, String q) {
  return r != null && words(rv(r, 0) + " " + rv(r, 1) + " " + rv(r, 10), q);
}""")
# 0.3.25: the search results of one mod: { mod, "hit", name, line 2, "", "0", target } - a tab ("c<i>") or a setting ("r<i>")
M(apg, r"""
public static java.util.ArrayList settingHits(String m, Object[] h, String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String title = hs(h, 2).length() > 0 ? hs(h, 2) : m;
  String[] ids = catIds(h);
  for (int c = 0; c < ids.length; c++) {
    if (words(catLabel(h, c), q)) out.add(new String[] { m, "hit", "Tab: " + catLabel(h, c), title + " (" + m + ") - every setting on its " + catLabel(h, c) + " tab", "", "0", "c" + c });
  }
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r == null || !rowHit(r, q)) continue;
    String help = rv(r, 10);
    String name = rv(r, 1).length() > 0 ? rv(r, 1) : rv(r, 0);
    out.add(new String[] { m, "hit", name, title + " > " + catLabel(h, catOf(h, r)) + "  -  " + rv(r, 0) + (help.length() > 0 ? "  -  " + help : ""), "", "0", "r" + i });
  }
  return out;
}""")
M(apg, r"""
public static void addRow(java.util.ArrayList found, java.util.ArrayList keys, String sortKey, String[] e) {
  keys.add(sortKey + "\t" + String.valueOf(1000000 + found.size()).substring(1));
  found.add(e);
}""")
'''
rep('''M(apg, r"""
public static java.util.ArrayList hitsOf(Object[] h, String q) {''', ADM_FIND + '''M(apg, r"""
public static java.util.ArrayList hitsOf(Object[] h, String q) {''')
rep('''    if (r != null && (has(rv(r, 1), q) || has(rv(r, 10), q))) out.add(rv(r, 1));''',
    '''    if (rowHit(r, q)) out.add(rv(r, 1));   // 0.3.25: + the key, every word''')
rep('''    if (r != null && (has(rv(r, 1), q) || has(rv(r, 10), q))) return i;''',
    '''    if (rowHit(r, q)) return i;   // 0.3.25: + the key, every word''')
rep('''  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) {
    seen.add(cm[i]);
    String[] e = cfgRow(cm[i], hdr(cm[i]), find ? q : null);
    if (e == null) continue;
    keys.add("0" + cm[i].toLowerCase() + "\\t" + found.size());
    found.add(e);
  }
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) {
    String m = @MD@.MOD_NAME[k];
    if (seen.contains(m) || !installed(k)) continue;
    if (find && !has(m, q)) continue;
    keys.add("1" + m.toLowerCase() + "\\t" + found.size());
    found.add(fileRow(k));
  }''', '''  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) {
    String m = cm[i];
    seen.add(m);
    Object[] h = hdr(m);
    // 0.3.25: a running mod on the registry lists its matching SETTINGS (and itself first when its name matches)
    if (find && h != null && contractOk(h) && alive(m)) {
      if (has(m, q) || has(hs(h, 2), q)) addRow(found, keys, "0" + m.toLowerCase(), cfgRow(m, h, null));
      java.util.ArrayList hits = settingHits(m, h, q);
      for (int j = 0; j < hits.size(); j++) addRow(found, keys, "0" + m.toLowerCase(), (String[]) hits.get(j));
      continue;
    }
    String[] e = cfgRow(m, h, find ? q : null);
    if (e == null) continue;
    addRow(found, keys, "0" + m.toLowerCase(), e);
  }
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) {
    String m = @MD@.MOD_NAME[k];
    if (seen.contains(m) || !installed(k)) continue;
    if (find && !has(m, q)) continue;
    addRow(found, keys, "1" + m.toLowerCase(), fileRow(k));
  }''')
rep('''  String sub = @MD@.ADM_LISTSUB;
  if (q.length() < 2 && nfile > 0) sub = ncfg + (ncfg == 1 ? " mod is" : " mods are") + " set up for in-game editing - the rest show their file. Click Open.";
  if (q.length() >= 2 && this.status.length() == 0) {
    if (lr.isEmpty()) setStatus("Nothing matches \\"" + q + "\\" - mods not set up yet are matched by name only.", 2);
    else setStatus(lr.size() + (lr.size() == 1 ? " mod matches" : " mods match") + " \\"" + q + "\\" - Open shows the first hit.", 0);
  }''', '''  String sub = @MD@.ADM_LISTSUB;
  if (q.length() < 2 && nfile > 0) sub = ncfg + (ncfg == 1 ? " mod is" : " mods are") + " set up for in-game editing - the rest show their file. Click Open.";
  int nhit = 0;
  for (int i = 0; i < lr.size(); i++) if ("hit".equals(((String[]) lr.get(i))[1])) nhit++;
  if (q.length() >= 2) sub = "Search: every mod's settings by name, help text or key (every word must match).";   // 0.3.25
  if (q.length() >= 2 && this.status.length() == 0) {
    if (lr.isEmpty()) setStatus("Nothing matches \\"" + q + "\\" - try other words. Mods not set up yet are matched by name only.", 2);
    else if (nhit > 0) setStatus(nhit + (nhit == 1 ? " match" : " matches") + " for \\"" + q + "\\" - Go to opens the setting, ready to change.", 0);
    else setStatus(lr.size() + (lr.size() == 1 ? " mod matches" : " mods match") + " \\"" + q + "\\" - Open shows the first hit.", 0);
  }''')
rep('''  this.listMods = new String[per];
  this.listReload = new String[per];
  for (int r = 0; r < per; r++) {''', '''  this.listMods = new String[per];
  this.listReload = new String[per];
  this.listJump = new String[per];
  for (int r = 0; r < per; r++) {''')
rep('''    this.listReload[r] = e[4];
''', '''    this.listReload[r] = e[4];
    this.listJump[r] = e.length > 6 ? e[6] : "";   // 0.3.25
''')
rep('''    b.appendInline(rsel, btn("SkyyAdmLOpen" + r, 150, 52, "Open", @MD@.ADM_BS));''',
    '''    b.appendInline(rsel, btn("SkyyAdmLOpen" + r, 150, 52, this.listJump[r].length() > 0 ? "Go to" : "Open", @MD@.ADM_BS));''')
rep('''    this.jumpHit = h != null && this.search != null && this.search.trim().length() >= 2;
    return;''', '''    this.jumpHit = h != null && this.search != null && this.search.trim().length() >= 2;
    // 0.3.25: a search result goes to exactly its tab / setting
    String j = this.listJump != null && r < this.listJump.length ? this.listJump[r] : null;
    int jn = j != null && j.length() > 1 ? tailNum(j, j.substring(0, 1)) : -1;
    if (h != null && jn >= 0 && j.startsWith("c")) { this.jumpHit = false; this.cat = jn; }
    if (h != null && jn >= 0 && j.startsWith("r")) { this.jumpHit = false; this.jumpRow = jn; }
    return;''')
ADM_JUMPTO = r'''# 0.3.25: open the mod on the tab + page of row i (an advanced row switches "show advanced" on) - a search result's Go to
M(apg, r"""
public void jumpTo(Object[] h, int i) {
  Object[] r = rowAt(h, i);
  if (r == null) return;
  this.cat = catOf(h, r);
  if (hasFlag(r, "adv")) this.showAdv = true;
  int[] vis = visible(h);
  for (int k = 0; k < vis.length; k++) if (vis[k] == i) { this.modPage = k / @MD@.ADM_ROWS; break; }
  setStatus("Found: " + rv(r, 1) + " (" + catLabel(h, this.cat) + " tab).", 0);
}""")
'''
rep('''M(apg, r"""
public static boolean typed(String t) {''', ADM_JUMPTO + '''M(apg, r"""
public static boolean typed(String t) {''')
rep('''  if (this.jumpHit) { jump(h); this.jumpHit = false; }
''', '''  if (this.jumpHit) { jump(h); this.jumpHit = false; }
  if (this.jumpRow >= 0) { jumpTo(h, this.jumpRow); this.jumpRow = -1; }   // 0.3.25
''')

# ---------------------------------------------------------------------------------------------------------------- 4. the Shards buttons
rep('''    (2, "Refund rebirth arm", "rebirthadmin refund {t}", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
''', '''    (2, "Refund rebirth arm", "rebirthadmin refund {t}", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
    # 0.3.25: SkyyShards 0.3's sub-commands (give / info / unplace / unload <player>; no shard word = the Farming Shard). give hands out
    # a new shard item and unplace clears the portal record: danger rows (press twice)
    (2, "Give Farming Shard", "shardadmin give {p}", "skyyshards.admin", "SkyyShards", True, "", ""),
    (2, "Shard info", "shardadmin info {p}", "skyyshards.admin", "SkyyShards", False, "", ""),
    (2, "Clear shard portal", "shardadmin unplace {p}", "skyyshards.admin", "SkyyShards", True, "", ""),
    (2, "Unload shard world", "shardadmin unload {p}", "skyyshards.admin", "SkyyShards", False, "", ""),
''')

# ---------------------------------------------------------------------------------------------------------------- done
assert s.count("SoundSw") >= 12 and s.count('mk("SoundSw")') == 1
_i = s.index
assert _i('ssw  = mk("SoundSw")') < _i("public static void pub(java.util.UUID u)") < _i("@PKG@.SoundSw.pub(u); return 1; }   // 0.3.25") < _i("@PKG@.SoundSw.pub(this.u);")
assert _i("public String[] found(Object[] vis, String q)") < _i("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  if (!this.drained)")
assert _i("public static java.util.ArrayList settingHits(") < _i("public java.util.ArrayList listRows()") and _i("public void jumpTo(") < _i("public void drawMod(")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.24 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.24 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
