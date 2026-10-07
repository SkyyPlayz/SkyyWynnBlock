"""Derive SkyyHud/build_skyyhud_0.3.15.py from the generated 0.3.14 (the SET pin since 2026-10-06; 0.3.14 is left untouched; line endings
preserved).
0.3.15 = a SEASONS entry in the layout editor that moves Dynamic Seasons' own season / weather / zone widget (Skyy 2026-10-06, with a
screenshot of it sitting bottom-right over SkyyHud's Skills list: "i know its not our mod, but can you add the widget from dynamic season
to our hud controller? so we can move it from there?").
FACTS (read-only bytecode of DynamicSeasons-6.1.2.jar + the engine, 2026-10-06):
  - DS shows its widget as a CustomUIHud subclass DynamicSeasons.ui.SeasonsDisplay, key "DynSeasons_hud", zOrder 0, through the engine's
    HudManager.addCustomHud (build() appends their own Hud/SeasonsHUD.ui; its root Group #HudBackground is anchored Right 0, Bottom 250,
    96 x 320). They keep one object per PlayerRef in their own map and call SeasonsDisplay.show(Player) on PlayerReady / heartbeats /
    /season commands: show() only makes a NEW object when their map has none, so the full document (CustomHud clear = true) is sent only
    for a new object. Their regular update() sends DELTAS only (CustomHud clear = false: label texts, weather icon Visible flags,
    "#HudBackground.Visible" when their show condition flips) - they NEVER send #HudBackground.Anchor.
  - The engine: HudManager.customHuds is a LinkedHashMap keyed by the HUD key (not thread safe -> read on the world thread only);
    CustomUIHud.update(boolean, UICommandBuilder) is PUBLIC and writes a CustomHud(key, zOrder, clear, commands) packet. So another plugin
    can move their widget WITHOUT replacing it: getCustomHud("DynSeasons_hud").update(false, { Set #HudBackground.Anchor }). Our move is
    undone only when their HUD object is replaced (a new full document) - SkyyHud then re-sends the one Set (identity check).
  - The engine's Player.resetManagers (Universe.resetPlayer) clears every custom HUD; DS's TemperatureHUD ("DynTemperature_hud") is a
    separate HUD (not part of this entry).
WHAT 0.3.15 DOES (no file of theirs is shipped or overridden; nothing of theirs is copied; their classes are never referenced - only the
key, their class NAME as a string and the element id #HudBackground):
  - Widget id Seasons APPENDED to Widgets.IDS (label "Seasons (Dynamic Seasons)"), default ON at THEIR own spot (br, x 0, y 250 = the
    anchor their file has), box 96 x 320, fixed size (WLayout.fixed: scale always 100, no Size buttons). skyyhud_main never draws it.
  - Editor: dragged / arrowed / hidden / shown / exported / imported / profiled / saved per player like every widget; its preview is a
    96 x 320 box "Seasons". Settings (the editor's Settings button or Widgets / Settings) = a small kit page: Show On / Off, Snap to (the 9
    presets, 8 px from the edges like every widget), Default spot (their own place), Reset, Back.
  - Runtime (DsLink): only while Dynamic Seasons 6.x is installed AND enabled (checked once through the engine's PluginManager, at the
    first player attach / editor open - BlueOrbit:DynamicSeasons; any other major version = left alone, one log line). Without it: the
    entry is hidden in the editor, Widgets / Settings and the Settings page, nothing is scheduled, the saved line is kept.
    A player whose Seasons layout is at their default spot and shown costs nothing (no task, no packet). Otherwise every 1 s HUD tick
    queues ONE tiny task on the player's world thread (never two at once) that reads HudManager.getCustomHud("DynSeasons_hud"): when the
    object is DS's SeasonsDisplay (class name check) and it is a NEW object or the layout changed since the last send, ONE update with
    one Set #HudBackground.Anchor goes out (the SkyyHud anchor maths, Widgets.anchorSrcWH, at 96 x 320). Hidden = the anchor moves off
    screen (Top -4000, Left -4000) - their own Visible flag is never touched (their show / hide rules keep working). Back at the default
    spot = one Set with their own anchor, then nothing again. A layout change (editor, settings, import, reset, profile load) asks at once.
    PlayerReady (every world change, after SkyyHud's attach) forgets the last object so the next check re-sends.
UNVERIFIED (needs the game): that the client applies a Set Anchor sent to another plugin's HUD document (the same CustomHud packet DS
itself sends; SkyyHud's minimap pan uses Set Anchor on its own HUD), that a negative anchor (off screen) hides it, and how it looks while DS
re-creates its HUD (up to 1 s at their spot before the re-send).
Harness: python SkyyHud/test_skyyhud_0.3.15.py (bare JVM, a FAKE SeasonsDisplay class made in the harness only).
To regenerate, delete SkyyHud/build_skyyhud_0.3.15.py first (the script refuses to overwrite it).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI      # patch time only: the Seasons settings page (kit markup, proven tokens)

src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.14.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.15.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:90])
    s = s.replace(old, new)


SUI.verify(quiet=True)
KIT_ID = SUI.kit_id()

DS_KEY = "DynSeasons_hud"
DS_CLS = "DynamicSeasons.ui.SeasonsDisplay"
DS_W, DS_H, DS_RIGHT, DS_BOTTOM = 96, 320, 0, 250          # their SeasonsHUD.ui #HudBackground anchor (6.1.2)

# =================================================================================================== the settings page (kit)
SP = "SkyyDsS"
PAGE_W = 1100
LAB_W = 220
ROW_H, ROW_GAP = 32, 8
binds = []


def opt_button(bid, text, cond, w):
    on = SUI.button(bid, text, "tertiary", "small", w=w, selected=True, anchor={"right": 6})
    off = SUI.button(bid, text, "tertiary", "small", w=w, anchor={"right": 6})
    return SUI.choose(cond, on, off)


def page_build():
    body = []

    def section(text):
        body.append(("sec", text))

    def row(rid, label, items, hint=None):
        body.append(("row", (rid, label, items, hint)))

    section("Dynamic Seasons widget")
    row("Show", "Show it", [("SkyyDsSEnOn", "On", "en", "ds:en:1", 110), ("SkyyDsSEnOff", "Off", "!en", "ds:en:0", 110)])
    row("Snap", "Snap to", [("SkyyDsSAn" + a.upper(), a.upper(), "anc.equals(%s)" % SUI.java_lit(a), "ds:an:" + a, 66)
                            for a in ("tl", "t", "tr", "l", "c", "r", "bl", "b", "br")])
    row("Home", "Its own spot", [("SkyyDsSHome", "Default spot", "home", "ds:home", 190)],
        hint=("SkyyDsSHomeTx", "Where Dynamic Seasons puts it: bottom right."))
    row("Info", "", [], hint=("SkyyDsSInfo", "Dynamic Seasons draws it - SkyyHud only moves it. Drag it in the editor like the others."))
    section("Status")
    row("St", "Dynamic Seasons", [], hint=("SkyyDsSStTx", SUI.J("dsText", "Dynamic Seasons 6.1.2 found - you can move its widget.")))

    n_sec = sum(1 for k, _d in body if k == "sec")
    n_row = sum(1 for k, _d in body if k == "row")
    foot_h = SUI.BTN_H + 8
    inner = n_sec * (26 + 14) + n_row * (ROW_H + ROW_GAP) + foot_h
    page_h = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + inner
    sh = SUI.page_shell(SP, PAGE_W, page_h, title="Seasons widget")
    assert sh.fit([inner]) == 0
    ap = sh.appends
    B_ = sh.body
    k_sec = 0
    for kind, d in body:
        if kind == "sec":
            ap.append((B_, SUI.section("SkyyDsSHd%d" % k_sec, d)))
            k_sec += 1
            continue
        rid, label, items, hint = d
        gid = "SkyyDsSR" + rid
        ap.append((B_, SUI.group(gid, "Left", h=ROW_H, anchor={"bottom": ROW_GAP})))
        if label:
            ap.text(gid, None, label, "default", w=LAB_W, h=ROW_H)
        else:
            ap.append((gid, SUI.spacer(w=LAB_W, h=ROW_H)))
        used = LAB_W
        for bid, text, cond, payload, w in items:
            ap.append((gid, opt_button(bid, text, cond, w)))
            binds.append(("#" + bid, payload))
            used += w + 6
        if hint:
            hid, htext = hint
            ap.text(gid, hid, htext, "caption", w=PAGE_W - 2 * SUI.CONTENT_PAD - used - 16, h=ROW_H, anchor={"left": 16})
        assert used <= PAGE_W - 2 * SUI.CONTENT_PAD, rid
    foot = "SkyyDsSFoot"
    ap.append((B_, SUI.button_row(foot, SUI.BTN_H, "left", 8)))
    ap.append((foot, SUI.button("SkyyDsSBack", "< Back", "secondary", sound="cancel")))
    ap.append((foot, SUI.button("SkyyDsSReset", "Reset", "secondary", anchor={"left": 12})))
    binds.append(("#SkyyDsSBack", "ds:back"))
    binds.append(("#SkyyDsSReset", "ds:reset"))
    SUI.check_page(ap, SP)
    toks = SUI.assert_proven(ap, what="SkyyHud Seasons settings page")
    for _p, mk in ap:
        assert "_" not in str(mk).split("{")[0], "no underscore in an element id: " + str(mk)[:60]
    out = []
    for parent, mk in ap:
        out.append(SUI.java_append(parent, mk, b="b"))
    for ident, prop, val in ap.sets:
        out.append(SUI.java_set(ident, prop, val, b="b"))
    for sel, payload in binds:
        out.append("ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(payload)))
    return "\n".join("  " + l for l in out), page_h, len(toks), len(ap)


DSUI_JAVA, DSUI_H, DSUI_TOKENS, DSUI_APPENDS = page_build()
assert "@@" not in DSUI_JAVA and '"""' not in DSUI_JAVA
assert DSUI_H <= 1080, DSUI_H
print("patch: Seasons settings page %d x %d, %d appends, %d proven tokens (kit %s)" % (PAGE_W, DSUI_H, DSUI_APPENDS, DSUI_TOKENS, KIT_ID))

