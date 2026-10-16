"""Derive SkyyFishing/build_skyyfishing_0.1.8.py from the LIVE 0.1.7 (build_skyyfishing_0.1.7.py = the tools/deploy_set.py SET pin, made by
tools/fishing_0_1_7_patch.py). Every anchor is asserted; every change is undone at the end to prove nothing else changed. Edit THIS file,
never the generated script.
Run:  python tools/fishing_0_1_8_patch.py   then   python SkyyFishing/build_skyyfishing_0.1.8.py   (never --deploy)
Test: python SkyyFishing/test_skyyfishing_0.1.8.py [--keep]

0.1.8 (2026-10-16) = THE LINE OVER WATER + REAL TACKLE MODELS + THE FISH BRIDGE FOR THE VOID (round "fish018"; Skyy 2026-10-16,
docs/answered/bags.md + ui.md: "fishing line still buggy/ broken. you can see it over land, but not over water", "broken texture.",
"fish not going in fishing bag."):
 A. LINE OVER WATER. The line is the engine debug line (DisplayDebug Cylinder pieces, 0.1.2). The client draws debug shapes BEFORE its
    see-through water and without writing depth, so wherever water is BEHIND the line (as the viewer looks), the water surface is drawn
    over it - over land the line shows, over a lake it vanishes. That is the client's draw order; no server packet changes it
    (DisplayDebug only has the flags Fade / NoWireframe / NoSolid; Angler's Almanac 1.2.2 still ships its debug-line renderer but no longer
    calls it). FALLBACK: our own tiny particle "beads" along the line (Server/Particles/SkyyFishing/SkyyFishing_Line_Bead: one off-white
    dot per spawn, no movement, alive 0.45 s) - particles are drawn after the water (the vanilla splash shows over water), so the line now
    shows over water as a fine dotted thread on top of the engine line. A bead's size grows with its distance from the caster's rod tip
    (about the same few pixels on screen near and far; never thinner than fish.line.thickness), the gap between beads is fish.line.beadGap
    bead sizes, at most 120 beads per refresh (the gap widens instead of dropping the far end). Sent with the line (FishEngApi.drawLine ->
    lineTo), every fish.line.beadSec seconds per caster, ONE batch of SpawnParticleSystem packets per viewer, only to players within
    FishDefs.VIEW of the line (like the line). Rows: fish.line.beads (on), fish.line.beadSec (0.33 s), fish.line.beadSize (1),
    fish.line.beadGap (3). UNVERIFIED in game: how the client scales a particle system by the packet's scale (the bead size) - the size
    rows are live so it can be tuned in Server Setup without a build.
 B. REAL MODELS FOR THE 23 TACKLE ITEMS (client log: "Missing model for item SkyyFishing_*" -> the purple-black cube): every reel / hook /
    line / sinker item gets the Model + Texture of a vanilla item BY PATH (nothing vanilla is copied or committed; the build asserts both
    files are in Assets.zip): reels = the Gadget Assembly; Barbed hook = the Iron Stud, Lost Property hook = Metal Scraps, Lure = the trap
    bait; Braided line = the Linen bolt, Steady = the Cotton bolt, Twin = the Spider Silk ball, Scholars = the Silk bolt; Weighted sinker =
    an Iron ingot, Clean = a Silver ingot, Deep = a Cobalt ingot. Their icons (the approved concept icons) stay.
 C. THE FISH BRIDGE (SkyySacks 0.8.10 puts whole fish into the Fishing category of the Void and must not lose a fish's weight / length /
    catcher): three plain-type bridge functions (java.lang in / out):
      fishing:fn:fishOf  {String item id, String metadata JSON or null} -> "grams,mm,catcher" for one of OUR whole fish whose metadata is
                         exactly ours (the SkyyFishing document v/g/mm/by + the tooltip), "" for a fish with no metadata, null = not a fish
                         or other metadata on it (the Void then leaves that stack alone)
      fishing:fn:fishDoc {String item id, String "grams,mm,catcher"} -> the metadata JSON of that fish (FishRig.makeFish - the same
                         weight, length, catcher and tooltip as when it was caught), null = not a fish / a broken entry
      fishing:fn:pond    UUID -> Long = fish landed by fishing on the player's ACTIVE profile (the Pond Fish count; SkyySacks 0.8.10 adds it
                         to the Fishing category's collected total, so landing fish levels the Fishing bag)
REVIEW FIXES (round fish018fix): (1) the bead refresh follows the line refresh: a batch is re-sent early enough that the NEXT line redraw
still falls inside the beads' 0.45 s life (fish.line.everyTicks 7-13 used to leave the line dark ~17-150 ms each cycle); above 13 ticks
(0.43 s) a gap is unavoidable (the row says so). (2) fishing:fn:fishOf answers null (the fish stays in the inventory) when the catcher's
name holds , ; | = a line break or edge spaces - so a fish out of the Void always has the SAME "Caught by" as when it went in.
SAVED DATA: none (four new Server Setup rows; absent = the defaults). ROLLBACK 0.1.8 -> 0.1.7: the beads and the tackle models go, the line
hides over water again; SkyySacks 0.8.10 without these bridge keys leaves fish with metadata in the inventory (no loss) and takes fish
back out of the Void only as plain fish ... so roll SkyySacks back first or together (deploy_set.py check).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "SkyyFishing")
CR, LF = chr(13), chr(10)
raw = open(os.path.join(D, "build_skyyfishing_0.1.7.py"), encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.7"\n' in s and "gear:fn:poleRule" in s and "fishing:fn:fishOf" not in s, "the source must be the generated 0.1.7 script"
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:200])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.8 (2026-10-16)"):].rstrip() + "\n"

rep('"""SkyyFishing 0.1.7 - build script (javassist via jpype). GENERATED by tools/fishing_0_1_7_patch.py from build_skyyfishing_0.1.6.py\n'
    '(itself generated by tools/fishing_0_1_6_patch.py from 0.1.5) - edit the patch, never this file.\n',
    '"""SkyyFishing 0.1.8 - build script (javassist via jpype). GENERATED by tools/fishing_0_1_8_patch.py from build_skyyfishing_0.1.7.py\n'
    '(itself generated by tools/fishing_0_1_7_patch.py from 0.1.6) - edit the patch, never this file.\n' + NOTE + '\n0.1.7 notes:\n')
