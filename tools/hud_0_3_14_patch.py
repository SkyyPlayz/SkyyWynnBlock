"""Derive SkyyHud/build_skyyhud_0.3.14.py from the LIVE 0.3.13 (the SET pin; 0.3.13 is left untouched; line endings preserved).
0.3.14 = the MINIMAP widget (research/Minimap-Widget-Spec.md rev 2; docs/answered/ui.md LOCKED / ANSWERED 2026-10-03: our own minimap as a
SkyyHud widget REQUIRING BetterMap, reusing the engine's map stream, DapperMap-like settings, no info panel; round, top-right, ~160 px,
north-up; each map piece sent once as a small cached picture; no world-thread map work).
  - widget id Minimap APPENDED to Widgets.IDS (default ON at tr 8,40 - under the Zone widget), its OWN keyed HUD "SkyyHudMinimap" (zOrder 5)
    through the engine's HudManager (world thread only for add / remove), never inside skyyhud_main
  - the map pieces come from the engine's outbound UpdateWorldMap stream (a PlayerPacketWatcher that only queues references) and, for chunks
    the player's own stream already sent, WorldMapManager.getImageIfInMemory; downscaled (alpha-weighted, 5-bit) + PNG-encoded on its OWN
    thread "SkyyHud-Minimap" (3 ms / 24 pieces per 0.25 s, round-robin), cached by CONTENT, each picture sent once per connection
  - the settings page (Display / Markers / Colours / Integrations) is built with the vanilla kit (tools/skyyui.py) HERE, at patch time
    (method B of research/Vanilla-UI-Style-Guide.md 8c): the generated script must not import the kit - its old-look pages would flood
    lint's kit-colour warnings (the 0.3.13 patch's reason too). The kit is verified (SUI.verify) and every page token proven here.
  - Server Setup -> Minimap rows (tools/skyycfg.py, KEEP=10); /skyyhud minimap [on | off]
FIX ROUND (2026-10-06, the three critic reports): see the generated docstring's FIX ROUND list (re-attach only for a new frame, pending
attach until the map stream starts, tap for every player, bounded by pieces, the burst kept in the window, chunk (-1,-1), per-session
detail, rate-limited markers + arrow on its own, rim re-pin, cap counts tiles + tells the player, budget scaling, watchdog, fast reconnect,
Online default, hint seconds, wording).
Harness: python SkyyHud/test_skyyhud_0.3.14.py (bare JVM; see its docstring).
To regenerate, delete SkyyHud/build_skyyhud_0.3.14.py first (the script refuses to overwrite it).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI      # patch time only: the settings page + the HUD markup checks (see the docstring)

src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.13.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.14.py")
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

# =================================================================================================== the HUD markup (kit-checked)
MM_KEY, MM_Z = "SkyyHudMinimap", 5
DARK_BG = SUI.COLOR["darkBlock"]          # the clip's backdrop: what "not yet received" shows
# templates: @@name@@ = a Java expression concatenated in at runtime (the same text is checked here with sample numbers)
T_ROOT = 'Group #SkyyMmRoot { Anchor: (Full: 0); }'
T_BOX = 'Group #SkyyMmBox { Anchor: @@anc@@; }'
T_CLIP = ('Group #SkyyMmClip { Anchor: (Left: @@rw@@, Top: @@rw@@, Width: @@c@@, Height: @@c@@); MaskTexturePath: "@@mask@@"; '
          'Background: ' + DARK_BG + '; }')
T_GRID = 'Group #SkyyMmGrid { Anchor: (Left: @@gl@@, Top: @@gt@@, Width: @@gs@@, Height: @@gs@@); }'
T_TILE = 'AssetImage #SkyyMmT@@i@@ { Anchor: (Left: @@x@@, Top: @@y@@, Width: @@t@@, Height: @@t@@); AssetPath: "@@p@@"; }'
T_MK = 'AssetImage #SkyyMmMk@@i@@ { Anchor: (Left: -4000, Top: -4000, Width: @@dp@@, Height: @@dp@@); AssetPath: "@@p@@"; }'
T_PT = 'AssetImage #SkyyMmPt@@i@@ { Anchor: (Left: -4000, Top: -4000, Width: @@dp@@, Height: @@dp@@); AssetPath: "@@p@@"; }'
T_ARROW = 'AssetImage #SkyyMmArrow { Anchor: (Left: @@ax@@, Top: @@ax@@, Width: @@ap@@, Height: @@ap@@); AssetPath: "@@p@@"; }'
T_RING = 'AssetImage #SkyyMmRing { Anchor: (Left: 0, Top: 0, Width: @@s@@, Height: @@s@@); AssetPath: "@@p@@"; }'
# what SkyyUiProbe 0.4 proved in game (P1a / P2, log 2026-10-04): a runtime picture in an AssetImage, its AssetPath, MaskTexturePath on a
# Group - the kit's table does not list them yet (MaskTexturePath sits behind its "text-mask" probe key)
MM_TRIAL = {"element AssetImage", "AssetPath", "MaskTexturePath"}


def tpl_sample(t, vals):
    out = t
    for k, v in vals.items():
        out = out.replace("@@%s@@" % k, str(v))
    assert "@@" not in out, out
    return out


def tpl_java(t, exprs):
    """the template as a Java String concatenation: literal parts as Java literals, @@x@@ = (expr)"""
    parts = t.split("@@")
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            if p:
                out.append(SUI.java_lit(p))
        else:
            out.append("(" + exprs[p] + ")")
    return " + ".join(out)


_SAMPLE = {"anc": "(Top: 40, Right: 8, Width: 160, Height: 160)", "rw": 4, "c": 152, "mask": "SkyyHudMmMask-0123456789abcdef.png",
           "gl": -100, "gt": -96, "gs": 375, "i": 7, "x": 105, "y": 30, "t": 15, "p": "UI/SkyyHud/mm/0123456789abcdef.png", "dp": 6,
           "ax": 68, "ap": 24, "s": 160}
_mm_doc = SUI.Appends()
_mm_doc.append((None, T_ROOT))
for _parent, _t in (("SkyyMmRoot", T_BOX), ("SkyyMmBox", T_CLIP), ("SkyyMmClip", T_GRID), ("SkyyMmGrid", T_TILE), ("SkyyMmGrid", T_MK),
                    ("SkyyMmGrid", T_PT), ("SkyyMmBox", T_ARROW), ("SkyyMmBox", T_RING)):
    _mm_doc.append((_parent, tpl_sample(_t, _SAMPLE)))
SUI.check_markup(T_ROOT, root=False)
for _p, _mk in list(_mm_doc)[1:]:
    SUI.check_markup(_mk)
    assert "_" not in _mk.split("{")[0], "no underscore in a minimap element id: " + _mk[:60]
_tok = SUI.proven_tokens(_mm_doc)
_bad = sorted(t for t, g in _tok.items() if g is not None and t not in MM_TRIAL)
assert not _bad, "minimap HUD tokens neither proven nor probe-proven: %s" % _bad
assert set(t for t, g in _tok.items() if g is not None) == MM_TRIAL, _tok

JE = {"anc": "anc", "rw": "s.rw", "c": "s.C", "mask": "s.maskRel", "gl": "gl", "gt": "gt", "gs": "s.span * s.t", "i": "i",
      "x": "(i % s.w) * s.t", "y": "(i / s.w) * s.t", "t": "s.t", "p": "pth", "dp": "s.dp", "ax": "(s.S - s.ap) / 2", "ap": "s.ap",
      "s": "s.S"}
J_BOX, J_CLIP, J_GRID, J_TILE = tpl_java(T_BOX, JE), tpl_java(T_CLIP, JE), tpl_java(T_GRID, JE), tpl_java(T_TILE, JE)
J_MK, J_PT, J_ARROW, J_RING = tpl_java(T_MK, JE), tpl_java(T_PT, JE), tpl_java(T_ARROW, JE), tpl_java(T_RING, JE)

# =================================================================================================== the settings page (kit)
SP = "SkyyMmS"                       # element id prefix (letters only)
PAGE_W = 1320
LAB_W = 250
PAL_KEYS = ["def", "white", "gold", "yellow", "green", "lime", "aqua", "blue", "purple", "pink", "red", "orange", "gray"]
PAL_NAMES = ["Default", "White", "Gold", "Yellow", "Green", "Lime", "Aqua", "Blue", "Purple", "Pink", "Red", "Orange", "Gray"]
RADII = [64, 96, 128, 160, 224, 320]
SIZES = [50, 75, 100, 125, 150, 175, 200]
ROW_H, ROW_GAP = 32, 8
sp_rows = []                         # (row id, label text) in order
sp_extra = []                        # extra Java lines (conditional appends) keyed by position
binds = []                           # (selector, payload)


def opt_button(bid, text, cond, w):
    on = SUI.button(bid, text, "tertiary", "small", w=w, selected=True, anchor={"right": 6})
    off = SUI.button(bid, text, "tertiary", "small", w=w, anchor={"right": 6})
    return SUI.choose(cond, on, off)


def page_build():
    import math
    rows = 0
    sections = 0
    texts = 0
    sh_parts = []
    ap = SUI.Appends()
    java = []

    # the frame is made after the height is known: collect the body first
    body = []                        # (kind, data)

    def section(text):
        body.append(("sec", text))

    def row(rid, label, items, hint=None):
        body.append(("row", (rid, label, items, hint)))

    section("Display")
    row("Show", "Show minimap", [("SkyyMmSEnOn", "On", "en", "mm:en:1", 110), ("SkyyMmSEnOff", "Off", "!en", "mm:en:0", 110)])
    row("Zoom", "Zoom in blocks", [("SkyyMmSZ%d" % r, str(r), "v[0] == %d" % r, "mm:z:%d" % r, 90, "%d <= mx" % r) for r in RADII],
        hint=("SkyyMmSZHint", SUI.J("zoomHint", "up to 224 here")))
    row("Size", "Size in percent", [("SkyyMmSSz%d" % z, str(z), "sc == %d" % z, "mm:sz:%d" % z, 90) for z in SIZES])
    row("Shape", "Shape", [("SkyyMmSShR", "Round", "v[1] == 0", "mm:s:0", 130), ("SkyyMmSShQ", "Square", "v[1] == 1", "mm:s:1", 130)])
    row("Upd", "Update speed", [("SkyyMmSU250", "Smooth", "v[2] == 250", "mm:u:250", 130, "mi <= 250L"),
                                ("SkyyMmSU500", "Normal", "v[2] == 500", "mm:u:500", 130, "mi <= 500L"),
                                ("SkyyMmSU1000", "Saver", "v[2] == 1000", "mm:u:1000", 130)],
        hint=("SkyyMmSUHint", SUI.J("speedHint", "fastest here: 0.25 s")))
    row("Ring", "Ring", [("SkyyMmSRgOn", "On", "v[3] == 1", "mm:g:1", 110), ("SkyyMmSRgOff", "Off", "v[3] == 0", "mm:g:0", 110)])
    row("Rot", "Rotation", [], hint=("SkyyMmSRotTx", "North up - your arrow turns (the game cannot turn HUD pictures)."))
    section("Markers")
    row("Party", "Party members", [("SkyyMmSPaOn", "On", "(mk & 1) != 0", "mm:mk:1:1", 110), ("SkyyMmSPaOff", "Off", "(mk & 1) == 0", "mm:mk:1:0", 110)],
        hint=("SkyyMmSPaHint", SUI.J("partyHint", "")))
    row("Mark", "Map markers", [("SkyyMmSMkOn", "On", "(mk & 2) != 0", "mm:mk:2:1", 110), ("SkyyMmSMkOff", "Off", "(mk & 2) == 0", "mm:mk:2:0", 110)],
        hint=("SkyyMmSMkHint", "Waypoints, homes, warps - whatever your big map shows."))
    row("Oth", "Other players", [("SkyyMmSOpOn", "On", "(mk & 4) != 0", "mm:mk:4:1", 110), ("SkyyMmSOpOff", "Off", "(mk & 4) == 0", "mm:mk:4:0", 110)],
        hint=("SkyyMmSOpHint", SUI.J("othersHint", "")))
    row("Msz", "Marker size", [("SkyyMmSMs0", "Small", "v[4] == 0", "mm:ms:0", 130), ("SkyyMmSMs1", "Normal", "v[4] == 1", "mm:ms:1", 130),
                               ("SkyyMmSMs2", "Large", "v[4] == 2", "mm:ms:2", 130)])
    section("Colours")
    for pre, lab, var, pay in (("Rc", "Ring colour", "rc", "rc"), ("Pc", "Party dot colour", "pcol", "pc")):
        for half in (0, 1):
            ks = range(0, 7) if half == 0 else range(7, 13)
            row(pre + str(half), lab if half == 0 else "",
                [("SkyyMmS%s%s" % (pre, PAL_NAMES[k]), PAL_NAMES[k], "%s.equals(%s)" % (SUI.java_lit(PAL_KEYS[k]), var),
                  "mm:%s:%s" % (pay, PAL_KEYS[k]), 130) for k in ks])
    section("Integrations")
    row("Bm", "BetterMap", [], hint=("SkyyMmSBmTx", SUI.J("bmText", "BetterMap 1.3.8 found - the minimap reads its map")))

    # heights: section label 26 + 10 + 4; a row 32 + 8; the footer button_row 44 + 8
    n_sec = sum(1 for k, _d in body if k == "sec")
    n_row = sum(1 for k, _d in body if k == "row")
    foot_h = SUI.BTN_H + 8
    inner = n_sec * (26 + 14) + n_row * (ROW_H + ROW_GAP) + foot_h
    page_h = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + inner
    sh = SUI.page_shell(SP, PAGE_W, page_h, title="Minimap settings")
    assert sh.fit([inner]) == 0
    ap = sh.appends
    B_ = sh.body
    lines = []
    k_sec = 0
    for kind, d in body:
        if kind == "sec":
            ap.append((B_, SUI.section("SkyyMmSHd%d" % k_sec, d)))
            k_sec += 1
            continue
        rid, label, items, hint = d
        gid = "SkyyMmSR" + rid
        ap.append((B_, SUI.group(gid, "Left", h=ROW_H, anchor={"bottom": ROW_GAP})))
        if label:
            ap.text(gid, None, label, "default", w=LAB_W, h=ROW_H)
        else:
            ap.append((gid, SUI.spacer(w=LAB_W, h=ROW_H)))
        used = LAB_W
        for it in items:
            bid, text, cond, payload, w = it[:5]
            mk = opt_button(bid, text, cond, w)
            if len(it) > 5:
                ap.append((gid, mk))
                lines.append(("cond", len(ap) - 1, it[5]))
            else:
                ap.append((gid, mk))
            binds.append(("#" + bid, payload, it[5] if len(it) > 5 else None))
            used += w + 6
        if hint:
            hid, htext = hint
            ap.text(gid, hid, htext, "caption", w=PAGE_W - 2 * SUI.CONTENT_PAD - used - 16, h=ROW_H, anchor={"left": 16})
    foot = "SkyyMmSFoot"
    ap.append((B_, SUI.button_row(foot, SUI.BTN_H, "left", 8)))
    ap.append((foot, SUI.button("SkyyMmSBack", "< Back", "secondary", sound="cancel")))
    ap.append((foot, SUI.button("SkyyMmSReset", "Reset", "secondary", anchor={"left": 12})))
    binds.append(("#SkyyMmSBack", "mm:back", None))
    binds.append(("#SkyyMmSReset", "mm:reset", None))
    SUI.check_page(ap, SP)
    toks = SUI.assert_proven(ap, what="SkyyHud minimap settings page")
    cond_at = dict((i, c) for kind, i, c in lines)
    out = []
    for i, (parent, mk) in enumerate(ap):
        st = SUI.java_append(parent, mk, b="b")
        out.append("if (%s) %s" % (cond_at[i], st) if i in cond_at else st)
    for ident, prop, val in ap.sets:
        out.append(SUI.java_set(ident, prop, val, b="b"))
    for sel, payload, cond in binds:
        st = "ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(payload))
        out.append("if (%s) %s" % (cond, st) if cond else st)
    return "\n".join("  " + l for l in out), page_h, len(toks), len(ap)


MMUI_JAVA, MMUI_H, MMUI_TOKENS, MMUI_APPENDS = page_build()
assert "@@" not in MMUI_JAVA
print("patch: minimap settings page %d x %d, %d appends, %d proven tokens (kit %s)" % (PAGE_W, MMUI_H, MMUI_APPENDS, MMUI_TOKENS, KIT_ID))

# =================================================================================================== the generated script
rep('''"""SkyyHud 0.3.13 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.13.py            -> SkyyHud/SkyyHud-0.3.13.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.14 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.14.py            -> SkyyHud/SkyyHud-0.3.14.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.14 (generated by tools/hud_0_3_14_patch.py from 0.3.13): the MINIMAP widget (research/Minimap-Widget-Spec.md rev 2; docs/answered/ui.md
  LOCKED / ANSWERED 2026-10-03: "our own minimap as a SkyyHud widget REQUIRING BetterMap, reusing the engine map data, DapperMap-like
  settings, no info panel"; round, top-right, ~160 px, north-up; each map piece sent once as a small cached picture; no world-thread map work).
  - Widget id Minimap APPENDED to Widgets.IDS (0.3.13 layout files, codes and profiles load as before; 0.3.13 ignores the id). Default ON
    (admin row hud.mm.defaultOn) at tr 8,40 (under the Zone widget), box 160 x 160 at 100 %; sizes in 7 steps 50-200 % (the editor's Size
    buttons move it 25 %; any other stored size snaps to the nearest step at load). Placed / dragged / snapped / exported / saved like every
    widget. Its look is NOT in skyyhud_main: it is its OWN keyed HUD "SkyyHudMinimap" (zOrder 5) through the engine's HudManager (add /
    remove on the world thread only; MmHud.show() = update(true, a document the minimap thread built and caches per geometry - the world
    thread never builds it). skyyhud_main skips the Minimap id.
  - REQUIRES BetterMap (dev.ninesliced:BetterMap): checked once through the engine's PluginManager at the first player connect (never a
    BetterMap class - AGPL; clean room: built from the engine jar and recorded packets only). Missing: ONE log line, the widget never
    attaches, the editor / settings say "Needs BetterMap", the packet tap is never registered. Found = only the first gate: a world needs
    WorldMapManager.isWorldMapEnabled(), and a minimap whose player got no UpdateWorldMap within 15 s in that world is hidden there (one
    log line per world).
  - Map pieces: the engine's own UpdateWorldMap / ClearWorldMap stream (PacketAdapters.registerOutbound PlayerPacketWatcher MmTap: one
    volatile read when no minimap runs; else the packet REFERENCE into the player's lock-free queue, bounded 20,000). The minimap thread
    drains it every 0.25 s: the chunk keys into the player's streamed set; images kept only inside the keep window and only until encoded.
    A window chunk without a piece that the player's OWN stream sent is read from WorldMapManager.getImageIfInMemory (never generates;
    never for a chunk the stream did not send this player - privacy: the engine cache holds the whole map).
  - Own thread "SkyyHud-Minimap" (single daemon, scheduleWithFixedDelay 0.25 s, every player in its own catch, a watchdog in the 1 s HUD
    tick restarts it): drain, downscale (alpha-weighted, alpha threshold 128, 5-bit colours, any size to min(source, hud.mm.detail) px),
    PNG (indexed <= 256 colours, else RGBA), a 3 ms / hud.mm.tilesPerTick budget shared ROUND-ROBIN (each player's pieces nearest first).
    Shared cache keyed by the piece's CONTENT (CRC32 of palette + packed bits + sizes, + detail), LRU max(4096, players x slots), holding
    pictures only (no MapImage). Each picture goes to a player ONCE per connection (AssetInitialize + AssetPart + AssetFinalize, the
    probe's proven sequence; kept across world changes - P3), at most 6,000 map pictures per connection (then dark fill + one log line).
    The 14 masks (7 sizes x round / square) + 16 arrows go at the first attach of a connection with ONE RequestCommonAssetsRebuild.
  - Look: a ring buffer of w x w AssetImage tiles (w = 2h + 1, slot = floorMod) in a grid Group that pans with ONE Anchor set and re-bases
    only every few chunks; the round (or square) mask on the clip; the ring + a gold north tick; your arrow in 16 headings (engine maths:
    yaw radians, 0 = north, bearing = -yaw); map-marker dots (40, nearest first, kinds by markerImage name) and party dots (8, 1 Hz, rim-
    pinned) inside the grid. Standing still sends nothing; a pan = one Anchor; the arrow only when its heading changes.
  - Settings page (the widget's Settings, kit look): Show, Zoom 64-320 (up to the admin max), Size, Shape, Update speed (capped by the admin
    minimum), Ring, Rotation (info), Party members, Map markers, Other players, Marker size, Ring colour, Party dot colour, BetterMap status.
    Saved per player in the layout line: lines = the marker bits (party 1, markers 2, other players 4; default 3), col = the ring colour, a
    15th field mm = "z160.sr.u500.g1.k1.cdef" written ONLY when not all default (then the 13th is "-" for the default markers and the 14th
    "def"); 0.3.13 reads such a line with every field but the 15th.
  - Server Setup -> Minimap (tools/skyycfg.py, KEEP=10, config.properties keys mm.*; a key missing from an existing file = its default):
    hud.mm.enabled, defaultOn, maxRadius, detail, minInterval, tilesPerTick, partyDots, otherPlayers, disabledWorlds.
  - /skyyhud minimap (opens its settings) | /skyyhud minimap on | off (hytale:Adventurer).
  - Unchanged: every other widget, page, command, permission and file format (except the Online widget's default: tr 8,206, under the
    minimap - it sat exactly beneath it at 8,40).
  - FIX ROUND (critic reports on the first build; these supersede the lines above where they differ):
    - a layout change re-attaches only when the drawn frame changes (size, zoom, shape, ring on / off); otherwise ONE small update (the box
      Anchor, the ring picture, dots, speed, detail) - editor clicks on other widgets send nothing to the minimap;
    - no attach before the world's map stream started (islands: no empty disc); it attaches with the first map packet;
    - the tap runs for every connected player (keys only while the minimap is off, so switching it on later fills from the engine cache);
      its bound counts map pieces (2,048 queued per player; past it a packet is queued as chunk keys only);
    - the join burst's pieces inside the player's window are kept (the position is read for it); chunk (-1,-1) - which the engine's map
      cache cannot hold - keeps the stream's own piece;
    - each session encodes at the detail its tile size needs (16 / 24 / 32 px, up to hud.mm.detail - default now 32); the fastest update
      default is 0.25 s (Smooth works), Smooth / Normal are hidden where the admin's cap is slower;
    - marker changes and fill leftovers wait for the player's update rate (only the first fill goes faster); the arrow alone follows a turn
      at once; rim-pinned party dots are re-pinned at every pan;
    - the 6,000 cap counts map pieces only and tells the player once; the budget grows with the players still filling (3-10 ms, up to 3x
      tilesPerTick, 64 at most);
    - the watchdog never doubles a tick stuck inside the lock (it interrupts + logs it), restarts a dead thread at most 3 times (each logged);
    - a fast reconnect: the new connection gets a NEW session (its own picture list); the old connection's quit no longer drops it.
''')
rep('VERSION = "0.3.13"', 'VERSION = "0.3.14"')

# ---- engine members the minimap uses (API drift fails the build here)
rep('''CMGR = "com.hypixel.hytale.server.core.command.system.CommandManager"
for c, m in ((CMGR, "get"), (CMGR, "resolveCommand"), (CMGR, "handleCommand")):
    B.probe(pool, c, m)
''', '''CMGR = "com.hypixel.hytale.server.core.command.system.CommandManager"
for c, m in ((CMGR, "get"), (CMGR, "resolveCommand"), (CMGR, "handleCommand")):
    B.probe(pool, c, m)
# 0.3.14 minimap: every engine member it uses (API drift fails the build here)
MMT = {
    "PKG": "com.skyy.hud", "PR": PR, "WLD": WLD, "ST": ST, "REF": REF, "UCB": UCB, "UEB": UEB, "PLA": PLA, "UNI": UNI, "MSG": MSG,
    "BT": BT, "EVD": EVD, "ANC": ANC,
    "HUD": HUD, "HM": "com.hypixel.hytale.server.core.entity.entities.player.hud.HudManager",
    "VAL": "com.hypixel.hytale.server.core.ui.Value",
    "MIM": "com.hypixel.hytale.protocol.packets.worldmap.MapImage",
    "UWM": "com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap",
    "CWM": "com.hypixel.hytale.protocol.packets.worldmap.ClearWorldMap",
    "MCH": "com.hypixel.hytale.protocol.packets.worldmap.MapChunk",
    "MMK": "com.hypixel.hytale.protocol.packets.worldmap.MapMarker",
    "CMA": "com.hypixel.hytale.server.core.asset.common.CommonAsset",
    "AINI": "com.hypixel.hytale.protocol.packets.setup.AssetInitialize",
    "APRT": "com.hypixel.hytale.protocol.packets.setup.AssetPart",
    "AFIN": "com.hypixel.hytale.protocol.packets.setup.AssetFinalize",
    "ARB": "com.hypixel.hytale.protocol.packets.setup.RequestCommonAssetsRebuild",
    "TCP": "com.hypixel.hytale.protocol.ToClientPacket",
    "PAD": "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPW": "com.hypixel.hytale.server.core.io.adapter.PlayerPacketWatcher",
    "PF": "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT": "com.hypixel.hytale.protocol.Packet",
    "WMM": "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager",
    "PLM": "com.hypixel.hytale.server.core.plugin.PluginManager",
    "PID": "com.hypixel.hytale.common.plugin.PluginIdentifier",
    "PB": "com.hypixel.hytale.server.core.plugin.PluginBase",
    "ES": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "PCE": "com.hypixel.hytale.server.core.event.events.player.PlayerConnectEvent",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "LOS": "it.unimi.dsi.fastutil.longs.LongOpenHashSet",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "MMKEY": "SkyyHudMinimap", "MMZ": "5",
}
for c, m in ((MMT["HUD"], "show"), (MMT["HUD"], "update"), (MMT["HUD"], "onRemove"), (MMT["HUD"], "build"), (MMT["HM"], "addCustomHud"),
             (MMT["HM"], "removeCustomHud"), (MMT["HM"], "getCustomHud"), (PLA, "getHudManager"), (MMT["CMA"], "hash"),
             (MMT["CMA"], "toPacket"), (MMT["CMA"], "getName"), (MMT["CMA"], "getBlob0"),
             ("com.hypixel.hytale.server.core.io.PacketHandler", "write"), ("com.hypixel.hytale.server.core.io.PacketHandler", "writeNoCache"),
             (PR, "getPacketHandler"), (PR, "getTransform"), (PR, "getHeadRotation"), (PR, "getWorldUuid"), (PR, "isValid"),
             (PR, "getReference"), (MMT["UWM"], "chunks"), (MMT["UWM"], "addedMarkers"), (MMT["UWM"], "removedMarkers"),
             (MMT["MCH"], "chunkX"), (MMT["MCH"], "chunkZ"), (MMT["MCH"], "image"), (MMT["MIM"], "width"), (MMT["MIM"], "height"),
             (MMT["MIM"], "palette"), (MMT["MIM"], "bitsPerIndex"), (MMT["MIM"], "packedIndices"), (MMT["MMK"], "id"),
             (MMT["MMK"], "markerImage"), (MMT["MMK"], "transform"), ("com.hypixel.hytale.protocol.Transform", "position"),
             ("com.hypixel.hytale.protocol.Position", "x"), ("com.hypixel.hytale.protocol.Position", "z"), (WLD, "getWorldMapManager"),
             (WLD, "getName"), (WLD, "execute"), (MMT["WMM"], "getImageIfInMemory"), (MMT["WMM"], "isWorldMapEnabled"),
             (MMT["PAD"], "registerOutbound"), (MMT["PAD"], "deregisterOutbound"), (MMT["PPW"], "accept"), (MMT["PLM"], "get"),
             (MMT["PLM"], "getPlugin"), (MMT["PB"], "isEnabled"), (MMT["PB"], "getManifest"),
             ("com.hypixel.hytale.common.plugin.PluginManifest", "getVersion"), (MMT["PCE"], "getPlayerRef"), (MMT["PDE"], "getPlayerRef"),
             (MMT["ES"], "getWorld"), (ST, "getExternalData"), (ANC, "setLeft"), (ANC, "setTop"), (ANC, "setWidth"), (ANC, "setHeight"),
             (MMT["VAL"], "of"), (UCB, "setObject"), (UCB, "getCommands"), (MMT["LOS"], "add"), (MMT["LOS"], "contains"),
             (MMT["LOS"], "remove"), (UNI, "getPlayer"), ("com.hypixel.hytale.math.vector.Rotation3f", "yaw")):
    B.probe(pool, c, m)
pool.get(MMT["PID"])
''')

# ---- 0.3.14 classes (made early: javassist resolves a type by name once it is in the pool)
rep('''tick = pool.makeClass(PKG + ".TickTask")''', '''tick = pool.makeClass(PKG + ".TickTask")
# 0.3.14 minimap classes (research/Minimap-Widget-Spec.md rev 2)
mmcfg = pool.makeClass(PKG + ".MmCfg")                     # admin settings + the per-player mm field codec (made first: WLayout uses it)
mmpng = pool.makeClass(PKG + ".MmPng")                     # MapImage unpack, alpha-weighted downscale, PNG writer, generated pictures
mmasset = pool.makeClass(PKG + ".MmAsset", pool.get(MMT["CMA"]))   # one runtime picture (keeps its bytes)
mmsess = pool.makeClass(PKG + ".MmSess")                   # one player's minimap
mmhud = pool.makeClass(PKG + ".MmHud", pool.get(HUD))       # the keyed HUD "SkyyHudMinimap"
mmreq = pool.makeClass(PKG + ".MmReq")                     # a request (event / world thread) for the minimap thread
mmmain = pool.makeClass(PKG + ".Minimap")                  # the engine: tick, tap, attach, cache
mmui = pool.makeClass(PKG + ".MmUi")                       # the settings page (kit markup made by the patch)
mmtick = pool.makeClass(PKG + ".MmTick")
mmthr = pool.makeClass(PKG + ".MmThreads")
mmatt = pool.makeClass(PKG + ".MmAttach")
mmdet = pool.makeClass(PKG + ".MmDetach")
mmtap = pool.makeClass(PKG + ".MmTap")
mmcon = pool.makeClass(PKG + ".MmConnect")
mmquit = pool.makeClass(PKG + ".MmQuit")
cmm = pool.makeClass(PKG + ".HudMinimapCmd", pool.get(APC))
cmmon = pool.makeClass(PKG + ".HudMinimapOnCmd", pool.get(APC))
cmmoff = pool.makeClass(PKG + ".HudMinimapOffCmd", pool.get(APC))''')

# ---- the widget list
rep('''IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild", "Skills", "Combat"]''',
    '''IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild", "Skills", "Combat", "Minimap"]''')
rep('''assert (CMB_TP, CMB_ROW, CMB_BAR, CMB_BP) == (3, 20, 6, 8), "Widgets.bodyH (not an f-string) spells the Combat maths out as 3 / 20 / 6 / 8"
''', '''assert (CMB_TP, CMB_ROW, CMB_BAR, CMB_BP) == (3, 20, 6, 8), "Widgets.bodyH (not an f-string) spells the Combat maths out as 3 / 20 / 6 / 8"
# 0.3.14 MINIMAP widget: default ON (admin row hud.mm.defaultOn) top-right under the Zone widget; a 160 x 160 box at 100 % (sizes in 7
# steps, MmCfg.snapScale); lines = its marker bits (party 1, map markers 2, other players 4; default 3)
DEFAULTS["Minimap"] = (True, "tr", 8, 40)
LABELS["Minimap"] = "Minimap"
SIZES["Minimap"] = (160, 160)
MM_DEF_MASK = 3
assert IDS[-1] == "Minimap" and DEFAULTS["Zone"][1:] == ("tr", 8, 8)
# fix round (critic: the Online widget's default tr 8,40 sat exactly under the minimap): Online moves below it (40 + 160 + 6)
assert DEFAULTS["Online"] == (False, "tr", 8, 40)
DEFAULTS["Online"] = (False, "tr", 8, 206)
''')

# ---- MmCfg (fields + the codec) right before WLayout (WLayout.parse / ser call it)
MMCFG_BLOCK = r'''
# ================= 0.3.14 MmCfg: the minimap's admin settings (bound by tools/skyycfg.py) + the per-player "mm" layout field codec =========
for _f in ("public static volatile boolean ENABLED = true;", "public static volatile boolean DEFAULT_ON = true;",
           'public static volatile String MAX_RADIUS = "224";', 'public static volatile String DETAIL = "32";',
           "public static volatile double MIN_INTERVAL = 0.25;", "public static volatile int TILES_PER_TICK = 24;",
           "public static volatile boolean PARTY_DOTS = true;", "public static volatile boolean OTHER_PLAYERS = true;",
           'public static volatile String DISABLED_WORLDS = "";',
           # BetterMap: 0 not checked yet, 1 found + enabled, 2 missing / disabled; its version for the log + the settings line
           "public static volatile int BM = 0;", 'public static volatile String BMV = "";',
           "public static final int[] RADII = new int[] { 64, 96, 128, 160, 224, 320 };",
           "public static final String[] PKEYS = %s;" % jarr([p[0] for p in PAL[:TEXT_N]])):
    mmcfg.addField(CtField.make(_f, mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static int num(String v) {
  if (v == null) return -1;
  try { return Integer.parseInt(v.trim()); } catch (Throwable t) { return -1; }
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static boolean isRadius(int r) {
  for (int i = 0; i < RADII.length; i++) if (RADII[i] == r) return true;
  return false;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static int maxRadius() {
  int v = num(MAX_RADIUS);
  return isRadius(v) ? v : 224;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static int detail() {
  int v = num(DETAIL);
  return (v == 16 || v == 24) ? v : 32;
}""", mmcfg))
# fix round (critic: blurry at 16 px): the detail a session needs = the smallest of 16 / 24 / 32 px that is at least its tile size on
# screen (t), never above the admin's sharpest (mm.detail)
mmcfg.addMethod(CtNewMethod.make("""
public static int detFor(int t) {
  int d = t <= 16 ? 16 : (t <= 24 ? 24 : 32);
  int m = detail();
  return d > m ? m : d;
}""", mmcfg))
# seconds for a hint: 250 -> 0.25, 500 -> 0.5, 1040 -> 1.04, 1100 -> 1.1, 2000 -> 2 (fix round: no zero padding before)
mmcfg.addMethod(CtNewMethod.make("""
public static String secText(long ms) {
  long w = ms / 1000L;
  long f = ms % 1000L;
  if (f < 0L) f = -f;
  String s = String.valueOf(w);
  if (f == 0L) return s;
  String d = String.valueOf(1000L + f).substring(1);
  while (d.endsWith("0")) d = d.substring(0, d.length() - 1);
  return s + "." + d;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static long minIntervalMs() {
  double d = MIN_INTERVAL;
  if (Double.isNaN(d) || Double.isInfinite(d)) d = 0.25;
  long ms = Math.round(d * 1000.0);
  if (ms < 250L) ms = 250L;
  if (ms > 2000L) ms = 2000L;
  return ms;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static int tilesPerTick() {
  int v = TILES_PER_TICK;
  return v < 1 ? 1 : (v > 64 ? 64 : v);
}""", mmcfg))
# comma list, case-insensitive; "name*" = every world whose name starts with name
mmcfg.addMethod(CtNewMethod.make("""
public static boolean worldDisabled(String n) {
  String l = DISABLED_WORLDS;
  if (n == null || l == null || l.trim().length() == 0) return false;
  String w = n.trim().toLowerCase(java.util.Locale.ROOT);
  String[] p = l.split(",");
  for (int i = 0; i < p.length; i++) {
    String e = p[i].trim().toLowerCase(java.util.Locale.ROOT);
    if (e.length() == 0) continue;
    if (e.endsWith("*")) { if (w.startsWith(e.substring(0, e.length() - 1))) return true; }
    else if (w.equals(e)) return true;
  }
  return false;
}""", mmcfg))
# the 7 sizes (50-200 % in 25s): the nearest step, a tie goes up
mmcfg.addMethod(CtNewMethod.make("""
public static int snapScale(int sc) {
  int v = sc < 50 ? 50 : (sc > 200 ? 200 : sc);
  int k = (v - 50 + 12) / 25;
  return 50 + 25 * k;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static boolean pkey(String k) {
  if (k == null) return false;
  for (int i = 0; i < PKEYS.length; i++) if (PKEYS[i].equals(k)) return true;
  return false;
}""", mmcfg))
# mm = "z<radius>.s<r|q>.u<250|500|1000>.g<0|1>.k<0-2>.c<palette key>" -> { zoom, shape (0 round, 1 square), update ms, ring, marker size };
# a missing or bad part = its default (one by one)
mmcfg.addMethod(CtNewMethod.make("""
public static int[] dec(String mm) {
  int[] v = new int[] { 160, 0, 500, 1, 1 };
  if (mm == null || mm.length() == 0) return v;
  String[] p = mm.split("\\\\.");
  for (int i = 0; i < p.length; i++) {
    String e = p[i].trim();
    if (e.length() < 2) continue;
    char c = e.charAt(0);
    String r = e.substring(1);
    if (c == 'z') { int z = num(r); if (isRadius(z)) v[0] = z; }
    else if (c == 's') { if (r.equals("r")) v[1] = 0; else if (r.equals("q")) v[1] = 1; }
    else if (c == 'u') { int u = num(r); if (u == 250 || u == 500 || u == 1000) v[2] = u; }
    else if (c == 'g') { if (r.equals("0")) v[3] = 0; else if (r.equals("1")) v[3] = 1; }
    else if (c == 'k') { int k = num(r); if (k >= 0 && k <= 2) v[4] = k; }
  }
  return v;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static String pcol(String mm) {
  if (mm == null || mm.length() == 0) return "def";
  String[] p = mm.split("\\\\.");
  for (int i = 0; i < p.length; i++) {
    String e = p[i].trim();
    if (e.length() >= 2 && e.charAt(0) == 'c' && pkey(e.substring(1))) return e.substring(1);
  }
  return "def";
}""", mmcfg))
# canonical text, "" when everything is default (then ser() writes the 0.3.13 line byte for byte)
mmcfg.addMethod(CtNewMethod.make("""
public static String enc(int[] v, String pc) {
  String c = pkey(pc) ? pc : "def";
  if (v[0] == 160 && v[1] == 0 && v[2] == 500 && v[3] == 1 && v[4] == 1 && "def".equals(c)) return "";
  return "z" + v[0] + ".s" + (v[1] == 1 ? "q" : "r") + ".u" + v[2] + ".g" + v[3] + ".k" + v[4] + ".c" + c;
}""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static String clean(String mm) { return enc(dec(mm), pcol(mm)); }""", mmcfg))
mmcfg.addMethod(CtNewMethod.make("""
public static boolean bool(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("true") || t.equals("1") || t.equals("on") || t.equals("yes")) return true;
  if (t.equals("false") || t.equals("0") || t.equals("off") || t.equals("no")) return false;
  return d;
}""", mmcfg))
# config.properties (HudCfg.load): a missing key keeps its default; a bad value keeps the default too (the kit refuses it in game)
mmcfg.addMethod(CtNewMethod.make("""
public static void loadFrom(java.util.Properties p) {
  if (p == null) return;
  ENABLED = bool(p.getProperty("mm.enabled"), true);
  DEFAULT_ON = bool(p.getProperty("mm.defaultOn"), true);
  String r = p.getProperty("mm.maxRadius");
  MAX_RADIUS = (r != null && isRadius(num(r))) ? r.trim() : "224";
  String d = p.getProperty("mm.detail");
  DETAIL = (d != null && (num(d) == 16 || num(d) == 24 || num(d) == 32)) ? d.trim() : "32";
  String mi = p.getProperty("mm.minInterval");
  double x = 0.25;
  try { if (mi != null) x = Double.parseDouble(mi.trim()); } catch (Throwable t) { x = 0.25; }
  if (Double.isNaN(x) || x < 0.25 || x > 2.0) x = 0.25;
  MIN_INTERVAL = x;
  String tp = p.getProperty("mm.tilesPerTick");
  int n = tp == null ? 24 : num(tp);
  TILES_PER_TICK = (n >= 1 && n <= 64) ? n : 24;
  PARTY_DOTS = bool(p.getProperty("mm.partyDots"), true);
  OTHER_PLAYERS = bool(p.getProperty("mm.otherPlayers"), true);
  String dw = p.getProperty("mm.disabledWorlds");
  DISABLED_WORLDS = dw == null ? "" : dw.trim();
}""", mmcfg))
'''
rep('''# ================= WLayout =================
''', MMCFG_BLOCK + '''
# ================= WLayout =================
''')

# ---- WLayout: the mm field (null = a widget without it; "" = the Minimap's defaults)
rep('''wl.addField(CtField.make("public String ocol;", wl))
''', '''wl.addField(CtField.make("public String ocol;", wl))
# 0.3.14: mm = the Minimap's own settings (MmCfg codec; null for every other widget, "" = all default), the layout line's 15th field
wl.addField(CtField.make("public String mm;", wl))
''')
rep('''  this.ocol = "def";
}""", wl))''', '''  this.ocol = "def";
  this.mm = null;
}""", wl))''')
rep('''wl.addMethod(CtNewMethod.make("""
public String ser() {
  boolean lx = ldef >= 0 && lines > 0 && lines != ldef;
  boolean ox = ocol != null && !"def".equals(ocol);
  String s = (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0");
  if (styleDefault() && opt && !lx && !ox) return s;
  s = s + "," + col + "," + (bold ? "1" : "0") + "," + (ital ? "1" : "0") + "," + (glow ? "1" : "0") + "," + gcol;
  if (!lx && !ox) {
    if (opt) return s;
    return s + ",0";
  }
  s = s + "," + (opt ? "1" : "0") + "," + (lx ? String.valueOf(lines) : "-");
  if (!ox) return s;
  return s + "," + ocol;
}""", wl))''', '''wl.addMethod(CtNewMethod.make("""
public String ser() {
  boolean lx = ldef >= 0 && lines > 0 && lines != ldef;
  boolean ox = ocol != null && !"def".equals(ocol);
  boolean mx = mm != null && mm.length() > 0;
  String s = (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0");
  if (styleDefault() && opt && !lx && !ox && !mx) return s;
  s = s + "," + col + "," + (bold ? "1" : "0") + "," + (ital ? "1" : "0") + "," + (glow ? "1" : "0") + "," + gcol;
  if (!lx && !ox && !mx) {
    if (opt) return s;
    return s + ",0";
  }
  s = s + "," + (opt ? "1" : "0") + "," + (lx ? String.valueOf(lines) : "-");
  if (!ox && !mx) return s;
  s = s + "," + (ocol == null ? "def" : ocol);
  if (!mx) return s;
  return s + "," + mm;
}""", wl))''')
rep('''    if (def != null) {{ w.bw = def.bw; w.bh = def.bh; w.ldef = def.ldef; w.lines = def.ldef; }}''',
    '''    if (def != null) {{ w.bw = def.bw; w.bh = def.bh; w.ldef = def.ldef; w.lines = def.ldef; w.mm = def.mm; }}''')
rep('''    if (p.length > 13) {{ String o = p[13].trim(); int oi = palIdx(o); if (oi >= 0 && oi < TEXT_N) w.ocol = o; }}''',
    '''    if (p.length > 13) {{ String o = p[13].trim(); int oi = palIdx(o); if (oi >= 0 && oi < TEXT_N) w.ocol = o; }}
    if (p.length > 14) w.mm = {PKG}.MmCfg.clean(p[14].trim());''')

# ---- Widgets.def: the Minimap's built-in layout (lines = marker bits, mm = "", en = the admin's defaultOn)
rep('''        extra = (" w.ldef = %d; w.lines = %d;" % (SKILL_DEF_MASK, SKILL_DEF_MASK)) if i == "Skills" else ""''',
    '''        extra = (" w.ldef = %d; w.lines = %d;" % (SKILL_DEF_MASK, SKILL_DEF_MASK)) if i == "Skills" else ""
        if i == "Minimap":
            extra = ' w.ldef = %d; w.lines = %d; w.mm = ""; w.en = %s.MmCfg.DEFAULT_ON;' % (MM_DEF_MASK, MM_DEF_MASK, PKG)''')
# ---- Widgets.text: the editor's stand-in text for the Minimap box
rep('''public static String text(String id, {PR} pr, long joinMs) {{
  try {{
    if (multi(id)) {{''', '''public static String text(String id, {PR} pr, long joinMs) {{
  try {{
    if ("Minimap".equals(id)) return {PKG}.MmCfg.BM == 2 ? "Needs BetterMap" : "Minimap";
    if (multi(id)) {{''')
# ---- the drawn width of the Minimap = its box
rep('''public static int viewW(String id, {PKG}.WLayout l, {PR} pr, long joinMs) {{
  if (multi(id)) return''', '''public static int viewW(String id, {PKG}.WLayout l, {PR} pr, long joinMs) {{
  if ("Minimap".equals(id)) return l.bw * l.scale / 100;
  if (multi(id)) return''')
# ---- clampToScreen snaps a Minimap size to its 7 steps (mm != null marks the Minimap layout)
rep('''public static void clampToScreen({PKG}.WLayout l) {{
  int h = hMax(l);''', '''public static void clampToScreen({PKG}.WLayout l) {{
  if (l.mm != null) l.scale = {PKG}.MmCfg.snapScale(l.scale);
  int h = hMax(l);''')
# ---- importCode keeps mm only for the Minimap
rep('''    l.ldef = dd.ldef; if (dd.ldef < 0) l.lines = -1; else if (l.lines <= 0) l.lines = dd.ldef;''',
    '''    l.ldef = dd.ldef; if (dd.ldef < 0) l.lines = -1; else if (l.lines <= 0) l.lines = dd.ldef;
    if (dd.mm == null) l.mm = null; else if (l.mm == null) l.mm = "";''')

# ---- config: the Minimap rows + the default file text + HudCfg.load reads mm.*
rep('''    "defaultLayout=",
    "",
])''', '''    "defaultLayout=",
    "",
    "# Minimap (needs BetterMap). Change these in game: SkyWynn Menu -> Server Setup -> Minimap. A missing key = its default.",
    "# mm.enabled = the minimap widget for everyone; mm.defaultOn = new players see it; mm.maxRadius = largest zoom in blocks (64 96 128",
    "# 160 224 320); mm.detail = sharpest map detail in px per chunk (16 24 32; each player gets what their zoom needs, up to this);",
    "# mm.minInterval = fastest update in seconds (0.25-2); mm.tilesPerTick = map pieces shrunk per 0.25 s for one filling player",
    "# (1-64; up to 3x while several fill); mm.partyDots / mm.otherPlayers = dots allowed; mm.disabledWorlds = comma",
    "# list of world names without a minimap (name* = every world starting with name).",
    "mm.enabled=true",
    "mm.defaultOn=true",
    "mm.maxRadius=224",
    "mm.detail=32",
    "mm.minInterval=0.25",
    "mm.tilesPerTick=24",
    "mm.partyDots=true",
    "mm.otherPlayers=true",
    "mm.disabledWorlds=",
    "",
])''')
rep('''      String s = p.getProperty("defaultLayout");
      if (s != null) v = s.trim();
    }''', '''      String s = p.getProperty("defaultLayout");
      if (s != null) v = s.trim();
      com.skyy.hud.MmCfg.loadFrom(p);
    }''')
rep('''HUD_CFG_CATS = [("hud", "HUD")]''', '''HUD_CFG_CATS = [("hud", "HUD"), ("mm", "Minimap")]''')
rep('''    ("hud.editor", "HUD editor", "hud", "link", "", "", "", "skyyhud", "", "",
     "Opens your own HUD editor: set the look up there, then press Use my layout above.", ""),
]''', '''    ("hud.editor", "HUD editor", "hud", "link", "", "", "", "skyyhud", "", "",
     "Opens your own HUD editor: set the look up there, then press Use my layout above.", ""),
    # 0.3.14 Minimap (research/Minimap-Widget-Spec.md section 2): live rows; the ones that change what is drawn re-lay every minimap out
    ("hud.mm.enabled", "Minimap widget", "mm", "bool", "true", "", "", "", "", "live",
     "Off = no minimap for anyone. It also needs BetterMap installed.",
     "field:MmCfg.ENABLED@config.properties:mm.enabled;after=Minimap.cfgChanged"),
    ("hud.mm.defaultOn", "New players see the minimap", "mm", "bool", "true", "", "", "", "", "live",
     "Only for players with no saved HUD layout yet; anyone who changed their HUD keeps their choice.",
     "field:MmCfg.DEFAULT_ON@config.properties:mm.defaultOn"),
    ("hud.mm.maxRadius", "Largest zoom (blocks)", "mm", "choice", "224", "", "",
     "64|64 blocks,96|96 blocks,128|128 blocks,160|160 blocks,224|224 blocks,320|320 blocks", "", "live",
     "320 shows up to 529 map pieces at once - client cost not tested yet.",
     "field:MmCfg.MAX_RADIUS@config.properties:mm.maxRadius;after=Minimap.cfgChanged"),
    ("hud.mm.detail", "Sharpest map detail (px per chunk)", "mm", "choice", "32", "", "", "16|16 px,24|24 px,32|32 px", "", "live",
     "Each player gets the detail their zoom and size need, up to this. Lower = less data, blurrier.",
     "field:MmCfg.DETAIL@config.properties:mm.detail;after=Minimap.cfgChanged"),
    ("hud.mm.minInterval", "Fastest update", "mm", "dec", "0.25", "0.25", "2", "", "s", "live",
     "Caps the players' Update speed (Smooth 0.25 s, Normal 0.5, Saver 1); faster ones are hidden.",
     "field:MmCfg.MIN_INTERVAL@config.properties:mm.minInterval;after=Minimap.cfgChanged"),
    ("hud.mm.tilesPerTick", "Map pieces shrunk per 0.25 s", "mm", "int", "24", "1", "64", "", "", "live",
     "For one filling player; up to 3x (max 64) while several fill. The thread stops after 3-10 ms.",
     "field:MmCfg.TILES_PER_TICK@config.properties:mm.tilesPerTick"),
    ("hud.mm.partyDots", "Party dots allowed", "mm", "bool", "true", "", "", "", "", "live",
     "Players still choose in their minimap settings.",
     "field:MmCfg.PARTY_DOTS@config.properties:mm.partyDots;after=Minimap.cfgChanged"),
    ("hud.mm.otherPlayers", "Other-player dots allowed", "mm", "bool", "true", "", "", "", "", "live",
     "Players still choose (off by default).",
     "field:MmCfg.OTHER_PLAYERS@config.properties:mm.otherPlayers;after=Minimap.cfgChanged"),
    ("hud.mm.disabledWorlds", "Worlds without minimap", "mm", "text", "", "", "500", "", "", "live",
     "Comma list of world names; name* = every world starting with name.",
     "field:MmCfg.DISABLED_WORLDS@config.properties:mm.disabledWorlds;after=Minimap.cfgChanged"),
]''')

# =================================================================================================== the minimap engine (before HudMain)
MM_BLOCK = r'''
# ================= 0.3.14 MINIMAP (research/Minimap-Widget-Spec.md rev 2) =================
# Java with @TOKEN@ placeholders (MMT): the probe's build pattern. Order: pure helpers -> data classes -> the HUD -> the engine -> the page.
import re as _re
_MMTOK = _re.compile(r"@([A-Z]{2,8})@")


def mmj(src):
    def _r(m):
        k = m.group(1)
        if k not in MMT:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return MMT[k]
    return _MMTOK.sub(_r, src)


def MMM(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(mmj(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, mmj(src)[:3000]))


def MMF(cls, src):
    try:
        cls.addField(CtField.make(mmj(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, mmj(src)[:600]))


def MMC(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(mmj(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, mmj(src)[:1500]))


def _rgba(h, a=255):
    v = (int(h[1:7], 16) << 8) | a
    return v - (1 << 32) if v >= (1 << 31) else v


MM_KIT_COLORS = @@KITCOL@@        # tools/skyyui.py COLOR (copied by tools/hud_0_3_14_patch.py)


def _kit_rgba(name, alpha=None):
    import re as _r2
    c = MM_KIT_COLORS[name]
    m = _r2.fullmatch(r"#([0-9a-fA-F]{6})(?:\(([0-9.]+)\))?", c)
    a = alpha if alpha is not None else (int(round(float(m.group(2)) * 255)) if m.group(2) else 255)
    return _rgba("#" + m.group(1), a)


MM_PART = 2621440                 # CommonAssetModule.sendAsset: ArrayUtil.split(blob, 2621440)
MM_CAP = 6000                     # map pieces (tiles) per connection (the client keeps them all - U11); generated pictures not counted
MM_BUDGET_NS = 3000000            # 3 ms of encoding per 0.25 s tick (critic C13) ...
MM_BUDGET_STEP_NS = 1000000       # ... + 1 ms per extra player still filling (fix round: 10 players filled at 8 pieces / s each) ...
MM_BUDGET_MAX_NS = 10000000       # ... 10 ms at most
MM_QMAX = 20000                   # packets queued per player between two drains (the probe's bound)
MM_QCHUNKS = 2048                 # map pieces (images) queued per player; past it a packet is queued as its chunk KEYS only (fix round:
                                  # a stalled thread held up to 20,000 packets of ~11 KB pieces; the engine cache serves those keys later)
MM_TICK_MS = 250
MM_STREAM_MS = 15000              # no UpdateWorldMap this long after an attach = no map here (hidden)
MM_MARKERS, MM_PARTY = 40, 8
MM_MAXW = 23                      # the widest window (529 slots: 320 px at zoom 320)
MM_ASSET_DIR = "UI/SkyyHud/mm/"   # an AssetImage AssetPath = the full common asset name (probe P1 / P2)
MM_MASK_DIR, MM_MASK_PREFIX = "UI/Custom/", "SkyyHudMmMask-"   # a MaskTexturePath resolves under UI/Custom/ (probe P2)
MMT.update({"QPART": str(MM_PART), "QCAP": str(MM_CAP), "QBUDGET": str(MM_BUDGET_NS), "QMAX": str(MM_QMAX), "QTICK": str(MM_TICK_MS),
            "QBSTEP": str(MM_BUDGET_STEP_NS), "QBMAX": str(MM_BUDGET_MAX_NS), "QCHUNKS": str(MM_QCHUNKS),
            "QSTREAM": str(MM_STREAM_MS), "QMK": str(MM_MARKERS), "QPT": str(MM_PARTY), "QMAXW": str(MM_MAXW), "QADIR": MM_ASSET_DIR,
            "QMDIR": MM_MASK_DIR, "QMPRE": MM_MASK_PREFIX, "QMLEN": str(len(MM_MASK_DIR))})
# kit colours (tools/skyyui.py COLOR, copied by the patch): the ring edge, the north tick, the marker kinds, the arrow
MMT.update({"CEDGE": str(_kit_rgba("darkBlock", 200)), "CTICK": str(_kit_rgba("gold")), "CARROW": str(_kit_rgba("white")),
            "COUT": str(_kit_rgba("darkBlock", 230)), "CWAY": str(_kit_rgba("gold")), "CDEATH": str(_kit_rgba("error")),
            "CHOME": str(_kit_rgba("success")), "CPLAYER": str(_kit_rgba("info")), "CPARTY": str(_kit_rgba("progressGreen")),
            "CRING": str(_kit_rgba("title"))})

# ---------------------------------------------------------------- MmPng (pure): unpack, downscale, PNG, generated pictures
MMM(mmpng, r"""
public static void put32(java.io.ByteArrayOutputStream o, int v) {
  o.write((v >>> 24) & 255);
  o.write((v >>> 16) & 255);
  o.write((v >>> 8) & 255);
  o.write(v & 255);
}""")
MMM(mmpng, r"""
public static void chunk(java.io.ByteArrayOutputStream o, String type, byte[] data) {
  byte[] t = new byte[4];
  for (int i = 0; i < 4; i++) t[i] = (byte) type.charAt(i);
  put32(o, data.length);
  o.write(t, 0, 4);
  o.write(data, 0, data.length);
  java.util.zip.CRC32 c = new java.util.zip.CRC32();
  c.update(t, 0, 4);
  c.update(data, 0, data.length);
  put32(o, (int) c.getValue());
}""")
MMM(mmpng, r"""
public static byte[] zlib(byte[] raw) {
  java.util.zip.Deflater d = new java.util.zip.Deflater(9);
  byte[] out = null;
  try {
    d.setInput(raw, 0, raw.length);
    d.finish();
    java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream(raw.length / 4 + 64);
    byte[] buf = new byte[4096];
    int guard = 0;
    while (!d.finished() && guard < 100000) {
      int n = d.deflate(buf, 0, buf.length);
      if (n > 0) o.write(buf, 0, n);
      guard = guard + 1;
    }
    if (d.finished()) out = o.toByteArray();
  } catch (Throwable t) { out = null; }
  try { d.end(); } catch (Throwable t) { }
  return out;
}""")
MMM(mmpng, r"""
public static byte[] png(int w, int h, int depth, int ctype, byte[] plte, byte[] trns, byte[] raw) {
  byte[] z = zlib(raw);
  if (z == null) return null;
  java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream(z.length + 160);
  o.write(137); o.write(80); o.write(78); o.write(71); o.write(13); o.write(10); o.write(26); o.write(10);
  byte[] ih = new byte[13];
  ih[0] = (byte) (w >>> 24); ih[1] = (byte) (w >>> 16); ih[2] = (byte) (w >>> 8); ih[3] = (byte) w;
  ih[4] = (byte) (h >>> 24); ih[5] = (byte) (h >>> 16); ih[6] = (byte) (h >>> 8); ih[7] = (byte) h;
  ih[8] = (byte) depth;
  ih[9] = (byte) ctype;
  chunk(o, "IHDR", ih);
  if (plte != null) chunk(o, "PLTE", plte);
  if (trns != null) chunk(o, "tRNS", trns);
  chunk(o, "IDAT", z);
  chunk(o, "IEND", new byte[0]);
  return o.toByteArray();
}""")
# the engine's BitFieldArr layout (probe MapPng.unpack): value i in bits [i * bits, i * bits + bits), LSB first
MMM(mmpng, r"""
public static int[] unpack(byte[] packed, int bits, int count) {
  int[] out = new int[count];
  if (bits <= 0 || packed == null) return out;
  for (int i = 0; i < count; i++) {
    long bit = (long) i * (long) bits;
    int v = 0;
    int got = 0;
    while (got < bits) {
      long p = bit + (long) got;
      int bi = (int) (p >> 3);
      int off = (int) (p & 7L);
      int take = 8 - off;
      if (take > bits - got) take = bits - got;
      int b = bi < packed.length ? (packed[bi] & 255) : 0;
      v = v | (((b >>> off) & ((1 << take) - 1)) << got);
      got = got + take;
    }
    out[i] = v;
  }
  return out;
}""")
# RGBA pixels (0xRRGGBBAA, row 0 = north) -> PNG: an indexed PNG (bit depth 1 / 2 / 4 / 8, PLTE + tRNS) up to 256 colours, else RGBA
MMM(mmpng, r"""
public static byte[] encode(int w, int h, int[] px) {
  if (w < 1 || h < 1 || px == null || px.length < w * h) return null;
  java.util.HashMap pi = new java.util.HashMap();
  int[] pal = new int[256];
  int n = 0;
  int[] idx = new int[w * h];
  boolean many = false;
  for (int i = 0; i < w * h; i++) {
    Integer c = Integer.valueOf(px[i]);
    Object o = pi.get(c);
    if (o == null) {
      if (n >= 256) { many = true; break; }
      pal[n] = px[i];
      pi.put(c, Integer.valueOf(n));
      idx[i] = n;
      n = n + 1;
    } else idx[i] = ((Integer) o).intValue();
  }
  if (many) {
    int row = 1 + w * 4;
    byte[] raw = new byte[h * row];
    for (int y = 0; y < h; y++) {
      for (int x = 0; x < w; x++) {
        int c = px[y * w + x];
        int p = y * row + 1 + x * 4;
        raw[p] = (byte) (c >>> 24);
        raw[p + 1] = (byte) (c >>> 16);
        raw[p + 2] = (byte) (c >>> 8);
        raw[p + 3] = (byte) c;
      }
    }
    return png(w, h, 8, 6, null, null, raw);
  }
  int depth = n <= 2 ? 1 : (n <= 4 ? 2 : (n <= 16 ? 4 : 8));
  int rb = (w * depth + 7) / 8;
  byte[] raw = new byte[h * (rb + 1)];
  for (int y = 0; y < h; y++) {
    int base = y * (rb + 1);
    for (int x = 0; x < w; x++) {
      int v = idx[y * w + x];
      int bit = x * depth;
      int bi = base + 1 + (bit >> 3);
      int sh = 8 - depth - (bit & 7);
      raw[bi] = (byte) (raw[bi] | (v << sh));
    }
  }
  byte[] plte = new byte[n * 3];
  int last = -1;
  for (int k = 0; k < n; k++) {
    int c = pal[k];
    plte[k * 3] = (byte) (c >>> 24);
    plte[k * 3 + 1] = (byte) (c >>> 16);
    plte[k * 3 + 2] = (byte) (c >>> 8);
    if ((c & 255) != 255) last = k;
  }
  byte[] trns = null;
  if (last >= 0) {
    trns = new byte[last + 1];
    for (int k = 0; k <= last; k++) trns[k] = (byte) (pal[k] & 255);
  }
  return png(w, h, depth, 3, plte, trns, raw);
}""")
MMM(mmpng, r"""
public static int q5(int v) {
  int x = v < 0 ? 0 : (v > 255 ? 255 : v);
  int v5 = (x * 31 + 127) / 255;
  return (v5 << 3) | (v5 >> 2);
}""")
MMM(mmpng, r"""
public static int target(int src, int detail) { return src < detail ? src : detail; }""")
# a MapImage -> its dw x dh RGBA pixels: each target pixel averages its source block (integer edges x * src / dst, any ratio)
# ALPHA-WEIGHTED (premultiplied) with an alpha threshold (>= 128 opaque, else fully transparent) and 5-bit colours; null = a MapImage this
# encoder refuses (sizes 1-512, bits 1-16, enough packed bytes, every index inside the palette)
MMM(mmpng, r"""
public static int[] down(@MIM@ m, int detail) {
  if (m == null) return null;
  int w = m.width;
  int h = m.height;
  int[] pal = m.palette;
  byte[] packed = m.packedIndices;
  int bits = m.bitsPerIndex & 255;
  if (w < 1 || h < 1 || w > 512 || h > 512 || detail < 1) return null;
  if (pal == null || pal.length < 1 || bits < 1 || bits > 16 || packed == null) return null;
  long need = ((long) w * (long) h * (long) bits + 7L) / 8L;
  if ((long) packed.length < need) return null;
  int[] idx = unpack(packed, bits, w * h);
  for (int i = 0; i < idx.length; i++) if (idx[i] >= pal.length) return null;
  int dw = target(w, detail);
  int dh = w == h ? dw : Math.max(1, h * dw / w);
  int[] out = new int[dw * dh];
  for (int ty = 0; ty < dh; ty++) {
    int y0 = ty * h / dh;
    int y1 = (ty + 1) * h / dh;
    if (y1 <= y0) y1 = y0 + 1;
    for (int tx = 0; tx < dw; tx++) {
      int x0 = tx * w / dw;
      int x1 = (tx + 1) * w / dw;
      if (x1 <= x0) x1 = x0 + 1;
      long sa = 0L;
      long sr = 0L;
      long sg = 0L;
      long sb = 0L;
      int n = 0;
      for (int y = y0; y < y1; y++) {
        for (int x = x0; x < x1; x++) {
          int c = pal[idx[y * w + x]];
          int a = c & 255;
          sa = sa + (long) a;
          sr = sr + (long) ((c >>> 24) & 255) * (long) a;
          sg = sg + (long) ((c >>> 16) & 255) * (long) a;
          sb = sb + (long) ((c >>> 8) & 255) * (long) a;
          n = n + 1;
        }
      }
      long avgA = (sa + (long) (n / 2)) / (long) n;
      if (avgA < 128L || sa == 0L) { out[ty * dw + tx] = 0; continue; }
      int r = (int) ((sr + sa / 2L) / sa);
      int g = (int) ((sg + sa / 2L) / sa);
      int b = (int) ((sb + sa / 2L) / sa);
      out[ty * dw + tx] = (q5(r) << 24) | (q5(g) << 16) | (q5(b) << 8) | 255;
    }
  }
  return out;
}""")
MMM(mmpng, r"""
public static byte[] tilePng(@MIM@ m, int detail) {
  int[] px = down(m, detail);
  if (px == null) return null;
  int dw = target(m.width, detail);
  int dh = m.width == m.height ? dw : Math.max(1, m.height * dw / m.width);
  return encode(dw, dh, px);
}""")
# the generated pictures (integer geometry, doubled grid: pixel centre 2x + 1)
MMM(mmpng, r"""
public static int[] mask(int d, int shape) {
  int[] px = new int[d * d];
  long r2 = (long) d * (long) d;
  for (int y = 0; y < d; y++) {
    for (int x = 0; x < d; x++) {
      long dx = (long) (2 * x + 1 - d);
      long dy = (long) (2 * y + 1 - d);
      px[y * d + x] = (shape == 1 || dx * dx + dy * dy <= r2) ? -1 : 0;
    }
  }
  return px;
}""")
# the ring: a band rw px wide at the edge (round: between radius S/2 - rw and S/2; square: the frame), 1 px dark edges, a gold north tick
MMM(mmpng, r"""
public static int[] ring(int S, int rw, int shape, int col) {
  int[] px = new int[S * S];
  long ro = (long) S;
  long ri = (long) (S - 2 * rw);
  long ro2 = ro * ro;
  long ri2 = ri * ri;
  long eo2 = (ro - 2L) * (ro - 2L);
  long ei2 = (ri + 2L) * (ri + 2L);
  for (int y = 0; y < S; y++) {
    for (int x = 0; x < S; x++) {
      int dx = 2 * x + 1 - S;
      int dy = 2 * y + 1 - S;
      int v = 0;
      boolean band = false;
      boolean edge = false;
      if (shape == 1) {
        int e = Math.min(Math.min(x, y), Math.min(S - 1 - x, S - 1 - y));
        band = e < rw;
        edge = e == 0 || e == rw - 1;
      } else {
        long r2 = (long) dx * (long) dx + (long) dy * (long) dy;
        band = r2 < ro2 && r2 >= ri2;
        edge = r2 >= eo2 || r2 < ei2;
      }
      if (band) {
        v = edge ? @CEDGE@ : col;
        int ax = dx < 0 ? -dx : dx;
        if (dy < 0 && ax <= 2 * rw && !edge) v = @CTICK@;
      }
      px[y * S + x] = v;
    }
  }
  return px;
}""")
MMM(mmpng, r"""
public static boolean inTri(double ax, double ay, double bx, double by, double cx, double cy, double px, double py) {
  double d1 = (bx - ax) * (py - ay) - (by - ay) * (px - ax);
  double d2 = (cx - bx) * (py - by) - (cy - by) * (px - bx);
  double d3 = (ax - cx) * (py - cy) - (ay - cy) * (px - cx);
  boolean neg = d1 < 0.0 || d2 < 0.0 || d3 < 0.0;
  boolean pos = d1 > 0.0 || d2 > 0.0 || d3 > 0.0;
  return !(neg && pos);
}""")
# arrow k (0 = N, then CLOCKWISE in 22.5 degree steps - the heading index): the north arrow (tip, right foot, notch, left foot on a 64 x 64
# doubled grid) turned k x 22.5 degrees clockwise on screen (y down); 32 x 32 px, a white arrow with a dark outline
MMM(mmpng, r"""
public static int[] arrow(int k) {
  int s = 32;
  double a = Math.toRadians(22.5 * (double) k);
  double ca = Math.cos(a);
  double sa = Math.sin(a);
  double[] vx = new double[] { 0.0, 20.0, 0.0, -20.0 };
  double[] vy = new double[] { -28.0, 26.0, 12.0, 26.0 };
  double[] qx = new double[4];
  double[] qy = new double[4];
  for (int i = 0; i < 4; i++) {
    qx[i] = 32.0 + vx[i] * ca - vy[i] * sa;
    qy[i] = 32.0 + vx[i] * sa + vy[i] * ca;
  }
  int[] px = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      double cx = (double) (2 * x + 1);
      double cy = (double) (2 * y + 1);
      if (inTri(qx[0], qy[0], qx[1], qy[1], qx[2], qy[2], cx, cy) || inTri(qx[0], qy[0], qx[2], qy[2], qx[3], qy[3], cx, cy)) px[y * s + x] = @CARROW@;
    }
  }
  int[] out = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      int v = px[y * s + x];
      if (v == 0) {
        boolean e = (x > 0 && px[y * s + x - 1] != 0) || (x + 1 < s && px[y * s + x + 1] != 0) || (y > 0 && px[(y - 1) * s + x] != 0) || (y + 1 < s && px[(y + 1) * s + x] != 0);
        if (e) v = @COUT@;
      }
      out[y * s + x] = v;
    }
  }
  return out;
}""")
MMM(mmpng, r"""
public static int[] dot(int col) {
  int s = 16;
  int[] px = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      int dx = 2 * x + 1 - s;
      int dy = 2 * y + 1 - s;
      int r2 = dx * dx + dy * dy;
      px[y * s + x] = r2 <= 11 * 11 ? col : (r2 <= 15 * 15 ? @COUT@ : 0);
    }
  }
  return px;
}""")
MMM(mmpng, r"""
public static int rgbaOf(String hex) {
  try {
    if (hex != null && hex.length() >= 7 && hex.charAt(0) == '#') return (Integer.parseInt(hex.substring(1, 7), 16) << 8) | 255;
  } catch (Throwable t) { }
  return @CRING@;
}""")

# ---------------------------------------------------------------- MmAsset: one runtime picture (CommonAsset keeps only a WeakReference)
MMF(mmasset, "public byte[] bytes;")
MMC(mmasset, "public MmAsset(String name, String hash, byte[] b) { super(name, hash, b); this.bytes = b; }")
MMM(mmasset, "protected java.util.concurrent.CompletableFuture getBlob0() { return java.util.concurrent.CompletableFuture.completedFuture(this.bytes); }")

# ---------------------------------------------------------------- MmReq: plain data from an event / the world thread
for _f in ("public String kind;", "public @PR@ pr;", "public java.util.UUID uuid;", "public @WLD@ world;", "public @ST@ store;", "public long at;"):
    MMF(mmreq, _f)
MMC(mmreq, "public MmReq(String k, @PR@ pr, @WLD@ w, @ST@ st) { this.kind = k; this.pr = pr; this.uuid = pr == null ? null : pr.getUuid(); this.world = w; this.store = st; this.at = System.currentTimeMillis(); }")

# ---------------------------------------------------------------- MmSess: one player's minimap (minimap-thread state unless marked)
for _f in ("public @PR@ pr;", "public java.util.UUID uuid;", "public String who;",
           "public @WLD@ world;", "public @ST@ store;", "public java.util.UUID wuuid;", "public String wname;",
           "public volatile @PKG@.MmHud hud;", "public volatile boolean wants;",
           # the tap's side (any thread): the queue of packet references + its bound
           "public final java.util.concurrent.ConcurrentLinkedQueue q = new java.util.concurrent.ConcurrentLinkedQueue();",
           "public final java.util.concurrent.atomic.AtomicInteger qn = new java.util.concurrent.atomic.AtomicInteger();",
           "public final java.util.concurrent.atomic.AtomicLong dropped = new java.util.concurrent.atomic.AtomicLong();",
           # what the stream sent this player in this world (keys only), the keep window's pieces (MapImage until encoded, then its content key)
           "public @LOS@ streamed = new @LOS@();", "public java.util.HashMap known = new java.util.HashMap();",
           "public java.util.HashMap markers = new java.util.HashMap();", "public boolean markersDirty;",
           "public boolean streamSeen;", "public long attachAt;", "public boolean needFull;", "public boolean more;",
           # geometry (MmSess.geometry)
           "public int S;", "public int rw;", "public int C;", "public int r;", "public int t;", "public int h;", "public int w;", "public int span;",
           "public int shape;", "public long upd;", "public int ring;", "public int msize;", "public int mask;", "public int dp;", "public int ap;",
           "public String ringCol;", "public String pcol;", "public String maskRel;", "public String ringPath;", "public String dark;",
           "public String[] arrows;", "public String[] kindPath;", "public String partyPath;",
           "public long[] slotKey;", "public String[] slotPath;",
           "public int ccx;", "public int ccz;", "public int bx;", "public int bz;", "public int gl;", "public int gt;", "public int arrow;",
           "public boolean posKnown;", "public double px;", "public double pz;", "public long nextPanAt;", "public long nextPartyAt;",
           "public int[] mkX;", "public int[] mkY;", "public String[] mkPath;", "public int[] ptX;", "public int[] ptY;", "public String[] ptPath;",
           # stats (the first-fill line, the status)
           "public int encodes;", "public int hits;", "public int dedup;", "public int sweepHit;", "public int sweepMiss;", "public int bad;",
           "public int pics;", "public long sentBytes;", "public long fillNs;", "public boolean fillLogged;", "public int updates;",
           "public int pans;", "public int rebases;", "public int errors;", "public long packets;", "public long clears;",
           # fix round: map pieces (tiles) delivered on this connection (the cap counts these only) + the one warning
           "public int tiles;", "public boolean capWarned;",
           # fix round: a NEW connection's session (hello) clears the uuid's per-connection lists on the minimap thread (fast reconnect)
           "public volatile boolean fresh;",
           # fix round: the drawn frame (re-attach only when it changes), the anchor sent, the detail this session encodes at
           "public String dkey;", "public String anc;", "public int det;", "public String dsuf;", "public boolean forceMk;",
           # fix round: no attach before this world's map stream started (islands send none: no empty disc)
           "public boolean pending;", "public long pendingSince;", "public boolean pendLogged;",
           # fix round: the tap's image bound (pieces queued) + packets queued as keys only
           "public final java.util.concurrent.atomic.AtomicInteger qc = new java.util.concurrent.atomic.AtomicInteger();",
           "public final java.util.concurrent.atomic.AtomicLong keysOnly = new java.util.concurrent.atomic.AtomicLong();",
           # fix round: chunk (-1,-1) - the engine's map cache cannot hold it (its key is the map's EMPTY marker): the stream's own piece
           "public @MIM@ originImg;",
           # fix round: the provisional keep window before the position is known (the join burst keeps its pieces)
           "public boolean provOk;", "public int pcx;", "public int pcz;", "public int ph;",
           # fix round: party dots pinned to the rim: the member's position, re-pinned at every pan
           "public double[] ptWX;", "public double[] ptWZ;", "public boolean[] ptRim;"):
    MMF(mmsess, _f)
MMC(mmsess, r"""
public MmSess(@PR@ pr) {
  this.pr = pr;
  this.uuid = pr == null ? null : pr.getUuid();
  try { this.who = pr == null ? "?" : pr.getUsername(); } catch (Throwable t) { this.who = "?"; }
  this.wname = "?";
  this.arrow = -1;
  this.mkX = new int[@QMK@];
  this.mkY = new int[@QMK@];
  this.mkPath = new String[@QMK@];
  this.ptX = new int[@QPT@];
  this.ptY = new int[@QPT@];
  this.ptPath = new String[@QPT@];
  this.slotKey = new long[0];
  this.slotPath = new String[0];
  this.ptWX = new double[@QPT@];
  this.ptWZ = new double[@QPT@];
  this.ptRim = new boolean[@QPT@];
  this.dsuf = "/0";
}""")

# ---------------------------------------------------------------- MmHud: the keyed HUD. show() hands the CACHED document over (no build on
# the world thread); push() = one update from the minimap thread; onRemove (engine, world thread) and push share the HUD's monitor, so no
# update can follow an onRemove (critic C12)
for _f in ("public @PKG@.MmSess sess;", "public @UCB@ doc;", "public volatile boolean attached;", "public volatile boolean gone;",
           "public volatile boolean ended;", "public int pushes;"):
    MMF(mmhud, _f)
MMC(mmhud, r"""
public MmHud(@PR@ pr, @PKG@.MmSess s, @UCB@ doc) {
  super(pr, "@MMKEY@", @MMZ@);
  this.sess = s;
  this.doc = doc;
}""")
MMM(mmhud, "protected void build(@UCB@ b) { }")
MMM(mmhud, "public void show() { update(true, this.doc); }")
MMM(mmhud, r"""
public synchronized boolean push(@UCB@ b) {
  if (!this.attached || this.gone || this.ended) return false;
  update(false, b);
  this.pushes = this.pushes + 1;
  return true;
}""")
MMM(mmhud, "protected synchronized void onRemove() { this.gone = true; }")

# ---------------------------------------------------------------- the small Runnables / listeners (bodies call Minimap, below)
mmtick.addInterface(pool.get("java.lang.Runnable"))
MMC(mmtick, "public MmTick() { }")
mmthr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
MMC(mmthr, "public MmThreads() { }")
MMM(mmthr, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyHud-Minimap");
  t.setDaemon(true);
  t.setPriority(Thread.NORM_PRIORITY - 1);
  return t;
}""")
mmatt.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PKG@.MmSess sess;", "public @PKG@.MmHud hud;", "public @ST@ store;"):
    MMF(mmatt, _f)
MMC(mmatt, "public MmAttach(@PKG@.MmSess s, @PKG@.MmHud h, @ST@ st) { this.sess = s; this.hud = h; this.store = st; }")
mmdet.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public @ST@ store;", "public @PKG@.MmHud hud;"):
    MMF(mmdet, _f)
MMC(mmdet, "public MmDetach(@PR@ pr, @ST@ st, @PKG@.MmHud h) { this.pr = pr; this.store = st; this.hud = h; }")
mmtap.addInterface(pool.get(MMT["PPW"]))
MMC(mmtap, "public MmTap() { }")
mmcon.addInterface(pool.get("java.util.function.Consumer"))
MMC(mmcon, "public MmConnect() { }")
mmquit.addInterface(pool.get("java.util.function.Consumer"))
MMC(mmquit, "public MmQuit() { }")

# ---------------------------------------------------------------- Minimap: the state
for _f in ("public static volatile java.util.concurrent.ScheduledExecutorService EXEC;",
           "public static volatile java.util.concurrent.ScheduledFuture FUT;",
           "public static volatile long LAST_TICK;", "public static volatile String LAST_THREAD;", "public static volatile long TICKS;",
           "public static final Object LOCK = new Object();",
           "public static final java.util.concurrent.ConcurrentHashMap SESS = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentLinkedQueue REQ = new java.util.concurrent.ConcurrentLinkedQueue();",
           # minimap thread only: uuid -> names this CONNECTION has; uuid of connections that got the statics + the one rebuild
           "public static final java.util.HashMap DELIVERED = new java.util.HashMap();",
           "public static final java.util.HashSet STATICS = new java.util.HashSet();",
           "public static final java.util.HashSet CAPPED = new java.util.HashSet();",
           # content key -> MmAsset (LRU), generated pictures by kind, cached documents by geometry
           "public static final java.util.LinkedHashMap CACHE = new java.util.LinkedHashMap(1024, 0.75f, true);",
           "public static final java.util.HashMap GEN = new java.util.HashMap();",
           "public static final java.util.LinkedHashMap DOCS = new java.util.LinkedHashMap(16, 0.75f, true);",
           "public static final java.util.HashMap ORDER = new java.util.HashMap();",
           "public static volatile int TAPS;", "public static volatile @PF@ TAPF;",
           "public static final java.util.concurrent.atomic.AtomicLong TAPERR = new java.util.concurrent.atomic.AtomicLong();",
           "public static volatile boolean RELAYOUT;", "public static volatile @LOG@ LOG;", "public static int RR;",
           "public static long ERRORS;", "public static final java.util.HashSet ERRKINDS = new java.util.HashSet();",
           "public static final java.util.HashSet NOSTREAM = new java.util.HashSet();",
           "public static final java.util.HashSet NAMES = new java.util.HashSet();",
           "public static volatile boolean WD_LOGGED;", "public static long ENC_NS;", "public static long ENC_N;",
           # fix round: the watchdog sees a tick stuck INSIDE the lock (no new thread then) and restarts a dead one at most 3 times
           "public static volatile boolean IN_TICK;", "public static volatile long TICK_START;", "public static volatile Thread TICK_THREAD;",
           "public static volatile int RESTARTS;", "public static volatile long HUNG_AT;",
           # the last 32 minimap log lines in memory (the harness reads them; a status line could too)
           "public static final java.util.LinkedList TAIL = new java.util.LinkedList();"):
    MMF(mmmain, _f)
MMM(mmmain, r"""
public static void remember0(String m) {
  TAIL.add(m);
  while (TAIL.size() > 32) TAIL.removeFirst();
}""")
MMM(mmmain, r"""
public static void remember(String m) {
  synchronized (TAIL) { remember0(m); }
}""")
MMM(mmmain, r"""
public static String[] tail() {
  synchronized (TAIL) { return (String[]) TAIL.toArray(new String[0]); }
}""")
MMM(mmmain, r"""
public static void info(String m) {
  try { remember(m); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyHud] " + m); } catch (Throwable t) { }
}""")
MMM(mmmain, r"""
public static void warn(String m) {
  try { remember("WARNING " + m); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyHud] " + m); } catch (Throwable t) { }
}""")
# a failure is counted; the first one of each kind is logged (one bad player never stops the tick - critic C11)
MMM(mmmain, r"""
public static void err(String kind, Throwable t) {
  ERRORS = ERRORS + 1L;
  boolean first = false;
  synchronized (ERRKINDS) { first = ERRKINDS.add(kind); }
  if (first) warn("minimap: " + kind + " failed (logged once, counted after): " + t);
}""")
# ---- pure geometry (the harness walks it): chunk keys, the ring-buffer slot (floorMod: negative chunks), pan positions, the heading
MMM(mmmain, "public static long key(int cx, int cz) { return (((long) cx) << 32) | (((long) cz) & 4294967295L); }")
MMM(mmmain, "public static int keyX(long k) { return (int) (k >> 32); }")
MMM(mmmain, "public static int keyZ(long k) { return (int) k; }")
MMM(mmmain, "public static int chunkOf(double v) { return (int) Math.floor(v / 32.0); }")
MMM(mmmain, "public static int slot(int cx, int cz, int w) { return Math.floorMod(cx, w) + w * Math.floorMod(cz, w); }")
MMM(mmmain, "public static int base(int cc, int w) { return cc - (w - 1); }")
MMM(mmmain, "public static boolean inGroup(int cc, int b, int h, int span) { return cc - h >= b && cc + h <= b + span - 1; }")
MMM(mmmain, "public static int tilePos(int c, int b, int t) { return (c - b) * t; }")
# the grid Group's Left / Top in the clip so that block coordinate p sits at the clip centre
MMM(mmmain, "public static int groupPos(double p, int b, int C, int t) { return (int) Math.round((double) C / 2.0 - (p - (double) b * 32.0) * (double) t / 32.0); }")
# the arrow picture for a yaw (RADIANS - Transform.getDirection: x = -sin(yaw), z = -cos(yaw): yaw 0 faces -Z = north, a growing yaw turns
# toward -X = west): bearing = -yaw in degrees clockwise from north; 16 buckets of 22.5 degrees, 0 = N, 4 = E, 8 = S, 12 = W
MMM(mmmain, r"""
public static int heading(float yaw) {
  if (Float.isNaN(yaw) || Float.isInfinite(yaw)) return 0;
  double deg = -((double) yaw) * 180.0 / Math.PI;
  double b = deg % 360.0;
  if (b < 0.0) b = b + 360.0;
  int k = (int) Math.floor((b + 11.25) / 22.5);
  return k % 16;
}""")
# the window offsets nearest first (the encode budget goes to the pieces closest to the player)
MMM(mmmain, r"""
public static int[] order(int h) {
  Integer K = Integer.valueOf(h);
  Object o = ORDER.get(K);
  if (o != null) return (int[]) o;
  int w = 2 * h + 1;
  int n = w * w;
  int[] d = new int[n];
  int[] out = new int[2 * n];
  int k = 0;
  for (int dz = -h; dz <= h; dz++) {
    for (int dx = -h; dx <= h; dx++) { out[2 * k] = dx; out[2 * k + 1] = dz; d[k] = dx * dx + dz * dz; k = k + 1; }
  }
  for (int i = 1; i < n; i++) {
    int dv = d[i]; int ax = out[2 * i]; int az = out[2 * i + 1];
    int j = i - 1;
    while (j >= 0 && d[j] > dv) { d[j + 1] = d[j]; out[2 * j + 2] = out[2 * j]; out[2 * j + 3] = out[2 * j + 1]; j = j - 1; }
    d[j + 1] = dv; out[2 * j + 2] = ax; out[2 * j + 3] = az;
  }
  ORDER.put(K, out);
  return out;
}""")
# ---- pictures: a content-named asset (sha256 = the engine's CommonAsset.hash), the generated ones once per server
MMM(mmmain, r"""
public static @PKG@.MmAsset asset(String kind, byte[] png) {
  if (png == null) return null;
  String hash = @CMA@.hash(png);
  String name = kind.equals("mask") ? "@QMDIR@@QMPRE@" + hash.substring(0, 16) + ".png" : "@QADIR@" + (kind.length() == 0 ? "" : kind + "-") + hash.substring(0, 16) + ".png";
  return new @PKG@.MmAsset(name, hash, png);
}""")
MMM(mmmain, r"""
public static @PKG@.MmAsset gen(String id) {
  Object o = GEN.get(id);
  if (o != null) return (@PKG@.MmAsset) o;
  @PKG@.MmAsset a = null;
  try {
    String[] p = id.split(":");
    if (p[0].equals("mask")) { int d = Integer.parseInt(p[1]); a = asset("mask", @PKG@.MmPng.encode(d, d, @PKG@.MmPng.mask(d, Integer.parseInt(p[2])))); }
    else if (p[0].equals("ring")) { int S = Integer.parseInt(p[1]); a = asset("ring", @PKG@.MmPng.encode(S, S, @PKG@.MmPng.ring(S, Integer.parseInt(p[2]), Integer.parseInt(p[3]), Integer.parseInt(p[4])))); }
    else if (p[0].equals("arrow")) a = asset("arrow", @PKG@.MmPng.encode(32, 32, @PKG@.MmPng.arrow(Integer.parseInt(p[1]))));
    else if (p[0].equals("dot")) a = asset("dot", @PKG@.MmPng.encode(16, 16, @PKG@.MmPng.dot(Integer.parseInt(p[1]))));
    else if (p[0].equals("dark")) a = asset("none", @PKG@.MmPng.encode(2, 2, new int[4]));
  } catch (Throwable t) { a = null; err("picture " + id, t); }
  if (a != null) GEN.put(id, a);
  return a;
}""")
MMM(mmmain, r"""
public static java.util.HashSet delivered(java.util.UUID u) {
  Object o = DELIVERED.get(u);
  if (o != null) return (java.util.HashSet) o;
  java.util.HashSet d = new java.util.HashSet();
  DELIVERED.put(u, d);
  return d;
}""")
# one picture to ONE player, once per connection: AssetInitialize + AssetPart(s) + AssetFinalize in one write (CommonAssetModule.sendAsset's
# sequence to this player - probe P1a); a map piece (tile = true) past the per-connection cap is not sent (false)
MMM(mmmain, r"""
public static boolean send(@PKG@.MmSess s, @PKG@.MmAsset a, boolean tile) {
  if (s == null || a == null || s.pr == null) return false;
  java.util.HashSet d = delivered(s.uuid);
  if (d.contains(a.getName())) { if (tile) s.dedup = s.dedup + 1; return true; }
  if (tile && s.tiles >= @QCAP@) {
    if (!s.capWarned) {
      s.capWarned = true;
      CAPPED.add(s.uuid);
      info("minimap: " + s.who + " reached " + @QCAP@ + " map pieces on this connection - new map pieces stay dark until a reconnect");
      try { s.pr.sendMessage(@MSG@.raw("[SkyyHud] Your minimap has drawn " + @QCAP@ + " map pieces this session - new areas stay dark until you rejoin.")); } catch (Throwable t) { }
    }
    return false;
  }
  byte[] b = a.bytes;
  int parts = (b.length + @QPART@ - 1) / @QPART@;
  if (parts < 1) parts = 1;
  @TCP@[] ps = new @TCP@[parts + 2];
  @AINI@ ai = new @AINI@((com.hypixel.hytale.protocol.Asset) a.toPacket(), b.length);
  ps[0] = ai;
  int bytes = ai.computeSize();
  for (int i = 0; i < parts; i++) {
    int off = i * @QPART@;
    int len = Math.min(@QPART@, b.length - off);
    if (len < 0) len = 0;
    byte[] part = new byte[len];
    System.arraycopy(b, off, part, 0, len);
    @APRT@ pa = new @APRT@(part);
    ps[1 + i] = pa;
    bytes = bytes + pa.computeSize();
  }
  @AFIN@ af = new @AFIN@();
  ps[parts + 1] = af;
  bytes = bytes + af.computeSize();
  s.pr.getPacketHandler().write(ps);
  d.add(a.getName());
  if (tile) s.tiles = s.tiles + 1;
  s.pics = s.pics + 1;
  s.sentBytes = s.sentBytes + (long) bytes;
  return true;
}""")
MMM(mmmain, r"""
public static @ANC@ anchor(int l, int t, int w, int h) {
  @ANC@ a = new @ANC@();
  a.setLeft(@VAL@.of(Integer.valueOf(l)));
  a.setTop(@VAL@.of(Integer.valueOf(t)));
  a.setWidth(@VAL@.of(Integer.valueOf(w)));
  a.setHeight(@VAL@.of(Integer.valueOf(h)));
  return a;
}""")
# the piece's CONTENT key (critic B6: never the coordinates): sizes, bits, palette length, packed length, CRC32 of palette + packed bytes,
# and the detail it is encoded at; null = not a MapImage this encoder takes
MMM(mmmain, r"""
public static String contentKey(@MIM@ m, int det) {
  if (m == null || m.palette == null || m.packedIndices == null) return null;
  int[] pal = m.palette;
  java.util.zip.CRC32 c = new java.util.zip.CRC32();
  byte[] pb = new byte[pal.length * 4];
  for (int i = 0; i < pal.length; i++) {
    int v = pal[i];
    pb[4 * i] = (byte) (v >>> 24); pb[4 * i + 1] = (byte) (v >>> 16); pb[4 * i + 2] = (byte) (v >>> 8); pb[4 * i + 3] = (byte) v;
  }
  c.update(pb, 0, pb.length);
  c.update(m.packedIndices, 0, m.packedIndices.length);
  return m.width + "x" + m.height + "b" + (m.bitsPerIndex & 255) + "p" + pal.length + "n" + m.packedIndices.length + "c" + Long.toHexString(c.getValue()) + "/" + det;
}""")
MMM(mmmain, r"""
public static int cacheCap() {
  int slots = 0;
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) { @PKG@.MmSess s = (@PKG@.MmSess) it.next(); slots = slots + s.w * s.w; }
  return Math.max(4096, slots);
}""")
MMM(mmmain, r"""
public static void trimCache() {
  int cap = cacheCap();
  java.util.Iterator it = CACHE.keySet().iterator();
  int over = CACHE.size() - cap;
  while (over > 0 && it.hasNext()) { it.next(); it.remove(); over = over - 1; }
}""")
# the picture for window chunk (cx, cz): the player's own piece (a MapImage until encoded, then its content key), else - ONLY for a chunk
# this player's stream sent (privacy, critic B6) - the engine's in-memory piece (a ConcurrentHashMap read; never generates). Encoding
# spends the budget; out of budget = null + s.more (the next tick goes on); "!" = a piece the encoder refused
MMM(mmmain, r"""
public static @PKG@.MmAsset resolve(@PKG@.MmSess s, int cx, int cz, int[] budget, long deadline, boolean count) {
  long k = key(cx, cz);
  Long K = Long.valueOf(k);
  Object o = s.known.get(K);
  if (o instanceof String) {
    if ("!".equals(o)) return null;
    Object a = ((String) o).endsWith(s.dsuf) ? CACHE.get(o) : null;
    if (a != null) return (@PKG@.MmAsset) a;
    s.known.remove(K);
    o = null;
  }
  if (o == null && k == -1L && s.originImg != null) o = s.originImg;
  boolean sent = o != null || s.streamed.contains(k);
  if (!sent) return null;
  // the 3 ms budget covers every map read, CRC and encode of the tick (critic C13): past it, the next tick goes on
  if (System.nanoTime() > deadline) { s.more = true; return null; }
  // this player's share of the encode budget is spent: no more map reads / CRCs for it this tick (its leftover pass may come)
  if (budget[0] <= 0) { s.more = true; return null; }
  boolean swept = false;
  if (o == null) {
    @MIM@ m = null;
    // chunk (-1,-1): its key is the engine map's EMPTY marker - never read there (only the stream's own piece, above)
    if (k == -1L) { if (count) s.sweepMiss = s.sweepMiss + 1; return null; }
    try {
      @WMM@ wm = s.world == null ? null : s.world.getWorldMapManager();
      if (wm != null) m = wm.getImageIfInMemory(cx, cz);
    } catch (Throwable t) { m = null; }
    if (m == null) { if (count) s.sweepMiss = s.sweepMiss + 1; return null; }
    swept = true;
    o = m;
  }
  @MIM@ m = (@MIM@) o;
  int det = s.det > 0 ? s.det : @PKG@.MmCfg.detail();
  String ck = contentKey(m, det);
  if (ck == null) { s.known.put(K, "!"); s.bad = s.bad + 1; return null; }
  Object c = CACHE.get(ck);
  if (c != null) { s.known.put(K, ck); s.hits = s.hits + 1; if (swept) s.sweepHit = s.sweepHit + 1; return (@PKG@.MmAsset) c; }
  // out of budget: a piece from the STREAM stays referenced until encoded; a swept one is not kept (the next pass reads the engine
  // cache again - a map read), so no MapImage is held for it (critic A2)
  if (budget[0] <= 0 || System.nanoTime() > deadline) { s.more = true; return null; }
  budget[0] = budget[0] - 1;
  long t0 = System.nanoTime();
  byte[] png = @PKG@.MmPng.tilePng(m, det);
  ENC_NS = ENC_NS + (System.nanoTime() - t0);
  ENC_N = ENC_N + 1L;
  s.encodes = s.encodes + 1;
  if (png == null) { s.known.put(K, "!"); s.bad = s.bad + 1; return null; }
  if (swept) s.sweepHit = s.sweepHit + 1;
  @PKG@.MmAsset a = asset("", png);
  CACHE.put(ck, a);
  s.known.put(K, ck);
  return a;
}""")
# the window chunks around (ccx, ccz), nearest first -> their ring-buffer slots: a slot whose chunk changed gets its Anchor + AssetPath, a
# slot whose picture changed its AssetPath; reanchor = every Anchor (a re-base / the first update after the attach). A picture is sent
# (once per connection) only when a slot is about to show it
MMM(mmmain, r"""
public static int assign(@PKG@.MmSess s, @UCB@ b, boolean reanchor, int[] budget, long deadline, boolean count) {
  int[] o = order(s.h);
  int n = o.length / 2;
  int changed = 0;
  for (int i = 0; i < n; i++) {
    int cx = s.ccx + o[2 * i];
    int cz = s.ccz + o[2 * i + 1];
    int sl = slot(cx, cz, s.w);
    long k = key(cx, cz);
    boolean moved = s.slotKey[sl] != k;
    if (moved || reanchor) b.setObject("#SkyyMmT" + sl + ".Anchor", anchor(tilePos(cx, s.bx, s.t), tilePos(cz, s.bz, s.t), s.t, s.t));
    @PKG@.MmAsset a = resolve(s, cx, cz, budget, deadline, count && (moved || reanchor));
    String p;
    if (a == null) p = s.dark;
    else if (!moved && a.getName().equals(s.slotPath[sl])) p = s.slotPath[sl];
    else p = send(s, a, true) ? a.getName() : s.dark;
    if (moved || reanchor || !p.equals(s.slotPath[sl])) { b.set("#SkyyMmT" + sl + ".AssetPath", p); changed = changed + 1; }
    s.slotKey[sl] = k;
    s.slotPath[sl] = p;
  }
  return changed;
}""")
# keep window == trim window (critic B7): an entry outside it goes, so an out-of-window change can never leave a stale piece
MMM(mmmain, r"""
public static void trim(@PKG@.MmSess s) {
  int lim = s.h + 2;
  java.util.Iterator it = s.known.keySet().iterator();
  while (it.hasNext()) {
    long k = ((Long) it.next()).longValue();
    int dx = keyX(k) - s.ccx;
    int dz = keyZ(k) - s.ccz;
    if (dx > lim || dx < -lim || dz > lim || dz < -lim) it.remove();
  }
}""")
MMM(mmmain, r"""
public static boolean inKeep(@PKG@.MmSess s, int cx, int cz) {
  if (!s.wants) return false;
  if (!s.posKnown) {
    if (!s.provOk) return false;
    int pdx = cx - s.pcx;
    int pdz = cz - s.pcz;
    return pdx <= s.ph && pdx >= -s.ph && pdz <= s.ph && pdz >= -s.ph;
  }
  int lim = s.h + 2;
  int dx = cx - s.ccx;
  int dz = cz - s.ccz;
  return dx <= lim && dx >= -lim && dz <= lim && dz >= -lim;
}""")
MMM(mmmain, r"""
public static void noteMarker(@MMK@ m) {
  String n = m.markerImage;
  if (n == null) return;
  boolean add = false;
  synchronized (NAMES) { add = NAMES.size() < 32 && NAMES.add(n); }
  if (add) info("minimap: map marker kind seen: '" + n + "' (recorded once - the Other players rule reads these names)");
}""")
# 0 waypoint / anything (gold), 1 death (red), 2 spawn / home / bed (green), 3 a player (other players: the markerImage names a player)
MMM(mmmain, r"""
public static int kindOf(@MMK@ m) {
  String n = m.markerImage == null ? "" : m.markerImage.toLowerCase(java.util.Locale.ROOT);
  if (n.indexOf("player") >= 0) return 3;
  if (n.indexOf("death") >= 0 || n.indexOf("grave") >= 0) return 1;
  if (n.indexOf("spawn") >= 0 || n.indexOf("home") >= 0 || n.indexOf("bed") >= 0) return 2;
  return 0;
}""")
# fix round: the window half-width (h) a layout gives - the same maths as geometry() (the provisional keep window before the attach)
MMM(mmmain, r"""
public static int halfFor(@PKG@.WLayout l) {
  int[] v = @PKG@.MmCfg.dec(l.mm);
  int S = 160 * @PKG@.MmCfg.snapScale(l.scale) / 100;
  int C = S - 2 * Math.max(3, S / 40);
  int r = v[0];
  int mx = @PKG@.MmCfg.maxRadius();
  if (r > mx) r = mx;
  int t = Math.max(2, (int) Math.round((double) C * 32.0 / (2.0 * (double) r)));
  int h = (C + 2 * t - 1) / (2 * t);
  if (2 * h + 1 > @QMAXW@) h = (@QMAXW@ - 1) / 2;
  return h;
}""")
# fix round (critic: the join burst's pieces were thrown away while the position was unknown): the player's position NOW (a transform
# read, as step() does) and its window = where the burst's pieces are kept; outside it keys only, as before
MMM(mmmain, r"""
public static void provisional(@PKG@.MmSess s) {
  s.provOk = false;
  try {
    com.hypixel.hytale.math.vector.Transform tr = s.pr == null ? null : s.pr.getTransform();
    if (tr == null || tr.getPosition() == null) return;
    int h = s.h;
    if (h <= 0) {
      @PKG@.WLayout l = (@PKG@.WLayout) @PKG@.LayoutStore.get(s.uuid).get("Minimap");
      h = l == null ? 6 : halfFor(l);
    }
    s.pcx = chunkOf(tr.getPosition().x);
    s.pcz = chunkOf(tr.getPosition().z);
    s.ph = h;
    s.provOk = true;
  } catch (Throwable t) { s.provOk = false; }
}""")
# tick thread: what the tap queued since the last tick (critic A3: an image is kept only inside the keep window - of the known position,
# or before it is known the provisional one; fix round)
MMM(mmmain, r"""
public static void drain(@PKG@.MmSess s) {
  int n = 0;
  s.provOk = false;
  while (n < 200000) {
    Object o = s.q.poll();
    if (o == null) break;
    s.qn.decrementAndGet();
    n = n + 1;
    if (n == 1 && !s.posKnown && s.wants) provisional(s);
    if (o instanceof long[]) {
      // queued past the image bound (tap): the keys only - the engine cache serves those pieces (a held piece there is stale now)
      long[] ks = (long[]) o;
      s.streamSeen = true;
      s.packets = s.packets + 1L;
      for (int i = 0; i < ks.length; i++) {
        s.streamed.add(ks[i]);
        s.known.remove(Long.valueOf(ks[i]));
        if (ks[i] == -1L) s.originImg = null;
      }
      s.more = true;
    } else if (o instanceof @UWM@) {
      @UWM@ u = (@UWM@) o;
      s.streamSeen = true;
      s.packets = s.packets + 1L;
      @MCH@[] cs = u.chunks;
      if (cs != null) {
        s.qc.addAndGet(-cs.length);
        for (int i = 0; i < cs.length; i++) {
          @MCH@ c = cs[i];
          if (c == null) continue;
          long k = key(c.chunkX, c.chunkZ);
          Long K = Long.valueOf(k);
          if (c.image == null) { s.streamed.remove(k); s.known.remove(K); if (k == -1L) s.originImg = null; continue; }
          s.streamed.add(k);
          if (k == -1L) { s.originImg = c.image; s.known.remove(K); s.more = true; continue; }
          if (inKeep(s, c.chunkX, c.chunkZ)) { s.known.put(K, c.image); s.more = true; }
          else s.known.remove(K);
        }
      }
      @MMK@[] am = u.addedMarkers;
      if (am != null) {
        for (int i = 0; i < am.length; i++) {
          @MMK@ m = am[i];
          if (m == null || m.id == null) continue;
          s.markers.put(m.id, m);
          noteMarker(m);
          s.markersDirty = true;
        }
      }
      String[] rm = u.removedMarkers;
      if (rm != null) {
        for (int i = 0; i < rm.length; i++) { if (rm[i] != null && s.markers.remove(rm[i]) != null) s.markersDirty = true; }
      }
    } else if (o instanceof @CWM@) {
      s.streamed.clear();
      s.known.clear();
      s.originImg = null;
      s.markers.clear();
      s.markersDirty = true;
      s.streamSeen = false;
      s.clears = s.clears + 1L;
    }
  }
}""")
MMM(mmmain, r"""
public static void dotAt(@UCB@ b, String id, int x, int y, int dp, String path, int[] ox, int[] oy, String[] op, int i, boolean force) {
  if (force || ox[i] != x || oy[i] != y) { b.setObject(id + ".Anchor", anchor(x, y, dp, dp)); ox[i] = x; oy[i] = y; }
  if (path != null && !path.equals(op[i])) { b.set(id + ".AssetPath", path); op[i] = path; }
}""")
MMM(mmmain, "public static int gx(@PKG@.MmSess s, double x) { return (int) Math.round((x - (double) s.bx * 32.0) * (double) s.t / 32.0) - s.dp / 2; }")
MMM(mmmain, "public static int gz(@PKG@.MmSess s, double z) { return (int) Math.round((z - (double) s.bz * 32.0) * (double) s.t / 32.0) - s.dp / 2; }")
# map-marker dots: the nearest 40 within the zoom radius (the kinds the player and the admin allow), in grid coordinates (they pan with the grid)
MMM(mmmain, r"""
public static void markers(@PKG@.MmSess s, @UCB@ b, double px, double pz, boolean force) {
  s.markersDirty = false;
  boolean mk = (s.mask & 2) != 0;
  boolean op = (s.mask & 4) != 0 && @PKG@.MmCfg.OTHER_PLAYERS;
  int cap = s.markers.size();
  double[] ds = new double[cap];
  Object[] ms = new Object[cap];
  int[] ks = new int[cap];
  int n = 0;
  double lim = (double) s.r * 1.05;
  lim = lim * lim;
  java.util.Iterator it = s.markers.values().iterator();
  while (it.hasNext() && n < cap) {
    @MMK@ m = (@MMK@) it.next();
    if (m.transform == null || m.transform.position == null) continue;
    int kd = kindOf(m);
    if (kd == 3 ? !op : !mk) continue;
    double dx = m.transform.position.x - px;
    double dz = m.transform.position.z - pz;
    double d = dx * dx + dz * dz;
    if (d > lim) continue;
    ds[n] = d; ms[n] = m; ks[n] = kd; n = n + 1;
  }
  int show = n < @QMK@ ? n : @QMK@;
  for (int i = 0; i < show; i++) {
    int best = i;
    for (int j = i + 1; j < n; j++) if (ds[j] < ds[best]) best = j;
    double td = ds[i]; ds[i] = ds[best]; ds[best] = td;
    Object tm = ms[i]; ms[i] = ms[best]; ms[best] = tm;
    int tk = ks[i]; ks[i] = ks[best]; ks[best] = tk;
  }
  for (int i = 0; i < @QMK@; i++) {
    if (i < show) {
      @MMK@ m = (@MMK@) ms[i];
      dotAt(b, "#SkyyMmMk" + i, gx(s, m.transform.position.x), gz(s, m.transform.position.z), s.dp, s.kindPath[ks[i]], s.mkX, s.mkY, s.mkPath, i, force);
    } else if (s.mkX[i] != -4000 || force) dotAt(b, "#SkyyMmMk" + i, -4000, -4000, s.dp, null, s.mkX, s.mkY, s.mkPath, i, true);
  }
}""")
# fix round (critic: a rim-pinned dot slid off the mask between the 1 Hz updates): the rim point for party dot i from the player's
# position NOW (party() keeps the member's position; move() re-pins the clamped dots at every pan)
MMM(mmmain, r"""
public static void rimDot(@PKG@.MmSess s, @UCB@ b, int i, double px, double pz) {
  double x = s.ptWX[i];
  double z = s.ptWZ[i];
  double dx = x - px;
  double dz = z - pz;
  double d = Math.sqrt(dx * dx + dz * dz);
  double lim = (double) s.r * 0.92;
  s.ptRim[i] = d > lim && d > 0.0;
  if (s.ptRim[i]) { x = px + dx * lim / d; z = pz + dz * lim / d; }
  dotAt(b, "#SkyyMmPt" + i, gx(s, x), gz(s, z), s.dp, s.partyPath, s.ptX, s.ptY, s.ptPath, i, false);
}""")
# party dots (1 Hz): the bridge's party:fn:members (the Party widget's own read), same world, rim-pinned when beyond the zoom radius
MMM(mmmain, r"""
public static void party(@PKG@.MmSess s, @UCB@ b) {
  int n = 0;
  if ((s.mask & 1) != 0 && @PKG@.MmCfg.PARTY_DOTS && s.posKnown) {
    String[] mem = @PKG@.Widgets.callArr(@PKG@.Widgets.bridge(), "party:fn:members", s.uuid);
    if (mem != null) {
      for (int i = 0; i < mem.length && n < @QPT@; i++) {
        java.util.UUID u = null;
        try { u = java.util.UUID.fromString(mem[i].trim()); } catch (Throwable t) { u = null; }
        if (u == null || u.equals(s.uuid)) continue;
        @PR@ o = null;
        try { o = @UNI@.get().getPlayer(u); } catch (Throwable t) { o = null; }
        if (o == null || !o.isValid()) continue;
        java.util.UUID ow = o.getWorldUuid();
        if (ow == null || !ow.equals(s.wuuid)) continue;
        com.hypixel.hytale.math.vector.Transform tr = o.getTransform();
        if (tr == null || tr.getPosition() == null) continue;
        s.ptWX[n] = tr.getPosition().x;
        s.ptWZ[n] = tr.getPosition().z;
        rimDot(s, b, n, s.px, s.pz);
        n = n + 1;
      }
    }
  }
  for (int i = n; i < @QPT@; i++) { s.ptRim[i] = false; if (s.ptX[i] != -4000) dotAt(b, "#SkyyMmPt" + i, -4000, -4000, s.dp, null, s.ptX, s.ptY, s.ptPath, i, true); }
}""")
# the window follows the player: a step into the next chunk changes only the slots of the entering row / column (ring buffer); leaving the
# grid Group's span re-bases it (every Anchor); then ONE Anchor for the grid, the arrow only when its heading changes, the dots
MMM(mmmain, r"""
public static void move(@PKG@.MmSess s, @UCB@ b, double px, double pz, float yaw, int[] budget, long deadline, boolean full) {
  int cx = chunkOf(px);
  int cz = chunkOf(pz);
  boolean crossed = full || cx != s.ccx || cz != s.ccz;
  s.ccx = cx;
  s.ccz = cz;
  boolean reb = full;
  if (!inGroup(cx, s.bx, s.h, s.span) || !inGroup(cz, s.bz, s.h, s.span)) { s.bx = base(cx, s.w); s.bz = base(cz, s.w); reb = true; s.rebases = s.rebases + 1; }
  if (crossed || reb || s.more) {
    s.more = false;
    assign(s, b, reb, budget, deadline, crossed || reb);
    if (crossed) trim(s);
  }
  int gl = groupPos(px, s.bx, s.C, s.t);
  int gt = groupPos(pz, s.bz, s.C, s.t);
  boolean pan = false;
  if (reb || gl != s.gl || gt != s.gt) {
    b.setObject("#SkyyMmGrid.Anchor", anchor(gl, gt, s.span * s.t, s.span * s.t));
    s.gl = gl;
    s.gt = gt;
    s.pans = s.pans + 1;
    pan = true;
  }
  int hd = heading(yaw);
  if (full || hd != s.arrow) { b.set("#SkyyMmArrow.AssetPath", s.arrows[hd]); s.arrow = hd; }
  boolean fm = reb || s.forceMk;
  if (fm || crossed || s.markersDirty) markers(s, b, px, pz, fm);
  s.forceMk = false;
  if (reb) { for (int i = 0; i < @QPT@; i++) if (s.ptX[i] != -4000) s.ptX[i] = -4001; s.nextPartyAt = 0L; }
  if (pan) for (int i = 0; i < @QPT@; i++) if (s.ptRim[i] && s.ptX[i] != -4000) rimDot(s, b, i, px, pz);
}""")
# the geometry of a session from its layout (WLayout Minimap + the admin's caps)
MMM(mmmain, r"""
public static void geometry(@PKG@.MmSess s, @PKG@.WLayout l) {
  int[] v = @PKG@.MmCfg.dec(l.mm);
  s.S = 160 * @PKG@.MmCfg.snapScale(l.scale) / 100;
  s.rw = Math.max(3, s.S / 40);
  s.C = s.S - 2 * s.rw;
  int r = v[0];
  int mx = @PKG@.MmCfg.maxRadius();
  if (r > mx) r = mx;
  s.r = r;
  s.t = Math.max(2, (int) Math.round((double) s.C * 32.0 / (2.0 * (double) r)));
  s.det = @PKG@.MmCfg.detFor(s.t);
  s.dsuf = "/" + s.det;
  s.h = (s.C + 2 * s.t - 1) / (2 * s.t);
  if (2 * s.h + 1 > @QMAXW@) s.h = (@QMAXW@ - 1) / 2;
  s.w = 2 * s.h + 1;
  s.span = 2 * s.w - 1;
  s.shape = v[1];
  long u = (long) v[2];
  long mi = @PKG@.MmCfg.minIntervalMs();
  s.upd = u < mi ? mi : u;
  s.ring = v[3];
  s.msize = v[4];
  s.pcol = @PKG@.MmCfg.pcol(l.mm);
  s.ringCol = l.col == null ? "def" : l.col;
  s.mask = l.lines <= 0 ? 3 : l.lines;
  int[] dz = new int[] { 4, 6, 8 };
  s.dp = Math.max(3, (int) Math.round((double) s.S * (double) dz[s.msize] / 160.0));
  s.ap = Math.max(10, s.S * 24 / 160);
  s.slotKey = new long[s.w * s.w];
  s.slotPath = new String[s.w * s.w];
  for (int i = 0; i < s.slotKey.length; i++) s.slotKey[i] = Long.MIN_VALUE;
  for (int i = 0; i < @QMK@; i++) { s.mkX[i] = -4000; s.mkY[i] = -4000; s.mkPath[i] = null; }
  for (int i = 0; i < @QPT@; i++) { s.ptX[i] = -4000; s.ptY[i] = -4000; s.ptPath[i] = null; s.ptRim[i] = false; }
  s.arrow = -1;
}""")
# the 14 masks (7 sizes x round / square) + 16 arrows + the "not yet" picture go ONCE per connection, then ONE rebuild (critic C14)
MMM(mmmain, r"""
public static void statics(@PKG@.MmSess s) {
  if (STATICS.contains(s.uuid)) return;
  for (int z = 50; z <= 200; z = z + 25) {
    int S = 160 * z / 100;
    int C = S - 2 * Math.max(3, S / 40);
    send(s, gen("mask:" + C + ":0"), false);
    send(s, gen("mask:" + C + ":1"), false);
  }
  for (int k = 0; k < 16; k++) send(s, gen("arrow:" + k), false);
  send(s, gen("dark"), false);
  s.pr.getPacketHandler().writeNoCache(new @ARB@());
  STATICS.add(s.uuid);
}""")
MMM(mmmain, r"""
public static void pictures(@PKG@.MmSess s) {
  @PKG@.MmAsset mk = gen("mask:" + s.C + ":" + s.shape);
  s.maskRel = mk.getName().substring(@QMLEN@);
  s.dark = gen("dark").getName();
  s.arrows = new String[16];
  for (int k = 0; k < 16; k++) s.arrows[k] = gen("arrow:" + k).getName();
  int rc = @PKG@.MmPng.rgbaOf("def".equals(s.ringCol) ? null : @PKG@.Widgets.hexOf(s.ringCol));
  @PKG@.MmAsset rg = gen("ring:" + s.S + ":" + s.rw + ":" + s.shape + ":" + rc);
  send(s, rg, false);
  s.ringPath = rg.getName();
  int[] kc = new int[] { @CWAY@, @CDEATH@, @CHOME@, @CPLAYER@ };
  s.kindPath = new String[4];
  for (int k = 0; k < 4; k++) { @PKG@.MmAsset d = gen("dot:" + kc[k]); send(s, d, false); s.kindPath[k] = d.getName(); }
  int pc = "def".equals(s.pcol) ? @CPARTY@ : @PKG@.MmPng.rgbaOf(@PKG@.Widgets.hexOf(s.pcol));
  @PKG@.MmAsset pd = gen("dot:" + pc);
  send(s, pd, false);
  s.partyPath = pd.getName();
}""")
# the document for a geometry, built once on THIS thread and cached (critic C10): MmHud.show() hands it over on the world thread
MMM(mmmain, r"""
public static @UCB@ doc(@PKG@.MmSess s, String anc) {
  String k = anc + "|" + s.S + "|" + s.C + "|" + s.t + "|" + s.w + "|" + s.dp + "|" + s.ap + "|" + s.ring + "|" + s.maskRel + "|" + s.ringPath + "|" + s.dark + "|" + s.arrows[0] + "|" + s.kindPath[0];
  Object o = DOCS.get(k);
  if (o != null) return (@UCB@) o;
  @UCB@ b = new @UCB@();
  String pth = s.dark;
  int gl = groupPos(16.0, 0, s.C, s.t);
  int gt = gl;
  b.appendInline((String) null, "Group #SkyyMmRoot { Anchor: (Full: 0); }");
  b.appendInline("#SkyyMmRoot", @@J_BOX@@);
  b.appendInline("#SkyyMmBox", @@J_CLIP@@);
  b.appendInline("#SkyyMmClip", @@J_GRID@@);
  for (int i = 0; i < s.w * s.w; i++) b.appendInline("#SkyyMmGrid", @@J_TILE@@);
  pth = s.kindPath[0];
  for (int i = 0; i < @QMK@; i++) b.appendInline("#SkyyMmGrid", @@J_MK@@);
  pth = s.partyPath;
  for (int i = 0; i < @QPT@; i++) b.appendInline("#SkyyMmGrid", @@J_PT@@);
  pth = s.arrows[0];
  b.appendInline("#SkyyMmBox", @@J_ARROW@@);
  if (s.ring == 1) { pth = s.ringPath; b.appendInline("#SkyyMmBox", @@J_RING@@); }
  DOCS.put(k, b);
  if (DOCS.size() > 64) { java.util.Iterator it = DOCS.keySet().iterator(); it.next(); it.remove(); }
  return b;
}""")
MMM(mmmain, r"""
public static void recountTaps() {
  TAPS = SESS.size();
}""")
# world thread: register the HUD with the player's HudManager (its own key; skyyhud_main is never touched) - only while the player is still in
# the world (store) the request was made in
MMM(mmmain, r"""
public static void attachNow(@PKG@.MmSess s, @PKG@.MmHud h, @ST@ st) {
  if (s == null || h == null || h.ended) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != st) { h.gone = true; return; }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { h.gone = true; return; }
    p.getHudManager().addCustomHud(s.pr, h);
    h.attached = true;
  } catch (Throwable t) { h.gone = true; err("showing the minimap HUD", t); }
}""")
MMM(mmmain, r"""
public static void detachNow(@PR@ pr, @ST@ st, @PKG@.MmHud h) {
  try {
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != st) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    @HM@ hm = p.getHudManager();
    if (hm.getCustomHud("@MMKEY@") == h) hm.removeCustomHud(pr, "@MMKEY@");
  } catch (Throwable t) { err("removing the minimap HUD", t); }
}""")
MMM(mmmain, r"""
public static void detach(@PKG@.MmSess s, String why) {
  @PKG@.MmHud h = s.hud;
  s.hud = null;
  s.posKnown = false;
  if (h == null) return;
  h.ended = true;
  if (s.world != null && s.pr != null && s.store != null) {
    try { s.world.execute(new @PKG@.MmDetach(s.pr, s.store, h)); } catch (Throwable t) { err("reaching the world thread to remove the minimap", t); }
  }
}""")
MMM(mmmain, r"""
public static @PKG@.WLayout layout(java.util.UUID u) {
  try { return (@PKG@.WLayout) @PKG@.LayoutStore.get(u).get("Minimap"); } catch (Throwable t) { return null; }
}""")
# fix round: what a document draws (re-attach only when this changes - critic: any editor / settings click re-sent the whole minimap)
MMM(mmmain, "public static String drawKey(@PKG@.MmSess g) { return g.S + \"|\" + g.C + \"|\" + g.t + \"|\" + g.w + \"|\" + g.ap + \"|\" + g.ring + \"|\" + g.shape; }")
# fix round: an Anchor object from Widgets.anchorSrcWH's text "(Top: 40, Right: 8, Width: 160, Height: 160)" (one push moves the box)
MMM(mmmain, r"""
public static @ANC@ ancObj(String src) {
  @ANC@ a = new @ANC@();
  String t = src.trim();
  if (t.startsWith("(")) t = t.substring(1);
  if (t.endsWith(")")) t = t.substring(0, t.length() - 1);
  String[] p = t.split(",");
  for (int i = 0; i < p.length; i++) {
    int c = p[i].indexOf(':');
    if (c < 0) continue;
    String k = p[i].substring(0, c).trim();
    int v = Integer.parseInt(p[i].substring(c + 1).trim());
    @VAL@ x = @VAL@.of(Integer.valueOf(v));
    if (k.equals("Top")) a.setTop(x);
    else if (k.equals("Bottom")) a.setBottom(x);
    else if (k.equals("Left")) a.setLeft(x);
    else if (k.equals("Right")) a.setRight(x);
    else if (k.equals("Width")) a.setWidth(x);
    else if (k.equals("Height")) a.setHeight(x);
  }
  return a;
}""")
# fix round: the same frame, other settings - only what changed goes out (the box Anchor, the ring picture, the update speed, markers,
# party colour, marker size, the detail); no new document, the map stays
MMM(mmmain, r"""
public static void soft(@PKG@.MmSess s, @PKG@.MmSess g, String anc, @PKG@.MmHud h, long now) {
  @UCB@ b = new @UCB@();
  if (!anc.equals(s.anc)) { b.setObject("#SkyyMmBox.Anchor", ancObj(anc)); s.anc = anc; }
  s.upd = g.upd;
  if (s.nextPanAt > now + s.upd) s.nextPanAt = now + s.upd;
  s.r = g.r;
  if (s.mask != g.mask) { s.mask = g.mask; s.markersDirty = true; s.nextPartyAt = 0L; }
  if (s.msize != g.msize || s.dp != g.dp) {
    s.msize = g.msize;
    s.dp = g.dp;
    s.forceMk = true;
    s.markersDirty = true;
    for (int i = 0; i < @QPT@; i++) if (s.ptX[i] != -4000) s.ptX[i] = -4001;
    s.nextPartyAt = 0L;
  }
  String oldRing = s.ringPath;
  String oldParty = s.partyPath;
  s.pcol = g.pcol;
  s.ringCol = g.ringCol;
  pictures(s);
  if (s.ring == 1 && s.ringPath != null && !s.ringPath.equals(oldRing)) b.set("#SkyyMmRing.AssetPath", s.ringPath);
  if (s.partyPath != null && !s.partyPath.equals(oldParty)) s.nextPartyAt = 0L;
  if (g.det != s.det) { s.det = g.det; s.dsuf = g.dsuf; s.needFull = true; }
  if (b.getCommands().length > 0) h.push(b);
}""")
# the gates (widget on, admin on, BetterMap found, world not disabled, the world has a map, its map stream started), then the pictures, the
# cached document and the attach on the world thread; force = a world change (a new HUD always); otherwise an unchanged frame is updated
# in place (soft)
MMM(mmmain, r"""
public static void attach(@PKG@.MmSess s, long now, boolean force) {
  @PKG@.WLayout l = layout(s.uuid);
  boolean want = l != null && l.en && @PKG@.MmCfg.ENABLED && @PKG@.MmCfg.BM == 1;
  if (want != s.wants) s.wants = want;
  if (!want) { s.pending = false; detach(s, "off"); return; }
  if (s.world == null || s.store == null) return;
  if (@PKG@.MmCfg.worldDisabled(s.wname)) { s.pending = false; detach(s, "world disabled"); return; }
  boolean map = false;
  try { @WMM@ wm = s.world.getWorldMapManager(); map = wm != null && wm.isWorldMapEnabled(); } catch (Throwable t) { map = false; }
  if (!map) { s.pending = false; detach(s, "no map"); return; }
  // fix round (critic: an island with the map on but no stream showed an empty disc for 15 s): wait for the first map packet
  if (!s.streamSeen) {
    if (s.hud != null) detach(s, "no stream yet");
    if (!s.pending) { s.pending = true; s.pendingSince = now; s.pendLogged = false; }
    return;
  }
  s.pending = false;
  @PKG@.MmHud cur = s.hud;
  if (!force && cur != null && cur.attached && !cur.gone && !cur.ended && s.dkey != null) {
    @PKG@.MmSess g = new @PKG@.MmSess(s.pr);
    g.uuid = s.uuid;
    geometry(g, l);
    if (drawKey(g).equals(s.dkey)) { soft(s, g, @PKG@.Widgets.anchorSrcWH(l, g.S, g.S), cur, now); return; }
  }
  geometry(s, l);
  statics(s);
  pictures(s);
  String anc = @PKG@.Widgets.anchorSrcWH(l, s.S, s.S);
  @UCB@ d = doc(s, anc);
  s.anc = anc;
  s.dkey = drawKey(s);
  @PKG@.MmHud h = new @PKG@.MmHud(s.pr, s, d);
  @PKG@.MmHud old = s.hud;
  if (old != null) old.ended = true;
  s.hud = h;
  s.needFull = true;
  s.more = false;
  s.attachAt = now;
  s.nextPanAt = 0L;
  s.nextPartyAt = 0L;
  s.fillLogged = false;
  s.fillNs = 0L;
  s.encodes = 0; s.hits = 0; s.dedup = 0; s.sweepHit = 0; s.sweepMiss = 0; s.pics = 0; s.sentBytes = 0L;
  try { s.world.execute(new @PKG@.MmAttach(s, h, s.store)); }
  catch (Throwable t) { h.gone = true; err("reaching the world thread to show the minimap", t); }
}""")
MMM(mmmain, r"""
public static @PKG@.MmSess sess(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  for (int tries = 0; tries < 8; tries++) {
    @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(u);
    if (s != null && s.pr == pr) return s;
    @PKG@.MmSess n = new @PKG@.MmSess(pr);
    n.fresh = true;
    n.wants = @PKG@.MmCfg.ENABLED;
    if (s == null) { if (SESS.putIfAbsent(u, n) == null) return n; }
    // a reconnect before the old connection's quit was handled (fix round): the new connection owns the uuid from now on
    else if (SESS.replace(u, s, n)) { s.wants = false; return n; }
  }
  return (@PKG@.MmSess) SESS.get(u);
}""")
# a fresh session (a new connection) taken over on the minimap thread: the uuid's per-connection lists start empty (the new client has no
# picture yet) - fix round, fast reconnect
MMM(mmmain, r"""
public static void own(@PKG@.MmSess s) {
  if (!s.fresh) return;
  s.fresh = false;
  DELIVERED.remove(s.uuid);
  STATICS.remove(s.uuid);
  CAPPED.remove(s.uuid);
}""")
MMM(mmmain, r"""
public static void drop(@PKG@.MmSess s) {
  detach(s, "gone");
  SESS.remove(s.uuid, s);
  s.wants = false;
  s.q.clear();
  s.qn.set(0);
  s.qc.set(0);
  s.known.clear();
  s.streamed.clear();
  s.markers.clear();
  s.world = null;
  s.store = null;
  DELIVERED.remove(s.uuid);
  STATICS.remove(s.uuid);
  CAPPED.remove(s.uuid);
  recountTaps();
}""")
MMM(mmmain, r"""
public static void handle(@PKG@.MmReq r, long now) {
  if (r == null || r.kind == null || r.uuid == null) return;
  if (r.kind.equals("quit")) {
    @PKG@.MmSess q = (@PKG@.MmSess) SESS.get(r.uuid);
    // a NEWER connection of this player already owns the uuid (fast reconnect - fix round): own() clears its lists, not this quit
    if (q != null && q.pr != r.pr) return;
    if (q != null) drop(q);
    DELIVERED.remove(r.uuid);
    STATICS.remove(r.uuid);
    CAPPED.remove(r.uuid);
    return;
  }
  if (@PKG@.MmCfg.BM != 1) return;
  if (r.kind.equals("ready")) {
    @PKG@.MmSess o = (@PKG@.MmSess) SESS.get(r.uuid);
    if (o != null && o.pr != r.pr && !r.pr.isValid()) return;
    @PKG@.MmSess s = sess(r.pr);
    own(s);
    s.world = r.world;
    s.store = r.store;
    s.wuuid = r.pr.getWorldUuid();
    try { s.wname = r.world == null ? "?" : r.world.getName(); } catch (Throwable t) { s.wname = "?"; }
    s.posKnown = false;
    recountTaps();
    attach(s, now, true);
    return;
  }
  if (r.kind.equals("layout")) {
    @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(r.uuid);
    if (s != null && s.world != null) { own(s); attach(s, now, false); }
  }
}""")
MMM(mmmain, r"""
public static void fillLog(@PKG@.MmSess s, long now) {
  s.fillLogged = true;
  int real = 0;
  for (int i = 0; i < s.slotPath.length; i++) if (s.slotPath[i] != null && !s.slotPath[i].equals(s.dark)) real = real + 1;
  info("minimap: first fill " + s.who + " in '" + s.wname + "': " + real + " of " + s.slotPath.length + " pieces (" + s.encodes + " shrunk, " + s.hits + " from the cache, "
    + s.dedup + " already on the client, " + s.sweepHit + " from the engine cache, " + s.sweepMiss + " not in it yet), " + s.pics + " pictures / " + ((s.sentBytes + 512L) / 1024L)
    + " KB sent, " + (s.fillNs / 1000000L) + "." + ((s.fillNs / 100000L) % 10L) + " ms on SkyyHud-Minimap, " + (now - s.attachAt) + " ms after the attach");
}""")
MMM(mmmain, r"""
public static boolean noStreamLog(String k) {
  boolean first = false;
  synchronized (NOSTREAM) { first = NOSTREAM.size() < 256 && NOSTREAM.add(k); }
  return first;
}""")
MMM(mmmain, r"""
public static void noStream(@PKG@.MmSess s) {
  String k = s.wname == null ? "?" : s.wname;
  if (noStreamLog(k)) info("minimap: no map stream in world '" + k + "' - hidden there (it shows once a map packet comes)");
  detach(s, "no stream");
  s.pending = true;
  s.pendingSince = System.currentTimeMillis();
  s.pendLogged = true;
}""")
# one player per call (inside its own catch in tick0): drain, the gates, then at most one update (pan / pieces / dots)
MMM(mmmain, r"""
public static void step(@PKG@.MmSess s, long now, int[] budget, long deadline) {
  @PR@ pr = s.pr;
  if (pr == null || !pr.isValid()) { drop(s); return; }
  own(s);
  drain(s);
  if (s.pending && s.hud == null) {
    if (s.streamSeen) attach(s, now, true);
    else if (!s.pendLogged && now - s.pendingSince > @QSTREAM@L) {
      s.pendLogged = true;
      String k = s.wname == null ? "?" : s.wname;
      if (noStreamLog(k)) info("minimap: no map stream in world '" + k + "' - not shown there (it shows once a map packet comes)");
    }
  }
  @PKG@.MmHud h = s.hud;
  if (h == null) return;
  if (h.gone || h.ended) { if (s.hud == h) s.hud = null; s.posKnown = false; return; }
  if (!h.attached) return;
  if (!@PKG@.MmCfg.ENABLED) { detach(s, "admin off"); return; }
  if (!s.streamSeen && now - s.attachAt > @QSTREAM@L) { noStream(s); return; }
  java.util.UUID wu = pr.getWorldUuid();
  if (wu == null || !wu.equals(s.wuuid)) { s.posKnown = false; return; }
  com.hypixel.hytale.math.vector.Transform tr = pr.getTransform();
  if (tr == null || tr.getPosition() == null) return;
  double x = tr.getPosition().x;
  double z = tr.getPosition().z;
  float yaw = 0.0f;
  com.hypixel.hytale.math.vector.Rotation3f hr = pr.getHeadRotation();
  if (hr != null) yaw = hr.yaw();
  if (!s.posKnown) { s.ccx = chunkOf(x); s.ccz = chunkOf(z); }
  s.posKnown = true;
  s.px = x;
  s.pz = z;
  // fix round (critic: marker changes and leftovers pushed every 0.25 s past the player's / admin's update rate): only the first fill
  // goes faster; the arrow alone follows a turn at once (one Set, only when the heading changes)
  boolean due = s.needFull || now >= s.nextPanAt || (s.more && !s.fillLogged);
  boolean pt = now >= s.nextPartyAt;
  int hd = heading(yaw);
  boolean turn = !due && s.arrow >= 0 && hd != s.arrow;
  if (!due && !pt && !turn) return;
  long t0 = System.nanoTime();
  @UCB@ b = new @UCB@();
  if (due) { move(s, b, x, z, yaw, budget, deadline, s.needFull); s.needFull = false; if (now >= s.nextPanAt) s.nextPanAt = now + s.upd; }
  else if (turn) { b.set("#SkyyMmArrow.AssetPath", s.arrows[hd]); s.arrow = hd; }
  if (pt) { party(s, b); s.nextPartyAt = now + 1000L; }
  if (b.getCommands().length > 0 && h.push(b)) s.updates = s.updates + 1;
  if (!s.fillLogged) { s.fillNs = s.fillNs + (System.nanoTime() - t0); if (!s.more) fillLog(s, now); }
}""")
MMM(mmmain, r"""
public static void relayoutAll(long now) {
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MmSess s = (@PKG@.MmSess) it.next();
    try { if (s.world != null) { own(s); attach(s, now, false); } } catch (Throwable t) { err("re-laying a minimap out", t); }
  }
}""")
# fix round (critic: 10 players filling got 2 pieces each per tick): the time budget and the piece cap grow with the players still filling -
# 3 ms + 1 ms per extra one (10 ms at most); tilesPerTick x (1-3) pieces (64 at most)
MMM(mmmain, r"""
public static long budgetNs(int needy) {
  long b = @QBUDGET@L + (long) Math.max(0, needy - 1) * @QBSTEP@L;
  return b > @QBMAX@L ? @QBMAX@L : b;
}""")
MMM(mmmain, r"""
public static int pieceCap(int needy) {
  int c = @PKG@.MmCfg.tilesPerTick() * Math.max(1, Math.min(3, needy));
  return c > 64 ? 64 : c;
}""")
# the tick (minimap thread): requests, then every player ROUND-ROBIN with a share of the encode budget (critic C13)
MMM(mmmain, r"""
public static void tick0() {
  long now = System.currentTimeMillis();
  LAST_THREAD = Thread.currentThread().getName();
  TICKS = TICKS + 1L;
  int guard = 0;
  while (guard < 10000) {
    Object o = REQ.poll();
    if (o == null) break;
    guard = guard + 1;
    try { handle((@PKG@.MmReq) o, now); } catch (Throwable t) { err("a minimap request", t); }
  }
  if (RELAYOUT) { RELAYOUT = false; relayoutAll(now); }
  Object[] all = SESS.values().toArray();
  int n = all.length;
  if (n == 0) return;
  int needy = 0;
  for (int i = 0; i < n; i++) { @PKG@.MmSess a = (@PKG@.MmSess) all[i]; if (a.hud != null && (a.more || a.needFull)) needy = needy + 1; }
  int cap = pieceCap(needy);
  long deadline = System.nanoTime() + budgetNs(needy);
  int per = Math.max(2, cap / Math.max(1, needy));
  int left = cap;
  int start = RR % n;
  RR = (RR + 1) % 1000000;
  for (int k = 0; k < n; k++) {
    @PKG@.MmSess s = (@PKG@.MmSess) all[(start + k) % n];
    int give = Math.min(per, left);
    int[] budget = new int[] { give };
    try { step(s, now, budget, deadline); } catch (Throwable t) { s.errors = s.errors + 1; err("a player's minimap", t); }
    left = left - (give - budget[0]);
  }
  // the leftover (players with nothing to fill gave theirs back) goes round again to those still filling, in the same order
  for (int k = 0; k < n && left > 0 && System.nanoTime() < deadline; k++) {
    @PKG@.MmSess s = (@PKG@.MmSess) all[(start + k) % n];
    if (s.hud == null || !s.more) continue;
    int[] budget = new int[] { left };
    try { step(s, now, budget, deadline); } catch (Throwable t) { s.errors = s.errors + 1; err("a player's minimap", t); }
    left = budget[0];
  }
  trimCache();
}""")
MMM(mmmain, r"""
public static void tickLocked() {
  long t = System.currentTimeMillis();
  TICK_THREAD = Thread.currentThread();
  TICK_START = t;
  LAST_TICK = t;
  IN_TICK = true;
  try { tick0(); } catch (Throwable x) { err("the minimap tick", x); }
  IN_TICK = false;
  LAST_TICK = System.currentTimeMillis();
}""")
# fix round (critic: a tick hung inside the lock - the watchdog's new thread blocked on it, one leaked thread every 5 s): the tick marks
# itself AFTER taking the lock; a stuck tick is interrupted and logged, never doubled
MMM(mmmain, r"""
public static void tick() {
  try {
    synchronized (LOCK) { tickLocked(); }
  } catch (Throwable t) { err("the minimap tick", t); }
}""")
MMM(mmmain, r"""
public static synchronized void ensureExec() {
  if (EXEC != null) return;
  try {
    java.util.concurrent.ScheduledExecutorService e = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.MmThreads());
    FUT = e.scheduleWithFixedDelay(new @PKG@.MmTick(), @QTICK@L, @QTICK@L, java.util.concurrent.TimeUnit.MILLISECONDS);
    EXEC = e;
    LAST_TICK = System.currentTimeMillis();
  } catch (Throwable t) { err("starting the SkyyHud-Minimap thread", t); }
}""")
# the 1 s HUD tick (shared scheduler) watches the minimap thread: no tick for 5 s while players have a minimap = a new thread (logged once)
MMM(mmmain, r"""
public static String frames(Thread t) {
  if (t == null) return "?";
  StringBuilder sb = new StringBuilder();
  try {
    StackTraceElement[] st = t.getStackTrace();
    for (int i = 0; i < st.length && i < 3; i++) { if (i > 0) sb.append(" < "); sb.append(String.valueOf(st[i])); }
  } catch (Throwable x) { sb.append("?"); }
  return sb.length() == 0 ? "?" : sb.toString();
}""")
MMM(mmmain, r"""
public static synchronized void watchdog() {
  if (EXEC == null || SESS.isEmpty()) return;
  long now = System.currentTimeMillis();
  if (IN_TICK) {
    if (now - TICK_START < 5000L) return;
    long at = TICK_START;
    if (HUNG_AT == at) return;
    HUNG_AT = at;
    Thread t = TICK_THREAD;
    warn("minimap: a minimap tick is stuck for " + ((now - at) / 1000L) + " s at " + frames(t) + " - interrupted it (no second thread: it would wait on the same lock)");
    try { if (t != null) t.interrupt(); } catch (Throwable x) { }
    return;
  }
  if (now - LAST_TICK < 5000L) return;
  if (RESTARTS >= 3) {
    if (!WD_LOGGED) { WD_LOGGED = true; warn("minimap: the SkyyHud-Minimap thread stopped 3 times - not restarted again (the minimap waits until the server restarts)"); }
    return;
  }
  RESTARTS = RESTARTS + 1;
  java.util.concurrent.ScheduledExecutorService old = EXEC;
  EXEC = null;
  try { old.shutdownNow(); } catch (Throwable t) { }
  warn("minimap: the SkyyHud-Minimap thread stopped ticking - started a new one (" + RESTARTS + " of 3)");
  ensureExec();
}""")
MMM(mmmain, r"""
public static void submit(@PKG@.MmReq r) {
  REQ.add(r);
  ensureExec();
}""")
# THE TAP (the thread that writes the packet): the reference only - one volatile read when no minimap runs, never a lock, never a throw
MMM(mmmain, r"""
public static void tap(@PR@ pr, Object p) {
  if (TAPS == 0 || pr == null || p == null) return;
  boolean up = p instanceof @UWM@;
  if (!up && !(p instanceof @CWM@)) return;
  @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(pr.getUuid());
  if (s == null || s.pr != pr) return;
  if (s.qn.incrementAndGet() > @QMAX@) { s.qn.decrementAndGet(); s.dropped.incrementAndGet(); return; }
  if (up) {
    @UWM@ u = (@UWM@) p;
    @MCH@[] cs = u.chunks;
    int n = cs == null ? 0 : cs.length;
    if (n > 0 && s.qc.addAndGet(n) > @QCHUNKS@) {
      s.qc.addAndGet(-n);
      // past the image bound: the chunk keys only (the pieces are not held; the engine cache serves them) + the markers as they came
      int m = 0;
      for (int i = 0; i < n; i++) if (cs[i] != null && cs[i].image != null) m = m + 1;
      long[] ks = new long[m];
      int j = 0;
      for (int i = 0; i < n && j < m; i++) if (cs[i] != null && cs[i].image != null) { ks[j] = key(cs[i].chunkX, cs[i].chunkZ); j = j + 1; }
      s.q.add(ks);
      s.keysOnly.incrementAndGet();
      if (u.addedMarkers != null || u.removedMarkers != null) {
        if (s.qn.incrementAndGet() > @QMAX@) { s.qn.decrementAndGet(); s.dropped.incrementAndGet(); return; }
        s.q.add(new @UWM@((@MCH@[]) null, u.addedMarkers, u.removedMarkers));
      }
      return;
    }
  }
  s.q.add(p);
}""")
MMM(mmmain, r"""
public static synchronized void tapOn() {
  if (TAPF != null) return;
  try {
    TAPF = @PAD@.registerOutbound((@PPW@) new @PKG@.MmTap());
  } catch (Throwable t) { TAPF = null; err("registering the map packet tap", t); }
}""")
MMM(mmmain, r"""
public static synchronized void tapOff() {
  @PF@ f = TAPF;
  TAPF = null;
  if (f != null) { try { @PAD@.deregisterOutbound(f); } catch (Throwable t) { } }
}""")
# BetterMap, checked ONCE (the first player connect): the engine's PluginManager only - never a BetterMap class (AGPL, clean room)
MMM(mmmain, r"""
public static synchronized void checkBM() {
  if (@PKG@.MmCfg.BM != 0) return;
  boolean ok = false;
  String ver = "";
  try {
    @PB@ pb = @PLM@.get().getPlugin(new @PID@("dev.ninesliced", "BetterMap"));
    if (pb != null && pb.isEnabled()) {
      ok = true;
      try { ver = String.valueOf(pb.getManifest().getVersion()); } catch (Throwable t) { ver = "?"; }
    }
  } catch (Throwable t) { ok = false; }
  @PKG@.MmCfg.BMV = ver;
  @PKG@.MmCfg.BM = ok ? 1 : 2;
  if (ok) { info("minimap: BetterMap " + ver + " found - minimap " + (@PKG@.MmCfg.ENABLED ? "on" : "off in Server Setup for now")); tapOn(); }
  else info("minimap: BetterMap (dev.ninesliced:BetterMap) is not installed or disabled - the minimap widget stays off");
}""")
# PlayerConnectEvent (before the first world's map burst): the session exists early, so the tap keeps the burst's keys
MMM(mmmain, r"""
public static void hello(@PR@ pr) {
  if (pr == null) return;
  if (@PKG@.MmCfg.BM == 0) checkBM();
  if (@PKG@.MmCfg.BM != 1) return;
  sess(pr);
  recountTaps();
  ensureExec();
}""")
# SkyyHud's AttachTask (world thread, PlayerReadyEvent + 1.5 s, after the main HUD): ONE cheap request
MMM(mmmain, r"""
public static void ready(@PR@ pr, @ST@ st) {
  if (pr == null || st == null) return;
  if (@PKG@.MmCfg.BM == 0) checkBM();
  if (@PKG@.MmCfg.BM != 1) return;
  @WLD@ w = null;
  try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
  if (w == null) return;
  submit(new @PKG@.MmReq("ready", pr, w, st));
}""")
MMM(mmmain, r"""
public static void quit(@PR@ pr) {
  if (pr == null || EXEC == null) return;
  submit(new @PKG@.MmReq("quit", pr, null, null));
}""")
# the editor / settings / commands changed a layout (SkyyHudPlugin.rebuildFor): re-lay this player's minimap out on the minimap thread
MMM(mmmain, r"""
public static void relayout(java.util.UUID u) {
  if (u == null || @PKG@.MmCfg.BM != 1 || !SESS.containsKey(u)) return;
  @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(u);
  if (s == null) return;
  @PKG@.MmReq r = new @PKG@.MmReq("layout", s.pr, null, null);
  submit(r);
}""")
# kit after= hook of the Server Setup rows that change what is drawn (static void m(String key))
MMM(mmmain, "public static void cfgChanged(String key) { RELAYOUT = true; }")
MMM(mmmain, r"""
public static void shutdown0() {
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) { @PKG@.MmSess s = (@PKG@.MmSess) it.next(); try { detach(s, "server stop"); } catch (Throwable t) { } }
  SESS.clear();
  REQ.clear();
  DELIVERED.clear();
  STATICS.clear();
  CAPPED.clear();
  CACHE.clear();
  DOCS.clear();
  TAPS = 0;
}""")
MMM(mmmain, r"""
public static void shutdown() {
  tapOff();
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  EXEC = null;
  try { if (e != null) e.shutdownNow(); } catch (Throwable t) { }
  synchronized (LOCK) { shutdown0(); }
}""")
# fix round: the /skyyhud minimap on | off answer - why nothing shows when the server says no
MMM(mmmain, r"""
public static String onText(boolean on, String world) {
  if (@PKG@.MmCfg.BM == 2) return "[SkyyHud] the minimap needs BetterMap - it is not installed on this server";
  if (!on) return "[SkyyHud] minimap off";
  if (!@PKG@.MmCfg.ENABLED) return "[SkyyHud] minimap on - but the server has the minimap switched off (Server Setup -> Minimap)";
  if (world != null && @PKG@.MmCfg.worldDisabled(world)) return "[SkyyHud] minimap on - it is not shown in this world";
  return "[SkyyHud] minimap on";
}""")
MMM(mmmain, r"""
public static String bmText() {
  int b = @PKG@.MmCfg.BM;
  if (b == 1) return "BetterMap " + @PKG@.MmCfg.BMV + " found - the minimap reads the map it streams.";
  if (b == 2) return "BetterMap is not installed on this server - the minimap is off.";
  return "BetterMap not checked yet (it is checked when the first player joins).";
}""")

# ---- the small bodies
MMM(mmtick, "public void run() { @PKG@.Minimap.tick(); }")
MMM(mmatt, "public void run() { @PKG@.Minimap.attachNow(this.sess, this.hud, this.store); }")
MMM(mmdet, "public void run() { @PKG@.Minimap.detachNow(this.pr, this.store, this.hud); }")
MMM(mmtap, "public void accept(@PR@ pr, @PKT@ p) { try { @PKG@.Minimap.tap(pr, p); } catch (Throwable t) { @PKG@.Minimap.TAPERR.incrementAndGet(); } }")
MMM(mmcon, "public void accept(Object ev) { try { @PKG@.Minimap.hello(((@PCE@) ev).getPlayerRef()); } catch (Throwable t) { } }")
MMM(mmquit, "public void accept(Object ev) { try { @PKG@.Minimap.quit(((@PDE@) ev).getPlayerRef()); } catch (Throwable t) { } }")

# ---------------------------------------------------------------- MmUi: the settings page (kit markup made by tools/hud_0_3_14_patch.py)
MMUI_JAVA = @@MMUI_JAVA@@
MMM(mmui, r"""
public static void settings(@UCB@ b, @UEB@ ev, @PR@ pr) {
  @PKG@.WLayout l = (@PKG@.WLayout) @PKG@.LayoutStore.get(pr.getUuid()).get("Minimap");
  if (l == null) return;
  int[] v = @PKG@.MmCfg.dec(l.mm);
  String pcol = @PKG@.MmCfg.pcol(l.mm);
  String rc = l.col == null ? "def" : l.col;
  boolean en = l.en;
  int mk = l.lines <= 0 ? 3 : l.lines;
  int sc = @PKG@.MmCfg.snapScale(l.scale);
  int mx = @PKG@.MmCfg.maxRadius();
  long mi = @PKG@.MmCfg.minIntervalMs();
  String zoomHint = "up to " + mx + " here";
  String speedHint = "fastest here: " + @PKG@.MmCfg.secText(mi) + " s";
  String partyHint = @PKG@.MmCfg.PARTY_DOTS ? "Your party in this world; off the map = on the rim." : "Party dots are off on this server.";
  String othersHint = @PKG@.MmCfg.OTHER_PLAYERS ? "Players the big map shows you." : "Other-player dots are off on this server.";
  String bmText = @PKG@.Minimap.bmText();
""" + MMUI_JAVA + r"""
}""")
# a click: 0 = nothing, 1 = back, 2 = changed (saved; the caller re-sends the HUDs and rebuilds the page)
MMM(mmui, r"""
public static int click(@PR@ pr, String data) {
  if (data == null) return 0;
  int p = data.indexOf("\"mm:");
  if (p < 0) return 0;
  int q = data.indexOf('"', p + 4);
  if (q < 0) return 0;
  String a = data.substring(p + 4, q);
  if (a.equals("back")) return 1;
  java.util.UUID u = pr.getUuid();
  @PKG@.WLayout l = (@PKG@.WLayout) @PKG@.LayoutStore.get(u).get("Minimap");
  if (l == null) return 0;
  int[] v = @PKG@.MmCfg.dec(l.mm);
  String pc = @PKG@.MmCfg.pcol(l.mm);
  int c = a.indexOf(':');
  String k = c < 0 ? a : a.substring(0, c);
  String val = c < 0 ? "" : a.substring(c + 1);
  if (k.equals("reset")) { v = @PKG@.MmCfg.dec(""); pc = "def"; l.lines = 3; l.col = "def"; l.scale = 100; }
  else if (k.equals("en")) l.en = val.equals("1");
  else if (k.equals("z")) { int z = @PKG@.MmCfg.num(val); if (!@PKG@.MmCfg.isRadius(z) || z > @PKG@.MmCfg.maxRadius()) return 0; v[0] = z; }
  else if (k.equals("sz")) { int z = @PKG@.MmCfg.num(val); if (z < 50 || z > 200) return 0; l.scale = @PKG@.MmCfg.snapScale(z); }
  else if (k.equals("s")) { if (val.equals("0")) v[1] = 0; else if (val.equals("1")) v[1] = 1; else return 0; }
  else if (k.equals("u")) { int z = @PKG@.MmCfg.num(val); if (z != 250 && z != 500 && z != 1000) return 0; v[2] = z; }
  else if (k.equals("g")) { if (val.equals("0")) v[3] = 0; else if (val.equals("1")) v[3] = 1; else return 0; }
  else if (k.equals("ms")) { int z = @PKG@.MmCfg.num(val); if (z < 0 || z > 2) return 0; v[4] = z; }
  else if (k.equals("mk")) {
    int d = val.indexOf(':');
    if (d < 0) return 0;
    int bit = @PKG@.MmCfg.num(val.substring(0, d));
    if (bit != 1 && bit != 2 && bit != 4) return 0;
    int m = l.lines <= 0 ? 3 : l.lines;
    l.lines = val.substring(d + 1).equals("1") ? (m | bit) : (m & ~bit);
    if (l.lines == 0) l.lines = 8;
  }
  else if (k.equals("rc")) { int i = @PKG@.WLayout.palIdx(val); if (i < 0 || i >= @PKG@.WLayout.TEXT_N) return 0; l.col = val; }
  else if (k.equals("pc")) { if (!@PKG@.MmCfg.pkey(val)) return 0; pc = val; }
  else return 0;
  l.mm = @PKG@.MmCfg.enc(v, pc);
  @PKG@.Widgets.clampToScreen(l);
  @PKG@.LayoutStore.save(u);
  return 2;
}""")
'''
assert "@@MMUI_JAVA@@" in MM_BLOCK
MM_BLOCK = MM_BLOCK.replace("@@MMUI_JAVA@@", repr(MMUI_JAVA))
MM_BLOCK = MM_BLOCK.replace("@@KITCOL@@", repr(dict((k, SUI.COLOR[k]) for k in ("darkBlock", "gold", "white", "error", "success", "info",
                                                                             "progressGreen", "title"))))
for _k, _v in (("BOX", J_BOX), ("CLIP", J_CLIP), ("GRID", J_GRID), ("TILE", J_TILE), ("MK", J_MK), ("PT", J_PT), ("ARROW", J_ARROW),
               ("RING", J_RING)):
    assert MM_BLOCK.count("@@J_%s@@" % _k) == 1, _k
    assert '"""' not in _v and "@" not in _v, _v
    MM_BLOCK = MM_BLOCK.replace("@@J_%s@@" % _k, _v)
assert "@@J_" not in MM_BLOCK and "@@KITCOL@@" not in MM_BLOCK and "@@MMUI_JAVA@@" not in MM_BLOCK
rep('''# ================= HudMain =================
''', MM_BLOCK + '''
# ================= HudMain =================
''')

# ---- skyyhud_main never draws the Minimap (its own keyed HUD does)
rep('''    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null || !l.en) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{
      String[] mm = {PKG}.Widgets.modelL(ids[i], pr, l);''', '''    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null || !l.en) continue;
    if ("Minimap".equals(ids[i])) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{
      String[] mm = {PKG}.Widgets.modelL(ids[i], pr, l);''')
# ---- plugin: the minimap follows layout changes
rep('''public void rebuildFor(java.util.UUID u) {{
  {PKG}.HudMain h = ({PKG}.HudMain) this.huds.get(u);
  if (h != null) h.rebuild();
}}''', '''public void rebuildFor(java.util.UUID u) {{
  {PKG}.HudMain h = ({PKG}.HudMain) this.huds.get(u);
  if (h != null) h.rebuild();
  {PKG}.Minimap.relayout(u);
}}''')
# ---- editor: the Minimap box is its own size; Size- / Size+ move it 25 %
rep('''      this.ww.put(ids[i], Integer.valueOf({PKG}.Widgets.lineW(l, text, l.scale, 6)));''',
    '''      this.ww.put(ids[i], Integer.valueOf("Minimap".equals(ids[i]) ? l.bw * l.scale / 100 : {PKG}.Widgets.lineW(l, text, l.scale, 6)));''')
rep('''    else if (data.indexOf("act:Sm\\\\"") >= 0) l.scale -= 10;
    else if (data.indexOf("act:Sp\\\\"") >= 0) l.scale += 10;''', '''    else if (data.indexOf("act:Sm\\\\"") >= 0) l.scale -= "Minimap".equals(this.sel) ? 25 : 10;
    else if (data.indexOf("act:Sp\\\\"") >= 0) l.scale += "Minimap".equals(this.sel) ? 25 : 10;''')
# ---- the widget's Settings page = the minimap page
rep('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 17''', '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  if ("Minimap".equals(this.wid)) {{ {PKG}.MmUi.settings(b, ev, this.playerRef); return; }}
  java.util.UUID u = this.playerRef.getUuid();
  {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 17''')
rep('''    java.util.UUID u = this.playerRef.getUuid();
    {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
    if (l == null) return;
    if (data.indexOf("\\\\"back\\\\"") >= 0) {{''', '''    java.util.UUID u = this.playerRef.getUuid();
    if ("Minimap".equals(this.wid)) {{
      int mr = {PKG}.MmUi.click(this.playerRef, data);
      if (mr == 1) {{
        {PLA} mp = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
        if (mp != null) mp.getPageManager().openCustomPage(ref, st, new {PKG}.WidgetsPage(this.playerRef, this.plugin));
        return;
      }}
      if (mr == 2) {{ plugin.rebuildFor(u); rebuild(); }}
      return;
    }}
    {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
    if (l == null) return;
    if (data.indexOf("\\\\"back\\\\"") >= 0) {{''')

# ---- /skyyhud minimap [on | off]
MM_CMDS = r'''
# 0.3.14 /skyyhud minimap (its settings page) and /skyyhud minimap on | off (Adventurer, like every player subcommand)
MM_SET = """    {PKG}.WLayout ml = ({PKG}.WLayout) {PKG}.LayoutStore.get(pr.getUuid()).get("Minimap");
    if (ml == null) return;
    ml.en = %s;
    {PKG}.Widgets.clampToScreen(ml);
    {PKG}.LayoutStore.save(pr.getUuid());
    this.plugin.rebuildFor(pr.getUuid());
    String wn = null;
    try { wn = world == null ? null : world.getName(); } catch (Throwable t) { wn = null; }
    pr.sendMessage({MSG}.raw({PKG}.Minimap.onText(%s, wn)));""".replace("{PKG}", PKG).replace("{MSG}", MSG)
hud_sub(cmmon, "on", "Show your minimap", "", MM_SET % ("true", "true"))
hud_sub(cmmoff, "off", "Hide your minimap", "", MM_SET % ("false", "false"))
hud_sub(cmm, "minimap", "Your minimap settings (on | off)",
        f"""  addSubCommand(new {PKG}.HudMinimapOnCmd(p));
  addSubCommand(new {PKG}.HudMinimapOffCmd(p));""",
        f"""    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("[SkyyHud] player entity not found")); return; }}
    if (!this.plugin.huds.containsKey(pr.getUuid())) this.plugin.attach(pr);
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SettingsPage(pr, this.plugin, "Minimap"));""")
'''
rep('''cmd.addConstructor(CtNewConstructor.make(f"""
public HudCmd({PKG}.SkyyHudPlugin p) {{''', MM_CMDS + '''
cmd.addConstructor(CtNewConstructor.make(f"""
public HudCmd({PKG}.SkyyHudPlugin p) {{''')
rep('''  addSubCommand(new {PKG}.HudDefaultCmd(p));
}}""", cmd))''', '''  addSubCommand(new {PKG}.HudDefaultCmd(p));
  addSubCommand(new {PKG}.HudMinimapCmd(p));
}}""", cmd))''')

# ---- the watchdog rides the 1 s HUD tick; the attach also asks for the minimap
rep('''public void run() {
  try { plugin.tickAll(); } catch (Throwable t) { }
}""", tick))''', '''public void run() {
  try { plugin.tickAll(); } catch (Throwable t) { }
  try { com.skyy.hud.Minimap.watchdog(); } catch (Throwable t) { }
}""", tick))''')
rep('''    this.plugin.attach(pr);
  }} catch (Throwable t) {{ }}
}}""", att))''', '''    this.plugin.attach(pr);
    {PKG}.Minimap.ready(pr, st);
  }} catch (Throwable t) {{ }}
}}""", att))''')
# ---- lifecycle
rep('''  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.SkyyHudReady(this));''',
    '''  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.SkyyHudReady(this));
  // 0.3.14 minimap: the BetterMap check + the session at the first connect, the cleanup at a disconnect (no thread, no tap until then)
  {PKG}.Minimap.LOG = getLogger();
  getEventRegistry().registerGlobal({MMT["PCE"]}.class, new {PKG}.MmConnect());
  getEventRegistry().registerGlobal({MMT["PDE"]}.class, new {PKG}.MmQuit());''')
rep('''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  this.huds.clear();''', '''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Minimap.shutdown(); }} catch (Throwable t) {{ }}
  this.huds.clear();''')
rep('''getLogger().at(java.util.logging.Level.INFO).log("[SkyyHud] {VERSION} ready - /skyyhud (alias /shud); " + cs + " (admins: /skyyhud default, Server Setup -> HUD)");''',
    '''getLogger().at(java.util.logging.Level.INFO).log("[SkyyHud] {VERSION} ready - /skyyhud (alias /shud); " + cs + "; minimap " + ({PKG}.MmCfg.ENABLED ? "on (needs BetterMap, checked at the first join)" : "off (Server Setup)") + " (admins: /skyyhud default, Server Setup -> HUD / Minimap)");''')

# ---- the class list + the manifest text
rep('''ALL = (wl, lst, wid, hudc, page, sett, wpg, cmd, cexp, cimp, crst, cprv, cpro, cpls, cpsv, cpld, cpdl, cdef, cduse, cdclr, hcfg, tick, att, rdy, pl)''',
    '''ALL = (wl, lst, wid, hudc, page, sett, wpg, cmd, cexp, cimp, crst, cprv, cpro, cpls, cpsv, cpld, cpdl, cdef, cduse, cdclr, hcfg, tick, att, rdy, pl,
       mmcfg, mmpng, mmasset, mmsess, mmhud, mmreq, mmmain, mmui, mmtick, mmthr, mmatt, mmdet, mmtap, mmcon, mmquit, cmm, cmmon, cmmoff)''')
rep('''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 12 widgets incl.''',
    '''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 13 widgets incl. a round minimap (needs BetterMap; reads the map it streams, shrunk on its own thread),''')
rep('''server default layout for new players (in-game admin config). Zero dependencies.",''',
    '''server default layout for new players (in-game admin config). No hard dependencies: the minimap stays off without BetterMap.",''')

out = s.replace(LF, NL)
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(%d lines)" % out.count(LF))