# =================================================================================================== the generated script
rep('''"""SkyyHud 0.3.14 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.14.py            -> SkyyHud/SkyyHud-0.3.14.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.15 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.15.py            -> SkyyHud/SkyyHud-0.3.15.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.15 (generated by tools/hud_0_3_15_patch.py from 0.3.14): a SEASONS entry that MOVES Dynamic Seasons' own season / weather / zone
  widget (Skyy 2026-10-06: "can you add the widget from dynamic season to our hud controller? so we can move it from there?"). Not our
  mod: nothing of theirs is shipped, overridden or copied; SkyyHud only sends ONE runtime Set to the HUD they show (the facts are in
  tools/hud_0_3_15_patch.py's docstring: their HUD key "DynSeasons_hud", class DynamicSeasons.ui.SeasonsDisplay, root #HudBackground
  anchored Right 0 / Bottom 250, 96 x 320; they send deltas only and never touch its Anchor; CustomUIHud.update is public).
  - Widget id Seasons APPENDED to Widgets.IDS (0.3.14 files, codes and profiles load as before; 0.3.14 ignores the id). Label
    "Seasons (Dynamic Seasons)", default ON at their own spot (br, x 0, y 250), box 96 x 320, FIXED size (WLayout.fixed, set from
    Widgets.def like bw / bh: scale always 100; the editor shows no Size buttons for it). skyyhud_main never draws it.
  - Editor: drag / arrows / Hide / Show / export / import / profiles / reset like every widget; preview = a 96 x 320 "Seasons" box.
    Settings = a small kit page (DsUi): Show On / Off, Snap to (9 presets), Default spot, Reset, Back.
  - DsLink: only with Dynamic Seasons 6.x installed + enabled (engine PluginManager, BlueOrbit:DynamicSeasons, checked once at the first
    attach / editor open). Without it the entry is hidden from the editor pages and nothing runs. At their spot + shown = no cost.
    Moved or hidden: each 1 s tick queues one small task on the player's world thread (never two at once): HudManager.getCustomHud(
    "DynSeasons_hud") - when it is their SeasonsDisplay (class NAME check) and a NEW object or the layout changed, ONE update(false,
    { Set #HudBackground.Anchor }) - Hidden = off screen (Top -4000, Left -4000); their Visible flag is never touched. Back at their spot
    = one Set with their own anchor, then nothing. Layout changes ask at once (rebuildFor); PlayerReady (attach) re-sends.
''')
rep('VERSION = "0.3.14"', 'VERSION = "0.3.15"')