rep('VERSION = "0.1.7"\n', 'VERSION = "0.1.8"\n')

# ---------------------------------------------------------------- B: real models for the tackle items (vanilla looks by path)
rep('''# ---- reels + parts: the approved concept icons with the vanilla metal gradients (make_fishing helpers, build time)
CMAP = MF.colour_map(P_ART)
ICON_DIR = MF.ICON_DIR


def part_item(iid, icon_file, name, desc, quality):
    ip = "%s/%s.png" % (ICON_DIR, iid)
    put(ip, SA.png_encode(MF.concept_icon(CMAP, icon_file)))
    d = {"TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
         "Icon": rel(ip), "Quality": quality, "MaxStack": 16, "Categories": ["Items.Tools"], "PlayerAnimationsId": "Item",
         "ItemSoundSetId": "ISS_Items_Metal"}''', '''# ---- reels + parts: the approved concept icons with the vanilla metal gradients (make_fishing helpers, build time)
CMAP = MF.colour_map(P_ART)
ICON_DIR = MF.ICON_DIR
# 0.1.8 (Skyy 2026-10-16 "broken texture."): the in-world / in-hand look of every reel and part = a vanilla item's Model + Texture BY PATH
# (nothing copied; both files asserted in Assets.zip) - the client logged "Missing model for item" for all 23 (the purple-black cube)
TACKLE_LOOK = {"Reel": "Ingredient_Gadget_Assembly",
               "Barbed": "Ingredient_Stud_Iron", "LostProperty": "Ingredient_Scraps", "Lure": "Tool_Trap_Bait",
               "Braided": "Ingredient_Bolt_Linen", "Steady": "Ingredient_Bolt_Cotton", "Twin": "Ingredient_Spider_Silk",
               "Scholars": "Ingredient_Bolt_Silk",
               "Weighted": "Ingredient_Bar_Iron", "Clean": "Ingredient_Bar_Silver", "Deep": "Ingredient_Bar_Cobalt"}


def tackle_look(kind):
    v = vjson(ITEM_PATH[TACKLE_LOOK[kind]])
    vp = vjson(ITEM_PATH[v["Parent"]]) if "Parent" in v else {}
    model, tex = v.get("Model") or vp.get("Model"), v.get("Texture") or vp.get("Texture")
    assert model and tex and ("Common/" + model) in AZ_NAMES and ("Common/" + tex) in AZ_NAMES, (kind, model, tex)
    return model, tex


TACKLE_MODELS = {}


def part_item(iid, icon_file, name, desc, quality, kind=None):
    ip = "%s/%s.png" % (ICON_DIR, iid)
    put(ip, SA.png_encode(MF.concept_icon(CMAP, icon_file)))
    d = {"TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
         "Icon": rel(ip), "Quality": quality, "MaxStack": 16, "Categories": ["Items.Tools"], "PlayerAnimationsId": "Item",
         "ItemSoundSetId": "ISS_Items_Metal"}
    if kind is not None:          # 0.1.8: a real model (was none = "Missing model for item")
        d["Model"], d["Texture"] = tackle_look(kind)
        TACKLE_MODELS[iid] = (d["Model"], d["Texture"])''')
