"""Derive SkyyFishing/build_skyyfishing_0.1.2.py + SkyyFishing/test_skyyfishing_0.1.2.py from the 0.1.1 GENERATED scripts (the
tools/deploy_set.py SET pin; chain: tools/fishing_0_1_1_patch.py -> this file. AGENT-BRIEF patch rule: edit THIS file, never the generated ones).
Run:  python tools/fishing_0_1_2_patch.py   then   python SkyyFishing/build_skyyfishing_0.1.2.py   (never --deploy: coordinated deploy)
      then python SkyyFishing/test_skyyfishing_0.1.2.py   (needs SkyyFishing-0.1.1.jar, the SET pin, next to it for the class compare)

SKYY'S WORDS (2026-10-09 night, two first-person screenshots at a Zone 1 river; docs/answered/skills.md LOCKED 2026-10-09):
  "dont show the line on the rod, just have the bobber slightly below the tip of the rod."   "fishing is buggy"
  "the widgets all seem to work though"   "but the fishing string is broken. one of the mods had a working fishing string, check that."

WHAT THE OTHER MODS USE (read-only study of the installed jars - no code or asset copied; neither jar carries a licence file):
  * Angler's Almanac 1.2.1 (the mod Skyy praised 2026-10-06: "nice working rods, that show the string to the bobber"): its only line
    renderer, Utils/LineRender/FishingLineRender.drawFishingLine, draws the string with the ENGINE's debug-shape line,
    com.hypixel.hytale.server.core.modules.debug.DebugUtils.addLine (a thin Cylinder DebugShape sent as a DisplayDebug packet that
    lives `time` seconds), split into a few pieces along a sagging curve. (In 1.2.1 nothing calls it any more - its bobber is a plain
    prop entity with no line component.) Vanilla Hytale has no fishing rod item, no rope / tether / leash component and no line
    renderer - only the FishingRod MODEL (with a posed, static Line1-4 + Bait + Hook chain: the "line into the air" of screenshot A).
  * HyFishing 0.6.8: no rod-to-bobber line at all - a static "Line" quad painted along its rod model; the bobber is an NPC.
  So the working "string" = the engine's DisplayDebug line. OUR line now uses that same engine mechanism, written in our own code:
  FishEngApi.segMatrix (the Cylinder transform: translate to the start, yaw / pitch onto the piece, scale thickness x length x
  thickness) + FishEngApi.sendLine builds one DisplayDebug(Cylinder, matrix, colour, time, FLAG_NO_WIREFRAME, opacity 1) per piece and
  writes them in ONE batch to the players near the line only (DebugUtils.add would send every piece to the whole world).

0.1.2 =
  (1) IDLE LOOK (rod in hand, line not out = reel looks 0..8 + the item's base Model): the rod model WITHOUT the posed Line1-4 chain; the
      vanilla red / white Bait (+ its Hook) re-hung IDLE_DROP model units (~0.38 block; 64 units = 1 block) below the rod's line eye
      (the start of the vanilla Line1 = the rod tip), pointing down in the held (Wand) pose. Two models per tier
      (SkyyFishing_Rod_<Tier>_Idle / _NoReel_Idle, built at run time from the make_fishing models - vanilla-derived art only in the jar).
      Line out (10..18) keeps the NoLine looks (no bobber on the rod - the real bobber floats). First AND third person use the same
      model (an item model is one model; the offset direction is a guess for the hold pose - UNVERIFIED, knobs IDLE_DROP / IDLE_DOWN).
  (2) THE LINE: engine debug-line pieces (above) from the rod tip (eye + fish.line.tipAhead along the look + tipRight sideways +
      tipUp) to the top of the bobber, with the old sag (tight while fighting). Redrawn every fish.line.everyTicks; each piece lives
      everyTicks / 30 s + 0.04 s (just over one tick: no flicker gap, and the old copy is gone 40 ms after the new one - 0.12 s left
      a visible ghost string trailing the camera when you turn). Sent to players within FishDefs.VIEW (64)
      blocks + half the line of its middle. Settings: fish.line.show, fish.line.spacing (now the piece length), fish.line.everyTicks,
      NEW fish.line.thickness, fish.line.tipAhead / tipRight / tipUp (live tuning of where the line starts - UNVERIFIED look).
  (3) THE WHITE CLOUD: it WAS the old line - SkyyFishing_Line_Dot was the vanilla GreenOrbTrail (a glowing blink-trail light system,
      several spawners, big soft glows) recoloured off-white, spawned up to 20 times per player every 5 ticks between you and the
      bobber -> a cloud of white glows. Dropped: no line particles at all, the Line_Dot particle system + its spawners are gone from the
      jar. The only particle left is the vanilla Water_Can_Splash at the bite, AT the bobber (on the water).
  (4) WATER CHECKS (what was wrong):
      "Something is in the way" at open water: FishEngApi.block called any block whose material is Solid a wall - but water flowers
      (lily pads, Plant_Flower_Water_*), tall flowers, giant ferns, branches, fences, half blocks, stairs ... are Solid MODEL blocks; and
      a block section without block data (or an unloaded spot, -1) also counted as "in the way". NOW a wall = Solid AND a full cube
      draw type (Cube / CubeWithModel); every Model block (plants, leaves, lily pads, reeds, fences, slabs) lets the line through;
      -1 just ends the ray (-> the look-down / "No water in reach" path), a section without block data = open. The ray still skips
      the first block (starts 1 block out).
      "too shallow" right after a catch: the fight is won by clicking fast, and the click that came right after the landing cast the
      rod AGAIN at wherever you were looking (the bank) -> "too shallow". NOW clicks within fish.recastDelay (1 s) after a catch, a
      lost fish or reeling in never cast. The depth itself is (and was) measured in the landing column: the first water block the aim
      hits, up to its surface, then fish.minDepth (2) blocks down - kept.
  CRITIC FIXES (same 0.1.2 round): the re-cast wait is set only after a catch, a lost fish or the player's own reel-in click (FishCore.hush)
      - a rod swap / walking away / nothing biting / profile or world switch casts again at once; drop() clears the wait on every path;
      MAX_SEG 16 -> 8 pieces per line (half the DisplayDebug packets per fisher per redraw; a 0.03 string needs no more).
  CRITIC FIXES 2: the re-cast wait is a DEBOUNCE (FishCore.quiet re-arms it on every swallowed click - a click burst longer than
      recastDelay after a catch no longer casts at the bank); line pieces live everyTicks/30 + 0.04 s (was + 0.12: a ghost string).
      Line start defaults KEPT (1.5 ahead / 0.4 right / 0.35 up): the vanilla FishingRod.blockymodel line eye sits ~116 model units
      (~1.8 blocks) up the rod from the hand - a rod held forward-up puts its tip ABOVE eye height, not below it as 0.1.1 assumed.
  UNCHANGED: items (except the 8 rods' looks), stat, interactions, bobber entity + model, catches, bench, saved files, commands.
  ROLLBACK 0.1.2 -> 0.1.1: nothing saved changed (the 5 new Server Setup rows are just ignored by 0.1.1).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISH = os.path.join(ROOT, "SkyyFishing")


def load(name):
    raw = open(os.path.join(FISH, name), "rb").read()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    assert nl == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in " + name
    return raw.decode("utf8").replace("\r\n", "\n"), nl


S = {}


def rep(old, new, count=1):
    assert S["s"].count(old) == count, "anchor count %d != %d: %s" % (S["s"].count(old), count, old[:160])
    S["s"] = S["s"].replace(old, new)


def cut(start, end, new):
    """replace S from the line starting `start` up to (not including) `end` (both unique)"""
    s = S["s"]
    assert s.count(start) == 1 and s.count(end) == 1, (s.count(start), s.count(end), start[:80], end[:80])
    i, j = s.index(start), s.index(end)
    assert i < j
    S["s"] = s[:i] + new + s[j:]


# =========================================================================================================== the build script
s, NL = load("build_skyyfishing_0.1.1.py")
assert 'VERSION = "0.1.1"\n' in s and "GENERATED by tools/fishing_0_1_1_patch.py" in s, "not the SkyyFishing 0.1.1 build"
S["s"] = s
REG0 = s.count("registerSystem(")

rep('"""SkyyFishing 0.1.1 - build script (javassist via jpype). GENERATED by tools/fishing_0_1_1_patch.py from the LIVE build_skyyfishing_0.1.py\n'
    '- edit the patch, never this file. 0.1.1',
    '"""SkyyFishing 0.1.2 - build script (javassist via jpype). GENERATED by tools/fishing_0_1_2_patch.py from build_skyyfishing_0.1.1.py\n'
    '- edit the patch, never this file. 0.1.2 (Skyy 2026-10-09 "dont show the line on the rod, just have the bobber slightly below the tip\n'
    'of the rod." + "but the fishing string is broken. one of the mods had a working fishing string, check that."): the idle rod shows no\n'
    'line, its bobber hangs just under the tip; the line is the ENGINE debug line (DisplayDebug Cylinder pieces - the mechanism Angler\'s\n'
    'Almanac\'s line renderer uses) instead of glowing particle dots (the white cloud); "Something is in the way" only for full solid\n'
    'cubes; no re-cast for 1 s after a catch (the "too shallow" after a catch). Details: tools/fishing_0_1_2_patch.py docstring.\n'
    'Base 0.1.1')
rep("Run:   python SkyyFishing/build_skyyfishing_0.1.1.py   -> SkyyFishing/SkyyFishing-0.1.1.jar\n",
    "Run:   python SkyyFishing/build_skyyfishing_0.1.2.py   -> SkyyFishing/SkyyFishing-0.1.2.jar\n")
rep("Check: python SkyyFishing/test_skyyfishing_0.1.1.py    (-Xverify:all, engine asset validators, every new code path executed, start twice on\n"
    "       a scratch copy of live data, engine-access audit, class compare with 0.1; scratch tools/dev/scratch/fish011/)",
    "Check: python SkyyFishing/test_skyyfishing_0.1.2.py    (-Xverify:all, engine asset validators, every new code path executed, start twice on\n"
    "       a scratch copy of live data, engine-access audit, class compare with 0.1.1; scratch tools/dev/scratch/fish012/)")
rep('VERSION = "0.1.1"\n', 'VERSION = "0.1.2"\n')
rep("    in your hand (0 none), 10..18 = the same while your line is out - that look hides the rod's built-in hanging line + bobber (the real\n"
    "    bobber floats on the water).",
    "    in your hand (0 none), 10..18 = the same while your line is out - that look hides the rod's bobber (the real bobber floats on the\n"
    "    water). 0.1.2: looks 0..8 (and the base Model) = the IDLE models: no line, the bobber hanging just under the tip.")
