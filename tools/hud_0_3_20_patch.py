"""Derive SkyyHud/build_skyyhud_0.3.20.py from the generated 0.3.19 (the SET pin; 0.3.19 is left untouched; line endings preserved).
Run:  python tools/hud_0_3_20_patch.py   then   python SkyyHud/build_skyyhud_0.3.20.py   (never --deploy)
Harness: python SkyyHud/test_skyyhud_0.3.20.py [--dir <scratch>] [--keep]

0.3.20 = phase 1 of the CHAT OVERFLOW plan (Skyy 2026-10-12, docs/answered/ui.md: "watch for things i probably wont notice, and figure out
ways to reduce the chat overflow while still giving players the info they need. the chat has top move slow enough people can read it for
server use. (unless we set up a second notification system that uses our widgets or something.)"; the approved cloud mockups
research/cloud/ui-mockups-1013/ (Layout-Spec.md sections 1, 3, 4, 5; pictures b_feed + c_skillxp), reviewed 2026-10-13 in docs/log).
No other mod's messages change in this round: a later round switches each mod's chat lines to msgroute:fn:get.

  1. NOTIFICATION FEED widget (new id "Feed", APPENDED to Widgets.IDS; label "Notification Feed"): default ON at bl 8,488 (its bottom edge
     8 px above the estimated vanilla chat), a 280 x 140 box at 100 % = 4 card slots of 280 x 32 with a 4 px gap. The newest card sits next
     to the anchored edge (bottom-anchored: at the bottom, the stack grows upward; a top-anchored feed grows downward). Card = box
     #0b1524(0.72) + a 1 px gold hairline #E8A93B(0.30) + a 22 px kind chip at x 6 (blue / gold coins + drops / green heals / purple pet XP)
     + the text at x 36 (Bold 14 #d6e4ee, or the widget's picked colour; cut with "..." to fit) + the count right-aligned 10 px from the edge
     ("x9"). Life: shown 4 s (Server Setup), then 60 % at +0.3 s, 25 % at +0.7 s, gone at +1 s. The same key (kind + item id, or kind + text)
     within 3 s of the card's last change adds to its count, restarts its time and makes it the newest card ("Pumpkin x1 -> x4 -> x9"; the
     stack is ordered by the last change, so the oldest card leaves first); the count flashes gold with a bright hairline for 0.3 s. A 5th card pushes the oldest out at once. Everything is ONE fixed markup per slot (the full / 60 % / 25 %
     variants + the gold highlight overlay, all Visible: false) - a card coming, merging, fading or leaving is only .Text / .Visible (and
     .ItemId) sets, never a HUD re-send. Editable like every widget (drag, arrows, Size, Hide, Snap to, Background, text colour / bold /
     italic, export / import / profiles); Settings row "Item icons Show / Hide" (Hide = the DEFAULT: an ItemIcon inside a HUD is UNVERIFIED -
     the Abilities-icons rule; Show draws the item's own icon over the chip).
     Its own timer: FeedTick every 250 ms on SkyyHud's OWN thread (HudThreads.EXEC, 0.3.19 - never HytaleServer.SCHEDULED_EXECUTOR). It
     touches ONLY players with something pending or shown (Feed.ACTIVE); nobody active = it returns at once. At most ONE HUD update per
     player per 250 ms (all pushes in between are merged first).
     Players whose saved layout has no Feed line (everyone today) get the default spot - unless it touches a shown widget's box or the
     estimated chat (8, 600, 560 x 360) in THEIR layout (e.g. a saved Guild / Skills at the old left-side defaults): then the first free spot
     on the bl anchor (Widgets.feedPlace: x 8 or right of a box, y 488 or just above / under a box, left half, nearest to 8,488 first). Saved
     lines are never moved; the server default layout (hud.defaultLayout) wins when it places Feed.
  2. SKILL XP FLASH on the existing Skills widget: XP per skill is added up for 2 s (Server Setup), then the row flashes for 3 s: gold tint
     #E8A93B 30 % for 0.5 s, 14 % until 1.75 s, then none; a 2 px gold left edge while tinted; the gain "+79" (Bold green #39f493,
     "+1,240", "+12.4k", "+1.2M") right-aligned 6 px left of the level until 3 s. A new batch during a flash adds to the number and restarts
     the 3 s. A skill whose line is OFF joins as a temporary row (name in #b7cedd) at the bottom while it flashes (Skills Settings: "XP of
     hidden skills Show / Hide", Show = WLayout.opt true = the default; the Skills widget never used opt before). The tints / edge are hidden
     elements of every Skills row (.Visible sets); the gain label is part of the row (its text = the model, so the box grows to fit "+9,999"
     at once and shrinks 15 s after the flash - the 0.3.13 width rule); a temporary row = a shape change = the proven 0.3.8 re-send (at most
     once per 1.5 s). Left out (no data in the agreed API): the 2 px XP bar and "LEVEL UP" (chat keeps the level-up line).
     Also LEFT OUT this round (review 2, queued for the next feed round): the TWO-LINE card (280 x 44: a 12 px #7f93a6 sub-line + a 4 px
     collection-progress bar - feed:fn:push has no sub-line / fraction argument yet, so "collection" draws a one-line card) and the
     Layout-Spec section 6 small-screen rule (feed height = min(140, chat top - 8 - the lowest top-left box above it - 8); move the feed
     right of the chat when one card does not fit) - the feed is editable, so a player on 1366 x 768 drags / resizes it meanwhile.
     DELIBERATE EXCEPTION to the LOCKED 2026-10-03 "box as small as its text" HUD rule: feed cards are a FIXED 280 px wide (the approved
     mockup + the task: 280 x 32), so cards line up and do not jump in width while they merge / fade.
  3. BRIDGE API (skyy.bridge, java.util.function.Function, plain java.lang types; any thread; no world-thread work, no I/O, no lock - each
     call = argument checks + map reads + one lock-free queue offer):
       feed:fn:push    apply(Object[] { UUID|String player, String kind, String itemId or null, String text, Number count or null })
                       -> Boolean TRUE = queued for the feed; FALSE = not shown (bad arguments, no HUD for that player, their Feed widget
                       off, the feed switched off in Server Setup, 64 pushes already waiting) - send it to chat yourself.
                       TRUE means the player WILL see it: a card pushed out before any step drew it (more than 4 in one 250 ms step)
                       becomes a chat line instead (Feed.overflow -> flushOver, review fix 1); an item id the server has not loaded
                       is dropped to "no icon" (Feed.iconOk, review fix 3).
                       kind = [a-z]{1,16} (the msgroute kinds; coins / drop = gold chip, heal = green, petxp = purple, others blue);
                       text <= 48 chars (control characters removed); count > 0 shows "x<count>" (merges add up).
       xpflash:fn:push apply(Object[] { UUID|String player, String skill, Number amount }) -> Boolean (TRUE = queued; FALSE = bad
                       arguments, no HUD, their Skills widget off, 64 pushes waiting, or the skill would NOT be drawn: its line is off and
                       the player set "XP of hidden skills: Hide", or no room is left for a temporary row - review 2 fix, Feed.xpShows) ->
                       send the chat line yourself. skill = the skill's name as the Skills widget shows it ("Mining", "Divinity").
       msgroute:fn:get apply(Object[] { UUID|String player, String kind }) -> "chat" | "feed" | "off". "feed" for skillxp = the Skills
                       widget flash. The player's own choice (settings:fn:get) else the Server Setup default; "feed" becomes "chat" when
                       the player's Feed (skillxp: Skills) widget is off or the feed is switched off; "system" and unknown kinds = "chat".
                       A player with no HUD (offline / not attached yet) gets the Server Setup default at once, "feed" -> "chat" - memory
                       only, settings:fn:get is NOT asked (it would read the player's settings file from disk on the caller's thread;
                       review 2 fix).
  4. ROUTING SETTINGS: Server Setup -> Messages (tools/skyycfg.py; config.properties msg.<kind>=chat|feed|off; a missing key = its
     default) holds the server default of the 10 kinds of the Settings > Messages mockup (pickup Feed, drop Feed, skillxp Skill list,
     levelup Chat, coins Feed, collection Feed, rankup Chat, quest Feed, heal Feed, petxp Feed; "System and server" = always Chat, no row).
     Per player: two switches per kind through the EXISTING Boolean settings API (settings:fn:register, category "messages" - SkyyMenu 0.3.18
     shows unknown categories under General until its Messages tab exists): msg.<kind> (On / Off) and msg.<kind>.feed (On = feed / skill
     list, Off = chat). Their registered defaults follow the Server Setup row (re-registered on every change, settings:def:* kept in step),
     so a player who never chose follows the server. DECISION: the rows carry the permission node skyyhud.messages (ops have it through "*"),
     so ordinary players do not see 20 switches that change nothing until the sender mods use msgroute (the later round drops the node).
     Server Setup -> Feed: hud.feed.enabled, showSecs 4, mergeSecs 3, maxCards 4, xpBatchSecs 2, xpFlashSecs 3 (live).
  5. DEFAULT SPOTS (the 2026-10-13 review): Party tl 8,200, Guild tl 8,324, Skills tr 8,240, Abilities br 460,21 - only the BUILT-IN
     default moves (players with no saved line for them); saved layouts never move (LayoutStore.get reads saved lines as before).
  6. /skyyhud testfeed (admin: skyyhud.admin + setPermissionGroups(new String[0])): six sample cards routed through msgroute exactly like a
     sender mod would (feed / chat / off), two of them pushed out at once (the 4-card cap), Pumpkin x1 -> x4 -> x9 over 2 s, and Skill XP
     for your class skill (+79) and Mining (+40) that flashes on the Skills widget after the 2 s batch.
ROLLBACK: 0.3.20 -> 0.3.19 is safe: 0.3.19 ignores the Feed layout line / export part and the new config.properties keys; the bridge keys
and the settings rows disappear with the jar (SkyyMenu keeps a player's stored msg.* choices harmlessly).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.19.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.20.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.19"' in s and s.startswith('"""SkyyHud 0.3.19 - build script')
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