rep('''               "Reel Power %s per click. Fit it on a rod at a Fishing Bench.") % (("%.1f" % REEL_POWER[ri])), ["Common", "Uncommon", "Uncommon"][ri])          # 0.1.7''',
    '''               "Reel Power %s per click. Fit it on a rod at a Fishing Bench.") % (("%.1f" % REEL_POWER[ri])), ["Common", "Uncommon", "Uncommon"][ri],
              kind="Reel")          # 0.1.7; 0.1.8: + the model''')
rep('''              "%s: %s. One %s per rod, fitted at a Fishing Bench." % (p[1].capitalize(), p[7] % vt, p[1]), ["Common", "Uncommon"][ti])''',
    '''              "%s: %s. One %s per rod, fitted at a Fishing Bench." % (p[1].capitalize(), p[7] % vt, p[1]), ["Common", "Uncommon"][ti],
              kind=p[2])          # 0.1.8: + the model
assert sorted(TACKLE_MODELS) == sorted(REEL_IDS + [p_[0] for p_ in PART_IDS]) and len(TACKLE_MODELS) == 23, "0.1.8: every reel / part has a model"''')

# ---------------------------------------------------------------- A: the bead particle system (our own JSON; a vanilla texture by path)
rep('''# ---- 0.1.2: no line particles (SkyyFishing_Line_Dot = the white cloud) - the line is the engine debug line (FishEngApi.sendLine)
''', '''# ---- 0.1.2: no line particles (SkyyFishing_Line_Dot = the white cloud) - the line is the engine debug line (FishEngApi.sendLine)
# ---- 0.1.8 THE LINE OVER WATER: the client draws debug shapes before its see-through water, so water behind the line hides it. Beads =
# ONE small off-white dot per spawn (no velocity, no spread, alive BEAD_LIFE s), drawn with the particles (after the water). Our own files;
# the texture is the vanilla round particle by path. The packet's scale sizes each bead (FishEngApi.beadPackets).
assert ("Common/" + BEAD_TEX) in AZ_NAMES, BEAD_TEX
assert BEAD not in PSYS and BEAD not in PSPAWN, "0.1.8: the bead id must be new"
_bead_frame = {"Scale": {"X": {"Min": BEAD_BASE, "Max": BEAD_BASE}, "Y": {"Min": BEAD_BASE, "Max": BEAD_BASE}},
               "Rotation": {"X": {"Min": 0, "Max": 0}, "Y": {"Min": 0, "Max": 0}, "Z": {"Min": 0, "Max": 0}}, "Opacity": 1, "Color": LINE_COLOR}
put("Server/Particles/SkyyFishing/Spawners/%s.particlespawner" % BEAD, {
    "RenderMode": "BlendLinear", "ParticleRotationInfluence": "Billboard", "LinearFiltering": True, "LightInfluence": 0.6,
    "ParticleRotateWithSpawner": False, "TrailSpawnerPositionMultiplier": 1, "TrailSpawnerRotationMultiplier": 1,
    "MaxConcurrentParticles": 1, "ParticleLifeSpan": {"Min": BEAD_LIFE, "Max": BEAD_LIFE}, "SpawnRate": {"Min": 120, "Max": 120},
    "TotalParticles": {"Min": 1, "Max": 1},
    "EmitOffset": {"X": {"Min": 0, "Max": 0}, "Y": {"Min": 0, "Max": 0}, "Z": {"Min": 0, "Max": 0}},
    "Particle": {"Texture": BEAD_TEX, "ScaleRatioConstraint": "OneToOne", "UVOption": "None", "InitialAnimationFrame": _bead_frame,
                 "Animation": {"0": {"Opacity": 1, "Scale": {"X": {"Min": 1, "Max": 1}, "Y": {"Min": 1, "Max": 1}}},
                               "85": {"Opacity": 1}, "100": {"Opacity": 0}}}})
put("Server/Particles/SkyyFishing/%s.particlesystem" % BEAD, {"Spawners": [{"SpawnerId": BEAD}], "LifeSpan": BEAD_LIFE + 0.05,
                                                              "CullDistance": 72, "IsImportant": False})
''')
rep('''PS_SPLASH = "Water_Can_Splash"
''', '''PS_SPLASH = "Water_Can_Splash"
BEAD = "SkyyFishing_Line_Bead"               # 0.1.8: the line beads (shows the line over water)
BEAD_TEX = "Particles/Textures/Basic/Ball.png"
BEAD_BASE = 0.1                              # the asset's bead size (blocks); the packet's scale = wanted size / BEAD_BASE
BEAD_LIFE = 0.45                             # seconds a bead lives (> the longest fish.line.beadSec 0.4)
''')
rep('''        "public static final String SPLASH = %s;" % jstr(PS_SPLASH),''',
    '''        "public static final String SPLASH = %s;" % jstr(PS_SPLASH),
        "public static final String BEAD = %s;" % jstr(BEAD),          # 0.1.8
        "public static final double BEAD_BASE = %r;" % BEAD_BASE,
        "public static final float BEAD_LIFE = %rf;" % BEAD_LIFE,
        "public static final int BEAD_MAX = 120;",
        "public static final double BEAD_ANG = 0.005;",          # bead size per block of distance (~4-5 px at 1080p)
        "public static final double BEAD_START = 0.25;",          # the first bead this far down the line from the rod tip
        "public static final double BEAD_MINSTEP = 0.06;",''')