rep("    our model SkyyFishing_Bobber (the vanilla rod's own red / white bobber node, extracted at build time). The line = small particle dots\n"
    "    from your rod to the bobber (a recoloured vanilla trail light, like the grapple rope), with a little sag.",
    "    our model SkyyFishing_Bobber (the vanilla rod's own red / white bobber node, extracted at build time). The line (0.1.2) = engine\n"
    "    debug-line pieces (DisplayDebug Cylinders, FLAG_NO_WIREFRAME) from the rod tip to the bobber with a little sag, sent to players near.")

# ---- (3) no line particles: the GreenOrbTrail copy (the white cloud) is gone; the colour feeds the engine line
rep('LINE_DOT = "SkyyFishing_Line_Dot"\n', '')
rep('LINE_COLOR = "#e6e6dc"                       # fishing line: an off-white thread (a particle colour, not a UI colour)  ui-data\n',
    'LINE_COLOR = "#e6e6dc"                       # fishing line: an off-white thread (the engine line colour, not a UI colour)  ui-data\n'
    'LINE_RGB = [round(int(LINE_COLOR[i:i + 2], 16) / 255.0, 4) for i in (1, 3, 5)]\n'
    '# 0.1.2 IDLE LOOK (Skyy "dont show the line on the rod, just have the bobber slightly below the tip of the rod."): the vanilla Bait (+ Hook)\n'
    '# re-hung IDLE_DROP model units (64 = 1 block) below the start of the vanilla Line1 (the rod tip), along IDLE_DOWN in the rod\'s\n'
    '# R-Attachment frame (+Y = along the rod; the vanilla line went +Y+Z and showed UP in first person -> down ~ -Y-Z) - UNVERIFIED look\n'
    'IDLE_DROP = 24.0\n'
    'IDLE_DOWN = (0.0, -0.5, -0.8660254)\n')
rep('assert PS_SPLASH in PSYS and "GreenOrbTrail" in PSYS, "particle systems missing"\n',
    'assert PS_SPLASH in PSYS, "particle systems missing"\n')
cut("# ---- the line dots: the vanilla GreenOrbTrail light (the blink trail, deployed) recoloured to the line colour (the grapple rope recipe)\n",
    'put("Server/Languages/en-US/server.lang", "\\n".join(LANG) + "\\n")\n',
    "# ---- 0.1.2: no line particles (SkyyFishing_Line_Dot = the white cloud) - the line is the engine debug line (FishEngApi.sendLine)\n")

# ---- (1) the idle models + the rods' looks 0..8 / base Model
IDLE_CODE = r'''# ---- 0.1.2 idle models: no Line1-4, the Bait (+ Hook) IDLE_DROP units under the line eye (Skyy "bobber slightly below the tip")


def _qrot(q, v):
    x, y, z, w = q
    ix = w * v[0] + y * v[2] - z * v[1]
    iy = w * v[1] + z * v[0] - x * v[2]
    iz = w * v[2] + x * v[1] - y * v[0]
    iw = -x * v[0] - y * v[1] - z * v[2]
    return (ix * w + iw * -x + iy * -z - iz * -y, iy * w + iw * -y + iz * -x - ix * -z, iz * w + iw * -z + ix * -y - iy * -x)


def idle_model(model):
    """the rod model with its posed line removed and its bobber hanging just below the tip (IDLE_DROP along IDLE_DOWN)"""
    m = copy.deepcopy(model)
    roots = [n for n in m["nodes"] if n.get("name") == "R-Attachment"]
    assert len(roots) == 1, "the rod has no single R-Attachment root"
    ro = roots[0].get("orientation") or {"x": 0, "y": 0, "z": 0, "w": 1}
    assert [ro[k] for k in "xyzw"] == [0, 0, 0, 1], "R-Attachment is rotated - re-check IDLE_DOWN"
    l1 = [n for n in roots[0].get("children") or [] if n.get("name") == "Line1"]
    assert len(l1) == 1 and l1[0]["shape"]["type"] == "quad", "the rod's Line1 moved"
    o = l1[0]["orientation"]
    q = (o["x"], o["y"], o["z"], o["w"])
    half = l1[0]["shape"]["settings"]["size"]["y"] / 2.0
    a = _qrot(q, (0.0, half, 0.0))
    p = l1[0]["position"]
    tip = (p["x"] - a[0], p["y"] - a[1], p["z"] - a[2])
    bait = copy.deepcopy(MF.find(m["nodes"], "Bait"))
    assert bait is not None and [c.get("name") for c in bait.get("children") or []] == ["Hook"], "the vanilla Bait / Hook changed"
    bh = bait["shape"]["settings"]["size"]["y"] / 2.0
    dn = IDLE_DOWN
    assert abs(dn[0] ** 2 + dn[1] ** 2 + dn[2] ** 2 - 1.0) < 1e-6 and dn[1] < 0, IDLE_DOWN
    c = [tip[i] + dn[i] * (IDLE_DROP + bh) for i in range(3)]
    bait["position"] = {"x": round(c[0], 4), "y": round(c[1], 4), "z": round(c[2], 4)}
    # the bobber's +Y (toward its line knot; the hook hangs at -Y) points UP = -IDLE_DOWN: a turn about X
    ang = math.atan2(-dn[2], -dn[1])
    bait["orientation"] = {"x": round(math.sin(ang / 2.0), 6), "y": 0.0, "z": 0.0, "w": round(math.cos(ang / 2.0), 6)}
    out = MF.strip_line(m)
    [r for r in out["nodes"] if r.get("name") == "R-Attachment"][0]["children"].append(bait)
    return out, tip, c


IDLE = {}
IDLE_GEOM = {}
for ti, tier in enumerate(TIERS):
    model, _tex, _shipped = MF.build_rod(az, P_ART, tier)
    im, _tip, _ctr = idle_model(model)
    imr, _tip2, _ctr2 = idle_model(MF.strip_reel(model))
    p1 = "%s/SkyyFishing_Rod_%s_Idle.blockymodel" % (ROD_DIR, tier)
    p2 = "%s/SkyyFishing_Rod_%s_NoReel_Idle.blockymodel" % (ROD_DIR, tier)
    put(p1, (json.dumps(im, indent=2) + "\n").encode("utf-8"))
    put(p2, (json.dumps(imr, indent=2) + "\n").encode("utf-8"))
    IDLE[tier] = (p2, p1)
    IDLE_GEOM[tier] = (_tip, _ctr)
'''
rep('''    NOLINE[tier] = (p1, p2)
WAND = vjson(ITEM_PATH["Weapon_Wand_Wood"])''', '''    NOLINE[tier] = (p1, p2)
''' + IDLE_CODE + '''WAND = vjson(ITEM_PATH["Weapon_Wand_Wood"])''')
rep('''    for lk in r["looks"]:
        conds.append({"Condition": [lk["reel"], lk["reel"]], "Model": rel(lk["model"]), "Texture": rel(lk["texture"])})
''', '''    for lk in r["looks"]:
        im_ = IDLE[tier][0] if lk["model"] == r["noreel_model"] else IDLE[tier][1]       # 0.1.2: the idle look (no line, bobber under the tip)
        conds.append({"Condition": [lk["reel"], lk["reel"]], "Model": rel(im_), "Texture": rel(lk["texture"])})
''')
rep('''         "Icon": rel(r["icon"]), "IconProperties": json.loads(json.dumps(PROPS)), "Model": rel(r["model"]), "Texture": rel(r["texture"])}
    d.update(HOLD)''', '''         "Icon": rel(r["icon"]), "IconProperties": json.loads(json.dumps(PROPS)), "Model": rel(IDLE[tier][1]), "Texture": rel(r["texture"])}
    d.update(HOLD)''')

# ---- (2) Server Setup rows: the line rows describe the engine line; 4 new line rows + the re-cast wait
rep('''    ("fish.line.show", "Show the fishing line", "cast", "bool", "true", "", "", "", "", "live",
     "Off = no line particles from the rod to the bobber.", "LINE_SHOW", "boolean"),
    ("fish.line.spacing", "Line dot spacing", "cast", "dec", "0.8", "0.3", "4", "", "blocks", "live,adv",
     "One line particle every this many blocks (smaller = denser line, more particles).", "LINE_SPACING", "double"),
    ("fish.line.everyTicks", "Line refresh (ticks)", "cast", "int", "5", "1", "30", "", "", "live,adv",
     "The line is redrawn every this many server ticks (30 ticks = 1 s).", "LINE_EVERY", "int"),
''', '''    ("fish.line.show", "Show the fishing line", "cast", "bool", "true", "", "", "", "", "live",
     "Off = no line from the rod tip to the bobber.", "LINE_SHOW", "boolean"),
    ("fish.line.spacing", "Line piece length", "cast", "dec", "0.8", "0.3", "4", "", "blocks", "live,adv",
     "The line is drawn as straight pieces this long (smaller = smoother sag, more packets).", "LINE_SPACING", "double"),
    ("fish.line.everyTicks", "Line refresh (ticks)", "cast", "int", "5", "1", "30", "", "", "live,adv",
     "The line is redrawn every this many server ticks (30 ticks = 1 s).", "LINE_EVERY", "int"),
    ("fish.line.thickness", "Line thickness", "cast", "dec", "0.03", "0.01", "0.2", "", "blocks", "live,adv",
     "How thick the fishing line is drawn.", "LINE_THICK", "double"),
    ("fish.line.tipAhead", "Line start: ahead", "cast", "dec", "1.5", "0", "3", "", "blocks", "live,adv",
     "The line starts (rod tip) this far ahead of your eyes.", "TIP_F", "double"),
    ("fish.line.tipRight", "Line start: right", "cast", "dec", "0.4", "-1.5", "1.5", "", "blocks", "live,adv",
     "The line start this far to the right of your eyes (minus = left).", "TIP_R", "double"),
    ("fish.line.tipUp", "Line start: up", "cast", "dec", "0.35", "-1.5", "1.5", "", "blocks", "live,adv",
     "The line start this far above your eyes (minus = below).", "TIP_U", "double"),
    ("fish.recastDelay", "Wait before the next cast", "cast", "dec", "1", "0", "5", "", "s", "live,adv",
     "Clicks right after a catch, a lost fish or reeling in do not cast again for this long.", "RECAST_S", "double"),
''')