# ---- engine members DsLink uses (API drift fails the build here)
rep('''pool.get(MMT["PID"])
''', '''pool.get(MMT["PID"])
# 0.3.15 Seasons mover: every engine member DsLink uses
for c, m in ((MMT["HM"], "getCustomHud"), (MMT["HUD"], "update"), (PLA, "getHudManager"), (REF, "isValid"), (REF, "getStore"),
             (ST, "getComponent"), (PR, "getReference"), (PR, "isValid"), (PR, "getUuid"), (WLD, "execute"), (MMT["ES"], "getWorld"),
             (UCB, "setObject"), (MMT["PLM"], "getPlugin"), (MMT["PB"], "isEnabled"), (MMT["PB"], "getManifest")):
    B.probe(pool, c, m)
''')

# ---- 0.3.15 classes
rep('''cmmoff = pool.makeClass(PKG + ".HudMinimapOffCmd", pool.get(APC))
''', '''cmmoff = pool.makeClass(PKG + ".HudMinimapOffCmd", pool.get(APC))
# 0.3.15 Seasons mover (Dynamic Seasons' own widget; tools/hud_0_3_15_patch.py)
dslink = pool.makeClass(PKG + ".DsLink")                    # the check, the per-player state map, the world-thread re-send
dsstate = pool.makeClass(PKG + ".DsState")                  # one player
dscheck = pool.makeClass(PKG + ".DsCheck")                  # Runnable: DsLink.checkNow on the player's world thread
dsui = pool.makeClass(PKG + ".DsUi")                        # the settings page (kit markup made by the patch)
''')