rep('''    ("fish.line.thickness", "Line thickness", "cast", "dec", "0.03", "0.01", "0.2", "", "blocks", "live,adv",
     "How thick the fishing line is drawn.", "LINE_THICK", "double"),''', '''    ("fish.line.thickness", "Line thickness", "cast", "dec", "0.03", "0.01", "0.2", "", "blocks", "live,adv",
     "How thick the fishing line is drawn.", "LINE_THICK", "double"),
    ("fish.line.beads", "Line beads (shows over water)", "cast", "bool", "true", "", "", "", "", "live",
     "On = small beads along the line, so it shows over water too (the plain line hides behind water).", "BEADS", "boolean"),          # 0.1.8
    ("fish.line.beadSec", "Bead refresh", "cast", "dec", "0.33", "0.1", "0.4", "", "s", "live,adv",
     "The beads are sent again this often while a line is out (each lives 0.45 s).", "BEAD_SEC", "double"),
    ("fish.line.beadSize", "Bead size", "cast", "dec", "1", "0.3", "4", "", "x", "live,adv",
     "Bead size x this (1 = about as thick as the line looks).", "BEAD_SIZE", "double"),
    ("fish.line.beadGap", "Bead spacing", "cast", "dec", "3", "1.2", "12", "", "x", "live,adv",
     "Space between beads in bead sizes (smaller = a more solid line, more packets; max 120 beads).", "BEAD_GAP", "double"),''')