# ---- engine classes for the line + the block kinds (every member probed)
rep('''    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
''', '''    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "M4D": "org.joml.Matrix4d",
    "M4U": "com.hypixel.hytale.math.matrix.Matrix4dUtil",
    "DDB": "com.hypixel.hytale.protocol.packets.player.DisplayDebug",
    "DSH": "com.hypixel.hytale.protocol.DebugShape",
    "DBU": "com.hypixel.hytale.server.core.modules.debug.DebugUtils",
    "TCP": "com.hypixel.hytale.protocol.ToClientPacket",
    "PH": "com.hypixel.hytale.server.core.io.PacketHandler",
    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "V3F": "org.joml.Vector3f",
    "DRT": "com.hypixel.hytale.protocol.DrawType",
''')
rep('''    (T["BTY"], "getMaterial", T["BMAT"], []), (T["FLU"], "getId", S_, []),
''', '''    (T["BTY"], "getMaterial", T["BMAT"], []), (T["FLU"], "getId", S_, []),
    (T["BTY"], "getDrawType", T["DRT"], []),
''')
rep('''    (T["PTU"], "spawnParticleEffect", "void", [S_, "org.joml.Vector3dc", T["CAC"]]),
''', '''    (T["PTU"], "spawnParticleEffect", "void", [S_, "org.joml.Vector3dc", T["CAC"]]),
    # 0.1.2 the line: the engine's debug-shape packet (what DebugUtils.addLine sends), to the players near the line only
    (T["M4D"], "<init>", "void", []), (T["M4D"], "translate", T["M4D"], ["double", "double", "double"]),
    (T["M4D"], "rotate", T["M4D"], ["double", "double", "double", "double"]), (T["M4D"], "scale", T["M4D"], ["double", "double", "double"]),
    (T["M4U"], "asFloatData", "float[]", ["org.joml.Matrix4dc"]),
    (T["DDB"], "<init>", "void", [T["DSH"], "float[]", "org.joml.Vector3fc", "float", "byte", "float[]", "float"]),
    (T["V3F"], "<init>", "void", ["float", "float", "float"]),
    (T["WLD"], "getPlayerRefs", "java.util.Collection", []), (T["PR"], "getTransform", T["TRF"], []),
    (T["PR"], "getPacketHandler", T["PH"], []), (T["TRF"], "getPosition", T["V3D"], []),
    (T["PH"], "write", "void", [T["TCP"] + "[]"]),
''')
rep('''               (T["HSV"], "SCHEDULED_EXECUTOR"), (T["FLU"], "EMPTY_ID")):''',
    '''               (T["HSV"], "SCHEDULED_EXECUTOR"), (T["FLU"], "EMPTY_ID"), (T["DSH"], "Cylinder"), (T["DBU"], "FLAG_NO_WIREFRAME"),
               (T["DRT"], "Cube"), (T["DRT"], "CubeWithModel")):''')

# ---- FishDefs: LINE_DOT gone; the line colour, the bobber top, the piece cap, the view range
rep('        "public static final String LINE_DOT = %s;" % jstr(LINE_DOT),\n',
    '        "public static final float[] LINE_RGB = new float[] { %sf, %sf, %sf };" % tuple(repr(v) for v in LINE_RGB),\n'
    '        "public static final double BOB_TOP = 0.12;",\n'
    '        "public static final int MAX_SEG = 8;",\n'
    '        "public static final double VIEW = 64.0;",\n')

# ---- FishApi: the line seam (the harness's stand-in records it; FishEngApi sends the engine line)
rep('''        "public abstract void particle(@PKG@.FishCtx c, String id, double x, double y, double z);",
''', '''        "public abstract void particle(@PKG@.FishCtx c, String id, double x, double y, double z);",
        "public abstract void drawLine(@PKG@.FishCtx c, double[] pts, int n, float secs);",       # 0.1.2: n points (x, y, z each) -> n-1 pieces
''')

# ---- FishEngApi: block kinds (a wall = Solid + a full cube), -1 only for "no chunk section"; the engine line
rep('''    @BSC@ sec = (@BSC@) cst.getComponent(sr, @BSC@.getComponentType());
    if (sec == null) return -1;
    int id = sec.get(x, y, z);
    if (id == @BTY@.EMPTY_ID) return 0;
    Object o = @BTY@.getAssetMap().getAsset(id);
    if (!(o instanceof @BTY@)) return 2;
    return ((@BTY@) o).getMaterial() == @BMAT@.Solid ? 2 : 0;
''', '''    @BSC@ sec = (@BSC@) cst.getComponent(sr, @BSC@.getComponentType());
    if (sec == null) return 0;
    int id = sec.get(x, y, z);
    if (id == @BTY@.EMPTY_ID) return 0;
    return kindOf(@BTY@.getAssetMap().getAsset(id));
''')
rep('''# the block at (x, y, z) of the player's world, never loading a chunk: 1 water (any Water* fluid), 2 solid, 0 open, -1 not loaded
M(EAPI, r"""
public int block(''', '''# 0.1.2: what stops the cast's aim = a Solid FULL CUBE (Cube / CubeWithModel draw type). Model blocks - plants, leaves, lily pads
# (Plant_Flower_Water_* are Solid!), reeds, ferns, branches, fences, slabs, stairs - let the line through (they made "Something is
# in the way" at open water). An unknown block type stays a wall.
M(EAPI, r"""
public static int kindOf(Object o) {
  if (!(o instanceof @BTY@)) return 2;
  @BTY@ b = (@BTY@) o;
  if (b.getMaterial() != @BMAT@.Solid) return 0;
  @DRT@ d = b.getDrawType();
  return (d == @DRT@.Cube || d == @DRT@.CubeWithModel) ? 2 : 0;
}""")
# the block at (x, y, z) of the player's world, never loading a chunk: 1 water (any Water* fluid), 2 a wall (kindOf), 0 open, -1 not loaded
M(EAPI, r"""
public int block(''')
LINE_ENG = r'''# 0.1.2 THE LINE = the engine debug line (the mechanism of Angler's Almanac's line renderer; our own code): one Cylinder DebugShape per
# piece - a unit cylinder moved to the piece's start, turned onto it (yaw about Y, then pitch about X), centred along +Y, scaled
# thickness x length x thickness - in a DisplayDebug packet that lives `secs` seconds, no wireframe, opaque. ONE batch write per
# viewer; only players within FishDefs.VIEW blocks (+ half the line) of the line's middle get it (DebugUtils.add sends to the world).
M(EAPI, r"""
public static @M4D@ segMatrix(double x1, double y1, double z1, double x2, double y2, double z2, double th) {
  double dx = x2 - x1;
  double dy = y2 - y1;
  double dz = z2 - z1;
  double len = Math.sqrt(dx * dx + dy * dy + dz * dz);
  if (len < 0.001) return null;
  @M4D@ m = new @M4D@();
  m.translate(x1, y1, z1);
  m.rotate(-(Math.atan2(dz, dx) + 1.5707963267948966), 0.0, 1.0, 0.0);
  m.rotate(-Math.atan2(Math.sqrt(dx * dx + dz * dz), dy), 1.0, 0.0, 0.0);
  m.translate(0.0, len / 2.0, 0.0);
  m.scale(th, len, th);
  return m;
}""")
M(EAPI, r"""
public static @TCP@[] linePackets(double[] p, int n, float secs, double th) {
  if (p == null || n < 2 || p.length < 3 * n) return new @TCP@[0];
  @TCP@[] pk = new @TCP@[n - 1];
  float[] rgb = @PKG@.FishDefs.LINE_RGB;
  int k = 0;
  for (int i = 0; i + 1 < n; i++) {
    @M4D@ m = segMatrix(p[3 * i], p[3 * i + 1], p[3 * i + 2], p[3 * i + 3], p[3 * i + 4], p[3 * i + 5], th);
    if (m == null) continue;
    pk[k] = new @DDB@(@DSH@.Cylinder, @M4U@.asFloatData(m), new @V3F@(rgb[0], rgb[1], rgb[2]), secs, (byte) @DBU@.FLAG_NO_WIREFRAME, null, 1.0f);
    k = k + 1;
  }
  if (k == pk.length) return pk;
  @TCP@[] q = new @TCP@[k];
  System.arraycopy(pk, 0, q, 0, k);
  return q;
}""")
M(EAPI, r"""
public static int sendLine(java.util.Collection prs, double[] p, int n, float secs, double th) {
  if (prs == null || p == null || n < 2) return 0;
  @TCP@[] pk = linePackets(p, n, secs, th);
  if (pk.length == 0) return 0;
  int e = 3 * (n - 1);
  double mx = (p[0] + p[e]) / 2.0;
  double my = (p[1] + p[e + 1]) / 2.0;
  double mz = (p[2] + p[e + 2]) / 2.0;
  double hx = (p[e] - p[0]) / 2.0;
  double hy = (p[e + 1] - p[1]) / 2.0;
  double hz = (p[e + 2] - p[2]) / 2.0;
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
    } catch (Throwable t2) { @PKG@.FishLog.warnOnce("line:" + t2.getClass().getName(), "a fishing line could not be sent: " + t2); }
  }
  LINE_PKTS = LINE_PKTS + (long) pk.length * (long) sent;
  return sent;
}""")
M(EAPI, r"""
public void drawLine(@PKG@.FishCtx c, double[] pts, int n, float secs) {
  try {
    if (c == null || c.world == null) return;
    sendLine(c.world.getPlayerRefs(), pts, n, secs, @PKG@.FishCfg.LINE_THICK);
  } catch (Throwable t) { @PKG@.FishLog.warnOnce("drawline", "the fishing line could not be drawn: " + t); }
}""")
'''
rep('''M(EAPI, r"""
public void particle(@PKG@.FishCtx c, String id, double x, double y, double z) {''', LINE_ENG + '''M(EAPI, r"""
public void particle(@PKG@.FishCtx c, String id, double x, double y, double z) {''')
rep('''for _f in ("public static volatile int CLICK_I = -1;", "public static volatile int STAT_I = -2;", "public static volatile long CLICKS = 0L;",
''', '''for _f in ("public static volatile int CLICK_I = -1;", "public static volatile int STAT_I = -2;", "public static volatile long CLICKS = 0L;",
           "public static volatile long LINE_PKTS = 0L;",
''')

