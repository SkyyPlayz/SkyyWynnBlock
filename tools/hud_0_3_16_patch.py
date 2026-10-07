"""Derive SkyyHud/build_skyyhud_0.3.16.py from the generated 0.3.15 (the SET pin: 0.3.14 minimap + 0.3.15 Dynamic Seasons mover - both
kept; 0.3.15 is left untouched; line endings preserved).
0.3.16 = the minimap fix round from Skyy's test of 0.3.14 (2026-10-06, screenshots; docs/log/2026-10.md ~18:45 + ~18:50, docs/answered/
ui.md LOCKED 2026-10-06): "map was working, but it broke on the island." (an empty blue disc + the arrow), "player icon is huge!",
LOCKED "it should scale with the amount of blocks shown on the minimap", and the minimap covering the top-right text widgets.
ROOT CAUSE of the blank island (server log 2026-10-06_18-40-21 + engine bytecode + the harness repro; NOT a cross-world cache reuse):
  - the island is a Void world (WorldGen Type Void). The engine's map ImageBuilder.generateImageAsync writes rgba 0,0,0,0 for a column
    with no block and no fluid (bytecode 735-790: outColor r = g = b = a = 0), so every void chunk of the island is ONE fully transparent
    piece. The island's first fill "166 of 169 (2 shrunk, 164 from the cache, 164 already on the client)" = 164 identical transparent
    void pieces (one picture, content-keyed - correct dedup, the same picture whatever world it came from) + the island's own 1-2 real
    pieces. 0.3.14 counted those void pieces as "real" (the fill line) and as "the map stream started" (the attach gate), so it showed
    a see-through disc: the 30 % dark backdrop over the blue sky = "an empty blue disc".
  - the island itself is one 32-block chunk ~ 15 px wide at the default zoom 160, drawn at the centre - exactly under the 24 px arrow
    (48 px at Skyy's 200 % size): the arrow hid the island's own pieces.
  - no other world's tile was drawn: the engine sends ClearWorldMap at every join (World.onFinishPlayerJoining -> WorldMapTracker.clear,
    bytecode), which empties the session's streamed / known sets; the harness proves it. Hardening anyway: the "ready" request ran the
    attach gate BEFORE the queue was drained, so the gate read the previous world's "stream started" flag; now the queue is drained
    first. And the tap marks every world boundary in the player's queue (the PlayerRef's world uuid changes in World.addPlayer, BEFORE
    the join's ClearWorldMap and the new burst - bytecode): the drain forgets the previous world's pieces + markers at the marker, so
    even a world change without a ClearWorldMap can never draw the old world's tiles.
FIX 1 (blank island): a piece whose palette is ALL transparent (alpha < 128 everywhere) is "empty" - never encoded or sent, its slot
  keeps the "not yet" backdrop, counted as "N empty" in the first-fill line. The attach gate waits for the first REAL piece (spec: worlds
  with nothing to draw hide the minimap - research/Minimap-Widget-Spec.md question 2 [hide]); a world whose stream sends only empty pieces
  stays hidden (one log line "only empty (void) map pieces"); 15 s after the attach with no real piece (after a ClearWorldMap) = hidden.
FIX 2 (arrow, LOCKED): the arrow is sized in WORLD BLOCKS: Server Setup -> Minimap "Your arrow's width" (hud.mm.arrowBlocks, int 4-64,
  default 16 blocks, KEEP=10 kit) -> px = blocks x clip / (2 x zoom radius), rounded to an even number, at least 8 px, at most 32 px.
  At 100 % size: zoom 64 = 20 px, 96 = 12, 128 = 10, 160 = 8 (was 24), 224 / 320 = 8 (the minimum). Skyy's 200 % zoom 128 = 20 (was 48).
  A zoom / size change re-attaches already (the arrow size is part of the drawn frame).
FIX 3 (overlap): a player whose layout file has NO Minimap line (never placed it) and no server-default entry for it gets the first free
  spot at 1080p instead of the fixed tr 8,40: candidates on the tr anchor (x 8 or just left of a widget box, y 40 / 8 or just under one),
  the box kept in the right half and on screen, never touching another SHOWN widget's maximum box (+ 4 px), the smallest
  2 x (dx - 8) + (dy - 8) wins (the right edge first, then high up). With the built-in layout nothing moves (tr 8,40 is free); a saved Minimap line is never touched; once the player saves
  their HUD the spot is saved like any other.
FIX ROUND (critics): keys-only bursts carry a "real piece seen" flag (no more realSeen without looking); forget / ClearWorldMap set
  s.more (the slots re-draw at once); "ready" forgets the old world when the new world's marker has not come yet; a 16 x 16 arrow set
  for arrows of 16 px or less; the shared content key = CRC32 + Adler32. Kept: the 8 px minimum (the task's "sane min px").
Harness: python SkyyHud/test_skyyhud_0.3.16.py (bare JVM; two-world repro, arrow sizes, placement maths, saved layouts, class diff).
To regenerate, delete SkyyHud/build_skyyhud_0.3.16.py first (the script refuses to overwrite it).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.15.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.16.py")
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


ARROW_DEF, ARROW_MIN_B, ARROW_MAX_B = 16, 4, 64      # blocks (the Server Setup row)
ARROW_MIN_PX, ARROW_MAX_PX = 8, 32                  # px on screen
PLACE_GAP = 4                                       # px kept free around another widget's box

# ---- header + version
rep('''"""SkyyHud 0.3.15 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.15.py            -> SkyyHud/SkyyHud-0.3.15.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.16 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.16.py            -> SkyyHud/SkyyHud-0.3.16.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.16 (generated by tools/hud_0_3_16_patch.py from 0.3.15): the MINIMAP fix round from Skyy's 0.3.14 test (2026-10-06: "map was
  working, but it broke on the island.", "player icon is huge!", LOCKED "it should scale with the amount of blocks shown on the
  minimap", the minimap over the top-right widgets). Root cause + facts: tools/hud_0_3_16_patch.py's docstring.
  - EMPTY pieces: a map piece whose palette is all transparent (the engine's void columns are rgba 0) is never encoded or sent; its slot
    keeps the backdrop; the first-fill line counts them ("N empty"). The minimap attaches only after the first REAL piece of this world
    (a Void world with nothing built shows nothing; an island shows once its own ground is on the map); only-empty streams log once.
  - World change: the "ready" request drains the player's queue BEFORE the attach gate (the engine's ClearWorldMap at the join is seen
    first); the tap puts a world-boundary marker into the queue when the player's world uuid changes (World.addPlayer, before the
    join's ClearWorldMap) and the drain forgets the old world's pieces + markers there (no other world's tile, even without a clear).
  - ARROW in world blocks: Server Setup -> Minimap "Your arrow's width" (hud.mm.arrowBlocks, %d blocks, %d-%d): px = blocks x clip /
    (2 x radius), even, %d-%d px (100 %%, zoom 160: 8 px - was 24). Part of the drawn frame (zoom / size changes re-attach as before).
  - DEFAULT SPOT: a player with no saved Minimap line (and no server-default entry for it) gets the first free spot at 1080p on the tr
    anchor (Widgets.mmPlace: never touching another shown widget's box + %d px, right half, the right edge first); the built-in layout
    keeps tr 8,40; saved lines are never moved.
  - Fix round (critics): a keys-only burst (past the queue's image bound) counts as "real" only when the tap saw a real piece in it; a
    world boundary / ClearWorldMap re-draws the slots at once; "ready" forgets the old world when no marker of the new one came yet; a
    16 x 16 arrow set (its own 1 px outline) is used at 16 px or smaller; the shared tile key carries an Adler32 next to the CRC32.
''' % (ARROW_DEF, ARROW_MIN_B, ARROW_MAX_B, ARROW_MIN_PX, ARROW_MAX_PX, PLACE_GAP))
rep('VERSION = "0.3.15"', 'VERSION = "0.3.16"')

# ---- MmCfg: the arrow row's field, its file key, the px maths
rep('''           'public static volatile String DISABLED_WORLDS = "";',
''', '''           'public static volatile String DISABLED_WORLDS = "";',
           # 0.3.16 (Skyy LOCKED 2026-10-06): the arrow's width in WORLD blocks (Server Setup -> Minimap, hud.mm.arrowBlocks)
           "public static volatile int ARROW_BLOCKS = %d;",
''' % ARROW_DEF)
rep('''  DISABLED_WORLDS = dw == null ? "" : dw.trim();
}""", mmcfg))
''', '''  DISABLED_WORLDS = dw == null ? "" : dw.trim();
  String ab = p.getProperty("mm.arrowBlocks");
  int abn = ab == null ? %d : num(ab);
  ARROW_BLOCKS = (abn >= %d && abn <= %d) ? abn : %d;
}""", mmcfg))
# 0.3.16 (Skyy LOCKED 2026-10-06 "it should scale with the amount of blocks shown on the minimap"): the arrow picture's size on screen =
# ARROW_BLOCKS world blocks at this frame's scale (clip px C for 2 x radius blocks), an even number of px, %d-%d px
mmcfg.addMethod(CtNewMethod.make("""
public static int arrowPx(int C, int r) {
  int b = ARROW_BLOCKS;
  if (b < %d) b = %d;
  if (b > %d) b = %d;
  int rr = r < 1 ? 160 : r;
  double px = (double) b * (double) C / (2.0 * (double) rr);
  int a = 2 * (int) Math.round(px / 2.0);
  if (a < %d) a = %d;
  if (a > %d) a = %d;
  return a;
}""", mmcfg))
''' % (ARROW_DEF, ARROW_MIN_B, ARROW_MAX_B, ARROW_DEF, ARROW_MIN_PX, ARROW_MAX_PX, ARROW_MIN_B, ARROW_MIN_B, ARROW_MAX_B, ARROW_MAX_B,
       ARROW_MIN_PX, ARROW_MIN_PX, ARROW_MAX_PX, ARROW_MAX_PX))
rep('''    "mm.disabledWorlds=",
    "",
])''', '''    "mm.disabledWorlds=",
    "# mm.arrowBlocks = how many blocks wide your arrow is drawn on the map (%d-%d): it shrinks when zoomed out (%d-%d px on screen).",
    "mm.arrowBlocks=%d",
    "",
])''' % (ARROW_MIN_B, ARROW_MAX_B, ARROW_MIN_PX, ARROW_MAX_PX, ARROW_DEF))
rep('''     "field:MmCfg.DISABLED_WORLDS@config.properties:mm.disabledWorlds;after=Minimap.cfgChanged"),
]''', '''     "field:MmCfg.DISABLED_WORLDS@config.properties:mm.disabledWorlds;after=Minimap.cfgChanged"),
    # 0.3.16 (Skyy LOCKED 2026-10-06): the arrow in world blocks
    ("hud.mm.arrowBlocks", "Your arrow's width", "mm", "int", "%d", "%d", "%d", "", "blocks", "live",
     "Drawn this many blocks wide, so it shrinks when zoomed out (%d-%d px on screen).",
     "field:MmCfg.ARROW_BLOCKS@config.properties:mm.arrowBlocks;after=Minimap.cfgChanged"),
]''' % (ARROW_DEF, ARROW_MIN_B, ARROW_MAX_B, ARROW_MIN_PX, ARROW_MAX_PX))

# ---- FIX 3: the first free spot for a player who never placed the minimap (Widgets, before LayoutStore.get calls it)
rep('''# ================= LayoutStore =================
''', '''# ================= 0.3.16 Widgets.mmPlace: the minimap's first free spot (Skyy 2026-10-06: it covered the top-right widgets) =========
# r = boxes (x, y, w, h at 1080p, 4 ints each); a box hits when it comes closer than the gap
wid.addMethod(CtNewMethod.make(f"""
public static boolean mmHit(int[] r, int n, int x, int y, int w, int h) {{
  for (int i = 0; i < n; i++) {{
    int bx = r[4 * i]; int by = r[4 * i + 1]; int bw = r[4 * i + 2]; int bh = r[4 * i + 3];
    if (x < bx + bw + %d && bx < x + w + %d && y < by + bh + %d && by < y + h + %d) return true;
  }}
  return false;
}}""", wid))
# only the built-in spot of a minimap the player never placed (no line in their file - LayoutStore.get) and the server default does not
# place: tr anchor candidates x 8 / just left of a box, y 40 / 8 / just under a box; right half, on screen, no shown widget's maximum box
# within the gap; the smallest 2 x (dx - 8) + (dy - 8) wins (the right edge first; ties: higher up). true = moved
wid.addMethod(CtNewMethod.make(f"""
public static boolean mmPlace(java.util.Map m) {{
  {{PKG}}.WLayout w = ({{PKG}}.WLayout) m.get("Minimap");
  if (w == null) return false;
  {{PKG}}.WLayout d = def("Minimap");
  if (!d.anchor.equals(w.anchor) || w.dx != d.dx || w.dy != d.dy) return false;
  try {{ java.util.HashMap dm = {{PKG}}.HudCfg.layoutMap(); if (dm != null && dm.get("Minimap") != null) return false; }} catch (Throwable t) {{ }}
  int S = w.bw * w.scale / 100;
  int n = 0;
  int[] r = new int[4 * IDS.length];
  for (int i = 0; i < IDS.length; i++) {{
    if ("Minimap".equals(IDS[i])) continue;
    {{PKG}}.WLayout o = ({{PKG}}.WLayout) m.get(IDS[i]);
    if (o == null || !o.en) continue;
    int ow = o.bw * o.scale / 100;
    int oh = hMax(o);
    int[] p = screenPosWH(o, ow, oh);
    r[4 * n] = p[0]; r[4 * n + 1] = p[1]; r[4 * n + 2] = ow; r[4 * n + 3] = oh;
    n = n + 1;
  }}
  if (!mmHit(r, n, 1920 - S - w.dx, w.dy, S, S)) return false;
  int[] cx = new int[n + 1];
  int[] cy = new int[n + 2];
  cx[0] = 8; cy[0] = d.dy; cy[1] = 8;
  for (int i = 0; i < n; i++) {{ cx[i + 1] = 1920 - r[4 * i] + 6; cy[i + 2] = r[4 * i + 1] + r[4 * i + 3] + 6; }}
  int best = -1; int bdx = 0; int bdy = 0;
  for (int i = 0; i < cx.length; i++) {{
    int dx = cx[i];
    if (dx < 8 || 1920 - S - dx < 960) continue;
    for (int j = 0; j < cy.length; j++) {{
      int dy = cy[j];
      if (dy < 8 || dy + S > 1080 - 8) continue;
      if (mmHit(r, n, 1920 - S - dx, dy, S, S)) continue;
      int sc = 2 * (dx - 8) + (dy - 8);
      if (best < 0 || sc < best || (sc == best && dy < bdy)) {{ best = sc; bdx = dx; bdy = dy; }}
    }}
  }}
  if (best < 0) return false;
  w.dx = bdx;
  w.dy = bdy;
  clampToScreen(w);
  return true;
}}""", wid))