rep('''     "The line is redrawn every this many server ticks (30 ticks = 1 s).", "LINE_EVERY", "int"),''',
    '''     "Line redraw interval in server ticks (30 ticks = 1 s). Above 13 the line beads blink.", "LINE_EVERY", "int"),''')

# ---------------------------------------------------------------- A: the engine side (FishEngApi): bead points, packets, the send + drawLine
rep('''    "TRF": "com.hypixel.hytale.math.vector.Transform",''', '''    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "SPS": "com.hypixel.hytale.protocol.packets.world.SpawnParticleSystem",          # 0.1.8: the line beads
    "POS": "com.hypixel.hytale.protocol.Position",
    "PDIR": "com.hypixel.hytale.protocol.Direction",
    "PCOL": "com.hypixel.hytale.protocol.Color",''')
rep('''    (T["PH"], "write", "void", [T["TCP"] + "[]"]),''', '''    (T["PH"], "write", "void", [T["TCP"] + "[]"]),
    # 0.1.8 the line beads (the packet ParticleUtil.spawnParticleEffect builds) + the fish bridge (metadata JSON round trip)
    (T["SPS"], "<init>", "void", [S_, T["POS"], T["PDIR"], "float", T["PCOL"], "float"]), (T["POS"], "<init>", "void", ["double", "double", "double"]),
    ("com.hypixel.hytale.codec.KeyedCodec", "getKey", S_, []), (T["BD"], "parse", T["BD"], [S_]), (T["BD"], "toJson", S_, []),''')
rep('''for _f in ("public static volatile int CLICK_I = -1;", "public static volatile int STAT_I = -2;", "public static volatile long CLICKS = 0L;",
           "public static volatile long LINE_PKTS = 0L;",''', '''for _f in ("public static volatile int CLICK_I = -1;", "public static volatile int STAT_I = -2;", "public static volatile long CLICKS = 0L;",
           "public static volatile long LINE_PKTS = 0L;",
           "public static volatile long BEAD_PKTS = 0L;",          # 0.1.8
           "public static final java.util.concurrent.ConcurrentHashMap BEADAT = new java.util.concurrent.ConcurrentHashMap();",''')