# ---- FishCore: the cast's ray (-1 = end of the ray, not "in the way"), the line points, the re-cast wait
rep('''    if (b == 1) { hit = true; hx = x; hy = y; hz = z; break; }
    if (b == 2 || b == -1) { blocked = true; break; }
''', '''    if (b == 1) { hit = true; hx = x; hy = y; hz = z; break; }
    if (b == 2) { blocked = true; break; }
    if (b == -1) break;
''')
rep('''           "public static volatile long CANCELS = 0L;", "public static volatile long CLAIMED = 0L;", "public static volatile long DOTS = 0L;",
           "public static volatile long DOT_WINDOW = 0L;", "public static volatile int DOT_USED = 0;",
           "public static final int DOT_BUDGET = 120;", "public static final int MAX_DOTS = 20;", "public static volatile String LAST_WHY = \\"\\";",
''', '''           "public static volatile long CANCELS = 0L;", "public static volatile long CLAIMED = 0L;", "public static volatile long LINES = 0L;",
           "public static volatile long SEGS = 0L;", "public static volatile long QUIETED = 0L;",
           "public static final java.util.concurrent.ConcurrentHashMap QUIET = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile String LAST_WHY = \\"\\";",
''')
# 0.1.2 FIX (critics): the re-cast wait only after a catch (2), a lost fish (1) or the player's own reel-in click - never after a rod
# swap / walking away / a profile or world switch / nothing biting (a cast right after those must work at once)
rep('''# ---- ends: 0 = quiet (reeled in / cancelled: the widget goes at once), 1 = lost (IT GOT AWAY card), 2 = landed (catch card)
''', '''# ---- 0.1.2: the re-cast wait (fish.recastDelay) - set after a catch, a lost fish or the player's own reel-in click only
M(CORE, r"""
public static void hush(java.util.UUID u, long now) {
  if (u != null) QUIET.put(u, Long.valueOf(now + Math.round(@PKG@.FishCfg.RECAST_S * 1000.0)));
}""")
# ---- ends: 0 = quiet (reeled in / cancelled: the widget goes at once), 1 = lost (IT GOT AWAY card), 2 = landed (catch card)
''')
rep('''public static void finish(@PKG@.FishCtx c, @PKG@.FishState s, int how, String why, long now) {
  s.ended = true;
  LAST_WHY = why == null ? "" : why;
''', '''public static void finish(@PKG@.FishCtx c, @PKG@.FishState s, int how, String why, long now) {
  s.ended = true;
  LAST_WHY = why == null ? "" : why;
  if (how != 0) hush(s.uuid, now);
''')
cut("# the line: particle dots from the rod tip to the bobber with a little sag, every fish.line.everyTicks ticks (a global budget per 100 ms)\n",
    "# ---- once per player per world tick (FishTick): the click, the reel look, the profile / world / rod checks, then the phase's work\n",
    r'''# 0.1.2 the line: from the rod tip (eye + fish.line.tipAhead along the look, tipRight sideways, tipUp) to the top of the bobber, a
# little sag (tight while fighting), cut in pieces of fish.line.spacing (2..MAX_SEG); drawn by the API (the engine debug line)
M(CORE, r"""
public static double[] linePts(@PKG@.FishState s, double[] e) {
  double fx = e[3];
  double fy = e[4];
  double fz = e[5];
  double hl = Math.sqrt(fx * fx + fz * fz);
  double rx = hl < 1.0E-6 ? 1.0 : -fz / hl;
  double rz = hl < 1.0E-6 ? 0.0 : fx / hl;
  double tx = e[0] + fx * @PKG@.FishCfg.TIP_F + rx * @PKG@.FishCfg.TIP_R;
  double ty = e[1] + fy * @PKG@.FishCfg.TIP_F + @PKG@.FishCfg.TIP_U;
  double tz = e[2] + fz * @PKG@.FishCfg.TIP_F + rz * @PKG@.FishCfg.TIP_R;
  double by = (s.phase == 2 ? s.by - 0.25 : s.by) + @PKG@.FishDefs.BOB_TOP;
  double dx = s.bx - tx;
  double dy = by - ty;
  double dz = s.bz - tz;
  double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
  int n = (int) Math.ceil(d / Math.max(0.3, @PKG@.FishCfg.LINE_SPACING));
  if (n < 2) n = 2;
  if (n > @PKG@.FishDefs.MAX_SEG) n = @PKG@.FishDefs.MAX_SEG;
  double sag = Math.min(1.2, d * 0.06) * (s.phase == 3 ? 0.3 : 1.0);
  double[] p = new double[3 * (n + 1)];
  for (int i = 0; i <= n; i++) {
    double u = (double) i / (double) n;
    p[3 * i] = tx + dx * u;
    p[3 * i + 1] = ty + dy * u - sag * 4.0 * u * (1.0 - u);
    p[3 * i + 2] = tz + dz * u;
  }
  return p;
}""")
M(CORE, r"""
public static void line(@PKG@.FishCtx c, @PKG@.FishState s, long now) {
  if (!@PKG@.FishCfg.LINE_SHOW) return;
  double[] e = @PKG@.FishEng.API.eye(c);
  if (e == null) return;
  double[] p = linePts(s, e);
  int n = p.length / 3;
  float secs = (float) (Math.max(1, @PKG@.FishCfg.LINE_EVERY) / 30.0 + 0.04);
  @PKG@.FishEng.API.drawLine(c, p, n, secs);
  LINES = LINES + 1L;
  SEGS = SEGS + (long) (n - 1);
}""")
# 0.1.2: a click within fish.recastDelay after a line ended (caught / lost / reeled in) never casts (the fight's clicks cast again before)
M(CORE, r"""
public static boolean quiet(java.util.UUID u, long now) {
  if (u == null) return false;
  Object q = QUIET.get(u);
  if (!(q instanceof Long)) return false;
  if (now < ((Long) q).longValue()) {
    hush(u, now);
    return true;
  }
  QUIET.remove(u, q);
  return false;
}""")
''')
rep('''    if (click) { cancel(c, s, "You reel in your line.", now); return; }
''', '''    if (click) { cancel(c, s, "You reel in your line.", now); hush(c.uuid, now); return; }
''')
rep('''    if (click && ri >= 0) cast(c, id, slot, held, s, now);
''', '''    if (click && ri >= 0) {
      if (quiet(c.uuid, now)) QUIETED = QUIETED + 1L;
      else cast(c, id, slot, held, s, now);
    }
''')
rep('''  if ("left the game".equals(why)) { EPOCHS.remove(u); EPOCH_AT.remove(u); FULLTOLD.remove(u); }''',
    '''  QUIET.remove(u);
  if ("left the game".equals(why)) { EPOCHS.remove(u); EPOCH_AT.remove(u); FULLTOLD.remove(u); }''')

assert "LINE_DOT" not in S["s"] and "GreenOrbTrail" not in S["s"] and "DOT_" not in S["s"], "line-dot leftovers"
assert S["s"].count("registerSystem(") == REG0
open(os.path.join(FISH, "build_skyyfishing_0.1.2.py"), "w", encoding="utf8", newline=NL).write(S["s"])
print("wrote SkyyFishing/build_skyyfishing_0.1.2.py")

# =========================================================================================================== the harness
t, TNL = load("test_skyyfishing_0.1.1.py")
assert 'VERSION = "0.1.1"\n' in t and "GENERATED by tools/fishing_0_1_1_patch.py" in t, "not the SkyyFishing 0.1.1 harness"
S["s"] = t
rep('''"""Harness for SkyyFishing 0.1.1 (GENERATED by tools/fishing_0_1_1_patch.py from test_skyyfishing_0.1.py - edit the patch).
Build first: python SkyyFishing/build_skyyfishing_0.1.1.py

    python SkyyFishing/test_skyyfishing_0.1.1.py [--jar <SkyyFishing-0.1.1.jar>] [--live <a world folder>] [--keep]

0.1.1 adds:''', '''"""Harness for SkyyFishing 0.1.2 (GENERATED by tools/fishing_0_1_2_patch.py from test_skyyfishing_0.1.1.py - edit the patch).
Build first: python SkyyFishing/build_skyyfishing_0.1.2.py

    python SkyyFishing/test_skyyfishing_0.1.2.py [--jar <SkyyFishing-0.1.2.jar>] [--live <a world folder>] [--keep]

0.1.2 adds: L  IDLE LOOK: rod looks 0..8 + the base Model = the _Idle models (no Line1-4; the vanilla Bait + Hook hung under R-Attachment
              0.3-0.5 block below the rod's line eye, pointing down); line-out looks 10..18 = NoLine (no bobber); no particle file left
            C3 CLASS COMPARE vs SkyyFishing-0.1.1.jar (the SET pin): same classes, assets = +16 idle models, -the Line_Dot particle system +
              its Dust / Sparks spawners (the white cloud), only the 8 rod JSONs changed; member diff = exactly the line / water / re-cast members
            X17 on the real BlockType store: kindOf = a wall only for Solid full cubes (grass soil, stone, trunks) - lily pads, giant ferns,
              branches, reeds, leaves, grass plants let the line through (the OLD rule called the Solid ones walls); a stand-in river (bank
              of real Soil_Grass + a giant fern + a lily pad, water 1 / 2 / 3 deep, open water 6 blocks out): open water casts (the old rule:
              "in the way"), 1 deep = "too shallow" measured in the landing column, 2 deep casts, a stone wall = "in the way", an unloaded
              spot = "No water in reach"; the line's points (rod tip from the eye + the tip settings -> the bobber top, sag above the water,
              pieces <= MAX_SEG) drawn on the line cadence with the overlap time; the only particle = the splash AT the bobber; the re-cast
              wait after a catch / reeling in (no "too shallow" from the fight's clicks)
            X15+ FishEngApi.drawLine / sendLine / segMatrix on stand-in players: the near player gets ONE batch of DisplayDebug Cylinder
              pieces (no wireframe, opaque, our colour, the time), the far one nothing; every piece's matrix maps the unit cylinder onto
              its two points with the line thickness
            V+ the Line_Dot particle system is NOT in the store; B+ the line goes FishCore.line -> FishApi.drawLine -> sendLine ->
              PacketHandler.write (no DebugUtils world broadcast, no particle from the line); tickPlayer asks quiet() before a cast
0.1.1 (kept):''')
rep('VERSION = "0.1.1"\nOLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.jar")      # the SET pin (class compare C2)\n',
    'VERSION = "0.1.2"\nOLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.1.jar")    # the SET pin (class compare C3)\n')
rep('SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fish011", "test")))',
    'SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fish012", "test")))')
rep('Scratch: tools/dev/scratch/fish011/test (deleted at the end unless --keep).', 'Scratch: tools/dev/scratch/fish012/test (deleted at the end unless --keep).')
rep('the line dots, the HUD widget, the bench page)', 'the engine line - DisplayDebug pieces - and where it starts, the idle bobber under the tip, the HUD widget, the bench page)')