# ---- the widget list
rep('''DEFAULTS["Online"] = (False, "tr", 8, 206)
''', '''DEFAULTS["Online"] = (False, "tr", 8, 206)
# 0.3.15 SEASONS (Dynamic Seasons' own widget, moved by DsLink): default ON at THEIR spot (their SeasonsHUD.ui: Right %d, Bottom %d,
# %d x %d), fixed size (WLayout.fixed)
IDS.append("Seasons")
DEFAULTS["Seasons"] = (True, "br", %d, %d)
LABELS["Seasons"] = "Seasons (Dynamic Seasons)"
SIZES["Seasons"] = (%d, %d)
assert IDS[-2:] == ["Minimap", "Seasons"]
''' % (DS_RIGHT, DS_BOTTOM, DS_W, DS_H, DS_RIGHT, DS_BOTTOM, DS_W, DS_H))

# ---- DsLink part A (fields + the Dynamic Seasons check) right before WLayout (Widgets.text reads DS)
DS_EARLY = r'''
# ================= 0.3.15 DsLink part A: the Dynamic Seasons check (engine PluginManager only - never a class of theirs) =================
for _f in ("public static volatile int DS = 0;", 'public static volatile String DSV = "";',
           'public static final String KEY = "@@KEY@@";', 'public static final String CLS = "@@CLS@@";',
           'public static final String SEL = "#HudBackground.Anchor";',
           'public static final String HOME = "(Bottom: @@BOT@@, Right: @@RIGHT@@, Width: @@W@@, Height: @@H@@)";',
           'public static final String GONE = "(Top: -4000, Left: -4000, Width: @@W@@, Height: @@H@@)";',
           "public static final int W = @@W@@;", "public static final int H = @@H@@;",
           "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.atomic.AtomicInteger SENT = new java.util.concurrent.atomic.AtomicInteger();",
           "public static final java.util.concurrent.atomic.AtomicInteger QUEUED = new java.util.concurrent.atomic.AtomicInteger();",
           "public static final java.util.concurrent.atomic.AtomicInteger ERRS = new java.util.concurrent.atomic.AtomicInteger();",
           "public static volatile com.hypixel.hytale.logger.HytaleLogger LOG;"):
    dslink.addField(CtField.make(_f, dslink))
dslink.addMethod(CtNewMethod.make("""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyHud] " + m); } catch (Throwable t) { }
}""", dslink))
dslink.addMethod(CtNewMethod.make("""
public static void err(String what, Throwable t) {
  if (ERRS.incrementAndGet() > 5) return;
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyHud] seasons: " + what + " failed: " + t); } catch (Throwable x) { }
}""", dslink))
# 0 = not checked, 1 = Dynamic Seasons 6.x installed + enabled, 2 = missing / disabled / another major version (left alone)
dslink.addMethod(CtNewMethod.make("""
public static synchronized void check() {
  if (DS != 0) return;
  boolean ok = false;
  boolean found = false;
  String ver = "";
  try {
    com.hypixel.hytale.server.core.plugin.PluginBase pb = com.hypixel.hytale.server.core.plugin.PluginManager.get().getPlugin(new com.hypixel.hytale.common.plugin.PluginIdentifier("BlueOrbit", "DynamicSeasons"));
    if (pb != null && pb.isEnabled()) {
      found = true;
      try { ver = String.valueOf(pb.getManifest().getVersion()); } catch (Throwable t) { ver = "?"; }
      ok = ver.startsWith("6.");
    }
  } catch (Throwable t) { ok = false; }
  DSV = ver;
  DS = ok ? 1 : 2;
  if (ok) info("seasons: Dynamic Seasons " + ver + " found - its season widget can be moved in /skyyhud (Seasons)");
  else if (found) info("seasons: Dynamic Seasons " + ver + " is not a 6.x version - its widget is left alone");
  else info("seasons: Dynamic Seasons (BlueOrbit:DynamicSeasons) is not installed or is disabled - the Seasons entry stays hidden");
}""", dslink))
dslink.addMethod(CtNewMethod.make("""
public static boolean present() {
  if (DS == 0) check();
  return DS == 1;
}""", dslink))
'''
for _k, _v in (("KEY", DS_KEY), ("CLS", DS_CLS), ("BOT", DS_BOTTOM), ("RIGHT", DS_RIGHT), ("W", DS_W), ("H", DS_H)):
    DS_EARLY = DS_EARLY.replace("@@%s@@" % _k, str(_v))