rep('''M(EAPI, r"""
public void drawLine(@PKG@.FishCtx c, double[] pts, int n, float secs) {
  try {
    if (c == null || c.world == null) return;
    sendLine(c.world.getPlayerRefs(), pts, n, secs, @PKG@.FishCfg.LINE_THICK);
  } catch (Throwable t) { @PKG@.FishLog.warnOnce("drawline", "the fishing line could not be drawn: " + t); }
}""")''', '''# 0.1.8 THE BEADS (the line over water): walk the line's pieces from the rod tip; a bead every max(BEAD_MINSTEP, size x gap) blocks; the
# size = max(line thickness, BEAD_ANG x distance from the caster's eye) x fish.line.beadSize. out[4k..4k+3] = x, y, z, size. Counts only
# when out == null.
M(EAPI, r"""
public static double beadSize(double d, double mul) {
  double w = Math.max(@PKG@.FishCfg.LINE_THICK, @PKG@.FishDefs.BEAD_ANG * d) * mul;
  if (w < 0.005) w = 0.005;
  if (w > 0.5) w = 0.5;
  return w;
}""")
M(EAPI, r"""
public static int beadWalk(double[] p, int n, double near, double mul, double gap, double[] out, int max) {
  double x0 = p[0];
  double y0 = p[1];
  double z0 = p[2];
  double next = @PKG@.FishDefs.BEAD_START;
  double run = 0.0;
  int k = 0;
  for (int i = 0; i + 1 < n && k < max; i++) {
    double ax = p[3 * i];
    double ay = p[3 * i + 1];
    double az = p[3 * i + 2];
    double dx = p[3 * i + 3] - ax;
    double dy = p[3 * i + 4] - ay;
    double dz = p[3 * i + 5] - az;
    double len = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (len < 1.0E-6) continue;
    while (next <= run + len && k < max) {
      double u = (next - run) / len;
      double x = ax + dx * u;
      double y = ay + dy * u;
      double z = az + dz * u;
      double ex = x - x0;
      double ey = y - y0;
      double ez = z - z0;
      double w = beadSize(Math.sqrt(ex * ex + ey * ey + ez * ez) + near, mul);
      if (out != null) { out[4 * k] = x; out[4 * k + 1] = y; out[4 * k + 2] = z; out[4 * k + 3] = w; }
      k = k + 1;
      next = next + Math.max(@PKG@.FishDefs.BEAD_MINSTEP, w * gap);
    }
    run = run + len;
  }
  return k;
}""")
# more than `max` beads: the gap widens (the far end - over the water - is never dropped)
M(EAPI, r"""
public static double[] beadPts(double[] p, int n, double near, double mul, double gap, int max) {
  if (p == null || n < 2 || p.length < 3 * n || max <= 0) return new double[0];
  double g = gap < 1.0 ? 1.0 : gap;
  for (int pass = 0; pass < 6; pass++) {
    int cnt = beadWalk(p, n, near, mul, g, (double[]) null, max * 8);
    if (cnt <= max) break;
    g = g * ((double) cnt / (double) max) * 1.05;
  }
  double[] out = new double[4 * max];
  int k = beadWalk(p, n, near, mul, g, out, max);
  double[] r = new double[4 * k];
  System.arraycopy(out, 0, r, 0, 4 * k);
  return r;
}""")
M(EAPI, r"""
public static @TCP@[] beadPackets(double[] b, float secs) {
  int k = b == null ? 0 : b.length / 4;
  @TCP@[] pk = new @TCP@[k];
  for (int i = 0; i < k; i++) {
    float sc = (float) (b[4 * i + 3] / @PKG@.FishDefs.BEAD_BASE);
    pk[i] = new @SPS@(@PKG@.FishDefs.BEAD, new @POS@(b[4 * i], b[4 * i + 1], b[4 * i + 2]), (@PDIR@) null, sc, (@PCOL@) null, secs);
  }
  return pk;
}""")
# the players near the beads (the line's own rule: FishDefs.VIEW + half the span from the middle) get ONE batch each
M(EAPI, r"""
public static int sendBeads(java.util.Collection prs, double[] b) {
  if (prs == null || b == null || b.length < 4) return 0;
  @TCP@[] pk = beadPackets(b, @PKG@.FishDefs.BEAD_LIFE);
  int e = b.length - 4;
  double mx = (b[0] + b[e]) / 2.0;
  double my = (b[1] + b[e + 1]) / 2.0;
  double mz = (b[2] + b[e + 2]) / 2.0;
  double hx = (b[e] - b[0]) / 2.0;
  double hy = (b[e + 1] - b[1]) / 2.0;
  double hz = (b[e + 2] - b[2]) / 2.0;
  double lim = @PKG@.FishDefs.VIEW + Math.sqrt(hx * hx + hy * hy + hz * hz);
  int sent = 0;
  java.util.Iterator it = prs.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @PR@)) continue;
    try {
      @PR@ pr = (@PR@) o;
      @TRF@ t = pr.getTransform();
      if (t == null) continue;
      @V3D@ q = t.getPosition();
      if (q == null) continue;
      double dx = q.x - mx;
      double dy = q.y - my;
      double dz = q.z - mz;
      if (dx * dx + dy * dy + dz * dz > lim * lim) continue;
      @PH@ h = pr.getPacketHandler();
      if (h == null) continue;
      h.write(pk);
      sent = sent + 1;
    } catch (Throwable t2) { @PKG@.FishLog.warnOnce("bead:" + t2.getClass().getName(), "fishing line beads could not be sent: " + t2); }
  }
  BEAD_PKTS = BEAD_PKTS + (long) pk.length * (long) sent;
  return sent;
}""")
# beads are due for this caster (fish.line.beadSec since the last batch, sooner when the line refresh is slow); never more often than the line
M(EAPI, r"""
public static boolean beadDue(java.util.UUID u, long now) {
  if (u == null) return false;
  Long last = (Long) BEADAT.get(u);
  long every = Math.round(@PKG@.FishCfg.BEAD_SEC * 1000.0) - 20L;
  // review fix: re-send early enough that the NEXT line redraw (fish.line.everyTicks) still falls inside the beads' life - no dark gap
  long lineMs = Math.round((double) Math.max(1, @PKG@.FishCfg.LINE_EVERY) * 1000.0 / 30.0);
  long room = Math.round((double) @PKG@.FishDefs.BEAD_LIFE * 1000.0) - lineMs - 30L;
  if (room < every) every = room;
  if (last != null && now - last.longValue() < every && now >= last.longValue()) return false;
  if (BEADAT.size() > 4096) BEADAT.clear();
  BEADAT.put(u, Long.valueOf(now));
  return true;
}""")
# the line (0.1.2) + 0.1.8 the beads along it (same points: the first one = the rod tip, TIP_F ahead of the eyes)
M(EAPI, r"""
public static int lineTo(java.util.Collection prs, java.util.UUID u, double[] pts, int n, float secs, long now) {
  int sent = sendLine(prs, pts, n, secs, @PKG@.FishCfg.LINE_THICK);
  if (!@PKG@.FishCfg.BEADS || pts == null || n < 2 || !beadDue(u, now)) return sent;
  double[] b = beadPts(pts, n, Math.max(0.0, @PKG@.FishCfg.TIP_F), @PKG@.FishCfg.BEAD_SIZE, @PKG@.FishCfg.BEAD_GAP, @PKG@.FishDefs.BEAD_MAX);
  sendBeads(prs, b);
  return sent;
}""")
M(EAPI, r"""
public void drawLine(@PKG@.FishCtx c, double[] pts, int n, float secs) {
  try {
    if (c == null || c.world == null) return;
    lineTo(c.world.getPlayerRefs(), c.uuid, pts, n, secs, System.currentTimeMillis());          // 0.1.8: + the beads
  } catch (Throwable t) { @PKG@.FishLog.warnOnce("drawline", "the fishing line could not be drawn: " + t); }
}""")''')