MSG_KINDS = [
    ("pickup", "R_PICKUP", "Item pickups", "feed", "Item pickups: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("drop", "R_DROP", "Double drops and perk procs", "feed", "Double drops, perk procs: feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("skillxp", "R_SKILLXP", "Skill XP", "feed", "Skill XP: flash on the skill list (off = chat)", "On = +79 flashes next to the skill on your HUD Skills widget. Off = a line in chat."),
    ("levelup", "R_LEVELUP", "Skill level-ups", "chat", "Skill level-ups: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("coins", "R_COINS", "Coins (interest, payments)", "feed", "Coins: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("collection", "R_COLL", "Collection progress", "feed", "Collection progress: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("rankup", "R_RANKUP", "Collection rank-ups", "chat", "Collection rank-ups: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("quest", "R_QUEST", "Quest progress", "feed", "Quest progress: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("heal", "R_HEAL", "Heals and buffs", "feed", "Heals and buffs: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
    ("petxp", "R_PETXP", "Pet and guild XP", "feed", "Pet and guild XP: in the feed (off = chat)", "On = a card in the feed above the chat. Off = a line in chat."),
]
MSG_KINDS_SRC = "MSG_KINDS = [" + chr(10) + "".join("    %r," % (k,) + chr(10) for k in MSG_KINDS) + "]" + chr(10)


# ---------------- docstring + version ----------------
rep('''"""SkyyHud 0.3.19 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.19.py            -> SkyyHud/SkyyHud-0.3.19.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.20 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.20.py            -> SkyyHud/SkyyHud-0.3.20.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.20 (generated by tools/hud_0_3_20_patch.py from 0.3.19): CHAT OVERFLOW phase 1 (Skyy 2026-10-12; research/cloud/ui-mockups-1013/
  Layout-Spec.md; details in tools/hud_0_3_20_patch.py): the NOTIFICATION FEED widget (id Feed, bl 8,488, 4 cards of 280 x 32, 4 s +
  1 s fade, repeats merged within 3 s, its own 250 ms timer on SkyyHud's thread); the SKILL XP FLASH on the Skills widget ("+79", batched
  2 s, temporary row for a hidden skill); the bridge API feed:fn:push / xpflash:fn:push / msgroute:fn:get; per-player Chat / Feed / Off
  switches (settings:fn:register) with the server defaults in Server Setup -> Messages; new built-in spots Party tl 8,200, Guild tl 8,324,
  Skills tr 8,240, Abilities br 460,21 (saved layouts never move); /skyyhud testfeed (admin).
''')
rep('VERSION = "0.3.19"\n', 'VERSION = "0.3.20"\n')

# ---------------- the new classes ----------------
after('''wtime = pool.makeClass(PKG + ".WTime")                    # 0.3.19: world time read on the world thread, cached per world''', '''
# 0.3.20 notification feed + Skill XP flash + message routing (tools/hud_0_3_20_patch.py)
fview = pool.makeClass(PKG + ".FeedView")                 # one published, never-changed render state of a player's feed + flashes
fstate = pool.makeClass(PKG + ".FeedState")               # one player: the lock-free push queue + the cards / batches (SkyyHud's thread only)
fcard = pool.makeClass(PKG + ".FeedCard")                 # one card
feed = pool.makeClass(PKG + ".Feed")                      # the statics: states, push / route / tick / test
fcfg = pool.makeClass(PKG + ".FeedCfg")                   # Server Setup -> Feed / Messages (tools/skyycfg.py) + the settings registration
fpush = pool.makeClass(PKG + ".FeedPushFn")               # bridge feed:fn:push
fxp = pool.makeClass(PKG + ".XpFlashFn")                  # bridge xpflash:fn:push
froute = pool.makeClass(PKG + ".MsgRouteFn")              # bridge msgroute:fn:get
ftick = pool.makeClass(PKG + ".FeedTick")                 # the 250 ms feed timer (SkyyHud's own thread)
ftest = pool.makeClass(PKG + ".FeedTestStep")             # /skyyhud testfeed's delayed merge pushes
ctf = pool.makeClass(PKG + ".HudTestFeedCmd", pool.get(APC))   # /skyyhud testfeed (admin)''')
rep('''       dslink, dsstate, dscheck, dsui, hthr, wtime)
for c in ALL:''', '''       dslink, dsstate, dscheck, dsui, hthr, wtime, fview, fstate, fcard, feed, fcfg, fpush, fxp, froute, ftick, ftest, ctf)
for c in ALL:''')

# ---------------- constants: the default moves, the Feed widget, the message kinds ----------------
after('''assert (ABL_TP, ABL_ROW, ABL_BAR, ABL_GAP, ABL_BP, ABL_ICON, ABL_IGAP) == (3, 20, 4, 2, 6, 18, 4), "Widgets.bodyH / innerW (not f-strings) spell these out"
''', '''# 0.3.20 the approved built-in spots (research/cloud/ui-mockups-1013/Layout-Spec.md section 1, review 2026-10-13): only the BUILT-IN default
# moves - a saved layout line is read as before (LayoutStore.get)
DEFAULTS["Party"] = (True, "tl", 8, 200)
DEFAULTS["Guild"] = (True, "tl", 8, 324)
DEFAULTS["Skills"] = (True, "tr", 8, 240)
DEFAULTS["Abilities"] = (True, "br", 460, 21)
# 0.3.20 NOTIFICATION FEED widget: APPENDED (old files / codes / profiles keep their meaning); 4 slots of 280 x 32, gap 4 = 280 x 140 at 100 %
IDS.append("Feed")
DEFAULTS["Feed"] = (True, "bl", 8, 488)
LABELS["Feed"] = "Notification Feed"
FEED_W, FEED_CH, FEED_GAP, FEED_SLOTS = 280, 32, 4, 4
SIZES["Feed"] = (FEED_W, FEED_SLOTS * FEED_CH + (FEED_SLOTS - 1) * FEED_GAP)
assert IDS[-4:] == ["Minimap", "Seasons", "Abilities", "Feed"] and SIZES["Feed"] == (280, 140) and FEED_SLOTS == 4
FEED_GOLD, FEED_NAME, FEED_BOX = "#E8A93B", "#d6e4ee", "#0b1524"
FEED_CHIPS = ["#7caacc", "#E8A93B", "#39f493", "#d2b8ff"]   # chip colours: 0 the rest, 1 coins / drops, 2 heals, 3 pet / guild XP
FEED_TEST_ICON = "Ingredient_Crystal_White"                  # the ItemIcon placeholder (Widgets.chipItem's id, a vanilla item)
FLASH_GREEN, TEMP_ROW = "#39f493", "#b7cedd"
assert SKL_ARR == 22 and len(SKILL_LINES) == 10, "Widgets.linePairs / skillsModelX spell the Skills model gains out as [22 + k], the temp count [32]"
# the message kinds of the Settings > Messages mockup (d_settings): (kind, FeedCfg field, Server Setup label, default, player switch label
# for the feed / skill list, its help). "System and server" is always Chat (no row).
''' + MSG_KINDS_SRC + '''MSG_SHOW_HELP = "Off = never shown. On = shown in the feed or in chat (the next switch)."
MSG_NODE = "skyyhud.messages"     # DECISION: the switches are shown to holders only (ops via "*") until the sender mods use msgroute
for _k, _f, _l, _d, _fl, _fh in MSG_KINDS:
    assert _d in ("chat", "feed", "off") and len(_l) <= 40 and len(_fl) <= 48 and len(_fh) <= 100 and len("msg.%s.feed" % _k) <= 48
assert len(MSG_SHOW_HELP) <= 100 and len(MSG_KINDS) == 10
''')

# ---------------- part A (before Widgets: Widgets.skillsModelX reads Feed.viewOf) ----------------
before('''# ================= Widgets =================
''', r'''# ================= 0.3.20 FEED part A: the render state + the read side (Widgets.skillsModelX, HudMain.feedFill read it) =================
# Java with @TOKEN@ placeholders (the minimap's pattern; FX / FXM / FXF / FXC are this round's own helpers - MMM is defined further down)
import re as _re20
_FXT = {"PKG": PKG, "UCB": UCB, "PR": PR, "MSG": MSG, "GX": str(SKL_ARR), "TX": str(SKL_ARR + len(SKILL_LINES)),
        "LN": str(len(SKILL_LINES)), "FNAME": FEED_NAME, "FBOX": FEED_BOX, "FGOLD": FEED_GOLD, "FICON": FEED_TEST_ICON,
        "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item"}


def FX(src):
    def _r(m_):
        k_ = m_.group(1)
        if k_ not in _FXT:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k_, src[:300]))
        return _FXT[k_]
    return _re20.sub(r"@([A-Z]{2,8})@", _r, src)


def FXM(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(FX(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, FX(src)[:3000]))


def FXF(cls, src):
    cls.addField(CtField.make(FX(src), cls))


def FXC(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(FX(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, FX(src)[:1500]))


# FeedView: what the HUD shows NOW, built by the feed thread (Feed.step) and published as a whole (FeedState.view is volatile); never
# changed after publication, so the HUD build (any thread) and feedFill read it without a lock. Slots: index 0 = the newest card.
# stage 1 = fully shown, 2 = 60 %, 3 = 25 %; hi = the 0.3 s merge highlight. Flashes: fn = skill name, fg = "+79", fst 1 = tint 30 %,
# 2 = tint 14 %, 3 = the gain text only.
for _f in ("public int n;", "public String[] name;", "public String[] cnt;", "public String[] icon;", "public int[] cls;", "public int[] stage;",
           "public boolean[] hi;", "public String[] fn;", "public String[] fg;", "public int[] fst;"):
    FXF(fview, _f)
FXC(fview, """
public FeedView(int slots, int flashes) {
  this.n = 0;
  this.name = new String[slots]; this.cnt = new String[slots]; this.icon = new String[slots];
  this.cls = new int[slots]; this.stage = new int[slots]; this.hi = new boolean[slots];
  this.fn = new String[flashes]; this.fg = new String[flashes]; this.fst = new int[flashes];
}""")
# FeedState: q / qn = the pushes (any thread: a lock-free queue + its counter, bounded by Feed.QMAX); cards / batch / flash = SkyyHud's
# thread only (Feed.step); view = the last published FeedView
for _f in ("public java.util.UUID uuid;",
           "public final java.util.concurrent.ConcurrentLinkedQueue q = new java.util.concurrent.ConcurrentLinkedQueue();",
           "public final java.util.concurrent.atomic.AtomicInteger qn = new java.util.concurrent.atomic.AtomicInteger();",
           "public final java.util.ArrayList cards = new java.util.ArrayList();",
           "public final java.util.LinkedHashMap batch = new java.util.LinkedHashMap();",
           "public final java.util.LinkedHashMap flash = new java.util.LinkedHashMap();",
           # FIX 1 (review): the chat lines of cards pushed out before they were ever drawn / XP batches past the cap (SkyyHud's thread only)
           "public final java.util.ArrayList over = new java.util.ArrayList();",
           "public volatile @PKG@.FeedView view;"):
    FXF(fstate, _f)
FXC(fstate, "public FeedState(java.util.UUID u) { this.uuid = u; this.view = null; }")
# FeedTestStep's fields (its constructor is made in part B)
ftest.addInterface(pool.get("java.lang.Runnable"))
FXF(ftest, "public @PR@ pr;")
FXF(ftest, "public int step;")
for _f in ("public String key;", "public String kind;", "public String icon;", "public String text;", "public long count;",
           "public boolean showCount;", "public long born;", "public long changed;", "public long hiUntil;", "public int cls;",
           "public boolean shown;"):
    FXF(fcard, _f)
FXC(fcard, """
public FeedCard(String key, String kind, String icon, String text, long count, boolean showCount, int cls, long now) {
  this.key = key; this.kind = kind; this.icon = icon; this.text = text; this.count = count; this.showCount = showCount;
  this.cls = cls; this.born = now; this.changed = now; this.hiUntil = 0L;
}""")
# Feed statics: STATES = every player with a feed state (removed when they leave: SkyyHudPlugin.tickAll -> forget); ACTIVE = the players
# the 250 ms timer looks at (something queued, shown or flashing) - nobody active = the timer returns at once
for _f in ("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap ACTIVE = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile @PKG@.SkyyHudPlugin PLUGIN;",
           "public static final int QMAX = 64;",
           "public static final java.util.concurrent.atomic.AtomicLong PUSHES = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong XPS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong DROPPED = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong TICKS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong ERRORS = new java.util.concurrent.atomic.AtomicLong();",
           # FIX 1: notices that could not be drawn and went to chat instead; FIX 3: item id -> Boolean "a loaded item" (bounded cache)
           "public static final java.util.concurrent.atomic.AtomicLong OVERFLOW = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.ConcurrentHashMap ICONS = new java.util.concurrent.ConcurrentHashMap();"):
    FXF(feed, _f)
FXM(feed, """
public static @PKG@.FeedView viewOf(java.util.UUID u) {
  if (u == null) return null;
  Object s = STATES.get(u);
  if (s == null) return null;
  return ((@PKG@.FeedState) s).view;
}""")
FXM(feed, """
public static void forget(java.util.UUID u) {
  if (u == null) return;
  STATES.remove(u);
  ACTIVE.remove(u);
}""")
# the gain text: "+79", "+1,240", "+12.4k", "+1.2M"
FXM(feed, """
public static String fmtGain(long g) {
  if (g < 0L) g = 0L;
  if (g < 1000L) return "+" + g;
  if (g < 10000L) return "+" + java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(g);
  if (g < 999950L) { long t = (g + 50L) / 100L; return "+" + (t / 10L) + "." + (t % 10L) + "k"; }
  long m = (g + 50000L) / 100000L;
  return "+" + (m / 10L) + "." + (m % 10L) + "M";
}""")
FXM(feed, """
public static int flashIdx(@PKG@.FeedView v, String name) {
  if (v == null || v.fn == null || name == null) return -1;
  String n = name.trim();
  for (int i = 0; i < v.fn.length; i++) if (v.fn[i] != null && v.fn[i].equalsIgnoreCase(n)) return i;
  return -1;
}""")
FXM(feed, """
public static int flashStage(@PKG@.FeedView v, String name) {
  int i = flashIdx(v, name);
  return i < 0 ? 0 : v.fst[i];
}""")

''')

# ---------------- Widgets: text, the Skills flash model, linePairs, innerW, skillsBody, the feed markup, viewW, feedPlace ----------------
rep('''    if ("Minimap".equals(id)) return {PKG}.MmCfg.BM == 2 ? "Needs BetterMap" : "Minimap";''',
    '''    if ("Minimap".equals(id)) return {PKG}.MmCfg.BM == 2 ? "Needs BetterMap" : "Minimap";
    if ("Feed".equals(id)) return "Notification Feed";          // 0.3.20: the editor / Settings stand-in of the feed box''')
before('''# model() is the MASK-LESS entry (Party / Guild pass their option here)''', r'''# 0.3.20 SKILL XP FLASH: the Skills model + the flashing skills (Feed.viewOf): a shown row whose skill flashes carries its gain at
# [@GX@ + k]; a flashing skill without a shown row joins as a temporary row at the bottom when hid (WLayout.opt, the Skills Settings row
# "XP of hidden skills", Show = the default) - [@TX@] = the number of temporary rows, the shape "K<n>+<t>". No flash = the 0.3.19 model
# exactly (same array, same shape). Bridge reads only (memory).
FXM(wid, """
public static String[] skillsModelX(java.util.UUID me, int mask, boolean hid) {
  String[] m = skillsModelU(me, mask);
  if (me == null) return m;
  @PKG@.FeedView v = @PKG@.Feed.viewOf(me);
  if (v == null || v.fn == null || v.fn.length == 0) return m;
  java.util.Map b = bridge();
  if (!skillsHave(b)) return m;
  String[] x = new String[@TX@ + 1];
  for (int i = 0; i < m.length && i < x.length; i++) x[i] = m[i];
  int n = 0;
  for (int k = 0; k < @LN@ && 3 + 2 * k < m.length; k++) { if (m[2 + 2 * k] == null) break; n = k + 1; }
  boolean[] used = new boolean[v.fn.length];
  for (int k = 0; k < n; k++) {
    int fi = @PKG@.Feed.flashIdx(v, x[2 + 2 * k]);
    if (fi >= 0) { x[@GX@ + k] = v.fg[fi]; used[fi] = true; }
  }
  int t = 0;
  if (hid) {
    String lv = bstr(b, "skill:" + me.toString());
    String[] parts = null;
    if (lv != null) parts = splitc(lv, ',');
    for (int i = 0; i < v.fn.length && n < @LN@; i++) {
      if (used[i] || v.fn[i] == null) continue;
      x[2 + 2 * n] = cut(v.fn[i], 16);
      x[3 + 2 * n] = skillVal(parts, v.fn[i]);
      x[@GX@ + n] = v.fg[i];
      n = n + 1;
      t = t + 1;
    }
  }
  if (n == 0) return m;
  x[@TX@] = String.valueOf(t);
  x[0] = "K" + n + (t > 0 ? "+" + t : "");
  x[1] = x[2] + " " + x[3];
  return x;
}""")
''')
rep('''  try {{ return skillsModelU(pr.getUuid(), l == null || l.lines <= 0 ? {PKG}.WLayout.LINES_DEF : l.lines); }} catch (Throwable t) {{ }}''',
    '''  try {{ return skillsModelX(pr.getUuid(), l == null || l.lines <= 0 ? {PKG}.WLayout.LINES_DEF : l.lines, l == null || l.opt); }} catch (Throwable t) {{ }}   // 0.3.20: + the XP flash''')
rep('''      a.add("N" + i); a.add(m[2 + 2 * i]);
      a.add("S" + i); a.add(m[3 + 2 * i] == null ? "" : m[3 + 2 * i]);
''', '''      a.add("N" + i); a.add(m[2 + 2 * i]);
      a.add("S" + i); a.add(m[3 + 2 * i] == null ? "" : m[3 + 2 * i]);
      a.add("X" + i); a.add(m.length > 22 + i && m[22 + i] != null ? m[22 + i] : "");     // 0.3.20: the XP flash gain ("" = none)
''')
rep('''      int lw = textW(m[2 + 2 * i], fs, bold);
      if (v != null && v.length() > 0) lw = lw + gap + textW(v, fs, bold);
''', '''      int lw = textW(m[2 + 2 * i], fs, bold);
      if (v != null && v.length() > 0) lw = lw + gap + textW(v, fs, bold);
      // 0.3.20: a row flashing Skill XP also holds its gain (room for "+9,999" at least) 6 px before the level
      if (m.length > {SKL_ARR} + i && m[{SKL_ARR} + i] != null && m[{SKL_ARR} + i].length() > 0) {{
        int gw = textW(m[{SKL_ARR} + i], fs, bold); int rw = textW("+9,999", fs, bold);
        lw = lw + (gw > rw ? gw : rw) + 6 * sc / 100;
      }}
''')
rep('''  int n = skillRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  for (int i = 0; i < n; i++) {{
    int y = tp + i * rh;
    sb.append(lineS(base + "N" + i, sp, y, w, rh, fs, l, col, gcol));
    sb.append(lineE(base + "S" + i, sp, y, w, rh, fs, l, col, gcol));
  }}''', '''  int n = skillRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  // 0.3.20 Skill XP flash (Layout-Spec.md section 4): per row two hidden tints (30 % / 14 %) and a 2 px gold left edge, shown by
  // HudMain.feedFill (.Visible); the green gain label ends 6 px left of the level; the last tmp rows are temporary rows of hidden skills
  int tmp = 0;
  if (m != null && m.length > {SKL_ARR + len(SKILL_LINES)}) {{ try {{ tmp = Integer.parseInt(m[{SKL_ARR + len(SKILL_LINES)}]); }} catch (Throwable x) {{ tmp = 0; }} }}
  int eg = 2 * sc / 100; if (eg < 1) eg = 1;
  int g6 = 6 * sc / 100;
  int dd = (fs * 3 + 12) / 24; if (dd < 1) dd = 1;
  for (int i = 0; i < n; i++) {{
    int y = tp + i * rh;
    sb.append("Group #").append(base).append("F").append(i).append("a {{ Anchor: (Left: 0, Top: ").append(y).append(", Width: ").append(w).append(", Height: ").append(rh).append("); Background: {FEED_GOLD}(0.30); Visible: false; }} ");
    sb.append("Group #").append(base).append("F").append(i).append("b {{ Anchor: (Left: 0, Top: ").append(y).append(", Width: ").append(w).append(", Height: ").append(rh).append("); Background: {FEED_GOLD}(0.14); Visible: false; }} ");
    sb.append("Group #").append(base).append("E").append(i).append(" {{ Anchor: (Left: 0, Top: ").append(y).append(", Width: ").append(eg).append(", Height: ").append(rh).append("); Background: {FEED_GOLD}(0.95); Visible: false; }} ");
    boolean tr = i >= n - tmp;
    String c = tr ? "{TEMP_ROW}" : col;
    String g = tr ? "{TEMP_ROW}(0.45)" : gcol;
    sb.append(lineS(base + "N" + i, sp, y, w, rh, fs, l, c, g));
    sb.append(lineE(base + "S" + i, sp, y, w, rh, fs, l, c, g));
    String lv = m[3 + 2 * i] == null ? "" : m[3 + 2 * i];
    int xr = w - sp - textW(lv, fs, l.bold) - g6; if (xr < 1) xr = 1;
    sb.append(lineSrc(base + "X" + i, 0, y, xr + dd, rh, fs, l, "{FLASH_GREEN}", "{FLASH_GREEN}(0.45)", "End"));
  }}''')
after('''wid.addField(CtField.make("public static final String[] AICONS = new String[] { %s };" % ", ".join('"%s"' % i for i in sorted(ABL_ICONS)), wid))
''', '''# 0.3.20 the feed's kind chips (55 %): 0 the rest, 1 coins / double drops (gold), 2 heals (green), 3 pet / guild XP (purple)
wid.addField(CtField.make("public static final String[] FCHIP = new String[] { %s };" % ", ".join('"%s(0.55)"' % c_ for c_ in FEED_CHIPS), wid))
# FIX 2 (review): the fade steps keep the chip + hairline, dimmed with the card (60 % = chip 0.33 / hairline 0.18, 25 % = 0.14 / 0.08)
wid.addField(CtField.make("public static final String[] FCHIPM = new String[] { %s };" % ", ".join('"%s(0.33)"' % c_ for c_ in FEED_CHIPS), wid))
wid.addField(CtField.make("public static final String[] FCHIPL = new String[] { %s };" % ", ".join('"%s(0.14)"' % c_ for c_ in FEED_CHIPS), wid))
''')
before('''wid.addMethod(CtNewMethod.make(f"""
public static void setLines(''', r'''# 0.3.20 THE FEED MARKUP (Layout-Spec.md section 3): the widget Group = the 280 x 140 box (no background of its own), 4 card slots, each
# FIXED: F (fully shown: box 0.72 + gold hairline + the 4 kind chips + the item icon when "Item icons Show" + text + count), M (60 %),
# L (25 %) and H (the merge highlight: bright hairline + the gold count) - all Visible: false; HudMain.feedFill only sets .Text /
# .Visible / .ItemId. The newest card (slot 0) sits at the anchored edge: bottom-anchored stacks grow upward, top-anchored downward.
FXM(wid, """
public static String feedHair(int w, int h, String c) {
  return "Group { Anchor: (Left: 0, Top: 0, Width: " + w + ", Height: 1); Background: " + c + "; } "
    + "Group { Anchor: (Left: 0, Top: " + (h - 1) + ", Width: " + w + ", Height: 1); Background: " + c + "; } "
    + "Group { Anchor: (Left: 0, Top: 0, Width: 1, Height: " + h + "); Background: " + c + "; } "
    + "Group { Anchor: (Left: " + (w - 1) + ", Top: 0, Width: 1, Height: " + h + "); Background: " + c + "; } ";
}""")
FXM(wid, """
public static String feedLabel(String id, int x, int w, int h, int fs, String style, String color, String align) {
  return "Label #" + id + " { Anchor: (Left: " + x + ", Top: 0, Width: " + w + ", Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + fs + ", " + style + ", TextColor: " + color + ", HorizontalAlignment: " + align + ", VerticalAlignment: Center); } ";
}""")
# the 4 kind chips of one card variant (v = "" for F, "M", "L"); chip 0 shown, the rest hidden (feedFill sets .Visible)
FXM(wid, """
public static String feedChips(String p, String v, String[] col, int cx, int cy, int ci) {
  StringBuilder sb = new StringBuilder();
  for (int c = 0; c < 4; c++) sb.append("Group #").append(p).append(v).append("K").append(c).append(" { Anchor: (Left: ").append(cx).append(", Top: ").append(cy).append(", Width: ").append(ci).append(", Height: ").append(ci).append("); Background: ").append(col[c]).append("; Visible: ").append(c == 0 ? "true" : "false").append("; } ");
  return sb.toString();
}""")
FXM(wid, """
public static String feedSrc(@PKG@.WLayout l, boolean icons) {
  int sc = l.scale;
  int cw = 280 * sc / 100; if (cw < 40) cw = 40;
  int ch = 32 * sc / 100; if (ch < 8) ch = 8;
  int gp = 4 * sc / 100;
  int hh = l.bh * sc / 100;
  int fs = 14 * sc / 100; if (fs < 6) fs = 6;
  int ci = 22 * sc / 100; if (ci < 4) ci = 4;
  int cx = 6 * sc / 100; int cy = (ch - ci) / 2;
  int nx = 36 * sc / 100; int rp = 10 * sc / 100;
  int nw = cw - nx - rp; if (nw < 1) nw = 1;
  int cwr = cw - rp; if (cwr < 1) cwr = 1;
  String a = l.anchor;
  boolean down = a.equals("tl") || a.equals("t") || a.equals("tr");
  String nc = "def".equals(l.col) ? "@FNAME@" : hexOf(l.col);
  String st = "RenderBold: " + (l.bold ? "true" : "false") + (l.ital ? ", RenderItalics: true" : "");
  StringBuilder sb = new StringBuilder();
  sb.append("Group #SkyyWFeed { Anchor: ").append(anchorSrcWH(l, cw, hh)).append("; ");
  for (int j = 0; j < 4; j++) {
    int top = down ? j * (ch + gp) : hh - ch - j * (ch + gp);
    if (top < 0) top = 0;
    String p = "SkyyWFeed" + j;
    String box = "Anchor: (Left: 0, Top: " + top + ", Width: " + cw + ", Height: " + ch + "); Visible: false; ";
    sb.append("Group #").append(p).append("F { ").append(box);
    if (l.bg) sb.append("Background: @FBOX@(0.72); ").append(feedHair(cw, ch, "@FGOLD@(0.30)"));
    sb.append(feedChips(p, "", FCHIP, cx, cy, ci));
    if (icons) sb.append("ItemIcon #").append(p).append("I { Anchor: (Left: ").append(cx).append(", Top: ").append(cy).append(", Width: ").append(ci).append(", Height: ").append(ci).append("); ItemId: \\"@FICON@\\"; Visible: false; } ");
    sb.append(feedLabel(p + "FN", nx, nw, ch, fs, st, nc, "Start"));
    sb.append(feedLabel(p + "FC", 0, cwr, ch, fs, st, "#ffffff", "End"));
    sb.append("} ");
    sb.append("Group #").append(p).append("M { ").append(box);
    if (l.bg) sb.append("Background: @FBOX@(0.43); ").append(feedHair(cw, ch, "@FGOLD@(0.18)"));
    sb.append(feedChips(p, "M", FCHIPM, cx, cy, ci));
    sb.append(feedLabel(p + "MN", nx, nw, ch, fs, st, nc + "(0.60)", "Start"));
    sb.append(feedLabel(p + "MC", 0, cwr, ch, fs, st, "#ffffff(0.60)", "End"));
    sb.append("} ");
    sb.append("Group #").append(p).append("L { ").append(box);
    if (l.bg) sb.append("Background: @FBOX@(0.18); ").append(feedHair(cw, ch, "@FGOLD@(0.08)"));
    sb.append(feedChips(p, "L", FCHIPL, cx, cy, ci));
    sb.append(feedLabel(p + "LN", nx, nw, ch, fs, st, nc + "(0.25)", "Start"));
    sb.append(feedLabel(p + "LC", 0, cwr, ch, fs, st, "#ffffff(0.25)", "End"));
    sb.append("} ");
    sb.append("Group #").append(p).append("H { ").append(box);
    if (l.bg) sb.append(feedHair(cw, ch, "@FGOLD@(0.85)"));
    sb.append(feedLabel(p + "HC", 0, cwr, ch, fs, st, "@FGOLD@", "End"));
    sb.append("} ");
  }
  sb.append("}");
  return sb.toString();
}""")
# a text cut with "..." to fit room px at fs (the kit font table, like every box width)
FXM(wid, """
public static String fitText(String s, int room, int fs, boolean bold) {
  if (s == null || room < 1) return "";
  if (textW(s, fs, bold) <= room) return s;
  String t = s;
  while (t.length() > 1 && textW(t + "...", fs, bold) > room) t = t.substring(0, t.length() - 1);
  return t.trim() + "...";
}""")
# the card text that fits beside its count (name at x 36, count 10 px from the right edge, 6 px between)
FXM(wid, """
public static String feedFit(String nm, String cn, int sc, boolean bold) {
  int fs = 14 * sc / 100; if (fs < 6) fs = 6;
  int room = 280 * sc / 100 - 36 * sc / 100 - 10 * sc / 100;
  if (cn != null && cn.length() > 0) room = room - textW(cn, fs, bold) - 6 * sc / 100;
  return fitText(nm, room, fs, bold);
}""")
''')
rep('''  if ("Minimap".equals(id) || l.fixed) return l.bw * l.scale / 100;''',
    '''  if ("Minimap".equals(id) || "Feed".equals(id) || l.fixed) return l.bw * l.scale / 100;   // 0.3.20: the feed box is fixed (280 x 140 at 100 %)''')
before('''
# ================= LayoutStore =================
''', r'''
# 0.3.20 Widgets.feedPlace: a player whose saved file has no Feed line (everyone before 0.3.20) and whose server default does not place it
# gets the built-in spot bl 8,488 - unless it comes within 4 px of a shown widget's maximum box or the estimated vanilla chat (8, 600,
# 560 x 360; Layout-Spec.md section 1, an ESTIMATE): then the first free spot on the bl anchor (x 8 or 6 px right of a box; y 488, 6 px
# above a box or 6 px under one; on screen, the left half), the one nearest 8,488 first. true = moved. Saved lines are never moved.
FXM(wid, """
public static boolean feedPlace(java.util.Map m) {
  @PKG@.WLayout w = (@PKG@.WLayout) m.get("Feed");
  if (w == null || !w.en) return false;
  @PKG@.WLayout d = def("Feed");
  if (!d.anchor.equals(w.anchor) || w.dx != d.dx || w.dy != d.dy || w.scale != d.scale) return false;
  try { java.util.HashMap dm = @PKG@.HudCfg.layoutMap(); if (dm != null && dm.get("Feed") != null) return false; } catch (Throwable t) { }
  int fw = w.bw * w.scale / 100;
  int fh = w.bh * w.scale / 100;
  int n = 0;
  int[] r = new int[4 * (IDS.length + 1)];
  for (int i = 0; i < IDS.length; i++) {
    if ("Feed".equals(IDS[i]) || "Seasons".equals(IDS[i])) continue;
    @PKG@.WLayout o = (@PKG@.WLayout) m.get(IDS[i]);
    if (o == null || !o.en) continue;
    int ow = o.bw * o.scale / 100;
    int oh = hMax(o);
    int[] p = screenPosWH(o, ow, oh);
    r[4 * n] = p[0]; r[4 * n + 1] = p[1]; r[4 * n + 2] = ow; r[4 * n + 3] = oh;
    n = n + 1;
  }
  r[4 * n] = 8; r[4 * n + 1] = 600; r[4 * n + 2] = 560; r[4 * n + 3] = 360;
  n = n + 1;
  if (!mmHit(r, n, w.dx, 1080 - fh - w.dy, fw, fh)) return false;
  int[] cx = new int[n + 1];
  cx[0] = 8;
  for (int i = 0; i < n; i++) cx[i + 1] = r[4 * i] + r[4 * i + 2] + 6;
  int[] cy = new int[2 * n + 1];
  cy[0] = d.dy;
  for (int i = 0; i < n; i++) { cy[2 * i + 1] = 1080 - r[4 * i + 1] + 6; cy[2 * i + 2] = 1080 - (r[4 * i + 1] + r[4 * i + 3] + 6) - fh; }
  int best = -1; int bdx = 0; int bdy = 0;
  for (int i = 0; i < cx.length; i++) {
    int dx = cx[i];
    if (dx < 8 || dx + fw > 960) continue;
    for (int j = 0; j < cy.length; j++) {
      int dy = cy[j];
      if (dy < 8 || 1080 - fh - dy < 8) continue;
      if (mmHit(r, n, dx, 1080 - fh - dy, fw, fh)) continue;
      int sc = Math.abs(dy - d.dy) + (dx - 8);
      if (best < 0 || sc < best || (sc == best && Math.abs(dy - d.dy) < Math.abs(bdy - d.dy))) { best = sc; bdx = dx; bdy = dy; }
    }
  }
  if (best < 0) return false;
  w.dx = bdx;
  w.dy = bdy;
  clampToScreen(w);
  return true;
}""")
''')
rep('''  boolean mmf = false;
''', '''  boolean mmf = false;
  boolean fdf = false;      // 0.3.20: the file has a Feed line
''')
rep('''        if (v != null && "Minimap".equals(ids[i])) mmf = true;
''', '''        if (v != null && "Minimap".equals(ids[i])) mmf = true;
        if (v != null && "Feed".equals(ids[i])) fdf = true;
''')
before('''  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);
  return prev != null ? prev : m;''', '''  // 0.3.20: a feed the player never placed takes the first free spot when the built-in one touches their widgets (a COPY, as the minimap)
  if (!fdf) {{
    try {{
      {PKG}.WLayout fw = ({PKG}.WLayout) m.get("Feed");
      if (fw != null) {{
        {PKG}.WLayout fc = {PKG}.WLayout.parse(fw.ser(), fw);
        if (fc != null && fc != fw) {{ m.put("Feed", fc); if (!{PKG}.Widgets.feedPlace(m)) m.put("Feed", fw); }}
      }}
    }} catch (Throwable t) {{ }}
  }}
''')

# ---------------- FeedCfg (before the config rows: emit reads the bound fields) ----------------
_cfg_route = "\n".join('  if (k.equals("%s")) return norm(%s, "%s");' % (k_, f_, d_) for k_, f_, l_, d_, fl_, fh_ in MSG_KINDS)
_cfg_load = "\n".join('  %s = choice(p.getProperty("msg.%s"), "%s");' % (f_, k_, d_) for k_, f_, l_, d_, fl_, fh_ in MSG_KINDS)
_cfg_fields = "\n".join('    "public static volatile String %s = \\"%s\\";",' % (f_, d_) for k_, f_, l_, d_, fl_, fh_ in MSG_KINDS)
before('''# the admin config registry (research/Server-Setup-Spec.md 4.8): Server Setup -> HUD
HUD_CFG_CATS = ''', r'''# ================= 0.3.20 FeedCfg: Server Setup -> Feed / Messages (tools/skyycfg.py binds these fields) + the per-player switches =========
for _f in ("public static volatile boolean ENABLED = true;", "public static volatile double SHOW_SECS = 4.0;",
           "public static volatile double MERGE_SECS = 3.0;", "public static volatile int MAX_CARDS = 4;",
           "public static volatile double XP_BATCH_SECS = 2.0;", "public static volatile double XP_FLASH_SECS = 3.0;",
''' + _cfg_fields + r'''
           "public static final String NODE = \"%s\";" % MSG_NODE,
           "public static final String SHELP = \"%s\";" % MSG_SHOW_HELP,
           "public static final String[] KINDS = %s;" % jarr([k_[0] for k_ in MSG_KINDS]),
           "public static final String[] SLABEL = %s;" % jarr([k_[2] for k_ in MSG_KINDS]),
           "public static final String[] FLABEL = %s;" % jarr([k_[4] for k_ in MSG_KINDS]),
           "public static final String[] FHELP = %s;" % jarr([k_[5] for k_ in MSG_KINDS])):
    FXF(fcfg, _f)
FXM(fcfg, """
public static String norm(String v, String d) {
  if ("chat".equals(v) || "feed".equals(v) || "off".equals(v)) return v;
  return d;
}""")
# the server default of a message kind ("chat" / "feed" / "off"); null = no such kind (system, unknown: always chat)
FXM(fcfg, """
public static String route(String k) {
  if (k == null) return null;
''' + _cfg_route + r'''
  return null;
}""")
FXM(fcfg, """
public static boolean bool(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("true") || t.equals("1") || t.equals("yes") || t.equals("on")) return true;
  if (t.equals("false") || t.equals("0") || t.equals("no") || t.equals("off")) return false;
  return d;
}""")
FXM(fcfg, """
public static double dec(String v, double d, double lo, double hi) {
  if (v == null) return d;
  double x = d;
  try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { return d; }
  if (Double.isNaN(x) || Double.isInfinite(x)) return d;
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
FXM(fcfg, """
public static String choice(String v, String d) {
  if (v == null) return d;
  return norm(v.trim().toLowerCase(java.util.Locale.ROOT), d);
}""")
# HudCfg.load (setup, the kit's reload of a hand-edited file goes through the field: rows) - a missing key = its default
FXM(fcfg, """
public static void loadFrom(java.util.Properties p) {
  ENABLED = bool(p.getProperty("feed.enabled"), true);
  SHOW_SECS = dec(p.getProperty("feed.showSecs"), 4.0, 1.0, 15.0);
  MERGE_SECS = dec(p.getProperty("feed.mergeSecs"), 3.0, 0.0, 10.0);
  MAX_CARDS = (int) dec(p.getProperty("feed.maxCards"), 4.0, 1.0, 4.0);
  XP_BATCH_SECS = dec(p.getProperty("feed.xpBatchSecs"), 2.0, 0.5, 10.0);
  XP_FLASH_SECS = dec(p.getProperty("feed.xpFlashSecs"), 3.0, 1.0, 10.0);
''' + _cfg_load + r'''
}""")
# the CREATING bridge (SkyyMenu's MenuUtil.bridge pattern)
FXM(fcfg, """
public static java.util.Map bridgeC() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# the two switches of kind i through the existing settings API (research/Settings-Spec.md 1.2; SkyyMenu 0.3.3+): msg.<kind> (shown or
# not) and msg.<kind>.feed (feed / skill list or chat). Their registered DEFAULTS follow the Server Setup row (a player who never chose
# follows the server); settings:def:* is written first (load order never matters) and kept in step; the 7th element = the node (NODE)
FXM(fcfg, """
public static void register(int i) {
  try {
    String k = KINDS[i];
    String d = route(k);
    java.util.Map br = bridgeC();
    Object[] a = new Object[] { "SkyyHud", "msg." + k, SLABEL[i], "messages", Boolean.valueOf(!"off".equals(d)), SHELP, NODE };
    Object[] f = new Object[] { "SkyyHud", "msg." + k + ".feed", FLABEL[i], "messages", Boolean.valueOf("feed".equals(d)), FHELP[i], NODE };
    br.put("settings:def:msg." + k, a);
    br.put("settings:def:msg." + k + ".feed", f);
    Object fn = br.get("settings:fn:register");
    if (fn instanceof java.util.function.Function) {
      ((java.util.function.Function) fn).apply(a);
      ((java.util.function.Function) fn).apply(f);
    }
  } catch (Throwable t) { }
}""")
FXM(fcfg, """
public static void registerAll() {
  for (int i = 0; i < KINDS.length; i++) register(i);
}""")
# the kit's after= hook of every hud.msg.* row: the players' defaults follow the new server default at once
FXM(fcfg, """
public static void routeChanged(String key) {
  registerAll();
}""")

''')
rep('''HUD_CFG_CATS = [("hud", "HUD"), ("mm", "Minimap")]''', '''HUD_CFG_CATS = [("hud", "HUD"), ("mm", "Minimap"), ("feed", "Feed"), ("msg", "Messages")]   # 0.3.20: + Feed, Messages''')
rep('''     "field:MmCfg.ARROW_BLOCKS@config.properties:mm.arrowBlocks;after=Minimap.cfgChanged"),
]''', '''     "field:MmCfg.ARROW_BLOCKS@config.properties:mm.arrowBlocks;after=Minimap.cfgChanged"),
    # 0.3.20 the notification feed + Skill XP flash (live: read at every 250 ms step)
    ("hud.feed.enabled", "Notification feed", "feed", "bool", "true", "", "", "", "", "live",
     "Off = no feed cards for anyone; messages meant for the feed go to chat instead.",
     "field:FeedCfg.ENABLED@config.properties:feed.enabled"),
    ("hud.feed.showSecs", "Card time", "feed", "dec", "4", "1", "15", "", "s", "live",
     "How long a card stays fully shown; then it fades out over 1 s.",
     "field:FeedCfg.SHOW_SECS@config.properties:feed.showSecs"),
    ("hud.feed.mergeSecs", "Merge window", "feed", "dec", "3", "0", "10", "", "s", "live",
     "The same item again within this time adds to its card (Pumpkin x9). 0 = never merge.",
     "field:FeedCfg.MERGE_SECS@config.properties:feed.mergeSecs"),
    ("hud.feed.maxCards", "Most cards at once", "feed", "int", "4", "1", "4", "", "", "live",
     "A new card pushes the oldest one out when the feed is full.",
     "field:FeedCfg.MAX_CARDS@config.properties:feed.maxCards"),
    ("hud.feed.xpBatchSecs", "Skill XP added up for", "feed", "dec", "2", "0.5", "10", "", "s", "live",
     "Skill XP is added up this long, then flashes as one number (+79) on the Skills widget.",
     "field:FeedCfg.XP_BATCH_SECS@config.properties:feed.xpBatchSecs"),
    ("hud.feed.xpFlashSecs", "Skill XP flash time", "feed", "dec", "3", "1", "10", "", "s", "live",
     "How long the +79 and the gold tint stay on the skill's row.",
     "field:FeedCfg.XP_FLASH_SECS@config.properties:feed.xpFlashSecs"),
] + [("hud.msg." + _k, _l, "msg", "choice", _d, "", "", "chat|Chat,feed|%s,off|Off" % ("Skill list" if _k == "skillxp" else "Feed"), "", "live",
      "Where it goes for players who never chose. Players change their own in /settings.",
      "field:FeedCfg.%s@config.properties:msg.%s;after=FeedCfg.routeChanged" % (_f, _k)) for _k, _f, _l, _d, _fl, _fh in MSG_KINDS]''')
rep('''    "mm.arrowBlocks=16",
    "",
])''', '''    "mm.arrowBlocks=16",
    "",
    "# Notification feed (bottom left, above the chat) + the Skill XP flash on the Skills widget. Change these in game: SkyWynn Menu ->",
    "# Server Setup -> Feed / Messages. feed.enabled = the feed for everyone; feed.showSecs = seconds a card stays fully shown (then it",
    "# fades out over 1 s); feed.mergeSecs = the same item again within this many seconds adds to its card (0 = never); feed.maxCards =",
    "# cards at once (1-4); feed.xpBatchSecs = Skill XP is added up this long, then flashes; feed.xpFlashSecs = how long the flash shows.",
    "feed.enabled=true",
    "feed.showSecs=4",
    "feed.mergeSecs=3",
    "feed.maxCards=4",
    "feed.xpBatchSecs=2",
    "feed.xpFlashSecs=3",
    "# msg.<type> = where each message type goes for players who never chose: chat, feed or off (skillxp: feed = the skill list flash).",
    "# Players change their own in /settings. Other mods ask SkyyHud (bridge msgroute:fn:get) before they send.",
] + ["msg.%s=%s" % (_k, _d) for _k, _f, _l, _d, _fl, _fh in MSG_KINDS] + [
    "",
])''')
rep('''      com.skyy.hud.MmCfg.loadFrom(p);
''', '''      com.skyy.hud.MmCfg.loadFrom(p);
      com.skyy.hud.FeedCfg.loadFrom(p);      // 0.3.20: Server Setup -> Feed / Messages (a missing key = its default)
''')

# ---------------- HudMain: fields, feedFill (before build), the build branch, feedTick ----------------
after('''hudc.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap narrow = new java.util.concurrent.ConcurrentHashMap();", hudc))
''', '''# 0.3.20: the feed built into this document (its scale / item icons / bold), and "a Skill XP flash was seen at the last feedFill"
for _f in ("public boolean feedOn;", "public int feedSc;", "public boolean feedIcons;", "public boolean feedBold;", "public boolean flashSeen;"):
    hudc.addField(CtField.make(_f, hudc))
''')
before('''hudc.addMethod(CtNewMethod.make(f"""
protected void build({UCB} b) {{''', r'''# 0.3.20 feedFill: the feed cards + the Skill XP flash of THIS document as .Text / .Visible / .ItemId sets, only what changed since the
# last send (this.last; full = everything after a build). Called by build (full) and feedTick (the 250 ms feed timer, SkyyHud's thread),
# both under the HudMain monitor. true = the Skills widget needs the shape re-send (a temporary row comes / goes, or a gain needs a wider
# box) - the caller does the 0.3.8 re-send (at most once per 1.5 s).
FXM(hudc, """
public boolean feedFill(@UCB@ b, boolean full) {
  boolean re = false;
  @PKG@.FeedView v = @PKG@.Feed.viewOf(this.uuid);
  if (this.feedOn) {
    for (int j = 0; j < 4; j++) {
      int st = 0; boolean hi = false; String nm = ""; String cn = ""; int cls = 0; String ic = "";
      if (v != null && j < v.n) {
        st = v.stage[j];
        hi = v.hi[j];
        nm = v.name[j] == null ? "" : v.name[j];
        cn = v.cnt[j] == null ? "" : v.cnt[j];
        cls = v.cls[j];
        ic = v.icon[j] == null ? "" : v.icon[j];
      }
      String p = "#SkyyWFeed" + j;
      String k = "Feed:" + j;
      if (st > 0) {
        String fit = @PKG@.Widgets.feedFit(nm, cn, this.feedSc, this.feedBold);
        if (full || !fit.equals(this.last.get(k + ":n"))) { this.last.put(k + ":n", fit); b.set(p + "FN.Text", fit); b.set(p + "MN.Text", fit); b.set(p + "LN.Text", fit); }
        String fc = hi ? "" : cn;
        if (full || !fc.equals(this.last.get(k + ":cf"))) { this.last.put(k + ":cf", fc); b.set(p + "FC.Text", fc); }
        if (full || !cn.equals(this.last.get(k + ":c"))) { this.last.put(k + ":c", cn); b.set(p + "MC.Text", cn); b.set(p + "LC.Text", cn); b.set(p + "HC.Text", cn); }
        String ks = String.valueOf(cls);
        if (full || !ks.equals(this.last.get(k + ":k"))) {
          this.last.put(k + ":k", ks);
          for (int c = 0; c < 4; c++) { b.set(p + "K" + c + ".Visible", c == cls); b.set(p + "MK" + c + ".Visible", c == cls); b.set(p + "LK" + c + ".Visible", c == cls); }
        }
        if (this.feedIcons && (full || !ic.equals(this.last.get(k + ":i")))) {
          this.last.put(k + ":i", ic);
          if (ic.length() > 0) b.set(p + "I.ItemId", ic);
          b.set(p + "I.Visible", ic.length() > 0);
        }
      }
      String vs = String.valueOf(st) + (st == 1 && hi ? "h" : "");
      if (full && st == 0) this.last.put(k + ":v", vs);
      else if (full || !vs.equals(this.last.get(k + ":v"))) {
        this.last.put(k + ":v", vs);
        b.set(p + "F.Visible", st == 1);
        b.set(p + "M.Visible", st == 2);
        b.set(p + "L.Visible", st == 3);
        b.set(p + "H.Visible", st == 1 && hi);
      }
    }
  }
  Object sh = this.shape.get("Skills");
  Object sg = this.built.get("Skills");
  if (sh != null && sg != null) {
    String[] m = (String[]) this.models.get("Skills");
    int gn = ((Integer) sg).intValue();
    boolean any = v != null && v.fn != null && v.fn.length > 0;
    boolean fresh = false;
    if (!full && (any || this.flashSeen)) {
      try {
        @PR@ pr = getPlayerRef();
        @PKG@.WLayout sl = (@PKG@.WLayout) @PKG@.LayoutStore.get(this.uuid).get("Skills");
        String[] nm2 = @PKG@.Widgets.modelL("Skills", pr, sl);
        if (!sh.equals(nm2[0])) re = true;
        else {
          Object wo = this.wb.get("Skills");
          if (wo != null && sl != null && @PKG@.Widgets.multiW("Skills", sl, nm2, sl.scale, 6) > ((Integer) wo).intValue()) re = true;
          m = nm2;
          fresh = true;
        }
      } catch (Throwable t) { }
    }
    this.flashSeen = any;
    if (m != null) {
      for (int k = 0; k < @LN@ && 3 + 2 * k < m.length; k++) {
        if (m[2 + 2 * k] == null) break;
        int fs = @PKG@.Feed.flashStage(v, m[2 + 2 * k]);
        String sv = String.valueOf(fs);
        String fk = "Skills:F" + k;
        boolean send = full ? fs != 0 : !sv.equals(this.last.get(fk));
        this.last.put(fk, sv);
        if (send) {
          b.set("#SkyyWSkillsF" + k + "a.Visible", fs == 1);
          b.set("#SkyyWSkillsF" + k + "b.Visible", fs == 2);
          b.set("#SkyyWSkillsE" + k + ".Visible", fs == 1 || fs == 2);
        }
      }
      if (fresh) {
        String[] pairs = @PKG@.Widgets.linePairs("Skills", m);
        for (int q = 0; q + 1 < pairs.length; q += 2) {
          String key = "Skills:" + pairs[q];
          String lt = pairs[q + 1];
          if (!lt.equals(this.last.get(key))) { this.last.put(key, lt); @PKG@.Widgets.setText(b, "#SkyyWSkills" + pairs[q], gn, lt); }
        }
      }
    }
  }
  return re;
}""")
''')
rep('''  this.narrow.clear();
  {PR} pr = getPlayerRef();''', '''  this.narrow.clear();
  this.feedOn = false;          // 0.3.20
  {PR} pr = getPlayerRef();''')
rep('''    if ("Minimap".equals(ids[i]) || "Seasons".equals(ids[i])) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{''', '''    if ("Feed".equals(ids[i])) {{
      // 0.3.20 the notification feed: 4 fixed card slots; every card change = .Text / .Visible / .ItemId sets (feedFill), never a re-send
      this.feedOn = true;
      this.feedSc = l.scale;
      this.feedIcons = !l.opt;          // opt true (the default) = Item icons Hide
      this.feedBold = l.bold;
      b.appendInline("#SkyyHudRoot", {PKG}.Widgets.feedSrc(l, !l.opt));
      continue;
    }}
    if ("Minimap".equals(ids[i]) || "Seasons".equals(ids[i])) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{''')
rep('''  this.last.clear();
  fill(b, true);
}}""", hudc))''', '''  this.last.clear();
  fill(b, true);
  feedFill(b, true);            // 0.3.20: the feed cards + Skill XP flash as they are right now
}}""", hudc))''')
after('''public synchronized void showNow() {
  show();
}""", hudc))
''', r'''# 0.3.20: one step of the feed timer for this player (SkyyHud's thread): the changed sets in ONE update, or the Skills shape re-send
FXM(hudc, """
public synchronized void feedTick(long now) {
  try {
    @UCB@ b = new @UCB@();
    boolean re = feedFill(b, false);
    if (re && now - this.lastRe >= 1500L) { this.lastRe = now; show(); return; }
    if (b.getCommands().length > 0) update(false, b);
  } catch (Throwable t) { }
}""")
''')

# ---------------- Plugin: the feed timer field, forget on leave ----------------
after('''pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
''', '''pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture feedTicker;", pl))     # 0.3.20: the 250 ms feed timer
''')
rep('''    if (pr == null || !pr.isValid()) {{ it.remove(); {PKG}.LayoutStore.CACHE.remove(e.getKey()); {PKG}.EditorPage.STEPS.remove(e.getKey()); continue; }}''',
    '''    if (pr == null || !pr.isValid()) {{ it.remove(); {PKG}.LayoutStore.CACHE.remove(e.getKey()); {PKG}.EditorPage.STEPS.remove(e.getKey()); {PKG}.Feed.forget((java.util.UUID) e.getKey()); continue; }}''')

# ---------------- part B: push / route / step / tick / test, the bridge Functions, the timer, /skyyhud testfeed ----------------
before('''# ================= HudCmd + subcommands (0.3.6) =================
''', r'''# ================= 0.3.20 FEED part B: the bridge API (any thread), the 250 ms step (SkyyHud's thread), /skyyhud testfeed ================
FXM(feed, """
public static java.util.UUID uuidOf(Object o) {
  if (o instanceof java.util.UUID) return (java.util.UUID) o;
  if (o instanceof String) { try { return java.util.UUID.fromString(((String) o).trim()); } catch (Throwable t) { return null; } }
  return null;
}""")
FXM(feed, """
public static String cleanKind(Object o) {
  if (!(o instanceof String)) return null;
  String s = ((String) o).trim().toLowerCase(java.util.Locale.ROOT);
  if (s.length() < 1 || s.length() > 16) return null;
  for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); if (c < 'a' || c > 'z') return null; }
  return s;
}""")
FXM(feed, """
public static String cleanText(Object o, int max) {
  if (o == null) return "";
  String s = String.valueOf(o);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); sb.append(c < ' ' || c == 127 ? ' ' : c); }
  String t = sb.toString().trim();
  if (t.length() > max) t = t.substring(0, max).trim();
  return t;
}""")
FXM(feed, """
public static String cleanIcon(Object o) {
  if (!(o instanceof String)) return null;
  String s = ((String) o).trim();
  if (s.length() < 1 || s.length() > 96) return null;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == ':' || c == '-')) return null;
  }
  return s;
}""")
FXM(feed, """
public static String cleanSkill(Object o) {
  String s = cleanText(o, 24);
  if (s.length() == 0) return null;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!(Character.isLetterOrDigit(c) || c == ' ' || c == '-' || c == 39)) return null;
  }
  return s;
}""")
FXM(feed, """
public static int clsOf(String kind) {
  if ("coins".equals(kind) || "drop".equals(kind)) return 1;
  if ("heal".equals(kind)) return 2;
  if ("petxp".equals(kind)) return 3;
  return 0;
}""")
# a widget of a player: the layout in memory (LayoutStore.CACHE - never a file read), else the default a new player gets
FXM(feed, """
public static boolean widgetOn(java.util.UUID u, String id) {
  try {
    Object m = null;
    if (u != null) m = @PKG@.LayoutStore.CACHE.get(u);
    Object o = null;
    if (m != null) o = ((java.util.Map) m).get(id);
    if (o instanceof @PKG@.WLayout) return ((@PKG@.WLayout) o).en;
    return @PKG@.Widgets.start(id).en;
  } catch (Throwable t) { return true; }
}""")
FXM(feed, """
public static boolean hasHud(java.util.UUID u) {
  @PKG@.SkyyHudPlugin p = PLUGIN;
  return p != null && u != null && p.huds.containsKey(u);
}""")
FXM(feed, """
public static @PKG@.FeedState stateFor(java.util.UUID u) {
  Object s = STATES.get(u);
  if (s != null) return (@PKG@.FeedState) s;
  @PKG@.FeedState n = new @PKG@.FeedState(u);
  Object o = STATES.putIfAbsent(u, n);
  return o == null ? n : (@PKG@.FeedState) o;
}""")
# one push into the player's lock-free queue (bounded by QMAX) and the player into ACTIVE - the only thing a caller's thread does
FXM(feed, """
public static boolean offer(java.util.UUID u, Object[] e) {
  @PKG@.FeedState s = stateFor(u);
  if (s.qn.incrementAndGet() > QMAX) { s.qn.decrementAndGet(); DROPPED.incrementAndGet(); return false; }
  s.q.offer(e);
  ACTIVE.put(u, s);
  return true;
}""")
# feed:fn:push - apply(Object[] { UUID|String player, String kind, String itemId or null, String text, Number count or null }) -> Boolean
FXM(feed, """
public static Boolean push(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 4 || !@PKG@.FeedCfg.ENABLED) return Boolean.FALSE;
    java.util.UUID u = uuidOf(a[0]);
    String kind = cleanKind(a[1]);
    String icon = cleanIcon(a[2]);
    String text = cleanText(a[3], 48);
    if (u == null || kind == null || text.length() == 0) return Boolean.FALSE;
    if (!hasHud(u) || !widgetOn(u, "Feed")) return Boolean.FALSE;
    long n = 1L;
    boolean hc = false;
    if (a.length > 4 && a[4] instanceof Number) {
      long c = ((Number) a[4]).longValue();
      if (c > 0L) { n = c > 999999999L ? 999999999L : c; hc = true; }
    }
    if (!offer(u, new Object[] { "f", kind, icon, text, Long.valueOf(n), Boolean.valueOf(hc) })) return Boolean.FALSE;
    PUSHES.incrementAndGet();
    return Boolean.TRUE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
# review 2 fix: would this skill's flash be DRAWN? (memory only: the layout in LayoutStore.CACHE / the default + bridge map reads) - a shown
# line (the class line = the player's class skill), else a temporary row when "XP of hidden skills" is Show and a row is still free.
# FALSE -> xpflash:fn:push answers FALSE and the sender sends its chat line (nothing vanishes silently).
FXM(feed, """
public static boolean xpShows(java.util.UUID u, String skill) {
  try {
    Object o = null;
    Object m = u == null ? null : @PKG@.LayoutStore.CACHE.get(u);
    if (m != null) o = ((java.util.Map) m).get("Skills");
    @PKG@.WLayout l = o instanceof @PKG@.WLayout ? (@PKG@.WLayout) o : @PKG@.Widgets.start("Skills");
    int mask = l == null || l.lines <= 0 ? @PKG@.WLayout.LINES_DEF : l.lines;
    java.util.Map b = @PKG@.Widgets.bridge();
    if (!@PKG@.Widgets.skillsHave(b)) return false;
    int vis = mask & @PKG@.Widgets.skillsVis(b);
    String n = skill.trim();
    for (int k = 2; k < @PKG@.WLayout.LINE_N; k++) {
      if ((vis & (1 << k)) != 0 && @PKG@.WLayout.LINE_LABELS[k].equalsIgnoreCase(n)) return true;
    }
    if ((vis & 2) != 0) {
      String cls = @PKG@.Widgets.bstr(b, "class:skill:" + u.toString());
      if (cls != null && cls.trim().equalsIgnoreCase(n)) return true;
    }
    boolean hid = l == null || l.opt;
    return hid && Integer.bitCount(vis) < @LN@;
  } catch (Throwable t) { return true; }
}""")
# xpflash:fn:push - apply(Object[] { UUID|String player, String skill, Number amount }) -> Boolean
FXM(feed, """
public static Boolean xpPush(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[2] instanceof Number)) return Boolean.FALSE;
    java.util.UUID u = uuidOf(a[0]);
    String skill = cleanSkill(a[1]);
    double d = ((Number) a[2]).doubleValue();
    if (u == null || skill == null || !(d >= 0.5) || Double.isInfinite(d)) return Boolean.FALSE;
    long amt = Math.round(d);
    if (amt > 999999999L) amt = 999999999L;
    if (!hasHud(u) || !widgetOn(u, "Skills") || !xpShows(u, skill)) return Boolean.FALSE;
    if (!offer(u, new Object[] { "x", skill, Long.valueOf(amt) })) return Boolean.FALSE;
    XPS.incrementAndGet();
    return Boolean.TRUE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
# msgroute:fn:get - "chat" | "feed" | "off": the player's own switches (settings:fn:get) else the Server Setup default; feed falls back to
# chat when the player's Feed (skillxp: Skills) widget is off or the feed is switched off; system / unknown kinds = chat
FXM(feed, """
public static String route(java.util.UUID u, Object kindO) {
  String k = cleanKind(kindO);
  if (k == null) return "chat";
  String d = @PKG@.FeedCfg.route(k);
  if (d == null) return "chat";
  if (!hasHud(u)) return "feed".equals(d) ? "chat" : d;      // review 2 fix: no HUD = memory only (settings:fn:get may read a file)
  String r = d;
  try {
    java.util.Map b = @PKG@.Widgets.bridge();
    Object f = null;
    if (b != null && u != null) f = b.get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object sh = ((java.util.function.Function) f).apply(new Object[] { u, "msg." + k });
      if (sh instanceof Boolean) {
        if (!((Boolean) sh).booleanValue()) r = "off";
        else {
          Object fe = ((java.util.function.Function) f).apply(new Object[] { u, "msg." + k + ".feed" });
          if (fe instanceof Boolean) r = ((Boolean) fe).booleanValue() ? "feed" : "chat";
          else r = "feed".equals(d) ? "feed" : "chat";
        }
      }
    }
  } catch (Throwable t) { r = d; }
  if ("feed".equals(r)) {
    if ("skillxp".equals(k)) { if (!widgetOn(u, "Skills")) r = "chat"; }
    else if (!@PKG@.FeedCfg.ENABLED || !widgetOn(u, "Feed")) r = "chat";
  }
  return r;
}""")
# ---- the 250 ms step of one player (SkyyHud's thread ONLY: cards / batch / flash are never touched elsewhere)
# FIX 3 (review): an item id is only drawn when the server has that item loaded (Item.getAssetMap - a read-only asset lookup, no world /
# store / entity; cached per id, at most 2048 ids) - a mistyped / removed / pack-only id becomes "no icon" and the card shows its text
FXM(feed, """
public static boolean iconOk(String id) {
  if (id == null) return false;
  Object c = ICONS.get(id);
  if (c != null) return ((Boolean) c).booleanValue();
  boolean ok = false;
  try { ok = @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { ok = false; }
  if (ICONS.size() >= 2048) ICONS.clear();
  ICONS.put(id, Boolean.valueOf(ok));
  return ok;
}""")
# FIX 1 (review): a notice the feed cannot draw (a card pushed out before any step drew it, an XP batch past the 16 cap) becomes a chat
# line instead (sent by tickAll -> flushOver, SkyyHud's thread) - push answered TRUE, so the sender relies on it being seen
FXM(feed, """
public static void overflow(@PKG@.FeedState s, String t) {
  OVERFLOW.incrementAndGet();
  if (t != null && t.length() > 0 && s.over.size() < QMAX) s.over.add(t);
}""")
FXM(feed, """
public static String cardLine(@PKG@.FeedCard c) {
  return c.text + (c.showCount ? "  x" + @PKG@.Widgets.fmt(c.count) : "");
}""")
FXM(feed, """
public static void addCard(@PKG@.FeedState s, Object[] e, long now, long mergeMs, int max) {
  String kind = (String) e[1];
  String icon = (String) e[2];
  if (icon != null && !iconOk(icon)) icon = null;
  String text = (String) e[3];
  long n = ((Long) e[4]).longValue();
  boolean hc = ((Boolean) e[5]).booleanValue();
  String key = kind + "|" + (icon != null ? icon : text.toLowerCase(java.util.Locale.ROOT));
  for (int i = 0; i < s.cards.size(); i++) {
    @PKG@.FeedCard c = (@PKG@.FeedCard) s.cards.get(i);
    if (c.key.equals(key) && now - c.changed < mergeMs) {
      long t = c.count + n;
      c.count = t > 999999999L ? 999999999L : t;
      c.showCount = true;
      c.text = text;
      c.changed = now;
      c.hiUntil = now + 300L;
      if (i > 0) { s.cards.remove(i); s.cards.add(0, c); }     // the stack is ordered by the last change: a merged card is the newest
      return;
    }
  }
  s.cards.add(0, new @PKG@.FeedCard(key, kind, icon, text, n, hc, clsOf(kind), now));
  while (s.cards.size() > max) {
    @PKG@.FeedCard o = (@PKG@.FeedCard) s.cards.remove(s.cards.size() - 1);
    if (!o.shown) overflow(s, cardLine(o));
  }
}""")
FXM(feed, """
public static void addXp(@PKG@.FeedState s, String skill, long amt, long now) {
  String key = skill.toLowerCase(java.util.Locale.ROOT);
  Object[] b = (Object[]) s.batch.get(key);
  if (b != null) { b[1] = Long.valueOf(((Long) b[1]).longValue() + amt); return; }
  if (s.batch.size() + s.flash.size() >= 16 && !s.flash.containsKey(key)) { DROPPED.incrementAndGet(); overflow(s, fmtGain(amt) + " " + skill + " XP"); return; }
  s.batch.put(key, new Object[] { skill, Long.valueOf(amt), Long.valueOf(now) });
}""")
FXM(feed, """
public static @PKG@.FeedView makeView(@PKG@.FeedState s, long now, long showMs, long flashMs) {
  int nf = s.flash.size();
  @PKG@.FeedView v = new @PKG@.FeedView(4, nf);
  int n = 0;
  for (int i = 0; i < s.cards.size() && n < 4; i++) {
    @PKG@.FeedCard c = (@PKG@.FeedCard) s.cards.get(i);
    long age = now - c.changed;
    int st = age < showMs + 300L ? 1 : (age < showMs + 700L ? 2 : 3);
    v.name[n] = c.text;
    v.cnt[n] = c.showCount ? "x" + @PKG@.Widgets.fmt(c.count) : "";
    v.icon[n] = c.icon;
    v.cls[n] = c.cls;
    v.stage[n] = st;
    v.hi[n] = now < c.hiUntil;
    c.shown = true;
    n = n + 1;
  }
  v.n = n;
  long s2 = 500L + (flashMs - 500L) / 2L;
  int k = 0;
  java.util.Iterator it = s.flash.values().iterator();
  while (it.hasNext() && k < nf) {
    Object[] f = (Object[]) it.next();
    long age = now - ((Long) f[2]).longValue();
    v.fn[k] = (String) f[0];
    v.fg[k] = fmtGain(((Long) f[1]).longValue());
    v.fst[k] = age < 500L ? 1 : (age < s2 ? 2 : 3);
    k = k + 1;
  }
  return v;
}""")
FXM(feed, """
public static void step(@PKG@.FeedState s, long now) {
  long showMs = (long) (@PKG@.FeedCfg.SHOW_SECS * 1000.0);
  long mergeMs = (long) (@PKG@.FeedCfg.MERGE_SECS * 1000.0);
  if (mergeMs > showMs) mergeMs = showMs;
  int max = @PKG@.FeedCfg.MAX_CARDS;
  if (max < 1) max = 1;
  if (max > 4) max = 4;
  long batchMs = (long) (@PKG@.FeedCfg.XP_BATCH_SECS * 1000.0);
  long flashMs = (long) (@PKG@.FeedCfg.XP_FLASH_SECS * 1000.0);
  if (flashMs < 1000L) flashMs = 1000L;
  for (int g = 0; g < 256; g++) {
    Object eo = s.q.poll();
    if (eo == null) break;
    s.qn.decrementAndGet();
    Object[] e = (Object[]) eo;
    if ("x".equals(e[0])) addXp(s, (String) e[1], ((Long) e[2]).longValue(), now);
    else addCard(s, e, now, mergeMs, max);
  }
  for (int i = s.cards.size() - 1; i >= 0; i--) {
    @PKG@.FeedCard c = (@PKG@.FeedCard) s.cards.get(i);
    if (now - c.changed >= showMs + 1000L) s.cards.remove(i);
  }
  while (s.cards.size() > max) s.cards.remove(s.cards.size() - 1);
  java.util.Iterator it = s.batch.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    Object[] b = (Object[]) en.getValue();
    if (now - ((Long) b[2]).longValue() < batchMs) continue;
    Object key = en.getKey();
    Object[] f = (Object[]) s.flash.get(key);
    if (f == null) s.flash.put(key, new Object[] { b[0], b[1], Long.valueOf(now) });
    else { f[1] = Long.valueOf(((Long) f[1]).longValue() + ((Long) b[1]).longValue()); f[2] = Long.valueOf(now); }
    it.remove();
  }
  java.util.Iterator fi = s.flash.values().iterator();
  while (fi.hasNext()) {
    Object[] f = (Object[]) fi.next();
    if (now - ((Long) f[2]).longValue() >= flashMs) fi.remove();
  }
  s.view = makeView(s, now, showMs, flashMs);
}""")
# FIX 1: send the overflow chat lines of one player (SkyyHud's thread; pr.sendMessage is the 0.3.18 minimap's off-world-thread pattern)
FXM(feed, """
public static int flushOver(@PKG@.FeedState s, @PKG@.HudMain h) {
  if (s.over.isEmpty()) return 0;
  int n = 0;
  try {
    @PR@ pr = h == null ? null : h.getPlayerRef();
    if (pr != null) {
      for (int i = 0; i < s.over.size(); i++) { pr.sendMessage(@MSG@.raw((String) s.over.get(i))); n = n + 1; }
    }
  } catch (Throwable t) { ERRORS.incrementAndGet(); }
  s.over.clear();
  return n;
}""")
FXM(feed, """
public static boolean idle(@PKG@.FeedState s) {
  return s.q.isEmpty() && s.cards.isEmpty() && s.batch.isEmpty() && s.flash.isEmpty();
}""")
# the timer (FeedTick, every 250 ms on SkyyHud's thread): only the ACTIVE players; each = drain + merge + expire, publish the view, ONE
# HUD update (HudMain.feedTick); a player with nothing left leaves ACTIVE (re-added at once if a push raced in)
FXM(feed, """
public static void tickAll(@PKG@.SkyyHudPlugin p) {
  if (p == null || ACTIVE.isEmpty()) return;
  TICKS.incrementAndGet();
  long now = System.currentTimeMillis();
  java.util.Iterator it = ACTIVE.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    java.util.UUID u = (java.util.UUID) e.getKey();
    @PKG@.FeedState s = (@PKG@.FeedState) e.getValue();
    try {
      @PKG@.HudMain h = (@PKG@.HudMain) p.huds.get(u);
      if (h == null) { ACTIVE.remove(u, s); STATES.remove(u, s); continue; }
      step(s, now);
      flushOver(s, h);
      h.feedTick(now);
      if (idle(s)) {
        ACTIVE.remove(u, s);
        if (!s.q.isEmpty()) ACTIVE.put(u, s);
      }
    } catch (Throwable t) { ERRORS.incrementAndGet(); }
  }
}""")
# ---- /skyyhud testfeed: sample cards routed exactly like a sender mod (msgroute -> feed / chat / off), the merge, the XP flash
FXM(feed, """
public static String testCard(@PR@ pr, String kind, String icon, String text, long count) {
  java.util.UUID u = pr.getUuid();
  String r = route(u, kind);
  if ("feed".equals(r)) {
    Long cnt = null;
    if (count > 0L) cnt = Long.valueOf(count);
    Object res = push(new Object[] { u, kind, icon, text, cnt });
    if (Boolean.TRUE.equals(res)) return "feed";
    r = "chat";
  }
  if ("off".equals(r)) return "off";
  pr.sendMessage(@MSG@.raw("[Feed test, chat] " + text + (count > 1L ? "  x" + count : "")));
  return "chat";
}""")
FXM(feed, """
public static String testXp(@PR@ pr, String skill, long amt) {
  java.util.UUID u = pr.getUuid();
  String r = route(u, "skillxp");
  if ("feed".equals(r) && Boolean.TRUE.equals(xpPush(new Object[] { u, skill, Long.valueOf(amt) }))) return "feed";
  if ("off".equals(r)) return "off";
  pr.sendMessage(@MSG@.raw("[Feed test, chat] +" + amt + " " + skill + " XP"));
  return "chat";
}""")
FXM(feed, """
public static void tally(int[] c, String r) {
  if ("feed".equals(r)) c[0] = c[0] + 1;
  else if ("chat".equals(r)) c[1] = c[1] + 1;
  else c[2] = c[2] + 1;
}""")
FXM(feed, """
public static void testStep(@PR@ pr, int step) {
  if (pr == null || !hasHud(pr.getUuid())) return;      // the player left: nothing to show
  testCard(pr, "pickup", "Plant_Crop_Pumpkin_Item", "Pumpkin", step == 1 ? 3L : 5L);
}""")
FXC(ftest, "public FeedTestStep(@PR@ pr, int step) { this.pr = pr; this.step = step; }")
FXM(feed, """
public static String test(@PR@ pr) {
  int[] c = new int[3];
  tally(c, testCard(pr, "heal", null, "+8 HP  Priest heal", 0L));
  tally(c, testCard(pr, "coins", null, "+120 coins  Bank interest", 0L));
  tally(c, testCard(pr, "petxp", null, "Wolf  +35 Pet XP", 0L));
  tally(c, testCard(pr, "quest", null, "Chop logs  7/10", 0L));
  tally(c, testCard(pr, "drop", "Wood_Oak_Trunk", "Double drop!  Oak Log", 2L));
  tally(c, testCard(pr, "pickup", "Plant_Crop_Pumpkin_Item", "Pumpkin", 1L));
  String cs = null;
  try { cs = @PKG@.Widgets.bstr(@PKG@.Widgets.bridge(), "class:skill:" + pr.getUuid().toString()); } catch (Throwable t) { cs = null; }
  if (cs == null || cs.trim().length() == 0) cs = "Foraging";
  cs = cs.trim();
  int[] x = new int[3];
  tally(x, testXp(pr, cs, 79L));
  tally(x, testXp(pr, "Mining", 40L));
  @PKG@.HudThreads.later(new @PKG@.FeedTestStep(pr, 1), 800L);
  @PKG@.HudThreads.later(new @PKG@.FeedTestStep(pr, 2), 2100L);
  return "Test feed: 6 cards (feed " + c[0] + ", chat " + c[1] + ", off " + c[2] + ") + Skill XP " + cs + " +79 and Mining +40 (skill list " + x[0]
    + ", chat " + x[1] + ", off " + x[2] + "). Watch: 4 cards at most - the 2 oldest never get drawn, so they come into chat instead, Pumpkin merges to x9 over 2 s, the XP flashes on your Skills widget after 2 s. Where each kind goes: /settings or Server Setup -> Messages.";
}""")
# the bridge Functions (plain java.lang types in and out)
for _c, _body in ((fpush, "return @PKG@.Feed.push(o);"), (fxp, "return @PKG@.Feed.xpPush(o);")):
    _c.addInterface(pool.get("java.util.function.Function"))
    FXC(_c, "public %s() { }" % _c.getSimpleName())
    FXM(_c, "public Object apply(Object o) { " + _body + " }")
froute.addInterface(pool.get("java.util.function.Function"))
FXC(froute, "public MsgRouteFn() { }")
FXM(froute, """
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "chat";
    Object[] a = (Object[]) o;
    if (a.length < 2) return "chat";
    return @PKG@.Feed.route(@PKG@.Feed.uuidOf(a[0]), a[1]);
  } catch (Throwable t) { return "chat"; }
}""")
# published once in setup() (never removed - the bridge convention; with the plugin gone every push answers FALSE)
FXM(feed, """
public static void publish() {
  java.util.Map br = @PKG@.FeedCfg.bridgeC();
  br.put("feed:fn:push", new @PKG@.FeedPushFn());
  br.put("xpflash:fn:push", new @PKG@.XpFlashFn());
  br.put("msgroute:fn:get", new @PKG@.MsgRouteFn());
}""")
ftick.addInterface(pool.get("java.lang.Runnable"))
FXF(ftick, "public @PKG@.SkyyHudPlugin plugin;")
FXC(ftick, "public FeedTick(@PKG@.SkyyHudPlugin p) { this.plugin = p; }")
FXM(ftick, """
public void run() {
  try { @PKG@.Feed.tickAll(this.plugin); } catch (Throwable t) { @PKG@.Feed.ERRORS.incrementAndGet(); }
}""")
FXM(ftest, """
public void run() {
  try { @PKG@.Feed.testStep(this.pr, this.step); } catch (Throwable t) { }
}""")
# /skyyhud testfeed - an ADMIN sub-command under the Adventurer command /skyyhud: requirePermission AND setPermissionGroups(new String[0])
ctf.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", ctf))
ctf.addConstructor(CtNewConstructor.make(f"""
public HudTestFeedCmd({PKG}.SkyyHudPlugin p) {{
  super("testfeed", "Admin: show test cards in your notification feed and a Skill XP flash");
  this.plugin = p;
  requirePermission("{HUD_NODE}");
  setPermissionGroups(new String[0]);
}}""", ctf))
ctf.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!pr.hasPermission("{HUD_NODE}")) {{ pr.sendMessage({MSG}.raw("[SkyyHud] no permission ({HUD_NODE})")); return; }}
    if (!this.plugin.huds.containsKey(pr.getUuid())) this.plugin.attach(pr);
    pr.sendMessage({MSG}.raw("[SkyyHud] " + {PKG}.Feed.test(pr)));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("[SkyyHud] error: " + t));
  }}
}}""", ctf))

''')
rep('''  addSubCommand(new {PKG}.HudMinimapCmd(p));
}}""", cmd))''', '''  addSubCommand(new {PKG}.HudMinimapCmd(p));
  addSubCommand(new {PKG}.HudTestFeedCmd(p));      // 0.3.20 (admin)
}}""", cmd))''')

# ---------------- EditorPage: the feed box is fixed-size ----------------
rep('''      this.ww.put(ids[i], Integer.valueOf(("Minimap".equals(ids[i]) || l.fixed) ? l.bw * l.scale / 100 : {PKG}.Widgets.lineW(l, text, l.scale, 6)));''',
    '''      this.ww.put(ids[i], Integer.valueOf(("Minimap".equals(ids[i]) || "Feed".equals(ids[i]) || l.fixed) ? l.bw * l.scale / 100 : {PKG}.Widgets.lineW(l, text, l.scale, 6)));''')

# ---------------- SettingsPage: Feed "Item icons", Skills "XP of hidden skills" ----------------
rep(r'''    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Hide shows the ability names only\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }}''', r'''    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Hide shows the ability names only\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }} else if ("Feed".equals(this.wid)) {{
    // 0.3.20 Feed: the item's own icon on each card - Show, or Hide (a colour chip per message type). Hide = WLayout.opt true = the DEFAULT
    // (an ItemIcon inside a HUD is UNVERIFIED in game - the Abilities-icons rule); the option row's place, ids and payloads
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 60, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 250, Height: 44); Text: \\"Item icons\\"; " + rl + " }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOff {{ Anchor: (Width: 104, Height: 44); Text: \\"Show\\"; " + (l.opt ? bs : on) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 8, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOn {{ Anchor: (Width: 104, Height: 44); Text: \\"Hide\\"; " + (l.opt ? on : bs) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 20, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Hide shows a colour chip per message type\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }} else if ("Skills".equals(this.wid)) {{
    // 0.3.20 Skills: a skill whose line is off joins as a temporary row while it flashes Skill XP - Show (WLayout.opt true, the default)
    // or Hide (only the shown lines flash)
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 60, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 250, Height: 44); Text: \\"XP of hidden skills\\"; " + rl + " }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOn {{ Anchor: (Width: 104, Height: 44); Text: \\"Show\\"; " + (l.opt ? on : bs) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 8, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOff {{ Anchor: (Width: 104, Height: 44); Text: \\"Hide\\"; " + (l.opt ? bs : on) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 20, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Show = a hidden skill joins while it gains XP\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }}''')

# ---------------- setup / shutdown ----------------
rep('''  this.ticker = {PKG}.HudThreads.start().scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);   // 0.3.19: own thread
''', '''  this.ticker = {PKG}.HudThreads.start().scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);   // 0.3.19: own thread
  // 0.3.20 notification feed + Skill XP flash: the bridge API (feed:fn:push, xpflash:fn:push, msgroute:fn:get), the per-player message
  // switches (settings:fn:register) and the 250 ms feed timer on SkyyHud's OWN thread (never the engine's shared scheduler)
  {PKG}.Feed.PLUGIN = this;
  {PKG}.Feed.publish();
  {PKG}.FeedCfg.registerAll();
  this.feedTicker = {PKG}.HudThreads.start().scheduleAtFixedRate(new {PKG}.FeedTick(this), 250L, 250L, java.util.concurrent.TimeUnit.MILLISECONDS);
''')
rep('''" (admins: /skyyhud default, Server Setup -> HUD / Minimap)");''',
    '''"; notification feed " + ({PKG}.FeedCfg.ENABLED ? "on" : "off (Server Setup)") + " (admins: /skyyhud default, /skyyhud testfeed, Server Setup -> HUD / Minimap / Feed / Messages)");''')
rep('''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.HudThreads.stop(); }} catch (Throwable t) {{ }}''', '''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.feedTicker != null) this.feedTicker.cancel(false); }} catch (Throwable t) {{ }}     // 0.3.20
  {PKG}.Feed.PLUGIN = null;                                                                            // 0.3.20: pushes answer FALSE now
  try {{ {PKG}.HudThreads.stop(); }} catch (Throwable t) {{ }}''')

# ---------------- the jar description ----------------
rep('''"SkyyHud: customizable server-side HUD. 14 widgets (15 with Dynamic Seasons) incl. Abilities''',
    '''"SkyyHud: customizable server-side HUD. 15 widgets (16 with Dynamic Seasons) incl. a Notification Feed (small cards above the chat that fade and merge repeats - Pumpkin x9; other mods send to it through the bridge, players pick Chat / Feed / Off per message type), a Skill XP flash on the Skills widget (+79 next to the skill), Abilities''')

# ---------------- self-checks ----------------
assert 'IDS.append("Feed")' in s and s.count('"Feed".equals(') >= 7
assert "SCHEDULED_EXECUTOR.scheduleAtFixedRate" not in s, "every timer on SkyyHud's own thread"
assert s.count("new {PKG}.FeedTick(this), 250L, 250L") == 1
assert "KEEP=10" in s and "KEEP=20" not in s
assert "_" not in "".join(__import__("re").findall(r'#SkyyW(?:Feed|Skills)[A-Za-z0-9" +]*', s)), "no underscores in element ids"
for a_, b_ in (("public static @PKG@.FeedView viewOf(", "public static String[] skillsModelX("),
               ("public static String[] skillsModelX(", "public static String[] modelL("),
               ("public static int flashStage(", "public boolean feedFill("),
               ("public static String feedSrc(", "protected void build({UCB} b)"),
               ("public static String feedFit(", "public boolean feedFill("),
               ("public boolean feedFill(", "protected void build({UCB} b)"),
               ("public static boolean feedPlace(", "public static java.util.Map get(java.util.UUID u)"),
               ("public static void loadFrom(java.util.Properties p) {\n  ENABLED", "public static String load()"),
               ("public static void forget(", "public void tickAll()"),
               ("public synchronized void feedTick(", "public static void tickAll(@PKG@.SkyyHudPlugin p)"),
               ("public static void tickAll(@PKG@.SkyyHudPlugin p)", "public FeedTick(@PKG@.SkyyHudPlugin p)"),
               ("public MsgRouteFn()", "public static void publish()"),
               ("public static String test(@PR@ pr)", "public HudTestFeedCmd("),
               ("public HudTestFeedCmd(", "addSubCommand(new {PKG}.HudTestFeedCmd(p))"),
               ("public static void testStep(", "FXC(ftest, \"public FeedTestStep("),
               ("FXF(ftest, \"public @PR@ pr;\")", "FXC(ftest, \"public FeedTestStep(")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.19 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
