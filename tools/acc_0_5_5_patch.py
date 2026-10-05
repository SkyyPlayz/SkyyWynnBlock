"""Derive SkyyAccessories/build_skyyaccessories_0.5.5.py from the GENERATED 0.5.4 script (build_skyyaccessories_0.5.4.py = the
tools/deploy_set.py SET pin, itself written by tools/acc_0_5_4_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.4 script
stays untouched - never re-run acc_0_5_4_patch.py on top of this), and SkyyAccessories/test_skyyaccessories_0.5.5.py from the 0.5.4
harness (every 0.5.4 check carried forward, run in the 0.5.4 light layout, + the new sections below).
Run:  python tools/acc_0_5_5_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.5.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.5.py

0.5.5 = LANTERN SMOOTH EDGES (lean round). Skyy 2026-10-04 (docs/answered/bags.md, Lantern squares test), verbatim: "2, try to smooth
the edges" -> option 2 (Advanced "Hidden light: highest" 128 -> 64) looked better; this build makes 64 the default and smooths the lit
edge.

WHY THE EDGE WAS HARD (the client's own shader text in HytaleClient.exe, LightCluster_inc.glsl / LightClusteredFS.glsl, read-only): every
dynamic light is cut off at 0.635 x its level (the CPU cut-off; the shader's own zero is 10/15 x level), world light = min(1, 3 x light),
lights combine with MAX. At the cut-off a light still gives 0.000552 x level, so the lit disc ends in a STEP of 0.00166 x level (world
brightness): the 0.5.4 Legendary helper (level 208, 123 blocks up) ended its 48-block disc at 35 % brightness -> 0, and lower ground (the
sphere around the light cuts it closer) shows that step as hard, blocky dark patches (UNVERIFIED that this is all of Skyy's "squares": the
client also bins lights into screen tiles x depth slices - ZSliceLightData / ClusterBBox; a step that small cannot show as a square).
The step only shrinks with a weaker light, and the brightness cap (bits near the wearer no brighter than torch-lit dust) puts a light of
level E at least ~0.53 E blocks up, where its ground footprint is only ~0.37 E blocks. So a long soft reach needs SEVERAL weaker lights.

WHAT 0.5.5 DOES
 - SOFTER HIDDEN LIGHTS: every hidden light is at most lantern.edge bright (new Advanced row "Hidden lights: brightest", default 96, 8-255;
   255 = no limit = 0.5.4). A rarity whose reach one such light can give keeps ONE light (Unique 31 at 14 up and Rare 72 at 38 up: exactly
   0.5.4). Otherwise the light above the wearer gets a RING of M more lights of the same level and height around it at radius R (the
   smallest M from 3 and then the smallest R in half blocks whose lit ground - walked outward in 0.25-block steps toward a ring light and
   between two ring lights, the worst of both - reaches the reach row with no dark gap; the most lights per wearer = lantern.lights, new
   Advanced row "Hidden lights: most", default 7, 1-9; 1 = the 0.5.4 single light). Legendary default: level 95 at 52 up + 5 around it at
   27.5 blocks = 6 lights; the ground stays ~0.8 bright to ~25 blocks and fades smoothly to 0.16 at 48 (0.5.4: fully lit to 24, then
   0.35 -> 0 at 48); the last step is 0.16 instead of 0.35 and in the direction of a ring light the fade goes on to ~56.
   Every light obeys the 0.5.4 brightness cap (its level <= the most allowed at its height - 3, so anything at or under the wearer's
   feet level + 3 gets no more than torch-lit dust from it), never higher than lantern.height, white (red = green = blue).
 - lantern.height default 128 -> 64 (Skyy's pick). ONE-TIME UPDATE of an existing config.properties (AccCfg.migrate055, setup() after
   migrate051 and before the loader; the 0.5.1 migrate051 pattern): a one-line lantern.height entry that still holds the old default 128
   becomes 64 (the value text only: key, separator and line ending stay); any other value is kept and noted; History copy of the old file
   first (verified byte for byte, else nothing is written), one config-changes.log line `SkyyAccessories 0.5.5 \t - \t update \t
   lantern.height \t 128 \t 64 \t ok` (Server Setup -> Changes can Undo it), and a marker comment ("SkyyAccessories 0.5.5 Lantern
   defaults") above the entry - or at the end of a file without one (Skyy's live file has no lantern line: it only gets the marker, so a
   later in-game 128 is never turned back) - so it runs once; every other byte and the line endings stay. A fresh file carries the marker.
 - THE RING ENTITIES are the 0.5.4 helper entity (Transform + NetworkId + Intangible + NonSerialized + DynamicLight + the 5 s
   DespawnComponent dead-man + AccLanternMark) with AccLanternMark.slot 1..8 (0 = the light above). AccLantern.ring places / moves / relights
   / removes them every tick next to helper(): each sits at angle 2 pi k / M, R blocks out, at the light-above height, only inside a loaded
   + ticking section (AccLantern.ringSectionOk: the target section, cached 20 ticks per slot; a slot in a missing / non-ticking section has
   no light), inside the world (y <= 318, the level lowered for the height it got) and inside the wearer's view radius - 4; moved when more
   than (its distance from the wearer) / 50 blocks (0.1 - 1.5) off its spot, at once when below it; the missing ones of a wearer are spawned
   together, at most one batch a second (maySpawnRing, its own limiter and WARN). EVERY EXIT PATH of 0.5.4 covers them: unequip / swap /
   profile switch / switch off / death -> the decision drops the whole ring at once (ringDrop); logout / world change -> AccLanternHelp
   (keepSlot: kept only while the owner's current entity is valid in THIS store and the slot still records this entity) removes them in
   their own world; a parked or duplicate copy is not the recorded one -> removed; plugin stopped -> the 5 s DespawnComponent; restart ->
   NonSerialized. AccLanternHide hides every marked entity of another wearer, so the ring lights are the wearer's own too.
 - Cost: Legendary 6 entities per wearer (0.5.4: 1), one move each per ~1.2 blocks walked (only to the wearer), 5 sin/cos + component reads
   a tick; the table solve (on a settings change only) is < 0.4 M light evaluations.
UNCHANGED: Normal / Unique / Rare, the glow, every item, recipe, text and asset (only the manifest version), the share / hide rules.
UNVERIFIED (in game only): the look (patchiness between ring lights, the flower-shaped outer edge), whether the client's light clusters
still show squares, how six helper entities move for a sprinting wearer.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.4.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.5.py")
tsrc = os.path.join(HERE, "test_skyyaccessories_0.5.4.py")
tdst = os.path.join(HERE, "test_skyyaccessories_0.5.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.4"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.4"\n' in s and "AccLanternHide" in s and "lanRingReach" not in s, "the source must be the generated 0.5.4 script"
REG0 = s.count("registerCommand(")
assert s.count("registerSystem(") == 4

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyAccessories 0.5.4 - build script (derived from the generated build_skyyaccessories_0.5.3.py by tools/acc_0_5_4_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.4.py            -> SkyyAccessories/SkyyAccessories-0.5.4.jar
       python build_skyyaccessories_0.5.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.4.py             (bare JVM -Xverify:all: every 0.5.3 check + the Night Vision retirement + the
                                                         Lantern on a real engine ECS world + compare with 0.5.3)
''', '''"""SkyyAccessories 0.5.5 - build script (derived from the generated build_skyyaccessories_0.5.4.py by tools/acc_0_5_5_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.5.py            -> SkyyAccessories/SkyyAccessories-0.5.5.jar
       python build_skyyaccessories_0.5.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.5.py             (bare JVM -Xverify:all: every 0.5.4 check in the 0.5.4 light layout + the
                                                         soft ring on the real ECS world and entity tracker + the height update + Y)
0.5.5: LANTERN SMOOTH EDGES (Skyy 2026-10-04: "2, try to smooth the edges"; full notes in tools/acc_0_5_5_patch.py):
     - every hidden light is at most lantern.edge bright (Advanced "Hidden lights: brightest", 96): a weaker light ends its lit area in a
       smaller step (0.00166 x level at the client's cut-off). A reach one such light cannot give gets a RING of lights of the same level
       and height around the light above (AccLanternMark.slot 1..8, AccLantern.ring; at most lantern.lights = Advanced "Hidden lights:
       most", 7, per wearer). Legendary: 95 at 52 up + 5 around at 27.5 blocks - fades smoothly to 0.16 at 48 blocks (0.5.4: a 0.35 step).
       Unique / Rare unchanged. Every 0.5.4 exit path (unequip, death, logout, world change, stop, restart) covers the ring.
     - lantern.height default 64 (0.5.4: 128); AccCfg.migrate055 turns a lantern.height line still at 128 into 64 ONCE (History copy,
       config-changes.log line with Undo, marker comment; other values kept).
''')
rep('VERSION = "0.5.4"\n', 'VERSION = "0.5.5"\n')

# ---------------------------------------------------------------------------------------------------------------- the settings (Python)
rep('''LAN_KEYS = (["lantern.glow.%s" % _r for _r in LAN_RARITIES] + ["lantern.reach.%s" % _r for _r in LAN_RARITIES] + ["lantern.height"])
LAN_FIELDS = ["LAN_GLOW1", "LAN_GLOW2", "LAN_GLOW3", "LAN_GLOW4", "LAN_REACH1", "LAN_REACH2", "LAN_REACH3", "LAN_REACH4", "LAN_HEIGHT"]
LAN_DEF = [11, 11, 11, 11, 6, 12, 24, 48, 128]
LAN_MIN = [0, 0, 0, 0, 0, 0, 0, 0, 8]
LAN_MAX = [15, 15, 15, 15, 64, 64, 64, 64, 160]
assert len(LAN_KEYS) == len(LAN_FIELDS) == len(LAN_DEF) == len(LAN_MIN) == len(LAN_MAX) == 9
''', '''# 0.5.5 (tools/acc_0_5_5_patch.py): + lantern.edge (the brightest a hidden light may be) and lantern.lights (the most hidden lights per
# wearer); lantern.height 128 -> 64 (Skyy 2026-10-04: "2, try to smooth the edges")
LAN_KEYS = (["lantern.glow.%s" % _r for _r in LAN_RARITIES] + ["lantern.reach.%s" % _r for _r in LAN_RARITIES] + ["lantern.height",
            "lantern.edge", "lantern.lights"])
LAN_FIELDS = ["LAN_GLOW1", "LAN_GLOW2", "LAN_GLOW3", "LAN_GLOW4", "LAN_REACH1", "LAN_REACH2", "LAN_REACH3", "LAN_REACH4", "LAN_HEIGHT",
              "LAN_EDGE", "LAN_LIGHTS"]
LAN_DEF = [11, 11, 11, 11, 6, 12, 24, 48, 64, 96, 7]
LAN_MIN = [0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 1]
LAN_MAX = [15, 15, 15, 15, 64, 64, 64, 64, 160, 255, 9]
assert len(LAN_KEYS) == len(LAN_FIELDS) == len(LAN_DEF) == len(LAN_MIN) == len(LAN_MAX) == 11
LAN_RING_MAX = 8                            # 0.5.5: at most 8 ring lights around the light above (lantern.lights max 9)
assert LAN_MAX[10] == LAN_RING_MAX + 1
# 0.5.5: the one-time lantern.height update (AccCfg.migrate055; the 0.5.1 migrate051 rules) - its marker is a doc comment (no '='), in
# the default text and in every updated file; looked for in comment lines only
M55_KEY, M55_OLD, M55_NEW = "lantern.height", "128", str(LAN_DEF[8])
M55_MARK_ID = "SkyyAccessories 0.5.5 Lantern defaults"
M55_MARK = ("# %s (Skyy 2026-10-04, smooth the edges): the hidden lights go at most 64 blocks up (0.5.4: 128) and are "
            "softer." % M55_MARK_ID)
M55_WHO = "SkyyAccessories 0.5.5"
assert M55_NEW == "64" and all(32 <= ord(_c) < 127 for _c in M55_MARK) and "=" not in M55_MARK and M55_MARK.startswith("# ")
''')
rep('''LAN_CONFIG_LINES = [
    "# Lantern Accessory (0.5.4): while it sits in a player's Accessory Bag, that player glows like a torch (everyone sees it), and from",
    "# Unique up a hidden light above them that only they see lights farther - around them it stays about as bright as their glow. Set",
    "# line.Lantern to false to switch it off for everyone. lantern.glow.<rarity> is the light level on the wearer, 0-15 (11 is a torch,",
    "# 15 the brightest vanilla light, 0 no glow). lantern.reach.<rarity> is how many blocks around the wearer are lit, 0-64 (a torch",
    "# lights about 6). lantern.height is the highest the hidden light may go above the wearer, 8-160 blocks (it sits as low as the reach",
    "# allows). lantern.shareReach true shows the hidden light to everyone near the wearer too (their bits near it can glow brightly).",
    "%s=true" % LAN_SWITCH]''', '''LAN_CONFIG_LINES = [
    "# Lantern Accessory (0.5.5): while it sits in a player's Accessory Bag, that player glows like a torch (everyone sees it), and from",
    "# Unique up hidden lights above them that only they see light farther - around them it stays about as bright as their glow. Set",
    "# line.Lantern to false to switch it off for everyone. lantern.glow.<rarity> is the light level on the wearer, 0-15 (11 is a torch,",
    "# 15 the brightest vanilla light, 0 no glow). lantern.reach.<rarity> is how many blocks around the wearer are lit, 0-64 (a torch",
    "# lights about 6). lantern.height is the highest a hidden light may go above the wearer, 8-160 blocks (they sit as low as the reach",
    "# allows). lantern.edge is the brightest a hidden light may be, 8-255: lower gives a softer far edge and needs more lights.",
    "# lantern.lights is the most hidden lights per wearer, 1-9 (just 1 is one big light, as in 0.5.4). lantern.shareReach true shows the",
    "# hidden lights to everyone near the wearer too (their bits near them can glow brightly).",
    M55_MARK,
    "%s=true" % LAN_SWITCH]''')
rep('''     "live,adv", "It sits as low as the reach allows, never higher than this (or the wearer's view distance).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[8], LAN_KEYS[8])),
''', '''     "live,adv", "They sit as low as the reach allows, never higher than this (or the wearer's view distance).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[8], LAN_KEYS[8])),
    (LAN_KEYS[9], "Hidden lights: brightest", "lantern", "int", str(LAN_DEF[9]), str(LAN_MIN[9]), str(LAN_MAX[9]), "step=1", "",
     "live,adv", "Lower = a softer far edge; long reaches then use more hidden lights. 255 = one big light (0.5.4).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[9], LAN_KEYS[9])),
    (LAN_KEYS[10], "Hidden lights: most", "lantern", "int", str(LAN_DEF[10]), str(LAN_MIN[10]), str(LAN_MAX[10]), "step=1", "",
     "live,adv", "Hidden lights per wearer, the one above them included. 1 = one light only (0.5.4).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[10], LAN_KEYS[10])),
''')
rep('assert len(LAN_ROWS) == 11 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false"',
    'assert len(LAN_ROWS) == 13 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false" and M55_MARK in LAN_CONFIG_LINES')

# ---------------------------------------------------------------------------------------------------------------- the light model (Python)
rep('''def lan_solve(glow, reach, hmax):
    """(height, level, reach reached) of the helper for one rarity: the LOWEST height whose cap-limited level reaches `reach`; the best
    reach under the cap and the height limit when nothing reaches it; (0, 0, the glow's own reach) when the glow alone is enough"""
    own = lan_reach(glow, 0.0)
    if reach <= own + 0.5:
        return 0, 0, own
    cap = lan_cap(glow)
    best = (0, 0, own)
    for h in range(LAN_MINH, hmax + 1):
        lv = lan_maxlevel(h - LAN_PZ, cap)
        if lv <= 0:
            continue
        r = lan_reach(lv, float(h))
        if r > best[2] + 1e-9:
            best = (h, lv, r)
        if r >= reach:
            return h, lv, r
    return best
''', '''# 0.5.5: cos(pi / M) for a ring of M lights (M 3..8) as literals, so the Java AccDefs.LAN_COS holds the very same doubles
import math as _math55
LAN_COS = [1.0, 1.0, 1.0] + [_math55.cos(_math55.pi / _m) for _m in range(3, LAN_RING_MAX + 1)]


def lan_ring_reach(level, h, m, rho):
    """0.5.5: how far the ground at the wearer's feet level is lit (>= LAN_VIS) with no dark gap, from the wearer outward in 0.25-block
    steps, by a light of this level h blocks above the wearer + m more at h, rho blocks out (angles 2 pi k / m): the worse of the walk
    toward a ring light (cos 1) and between two (cos pi / m) - the nearest light decides (same level: the nearest is the brightest).
    The Java AccDefs.lanRingReach (same arithmetic, same order)"""
    import math as _m
    hh = h * h
    worst = 400.0
    for c in (1.0, LAN_COS[m]):
        i = 0
        while i < 1600:
            x = i * 0.25
            d1 = _m.sqrt(x * x + hh)
            d2 = _m.sqrt(x * x + rho * rho - 2.0 * x * rho * c + hh)
            if lan_light(level, d1 if d1 < d2 else d2) < LAN_VIS:
                break
            i += 1
        r = 0.0 if i == 0 else (i - 1) * 0.25
        if r < worst:
            worst = r
    return worst


def lan_solve5(glow, reach, hmax, emax, nmax):
    """0.5.5: (height, level, reach reached, ring lights, ring radius in half blocks) for one rarity. First ONE light, as 0.5.4 but never
    brighter than emax: the LOWEST height whose cap-limited level reaches `reach`. Else the best of those (h0, l0) + a ring of m = 3 ..
    nmax - 1 lights (at most LAN_RING_MAX) of that level and height: the smallest m, then the smallest radius (half blocks up to 2 x
    reach) whose lan_ring_reach reaches `reach`; the best reach found when nothing does; (0, 0, the glow's own reach, 0, 0) when the glow
    alone is enough. The Java AccDefs.lanSolve"""
    own = lan_reach(glow, 0.0)
    if reach <= own + 0.5:
        return 0, 0, own, 0, 0
    cap = lan_cap(glow)
    best = (0, 0, own, 0, 0)
    for h in range(LAN_MINH, hmax + 1):
        lv = lan_maxlevel(h - LAN_PZ, cap)
        if lv > emax:
            lv = emax
        if lv <= 0:
            continue
        r = lan_reach(lv, float(h))
        if r > best[2] + 1e-9:
            best = (h, lv, r, 0, 0)
        if r >= reach:
            return h, lv, r, 0, 0
    h0, l0 = best[0], best[1]
    if h0 <= 0:
        return best
    for m in range(3, min(nmax - 1, LAN_RING_MAX) + 1):
        for p2 in range(1, 2 * reach + 1):
            r = lan_ring_reach(l0, float(h0), m, p2 * 0.5)
            if r > best[2] + 1e-9:
                best = (h0, l0, r, m, p2)
            if r >= reach:
                return h0, l0, r, m, p2
    return best


def lan_solve(glow, reach, hmax):
    """the 0.5.4 single-light solve (no level limit, one light): (height, level, reach reached)"""
    return lan_solve5(glow, reach, hmax, 255, 1)[:3]
''')
rep('''LAN_TABLE = [None] + [lan_solve(LAN_DEF[_t - 1], LAN_DEF[3 + _t], LAN_DEF[8]) for _t in range(1, 5)]
assert [(_h, _l) for _h, _l, _r in LAN_TABLE[1:]] == [(0, 0), (14, 31), (38, 72), (123, 208)], LAN_TABLE
assert [round(_r, 1) for _h, _l, _r in LAN_TABLE[1:]] == [5.9, 12.3, 24.7, 48.1], LAN_TABLE
''', '''LAN_TABLE5 = [None] + [lan_solve5(LAN_DEF[_t - 1], LAN_DEF[3 + _t], LAN_DEF[8], LAN_DEF[9], LAN_DEF[10]) for _t in range(1, 5)]
LAN_TABLE = [None] + [_x[:3] for _x in LAN_TABLE5[1:]]       # (height, level, reach) as in 0.5.4
LAN_RING = [None] + [_x[3:] for _x in LAN_TABLE5[1:]]        # 0.5.5: (ring lights, ring radius in half blocks)
assert [(_h, _l) for _h, _l, _r in LAN_TABLE[1:]] == [(0, 0), (14, 31), (38, 72), (52, 95)], LAN_TABLE
assert LAN_RING[1:] == [(0, 0), (0, 0), (0, 0), (5, 55)], LAN_RING
assert [round(_r, 1) for _h, _l, _r in LAN_TABLE[1:]] == [5.9, 12.3, 24.7, 48.0], LAN_TABLE
assert all(_l <= LAN_DEF[9] and _h <= LAN_DEF[8] for _h, _l, _r in LAN_TABLE[1:]) and all(1 + _m <= LAN_DEF[10] for _m, _p in LAN_RING[1:])
# 0.5.4's table is still what lantern.edge 255 + lantern.lights 1 + lantern.height 128 give
assert [lan_solve(LAN_DEF[_t - 1], LAN_DEF[3 + _t], 128)[:2] for _t in range(1, 5)] == [(0, 0), (14, 31), (38, 72), (123, 208)]
# the step at the edge (world brightness = 3 x the light at the cut-off 0.635 x level): 0.5.4's Legendary 0.34, now 0.16
assert 3.0 * lan_light(208, 0.635 * 208 - 1e-9) > 0.34 and 3.0 * lan_light(LAN_TABLE[4][1], 0.635 * LAN_TABLE[4][1] - 1e-9) < 0.17
''')
rep('''for _h, _l, _r in LAN_TABLE[2:]:
    for _d in (float(_h), (_h * _h + (_r * 0.98) ** 2) ** 0.5):''', '''for _h, _l, _r in LAN_TABLE[2:]:
    for _d in (float(_h), min((_h * _h + (_r * 0.98) ** 2) ** 0.5, 0.98 * 0.635 * _l)):   # 0.5.5: a ring row's reach is not one light's''')
rep('''    "%s glow %d%s -> %.1f" % (LAN_RARITIES[_t - 1], LAN_DEF[_t - 1], (" + light %d at %d up" % (LAN_TABLE[_t][1], LAN_TABLE[_t][0]))
                              if LAN_TABLE[_t][0] else "", LAN_TABLE[_t][2]) for _t in range(1, 5))))''',
    '''    "%s glow %d%s%s -> %.1f" % (LAN_RARITIES[_t - 1], LAN_DEF[_t - 1], (" + light %d at %d up" % (LAN_TABLE[_t][1], LAN_TABLE[_t][0]))
                                if LAN_TABLE[_t][0] else "", (" + %d around at %.1f blocks" % (LAN_RING[_t][0], LAN_RING[_t][1] * 0.5))
                                if LAN_RING[_t][0] else "", LAN_TABLE[_t][2]) for _t in range(1, 5))))''')

# ---------------------------------------------------------------------------------------------------------------- AccDefs (Java)
rep('''dfs.addField(CtField.make('public static volatile int LAN_EPOCH = 0;', dfs))                  # +1 per rebuild (players decide again)
''', '''dfs.addField(CtField.make('public static volatile int LAN_EPOCH = 0;', dfs))                  # +1 per rebuild (players decide again)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_M = new int[5];', dfs))      # 0.5.5: per rarity: ring lights (0 = one light)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_P = new int[5];', dfs))      # 0.5.5: per rarity: the ring radius, half blocks
dfs.addField(CtField.make('public static final int LAN_RING_MAX = %d;' % LAN_RING_MAX, dfs))
dfs.addField(CtField.make('public static final double[] LAN_COS = new double[] { %s };' % ", ".join(repr(_c) for _c in LAN_COS), dfs))
''')
rep('''JM(dfs, r"""
public static int lanGlow(int t) {''', '''# 0.5.5: the ring's lit reach (the Python lan_ring_reach: same arithmetic, same order, the same cos literals)
JM(dfs, r"""
public static double lanRingReach(int level, double h, int m, double rho) {
  double hh = h * h;
  double worst = 400.0;
  for (int k = 0; k < 2; k++) {
    double c = k == 0 ? 1.0 : LAN_COS[m];
    int i = 0;
    while (i < 1600) {
      double x = (double) i * 0.25;
      double d1 = Math.sqrt(x * x + hh);
      double d2 = Math.sqrt(x * x + rho * rho - 2.0 * x * rho * c + hh);
      if (lanLight(level, d1 < d2 ? d1 : d2) < LAN_VIS) break;
      i++;
    }
    double r = i == 0 ? 0.0 : (double) (i - 1) * 0.25;
    if (r < worst) worst = r;
  }
  return worst;
}""")
JM(dfs, r"""
public static int lanGlow(int t) {''')
rep('''# one rarity's helper: the LOWEST height (5 .. lantern.height) whose cap-limited level reaches the reach row; the best reach when none
# does; none when the glow alone reaches it. out = { height, level } and the reach reached in r[t]
JM(dfs, r"""
public static void lanSolve(int t, int[] hh, int[] ll, float[] rr) {
  int g = lanGlow(t);
  double own = lanReach(g, 0.0);
  int want = lanReachOf(t);
  hh[t] = 0;
  ll[t] = 0;
  rr[t] = (float) own;
  if ((double) want <= own + 0.5) return;
  double cap = lanCap(t);
  int hmax = LAN_HEIGHT;
  double best = own;
  for (int h = LAN_MINH; h <= hmax; h++) {
    int lv = lanMaxLevel((double) h - LAN_PZ, cap);
    if (lv <= 0) continue;
    double r = lanReach(lv, (double) h);
    if (r > best + 0.000000001) { best = r; hh[t] = h; ll[t] = lv; rr[t] = (float) r; }
    if (r >= (double) want) { hh[t] = h; ll[t] = lv; rr[t] = (float) r; return; }
  }
}""")
JM(dfs, r"""
public static synchronized void lanTable() {
  String sig = LAN_GLOW1 + "," + LAN_GLOW2 + "," + LAN_GLOW3 + "," + LAN_GLOW4 + "," + LAN_REACH1 + "," + LAN_REACH2 + "," + LAN_REACH3 + "," + LAN_REACH4 + "," + LAN_HEIGHT;
  if (sig.equals(LAN_SIG)) return;
  int[] hh = new int[5];
  int[] ll = new int[5];
  float[] rr = new float[5];
  for (int t = 1; t <= 4; t++) lanSolve(t, hh, ll, rr);
  LAN_TAB_H = hh;
  LAN_TAB_L = ll;
  LAN_TAB_R = rr;
  LAN_SIG = sig;
  LAN_EPOCH = LAN_EPOCH + 1;
}""")''', '''# one rarity's hidden lights (the Python lan_solve5): ONE light first - the LOWEST height (5 .. lantern.height) whose cap-limited level,
# never above lantern.edge, reaches the reach row; else the best of those + a ring of m (3 .. lantern.lights - 1, at most LAN_RING_MAX)
# lights of that level and height, the smallest m and then the smallest radius (half blocks) that reaches it; the best reach when nothing
# does; none when the glow alone reaches it. out = { height, level } in hh / ll, the reach in rr, the ring in mm / pp (0.5.5)
JM(dfs, r"""
public static void lanSolve(int t, int[] hh, int[] ll, float[] rr, int[] mm, int[] pp) {
  int g = lanGlow(t);
  double own = lanReach(g, 0.0);
  int want = lanReachOf(t);
  hh[t] = 0;
  ll[t] = 0;
  rr[t] = (float) own;
  mm[t] = 0;
  pp[t] = 0;
  if ((double) want <= own + 0.5) return;
  double cap = lanCap(t);
  int hmax = LAN_HEIGHT;
  int emax = LAN_EDGE;
  double best = own;
  for (int h = LAN_MINH; h <= hmax; h++) {
    int lv = lanMaxLevel((double) h - LAN_PZ, cap);
    if (lv > emax) lv = emax;
    if (lv <= 0) continue;
    double r = lanReach(lv, (double) h);
    if (r > best + 0.000000001) { best = r; hh[t] = h; ll[t] = lv; rr[t] = (float) r; }
    if (r >= (double) want) { hh[t] = h; ll[t] = lv; rr[t] = (float) r; return; }
  }
  int h0 = hh[t];
  int l0 = ll[t];
  if (h0 <= 0) return;
  int mmax = LAN_LIGHTS - 1;
  if (mmax > LAN_RING_MAX) mmax = LAN_RING_MAX;
  for (int m = 3; m <= mmax; m++) {
    for (int p2 = 1; p2 <= 2 * want; p2++) {
      double r = lanRingReach(l0, (double) h0, m, (double) p2 * 0.5);
      if (r > best + 0.000000001) { best = r; rr[t] = (float) r; mm[t] = m; pp[t] = p2; }
      if (r >= (double) want) { rr[t] = (float) r; mm[t] = m; pp[t] = p2; return; }
    }
  }
}""")
JM(dfs, r"""
public static synchronized void lanTable() {
  String sig = LAN_GLOW1 + "," + LAN_GLOW2 + "," + LAN_GLOW3 + "," + LAN_GLOW4 + "," + LAN_REACH1 + "," + LAN_REACH2 + "," + LAN_REACH3 + "," + LAN_REACH4 + "," + LAN_HEIGHT + "," + LAN_EDGE + "," + LAN_LIGHTS;
  if (sig.equals(LAN_SIG)) return;
  int[] hh = new int[5];
  int[] ll = new int[5];
  float[] rr = new float[5];
  int[] mm = new int[5];
  int[] pp = new int[5];
  for (int t = 1; t <= 4; t++) lanSolve(t, hh, ll, rr, mm, pp);
  LAN_TAB_M = mm;
  LAN_TAB_P = pp;
  LAN_TAB_H = hh;
  LAN_TAB_L = ll;
  LAN_TAB_R = rr;
  LAN_SIG = sig;
  LAN_EPOCH = LAN_EPOCH + 1;
}""")''')

# ---------------------------------------------------------------------------------------------------------------- AccLanternMark: the slot
rep('''JF(lmk, "public java.util.UUID owner;")
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark() { this.owner = null; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u) { this.owner = u; }", lmk))
JM(lmk, LANJ(r"""
public com.hypixel.hytale.component.Component clone() {
  return new @PKG@.AccLanternMark(this.owner);
}"""))''', '''JF(lmk, "public java.util.UUID owner;")
JF(lmk, "public int slot;")   # 0.5.5: 0 = the light above the wearer, 1..8 = a ring light (AccLantern.RING[slot - 1])
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark() { this.owner = null; this.slot = 0; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u) { this.owner = u; this.slot = 0; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u, int s) { this.owner = u; this.slot = s; }", lmk))
JM(lmk, LANJ(r"""
public com.hypixel.hytale.component.Component clone() {
  return new @PKG@.AccLanternMark(this.owner, this.slot);
}"""))''')

# ---------------------------------------------------------------------------------------------------------------- AccLantern: state
rep('''for _f in ("CLK", "WANT", "HELPER", "HSTATE", "OWNER", "HY", "SPAWNT"):
    JF(lan, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)''',
    '''# 0.5.5 THE RING: RING Object[RING_MAX] {the ring lights' Refs by slot - 1}; RSTATE int[RING_MAX x 3] {ticks since spawn, seen valid,
# light key} per slot; RSEC long[RING_MAX x 5] {cx, cy, cz, ok, ticks} the per-slot section check; RSPAWNT the ring's spawn limit (one
# batch a second). WANT gains [6] ring lights and [7] the ring radius in half blocks.
for _f in ("CLK", "WANT", "HELPER", "HSTATE", "OWNER", "HY", "SPAWNT", "RING", "RSTATE", "RSEC", "RSPAWNT"):
    JF(lan, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)''')
rep('''for _f in ("GLOW_ON", "GLOW_SET", "GLOW_OFF", "FOREIGN", "SPAWNS", "HREMOVES", "ORPHANS", "MOVES", "GONE", "LIMITED", "RELIT", "HIDDEN",
           "CLAMPED"):''', '''for _f in ("GLOW_ON", "GLOW_SET", "GLOW_OFF", "FOREIGN", "SPAWNS", "HREMOVES", "ORPHANS", "MOVES", "GONE", "LIMITED", "RELIT", "HIDDEN",
           "CLAMPED", "RCLAMPED", "RSKIPPED"):   # 0.5.5: RCLAMPED ring outside the view radius, RSKIPPED a slot in a bad section''')
rep('''JF(lan, "public static boolean LIMIT_WARNED = false;")''', '''JF(lan, "public static boolean LIMIT_WARNED = false;")
JF(lan, "public static boolean RLIMIT_WARNED = false;")
lan.addField(CtField.make("public static final int RING_MAX = %d;" % LAN_RING_MAX, lan))''')
# the helper entity with a slot (spawnS); spawn = slot 0 (the 0.5.4 call)
rep('''JM(lan, LANJ(r"""
public static @REF@ spawn(java.util.UUID u, @ST@ store, @CB@ cb, double x, double y, double z, int key) {''', '''JM(lan, LANJ(r"""
public static @REF@ spawnS(java.util.UUID u, int slot, @ST@ store, @CB@ cb, double x, double y, double z, int key) {''')
rep('''  h.addComponent(T_MARK, new @PKG@.AccLanternMark(u));
  SPAWNS.incrementAndGet();
  return cb.addEntity(h, @ARS@.SPAWN);
}"""))''', '''  h.addComponent(T_MARK, new @PKG@.AccLanternMark(u, slot));
  SPAWNS.incrementAndGet();
  return cb.addEntity(h, @ARS@.SPAWN);
}"""))
JM(lan, LANJ(r"""
public static @REF@ spawn(java.util.UUID u, @ST@ store, @CB@ cb, double x, double y, double z, int key) {
  return spawnS(u, 0, store, cb, x, y, z, key);
}"""))''')

# the ring (before step, its caller)
RING_JAVA = r'''# 0.5.5 THE RING. One ring light goes: removed only from its OWN store (a ring light left in another world is removed by that world's
# AccLanternHelp: the slot no longer records it); 128 when one was removed
JM(lan, LANJ(r"""
public static int dropOne(@REF@ r, @ST@ store, @CB@ cb) {
  if (r == null || r.getStore() != store || !r.isValid()) return 0;
  cb.tryRemoveEntity(r, @RRS@.REMOVE);
  HREMOVES.incrementAndGet();
  return 128;
}"""))
# the whole ring goes (not wanted, no room, death, swap to a rarity with one light, switch off) and its state is forgotten
JM(lan, LANJ(r"""
public static int ringDrop(java.util.UUID u, @ST@ store, @CB@ cb) {
  Object o = RING.remove(u);
  RSTATE.remove(u);
  RSEC.remove(u);
  int code = 0;
  if (o instanceof Object[]) {
    Object[] rs = (Object[]) o;
    for (int k = 0; k < rs.length; k++) if (rs[k] instanceof @REF@) code = code | dropOne((@REF@) rs[k], store, cb);
  }
  return code;
}"""))
JM(lan, r"""
public static int[] rstate(java.util.UUID u) {
  int[] h = (int[]) RSTATE.get(u);
  if (h == null) { h = new int[RING_MAX * 3]; RSTATE.put(u, h); }
  return h;
}""")
# one slot's section: loaded AND ticking (sectionOk), re-checked when the slot's section changes or every 20 ticks; a store that is not a
# world's (w null: the harness's own stores) is always fine
JM(lan, LANJ(r"""
public static boolean ringSectionOk(java.util.UUID u, int k, @WLD@ w, double x, double y, double z) {
  if (w == null) return true;
  long cx = (long) (((int) Math.floor(x)) >> 5);
  long cy = (long) (((int) Math.floor(y)) >> 5);
  long cz = (long) (((int) Math.floor(z)) >> 5);
  long[] c = (long[]) RSEC.get(u);
  if (c == null) {
    c = new long[RING_MAX * 5];
    for (int i = 0; i < RING_MAX; i++) c[i * 5 + 4] = 99L;
    RSEC.put(u, c);
  }
  int b = k * 5;
  if (c[b] == cx && c[b + 1] == cy && c[b + 2] == cz && c[b + 4] < 20L) {
    c[b + 4] = c[b + 4] + 1L;
    return c[b + 3] != 0L;
  }
  boolean ok = sectionOk(w, (int) cx, (int) cy, (int) cz);
  c[b] = cx;
  c[b + 1] = cy;
  c[b + 2] = cz;
  c[b + 3] = ok ? 1L : 0L;
  c[b + 4] = 0L;
  return ok;
}"""))
# the ring's spawn limit: the missing lights of a wearer are spawned TOGETHER, at most one batch a second; more than 20 batches in a minute
# (something keeps removing them) -> one WARN, then one batch per 10 s
JM(lan, r"""
public static boolean maySpawnRing(java.util.UUID u, long now) {
  long[] st = (long[]) RSPAWNT.get(u);
  if (st == null) { st = new long[] { 0L, 0L, now }; RSPAWNT.put(u, st); }
  if (now - st[2] > 60000L) { st[1] = 0L; st[2] = now; }
  long gap = st[1] >= 20L ? 10000L : 1000L;
  if (st[0] != 0L && now - st[0] < gap) { LIMITED.incrementAndGet(); return false; }
  st[0] = now;
  st[1] = st[1] + 1L;
  if (st[1] == 21L && !RLIMIT_WARNED) { RLIMIT_WARNED = true; @PKG@.AccStore.warn("Lantern: the ring lights had to be placed again more than 20 times in a minute for " + u + " - something keeps removing them; trying every 10 s now (logged once)"); }
  return true;
}""")
# THE RING (every tick next to helper()): w[6] = M lights at w[7] / 2 blocks around the wearer, at the light-above height w[2] with its
# level w[3] (lowered for the height it really got: the world top), angle 2 pi k / M. A slot outside the wearer's view radius - 4 (3-D) or
# in a section that is not loaded + ticking has no light. Placed (32), moved (64) when more than its distance / 50 blocks (0.1 - 1.5) off
# its spot or at all BELOW it, relit (256), the dead-man refreshed; removed (128) past M or when not wanted; 1024 = a spawn waits.
JM(lan, LANJ(r"""
public static int ring(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int[] w) {
  Object ro = RING.get(u);
  Object[] rs = null;
  if (ro instanceof Object[]) rs = (Object[]) ro;
  int m = 0;
  if (w != null && w.length > 7 && w[2] > 0 && w[3] > 0) m = w[6];
  if (m > RING_MAX) m = RING_MAX;
  if (m <= 0) return rs == null ? 0 : ringDrop(u, store, cb);
  @TCO@ tc = null;
  if (T_TC != null) tc = (@TCO@) store.getComponent(ref, T_TC);
  if (tc == null) return 0;
  @V3D@ p = tc.getPosition();
  double x = p.x();
  double feet = p.y();
  double z = p.z();
  double rho = (double) w[7] * 0.5;
  double top = feet + (double) w[2];
  if (top > TOP_Y) top = TOP_Y;
  boolean room = top >= BOTTOM_Y && top - feet >= (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS;
  if (room && T_EV != null) {
    @EVW@ ev = (@EVW@) store.getComponent(ref, T_EV);
    if (ev != null) {
      int vr = ev.viewRadiusBlocks - @PKG@.AccDefs.LAN_VIEW_MARGIN;
      if (Math.sqrt(rho * rho + (double) w[2] * (double) w[2]) > (double) vr) { room = false; RCLAMPED.incrementAndGet(); }
    }
  }
  int hgt = (int) Math.floor(top - feet + @PKG@.AccDefs.LAN_EPS);
  int lvl = w[3];
  if (hgt < w[2]) {
    int mx = @PKG@.AccDefs.lanMaxLevel((double) hgt - @PKG@.AccDefs.LAN_PZ, @PKG@.AccDefs.lanCap(w[0]));
    if (mx < lvl) lvl = mx;
  }
  if (!room || lvl <= 0) return rs == null ? 0 : ringDrop(u, store, cb);
  if (rs == null) { rs = new Object[RING_MAX]; RING.put(u, rs); }
  int[] st = rstate(u);
  int key = @PKG@.AccDefs.lanHKey(lvl);
  double th = Math.sqrt(rho * rho + (double) hgt * (double) hgt) / @PKG@.AccDefs.LAN_MOVE_DIV;
  if (th < @PKG@.AccDefs.LAN_MOVE_MIN) th = @PKG@.AccDefs.LAN_MOVE_MIN;
  if (th > @PKG@.AccDefs.LAN_MOVE_MAX) th = @PKG@.AccDefs.LAN_MOVE_MAX;
  @WLD@ wld = worldOf(store);
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  int asked = 0;
  int code = 0;
  for (int k = 0; k < RING_MAX; k++) {
    @REF@ hr = null;
    if (rs[k] instanceof @REF@) hr = (@REF@) rs[k];
    if (k >= m) {
      if (hr != null) { rs[k] = null; code = code | dropOne(hr, store, cb); }
      continue;
    }
    double a = 6.283185307179586 * (double) k / (double) m;
    double lx = x + rho * Math.cos(a);
    double lz = z + rho * Math.sin(a);
    if (!ringSectionOk(u, k, wld, lx, top, lz)) {
      RSKIPPED.incrementAndGet();
      if (hr != null) { rs[k] = null; code = code | dropOne(hr, store, cb); }
      continue;
    }
    if (hr != null && hr.getStore() != store) { rs[k] = null; hr = null; }
    int b = k * 3;
    if (hr != null && !hr.isValid()) {
      if (st[b + 1] != 0 || st[b] > 30) { rs[k] = null; hr = null; GONE.incrementAndGet(); }
      else { st[b] = st[b] + 1; continue; }
    }
    if (hr == null) {
      if (asked == 0) asked = maySpawnRing(u, System.currentTimeMillis()) ? 1 : 2;
      if (asked != 1) { code = code | 1024; continue; }
      rs[k] = spawnS(u, k + 1, store, cb, lx, top, lz, key);
      st[b] = 0;
      st[b + 1] = 0;
      st[b + 2] = key;
      code = code | 32;
      continue;
    }
    st[b + 1] = 1;
    st[b] = st[b] + 1;
    @TCO@ htc = (@TCO@) cb.getComponent(hr, T_TC);
    if (htc != null) {
      @V3D@ hp = htc.getPosition();
      double dx = hp.x() - lx;
      double dy = hp.y() - top;
      double dz = hp.z() - lz;
      if (dy < -0.02 || dx * dx + dy * dy + dz * dz > th * th) { htc.setPosition(new @V3D@(lx, top, lz)); MOVES.incrementAndGet(); code = code | 64; }
    }
    if (st[b + 2] != key) {
      @DLC@ hdl = (@DLC@) cb.getComponent(hr, T_DL);
      if (hdl != null) { hdl.setColorLight(@PKG@.AccDefs.lanColor(key)); st[b + 2] = key; RELIT.incrementAndGet(); code = code | 256; }
    }
    @DES@ dc = null;
    if (T_DES != null) dc = (@DES@) cb.getComponent(hr, T_DES);
    if (dc != null && tr != null) dc.setDespawnTo(tr.getNow(), DESPAWN_S);
  }
  return code;
}"""))
'''
rep('''# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt).''',
    RING_JAVA + '''# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt).''')
rep('''  if (w == null && !poke && !moved && c[0] < 1.0f && !HELPER.containsKey(u)) return 0;''',
    '''  if (w == null && !poke && !moved && c[0] < 1.0f && !HELPER.containsKey(u) && !RING.containsKey(u)) return 0;''')
rep('''      w = new int[] { t, g > 0 ? @PKG@.AccDefs.lanKey(g) : 0, @PKG@.AccDefs.LAN_TAB_H[t], @PKG@.AccDefs.LAN_TAB_L[t], dead ? 1 : 0, @PKG@.AccDefs.LAN_EPOCH };''',
    '''      w = new int[] { t, g > 0 ? @PKG@.AccDefs.lanKey(g) : 0, @PKG@.AccDefs.LAN_TAB_H[t], @PKG@.AccDefs.LAN_TAB_L[t], dead ? 1 : 0, @PKG@.AccDefs.LAN_EPOCH, @PKG@.AccDefs.LAN_TAB_M[t], @PKG@.AccDefs.LAN_TAB_P[t] };''')
rep('''  code = code | helper(u, ref, store, cb, w);
  return code;
}"""))''', '''  code = code | helper(u, ref, store, cb, w);
  code = code | ring(u, ref, store, cb, w);   // 0.5.5: the ring lights around the light above
  return code;
}"""))''')
rep('''  if (!r.isValid() || r.getStore() != store) return false;
  return HELPER.get(u) == helper;
}""")''', '''  if (!r.isValid() || r.getStore() != store) return false;
  return HELPER.get(u) == helper;
}""")
# 0.5.5: the same question for any slot (0 = the light above = keep; 1..8 = the ring light the slot records)
JM(lan, r"""
public static boolean keepSlot(java.util.UUID u, int slot, @REF@ helper, @ST@ store) {
  if (slot <= 0) return keep(u, helper, store);
  if (u == null || helper == null) return false;
  Object o = OWNER.get(u);
  if (!(o instanceof @REF@)) return false;
  @REF@ r = (@REF@) o;
  if (!r.isValid() || r.getStore() != store) return false;
  Object ro = RING.get(u);
  if (!(ro instanceof Object[])) return false;
  Object[] rs = (Object[]) ro;
  if (slot > rs.length) return false;
  return rs[slot - 1] == helper;
}""")''')
rep('''  SPAWNT.keySet().retainAll(online);
  @PKG@.AccStore.LPOKE.keySet().retainAll(online);''', '''  SPAWNT.keySet().retainAll(online);
  RING.keySet().retainAll(online);
  RSTATE.keySet().retainAll(online);
  RSEC.keySet().retainAll(online);
  RSPAWNT.keySet().retainAll(online);
  @PKG@.AccStore.LPOKE.keySet().retainAll(online);''')
rep('''  SPAWNT.clear();
  @PKG@.AccStore.LPOKE.clear();''', '''  SPAWNT.clear();
  RING.clear();
  RSTATE.clear();
  RSEC.clear();
  RSPAWNT.clear();
  @PKG@.AccStore.LPOKE.clear();''')
rep('''    if (@PKG@.AccLantern.keep(u, ref, store)) return;''', '''    int sl = 0;
    if (m != null) sl = m.slot;
    if (@PKG@.AccLantern.keepSlot(u, sl, ref, store)) return;   // 0.5.5: the ring lights too''')

# ---------------------------------------------------------------------------------------------------------------- the 0.5.5 update (AccCfg)
M55_JAVA = r'''
# ================= 0.5.5: the one-time lantern.height update (AccCfg.migrate055; the migrate051 pattern and its kit helpers) =================
cfg_.addField(CtField.make("public static final String M55_KEY = %s;" % jlit(M55_KEY), cfg_))
cfg_.addField(CtField.make("public static final String M55_OLD = %s;" % jlit(M55_OLD), cfg_))
cfg_.addField(CtField.make("public static final String M55_NEW = %s;" % jlit(M55_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M55_MARK = %s;" % jlit(M55_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M55_MARK_ID = %s;" % jlit(M55_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M55_WHO = %s;" % jlit(M55_WHO), cfg_))
for _src in [
# the value as the loader reads an int (trimmed, Integer.parseInt) equals this number
r"""
public static boolean m55Is(String v, String want) {
  if (v == null) return false;
  try { return Integer.parseInt(v.trim()) == Integer.parseInt(want); } catch (Throwable t) { return false; }
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile). null = the 0.5.5 marker is already in a
# comment line. Else { new text, "lantern.height 128 -> 64" or "", String[] kept notes, String[] { key, old, new } or empty }. The LAST
# live lantern.height entry (the one Properties keeps) decides: a one-line entry holding 128 -> every one-line entry holding 128 gets 64
# (value text only: key, separator and CR stay); anything else is kept (a custom value is noted unless it already is 64). The marker goes
# on its own line right above the first lantern.height entry, or at the end of a file without one (the file's own line ending).
r"""
public static Object[] m55Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int first = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M55_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (M55_KEY.equals(@PKG@.CfgFile.key(s))) {
      if (first < 0) first = k;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && m55Is(eff, M55_OLD);
  String chg = "";
  String[] rows = new String[0];
  java.util.ArrayList kept = new java.util.ArrayList();
  if (mig) {
    chg = M55_KEY + " " + oneLine(eff) + " -> " + M55_NEW;
    rows = new String[] { M55_KEY, eff, M55_NEW };
  } else if (eff != null && (multi || !m55Is(eff, M55_NEW))) {
    kept.add(M55_KEY + "=" + oneLine(eff) + " kept (custom) - the 0.5.5 default is " + M55_NEW);
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M55_MARK + nl : text + nl + M55_MARK;
    return new Object[] { out0, chg, (String[]) kept.toArray(new String[0]), rows };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M55_MARK + (crm ? "\r" : ""));
    }
    if (mig && e2 == k && M55_KEY.equals(@PKG@.CfgFile.key(s2)) && m55Is(@PKG@.CfgFile.value(l, k).trim(), M55_OLD)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M55_NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M55_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, (String[]) kept.toArray(new String[0]), rows };
}""",
# one config-changes.log line in the kit's format: time, name, uuid, via, key, old, new, status - a scalar row, so Server Setup -> Changes
# undoes it with a set back to the old value
r"""
public static String m55Log(String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M55_WHO + "\t-\tupdate\t" + M55_KEY + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), after migrate051 and BEFORE load(true) / CfgPub.start: the file before this update becomes a History version (verified by
# m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line when the value
# changed, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; " ("" = nothing done: no file, the marker is
# there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate055() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m55Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M55_WHO, "before the 0.5.5 Lantern defaults update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.5 Lantern defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    if (rows.length == 3) {
      @PKG@.CfgLog.enqueue(m55Log(rows[1], rows[2]));
      @PKG@.CfgLog.flush();
    }
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.5 Lantern default: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: no lantern.height line held the old 128 - nothing changed (0.5.5 Lantern marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.5 Lantern defaults (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))
'''
rep('''    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))

# ================= 0.5 part 2: AccGear''', '''    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))
''' + M55_JAVA + '''
# ================= 0.5 part 2: AccGear''')
rep('''  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  if (m51.length() > 0) cs = cs + "; " + m51;''', '''  String m55 = @PKG@.AccCfg.migrate055();   // 0.5.5: a lantern.height line still at 128 becomes 64 ONCE (History copy first), before the loader
  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  if (m51.length() > 0) cs = cs + "; " + m51;
  if (m55.length() > 0) cs = cs + "; " + m55;''')

# ---------------------------------------------------------------------------------------------------------------- final checks
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 4 and s.count("registerComponent(@PKG@.AccLanternMark.class") == 1, "systems / marker unchanged"
assert 'VERSION = "0.5.5"' in s and s.count("cb.addEntity(h, @ARS@.SPAWN)") == 1 and s.count("cb.addComponent(ref, T_DL,") == 1
assert s.count("new @PKG@.AccLanternMark(u, slot)") == 1 and "PersistentDynamicLight(" not in s
for _a, _b in (("public static double lanRingReach(", "public static void lanSolve("), ("public static void lanSolve(", "public static synchronized void lanTable("),
               ("public static " + "@REF@ spawnS(", "public static " + "@REF@ spawn(java.util.UUID u, @ST@ store"),
               ("public static int dropOne(", "public static int ringDrop("), ("public static int ringDrop(", "public static int ring(java"),
               ("public static boolean ringSectionOk(", "public static int ring(java"), ("public static boolean maySpawnRing(", "public static int ring(java"),
               ("public static int ring(java", "public static int step("), ("public static boolean keep(", "public static boolean keepSlot("),
               ("public static boolean keepSlot(", "lhs.addConstructor("), ("public static Object[] m55Update(", "public static synchronized String migrate055()"),
               ("public static synchronized String migrate055()", "public void setup() {"), ("String m51 = @PKG@.AccCfg.migrate051();", "String m55 = @PKG@.AccCfg.migrate055();"),
               ("String m55 = @PKG@.AccCfg.migrate055();", "String cs = @PKG@.AccCfg.load(true);"), ("M55_MARK = (", "LAN_CONFIG_LINES = [")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:40], _b[:40])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.5.4
print("wrote", dst, "(%d lines; 0.5.4 had %d)" % (s.count(LF), OLD.count(LF)))

# ================================================================================================================ THE HARNESS (0.5.5)
traw = open(tsrc, "rb").read()
TNL = "\r\n" if b"\r\n" in traw else "\n"
s = traw.decode("utf8").replace("\r\n", "\n")
TOLD = s
assert 'VERSION = "0.5.4"' in s and "def run_tracker(" in s and "run_m55" not in s, "the source must be the 0.5.4 harness"
rep('''"""Bare-JVM checks for SkyyAccessories 0.5.4, kept next to the build so every claim of the build report can be re-run by anyone.
''', '''"""Bare-JVM checks for SkyyAccessories 0.5.5, kept next to the build so every claim of the build report can be re-run by anyone.
0.5.5 (LANTERN SMOOTH EDGES, tools/acc_0_5_5_patch.py writes this file from test_skyyaccessories_0.5.4.py): every 0.5.4 check below is
carried forward and its Lantern sections run in the 0.5.4 light layout (lantern.height 128, lantern.edge 255, lantern.lights 1 - the
0.5.4 behaviour, proven equal); new:
  Q22 THE SOFT RING: the jar's ring reach / solver = the build's Python bit for bit (+ 24 random settings: every light under the brightness
      cap, never above the height row, never more lights than the row), the default table (Legendary 95 at 52 up + 5 around at 27.5), and
      on the REAL ECS world: six entities (slots 0-5, every part of the 0.5.4 helper, never saved) at their spots, following a walk
      within distance / 50, the swap to Rare (ring gone at once), death, lantern.lights 1, logout, world change both ways, the spawn
      batch limit, and a REAL World + ChunkStore (a ring slot in a non-ticking / missing section has no light until it ticks)
  Q21 + the ring on the REAL entity tracker: all six reach the wearer's client only, white 95, and leave it on unequip
  U   THE ONE-TIME lantern.height UPDATE (AccCfg.m55Update / migrate055): the 0.5.4 default file (128 -> 64 + marker, every other byte
      kept), CRLF, custom / 64 / spaced / continued / duplicated / commented lines, no lantern line (marker at the end), the 0.5.5 default
      text (never updated); on files with the real kit: History copy = the old bytes, the change-log line, the loader, the second start,
      Undo through the kit stays; a scratch copy of the LIVE folder; a fresh install
  L   the start sequence now includes migrate055: the first start may add the marker (config.properties + History only), then no churn
  Y   COMPARE with the 0.5.4 jar (the SET pin): only the Lantern / config / plugin classes change, every asset but the manifest identical
The 0.5.4 notes:
''')
rep('VERSION = "0.5.4"\n', 'VERSION = "0.5.5"\n')
rep('''JAR053 = os.path.join(HERE, "SkyyAccessories-0.5.3.jar")       # 0.5.4: the SET pin (live) - sections Y, R, Q19
''', '''JAR053 = os.path.join(HERE, "SkyyAccessories-0.5.3.jar")       # 0.5.4: sections R, Q19 (a 0.5.3 server's file)
JAR054 = os.path.join(HERE, "SkyyAccessories-0.5.4.jar")       # 0.5.5: the SET pin (live) - sections Y, U (its default file)
''')
rep('os.path.join(TOOLS, "dev", "scratch", "acc054", "test")', 'os.path.join(TOOLS, "dev", "scratch", "acc055", "test")')
rep("Default scratch folder: tools/dev/scratch/acc054/test", "Default scratch folder: tools/dev/scratch/acc055/test")
rep("    for p in (JAR053, SACKS_JAR):", "    for p in (JAR053, JAR054, SACKS_JAR):")
rep('''    if os.path.exists(JAR053):
        run_y054(jar)
    else:
        check(False, "Y no SkyyAccessories-0.5.3.jar next to the build")''', '''    if os.path.exists(JAR054):
        run_y055(jar)   # 0.5.5 (0.5.4's run_y054 compared 0.5.3 -> 0.5.4)
    else:
        check(False, "Y no SkyyAccessories-0.5.4.jar next to the build")''')
rep('''    run_lantern(P, jar, tns, BO, Defs, Store, Cfg, jpath, UUID, jarr)
''', '''    run_lantern(P, jar, tns, BO, Defs, Store, Cfg, jpath, UUID, jarr)
    # ---------------- 0.5.5: U the one-time lantern.height update
    run_m55(P, Defs, Cfg, jpath)
''')
# L: the first 0.5.5 start may write the marker once; then no churn
rep('''        before = snap(d)
        P_ = lambda n: JClass("com.skyy.accessories." + n)
        notes = []
        for rnd in (1, 2):
            P_("AccStore").DIR = Paths_.get(os.path.join(d, "bags"))
            P_("AccCfg").FILE = Paths_.get(os.path.join(d, "config.properties"))
            m51 = str(P_("AccCfg").migrate051())
''', '''        before0 = snap(d)
        before = None
        m55first = ""
        P_ = lambda n: JClass("com.skyy.accessories." + n)
        notes = []
        for rnd in (0, 1, 2):   # 0.5.5: round 0 = the first 0.5.5 start (the one-time lantern.height update writes once), then no churn
            if rnd == 1:
                before = snap(d)
            P_("AccStore").DIR = Paths_.get(os.path.join(d, "bags"))
            P_("AccCfg").FILE = Paths_.get(os.path.join(d, "config.properties"))
            m51 = str(P_("AccCfg").migrate051())
            m55 = str(P_("AccCfg").migrate055())
            if rnd == 0:
                m55first = m55
''')
rep('''        print("L. two starts on the live copy: %d files unchanged (%s)" % (len(before), notes[-1][:120]))
''', '''        print("L. two starts on the live copy: %d files unchanged (%s)" % (len(before), notes[-1][:120]))
        ch0 = sorted(k2 for k2 in set(before0) | set(before) if before0.get(k2) != before.get(k2))
        mk0 = str(P_("AccCfg").M55_MARK_ID).encode("latin-1") in before0.get("config.properties", b"")
        check(all(k2 == "config.properties" or k2.startswith("config-history" + os.sep) or k2 == "config-changes.log" for k2 in ch0) and
              (mk0 or (str(P_("AccCfg").M55_MARK_ID).encode("latin-1") in before["config.properties"] and m55first != "")) and
              any(v_ == before0["config.properties"] for k2, v_ in before.items() if k2.startswith("config-history" + os.sep)) == (not mk0),
              "L 0.5.5 the first start on the live copy: only config.properties (the marker / lantern.height), its History copy and the change "
              "log change: %s - %s" % (ch0[:4], m55first[:100]))
''')
# Q1: the carried checks in the 0.5.4 light layout
rep('''    set_lan(DEF)
    want0 = [(h, l, f32(r)) for h, l, r in L["LAN_TABLE"][1:]]''', '''    DEF054 = [11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1]   # 0.5.5: the carried 0.5.4 checks run in the 0.5.4 light layout
    check(len(DEF) == 11 and DEF[:8] == DEF054[:8] and DEF[8:] == [64, 96, 7], "Q1 0.5.5 defaults: height 64, edge 96, lights 7 %r" % DEF)
    set_lan(DEF054)
    want0 = [(h, l, f32(r)) for h, l, r in [lso(DEF054[t - 1], DEF054[3 + t], 128) for t in range(1, 5)]]''')
rep('''    set_lan(DEF)
    ep = int(Defs.LAN_EPOCH)''', '''    set_lan(DEF054)
    ep = int(Defs.LAN_EPOCH)''')
# Q20: spawn -> spawnS, dropOne
rep('''    check(users("DynamicLight.<init>") == ["AccLantern.glow", "AccLantern.spawn"] and users("CommandBuffer.addEntity") == ["AccLantern.spawn"] and''',
    '''    check(users("DynamicLight.<init>") == ["AccLantern.glow", "AccLantern.spawnS"] and users("CommandBuffer.addEntity") == ["AccLantern.spawnS"] and''')
rep('''          users("CommandBuffer.tryRemoveEntity") == ["AccLantern.drop", "AccLanternHelp.tick"],''',
    '''          users("CommandBuffer.tryRemoveEntity") == ["AccLantern.drop", "AccLantern.dropOne", "AccLanternHelp.tick"],''')
rep('''    sp_ = code.get("AccLantern.spawn", "")''', '''    sp_ = code.get("AccLantern.spawnS", "")   # 0.5.5: spawn = spawnS(slot 0)''')
# Q19: the default file's comment lines and the 13 rows
rep('''    i_lc = [i_ for i_, l_ in enumerate(dtx) if l_.startswith("# Lantern Accessory (0.5.4)")]''',
    '''    i_lc = [i_ for i_, l_ in enumerate(dtx) if l_.startswith("# Lantern Accessory (0.5.5)")]''')
rep('''not any(l_.startswith(("nightVision.", "line.NightVision")) for l_ in dtx) and len(lcom) == 6 and''',
    '''not any(l_.startswith(("nightVision.", "line.NightVision")) for l_ in dtx) and len(lcom) == 9 and lcom[-1] == str(Cfg.M55_MARK) and''')
rep('''"Q19 a fresh config.properties carries the 11 Lantern keys (+ lantern.shareReach=false) and no Night Vision key (6 comment lines, "''',
    '''"Q19 a fresh config.properties carries the 13 Lantern keys (+ lantern.shareReach=false) and no Night Vision key (9 comment lines, "''')
rep('''          [r_[0] for r_ in lr] == ["line.Lantern"] + KEYS + ["lantern.shareReach"] and [r_[3] for r_ in lr] == ["bool"] + ["int"] * 9 + ["bool"] and
          [r_[4] for r_ in lr] == ["true"] + [str(x) for x in DEF] + ["false"] and [r_[8] for r_ in lr] == [""] * 5 + ["blocks"] * 5 + [""] and
          [("adv" in r_[9]) for r_ in lr] == [False] * 9 + [True, True] and all("live" in r_[9] for r_ in lr) and
          [r_[1] for r_ in lr][1:3] == ["Normal: glow", "Unique: glow"] and lr[-2][1] == "Hidden light: highest" and''',
    '''          [r_[0] for r_ in lr] == ["line.Lantern"] + KEYS + ["lantern.shareReach"] and [r_[3] for r_ in lr] == ["bool"] + ["int"] * 11 + ["bool"] and
          [r_[4] for r_ in lr] == ["true"] + [str(x) for x in DEF] + ["false"] and [r_[8] for r_ in lr] == [""] * 5 + ["blocks"] * 5 + ["", "", ""] and
          [("adv" in r_[9]) for r_ in lr] == [False] * 9 + [True] * 4 and all("live" in r_[9] for r_ in lr) and
          [r_[1] for r_ in lr][1:3] == ["Normal: glow", "Unique: glow"] and lr[-4][1] == "Hidden light: highest" and
          lr[-3][1] == "Hidden lights: brightest" and lr[-2][1] == "Hidden lights: most" and''')
rep('''          "Q19 Server Setup -> Accessories -> Lantern: the switch, glow x4, reach x4 (blocks), the highest helper and the shared reach "''',
    '''          "Q19 Server Setup -> Accessories -> Lantern: the switch, glow x4, reach x4 (blocks), the highest helper, 0.5.5's brightest / most and the shared reach "''')
# Q21: the carried checks in the 0.5.4 layout, + the ring on the real tracker
rep('''    Lan = JClass(P + ".AccLantern")
    Mark, MarkSup = JClass(P + ".AccLanternMark"), JClass(P + ".AccLanternMarkSup")
    LANS_ = ''', '''    Lan = JClass(P + ".AccLantern")
    for f_, v_ in (("LAN_HEIGHT", 128), ("LAN_EDGE", 255), ("LAN_LIGHTS", 1)):   # 0.5.5: the carried checks in the 0.5.4 light layout
        setattr(Defs, f_, v_)
    Defs.lanTable()
    Mark, MarkSup = JClass(P + ".AccLanternMark"), JClass(P + ".AccLanternMarkSup")
    LANS_ = ''')
rep('''              not helpers(a1) and not bool(h.isValid()), "Q21 Ava unequips: both clients are told her light is gone, her client drops the helper")
''', '''              not helpers(a1) and not bool(h.isValid()), "Q21 Ava unequips: both clients are told her light is gone, her client drops the helper")
        # 0.5.5: THE RING on the real tracker - the default layout (height 64, edge 96, lights 7): Ava's Legendary = the light above + 5
        # around it; each reaches HER client only (AccLanternHide takes every marked entity of another wearer out), white 95
        for f_, v_ in (("LAN_HEIGHT", 64), ("LAN_EDGE", 96), ("LAN_LIGHTS", 7)):
            setattr(Defs, f_, v_)
        Defs.lanTable()
        Lan.SPAWNT.remove(a1)
        Lan.RSPAWNT.remove(a1)
        na4, nb4 = len(reca.p), len(recb.p)
        Store.equipK(a1, str(a1), LANS_[3])
        tick(3)
        hr_ = helpers(a1)
        sl_ = dict((int(w1.getComponent(r_, T_MARK).slot), r_) for r_ in hr_)
        K95 = int(Defs.lanHKey(95))
        nids_ = [nid(r_) for r_ in hr_]
        ax_, ay_, az_ = pos(ra)                           # where Ava stands now
        spot = lambda k_: (ax_, ay_ + 52.0, az_) if k_ == 0 else (ax_ + 27.5 * math.cos(2 * math.pi * (k_ - 1) / 5), ay_ + 52.0,
                                                                  az_ + 27.5 * math.sin(2 * math.pi * (k_ - 1) / 5))
        check(len(hr_) == 6 and sorted(sl_) == [0, 1, 2, 3, 4, 5] and all(gkey(r_) == K95 for r_ in hr_) and
              all(bool(va.visible.contains(r_)) and not bool(vb.visible.contains(r_)) for r_ in hr_) and
              all(lights(got(reca, n_, na4)[0]) == [K95] for n_ in nids_) and all(not got(recb, n_, nb4)[0] for n_ in nids_) and
              all(max(abs(a_ - b_) for a_, b_ in zip(pos(sl_[k_]), spot(k_))) < 1e-9 for k_ in sl_),
              "Q21 0.5.5 the ring on the real tracker: Ava's Legendary = 6 hidden lights (the one 52 up + 5 around at 27.5, slots 0-5), "
              "each in HER visible set only - her client got each one's white 95 light, Ben's client none of them %r" % ((
                  [(k_, pos(r_), gkey(r_), bool(va.visible.contains(r_)), bool(vb.visible.contains(r_))) for k_, r_ in sorted(sl_.items())],
                  [lights(got(reca, n_, na4)[0]) for n_ in nids_], [len(got(recb, n_, nb4)[0]) for n_ in nids_]),))
        na5 = len(reca.p)
        Store.unequipK(a1, str(a1), 0)
        tick(2)
        check(not helpers(a1) and all(got(reca, n_, na5)[2] >= 1 for n_ in nids_) and Lan.RING.get(a1) is None,
              "Q21 0.5.5 Ava unequips: all six leave her client at once, the ring state is gone")
        for f_, v_ in (("LAN_HEIGHT", 128), ("LAN_EDGE", 255), ("LAN_LIGHTS", 1)):   # back to the 0.5.4 layout for the rest of Q21
            setattr(Defs, f_, v_)
        Defs.lanTable()
''')
# Q22: the soft ring on the ECS world (before Q19, while the worlds of Q4-Q18 are still there)
Q22 = r'''
    # ---------------- Q22. 0.5.5 THE SOFT RING: model = the build's Python, the default table, the real ECS world
    lso5, lrr = L["lan_solve5"], L["lan_ring_reach"]
    bad, n_ = [], 0
    for lv in (24, 31, 72, 95, 208):
        for h in (14.0, 38.0, 52.0):
            for m in range(3, 9):
                for rho in (0.5, 10.0, 27.5, 41.0):
                    n_ += 1
                    if float(Defs.lanRingReach(lv, h, m, rho)) != lrr(lv, h, m, rho):
                        bad.append((lv, h, m, rho))
    check(not bad and [float(x) for x in Defs.LAN_COS] == L["LAN_COS"] and int(Defs.LAN_RING_MAX) == 8 == int(Lan.RING_MAX),
          "Q22 the jar's ring reach = the build's Python to the last bit on %d inputs; cos(pi / M) the same literals %r" % (n_, bad[:3]))
    set_lan(DEF)
    tab5 = lambda t: (tab(t), int(Defs.LAN_TAB_M[t]), int(Defs.LAN_TAB_P[t]))
    want5 = [((h, l, f32(r)), m, p) for h, l, r, m, p in L["LAN_TABLE5"][1:]]
    check([tab5(t) for t in range(1, 5)] == want5 and [x[0][:2] for x in want5] == [(0, 0), (14, 31), (38, 72), (52, 95)] and
          [x[1:] for x in want5] == [(0, 0), (0, 0), (0, 0), (5, 55)] and [int(Defs.lanShown(t)) for t in range(1, 5)] == [6, 12, 24, 48] and
          str(Defs.lanRow(4)) == "torch glow, lights about 48 blocks",
          "Q22 the default table = the build's: Unique 31 at 14, Rare 72 at 38 (one light each, as in 0.5.4), Legendary 95 at 52 up + 5 around "
          "at 27.5 blocks; shown 6 / 12 / 24 / 48: %r" % [tab5(t) for t in range(1, 5)])
    check(3.0 * ll(208, 0.635 * 208 - 1e-9) > 0.34 and 3.0 * ll(95, 0.635 * 95 - 1e-9) < 0.17 and
          all(ll(95, 52.0 - 3.0) <= ll(11, 0.3) for _q in (0,)),
          "Q22 the step at the edge of the lit ground (3 x the light at the cut-off): 0.5.4's Legendary 0.34, now 0.16; the cap holds")
    rnd5 = random.Random(55)
    badt = []
    for _ in range(24):
        vals = ([rnd5.randint(0, 15) for _q in range(4)] + [rnd5.randint(0, 64) for _q in range(4)] +
                [rnd5.randint(8, 160), rnd5.randint(24, 255), rnd5.randint(1, 9)])
        set_lan(vals)
        for t in range(1, 5):
            h, l, r, m, p = lso5(vals[t - 1], vals[3 + t], vals[8], vals[9], vals[10])
            if tab5(t) != ((h, l, f32(r)), m, p):
                badt.append((vals, t, tab5(t), (h, l, r, m, p)))
            if h > 0 and (ll(l, h - 3.0) > ll(vals[t - 1] if vals[t - 1] > 0 else 11, 0.3) or l > vals[9] or h > vals[8] or 1 + m > vals[10]):
                badt.append(("rule", vals, t))
    check(not badt, "Q22 24 random settings (+ edge, lights): the jar's table = the Python solver; every light under the brightness cap, "
          "never brighter than the edge row, never above the height row, never more lights than the lights row: %r" % badt[:2])
    set_lan([11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1])
    check([tab5(t) for t in range(1, 5)] == [((h, l, f32(r)), 0, 0) for h, l, r in [lso(11, x, 128) for x in (6, 12, 24, 48)]] and tab(4)[:2] == (123, 208),
          "Q22 edge 255 + lights 1 + height 128 = the 0.5.4 table exactly (one light, 208 at 123 for Legendary)")
    # the ECS world: Dee wears Legendary in the default layout in a third world
    set_lan(DEF)
    wc = reg.addStore(ES(None), ERS.get())
    ug = UUID.randomUUID()
    kg = str(ug)
    rg = player(wc, ug, "Dee", 100.5, 64.0, -40.5)
    slot = lambda w_, r_: int(w_.getComponent(r_, Lan.T_MARK).slot)
    K95 = int(Defs.lanHKey(95))

    def spot(k_, x_=100.5, y_=64.0, z_=-40.5):
        if k_ == 0:
            return (x_, y_ + 52.0, z_)
        a_ = 2 * math.pi * (k_ - 1) / 5
        return (x_ + 27.5 * math.cos(a_), y_ + 52.0, z_ + 27.5 * math.sin(a_))

    def ring_ok(w_, u_, x_, y_, z_, n_=6):
        hs_ = helpers(w_, u_)
        by_ = dict((slot(w_, r_), r_) for r_ in hs_)
        return (len(hs_) == n_ and sorted(by_) == list(range(n_)) and all(gkey(w_, r_) == K95 for r_ in hs_) and
                all(max(abs(a_ - b_) for a_, b_ in zip(pos(w_, by_[k_]), spot(k_, x_, y_, z_))) < 1e-9 for k_ in by_)), by_
    Store.equipK(ug, kg, LANS[3])
    sp5 = cnt("SPAWNS")
    tick(wc)
    ok_, by = ring_ok(wc, ug, 100.5, 64.0, -40.5)
    rs_ = Lan.RING.get(ug)
    check(ok_ and cnt("SPAWNS") == sp5 + 6 and Lan.HELPER.get(ug) == by.get(0) and rs_ is not None and
          all(rs_[k_ - 1] == by.get(k_) for k_ in range(1, 6)) and all(rs_[k_] is None for k_ in range(5, 8)),
          "Q22 Dee equips Legendary: ONE tick -> 6 hidden lights (one batch): slot 0 = 52 up (the recorded helper), slots 1-5 at 27.5 blocks "
          "around it at angles 2 pi k / 5, all white 95, recorded in RING")
    arcs = [wc.getArchetype(r_) for r_ in by.values()]
    check(all(all(bool(a_.contains(t_)) for t_ in (Lan.T_TC, Lan.T_DL, Lan.T_NID, Lan.T_INT, Lan.T_DES, Lan.T_MARK, NONSER)) and
              not bool(a_.contains(Lan.T_PR)) and not bool(a_.hasSerializableComponents(reg.getData())) for a_ in arcs) and
          all(wc.getComponent(r_, Lan.T_MARK).owner.equals(ug) for r_ in by.values()) and
          int(Mark(ug, 3).clone().slot) == 3 and Mark(ug, 3).clone().owner.equals(ug) and int(Mark(ug).slot) == 0 and int(MarkSup().get().slot) == 0,
          "Q22 every ring light is the 0.5.4 helper entity (Transform, DynamicLight, NetworkId, Intangible, Despawn, NonSerialized, our marker "
          "with the owner + its slot), never saved; AccLanternMark.clone keeps the slot")
    tr = wc.getResource(Lan.R_TIME)
    if tr is not None:
        check(all(str(wc.getComponent(r_, Lan.T_DES).getDespawn()) == str(tr.getNow().plusSeconds(5)) for r_ in by.values()),
              "Q22 each ring light carries the 5 s dead-man (refreshed every tick)")
    tick(wc, 40)
    ok2, by2 = ring_ok(wc, ug, 100.5, 64.0, -40.5)
    check(ok2 and by2 == by and cnt("SPAWNS") == sp5 + 6, "Q22 40 ticks standing still: the same six, nothing re-sent")
    # the walk: 300 ticks at 4.3 blocks a second; each ring light at most its distance / 50 (1.18 blocks) off its spot, never below it
    m0_, off_, low_ = cnt("MOVES"), 0.0, 0.0
    thr = math.sqrt(27.5 ** 2 + 52.0 ** 2) / 50.0
    for k_ in range(1, 301):
        x_ = 100.5 + k_ * (4.3 / 30.0)
        move(wc, rg, x_, 64.0, -40.5)
        tick(wc)
        for kk, r_ in by.items():
            if kk == 0:
                continue
            p_, s_ = pos(wc, r_), spot(kk, x_)
            off_ = max(off_, math.sqrt(sum((a_ - b_) ** 2 for a_, b_ in zip(p_, s_))))
            low_ = max(low_, s_[1] - p_[1])
    nmv = cnt("MOVES") - m0_
    check(off_ <= thr + 1e-9 and low_ <= 0.0 and nmv <= 6 * 40, "Q22 a 300-tick walk at 4.3 blocks a second: %d moves for the six lights, a ring "
          "light at most %.2f blocks off its spot (threshold %.2f), never below it" % (nmv, off_, thr))
    print("Q22. a 300-tick walk with the Legendary ring: %d moves for six lights, at most %.2f blocks off" % (nmv, off_))
    move(wc, rg, 100.5, 64.0, -40.5)
    tick(wc)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0], "Q22 back at the start: every light on its spot")
    # swap to Rare: the ring goes at once, the light above moves to 38 / 72; back to Legendary: the ring is placed again
    hr0 = cnt("HREMOVES")
    snl = [str(x) if x is not None else None for x in Store.snapshot(ug)]
    Store.unequipK(ug, kg, snl.index(LANS[3]))
    check(str(Store.equipK(ug, kg, LANS[2])) == "", "Q22 Dee takes the Legendary Lantern out and puts a Rare one in")
    tick(wc)
    hs_ = helpers(wc, ug)
    check(len(hs_) == 1 and hs_[0] == by[0] and pos(wc, hs_[0])[1] == 64.0 + 38 and gkey(wc, hs_[0]) == int(Defs.lanHKey(72)) and
          cnt("HREMOVES") == hr0 + 5 and Lan.RING.get(ug) is None and Lan.RSTATE.get(ug) is None,
          "Q22 one tick: the 5 ring lights removed (ringDrop), the light above becomes Rare's 72 at 38")
    check(str(Store.equipK(ug, kg, LANS[3])) == LANS[2], "Q22 the Legendary Lantern swaps the Rare one out")
    Lan.RSPAWNT.remove(ug)
    pre_ = bool(Lan.maySpawnRing(ug, JClass("java.lang.System").currentTimeMillis()))   # a batch just now
    tick(wc)
    lim_ = len(helpers(wc, ug))
    Lan.RSPAWNT.remove(ug)
    tick(wc)
    check(pre_ and lim_ == 1 and ring_ok(wc, ug, 100.5, 64.0, -40.5)[0],
          "Q22 back to Legendary within a second of the last batch: the ring waits (one batch a second), then all five come back together")
    uu5 = UUID.randomUUID()
    sq5 = [bool(Lan.maySpawnRing(uu5, t_)) for t_ in (1000, 1500, 2000, 2999, 3000)]
    for t_ in range(1, 25):
        Lan.maySpawnRing(uu5, 3000 + t_ * 1000)
    st5 = list(Lan.RSPAWNT.get(uu5))
    check(sq5 == [True, False, True, False, True] and not bool(Lan.maySpawnRing(uu5, int(st5[0]) + 5000)) and
          bool(Lan.maySpawnRing(uu5, int(st5[0]) + 10000)) and bool(Lan.RLIMIT_WARNED),
          "Q22 the ring's own limit: one batch a second; past 20 in a minute one WARN and one batch per 10 s")
    # death: everything at once; back after the respawn
    dc5 = US.allocateInstance(DTHC.class_)
    wc.addComponent(rg, Lan.T_DEATH, dc5)
    tick(wc)
    check(not helpers(wc, ug) and gkey(wc, rg) is None and Lan.RING.get(ug) is None, "Q22 Dee dies: all six lights and the glow gone the next tick")
    wc.removeComponent(rg, Lan.T_DEATH)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wc, 32)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0] and gkey(wc, rg) == K11, "Q22 respawned: the six are back within a second")
    # Server Setup: lantern.lights 1 -> one light (no ring); edge 255 too -> the 0.5.4-style single light (114 at 64: height 64)
    Defs.LAN_LIGHTS = 1
    Defs.lanTable()
    tick(wc)
    hs_ = helpers(wc, ug)
    check(len(hs_) == 1 and slot(wc, hs_[0]) == 0 and pos(wc, hs_[0])[1] == 64.0 + 52 and Lan.RING.get(ug) is None,
          "Q22 Hidden lights: most = 1 (live): the ring goes, the light above stays")
    Defs.LAN_EDGE = 255
    Defs.lanTable()
    tick(wc)
    h64, l64, r64 = lso(11, 48, 64)
    check(len(helpers(wc, ug)) == 1 and pos(wc, helpers(wc, ug)[0])[1] == 64.0 + h64 and gkey(wc, helpers(wc, ug)[0]) == int(Defs.lanHKey(l64)) and
          (h64, l64) == (64, 114), "Q22 + brightest = 255: Skyy's tested option 2 - one light %d at %d up (reach %.1f)" % (l64, h64, r64))
    set_lan(DEF)
    Lan.RSPAWNT.remove(ug)
    tick(wc)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0], "Q22 back to the defaults: the ring again")
    # logout: AccLanternHelp removes all six in their own world; prune forgets the ring state
    o5 = cnt("ORPHANS")
    wc.removeEntity(rg, RR.UNLOAD)
    tick(wc)
    online5 = HashSet()
    for u_ in (ua, ub, uc):
        online5.add(u_)
    Lan.prune(online5)
    check(not helpers(wc, ug) and cnt("ORPHANS") == o5 + 6 and all(getattr(Lan, m_).get(ug) is None for m_ in ("RING", "RSTATE", "RSEC", "RSPAWNT", "HELPER")),
          "Q22 Dee logs out: AccLanternHelp (keepSlot) removes all six the next tick; prune forgets RING / RSTATE / RSEC / RSPAWNT")
    # world change both ways: each world removes only its own lights
    rg = player(wc, ug, "Dee", 100.5, 64.0, -40.5)
    tick(wc)
    old6 = helpers(wc, ug)
    wc.removeEntity(rg, RR.UNLOAD)
    rg2 = player(wa, ug, "Dee", 200.5, 70.0, 200.5)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wa)
    check(len(old6) == 6 and ring_ok(wa, ug, 200.5, 70.0, 200.5)[0] and len(helpers(wc, ug)) == 6 and all(bool(r_.isValid()) for r_ in old6),
          "Q22 Dee moves to world A (A ticks first): six new lights in A, the old six in the old world untouched by A's systems")
    tick(wc)
    check(not helpers(wc, ug) and ring_ok(wa, ug, 200.5, 70.0, 200.5)[0], "Q22 the old world's own AccLanternHelp removes its six")
    wa.removeEntity(rg2, RR.UNLOAD)
    tick(wa)
    check(not helpers(wa, ug), "Q22 Dee leaves world A: all six go with her")
    # a REAL World + ChunkStore (Q16c's): a ring slot only goes into a loaded + ticking section, re-checked every 20 ticks
    wsw2 = reg.addStore(ES(world), ERS.get())
    rk0 = cnt("RSKIPPED")
    rg3 = player(wsw2, ug, "Dee", 10.5, 64.3, 10.5)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wsw2)
    h3 = helpers(wsw2, ug)
    check(len(h3) == 1 and slot(wsw2, h3[0]) == 0 and pos(wsw2, h3[0]) == (10.5, 64.3 + 52.0, 10.5) and cnt("RSKIPPED") >= rk0 + 5,
          "Q22 Dee in the real-ChunkStore world: the light above fits in section 3 of her column (y 116.3); every ring slot lands in a "
          "NonTicking (column 1) or missing section -> no light there")
    section(1, 3, 0, True)                                # column 1's section 3 starts ticking
    tick(wsw2, 23)
    h3 = helpers(wsw2, ug)
    by3 = dict((slot(wsw2, r_), r_) for r_ in h3)
    check(sorted(by3) == [0, 1] and max(abs(a_ - b_) for a_, b_ in zip(pos(wsw2, by3[1]), (38.0, 64.3 + 52.0, 10.5))) < 1e-9,
          "Q22 that section ticks: within the 20-tick re-check slot 1 (toward +x, x 38) gets its light, the others still wait")
    section(1, 3, 0, False)
    wsw2.removeEntity(rg3, RR.UNLOAD)
    tick(wsw2)
    check(not helpers(wsw2, ug), "Q22 Dee leaves: her lights go with her")
    Store.unequipK(ug, kg, 0)
    Lan.prune(online5)
    set_lan([11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1])   # the carried Q19 continues where 0.5.4's did
    print("Q22. the soft ring: model = Python, defaults, 24 random settings, six lights on the real ECS world (walk, swap, death, settings, "
          "logout, world change, real ChunkStore sections)")
'''
rep('''    # ---------------- Q19. config: the default file, the loader (an existing file untouched), the Server Setup rows through the real kit
''', Q22 + '''
    # ---------------- Q19. config: the default file, the loader (an existing file untouched), the Server Setup rows through the real kit
''')
# U + Y055: new module-level sections
NEW_FUNCS = r'''
def run_m55(P, Defs, Cfg, jpath):
    """0.5.5: U - THE ONE-TIME lantern.height UPDATE (AccCfg.m55Update / migrate055, setup()'s order: migrate051, migrate055, load(true))."""
    import skyybuild as B
    from jpype import JClass, JArray, JString
    MARK, MARK_ID = str(Cfg.M55_MARK), str(Cfg.M55_MARK_ID)
    check(str(Cfg.M55_KEY) == "lantern.height" and str(Cfg.M55_OLD) == "128" and str(Cfg.M55_NEW) == "64" and
          str(Cfg.M55_WHO) == "SkyyAccessories 0.5.5" and MARK.startswith("# " + MARK_ID) and "=" not in MARK and
          MARK in str(Cfg.DEFAULT_TEXT).split("\n") and "lantern.height=64" in str(Cfg.DEFAULT_TEXT).split("\n"),
          "U the update's data; the 0.5.5 default text carries lantern.height=64 and the marker")

    def upd(t):
        r = Cfg.m55Update(JString(t))
        if r is None:
            return None
        return str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]
    u54 = JArray(JClass("java.net.URL"))(2)
    u54[0] = JClass("java.io.File")(JAR054).toURI().toURL()
    u54[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    t054 = str(JClass(P + ".AccCfg", loader=JClass("java.net.URLClassLoader")(u54, JClass("java.lang.ClassLoader").getPlatformClassLoader())).DEFAULT_TEXT)
    u53 = JArray(JClass("java.net.URL"))(2)
    u53[0] = JClass("java.io.File")(JAR053).toURI().toURL()
    u53[1] = u54[1]
    t053 = str(JClass(P + ".AccCfg", loader=JClass("java.net.URLClassLoader")(u53, JClass("java.lang.ClassLoader").getPlatformClassLoader())).DEFAULT_TEXT)
    lines = t054.split("\n")
    check("lantern.height=128" in lines and lines.count("lantern.height=128") == 1 and MARK_ID not in t054,
          "U the 0.5.4 default file (what a fresh 0.5.4 install wrote) holds lantern.height=128 and no marker")
    i_ = lines.index("lantern.height=128")
    exp = list(lines)
    exp[i_] = "lantern.height=64"
    exp.insert(i_, MARK)
    exp = "\n".join(exp)
    r = upd(t054)
    check(r is not None and r[0] == exp and r[1] == "lantern.height 128 -> 64" and r[2] == [] and r[3] == ["lantern.height", "128", "64"],
          "U1 the 0.5.4 default file: lantern.height 128 -> 64, the marker right above it, every other line byte for byte")
    check(upd(r[0]) is None and upd(str(Cfg.DEFAULT_TEXT)) is None, "U1 a file with the marker (an updated one, a fresh 0.5.5 one) is never updated")
    rc = upd(t054.replace("\n", "\r\n"))
    check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "U2 a CRLF file stays CRLF (the marker line too)")
    t_c = t054.replace("lantern.height=128", "lantern.height = 100")
    r_c = upd(t_c)
    check(r_c[0] == t_c.replace("lantern.height = 100", MARK + "\nlantern.height = 100") and r_c[1] == "" and r_c[3] == [] and
          r_c[2] == ["lantern.height=100 kept (custom) - the 0.5.5 default is 64"], "U3 a custom value is kept and noted (the marker added)")
    t_6 = t054.replace("lantern.height=128", "lantern.height=64")
    r_6 = upd(t_6)
    check(r_6[0] == t_6.replace("lantern.height=64", MARK + "\nlantern.height=64") and r_6[1] == "" and r_6[2] == [] and r_6[3] == [],
          "U3 already 64: only the marker, no note")
    t_s = t054.replace("lantern.height=128", "  lantern.height :  128  ")
    r_s = upd(t_s)
    check(r_s[0] == t_s.replace("  lantern.height :  128  ", MARK + "\n  lantern.height :  64") and r_s[1] == "lantern.height 128 -> 64",
          "U3 spaced: the key, the separator and the spaces before the value stay")
    t_m = t054.replace("lantern.height=128", "lantern.height=12\\\n8")
    r_m = upd(t_m)
    check(r_m[0] == t_m.replace("lantern.height=12\\\n8", MARK + "\nlantern.height=12\\\n8") and r_m[3] == [] and len(r_m[2]) == 1,
          "U3 a continued entry is kept (noted)")
    r_d = upd(t054 + "lantern.height=128\n")
    check(r_d[0] == exp + "lantern.height=64\n" and r_d[3] == ["lantern.height", "128", "64"], "U3 a duplicated 128 line: both become 64")
    r_d2 = upd(t054 + "lantern.height=90\n")
    check(r_d2[0] == t054.replace("lantern.height=128", MARK + "\nlantern.height=128") + "lantern.height=90\n" and r_d2[3] == [] and
          r_d2[2] == ["lantern.height=90 kept (custom) - the 0.5.5 default is 64"], "U3 the LAST entry decides (Properties keeps it): 90 -> nothing changes")
    r_t = upd(t054.replace("lantern.height=128", "#lantern.height=128\nlantern.height=128"))
    check(r_t[0] == exp.replace(MARK + "\nlantern.height=64", "#lantern.height=128\n" + MARK + "\nlantern.height=64"),
          "U3 a commented '#lantern.height=128' line is left alone")
    r_n = upd(t053)
    check(r_n[0] == t053 + MARK + "\n" and r_n[1] == "" and r_n[2] == [] and r_n[3] == [] and t053.endswith("\n"),
          "U4 a file with no lantern line (0.5.3's): only the marker, at the end - a later in-game 128 is never turned back")
    check(upd("slots=18")[0] == "slots=18\n" + MARK and upd("slots=18\r\n")[0] == "slots=18\r\n" + MARK + "\r\n" and upd("")[0] == MARK + "\n",
          "U4 no trailing newline / CRLF / empty: the file's own line ending")
    Pub, Fn = JClass(P + ".CfgPub"), JClass(P + ".CfgFn")

    def jobj(*xs):
        a = JArray(JClass("java.lang.Object"))(len(xs))
        for i, v in enumerate(xs):
            a[i] = JString(v) if isinstance(v, str) else v
        return a

    def histfiles(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(f_ for f_ in os.listdir(hd) if f_ != "index.log") if os.path.isdir(hd) else []
    mods = os.path.join(SCRATCH, "m55-kit")
    d = os.path.join(mods, "Skyy_SkyyAccessories")
    os.makedirs(d)
    f = os.path.join(d, "config.properties")
    open(f, "wb").write(t054.encode("latin-1"))
    Cfg.FILE = jpath(f)
    res = str(Cfg.migrate055())
    new = open(f, "rb").read()
    hf = histfiles(d)
    log = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().split("\n") if os.path.exists(os.path.join(d, "config-changes.log")) else []
    lg = [l_ for l_ in log if l_]
    check(new == exp.encode("latin-1") and "lantern.height 128 -> 64" in res and len(hf) == 1 and
          open(os.path.join(d, "config-history", hf[0]), "rb").read() == t054.encode("latin-1") if hf else False,
          "U5 migrate055 on a 0.5.4 file: written as m55Update says, the History copy = the old file byte for byte: " + res[:120])
    check(len(lg) == 1 and lg[0].split("\t")[1:] == ["SkyyAccessories 0.5.5", "-", "update", "lantern.height", "128", "64", "ok"],
          "U5 one config-changes.log line in the kit's format (status ok: Server Setup -> Changes offers Undo): %r" % lg)
    cs = str(Cfg.load(True))
    check(int(Defs.LAN_HEIGHT) == 64 and open(f, "rb").read() == new, "U5 the loader then runs at height 64 and leaves the file alone")
    check(str(Cfg.migrate055()) == "" and open(f, "rb").read() == new and len(histfiles(d)) == 1, "U5 the next start changes nothing")
    Pub.start(jpath(mods), None)
    rU = [str(x) for x in Fn().apply(jobj("set", "lantern.height", "128", None, "console", "yes", "console"))]
    Pub.flush()
    Pub.shutdown()
    after = open(f, "rb").read().decode("latin-1")
    check(rU[0] == "ok" and parse_props(after).get("lantern.height") == "128" and int(Defs.LAN_HEIGHT) == 128 and str(Cfg.migrate055()) == "" and
          open(f, "rb").read().decode("latin-1") == after, "U5 Undo through the real kit (set back to 128): it stays 128 at the next start (the marker)")
    # the live data (a scratch copy) and a fresh install
    lf = os.path.join(LIVE, "config.properties")
    if os.path.exists(lf):
        dl = os.path.join(SCRATCH, "m55-live", "Skyy_SkyyAccessories")
        shutil.copytree(LIVE, dl)
        fl = os.path.join(dl, "config.properties")
        old = open(fl, "rb").read()
        logn = len(open(os.path.join(dl, "config-changes.log"), "rb").read().split(b"\n")) if os.path.exists(os.path.join(dl, "config-changes.log")) else 0
        h0 = histfiles(dl)
        Cfg.FILE = jpath(fl)
        resl = str(Cfg.migrate055())
        newl = open(fl, "rb").read()
        exl = upd(old.decode("latin-1"))
        h1 = histfiles(dl)
        logn2 = len(open(os.path.join(dl, "config-changes.log"), "rb").read().split(b"\n")) if os.path.exists(os.path.join(dl, "config-changes.log")) else 0
        check((exl is None and newl == old and resl == "") or (exl is not None and newl == exl[0].encode("latin-1") and len(h1) == len(h0) + 1 and
              any(open(os.path.join(dl, "config-history", x), "rb").read() == old for x in h1) and logn2 == logn + (1 if exl[3] else 0)),
              "U6 Skyy's live file (a scratch copy): %s" % (resl[:140] or "already updated"))
        check(str(Cfg.migrate055()) == "" and open(fl, "rb").read() == newl, "U6 the live copy's next start changes nothing")
        print("U6. the live copy: %s" % (resl or "nothing to do"))
    else:
        print("note: no live config.properties - U6 skipped")
    df = os.path.join(SCRATCH, "m55-fresh")
    os.makedirs(df)
    ff = os.path.join(df, "config.properties")
    Cfg.FILE = jpath(ff)
    r0 = str(Cfg.migrate055())
    Cfg.load(True)
    ft = open(ff, "rb").read()
    check(r0 == "" and MARK.encode("latin-1") in ft and b"lantern.height=64" in ft and str(Cfg.migrate055()) == "" and open(ff, "rb").read() == ft and
          not histfiles(df), "U7 a fresh install: no file -> nothing; the default file carries height 64 + the marker -> never updated")
    print("U. the lantern.height update: 0.5.4 file 128 -> 64, CRLF, custom / spaced / continued / duplicated / commented, no line, the kit "
          "(History, log, loader, Undo), the live copy, a fresh install")


def run_y055(jar):
    """0.5.5: Y - compare with the 0.5.4 jar (the SET pin): classes and assets."""
    import zipfile
    za, zb = zipfile.ZipFile(JAR054), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    ca = dict((n, za.read(n)) for n in na if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in nb if n.endswith(".class"))
    same = sorted(n for n in ca if n in cb and ca[n] == cb[n])
    changed = sorted(n for n in ca if n in cb and ca[n] != cb[n])
    new_ = sorted(n for n in cb if n not in ca)
    gone = sorted(n for n in ca if n not in cb)
    short = lambda xs: ", ".join(x.split("/")[-1][:-6] for x in xs)
    check(not new_ and not gone, "Y no class new or gone: %s / %s" % (short(new_), short(gone)))
    check(set(short(changed).split(", ")) <= {"AccCfg", "AccDefs", "AccLantern", "AccLanternMark", "AccLanternHelp", "SkyyAccessoriesPlugin",
                                             "CfgFile", "CfgFn", "CfgRows", "CfgPub"} and
          {"AccCfg", "AccDefs", "AccLantern", "AccLanternMark", "AccLanternHelp", "SkyyAccessoriesPlugin"} <= set(short(changed).split(", ")),
          "Y changed classes: the Lantern ones, the config and the plugin (+ the kit's version texts): " + short(changed))
    check(all(("com/skyy/accessories/%s.class" % c) in same for c in ("AccEffects", "AccGear", "MoveSync", "AccPage", "AccNotice", "AccStore",
                                                                   "AccTick", "AccLanternSys", "AccLanternHide", "AccLanternMarkSup", "WbTab",
                                                                   "WbRank", "AccFn", "AccGiveFn", "AccRestampTask", "CfgHist", "CfgLog")),
          "Y byte-identical: AccEffects, AccGear, MoveSync, the page, the notice, AccStore, AccTick, AccLanternSys, AccLanternHide, the "
          "Workbench tab, the give / restamp paths, the kit's History and log")
    assets_a = dict((n, za.read(n)) for n in na if not n.endswith(".class"))
    assets_b = dict((n, zb.read(n)) for n in nb if not n.endswith(".class"))
    diff = sorted(n for n in set(assets_a) | set(assets_b) if assets_a.get(n) != assets_b.get(n))
    ma, mb = json.loads(assets_a["manifest.json"]), json.loads(assets_b["manifest.json"])
    check(diff == ["manifest.json"] and sorted(k2 for k2 in set(ma) | set(mb) if ma.get(k2) != mb.get(k2)) == ["Name", "Version"] and
          mb["Version"] == "0.5.5", "Y every asset identical (items, recipes, server.lang, icons) but the manifest's Name / Version: %r" % diff)
    print("Y. compare with 0.5.4: classes identical %d, changed %d (%s); assets: only the manifest version" % (len(same), len(changed), short(changed)))


'''
rep('''
OLD_045_DEFAULT = """''', NEW_FUNCS + '''
OLD_045_DEFAULT = """''')
# --oldjars: the old jars tools/tidy_local.py packed away (sections R / X / S / B1)
rep('''KEEP = "--keep" in sys.argv
''', '''KEEP = "--keep" in sys.argv
# 0.5.5: tools/tidy_local.py packs old jars into backups/archive/old-jars-*.tar.xz; extract that archive into a scratch folder and pass
# --oldjars <folder> to give sections R / X / S / B1 their old jars (SkyyAccessories 0.4.5 + 0.5, SkyyGear 0.1) again
OLDJARS = arg("--oldjars")
if OLDJARS:
    OLDJARS = os.path.abspath(OLDJARS)
    JAR045 = os.path.join(OLDJARS, "SkyyAccessories", "SkyyAccessories-0.4.5.jar")
    JAR05 = os.path.join(OLDJARS, "SkyyAccessories", "SkyyAccessories-0.5.jar")
    GEAR_JARS[0] = os.path.join(OLDJARS, "SkyyGear", "SkyyGear-0.1.jar")
''')
rep('''    if "--synthetic" in sys.argv:
        args.append("--synthetic")''', '''    if "--synthetic" in sys.argv:
        args.append("--synthetic")
    if OLDJARS:
        args += ["--oldjars", OLDJARS]''')
compile(s, tdst, "exec")
open(tdst, "w", encoding="utf8", newline=TNL).write(s)
print("wrote", tdst, "(%d lines; 0.5.4 had %d)" % (s.count(LF), TOLD.count(LF)))