# ---------------------------------------------------------------- C: the fish bridge (SkyySacks 0.8.10's Fishing category)
rep('''M(RIG, "public static int mm(@IS@ s) { return num(doc(s), \\"mm\\"); }")''', '''M(RIG, "public static int mm(@IS@ s) { return num(doc(s), \\"mm\\"); }")
# 0.1.8 fishing:fn:fishOf: "grams,mm,catcher" of OUR whole fish whose metadata is exactly ours (our document with only v / g / mm / by +
# the tooltip), "" = a fish with no metadata, null = not our fish / anything else in its metadata (the Void leaves such a stack alone)
M(RIG, r"""
public static String fishOf(String id, String json) {
  if (@PKG@.FishDefs.fishIndex(id) < 0) return null;
  if (json == null || json.length() == 0) return "";
  try {
    @BD@ m = @BD@.parse(json);
    if (m.isEmpty()) return "";
    String dk = @IDM@.KEYED_CODEC.getKey();
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!@PKG@.FishDefs.META.equals(k) && !k.equals(dk)) return null;
    }
    @BV@ v = m.get(@PKG@.FishDefs.META);
    if (v == null || !v.isDocument()) return null;
    @BD@ d = v.asDocument();
    java.util.Iterator di = d.keySet().iterator();
    while (di.hasNext()) {
      String k2 = (String) di.next();
      if (!"v".equals(k2) && !"g".equals(k2) && !"mm".equals(k2) && !"by".equals(k2)) return null;
    }
    int g = num(d, "g");
    int mm = num(d, "mm");
    if (g <= 0 || mm < 0) return null;
    String by = str(d, "by");
    // review fix: a name the entry cannot carry unchanged (separators, a line break, edge spaces) = leave the fish alone (same "Caught by" always)
    if (by.indexOf(',') >= 0 || by.indexOf(';') >= 0 || by.indexOf('|') >= 0 || by.indexOf('=') >= 0 || by.indexOf(10) >= 0
        || by.indexOf(13) >= 0 || !by.equals(by.trim())) return null;
    return g + "," + mm + "," + by;
  } catch (Throwable t) { return null; }
}""")
# 0.1.8 fishing:fn:fishDoc: the metadata JSON of the fish "grams,mm,catcher" (makeFish - the caught fish's document + tooltip again)
M(RIG, r"""
public static String fishDoc(String id, String e) {
  int sp = @PKG@.FishDefs.fishIndex(id);
  if (sp < 0 || e == null) return null;
  try {
    String[] a = e.split(",", -1);
    if (a.length != 3) return null;
    int g = Integer.parseInt(a[0].trim());
    int mm = Integer.parseInt(a[1].trim());
    if (g <= 0 || mm < 0) return null;
    @BD@ m = makeFish(sp, g, mm, a[2].trim()).getMetadata();
    return m == null ? null : m.toJson();
  } catch (Throwable t) { return null; }
}""")''')
rep('''public Object apply(Object o) {
  try {
    if ("grantOf".equals(this.mode)) return o instanceof @IS@ ? @PKG@.FishRig.grantOf((@IS@) o) : null;''', '''public Object apply(Object o) {
  try {
    // 0.1.8 the fish bridge for SkyySacks 0.8.10 (plain types in / out)
    if ("pond".equals(this.mode)) return o instanceof java.util.UUID ? Long.valueOf((long) @PKG@.FishStore.pond(@PKG@.FishBridge.pkey((java.util.UUID) o))) : null;
    if ("fishOf".equals(this.mode) || "fishDoc".equals(this.mode)) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2 || !(((Object[]) o)[0] instanceof String)) return null;
      Object[] f = (Object[]) o;
      String b = f[1] instanceof String ? (String) f[1] : null;
      return "fishOf".equals(this.mode) ? @PKG@.FishRig.fishOf((String) f[0], b) : @PKG@.FishRig.fishDoc((String) f[0], b);
    }
    if ("grantOf".equals(this.mode)) return o instanceof @IS@ ? @PKG@.FishRig.grantOf((@IS@) o) : null;''')