assert "@@" not in DS_EARLY
rep('''# ================= WLayout =================
''', DS_EARLY + '''
# ================= WLayout =================
''')

# ---- idList (the "widgets are ..." hint in layout-code errors): name Seasons only while Dynamic Seasons is here.
#      (reads DsLink.DS, never present(): a config check at startup must not latch the one-time plugin check early)
#      knownId still accepts Seasons so a code exported on a server with Dynamic Seasons imports cleanly (the line is kept, unused)
rep('''public static String idList() {{
  StringBuilder sb = new StringBuilder();
  String[] ids = {PKG}.Widgets.IDS;
  for (int i = 0; i < ids.length; i++) {{ if (i > 0) sb.append(", "); sb.append(ids[i]); }}
  return sb.toString();
}}""", hcfg))''', '''public static String idList() {{
  StringBuilder sb = new StringBuilder();
  String[] ids = {PKG}.Widgets.IDS;
  boolean ds = {PKG}.DsLink.DS == 1;
  int k = 0;
  for (int i = 0; i < ids.length; i++) {{
    if (!ds && "Seasons".equals(ids[i])) continue;
    if (k > 0) sb.append(", ");
    sb.append(ids[i]);
    k++;
  }}
  return sb.toString();
}}""", hcfg))''')

# ---- WLayout.fixed: a widget whose size never changes (the Seasons box = their 96 x 320); copied from Widgets.def like bw / bh
rep('''wl.addField(CtField.make("public String mm;", wl))
''', '''wl.addField(CtField.make("public String mm;", wl))
# 0.3.15: fixed = a box of one size (Seasons: Dynamic Seasons' widget); never written to the file - Widgets.def sets it
wl.addField(CtField.make("public boolean fixed;", wl))
''')
rep('''  this.mm = null;
}""", wl))''', '''  this.mm = null;
  this.fixed = false;
}""", wl))''')
rep('''    if (def != null) {{ w.bw = def.bw; w.bh = def.bh; w.ldef = def.ldef; w.lines = def.ldef; w.mm = def.mm; }}''',
    '''    if (def != null) {{ w.bw = def.bw; w.bh = def.bh; w.ldef = def.ldef; w.lines = def.ldef; w.mm = def.mm; w.fixed = def.fixed; if (def.fixed) w.scale = 100; }}''')
rep('''        if i == "Minimap":
            extra = ' w.ldef = %d; w.lines = %d; w.mm = ""; w.en = %s.MmCfg.DEFAULT_ON;' % (MM_DEF_MASK, MM_DEF_MASK, PKG)''',
    '''        if i == "Minimap":
            extra = ' w.ldef = %d; w.lines = %d; w.mm = ""; w.en = %s.MmCfg.DEFAULT_ON;' % (MM_DEF_MASK, MM_DEF_MASK, PKG)
        if i == "Seasons":
            extra = " w.fixed = true;"''')
# ---- Widgets.text: the editor's stand-in text for the Seasons box
rep('''    if ("Minimap".equals(id)) return {PKG}.MmCfg.BM == 2 ? "Needs BetterMap" : "Minimap";''',
    '''    if ("Minimap".equals(id)) return {PKG}.MmCfg.BM == 2 ? "Needs BetterMap" : "Minimap";
    if ("Seasons".equals(id)) return "Seasons";''')
# ---- the drawn width of a fixed box = its box
rep('''  if ("Minimap".equals(id)) return l.bw * l.scale / 100;''',
    '''  if ("Minimap".equals(id) || l.fixed) return l.bw * l.scale / 100;''')
# ---- clampToScreen keeps a fixed box at 100 %
rep('''  if (l.mm != null) l.scale = {PKG}.MmCfg.snapScale(l.scale);''',
    '''  if (l.mm != null) l.scale = {PKG}.MmCfg.snapScale(l.scale);
  if (l.fixed) l.scale = 100;''')
# ---- importCode: fixed from the built-in layout
rep('''    if (dd.mm == null) l.mm = null; else if (l.mm == null) l.mm = "";''',
    '''    if (dd.mm == null) l.mm = null; else if (l.mm == null) l.mm = "";
    l.fixed = dd.fixed;''')