# ---- J: no particle file; the idle models are in the jar
rep('''                 "Server/Models/SkyyFishing/SkyyFishing_Bobber.json", "Server/Particles/SkyyFishing/SkyyFishing_Line_Dot.particlesystem",
                 "Server/Languages/en-US/server.lang"):
        check(need in assets, "J. %s in the jar" % need)
''', '''                 "Server/Models/SkyyFishing/SkyyFishing_Bobber.json", "Server/Languages/en-US/server.lang"):
        check(need in assets, "J. %s in the jar" % need)
    idle_paths = ["Common/Items/Tools/Fishing_Rod/SkyyFishing_Rod_%s%s_Idle.blockymodel" % (t_, v_) for t_ in TIERS for v_ in ("", "_NoReel")]
    check(all(p_ in assets for p_ in idle_paths) and not [n for n in jn if "Particle" in n],
          "J. 0.1.2: the 16 idle models are in the jar; NO particle file (the Line_Dot system + Dust / Sparks spawners = the white cloud, gone)")
''')
# ---- I: the idle looks (0..8 + base Model) and their geometry; NoLine (10..18) without a bobber
rep('''    check(not bad, "I. 8 rods: 18 conditions (0-8, 10-18) on %s, Secondary = SkyyFishing_Rod_Use, MaxStack 1, no recipe, every file exists, "
                   "line-out looks = NoLine models: %s" % (STAT, bad[:3]))
''', '''    check(not bad, "I. 8 rods: 18 conditions (0-8, 10-18) on %s, Secondary = SkyyFishing_Rod_Use, MaxStack 1, no recipe, every file exists, "
                   "line-out looks = NoLine models: %s" % (STAT, bad[:3]))
    # 0.1.2 L: the idle look (Skyy "dont show the line on the rod, just have the bobber slightly below the tip of the rod.")
    def names_of(m_):
        out_ = []

        def w_(n_, par):
            out_.append((n_.get("name"), par))
            for c_ in n_.get("children") or []:
                w_(c_, n_.get("name"))
        for r_ in m_["nodes"]:
            w_(r_, None)
        return out_

    def qrot(q, v):
        x, y, z, w = q
        ix, iy, iz = w * v[0] + y * v[2] - z * v[1], w * v[1] + z * v[0] - x * v[2], w * v[2] + x * v[1] - y * v[0]
        iw = -x * v[0] - y * v[1] - z * v[2]
        return (ix * w + iw * -x + iy * -z - iz * -y, iy * w + iw * -y + iz * -x - ix * -z, iz * w + iw * -z + ix * -y - iy * -x)
    van = json.loads(az.read("Common/Items/Tools/Fishing_Rod/FishingRod.blockymodel").decode("utf-8-sig"))
    l1 = [c_ for c_ in van["nodes"][0]["children"] if c_["name"] == "Line1"][0]
    q1 = tuple(l1["orientation"][k_] for k_ in "xyzw")
    a1 = qrot(q1, (0.0, l1["shape"]["settings"]["size"]["y"] / 2.0, 0.0))
    eye_ = [l1["position"][k_] - a1[i_] for i_, k_ in enumerate("xyz")]
    lbad, geo = [], []
    for iid in RODS:
        d = items[iid][1]
        conds = d["ItemAppearanceConditions"][STAT]
        idle_ms = [c["Model"] for c in conds if c["Condition"][0] <= 8] + [d["Model"]]
        if any(not m_.endswith("_Idle.blockymodel") for m_ in idle_ms) or not conds[0]["Model"].endswith("_NoReel_Idle.blockymodel"):
            lbad.append((iid, "idle looks", idle_ms[:2]))
        for m_ in sorted(set(idle_ms)):
            md = json.loads(jz.read("Common/" + m_))
            nm_ = names_of(md)
            if [n_ for n_, _p in nm_ if n_ in ("Line1", "Line2", "Line3", "Line4")] or ("Bait", "R-Attachment") not in nm_ or ("Hook", "Bait") not in nm_:
                lbad.append((iid, m_, "nodes"))
                continue
            bait = [c_ for c_ in md["nodes"][0]["children"] if c_["name"] == "Bait"][0]
            bc = [bait["position"][k_] for k_ in "xyz"]
            v_ = [bc[i_] - eye_[i_] for i_ in range(3)]
            vl = sum(x_ * x_ for x_ in v_) ** 0.5
            dist = vl - bait["shape"]["settings"]["size"]["y"] / 2.0
            bq = tuple(bait["orientation"][k_] for k_ in "xyzw")
            up = qrot(bq, (0.0, 1.0, 0.0))
            dn = [x_ / vl for x_ in v_]
            geo.append(round(dist / 64.0, 3))
            if not (0.3 * 64 <= dist <= 0.5 * 64) or dn[1] >= 0 or sum(up[i_] * dn[i_] for i_ in range(3)) > -0.99:
                lbad.append((iid, m_, "geometry", round(dist, 2), dn, up))
        for c in conds:
            if c["Condition"][0] >= 10:
                md = json.loads(jz.read("Common/" + c["Model"]))
                if [n_ for n_, _p in names_of(md) if n_ in ("Line1", "Line2", "Line3", "Line4", "Bait", "Hook")]:
                    lbad.append((iid, c["Model"], "line-out look still has a line / bobber"))
    check(not lbad, "L. idle looks (reel 0..8 + the base Model) = _Idle models: no Line1-4, the vanilla Bait + Hook under R-Attachment "
                    "%s block below the rod's line eye, hanging down (its top toward the tip); line-out looks have no bobber: %s"
          % (sorted(set(geo)), lbad[:3]))
''')
# ---- C: the probe compare - looks 0..8 = the probe's looks with the model swapped for its idle variant (same textures, same art bytes)
rep('''            pc = pd["ItemAppearanceConditions"][STAT]
            oc = [c for c in d["ItemAppearanceConditions"][STAT] if c["Condition"][0] <= 8]
            if pc != oc:
                cbad.append((iid, "looks 0-8 differ"))
            for k in ("Icon", "Model", "Texture", "IconProperties", "PlayerAnimationsId"):
                if pd.get(k) != d.get(k):
                    cbad.append((iid, k))
''', '''            pc = pd["ItemAppearanceConditions"][STAT]
            oc = [c for c in d["ItemAppearanceConditions"][STAT] if c["Condition"][0] <= 8]
            tier_ = iid.rsplit("_", 1)[1]
            want_ = [{"Condition": c["Condition"], "Texture": c["Texture"],
                      "Model": "Items/Tools/Fishing_Rod/SkyyFishing_Rod_%s%s_Idle.blockymodel" % (tier_, "_NoReel" if c["Condition"][0] == 0 else "")}
                     for c in pc]
            if [dict(c) for c in oc] != want_:
                cbad.append((iid, "looks 0-8 differ from the probe's (idle model swap only)"))
            for k in ("Icon", "Texture", "IconProperties", "PlayerAnimationsId"):
                if pd.get(k) != d.get(k):
                    cbad.append((iid, k))
            if d.get("Model") != "Items/Tools/Fishing_Rod/SkyyFishing_Rod_%s_Idle.blockymodel" % tier_:
                cbad.append((iid, "Model"))
''')
rep('''        check(not cbad and ps == st, "C. the 8 rods = SkyyReelProbe 0.1's (looks 0-8, icon, model, texture, art bytes) + 9 line-out looks; the stat = "''',
    '''        check(not cbad and ps == st, "C. the 8 rods = SkyyReelProbe 0.1's (looks 0-8 with the idle model, icon, texture, art bytes) + 9 line-out looks; the stat = "''')