rep('''  b.put("quest:caller:fishingrig", Boolean.TRUE);          // 0.1.7: the Rig tab sends fishing:rig (SkyyQuests 0.3.4 "Fit tackle on your pole")
}""")''', '''  b.put("quest:caller:fishingrig", Boolean.TRUE);          // 0.1.7: the Rig tab sends fishing:rig (SkyyQuests 0.3.4 "Fit tackle on your pole")
  b.put("fishing:fn:fishOf", new @PKG@.FishQuestFn("fishOf"));          // 0.1.8: SkyySacks 0.8.10 keeps a fish's weight in the Void
  b.put("fishing:fn:fishDoc", new @PKG@.FishQuestFn("fishDoc"));
  b.put("fishing:fn:pond", new @PKG@.FishQuestFn("pond"));          // 0.1.8: fish landed (the Fishing category's level)
}""")''')

# ---------------------------------------------------------------- the manifest
rep('''"tackle); one lifelong pole per profile with SkyyGear 0.3.11 (the bench's Wooden rod is locked, Copper / Iron rods are its tier-ups)."''',
    '''"tackle); one lifelong pole per profile with SkyyGear 0.3.11 (the bench's Wooden rod is locked, Copper / Iron rods are its tier-ups); "
                 "the line shows over water (beads); whole fish keep their weight in the SkyyVoid Fishing category (SkyySacks 0.8.10)."''')

# ---------------------------------------------------------------- checks
assert s.count("lineTo(") == 2 and s.count('b.put("fishing:fn:fishOf"') == 1 and s.count("kind=") == 3
assert s.index("public static String fishDoc(") > s.index("public static @IS@ makeFish(")
assert s.index("BEAD = \"SkyyFishing_Line_Bead\"") < s.index("assert (\"Common/\" + BEAD_TEX) in AZ_NAMES")
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.1.7 outside the recorded changes"
dst = os.path.join(D, "build_skyyfishing_0.1.8.py")
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