# =================================================================================================== DsLink part B + DsUi (before HudMain)
DS_BLOCK = r'''
# ================= 0.3.15 SEASONS mover (Dynamic Seasons' own widget; tools/hud_0_3_15_patch.py) =================
# ---------------------------------------------------------------- DsState: one player (the world-thread fields are only written there)
for _f in ("public @PR@ pr;", "public java.util.UUID uuid;", "public volatile @WLD@ world;", "public volatile @ST@ store;",
           "public volatile Object hud;", "public volatile String anc;", "public volatile boolean queued;"):
    MMF(dsstate, _f)
MMC(dsstate, "public DsState(@PR@ pr) { this.pr = pr; this.uuid = pr.getUuid(); this.hud = null; this.anc = null; this.queued = false; }")
# ---------------------------------------------------------------- DsLink part B
# where the player wants their widget: null = their own spot and shown (nothing to send), else the Anchor text (off screen when hidden)
MMM(dslink, r"""
public static String target(java.util.UUID u) {
  @PKG@.WLayout l = null;
  try { l = (@PKG@.WLayout) @PKG@.LayoutStore.get(u).get("Seasons"); } catch (Throwable t) { l = null; }
  if (l == null) return null;
  if (!l.en) return GONE;
  String a = @PKG@.Widgets.anchorSrcWH(l, W, H);
  return HOME.equals(a) ? null : a;
}""")
MMM(dslink, r"""
public static boolean needed(@PKG@.DsState s) {
  return s.anc != null || target(s.uuid) != null;
}""")
# ONE update to THEIR HUD object: Set #HudBackground.Anchor (CustomUIHud.update is public; their key / zOrder, clear = false)
MMM(dslink, r"""
public static void send(@HUD@ h, String anc) {
  @UCB@ b = new @UCB@();
  b.setObject(SEL, @PKG@.Minimap.ancObj(anc));
  h.update(false, b);
  SENT.incrementAndGet();
}""")
# world thread: their HUD now -> re-send only for a new object or a changed layout
MMM(dslink, r"""
public static void checkNow(@PKG@.DsState s) {
  s.queued = false;
  try {
    @PR@ pr = s.pr;
    if (pr == null || !pr.isValid()) return;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || st != s.store) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @HM@ hm = p.getHudManager();
    if (hm == null) return;
    @HUD@ h = hm.getCustomHud(KEY);
    if (h == null || !CLS.equals(h.getClass().getName())) { s.hud = null; return; }
    String t = target(s.uuid);
    if (t == null) {
      if (s.anc != null) { send(h, HOME); s.anc = null; }
      s.hud = h;
      return;
    }
    if (h == s.hud && t.equals(s.anc)) return;
    send(h, t);
    s.hud = h;
    s.anc = t;
  } catch (Throwable t) { err("moving the Dynamic Seasons widget", t); }
}""")
MMF(dscheck, "public @PKG@.DsState s;")
dscheck.addInterface(pool.get("java.lang.Runnable"))
MMC(dscheck, "public DsCheck(@PKG@.DsState s) { this.s = s; }")
MMM(dscheck, "public void run() { @PKG@.DsLink.checkNow(this.s); }")
MMM(dslink, r"""
public static void schedule(@PKG@.DsState s) {
  if (s == null || s.queued) return;
  @WLD@ w = s.world;
  if (w == null) return;
  s.queued = true;
  try { w.execute(new @PKG@.DsCheck(s)); QUEUED.incrementAndGet(); }
  catch (Throwable t) { s.queued = false; err("reaching the world thread", t); }
}""")
# the 1 s HUD tick (scheduler thread): nothing at all without Dynamic Seasons; a player at their spot costs one map read
MMM(dslink, r"""
public static void tick() {
  if (DS != 1 || ST.isEmpty()) return;
  java.util.Iterator it = ST.values().iterator();
  while (it.hasNext()) {
    @PKG@.DsState s = (@PKG@.DsState) it.next();
    try {
      if (s.pr == null || !s.pr.isValid()) { it.remove(); continue; }
      if (needed(s)) schedule(s);
    } catch (Throwable t) { err("the seasons tick", t); }
  }
}""")
# the attach (AttachTask, ON the player's world thread, after every PlayerReady): this world + store, forget the last object, check now.
# A new connection (another PlayerRef) starts clean - its client has their widget at their spot
MMM(dslink, r"""
public static void ready(@PR@ pr, @ST@ st) {
  if (pr == null || st == null) return;
  if (!present()) return;
  @WLD@ w = null;
  try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
  if (w == null) return;
  java.util.UUID u = pr.getUuid();
  @PKG@.DsState s = (@PKG@.DsState) ST.get(u);
  if (s == null || s.pr != pr) { s = new @PKG@.DsState(pr); ST.put(u, s); }
  s.store = st;
  s.world = w;
  s.hud = null;
  checkNow(s);
}""")
# a layout change (SkyyHudPlugin.rebuildFor): check at once on the world thread
MMM(dslink, r"""
public static void relayout(java.util.UUID u) {
  if (u == null || DS != 1) return;
  schedule((@PKG@.DsState) ST.get(u));
}""")
MMM(dslink, r"""
public static String statusText() {
  if (DS == 1) return "Dynamic Seasons " + DSV + " found - you can move its widget.";
  if (DS == 2) return DSV.length() > 0 ? "Dynamic Seasons " + DSV + " is not a 6.x version - its widget is left alone." : "Dynamic Seasons is not installed - nothing to move.";
  return "Not checked yet (checked when a player joins).";
}""")
# the editor pages list Seasons only while Dynamic Seasons is here (the saved line is kept either way)
MMM(wid, r"""
public static String[] edIds() {
  if (@PKG@.DsLink.present()) return IDS;
  int n = 0;
  for (int i = 0; i < IDS.length; i++) if (!"Seasons".equals(IDS[i])) n++;
  String[] o = new String[n];
  int k = 0;
  for (int i = 0; i < IDS.length; i++) if (!"Seasons".equals(IDS[i])) { o[k] = IDS[i]; k++; }
  return o;
}""")

# ---------------------------------------------------------------- DsUi: the settings page (kit markup made by tools/hud_0_3_15_patch.py)
DSUI_JAVA = @@DSUI_JAVA@@
MMM(dsui, r"""
public static void settings(@UCB@ b, @UEB@ ev, @PR@ pr) {
  @PKG@.WLayout l = (@PKG@.WLayout) @PKG@.LayoutStore.get(pr.getUuid()).get("Seasons");
  if (l == null) return;
  boolean en = l.en;
  String anc = l.anchor == null ? "" : l.anchor;
  boolean home = "br".equals(anc) && l.dx == @@RIGHT@@ && l.dy == @@BOT@@;
  String dsText = @PKG@.DsLink.statusText();
""" + DSUI_JAVA + r"""
}""")
# a click: 0 = nothing, 1 = back, 2 = changed (saved; the caller re-sends and rebuilds the page)
MMM(dsui, r"""
public static int click(@PR@ pr, String data) {
  if (data == null) return 0;
  int p = data.indexOf("\"ds:");
  if (p < 0) return 0;
  int q = data.indexOf('"', p + 4);
  if (q < 0) return 0;
  String a = data.substring(p + 4, q);
  if (a.equals("back")) return 1;
  java.util.UUID u = pr.getUuid();
  @PKG@.WLayout l = (@PKG@.WLayout) @PKG@.LayoutStore.get(u).get("Seasons");
  if (l == null) return 0;
  if (a.equals("en:1")) l.en = true;
  else if (a.equals("en:0")) l.en = false;
  else if (a.equals("home")) { l.anchor = "br"; l.dx = @@RIGHT@@; l.dy = @@BOT@@; }
  else if (a.equals("reset")) { l.en = true; l.anchor = "br"; l.dx = @@RIGHT@@; l.dy = @@BOT@@; l.scale = 100; }
  else if (a.startsWith("an:")) { String an = a.substring(3); if (!@PKG@.WLayout.validAnchor(an)) return 0; @PKG@.Widgets.snapTo(l, an); }
  else return 0;
  @PKG@.Widgets.clampToScreen(l);
  @PKG@.LayoutStore.save(u);
  return 2;
}""")
'''
DS_BLOCK = DS_BLOCK.replace("@@DSUI_JAVA@@", repr(DSUI_JAVA))
DS_BLOCK = DS_BLOCK.replace("@@RIGHT@@", str(DS_RIGHT)).replace("@@BOT@@", str(DS_BOTTOM))
assert "@@" not in DS_BLOCK
rep('''# ================= HudMain =================
''', DS_BLOCK + '''
# ================= HudMain =================
''')