# ================= LayoutStore =================
''' % (PLACE_GAP, PLACE_GAP, PLACE_GAP, PLACE_GAP))
# the f-string above is inside the generated file: {{PKG}} must come out as {PKG} there
rep('''  {{PKG}}.WLayout w = ({{PKG}}.WLayout) m.get("Minimap");''', '''  {PKG}.WLayout w = ({PKG}.WLayout) m.get("Minimap");''')
rep('''  {{PKG}}.WLayout d = def("Minimap");''', '''  {PKG}.WLayout d = def("Minimap");''')
rep('''java.util.HashMap dm = {{PKG}}.HudCfg.layoutMap();''', '''java.util.HashMap dm = {PKG}.HudCfg.layoutMap();''')
rep('''    {{PKG}}.WLayout o = ({{PKG}}.WLayout) m.get(IDS[i]);''', '''    {PKG}.WLayout o = ({PKG}.WLayout) m.get(IDS[i]);''')
rep('''  m = new java.util.concurrent.ConcurrentHashMap();
  String[] ids = {PKG}.Widgets.IDS;
  try {{
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");''', '''  m = new java.util.concurrent.ConcurrentHashMap();
  String[] ids = {PKG}.Widgets.IDS;
  boolean mmf = false;
  try {{
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");''')
rep('''        String v = p.getProperty(ids[i]);
        {PKG}.WLayout d = {PKG}.Widgets.start(ids[i]);
        m.put(ids[i], v == null ? d : {PKG}.WLayout.parse(v, d));''', '''        String v = p.getProperty(ids[i]);
        if (v != null && "Minimap".equals(ids[i])) mmf = true;
        {PKG}.WLayout d = {PKG}.Widgets.start(ids[i]);
        m.put(ids[i], v == null ? d : {PKG}.WLayout.parse(v, d));''')
rep('''    {PKG}.Widgets.clampToScreen(w);
  }}
  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);''', '''    {PKG}.Widgets.clampToScreen(w);
  }}
  // 0.3.16: a minimap the player never placed takes the first free spot (a COPY: Widgets.start may hand out the shared default)
  if (!mmf) {{
    try {{
      {PKG}.WLayout mw = ({PKG}.WLayout) m.get("Minimap");
      if (mw != null) {{
        {PKG}.WLayout cp = {PKG}.WLayout.parse(mw.ser(), mw);
        if (cp != null && cp != mw) {{ m.put("Minimap", cp); if (!{PKG}.Widgets.mmPlace(m)) m.put("Minimap", mw); }}
      }}
    }} catch (Throwable t) {{ }}
  }}
  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);''')

# ---- MmPng.empty: an all-transparent piece (the engine's void columns)
rep('''  return encode(dw, dh, px);
}""")
''', '''  return encode(dw, dh, px);
}""")
# 0.3.16: a piece with NOTHING to draw - every palette colour below the alpha threshold (the engine's map writes rgba 0 for a column with
# no block and no fluid: a Void world's chunks); such a piece is never encoded or sent and does not count as "the map started"
MMM(mmpng, r"""
public static boolean empty(@MIM@ m) {
  if (m == null || m.palette == null || m.palette.length == 0) return false;
  int[] p = m.palette;
  for (int i = 0; i < p.length; i++) if ((p[i] & 255) >= 128) return false;
  return true;
}""")
''')

# ---- MmSess: the new per-world state
rep('''           "public double[] ptWX;", "public double[] ptWZ;", "public boolean[] ptRim;"):
    MMF(mmsess, _f)''', '''           "public double[] ptWX;", "public double[] ptWZ;", "public boolean[] ptRim;",
           # 0.3.16: a REAL (not all-transparent) piece seen in this world's stream since the last ClearWorldMap; empty pieces met;
           # the world uuid the tap last marked (its thread only) / the drain last crossed (minimap thread only)
           "public boolean realSeen;", "public int voids;", "public volatile java.util.UUID tapW;", "public java.util.UUID drainW;"):
    MMF(mmsess, _f)''')

# ---- resolve: an empty piece = the backdrop, remembered as "0" (no encode, no picture)
rep('''    if ("!".equals(o)) return null;
''', '''    if ("!".equals(o)) return null;
    if ("0".equals(o)) return null;
''')
rep('''  @MIM@ m = (@MIM@) o;
  int det = s.det > 0 ? s.det : @PKG@.MmCfg.detail();''', '''  @MIM@ m = (@MIM@) o;
  // 0.3.16: nothing to draw (void) - the slot keeps the backdrop, no encode, no picture
  if (@PKG@.MmPng.empty(m)) { s.known.put(K, "0"); s.voids = s.voids + 1; return null; }
  int det = s.det > 0 ? s.det : @PKG@.MmCfg.detail();''')

# ---- drain: realSeen
# fix round (critic: a keys-only burst set realSeen without looking at a piece - a big Void burst showed the empty disc again): the
# tap's keys-only array ends with ONE flag element (1 = at least one real piece in that packet); only that flag counts
rep('''      s.streamSeen = true;
      s.packets = s.packets + 1L;
      for (int i = 0; i < ks.length; i++) {''', '''      s.streamSeen = true;
      int kn = ks.length - 1;
      if (kn >= 0 && ks[kn] != 0L) s.realSeen = true;
      s.packets = s.packets + 1L;
      for (int i = 0; i < kn; i++) {''')
rep('''          s.streamed.add(k);
          if (k == -1L) { s.originImg = c.image;''', '''          s.streamed.add(k);
          if (!s.realSeen && !@PKG@.MmPng.empty(c.image)) s.realSeen = true;
          if (k == -1L) { s.originImg = c.image;''')
rep('''      s.streamSeen = false;
      s.clears = s.clears + 1L;''', '''      s.streamSeen = false;
      s.realSeen = false;
      s.more = true;
      s.clears = s.clears + 1L;''')

# ---- geometry: the arrow in world blocks
rep('''  s.ap = Math.max(10, s.S * 24 / 160);''', '''  s.ap = @PKG@.MmCfg.arrowPx(s.C, s.r);''')

# ---- attach gate + step: wait for a REAL piece
rep('''  if (!s.streamSeen) {
    if (s.hud != null) detach(s, "no stream yet");''', '''  // 0.3.16: ... and for a REAL piece (a Void world's all-transparent pieces drew an empty disc on Skyy's island)
  if (!s.realSeen) {
    if (s.hud != null) detach(s, "no stream yet");''')
rep('''    if (s.streamSeen) attach(s, now, true);
    else if (!s.pendLogged && now - s.pendingSince > @QSTREAM@L) {
      s.pendLogged = true;
      String k = s.wname == null ? "?" : s.wname;
      if (noStreamLog(k)) info("minimap: no map stream in world '" + k + "' - not shown there (it shows once a map packet comes)");''',
    '''    if (s.realSeen) attach(s, now, true);
    else if (!s.pendLogged && now - s.pendingSince > @QSTREAM@L) {
      s.pendLogged = true;
      String k = s.wname == null ? "?" : s.wname;
      if (s.streamSeen) { if (noStreamLog(k + "|void")) info("minimap: only empty (void) map pieces in world '" + k + "' so far - not shown there (it shows once real ground is on the map)"); }
      else if (noStreamLog(k)) info("minimap: no map stream in world '" + k + "' - not shown there (it shows once a map packet comes)");''')
rep('''  if (!s.streamSeen && now - s.attachAt > @QSTREAM@L) { noStream(s); return; }''',
    '''  if (!s.realSeen && now - s.attachAt > @QSTREAM@L) { noStream(s); return; }''')

# ---- stats + the first-fill line
rep('''  s.encodes = 0; s.hits = 0; s.dedup = 0; s.sweepHit = 0; s.sweepMiss = 0; s.pics = 0; s.sentBytes = 0L;''',
    '''  s.encodes = 0; s.hits = 0; s.dedup = 0; s.sweepHit = 0; s.sweepMiss = 0; s.pics = 0; s.sentBytes = 0L; s.voids = 0;''')
rep('''  for (int i = 0; i < s.slotPath.length; i++) if (s.slotPath[i] != null && !s.slotPath[i].equals(s.dark)) real = real + 1;
''', '''  for (int i = 0; i < s.slotPath.length; i++) if (s.slotPath[i] != null && !s.slotPath[i].equals(s.dark)) real = real + 1;
  int empty = 0;
  for (int i = 0; i < s.slotKey.length; i++) if (s.slotKey[i] != Long.MIN_VALUE && "0".equals(s.known.get(Long.valueOf(s.slotKey[i])))) empty = empty + 1;
''')
rep('''s.sweepMiss + " not in it yet), "''', '''s.sweepMiss + " not in it yet, " + empty + " empty), "''')

# ---- the world boundary: forget (before drain), the drain's marker handling, the tap's marker
rep('''MMM(mmmain, r"""
public static void drain(@PKG@.MmSess s) {
  int n = 0;
  s.provOk = false;
  while (n < 200000) {
    Object o = s.q.poll();
    if (o == null) break;
    s.qn.decrementAndGet();''', '''# 0.3.16: the previous world's pieces / markers forgotten at a world boundary (the tap's marker)
MMM(mmmain, r"""
public static void forget(@PKG@.MmSess s) {
  s.streamed.clear();
  s.known.clear();
  s.originImg = null;
  s.markers.clear();
  s.markersDirty = true;
  s.streamSeen = false;
  s.realSeen = false;
  s.more = true;
}""")
MMM(mmmain, r"""
public static void drain(@PKG@.MmSess s) {
  int n = 0;
  s.provOk = false;
  while (n < 200000) {
    Object o = s.q.poll();
    if (o == null) break;
    // 0.3.16: a world boundary (the tap saw a new world uuid): nothing queued after it belongs to the old world
    if (o instanceof java.util.UUID) {
      if (s.drainW != null && !o.equals(s.drainW)) forget(s);
      s.drainW = (java.util.UUID) o;
      continue;
    }
    s.qn.decrementAndGet();''')
rep('''  @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(pr.getUuid());
  if (s == null || s.pr != pr) return;
  if (s.qn.incrementAndGet() > @QMAX@) {''', '''  @PKG@.MmSess s = (@PKG@.MmSess) SESS.get(pr.getUuid());
  if (s == null || s.pr != pr) return;
  // 0.3.16: the player's world changed (World.addPlayer sets it before the join's ClearWorldMap + burst): one boundary marker first
  java.util.UUID wu = pr.getWorldUuid();
  if (wu != null && !wu.equals(s.tapW)) { s.tapW = wu; s.q.add(wu); }
  if (s.qn.incrementAndGet() > @QMAX@) {''')
# fix round (critic: keys-only bursts): the keys-only array gets one trailing flag element = 1 when at least one piece of the packet is
# REAL (MmPng.empty stops at the first opaque palette colour; checked only until one real piece is found)
rep('''      long[] ks = new long[m];
      int j = 0;
      for (int i = 0; i < n && j < m; i++) if (cs[i] != null && cs[i].image != null) { ks[j] = key(cs[i].chunkX, cs[i].chunkZ); j = j + 1; }
      s.q.add(ks);''', '''      long[] ks = new long[m + 1];
      int j = 0;
      boolean real = false;
      for (int i = 0; i < n && j < m; i++) {
        if (cs[i] != null && cs[i].image != null) {
          ks[j] = key(cs[i].chunkX, cs[i].chunkZ);
          j = j + 1;
          if (!real && !@PKG@.MmPng.empty(cs[i].image)) real = true;
        }
      }
      ks[m] = real ? 1L : 0L;
      s.q.add(ks);''')
# ---- ready: drain first, then the gate
rep('''    s.posKnown = false;
    recountTaps();
    attach(s, now, true);''', '''    s.posKnown = false;
    recountTaps();
    // 0.3.16: the queue first (the world boundary, the engine's ClearWorldMap at the join, this world's first pieces), so the gate
    // below reads THIS world, never the previous world's "stream started"
    drain(s);
    // fix round (review): no packet of the new world queued yet (no boundary marker drained) - forget the old world here too
    if (s.wuuid != null && s.drainW != null && !s.wuuid.equals(s.drainW)) { forget(s); s.drainW = s.wuuid; }
    attach(s, now, true);''')

# ---- fix round (critic: an 8 px arrow from a 32 px picture loses its 1 px outline): a 16 x 16 set with its own 1 px outline, used
# when the arrow is 16 px or smaller (the outline stays half a pixel or more on screen); both sets go in the one statics rebuild
rep('''MMM(mmpng, r"""
public static int[] dot(int col) {''', '''MMM(mmpng, r"""
public static int[] arrowSm(int k) {
  int s = 16;
  double a = Math.toRadians(22.5 * (double) k);
  double ca = Math.cos(a);
  double sa = Math.sin(a);
  double[] vx = new double[] { 0.0, 10.0, 0.0, -10.0 };
  double[] vy = new double[] { -14.0, 13.0, 6.0, 13.0 };
  double[] qx = new double[4];
  double[] qy = new double[4];
  for (int i = 0; i < 4; i++) {
    qx[i] = 16.0 + vx[i] * ca - vy[i] * sa;
    qy[i] = 16.0 + vx[i] * sa + vy[i] * ca;
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
public static int[] dot(int col) {''')
rep('''    else if (p[0].equals("arrow")) a = asset("arrow", @PKG@.MmPng.encode(32, 32, @PKG@.MmPng.arrow(Integer.parseInt(p[1]))));''',
    '''    else if (p[0].equals("arrow")) a = asset("arrow", @PKG@.MmPng.encode(32, 32, @PKG@.MmPng.arrow(Integer.parseInt(p[1]))));
    else if (p[0].equals("arrowS")) a = asset("arrow", @PKG@.MmPng.encode(16, 16, @PKG@.MmPng.arrowSm(Integer.parseInt(p[1]))));''')
rep('''  for (int k = 0; k < 16; k++) send(s, gen("arrow:" + k), false);
  send(s, gen("dark"), false);''', '''  for (int k = 0; k < 16; k++) send(s, gen("arrow:" + k), false);
  for (int k = 0; k < 16; k++) send(s, gen("arrowS:" + k), false);
  send(s, gen("dark"), false);''')
rep('''  for (int k = 0; k < 16; k++) s.arrows[k] = gen("arrow:" + k).getName();''',
    '''  String ak = s.ap <= 16 ? "arrowS:" : "arrow:";
  for (int k = 0; k < 16; k++) s.arrows[k] = gen(ak + k).getName();''')

# ---- fix round (critic: one 32-bit CRC in the shared content key): a second checksum (Adler32 over the same bytes) in the key
rep('''  c.update(pb, 0, pb.length);
  c.update(m.packedIndices, 0, m.packedIndices.length);
  return m.width + "x" + m.height + "b" + (m.bitsPerIndex & 255) + "p" + pal.length + "n" + m.packedIndices.length + "c" + Long.toHexString(c.getValue()) + "/" + det;''',
    '''  c.update(pb, 0, pb.length);
  c.update(m.packedIndices, 0, m.packedIndices.length);
  java.util.zip.Adler32 ad = new java.util.zip.Adler32();
  ad.update(pb, 0, pb.length);
  ad.update(m.packedIndices, 0, m.packedIndices.length);
  return m.width + "x" + m.height + "b" + (m.bitsPerIndex & 255) + "p" + pal.length + "n" + m.packedIndices.length + "c" + Long.toHexString(c.getValue()) + "a" + Long.toHexString(ad.getValue()) + "/" + det;''')

# ---- manifest text
rep('''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 13 widgets (14 with Dynamic Seasons) incl. a round minimap (needs BetterMap; reads the map it streams, shrunk on its own thread),''',
    '''B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 13 widgets (14 with Dynamic Seasons) incl. a round minimap (needs BetterMap; reads the map it streams, shrunk on its own thread; your arrow sized in blocks),''')

out = s.replace(LF, NL)
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(%d lines)" % out.count(LF))