# ---- C3: the class compare vs 0.1.1
cut('def part_compare(jz):\n', '# ====================================================================================================== children\n',
    '''def part_compare(jz):
    """C3: SkyyFishing-0.1.1.jar (the SET pin) vs this jar"""
    if not os.path.isfile(OLD_JAR):
        check(False, "C3. %s not found for the class compare" % OLD_JAR)
        return
    oz = zipfile.ZipFile(OLD_JAR)
    on, nn = set(oz.namelist()), set(jz.namelist())
    ocls, ncls = sorted(n for n in on if n.endswith(".class")), sorted(n for n in nn if n.endswith(".class"))
    check(ocls == ncls, "C3. same classes as 0.1.1 (31 + kit 7): extra %s missing %s" % (sorted(set(ncls) - set(ocls)), sorted(set(ocls) - set(ncls))))
    oa = set(n for n in on if not n.endswith(".class") and n != "manifest.json")
    na = set(n for n in nn if not n.endswith(".class") and n != "manifest.json")
    added, gone = sorted(na - oa), sorted(oa - na)
    changed = sorted(n for n in oa & na if oz.read(n) != jz.read(n))
    want_added = sorted("Common/Items/Tools/Fishing_Rod/SkyyFishing_Rod_%s%s_Idle.blockymodel" % (t_, v_) for t_ in TIERS for v_ in ("", "_NoReel"))
    want_gone = ["Server/Particles/SkyyFishing/SkyyFishing_Line_Dot.particlesystem",
                 "Server/Particles/SkyyFishing/Spawners/SkyyFishing_Line_Dust.particlespawner",
                 "Server/Particles/SkyyFishing/Spawners/SkyyFishing_Line_Sparks.particlespawner"]
    want_changed = sorted("Server/Item/Items/SkyyFishing/Rods/%s.json" % r_ for r_ in RODS)
    check(added == want_added and gone == want_gone and changed == want_changed,
          "C3. assets vs 0.1.1: +16 idle models, -the Line_Dot particle system + its Dust / Sparks spawners, only the 8 rod JSONs changed "
          "(lang, stat, other items, models, art byte for byte): +%s -%s ~%s" % (added[:2], gone, [c for c in changed if c not in want_changed][:4]))
    for r_ in RODS:
        p_ = "Server/Item/Items/SkyyFishing/Rods/%s.json" % r_
        od, nd = json.loads(oz.read(p_)), json.loads(jz.read(p_))
        oc, nc = od.pop("ItemAppearanceConditions")[STAT], nd.pop("ItemAppearanceConditions")[STAT]
        od.pop("Model"), nd.pop("Model")
        same_rest = (od == nd and [c for c in oc if c["Condition"][0] >= 10] == [c for c in nc if c["Condition"][0] >= 10]
                     and [(c["Condition"], c["Texture"]) for c in oc if c["Condition"][0] <= 8] == [(c["Condition"], c["Texture"]) for c in nc if c["Condition"][0] <= 8])
        check(same_rest, "C3. %s: only Model + the 0-8 look models changed (textures, line-out looks, every other key the same)" % r_)
    F_ = "Lcom/skyy/fishing/FishCtx;"
    want_add = {"FishApi": {"drawLine (%s[DIF)V" % F_},
                "FishEngApi": {"LINE_PKTS J", "kindOf (Ljava/lang/Object;)I", "segMatrix (DDDDDDD)Lorg/joml/Matrix4d;",
                               "linePackets ([DIFD)[Lcom/hypixel/hytale/protocol/ToClientPacket;", "sendLine (Ljava/util/Collection;[DIFD)I",
                               "drawLine (%s[DIF)V" % F_},
                "FishCore": {"LINES J", "SEGS J", "QUIETED J", "QUIET Ljava/util/concurrent/ConcurrentHashMap;", "hush (Ljava/util/UUID;J)V",
                             "linePts (Lcom/skyy/fishing/FishState;[D)[D", "quiet (Ljava/util/UUID;J)Z"},
                "FishDefs": {"LINE_RGB [F", "BOB_TOP D", "MAX_SEG I", "VIEW D"},
                "FishCfg": {"LINE_THICK D", "TIP_F D", "TIP_R D", "TIP_U D", "RECAST_S D"}}
    want_rm = {"FishDefs": {"LINE_DOT Ljava/lang/String;"},
               "FishCore": {"DOTS J", "DOT_WINDOW J", "DOT_USED I", "DOT_BUDGET I", "MAX_DOTS I"}}
    bad = []
    for c in ncls:
        of, om = class_members(oz.read(c))
        nf, nm = class_members(jz.read(c))
        short = c.rsplit("/", 1)[1][:-6]
        add_ = (nm - om) | (nf - of)
        rm_ = (om - nm) | (of - nf)
        if add_ != want_add.get(short, set()):
            bad.append((short, "added", sorted(add_ ^ want_add.get(short, set()))))
        if rm_ != want_rm.get(short, set()):
            bad.append((short, "removed", sorted(rm_ ^ want_rm.get(short, set()))))
    check(not bad, "C3. member compare vs 0.1.1: added exactly the line (FishApi / FishEngApi drawLine, sendLine, linePackets, segMatrix, "
                   "kindOf; FishCore linePts, quiet + counters; FishDefs LINE_RGB / BOB_TOP / MAX_SEG / VIEW; 5 FishCfg rows), removed exactly the "
                   "line-dot members (FishDefs.LINE_DOT, FishCore.DOT*): %s" % bad[:4])
    om_ = json.loads(oz.read("manifest.json"))
    nm_ = json.loads(jz.read("manifest.json"))
    om_.pop("Version"), nm_.pop("Version"), om_.pop("Name", None), nm_.pop("Name", None)
    check(om_ == nm_, "C3. manifest unchanged except the version")
    print("C3. class compare vs SkyyFishing-0.1.1.jar: %d classes, %d assets (+16 idle models, -3 particle files); member diffs = the line / water / "
          "re-cast members only" % (len(ncls), len(na)))


''')
# ---- V: the line particle system is gone (the splash stays)
rep('''    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    psys = PSY.getAssetMap().getAsset("SkyyFishing_Line_Dot")
    try:
        psys.toPacket()
        pok = True
    except Exception as e:
        pok = str(e)[:150]
    K.check(psys is not None and pok is True and PSY.getAssetMap().getAsset("Water_Can_Splash") is not None,
            "V: the line particle system is in the store (toPacket ok) + the vanilla splash system it plays: %s" % pok)
''', '''    PSY = JClass("com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem")
    K.check(PSY.getAssetMap().getAsset("SkyyFishing_Line_Dot") is None and PSY.getAssetMap().getAsset("Water_Can_Splash") is not None,
            "V: 0.1.2 - no SkyyFishing_Line_Dot particle system any more (the white cloud); the vanilla splash system is in the store")
''')
rep('''    print("V. the jar loaded as a pack: 0 failed stores, 0 SEVERE / WARNING; 42 items, stat, effect, root (1 ApplyEffect), bobber model, line "
          "particles, bench block; 3 negative controls refused")''',
    '''    print("V. the jar loaded as a pack: 0 failed stores, 0 SEVERE / WARNING; 42 items (rods with idle looks), stat, effect, root (1 ApplyEffect), "
          "bobber model, no line particles, bench block; 3 negative controls refused")''')
# ---- the stand-ins: a PacketHandler that records what is written
rep('''    lk = cp.makeClass(P + ".LookupIn")''', '''    fh = cp.makeClass(P + ".FakeHandler")
    fh.setSuperclass(cp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    fh.addField(CtField.make("public java.util.ArrayList got;", fh))
    fh.addMethod(CtNewMethod.make("""public void write(com.hypixel.hytale.protocol.ToClientPacket[] p) {
  if (this.got == null) this.got = new java.util.ArrayList();
  this.got.add(p);
}""", fh))
    fh.addMethod(CtNewMethod.make("""public void write(com.hypixel.hytale.protocol.ToClientPacket p) {
  if (this.got == null) this.got = new java.util.ArrayList();
  this.got.add(new com.hypixel.hytale.protocol.ToClientPacket[] { p });
}""", fh))
    fh.writeFile(out_dir)
    lk = cp.makeClass(P + ".LookupIn")''')