# ---- skyyhud_main never draws Seasons (Dynamic Seasons does)
rep('''    if ("Minimap".equals(ids[i])) continue;''', '''    if ("Minimap".equals(ids[i]) || "Seasons".equals(ids[i])) continue;''')
# ---- plugin: the mover follows layout changes
rep('''  {PKG}.Minimap.relayout(u);
}}''', '''  {PKG}.Minimap.relayout(u);
  {PKG}.DsLink.relayout(u);
}}''')
# ---- editor + widgets page: Seasons only while Dynamic Seasons is here
rep('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.IDS;
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10,''',
    '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.edIds();
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10,''')
rep('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.IDS;
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 17,''',
    '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.edIds();
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 17,''')
rep(r'''    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.IDS;
    if (data.indexOf("\\"drop\\"") >= 0 || data.indexOf("Dropped") >= 0) {{''',
    r'''    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.edIds();
    if (data.indexOf("\\"drop\\"") >= 0 || data.indexOf("Dropped") >= 0) {{''')
rep('''    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.IDS;
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());''',
    '''    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.edIds();
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());''')
# ---- editor: a fixed box is its own size (no Size- / Size+ buttons)
rep('''      this.ww.put(ids[i], Integer.valueOf("Minimap".equals(ids[i]) ? l.bw * l.scale / 100 : {PKG}.Widgets.lineW(l, text, l.scale, 6)));''',
    '''      this.ww.put(ids[i], Integer.valueOf(("Minimap".equals(ids[i]) || l.fixed) ? l.bw * l.scale / 100 : {PKG}.Widgets.lineW(l, text, l.scale, 6)));''')
rep('''    int[] widths = new int[] {{ 40, 40, 40, 40, 90, 60, 60, 70, 90 }};
    for (int a = 0; a < acts.length; a++) {{
''', '''    int[] widths = new int[] {{ 40, 40, 40, 40, 90, 60, 60, 70, 90 }};
    {PKG}.WLayout fxl = ({PKG}.WLayout) m.get(this.sel);
    boolean fx = fxl != null && fxl.fixed;
    for (int a = 0; a < acts.length; a++) {{
      if (fx && (a == 5 || a == 6)) continue;
''')
# ---- the widget's Settings page = the Seasons page (only while Dynamic Seasons is here)
rep('''  if ("Minimap".equals(this.wid)) {{ {PKG}.MmUi.settings(b, ev, this.playerRef); return; }}''',
    '''  if ("Minimap".equals(this.wid)) {{ {PKG}.MmUi.settings(b, ev, this.playerRef); return; }}
  if ("Seasons".equals(this.wid)) {{ if ({PKG}.DsLink.present()) {PKG}.DsUi.settings(b, ev, this.playerRef); return; }}''')
rep('''    java.util.UUID u = this.playerRef.getUuid();
    if ("Minimap".equals(this.wid)) {{
      int mr = {PKG}.MmUi.click(this.playerRef, data);''', '''    java.util.UUID u = this.playerRef.getUuid();
    if ("Seasons".equals(this.wid)) {{
      int dr = {PKG}.DsUi.click(this.playerRef, data);
      if (dr == 1) {{
        {PLA} dp = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
        if (dp != null) dp.getPageManager().openCustomPage(ref, st, new {PKG}.WidgetsPage(this.playerRef, this.plugin));
        return;
      }}
      if (dr == 2) {{ plugin.rebuildFor(u); rebuild(); }}
      return;
    }}
    if ("Minimap".equals(this.wid)) {{
      int mr = {PKG}.MmUi.click(this.playerRef, data);''')

# ---- the 1 s HUD tick + the attach (world thread) + the logger
rep('''  try { com.skyy.hud.Minimap.watchdog(); } catch (Throwable t) { }
}""", tick))''', '''  try { com.skyy.hud.Minimap.watchdog(); } catch (Throwable t) { }
  try { com.skyy.hud.DsLink.tick(); } catch (Throwable t) { }
}""", tick))''')
rep('''    {PKG}.Minimap.ready(pr, st);
  }} catch (Throwable t) {{ }}
}}""", att))''', '''    {PKG}.Minimap.ready(pr, st);
    {PKG}.DsLink.ready(pr, st);
  }} catch (Throwable t) {{ }}
}}""", att))''')
rep('''  {PKG}.Minimap.LOG = getLogger();
''', '''  {PKG}.Minimap.LOG = getLogger();
  {PKG}.DsLink.LOG = getLogger();
''')

# ---- the class list + the manifest text
rep('''       mmcfg, mmpng, mmasset, mmsess, mmhud, mmreq, mmmain, mmui, mmtick, mmthr, mmatt, mmdet, mmtap, mmcon, mmquit, cmm, cmmon, cmmoff)''',
    '''       mmcfg, mmpng, mmasset, mmsess, mmhud, mmreq, mmmain, mmui, mmtick, mmthr, mmatt, mmdet, mmtap, mmcon, mmquit, cmm, cmmon, cmmoff,
       dslink, dsstate, dscheck, dsui)''')
rep('''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 13 widgets incl. a round minimap (needs BetterMap; reads the map it streams, shrunk on its own thread),''',
    '''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 13 widgets (14 with Dynamic Seasons) incl. a round minimap (needs BetterMap; reads the map it streams, shrunk on its own thread), a Seasons entry that moves Dynamic Seasons' own widget when that mod is installed,''')

out = s.replace(LF, NL)
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(%d lines)" % out.count(LF))