# ---- X: the stand-in API: block ids through the REAL kindOf, particle positions, the line
rep('''    W.hud_cmds = 0
''', '''    W.hud_cmds = 0
    W.parts, W.lines, W.kind_fn = [], [], None
''')
rep('''        def block(self, c, x, y, z): return W.cells.get((int(x), int(y), int(z)), 2 if int(y) < 60 else 0)
''', '''        def block(self, c, x, y, z):
            v_ = W.cells.get((int(x), int(y), int(z)), 2 if int(y) < 60 else 0)
            return W.kind_fn(v_) if isinstance(v_, str) else v_
''')
rep('''        def particle(self, c, i, x, y, z): W.log.append(("particle", str(i)))
''', '''        def particle(self, c, i, x, y, z):
            W.log.append(("particle", str(i)))
            W.parts.append((str(i), float(x), float(y), float(z)))

        @JOverride
        def drawLine(self, c, p, n, secs):
            W.lines.append(([float(v) for v in p], int(n), float(secs)))
            W.log.append(("line", int(n)))
''')
rep('''            "X: FishCfg.load seeds config.properties with the defaults and reads them back (range 12, bar 35, pulls, 13 junk lines, Pond VI = 1000)")
''', '''            "X: FishCfg.load seeds config.properties with the defaults and reads them back (range 12, bar 35, pulls, 13 junk lines, Pond VI = 1000)")
    K.check(abs(float(Cfg.RECAST_S) - 1.0) < 1e-9 and abs(float(Cfg.LINE_THICK) - 0.03) < 1e-9 and abs(float(Cfg.TIP_F) - 1.5) < 1e-9
            and abs(float(Cfg.TIP_R) - 0.4) < 1e-9 and abs(float(Cfg.TIP_U) - 0.35) < 1e-9 and abs(float(Cfg.LINE_SPACING) - 0.8) < 1e-9
            and int(Cfg.LINE_EVERY) == 5, "X: 0.1.2 rows seeded + read: recastDelay 1 s, line thickness 0.03, tip 1.5 / 0.4 / 0.35, piece 0.8, every 5 ticks")
    Cfg.RECAST_S = 0.0          # the older flows click again at once; X17 tests the wait with 1 s
''')
# ---- X14: the old dot cap -> the line's pieces; then X17
X17 = r'''    # ============================================================================ X17 0.1.2: block kinds, a river, the line, particles, the re-cast wait
    EA_ = P("FishEngApi")
    BTk = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    BMk = JClass("com.hypixel.hytale.protocol.BlockMaterial")
    want_k = {"Soil_Grass": 2, "Soil_Dirt": 2, "Rock_Stone": 2, "Wood_Oak_Trunk": 2, "Plant_Flower_Water_Blue": 0, "Plant_Fern_Giant": 0,
              "Wood_Oak_Branch_Long": 0, "Plant_Reeds_Water": 0, "Plant_Leaves_Oak": 0, "Plant_Grass_Lush": 0, "Plant_Grass_Sharp": 0,
              "Soil_Grass_Half": 0, "Plant_Fern": 0}
    got_k, old_k, mat_k, miss_k = {}, {}, {}, []
    for bid, wk in sorted(want_k.items()):
        bt_ = BTk.getAssetMap().getAsset(bid)
        if bt_ is None:
            miss_k.append(bid)
            continue
        got_k[bid] = int(EA_.kindOf(bt_))
        old_k[bid] = 2 if bt_.getMaterial() == BMk.Solid else 0
        mat_k[bid] = "%s/%s" % (bt_.getMaterial(), bt_.getDrawType())
    K.check(len(got_k) >= 9 and "Soil_Dirt" in got_k and "Plant_Fern_Giant" in got_k and "Plant_Flower_Water_Blue" in got_k and "Rock_Stone" in got_k
            and all(got_k[b_] == want_k[b_] for b_ in got_k) and int(EA_.kindOf(None)) == 2,
            "X17: kindOf on REAL block types = a wall only for Solid full cubes (soil / stone / trunk); lily pads, giant ferns, branches, reeds, "
            "leaves, grass plants, half blocks let the line through; an unknown type stays a wall: %s (absent %s)" % (got_k, miss_k))
    old_walls = sorted(b_ for b_ in got_k if old_k[b_] == 2 and got_k[b_] == 0)
    K.check(len(old_walls) >= 2, "X17: what was wrong - the 0.1.1 rule (material Solid) called these see-through blocks walls: %s" % old_walls)
    K.notes.append("X17 block kinds (material/drawType): %s; 0.1.1 walls that are not walls now: %s" % (mat_k, old_walls))
    W.kind_fn = lambda b_: int(EA_.kindOf(BTk.getAssetMap().getAsset(b_)))

    BANK = "Soil_Grass" if "Soil_Grass" in got_k else "Soil_Dirt"     # the bare test loader has no Soil_Grass block type; Soil_Dirt = same kind

    def river():
        W.cells.clear()
        for x_ in range(-8, 12):
            for z_ in range(-2, 8):
                for y_ in range(55, 63):
                    W.cells[(x_, y_, z_)] = BANK
        for x_ in range(1, 12):
            for z_ in range(-2, 8):
                depth_ = 1 if x_ == 1 else (2 if x_ == 2 else 3)
                for y_ in range(63 - depth_, 63):
                    W.cells[(x_, y_, z_)] = 1
        W.cells[(0, 63, 2)] = "Plant_Fern_Giant"          # a giant fern on the bank edge (2 tall)
        W.cells[(0, 64, 2)] = "Plant_Fern_Giant"
        W.cells[(4, 63, 2)] = "Plant_Flower_Water_Blue"   # a lily pad on the water

    def aim_at(tx, ty, tz):
        ex, ey, ez = -3.0, 64.6, 2.5
        dx, dy, dz = tx - ex, ty - ey, tz - ez
        L_ = (dx * dx + dy * dy + dz * dz) ** 0.5
        W.eye = [ex, ey, ez, dx / L_, dy / L_, dz / L_]
        W.feet = [ex, 63.0, ez]
        return JArray(JClass("double"))(W.eye)
    Cfg.RECAST_S = 0.0
    Core.STATES.clear()
    W.held, W.slot = rod("Bamboo", ("1", "", "", "")), 0
    river()
    outw = JArray(JClass("int"))(3)
    e_open = aim_at(6.5, 62.9, 2.5)
    c_new = int(Core.water(C1, e_open, outw))
    land_open = [int(outw[0]), int(outw[1]), int(outw[2])]
    def old_rule(b_):                                                                                  # the 0.1.1 rule, for the record
        o_ = BTk.getAssetMap().getAsset(b_)
        return 2 if o_ is None or o_.getMaterial() == BMk.Solid else 0
    W.kind_fn = old_rule
    c_old = int(Core.water(C1, e_open, outw))
    W.kind_fn = lambda b_: int(EA_.kindOf(BTk.getAssetMap().getAsset(b_)))
    K.check(c_new == 1 and land_open[0] in (5, 6) and land_open[1] == 62 and c_old == 4,
            "X17 river: open water 6+ blocks out past a giant fern + a lily pad = a cast (lands at %s, 3 deep); the 0.1.1 rule said "
            "'Something is in the way' here (code %d)" % (land_open, c_old))
    W.log, W.parts, W.lines = [], [], []
    tick(1, 4000)
    W.click = True
    tick()
    s = state()
    K.check(s is not None and int(s.phase) == 1 and abs(float(s.by) - 62.8) < 1e-9 and not [t_ for t_ in tells() if "in the way" in t_],
            "X17 river: the real cast lands ON the water surface where aimed (%s)" % ([float(s.bx), float(s.by), float(s.bz)] if s else tells()[-2:]))
    # the line points: rod tip from the eye + the tip settings -> the bobber's top, sag above the water, pieces <= MAX_SEG
    pts = [float(v) for v in Core.linePts(s, e_open)]
    ev = W.eye
    hl = (ev[3] ** 2 + ev[5] ** 2) ** 0.5
    tip = [ev[0] + ev[3] * 1.5 + (-ev[5] / hl) * 0.4, ev[1] + ev[4] * 1.5 + 0.35, ev[2] + ev[5] * 1.5 + (ev[3] / hl) * 0.4]
    end = [float(s.bx), float(s.by) + 0.12, float(s.bz)]
    npt = len(pts) // 3
    dline = sum((end[i_] - tip[i_]) ** 2 for i_ in range(3)) ** 0.5
    mi = npt // 2
    mid = pts[3 * mi: 3 * mi + 3]
    chord_mid_y = tip[1] + (end[1] - tip[1]) * (mi / float(npt - 1))
    K.check(all(abs(pts[i_] - tip[i_]) < 1e-9 for i_ in range(3)) and all(abs(pts[3 * (npt - 1) + i_] - end[i_]) < 1e-9 for i_ in range(3))
            and npt - 1 == min(8, max(2, int(-(-dline // 0.8)))) and mid[1] < chord_mid_y and min(pts[1::3]) > float(s.by),
            "X17 line: starts at the rod tip (eye + 1.5 ahead, 0.4 right, 0.35 up), ends on the bobber's top, %d pieces of <= 0.8 block, sags "
            "below the straight line but never under the bobber (lowest %.2f > %.2f)" % (npt - 1, min(pts[1::3]), float(s.by)))
    W.lines = []
    tick(10)
    K.check(len(W.lines) == 2 and all(abs(l_[2] - (5 / 30.0 + 0.04)) < 1e-6 for l_ in W.lines) and W.lines[0][1] >= 3,
            "X17 line: drawn every 5 ticks while waiting (2 in 10 ticks), each piece lives 5/30 + 0.04 s (one tick of overlap, no ghost): %s"
            % [(l_[1], round(l_[2], 3)) for l_ in W.lines])
    s.biteAt = W.now + 50
    tick(3)
    K.check(int(s.phase) == 2 and W.parts == [("Water_Can_Splash", float(s.bx), float(s.by), float(s.bz))],
            "X17 particles: from the cast through the bite the ONLY particle is the splash, AT the bobber on the water (no line dots, nothing "
            "between you and the water): %s" % W.parts)
    tick(5)
    bl = W.lines[-1]
    K.check(abs(bl[0][-2] - (float(s.by) - 0.25 + 0.12)) < 1e-9, "X17 line: during the bite the line follows the dipped bobber")
    Core.cancel(C1, s, None, JLong(W.now))
    Core.STATES.clear()
    # the depth is measured in the landing column: 1 deep = too shallow, 2 deep casts (the 2-block rule kept)
    del W.log[:]
    e1 = aim_at(1.5, 62.9, 2.5)
    c1_ = int(Core.water(C1, e1, outw))
    l1_ = [int(outw[0]), int(outw[1])]
    e2 = aim_at(2.5, 62.9, 2.5)
    c2_ = int(Core.water(C1, e2, outw))
    l2_ = [int(outw[0]), int(outw[1])]
    K.check(c1_ == 2 and l1_ == [1, 62] and c2_ == 1 and l2_ == [2, 62],
            "X17 depth: aiming at the 1-deep strip = 'too shallow' measured AT that column %s; the 2-deep strip casts %s" % (l1_, l2_))
    aim_at(1.5, 62.9, 2.5)
    tick(1, 4000)
    W.click = True
    tick()
    K.check(state() is None and any("too shallow" in t_ for t_ in tells()), "X17 depth: the real click at the 1-deep strip says 'too shallow'")
    # a real wall in the aim (on the bank = 'in the way'; over the water = the bobber drops in front of it) + an unloaded spot
    W.cells[(-1, 63, 2)] = "Rock_Stone"
    W.cells[(-1, 64, 2)] = "Rock_Stone"
    cw = int(Core.water(C1, aim_at(6.5, 62.9, 2.5), outw))
    del W.cells[(-1, 63, 2)]
    del W.cells[(-1, 64, 2)]
    W.cells[(3, 63, 2)] = "Rock_Stone"
    W.cells[(3, 64, 2)] = "Rock_Stone"
    cf = int(Core.water(C1, aim_at(6.5, 62.9, 2.5), outw))
    lf = [int(outw[0]), int(outw[1])]
    del W.cells[(3, 63, 2)]
    del W.cells[(3, 64, 2)]
    W.cells[(1, 63, 2)] = -1
    W.cells[(1, 64, 2)] = -1
    cu = int(Core.water(C1, aim_at(6.5, 62.9, 2.5), outw))
    del W.cells[(1, 63, 2)]
    del W.cells[(1, 64, 2)]
    K.check(cw == 4 and cu == 0 and cf == 1 and lf == [2, 62],
            "X17: a stone wall on the bank in the aim = 'Something is in the way' (%d); a wall standing in the water = the bobber drops into the "
            "water just in front of it (%d at %s); an unloaded spot only ends the ray = 'No water in reach' (%d), never 'in the way'" % (cw, cf, lf, cu))
    # the re-cast wait: a click right after a catch / reeling in does not cast (the 0.1.1 "too shallow" right after a catch)
    Cfg.RECAST_S = 1.0
    aim_at(6.5, 62.9, 2.5)
    tick(1, 4000)
    W.click = True
    tick()
    s = state()
    g0 = int(s.gen) if s is not None else -1
    q0 = int(Core.QUIETED)
    Core.finish(C1, s, 2, "landed", JLong(W.now))          # landed (the result card, phase 5)
    del W.log[:]
    aim_at(1.5, 62.9, 2.5)                                 # the fight's next click, now aimed at the shallow bank
    W.click = True
    tick()
    s1 = state()
    bad_t = [t_ for t_ in tells() if "shallow" in t_ or "in the way" in t_ or "No water" in t_]
    K.check(s1 is not None and int(s1.gen) == g0 and int(s1.phase) == 5 and not bad_t and int(Core.QUIETED) == q0 + 1,
            "X17 re-cast: the click right after a catch casts nothing and says nothing (0.1.1 cast again -> 'too shallow'): %s %s"
            % (tells(), int(Core.QUIETED) - q0))
    tick(1, 1100)
    aim_at(6.5, 62.9, 2.5)
    W.click = True
    tick()
    s2 = state()
    K.check(s2 is not None and int(s2.gen) != g0 and int(s2.phase) == 1, "X17 re-cast: after fish.recastDelay (1 s) the next click casts")
    W.click = True
    tick()
    K.check(state() is None and any("reel in your line" in t_ for t_ in tells()), "X17 re-cast: a click while waiting reels in")
    W.click = True
    tick()
    K.check(state() is None and int(Core.QUIETED) == q0 + 2, "X17 re-cast: ... and the click right after reeling in does not cast either")
    # FIX (critics): other line ends (rod put away / walked off / nothing biting / profile switch / busy) set NO wait - the next click casts
    tick(1, 1100)
    W.click = True
    tick()
    s3 = state()
    ok3 = s3 is not None and int(s3.phase) == 1
    Core.cancel(C1, s3, "You put the rod away - your line is reeled in.", JLong(W.now))
    nq3 = not Core.QUIET.containsKey(U1)
    W.click = True
    tick()
    s4 = state()
    K.check(ok3 and nq3 and s4 is not None and int(s4.phase) == 1 and int(Core.QUIETED) == q0 + 2,
            "X17 FIX re-cast: a line ended by putting the rod away (cancel, how 0) sets no wait - the very next click casts at once")
    # a lost fish (how 1) DOES set the wait
    Core.finish(C1, s4, 1, "test lost", JLong(W.now))
    K.check(Core.QUIET.containsKey(U1), "X17 FIX re-cast: a lost fish (how 1) sets the wait")
    # FIX (critics): drop() clears the wait on EVERY path (world change / shutdown too), not only 'left the game'
    Core.drop(U1, "world change")
    K.check(not Core.QUIET.containsKey(U1), "X17 FIX: drop('world change') clears the re-cast wait entry")
    Core.hush(U1, JLong(W.now))
    Core.drop(U1, "shutdown")
    K.check(not Core.QUIET.containsKey(U1), "X17 FIX: drop('shutdown') clears the re-cast wait entry")
    # FIX 2 (critic): the wait is a debounce - every swallowed click pushes it out again, so a fast-click burst that runs on for
    # 3 s after the landing never casts at the bank; the first click a full recastDelay after the LAST swallowed click casts
    Core.STATES.clear()
    Core.QUIET.clear()
    del W.log[:]
    qb = int(Core.QUIETED)
    Core.hush(U1, JLong(W.now))                            # the fish lands
    aim_at(1.5, 62.9, 2.5)                                 # still clicking, now aimed at the shallow bank
    tick(10, 300, click_every=1)                           # 10 clicks over 3 s (0.3 s apart - slower than a fast clicker)
    burst_ok = state() is None and int(Core.QUIETED) == qb + 10 and not [t_ for t_ in tells() if "shallow" in t_ or "in the way" in t_]
    tick(1, 900)
    W.click = True
    tick()
    held_ok = state() is None and int(Core.QUIETED) == qb + 11
    tick(1, 1100)
    aim_at(6.5, 62.9, 2.5)
    W.click = True
    tick()
    s5 = state()
    K.check(burst_ok and held_ok and s5 is not None and int(s5.phase) == 1,
            "X17 FIX 2 re-cast debounce: 10 clicks over 3 s after a landing + one 0.93 s later never cast (no 'too shallow'); "
            "1.1 s after the last click the next click casts: %s %s %s" % (burst_ok, held_ok, tells()[-2:]))
    Core.STATES.clear()
    Cfg.RECAST_S = 0.0
    Core.QUIET.clear()
    Core.STATES.clear()
    W.kind_fn = None
    pond()
    aim_ok()
'''
rep('''    # ---- FIX: the line is at most 20 dots per player per draw
    s = cast_now()
    sp0 = Cfg.LINE_SPACING
    Cfg.LINE_SPACING = 0.3
    s.bx, s.bz = s.bx + 10.0, s.bz + 5.0
    del W.log[:]
    Core.DOT_WINDOW = 0
    Core.line(C1, s, JLong(W.now))
    Cfg.LINE_SPACING = sp0
    nd = sum(1 for e in W.log if e[0] == "particle")
    K.check(int(Core.MAX_DOTS) == 20 and 0 < nd <= 19, "X14 FIX: a long line at spacing 0.3 draws %d dots (cap 20 per player)" % nd)
    Core.cancel(C1, s, None, JLong(W.now))
    Core.STATES.clear()
''', '''    # ---- 0.1.2: a long line at the smallest piece length is at most MAX_SEG pieces, drawn ONCE through the API, no particle
    s = cast_now()
    sp0 = Cfg.LINE_SPACING
    Cfg.LINE_SPACING = 0.3
    s.bx, s.bz = s.bx + 10.0, s.bz + 5.0
    del W.log[:]
    del W.lines[:]
    Core.line(C1, s, JLong(W.now))
    Cfg.LINE_SPACING = sp0
    nd = sum(1 for e in W.log if e[0] == "particle")
    K.check(int(Defs.MAX_SEG) == 8 and len(W.lines) == 1 and W.lines[0][1] == 9 and nd == 0,
            "X14 0.1.2 FIX: a long line at piece 0.3 = ONE drawLine of %s points (8 pieces max: half the packets of the first 0.1.2 build), no particle" % ([l_[1] for l_ in W.lines]))
    Core.cancel(C1, s, None, JLong(W.now))
    Core.STATES.clear()
''' + X17)
# ---- X15: the engine line on stand-in players (near + far) + the cylinder matrix
rep('''    K.check(int(EA.block(c3, 0, 64, 0)) == -1, "X15: FishEngApi.block without a world = -1 (never throws, never loads a chunk)")
''', '''    K.check(int(EA.block(c3, 0, 64, 0)) == -1, "X15: FishEngApi.block without a world = -1 (never throws, never loads a chunk)")
    # 0.1.2 the engine line: a stand-in world with a near and a far player (recording packet handlers)
    EA_ = P("FishEngApi")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRc = JClass("com.hypixel.hytale.math.vector.Transform")
    WLc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    FHc = JClass(FAKE_PKG + ".FakeHandler")
    DDc = JClass("com.hypixel.hytale.protocol.packets.player.DisplayDebug")
    DSc = JClass("com.hypixel.hytale.protocol.DebugShape")

    def fake_player(x, y, z):
        p_ = us.allocateInstance(PRc.class_)
        h_ = us.allocateInstance(FHc.class_)
        h_.got = AL()
        jf(PRc, "transform").set(p_, TRc(V3(x, y, z), R3()))
        jf(PRc, "packetHandler").set(p_, h_)
        return p_, h_
    near, hn = fake_player(2.0, 64.0, 2.0)
    far, hf = fake_player(250.0, 64.0, 2.0)
    wl = us.allocateInstance(WLc.class_)
    plist = AL()
    plist.add(near)
    plist.add(far)
    plist.add(JClass("java.lang.String")("not a player"))
    jf(WLc, "playerRefs").set(wl, plist)
    c4 = Ctx(U1, "Skyy", ref, store, buf, wl, pr)
    lp = [0.5, 65.5, 2.0, 3.0, 64.2, 2.0, 6.5, 62.92, 2.5]
    pk0 = int(EA_.LINE_PKTS)
    EA.drawLine(c4, JArray(JClass("double"))(lp), 3, JFloat(0.3))
    got = [list(b_) for b_ in hn.got]
    pieces = got[0] if len(got) == 1 else []
    okp = len(pieces) == 2 and all(DDc.class_.isInstance(p_) and p_.shape == DSc.Cylinder and int(p_.flags) == 2 and abs(float(p_.time) - 0.3) < 1e-6
                                     and abs(float(p_.opacity) - 1.0) < 1e-6 and len(list(p_.matrix)) == 16
                                     and abs(float(p_.color.x()) - 0.902) < 0.001 and abs(float(p_.color.z()) - 0.8627) < 0.001 for p_ in pieces)
    K.check(okp and hf.got.size() == 0 and int(EA_.LINE_PKTS) == pk0 + 2,
            "X15 0.1.2: FishEngApi.drawLine -> sendLine: the near player gets ONE batch of 2 DisplayDebug Cylinder pieces (no wireframe, opaque, "
            "our off-white, 0.3 s), the far player (250 blocks) nothing, a non-player entry is skipped: near %s far %d" % ([len(g_) for g_ in got], hf.got.size()))
    V3c = JClass("org.joml.Vector3d")
    mbad = []
    for i_ in range(2):
        a_, b_ = lp[3 * i_: 3 * i_ + 3], lp[3 * i_ + 3: 3 * i_ + 6]
        m_ = EA_.segMatrix(a_[0], a_[1], a_[2], b_[0], b_[1], b_[2], 0.03)
        p0 = m_.transformPosition(V3c(0.0, -0.5, 0.0))
        p0 = [float(p0.x()), float(p0.y()), float(p0.z())]
        p1 = m_.transformPosition(V3c(0.0, 0.5, 0.0))
        p1 = [float(p1.x()), float(p1.y()), float(p1.z())]
        pr_ = m_.transformPosition(V3c(0.5, -0.5, 0.0))
        pr_ = [float(pr_.x()), float(pr_.y()), float(pr_.z())]
        rr = sum((pr_[k_] - p0[k_]) ** 2 for k_ in range(3)) ** 0.5
        if max([abs(p0[k_] - a_[k_]) for k_ in range(3)] + [abs(p1[k_] - b_[k_]) for k_ in range(3)]) > 1e-9 or abs(rr - 0.015) > 1e-9:
            mbad.append((i_, p0, p1, rr))
    up_ = EA_.segMatrix(0.0, 60.0, 0.0, 0.0, 61.0, 0.0, 0.03).transformPosition(V3c(0.0, 0.5, 0.0))
    K.check(not mbad and abs(float(up_.y()) - 61.0) < 1e-9 and EA_.segMatrix(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.03) is None
            and int(EA_.sendLine(plist, JArray(JClass("double"))(lp), 1, JFloat(0.3), 0.03)) == 0,
            "X15 0.1.2: segMatrix maps the unit cylinder's ends (0, -+0.5, 0) exactly onto each piece's two points with the line thickness "
            "(also straight up), a zero-length piece = no piece, one point = nothing sent: %s" % mbad[:2])
    EA.drawLine(Ctx(U1, "Skyy", ref, store, buf, None, pr), JArray(JClass("double"))(lp), 3, JFloat(0.3))
    K.check(int(EA_.LINE_PKTS) == pk0 + 2, "X15 0.1.2: drawLine without a world sends nothing and never throws")
''')
# ---- B: the line path + the re-cast gate
rep('''            and "FishApi.later" in calls_of("FishCore", "kick"), "B: land() saves claims then kicks ONE hand-over task (kick -> API.later)")
''', '''            and "FishApi.later" in calls_of("FishCore", "kick"), "B: land() saves claims then kicks ONE hand-over task (kick -> API.later)")
    ln_, dl_, sl_ = calls_of("FishCore", "line"), calls_of("FishEngApi", "drawLine"), calls_of("FishEngApi", "sendLine")
    every_ = []
    for cl_ in ("FishCore", "FishEngApi"):
        for m_ in ("line", "linePts", "drawLine", "sendLine", "linePackets", "segMatrix", "tickPlayer", "particle", "bite", "cast"):
            try:
                every_ += calls_of(cl_, m_)
            except Exception:
                pass
    K.check("FishApi.drawLine" in ln_ and "FishCore.linePts" in ln_ and not [c_ for c_ in ln_ if "particle" in c_.lower()]
            and "FishEngApi.sendLine" in dl_ and "PacketHandler.write" in sl_ and "FishEngApi.linePackets" in sl_
            and not [c_ for c_ in every_ if c_.startswith("DebugUtils.")],
            "B 0.1.2: FishCore.line -> linePts + FishApi.drawLine (no particle); FishEngApi.drawLine -> sendLine -> linePackets + "
            "PacketHandler.write to the near players (never DebugUtils' whole-world send): %s | %s | %s" % (ln_, dl_, sl_))
    K.check("FishCore.quiet" in calls_of("FishCore", "tickPlayer") and "FishEngApi.kindOf" in calls_of("FishEngApi", "block")
            and "BlockType.getDrawType" in calls_of("FishEngApi", "kindOf"),
            "B 0.1.2: tickPlayer asks quiet() before a cast; block() classifies through kindOf (material + draw type): %s" % calls_of("FishEngApi", "kindOf"))
''')

assert S["s"].count("0.1.1 adds:") == 0
open(os.path.join(FISH, "test_skyyfishing_0.1.2.py"), "w", encoding="utf8", newline=TNL).write(S["s"])
print("wrote SkyyFishing/test_skyyfishing_0.1.2.py")
