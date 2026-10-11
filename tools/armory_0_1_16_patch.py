"""Derive SkyyArmory/build_skyyarmory_0.1.16.py (+ its harness SkyyArmory/test_skyyarmory_0.1.16.py) from the GENERATED 0.1.15
(SkyyArmory/build_skyyarmory_0.1.15.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_15_patch.py; test_skyyarmory_0.1.15.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_16_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.16.py   then
      python SkyyArmory/test_skyyarmory_0.1.16.py --dir tools/dev/scratch/<task>/harness      (never --deploy)

0.1.16 = THE WAND HOP FIX (Skyy 2026-10-10: "the wand charge shot launches me twice for some reason, and it launches a little too far
especially if i look down and jump"; docs/answered/classes.md LOCKED 2026-10-04 wand line + hop.force 13 -> 30; NO void protection - Skyy:
"dont put any void protection on any traversal").
  ONE HOP PER CAST ("launches me twice"). In 0.1.15 a wand charged cast is: the orb's SPAWN -> Leap.onWandOrb -> the hop (one Velocity Set with
    the dagger dash config) -> rise -> hang -> Leap.fire re-launches the SAME orb, and ArmoryTrav.added tells that second SPAWN apart ONLY by its
    entity Ref in TravWorld.pend. Two ways in that code give the caster a second full hop for one cast (both REPRODUCED in the harness on the
    0.1.15 logic as MUTANTS, R19b): (1) the re-launched orb's SPAWN is not matched by its Ref (the record dropped, the world record rebuilt,
    another Ref) -> it is taken for a NEW cast -> a second leap + a second Stamina charge (Priest Stamina ~10-13, cap 5 per hop = exactly two
    hops, the third is refused - "launches me twice"); (2) a second charged orb of the same cast (two SPAWNs within a tick) -> Leap.begin fires
    the first leap's orb at once and hops AGAIN. Fix (Leap + ArmoryTrav, no new row): the re-launched orb is ALSO recognised by its caster +
    projectile id within 0.5 s of the re-launch (Leap.ownShot); a second wand hop for the same caster within 250 ms (no real cast is that quick:
    the hold alone takes 0.35 s) is the same cast - no hop, no Stamina, its orb removed (ArmoryTrav.dupHop / markHop, both hop paths: the leap
    and the 0.1.2 hop job). Each guard writes ONE WARN the first time it fires (the server log then says which cause Skyy hit). The hang's
    per-tick Sets were checked too: never upward, sideways at most 0.2 x the hop's (no second push). The asset path (HOP_MODE "asset" = an
    ApplyForce in the chain) is off in the jar - R19a walks every wand charged chain: no ApplyForce.
  SHORTER ("a little too far, especially if i look down and jump"). hop.force default 30 -> 22 (one-time update of an untouched 30, PROJECT-RULES
    4: History copy first, a change-log line Server Setup -> Changes can undo, the run-once marker "SkyyArmory 0.1.16 wand hop force", bytes +
    line endings kept; a hand-set value is kept + logged). NEW row hop.maxUp (Server Setup > Armory > Wand + signature, default 15 b/s, 0 = no
    cap = the 0.1.15 way): the UPWARD part of the push is at most 15 b/s (~3.5 blocks up, the height of a normal 45-degree backward hop at 22),
    and in mid-air a jump's rise counts toward it (TravMath.capUp: v^2 = cap^2 - (jump^2 - vy^2) while |vy| < the player's jump speed; the
    jump's own rise is never cut) - the hop is still a Velocity SET (never Add), so a jump never stacks on top. Downward / flat pushes are
    unchanged; the sideways part is unchanged (a backwards escape). The bow leap (bow.hopForce) is untouched.
  ONE INFO line per start: the first wand hop's real numbers (sideways, up, the cap, the speed you had) so a test session's log shows them.
  NUMBERS (g = 32 b/s^2, the engine's PhysicsConstants; the Monk probe measured 17 b/s -> 4.6 blocks up; jump 11.8 b/s = vanilla JumpForce):
    looking straight down: 0.1.15 30 b/s up = ~14 blocks; 0.1.16 15 b/s = ~3.5 blocks. Down + jump: 0.1.15 ~16 blocks (14 + the jump's ~2.2);
    0.1.16 ~3.5 blocks above where the jump started. 45 degrees down: 0.1.15 21.2 up / 21.2 back = ~7 blocks up, ~9 back; 0.1.16 15 up / 15.6
    back = ~3.5 up, ~5 back. Flat: 0.1.15 ~5 blocks back; 0.1.16 ~3.7 (horizontal = estimates: the hang starts 0.1 s after a flat hop and the
    engine bleeds about half of a sideways push in the air - Monk probe m5).
No new item / asset / interaction; saved data: config.properties only (the migration + 1 new key - a missing key reads its default).
ROLLBACK: 0.1.15 reads hop.force 22 as a custom value and ignores hop.maxUp (no data loss); set hop.force back to 30 by hand if wanted.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.15.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.16.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.15.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.16.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.15"\nMOD = "SkyyArmory"' in s and "0.1.15 = THE THREE ARMORY UNTIERED ITEMS" in s, "build_skyyarmory_0.1.15.py is not the 0.1.15 pin"
assert "hop.maxUp" not in s and "migrate016" not in s and "dupHop" not in s, "0.1.15 already has the 0.1.16 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.15 - build script (javassist via jpype). GENERATED by tools/armory_0_1_15_patch.py from the GENERATED 0.1.14 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.15.py -> SkyyArmory/SkyyArmory-0.1.15.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.15.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.16 - build script (javassist via jpype). GENERATED by tools/armory_0_1_16_patch.py from the GENERATED 0.1.15 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.16.py -> SkyyArmory/SkyyArmory-0.1.16.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.16.py --dir tools/dev/scratch/<task>/harness.

0.1.16 = THE WAND HOP FIX (Skyy 2026-10-10: "the wand charge shot launches me twice for some reason, and it launches a little too far
especially if i look down and jump"; full notes in tools/armory_0_1_16_patch.py): ONE hop per charged cast - the orb re-launched after the hang
is also known by its caster + id (never a second leap), a second wand hop of the same caster within 250 ms is the same cast (no hop, no
Stamina, its orb removed); hop.force default 30 -> 22 (one-time update of an untouched 30); NEW row hop.maxUp (15 b/s, 0 = no cap): the upward
part of the push is capped and a jump's rise counts toward it (the hop is a Set, it never stacks on a jump). No void protection (Skyy).

0.1.15 (the base, everything below is still true unless 0.1.16 above says otherwise):
''')
rep('VERSION = "0.1.15"\nMOD = "SkyyArmory"', 'VERSION = "0.1.16"\nMOD = "SkyyArmory"')

# ---------------------------------------------------------------------------------------------------------------- rows: hop.force 22 + hop.maxUp
rep(""" ('hop.force',
  'Wand hop force',
  'hop',
  'dec',
  '30',
  '0',
  '50',
  '',
  '',
  'live',
  'Skyy 2026-10-06: 30 (0.1.2: 13 = the dagger dash, too weak). 0 = no hop.',
  'HOP_FORCE',
  'double',
  '30',
  'Wand hop force (Skyy 2026-10-06: 30; 13 = the vanilla dagger dash, 0 = no hop).'),""",
    """ ('hop.force',
  'Wand hop force',
  'hop',
  'dec',
  '22',
  '0',
  '50',
  '',
  '',
  'live',
  'Skyy 2026-10-10: 22 ("a little too far"; 0.1.15: 30, 0.1.2: 13). 0 = no hop.',
  'HOP_FORCE',
  'double',
  '22',
  'Wand hop force (Skyy 2026-10-10: 22, "a little too far"; 0.1.15: 30; 13 = the vanilla dagger dash, 0 = no hop).'),""")
rep("""    ('hop.hangFall', 'Wand hang drift down (b/s)', 'hop', 'dec', '1.5', '0', '10', '', '', 'live', 'Downward speed while hanging (0 = hold still).', 'HOP_FALL', 'double', '1.5', 'Downward speed (blocks per second) while the wand hop hangs at the top (0 = hold still).'),
""", """    ('hop.hangFall', 'Wand hang drift down (b/s)', 'hop', 'dec', '1.5', '0', '10', '', '', 'live', 'Downward speed while hanging (0 = hold still).', 'HOP_FALL', 'double', '1.5', 'Downward speed (blocks per second) while the wand hop hangs at the top (0 = hold still).'),
    # 0.1.16 (Skyy 2026-10-10: "a little too far especially if i look down and jump"): the upward part of the wand hop is capped (TravMath.capUp)
    ('hop.maxUp', 'Wand hop max up speed (b/s)', 'hop', 'dec', '15', '0', '50', '', '', 'live', 'Caps the upward push (look down = up). 15 = about 3.5 blocks; a jump never adds. 0 = no cap.', 'HOP_MAXUP', 'double', '15', "Wand hop: the upward part of the push is at most this (blocks per second; 15 = about 3.5 blocks up; in mid-air a jump's rise counts toward it; 0 = no cap, the 0.1.15 way)."),
""")
rep("""M14_MARK_ID = 'SkyyArmory 0.1.4 staff blink reach'
""", """M16_MARK_ID = 'SkyyArmory 0.1.16 wand hop force'
M16_MARK = '# SkyyArmory 0.1.16 wand hop force (Skyy 2026-10-10: "a little too far"): the wand hop pushes 22 (0.1.15: 30) - a line still on the old 30 was updated once'
M14_MARK_ID = 'SkyyArmory 0.1.4 staff blink reach'
""")
rep('''    "# Wand hop force (Skyy 2026-10-06: 30; 13 = the vanilla dagger dash, 0 = no hop).",
    M13_MARK,
    "hop.force=30",''', '''    "# Wand hop force (Skyy 2026-10-10: 22, \\"a little too far\\"; 0.1.15: 30; 13 = the vanilla dagger dash, 0 = no hop).",
    M13_MARK,
    M16_MARK,
    "hop.force=22",''')
rep('''  HOP_FORCE = dec(c.getProperty("hop.force"), 30.0, 0.0, 50.0);      // 0.1.3: Skyy "30" (max 25 -> 50)''',
    '''  HOP_FORCE = dec(c.getProperty("hop.force"), 22.0, 0.0, 50.0);      // 0.1.16: Skyy "a little too far" 30 -> 22 (0.1.3: "30", max 25 -> 50)''')
rep('''  HOP_FALL = dec(c.getProperty("hop.hangFall"), 1.5, 0.0, 10.0);
''', '''  HOP_FALL = dec(c.getProperty("hop.hangFall"), 1.5, 0.0, 10.0);
  HOP_MAXUP = dec(c.getProperty("hop.maxUp"), 15.0, 0.0, 50.0);          // 0.1.16: the upward part of the wand hop (0 = no cap)
''')
rep('''  return "wand hold: hop " + HOP_FORCE + (HOP_HANG > 0.0 ?''',
    '''  return "wand hold: hop " + HOP_FORCE + (HOP_MAXUP > 0.0 ? " (up at most " + HOP_MAXUP + " b/s, a jump never adds)" : " (no up cap)") + ", one hop per cast" + (HOP_HANG > 0.0 ?''')

# ---------------------------------------------------------------------------------------------------------------- the one-time update 30 -> 22
_a = s.index('for f in ("public static final String M13_KEY = \\"hop.force\\";"')
_b = s.index('for f in ("public static final String M14_KEY1 = \\"blink.distance\\";"')
_m13 = s[_a:_b]
assert _m13.count("migrate013") == 1 and _m13.count('M13_OLD = \\"13\\"') == 1 and _m13.count('M13_NEW = \\"30\\"') == 1, "the migrate013 block moved"
_m16 = _m13.replace("M13_", "M16_").replace("m13Is", "m16Is").replace("m13Update", "m16Update").replace("m13Log", "m16Log").replace("migrate013", "migrate016")
for _o, _n in (('M16_OLD = \\"13\\"', 'M16_OLD = \\"30\\"'), ('M16_NEW = \\"30\\"', 'M16_NEW = \\"22\\"'),
               ('M16_WHO = \\"SkyyArmory 0.1.3\\"', 'M16_WHO = \\"SkyyArmory 0.1.16\\"'),
               ('" kept (custom) - the 0.1.3 default is "', '" kept (custom) - the 0.1.16 default is "'),
               ('"before the 0.1.3 wand hop force update"', '"before the 0.1.16 wand hop force update"'),
               ('"config.properties NOT updated to the 0.1.3 wand hop force:', '"config.properties NOT updated to the 0.1.16 wand hop force:'),
               ('"config.properties updated to the 0.1.3 wand hop force: " + chg + " (Skyy 2026-10-06; the old file',
                '"config.properties updated to the 0.1.16 wand hop force: " + chg + " (Skyy 2026-10-10: a little too far; the old file'),
               ('"config.properties: no hop.force line held the old 13 - nothing changed (0.1.3 hop force marker added)"',
                '"config.properties: no hop.force line held the old 30 - nothing changed, the new default 22 applies (0.1.16 hop force marker added)"'),
               ('"could not update config.properties to the 0.1.3 wand hop force (the file is used as it is): "',
                '"could not update config.properties to the 0.1.16 wand hop force (the file is used as it is): "')):
    assert _m16.count(_o) == 1, "m16 clone anchor: " + _o
    _m16 = _m16.replace(_o, _n)
assert "0.1.3" not in _m16 and "M13" not in _m16 and "m13" not in _m16, [l_ for l_ in _m16.split("\n") if "0.1.3" in l_ or "13" in l_][:5]
s = s[:_b] + "# 0.1.16 (Skyy 2026-10-10: \"a little too far\"): hop.force 30 -> 22 ONCE - the migrate013 steps, same rules (PROJECT-RULES 4)\n" + _m16 + s[_b:]
rep('''  String m14 = @PKG@.ArmoryCfg.migrate014();          // 0.1.4: blink.distance 10 -> 16 / blink.floorCheck 12 -> 0 ONCE (same rules)
''', '''  String m14 = @PKG@.ArmoryCfg.migrate014();          // 0.1.4: blink.distance 10 -> 16 / blink.floorCheck 12 -> 0 ONCE (same rules)
  String m16 = @PKG@.ArmoryCfg.migrate016();          // 0.1.16: a hop.force line still at 30 becomes 22 ONCE (same rules; after 0.1.3's 13 -> 30)
''')
rep('''  @PKG@.ArmoryLog.info("@VERSION@ leap: " + @PKG@.ArmoryCfg.LEAP_TEXT + (m13.length() > 0 ? "; " + m13 : "") + (m14.length() > 0 ? "; " + m14 : ""));''',
    '''  @PKG@.ArmoryLog.info("@VERSION@ leap: " + @PKG@.ArmoryCfg.LEAP_TEXT + (m13.length() > 0 ? "; " + m13 : "") + (m14.length() > 0 ? "; " + m14 : "") + (m16.length() > 0 ? "; " + m16 : ""));''')
rep('''  @PKG@.Leap.STATES.clear();
''', '''  @PKG@.Leap.STATES.clear();
  @PKG@.Leap.REFIRE_T.clear();          // 0.1.16: one hop per cast
  @PKG@.Leap.REFIRE_P.clear();
  @PKG@.Leap.HOP_LOGGED = false;
  @PKG@.ArmoryTrav.LASTHOP.clear();
''', count=2)          # setup + shutdown

# ---------------------------------------------------------------------------------------------------------------- TravMath.capUp (pure)
rep('''# 0.1.3 THE RHYTHM (pure): the top of a leap''', '''# 0.1.16 (Skyy 2026-10-10: "a little too far, especially if i look down and jump"): the hop's UPWARD speed is at most maxUp; in mid-air
# (jf = the player's jump speed, 0 on the ground) the rise already gained counts toward it - the hop tops out where a hop from the ground
# would (v^2 = cap^2 - (jf^2 - cvy^2) while |cvy| < jf) - and a jump's own rise is never cut (at least cvy). maxUp 0 = no cap (0.1.15);
# a downward / flat push is never changed. The hop stays a Set: a jump never adds on top.
M(tmath, r"""
public static double capUp(double vy, double maxUp, double jf, double cvy) {
  if (!(maxUp > 0.0) || !(vy > 0.0)) return vy;
  double v = vy < maxUp ? vy : maxUp;
  if (jf > 0.0 && !Double.isNaN(cvy) && cvy > 0.0 - jf && cvy < jf) {
    double left = v * v - (jf * jf - cvy * cvy);
    v = left > 0.0 ? Math.sqrt(left) : 0.0;
    if (cvy > v) v = cvy;
  }
  return v;
}""")
# 0.1.3 THE RHYTHM (pure): the top of a leap''')

# ---------------------------------------------------------------------------------------------------------------- ArmoryTrav: one hop per cast + the cap
rep('''# ---- THE HOP (spec 1.2 + 2.3): Set velocity opposite to the look, the dagger dash's config; half without ground behind
M(trav, r"""
public static void hop(@PKG@.TravJob j) {''', '''# ---- 0.1.16 ONE HOP PER CAST (Skyy: "launches me twice"): the last wand hop per caster; a second one within DUP_MS is the same cast (no real
# cast is that quick: the hold alone takes 0.35 s) - shared by the leap (Leap.onWandOrb) and the 0.1.2 hop job (hop)
for f in ("public static final java.util.concurrent.ConcurrentHashMap LASTHOP = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long DUP_MS = 250L;", "public static volatile long DUPS = 0L;"):          # DUP_MS: a harness seam (0 = off = the 0.1.15 logic)
    F(trav, f)
M(trav, r"""
public static boolean dupHop(java.util.UUID u, long now) {
  if (u == null || DUP_MS <= 0L) return false;
  Object o = LASTHOP.get(u);
  if (!(o instanceof Long)) return false;
  long age = now - ((Long) o).longValue();
  return age >= 0L && age < DUP_MS;
}""")
# fix round: bounded like TravWorld.pend (a caster's entry only matters for DUP_MS; 256+ casters since the start -> start over)
M(trav, r"""
public static void markHop(java.util.UUID u, long now) {
  if (u == null) return;
  if (LASTHOP.size() > 256) LASTHOP.clear();
  LASTHOP.put(u, Long.valueOf(now));
}""")
# the player's own jump speed (MovementManager settings - Acrobatics boosts included; the Monk's reader) and ground flag; unreadable = 11.8 / ground
M(trav, r"""
public static double jumpOf(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MMG@.getComponentType());
    @MVS@ s = o instanceof @MMG@ ? ((@MMG@) o).getSettings() : null;
    if (s != null && s.jumpForce > 0.0f) return (double) s.jumpForce;
  } catch (Throwable t) { }
  return 11.8;
}""")
M(trav, r"""
public static boolean grounded(@CAC@ acc, @REF@ r) {
  try {
    Object o = acc.getComponent(r, @MSC@.getComponentType());
    if (!(o instanceof @MSC@)) return true;
    @MST@ m = ((@MSC@) o).getMovementStates();
    return m == null || m.onGround;
  } catch (Throwable t) { return true; }
}""")
# the wand hop's upward speed: hop.maxUp, a mid-air jump's rise counted (TravMath.capUp); maxUp 0 = unchanged (0.1.15)
M(trav, r"""
public static double upVy(@CAC@ acc, @REF@ r, double vy, double maxUp, double cvy) {
  if (!(maxUp > 0.0) || !(vy > 0.0)) return vy;
  double jf = grounded(acc, r) ? 0.0 : jumpOf(acc, r);
  return @PKG@.TravMath.capUp(vy, maxUp, jf, cvy);
}""")
# ---- THE HOP (spec 1.2 + 2.3): Set velocity opposite to the look, the dagger dash's config; half without ground behind
M(trav, r"""
public static void hop(@PKG@.TravJob j) {''')
rep('''  if (pos == null || v == null || w == null) return;
  double cost = @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.W_C[j.idx], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (takeStamina(st, ref, cost) == 0) { LAST_WHY = "hop: too little Stamina"; tell(pr, "Not enough Stamina to hop - " + @PKG@.TravMath.fmt(cost) + " needed."); return; }
  double[] hv = @PKG@.TravMath.hopVector(j.dir[0], j.dir[1], j.dir[2], @PKG@.ArmoryCfg.HOP_FORCE, false);          // 0.1.7: never halved over the void (Skyy)
  double cvy = Double.NaN;
  try { @VEC@ cv = v.getClientVelocity(); if (cv != null) cvy = cv.y; } catch (Throwable t1) { cvy = Double.NaN; }
  double vy = @PKG@.TravMath.hopVy(hv[1], cvy, maxFall(w));         // trav-fix: a hop never cancels a damaging fall (Double-Jump rule 7)
  boolean kept = vy != hv[1];
  v.addInstruction(new @VEC@(hv[0], vy, hv[2]), dash(), @CVT@.Set);
  HOPS = HOPS + 1L;''', '''  if (pos == null || v == null || w == null) return;
  long now = System.currentTimeMillis();
  if (dupHop(j.u, now)) {          // 0.1.16: the same cast twice (Skyy: "launches me twice") - no second hop, no Stamina
    DUPS = DUPS + 1L;
    LAST_WHY = "hop: same cast - second hop blocked";
    warn("dup", "a second wand hop for the same cast was blocked (two hop jobs within " + DUP_MS + " ms) - one hop per cast (0.1.16)");
    return;
  }
  double cost = @PKG@.TravMath.staminaCost((double) @PKG@.ArmoryDefs.W_C[j.idx], @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (takeStamina(st, ref, cost) == 0) { LAST_WHY = "hop: too little Stamina"; tell(pr, "Not enough Stamina to hop - " + @PKG@.TravMath.fmt(cost) + " needed."); return; }
  double[] hv = @PKG@.TravMath.hopVector(j.dir[0], j.dir[1], j.dir[2], @PKG@.ArmoryCfg.HOP_FORCE, false);          // 0.1.7: never halved over the void (Skyy)
  double cvy = Double.NaN;
  try { @VEC@ cv = v.getClientVelocity(); if (cv != null) cvy = cv.y; } catch (Throwable t1) { cvy = Double.NaN; }
  double up = upVy(st, ref, hv[1], @PKG@.ArmoryCfg.HOP_MAXUP, cvy);          // 0.1.16: hop.maxUp, a jump never adds
  double vy = @PKG@.TravMath.hopVy(up, cvy, maxFall(w));         // trav-fix: a hop never cancels a damaging fall (Double-Jump rule 7)
  boolean kept = vy != up;
  v.addInstruction(new @VEC@(hv[0], vy, hv[2]), dash(), @CVT@.Set);
  markHop(j.u, now);
  HOPS = HOPS + 1L;''')

# ---------------------------------------------------------------------------------------------------------------- Leap: the re-launched orb by caster + the cap
rep('''          "public static volatile long REFUSED = 0L;", "public static volatile long NOSHOT = 0L;", "public static volatile long SWEPT = 0L;",''',
    '''          "public static volatile long REFUSED = 0L;", "public static volatile long NOSHOT = 0L;", "public static volatile long SWEPT = 0L;",
          # 0.1.16 one hop per cast: the wand orb re-launched at the end of the hang, by caster (time + projectile id); the counters; the INFO once
          "public static final java.util.concurrent.ConcurrentHashMap REFIRE_T = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap REFIRE_P = new java.util.concurrent.ConcurrentHashMap();",
          # REFIRE_MS is also a harness seam (0 = off = the 0.1.15 logic: by the Ref only)
          "public static volatile long REFIRE_MS = 500L;", "public static volatile long DUPES = 0L;", "public static volatile long REFIRE_SEEN = 0L;",
          "public static volatile boolean HOP_LOGGED = false;",''')
rep('''  tw.pend.put(nr, ts);
  if (s.kind == 2) @PKG@.ArmoryTrav.sound(SND_SHOT, x, y, z, buf);''', '''  tw.pend.put(nr, ts);
  if (s.kind == 1 && s.u != null && s.pid != null) {          // 0.1.16: also known by its caster + id (never a second leap)
    if (REFIRE_T.size() > 256) { REFIRE_T.clear(); REFIRE_P.clear(); }          // fix round: bounded (a record matters for REFIRE_MS only)
    REFIRE_T.put(s.u, Long.valueOf(System.currentTimeMillis()));
    REFIRE_P.put(s.u, s.pid);
  }
  if (s.kind == 2) @PKG@.ArmoryTrav.sound(SND_SHOT, x, y, z, buf);''')
rep('''public static double[] hopNow(@CB@ buf, @REF@ r, double[] dir, double force) {
  @VEC@ pos = @PKG@.ArmoryTrav.posOf(buf, r);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
  if (pos == null || dir == null || !(force > 0.0)) return null;
  double[] hv = @PKG@.TravMath.hopVector(dir[0], dir[1], dir[2], force, false);          // 0.1.7: never halved over the void (Skyy)
  double cvy = clientVy(buf, r);
  double vy = @PKG@.TravMath.hopVy(hv[1], cvy, @PKG@.ArmoryTrav.maxFall(w));
  if (!vel(buf, r, hv[0], vy, hv[2], true)) return null;
  return new double[] { hv[0], vy, hv[2], vy != hv[1] ? 1.0 : 0.0, 1.0 };
}""")''', '''public static double[] hopNow(@CB@ buf, @REF@ r, double[] dir, double force, double maxUp) {
  @VEC@ pos = @PKG@.ArmoryTrav.posOf(buf, r);
  @WLD@ w = @PKG@.ArmoryTrav.worldOf(buf);
  if (pos == null || dir == null || !(force > 0.0)) return null;
  double[] hv = @PKG@.TravMath.hopVector(dir[0], dir[1], dir[2], force, false);          // 0.1.7: never halved over the void (Skyy)
  double cvy = clientVy(buf, r);
  double up = @PKG@.ArmoryTrav.upVy(buf, r, hv[1], maxUp, cvy);          // 0.1.16: the wand's hop.maxUp (the bow passes 0 = unchanged)
  double vy = @PKG@.TravMath.hopVy(up, cvy, @PKG@.ArmoryTrav.maxFall(w));
  if (!vel(buf, r, hv[0], vy, hv[2], true)) return null;
  if (maxUp > 0.0 && !HOP_LOGGED) {
    HOP_LOGGED = true;
    @PKG@.ArmoryLog.info("first wand hop after start: back " + @PKG@.TravMath.fmt(Math.sqrt(hv[0] * hv[0] + hv[2] * hv[2])) + " b/s, up "
      + @PKG@.TravMath.fmt(vy) + " b/s (look " + @PKG@.TravMath.fmt(hv[1]) + ", hop.force " + @PKG@.TravMath.fmt(force) + ", hop.maxUp "
      + @PKG@.TravMath.fmt(maxUp) + ", your up speed before it " + (Double.isNaN(cvy) ? "?" : @PKG@.TravMath.fmt(cvy)) + ") - one hop per cast");
  }
  return new double[] { hv[0], vy, hv[2], vy != up ? 1.0 : 0.0, 1.0 };
}""")''')
rep('''  double[] h = hopNow(buf, r, dir, force);
  if (h != null) { s.hx = h[0]; s.hz = h[2]; s.hopVy = h[1]; s.kept = h[3] > 0.5; }''',
    '''  double[] h = hopNow(buf, r, dir, force, kind == 1 ? @PKG@.ArmoryCfg.HOP_MAXUP : 0.0);          // 0.1.16: the cap on the wand only
  if (h != null) { s.hx = h[0]; s.hz = h[2]; s.hopVy = h[1]; s.kept = h[3] > 0.5; }''')
rep('''public static boolean onWandOrb(@REF@ orb, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  java.util.UUID u = pc.getCreatorUuid();
  @REF@ r = refOf(buf, u);''', '''public static boolean onWandOrb(@REF@ orb, @LPC@ pc, int c, @ST@ st, @CB@ buf) {
  java.util.UUID u = pc.getCreatorUuid();
  long now = System.currentTimeMillis();
  if (u != null && @PKG@.ArmoryTrav.dupHop(u, now)) {          // 0.1.16: a second charged orb of the SAME cast (Skyy: "launches me twice")
    buf.removeEntity(orb, @REMR@.REMOVE);
    DUPES = DUPES + 1L;
    LAST_WHY = "wand: same cast - second hop blocked";
    warn("dup", "a second wand hop for the same cast was blocked (two charged orbs within " + @PKG@.ArmoryTrav.DUP_MS + " ms) - one hop per cast (0.1.16)");
    return true;
  }
  @REF@ r = refOf(buf, u);''')
rep('''  buf.removeEntity(orb, @REMR@.REMOVE);
  begin(1, u, r, st, buf, pc.getProjectileAssetName(), c, item, 0.0, d, @PKG@.ArmoryCfg.HOP_FORCE, @PKG@.ArmoryCfg.HOP_HANG, @PKG@.ArmoryCfg.HOP_FALL);
  @PKG@.ArmoryTrav.HOPS = @PKG@.ArmoryTrav.HOPS + 1L;''', '''  buf.removeEntity(orb, @REMR@.REMOVE);
  begin(1, u, r, st, buf, pc.getProjectileAssetName(), c, item, 0.0, d, @PKG@.ArmoryCfg.HOP_FORCE, @PKG@.ArmoryCfg.HOP_HANG, @PKG@.ArmoryCfg.HOP_FALL);
  @PKG@.ArmoryTrav.markHop(u, now);          // 0.1.16: one hop per cast
  @PKG@.ArmoryTrav.HOPS = @PKG@.ArmoryTrav.HOPS + 1L;''')
# Leap.ownShot: the SPAWN of a wand charged orb is the leap's own re-launch when its Ref was marked (pend) OR its caster re-launched that id
# within REFIRE_MS (0.1.15 knew it by the Ref only - a miss = a second leap + a second hop)
rep('''# BOW (GrappleBoltSys, the full-draw arrow's SPAWN - our model id)''', '''# 0.1.16: is this wand charged orb's SPAWN the leap's own re-launch? hit = its Ref was in TravWorld.pend; else its caster re-launched this
# projectile id within REFIRE_MS (the record is used once; an old one is dropped)
M(leap, r"""
public static boolean ownShot(java.util.UUID u, String pid, boolean hit) {
  if (u == null) return hit;
  Object t = REFIRE_T.get(u);
  Object p = REFIRE_P.get(u);
  if (hit) { REFIRE_T.remove(u); REFIRE_P.remove(u); return true; }
  if (REFIRE_MS <= 0L) return false;
  long now = System.currentTimeMillis();
  if (t instanceof Long) {
    long age = now - ((Long) t).longValue();
    if (age < 0L || age > REFIRE_MS) { REFIRE_T.remove(u); REFIRE_P.remove(u); }
    else if (pid != null && p != null && pid.equals(String.valueOf(p))) {
      REFIRE_T.remove(u);
      REFIRE_P.remove(u);
      REFIRE_SEEN = REFIRE_SEEN + 1L;
      warn("refire", "the wand orb re-launched after the hang was known by its caster, not by its entity - no second hop (0.1.16 guard)");
      return true;
    }
  }
  // fix round (a hang shorter than the 250 ms same-cast window): this caster hopped moments ago and that leap has ALREADY fired (none
  // running) -> this is its re-launched orb: kept as the shot (never removed as a duplicate), no second hop
  if (@PKG@.ArmoryCfg.HOP_HANG > 0.0 && STATES.get(u) == null && @PKG@.ArmoryTrav.dupHop(u, now)) {
    REFIRE_SEEN = REFIRE_SEEN + 1L;
    warn("refire", "the wand orb re-launched after a short hang was known by its caster's hop moments ago - kept as the shot, no second hop (0.1.16 guard)");
    return true;
  }
  return false;
}""")
# BOW (GrappleBoltSys, the full-draw arrow's SPAWN - our model id)''')
rep('''    @PKG@.TravShot lp = (@PKG@.TravShot) tw.pend.remove(ref);          // 0.1.3: the orb a leap fired at the end of its hang (no new leap)
    if (lp == null && @PKG@.ArmoryCfg.PART_TRAV && cu != null && HOP_SERVER && @PKG@.ArmoryCfg.HOP_HANG > 0.0 && @PKG@.ArmoryCfg.HOP_FORCE > 0.0
        && @PKG@.Leap.onWandOrb(ref, pc, c, st, buf)) return;           // 0.1.3: hop -> hang -> THEN the orb (Skyy 2026-10-06)''',
    '''    @PKG@.TravShot lp = (@PKG@.TravShot) tw.pend.remove(ref);          // 0.1.3: the orb a leap fired at the end of its hang (no new leap)
    boolean own = @PKG@.Leap.ownShot(cu, pid, lp != null);          // 0.1.16: ... also known by its caster + id (Skyy: "launches me twice")
    if (!own && @PKG@.ArmoryCfg.PART_TRAV && cu != null && HOP_SERVER && @PKG@.ArmoryCfg.HOP_HANG > 0.0 && @PKG@.ArmoryCfg.HOP_FORCE > 0.0
        && @PKG@.Leap.onWandOrb(ref, pc, c, st, buf)) return;           // 0.1.3: hop -> hang -> THEN the orb (Skyy 2026-10-06)''')
rep('''    tw.orbs.put(ref, ws);
    if (lp != null) return;
    if (!@PKG@.ArmoryCfg.PART_TRAV || cu == null || !HOP_SERVER) return;''', '''    tw.orbs.put(ref, ws);
    if (own) return;
    if (!@PKG@.ArmoryCfg.PART_TRAV || cu == null || !HOP_SERVER) return;''')

# ---------------------------------------------------------------------------------------------------------------- prints
rep('''print("0.1.15 Untiered items: %s;''', '''print("0.1.16 wand hop: one hop per cast (re-launch known by caster + id within %d ms, same-cast guard %d ms), hop.force default 22 (one-time update "
      "marker %r), hop.maxUp row default %s (a jump never adds)" % (500, 250, M16_MARK_ID, [r_[4] for r_ in CFG_LEAP if r_[0] == "hop.maxUp"][0]))
print("0.1.15 Untiered items: %s;''')

with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(DST, ROOT))

# ================================================================================================================ the harness
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.15 - test harness. GENERATED by tools/armory_0_1_15_patch.py from test_skyyarmory_0.1.14.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.16 - test harness. GENERATED by tools/armory_0_1_16_patch.py from test_skyyarmory_0.1.15.py - edit the patch, never this file.
Run: python SkyyArmory/test_skyyarmory_0.1.16.py --dir tools/dev/scratch/<task>/harness   (--no-set skips the one-JVM SET run, --keep keeps it)
Every 0.1.15 check still runs on the 0.1.15 shape: the jar's files are 0.1.15's (P18 proves it: only the classes + the manifest version differ);
the classes are the real 0.1.16 ones; the old wand / migration / row checks run with the 0.1.15 numbers pinned (hop.force 30, hop.maxUp 0 = no
cap - the exact 0.1.15 maths) where they need them; R18g now compares 0.1.14 -> 0.1.15 (history), R19g 0.1.15 -> 0.1.16.
NEW P18 (Python) + R19 (JVM, after R18) EXECUTE every 0.1.16 path:
  P18  vs the 0.1.15 jar: every non-class file byte-identical except the manifest (its version only)
  R19  a: every wand charged chain in the jar (7 metal roots + the Wood wand) walked: no ApplyForce anywhere (the asset hop path is off),
       exactly ONE Charging key reaches the charged cast; b: THE TWO WAYS ONE CAST HOPPED TWICE, reproduced as MUTANTS (the 0.1.16 guards off =
       the 0.1.15 logic): (1) the re-launched orb's SPAWN not matched by its Ref -> 2 dash pushes + 2 Stamina charges (Priest Stamina 10 = two
       hops, "launches me twice"), (2) two charged orbs of one cast -> 2 pushes; with the guards: exactly ONE push per cast in both, the
       re-launched orb still bursts + heals; a REAL second cast 0.3 s later still hops; the 0.1.2 hop job (hang 0) also once; c: a full cast
       counted end to end (spawn -> rise -> hang -> re-launch -> its SPAWN -> more ticks): 1 push, the hang Sets never upward and at most
       0.2 x the hop sideways; d: TravMath.capUp numbers + ArmoryTrav.upVy on the stand-ins (ground / mid-air / the jump's own rise kept /
       0 = no cap); the hop numbers flat / 45 down / straight down / down + jump at 0.1.15 and 0.1.16 defaults (the report's table); the bow
       leap unchanged (no cap); e: the rows (hop.force 22, hop.maxUp 15 + clamps) + armory:leap text; f: THE ONE-TIME UPDATE 30 -> 22 (text
       step: untouched 30 -> 22 + marker, 22 / custom kept + note, no line = marker only, CRLF kept; then the real migrate016 on a scratch
       file: History copy first, a change-log line, the marker; the second run changes nothing); g: vs the 0.1.15 jar method by method (only
       the planned methods / fields differ).

0.1.15 harness: SkyyArmory 0.1.15 - test harness. GENERATED by tools/armory_0_1_15_patch.py from test_skyyarmory_0.1.14.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.15"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.15 SkyyArmory"',
     'VERSION = "0.1.16"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.16 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "ut02", "harness")', 'os.path.join(SCRATCH_ROOT, "armory0116", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.15.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.16.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.15"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.16"))')
hrep('"[SkyyArmory] 0.1.15 ready" in m_', '"[SkyyArmory] 0.1.16 ready" in m_')
hrep('"0.1.15 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.16 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.15 crossbow grapple: grapple on" in m_', '"0.1.16 crossbow grapple: grapple on" in m_')
hrep('"0.1.15 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_',
     '"0.1.16 monk moves on - Pole-Vault (Bo hold): lunge 3 in 0.2 s, 4.5 up x 7 forward (push x2.1)" in m_')
hrep('"0.1.15 wand signature on - the signature key when the meter is full (20; quick-shot hit +1, charged hit +2)" in m_',
     '"0.1.16 wand signature on - the signature key when the meter is full (20; quick-shot hit +1, charged hit +2)" in m_')
hrep('come from Skyy:0.1.15 SkyyArmory" in str(r[1])', 'come from Skyy:0.1.16 SkyyArmory" in str(r[1])')
hrep('t_.replace("0.1.15", "V").replace("0.1.14", "V")', 't_.replace("0.1.16", "V").replace("0.1.15", "V").replace("0.1.14", "V")')
hrep("    MN18, MO18 = methods_of(JAR), methods_of(OLD114)",
     "    MN18, MO18 = methods_of(OLD115), methods_of(OLD114)          # 0.1.16: R18g = the 0.1.15 round's compare (history); R19g = 0.1.15 -> 0.1.16")
hrep('OLD113 = os.path.join(HERE, "SkyyArmory-0.1.13.jar")\n', '''OLD113 = os.path.join(HERE, "SkyyArmory-0.1.13.jar")
OLD115 = os.path.join(HERE, "SkyyArmory-0.1.15.jar")          # 0.1.16: the base (the SET pin)
if not os.path.isfile(OLD115):
    raise SystemExit("the 0.1.16 harness needs SkyyArmory-0.1.15.jar (the base, the SET pin) next to it: %s" % OLD115)
''')

# ---- the old checks on the 0.1.15 shape: the guards off (their synthetic casts come in the same millisecond) - R19 switches them on
hrep('''    AT, TW, TM, TJ, TH = (JClass(PKG + n_) for n_ in ("ArmoryTrav", "TravWorld", "TravMath", "TravJob", "TravHeal"))
''', '''    AT, TW, TM, TJ, TH = (JClass(PKG + n_) for n_ in ("ArmoryTrav", "TravWorld", "TravMath", "TravJob", "TravHeal"))
    AT.DUP_MS = 0          # 0.1.16: the older checks run the 0.1.15 hop logic (their casts come in the same ms); R19 switches the guards on
    JClass(PKG + "Leap").REFIRE_MS = 0
''')
hrep('''    ACfg.HOP_FORCE = 13.0          # 0.1.3: N2-N7 keep 0.1.1's hop numbers (13) and the 0.1.2 way (no hang); the 0.1.3 defaults are checked in R
''', '''    ACfg.HOP_FORCE = 13.0          # 0.1.3: N2-N7 keep 0.1.1's hop numbers (13) and the 0.1.2 way (no hang); the 0.1.3 defaults are checked in R
    ACfg.HOP_MAXUP = 0.0          # 0.1.16: no up cap (the 0.1.15 maths); the cap is checked in R19
''')
hrep('''"blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "30", "burst.radius": "6",''',
     '''"blink.trailPercent": "30", "blink.tick": "0.5", "blink.cooldown": "0", "hop.force": "22", "burst.radius": "6",          # 0.1.16: 30 -> 22''')
hrep('''    NEW_ROWS += ["hop.hangSeconds", "hop.hangFall", "part.bowtrav",''', '''    NEW_ROWS += ["hop.hangSeconds", "hop.hangFall", "hop.maxUp", "part.bowtrav",''')          # 0.1.16: + hop.maxUp
hrep("    lh11 = LP.hopNow(tbuf, rc, JArray(JDouble)([0.0, 0.0, 1.0]), 30.0)",
     "    lh11 = LP.hopNow(tbuf, rc, JArray(JDouble)([0.0, 0.0, 1.0]), 30.0, 0.0)          # 0.1.16: + maxUp (0 = no cap, the 0.1.15 maths)")
hrep('''    want_l = {"hop.force": "30", "hop.hangSeconds": "0.35",''', '''    want_l = {"hop.force": "22", "hop.maxUp": "15", "hop.hangSeconds": "0.35",          # 0.1.16: 30 -> 22 + the cap row''')
hrep('''    check(abs(float(ACfg.HOP_FORCE) - 30.0) < 1e-9 and abs(float(ACfg.HOP_HANG) - 0.35) < 1e-9''',
     '''    check(abs(float(ACfg.HOP_FORCE) - 22.0) < 1e-9 and abs(float(ACfg.HOP_MAXUP) - 15.0) < 1e-9 and abs(float(ACfg.HOP_HANG) - 0.35) < 1e-9''')
hrep('''ltxt.startswith("wand hold: hop 30.0, hang 0.35 s")''',
     '''ltxt.startswith("wand hold: hop 22.0 (up at most 15.0 b/s, a jump never adds), one hop per cast, hang 0.35 s")''')
hrep('''    # --- R3. THE WAND LEAP: orb removed at its SPAWN -> hop 30 with the dash config -> rise -> hang Sets -> the same orb where you look now
    reset_buf()
''', '''    # --- R3. THE WAND LEAP: orb removed at its SPAWN -> hop 30 with the dash config -> rise -> hang Sets -> the same orb where you look now
    ACfg.HOP_FORCE = 30.0          # 0.1.16: R3 keeps the 0.1.15 numbers (hop.force 30, no up cap); the 0.1.16 defaults are checked in R19
    ACfg.HOP_MAXUP = 0.0
    reset_buf()
''')
hrep('''        r14_ = ACfg.m14Update(t13_)
        want_ = (str(r14_[0]) if r14_ is not None else t13_).encode("latin-1")''', '''        r14_ = ACfg.m14Update(t13_)
        t14_ = str(r14_[0]) if r14_ is not None else t13_
        r16_ = ACfg.m16Update(t14_)          # 0.1.16: + the hop.force 30 -> 22 step
        want_ = (str(r16_[0]) if r16_ is not None else t14_).encode("latin-1")''')
hrep('''and str(ACfg.M13_MARK_ID) in txt1_
              and str(ACfg.M14_MARK_ID) in txt1_,''', '''and str(ACfg.M13_MARK_ID) in txt1_
              and str(ACfg.M14_MARK_ID) in txt1_ and str(ACfg.M16_MARK_ID) in txt1_,''')

hrep('''    check(hv11 is not None and hv11[0] == (0.0, 0.0, -30.0) and why11.startswith("hop full") and hv11b is not None and hv11b[0] == (0.0, 0.0, -30.0)''',
     '''    check(hv11 is not None and hv11[0] == (0.0, 0.0, -22.0) and why11.startswith("hop full") and hv11b is not None and hv11b[0] == (0.0, 0.0, -22.0)          # 0.1.16: the default 22''')

# ---- P18 (Python): vs the 0.1.15 jar every non-class file is byte-identical, the manifest differs in its version only
P18 = r'''
# ================================================================================================================ P18. 0.1.16: only the classes changed
OZ115 = zipfile.ZipFile(OLD115)
_n18, _o18 = set(JZ15.namelist()), set(OZ115.namelist())
_files18 = sorted(n_ for n_ in _n18 | _o18 if not n_.endswith(".class"))
_diff18 = [n_ for n_ in _files18 if n_ != "manifest.json" and (n_ not in _n18 or n_ not in _o18 or JZ15.read(n_) != OZ115.read(n_))]
_m18n, _m18o = json.loads(JZ15.read("manifest.json").decode("utf-8")), json.loads(OZ115.read("manifest.json").decode("utf-8"))
_m18o2 = dict(_m18o)
_m18o2["Version"] = VERSION
_m18o2["Name"] = str(_m18o.get("Name", "")).replace("0.1.15", VERSION)
check(not _diff18 and _m18n == _m18o2 and _m18o.get("Version") == "0.1.15",
      "P18: vs the 0.1.15 jar every one of the %d non-class files is byte-identical; the manifest differs only in its version (Version + the Name's version, 0.1.15 -> %s): %s" % (
          len(_files18), VERSION, _diff18[:5]))
_c18n, _c18o = sorted(n_ for n_ in _n18 if n_.endswith(".class")), sorted(n_ for n_ in _o18 if n_.endswith(".class"))
check(_c18n == _c18o, "P18: the same %d classes (none added / removed): %s" % (len(_c18n), sorted(set(_c18n) ^ set(_c18o))))
print("P18. 0.1.16: %d non-class files identical to 0.1.15, manifest version only, the same %d classes" % (len(_files18), len(_c18n)))
'''
hrep('''print("P17. 0.1.15: 3 Untiered items (Iron copies, no recipe, orange placeholder art), 6 lang lines, nothing else")
''', '''print("P17. 0.1.15: 3 Untiered items (Iron copies, no recipe, orange placeholder art), 6 lang lines, nothing else")
''' + P18)

# ---- R19 (JVM)
R19 = r'''    # ============================================================================ R19. 0.1.16 THE WAND HOP FIX - every new path EXECUTED
    LJ = JClass("java.lang.Long")
    # R19a every wand charged chain (7 metal roots + the Wood wand's Wand_Primary override + SkyySkills' hold) walked: no ApplyForce anywhere
    # (the asset hop path HOP_MODE "asset" is off - the server push is the only one), ONE Charging key reaches the charged cast
    def walk19(x_, seen_, types_):
        if isinstance(x_, str):
            if x_ in seen_:
                return
            seen_.add(x_)
            d_ = JINT.get(x_) or SK_INTS.get(x_) or (aresolve("int", x_) if ahas("int", x_) else None)
            if d_ is not None:
                walk19(d_, seen_, types_)
        elif isinstance(x_, list):
            for e_ in x_:
                walk19(e_, seen_, types_)
        elif isinstance(x_, dict):
            if "Type" in x_:
                types_.append(str(x_["Type"]))
            for k_, v_ in x_.items():
                if k_ in ("Next", "Failed", "Interactions", "CollisionNext", "GroundNext") or "Type" not in x_:          # + Charging key maps
                    walk19(v_, seen_, types_)
    a19 = {}
    for m_ in NEW + ["Wood"]:
        root_ = JINT["SkyyArmory_Wand_Primary_" + m_] if m_ != "Wood" else JINT["Wand_Primary"]
        types_ = []
        walk19(root_, set(), types_)
        hold_ = [k_ for k_ in root_["Next"] if float(k_) >= 0.35]
        a19[m_] = ("ApplyForce" in types_, types_.count("LaunchProjectile") >= 2, len(hold_))
    check(all(v_ == (False, True, 1) for k_, v_ in a19.items() if k_ != "Wood") and a19["Wood"][0] is False and a19["Wood"][2] == 1 and len(a19) == 8,
          "R19a: the 7 metal wands + the Wood wand: no ApplyForce in any tap / hold chain (the asset hop is off: the Java push is the only push), "
          "both shots launch (the Wood hold = SkyySkills' vanilla-var cast), exactly ONE hold key: %s" % a19)

    # the stand-in caster on open ground; every Velocity instruction of the caster, the dash-config ones = the hop pushes
    def instrs19(r_):
        out_ = []
        for o_ in list(comp(r_, VELc.getComponentType()).getInstructions()):
            vec_, cfg_ = None, False
            for f_ in o_.getClass().getDeclaredFields():
                f_.setAccessible(True)
                x_ = f_.get(o_)
                if V3.class_.isInstance(x_):
                    vec_ = (round(float(x_.x()), 4), round(float(x_.y()), 4), round(float(x_.z()), 4))
                elif x_ is not None and str(x_.getClass().getSimpleName()) == "VelocityConfig":
                    cfg_ = True
            out_.append((vec_, cfg_))
        return out_

    def fresh19(stam=10.0):
        reset_buf()
        TW.ALL.clear()
        LP.STATES.clear()
        LP.REFIRE_T.clear()
        LP.REFIRE_P.clear()
        AT.LASTHOP.clear()
        ACfg.useDefaults()
        ACfg.TRAV_FX = False
        AT.GRID = Grid(world_fn())
        AT.NEAR = Near()
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        put(rc, VELc.getComponentType(), VELc())
        put(rc, MSCc.getComponentType(), None)
        comp(rc, VELc.getComponentType()).setClient(0.0, 0.0, 0.0)
        mc.setStatValue(STAM, JFloat(stam))
        mc.setStatValue(MANA, JFloat(200.0))
        if LP.LOOK is not None:
            LP.LOOK.remove(cu)

    def guards19(dup, refire):
        AT.DUP_MS = 250 if dup else 0
        LP.REFIRE_MS = 500 if refire else 0

    def cast19(ref_i, pitch=0.0):
        o_, p_ = launched(ORB["Iron"], ref_i, 0.5, 65.5, 0.5, pitch=pitch)
        AT.added(o_, p_, 2002, tst, tbuf)
        return o_, p_

    def tohang19():          # a level hop: the top at 0.1 s -> the hang; one hang tick
        s_ = LP.STATES.get(cu)
        s_.t0 = NOW() - 150
        LP.tickPlayer(rc, tst, tbuf)
        return s_

    def refire19():          # the hang ends -> Leap.fire re-launches the orb (TBuf.ADDED gets it)
        s_ = LP.STATES.get(cu)
        s_.hangUntil = NOW() - 1
        n_ = len(list(TBf.ADDED))
        LP.tickPlayer(rc, tst, tbuf)
        ad_ = list(TBf.ADDED)[n_:]
        return None if not ad_ else (ad_[0][0].getComponent(LPCc.getComponentType()), ad_[0][1])

    def spawn19(pc_, ref_):          # that orb's SPAWN through the hook (ArmoryTravSys -> ArmoryTrav.added)
        put(ref_, LPCc.getComponentType(), pc_)
        put(ref_, TCc.getComponentType(), TCc(V3(0.5, 65.6, 1.0), R3(0.0, 0.0, 0.0)))
        AT.added(ref_, pc_, 2002, tst, tbuf)

    def pushes19():
        return len([x_ for x_ in instrs19(rc) if x_[1]])

    # R19b(1) the re-launched orb's SPAWN NOT matched by its Ref (another Ref - the record lost) -> 0.1.15: a SECOND leap
    res19 = {}
    for name_, dup_, rf_ in (("mutant (0.1.15 logic)", False, False), ("refire guard only", False, True), ("0.1.16", True, True)):
        fresh19()
        guards19(dup_, rf_)
        cast19(1901)
        tohang19()
        if dup_:
            AT.LASTHOP.put(cu, LJ.valueOf(NOW() - 600))          # the hang took 0.6 s in game (the harness runs it in 0 ms)
        rf = refire19()
        other_ = REFc(tst, 1902)          # NOT the Ref the leap marked in TravWorld.pend
        spawn19(rf[0], other_)
        tw_ = TW.of(tst)
        res19[name_] = (pushes19(), sv(mc, STAM), LP.STATES.get(cu) is not None, tw_.orbs.containsKey(other_), other_ in list(TBf.REMOVED))
    check(res19["mutant (0.1.15 logic)"] == (2, 0.0, True, False, True),
          "R19b(1) MUTANT = the 0.1.15 logic: the re-launched orb's SPAWN with another Ref is taken for a NEW cast -> a SECOND hop + a second "
          "5 Stamina (10 -> 0: a Priest's bar = exactly two hops - Skyy's 'launches me twice'), a new leap, the orb removed again: %s" % (res19["mutant (0.1.15 logic)"],))
    check(res19["refire guard only"] == (1, 5.0, False, True, False) and res19["0.1.16"] == (1, 5.0, False, True, False),
          "R19b(1) FIXED: the same SPAWN is known by its caster + id (Leap.ownShot) -> ONE hop, 5 Stamina once, no new leap, the orb kept as the "
          "burst record (it still bursts + heals): %s" % ({k_: v_ for k_, v_ in res19.items() if k_ != "mutant (0.1.15 logic)"},))
    # R19b(2) two charged orbs of ONE cast (two SPAWNs in one tick) -> 0.1.15: the first leap's orb at once + a SECOND hop
    res19b = {}
    for name_, dup_ in (("mutant (0.1.15 logic)", False), ("0.1.16", True)):
        fresh19()
        guards19(dup_, True)
        cast19(1911)
        n_ad = len(list(TBf.ADDED))
        o2_, p2_ = cast19(1912)
        res19b[name_] = (pushes19(), sv(mc, STAM), len(list(TBf.ADDED)) - n_ad, o2_ in list(TBf.REMOVED), int(LP.DUPES))
    d0_ = res19b["mutant (0.1.15 logic)"][4]
    check(res19b["mutant (0.1.15 logic)"][:4] == (2, 0.0, 1, True) and res19b["0.1.16"][:4] == (1, 5.0, 0, True) and res19b["0.1.16"][4] == d0_ + 1,
          "R19b(2): two charged orbs of one cast - MUTANT (0.1.15 logic): 2 hops, 10 Stamina, the first orb fired at once; 0.1.16: ONE hop, 5 Stamina, "
          "the second orb removed (one shot per cast), DUPES +1: %s" % res19b)
    # fix round: a SHORT hang (0.1 s < the 250 ms same-cast window) + the re-launch missed by its Ref AND by its caster + id -> the orb is the
    # shot (kept, bursts), ONE hop; a bounded LASTHOP (257+ casters -> start over)
    fresh19()
    guards19(True, True)
    ACfg.HOP_HANG = 0.1
    cast19(1961)
    tohang19()
    AT.LASTHOP.put(cu, LJ.valueOf(NOW() - 150))          # rise + the 0.1 s hang
    seen0 = int(LP.REFIRE_SEEN)
    rf = refire19()
    LP.REFIRE_T.clear()          # the caster + id record missed too
    LP.REFIRE_P.clear()
    other_ = REFc(tst, 1962)
    spawn19(rf[0], other_)
    short19 = (pushes19(), sv(mc, STAM), LP.STATES.get(cu) is not None, TW.of(tst).orbs.containsKey(other_), other_ in list(TBf.REMOVED),
               int(LP.REFIRE_SEEN) - seen0)
    UU = JClass("java.util.UUID")
    for k_ in range(300):
        AT.markHop(UU.randomUUID(), 1)
    nlast = int(AT.LASTHOP.size())
    fresh19()
    check(short19 == (1, 5.0, False, True, False, 1) and nlast <= 257,
          "fix round: hang 0.1 s, the re-launch missed by Ref + by caster/id -> ONE hop, 5 Stamina once, no new leap, the orb KEPT as the burst record "
          "(not removed as a duplicate), REFIRE_SEEN +1; LASTHOP bounded (300 casters -> %d): %s" % (nlast, short19,))
    print("R19b-fix. short hang (0.1 s) + the re-launch missed twice: %s (pushes, Stamina, leap running, orb kept, orb removed, REFIRE_SEEN +); LASTHOP after 300 casters: %d" % (short19, nlast))
    # a REAL second cast (0.3 s later) still hops; the 0.1.2 hop job (hop.hangSeconds 0): two jobs of one cast = one hop
    fresh19()
    guards19(True, True)
    cast19(1921)
    AT.LASTHOP.put(cu, LJ.valueOf(NOW() - 300))
    cast19(1922)
    real2 = (pushes19(), sv(mc, STAM))
    jobs19 = {}
    for name_, dup_ in (("mutant (0.1.15 logic)", False), ("0.1.16", True)):
        fresh19()
        guards19(dup_, True)
        ACfg.HOP_HANG = 0.0
        cast19(1931)
        cast19(1932)
        d1_ = int(AT.DUPS)
        for j_ in list(TWd.JOBS):
            j_.run()
        jobs19[name_] = (pushes19(), sv(mc, STAM), len(list(TWd.JOBS)), int(AT.DUPS) - d1_)
    check(real2 == (2, 0.0) and jobs19["mutant (0.1.15 logic)"] == (2, 0.0, 2, 0) and jobs19["0.1.16"] == (1, 5.0, 2, 1),
          "R19b: a real second cast 0.3 s later hops again (%s); the 0.1.2 hop job (hang 0) - MUTANT: two jobs of one cast = 2 hops; 0.1.16: 1 hop, "
          "the second job refused for free (DUPS +1): %s" % (real2, jobs19))
    # R19c ONE CAST END TO END at the 0.1.16 defaults, looking 45 degrees down: spawn -> rise -> top -> hang -> re-launch -> its SPAWN -> 40 ticks
    fresh19()
    guards19(True, True)
    vr_ = comp(rc, VELc.getComponentType())
    cast19(1941, pitch=-0.7853982)
    h0_ = instrs19(rc)
    s_ = LP.STATES.get(cu)
    s_.t0 = NOW() - 150
    vr_.setClient(0.0, 8.0, 0.0)
    LP.tickPlayer(rc, tst, tbuf)
    vr_.setClient(0.0, 0.3, 0.0)
    for k_ in range(5):
        LP.tickPlayer(rc, tst, tbuf)
    AT.LASTHOP.put(cu, LJ.valueOf(NOW() - 800))
    rf = refire19()
    put(rf[1], LPCc.getComponentType(), rf[0])
    put(rf[1], TCc.getComponentType(), TCc(V3(0.5, 66.0, 1.0), R3(0.0, 0.0, 0.0)))
    AT.added(rf[1], rf[0], 2002, tst, tbuf)
    for k_ in range(40):
        LP.tickPlayer(rc, tst, tbuf)
    all_ = instrs19(rc)
    hops_ = [x_ for x_ in all_ if x_[1]]
    hang_ = [x_ for x_ in all_ if not x_[1]]
    side0 = math.hypot(hops_[0][0][0], hops_[0][0][2]) if hops_ else 0.0
    check(len(h0_) == 1 and len(hops_) == 1 and abs(hops_[0][0][1] - 15.0) < 1e-6 and abs(side0 - 22.0 * math.sqrt(0.5)) < 0.05 and len(hang_) == 5
          and all(x_[0][1] <= 0.0 and math.hypot(x_[0][0], x_[0][2]) <= 0.2 * side0 + 1e-3 for x_ in hang_) and TW.of(tst).orbs.containsKey(rf[1])
          and LP.STATES.get(cu) is None and sv(mc, STAM) == 5.0,
          "R19c ONE CAST END TO END (0.1.16 defaults, 45 degrees down): exactly ONE dash push (%s: up capped 15.56 -> 15, back 15.56 kept), the 5 hang "
          "Sets never up and at most 0.2 x the back speed, the re-launched orb's SPAWN = the burst record (no second leap), 40 more ticks add nothing, "
          "5 Stamina once: %s %s" % (hops_, hang_[:2], (len(h0_), len(hang_), TW.of(tst).orbs.containsKey(rf[1]), LP.STATES.get(cu) is None, sv(mc, STAM))))

    # R19d THE CAP (pure + on the stand-ins): TravMath.capUp; ArmoryTrav.upVy with the ground flag (MovementStates) and the jump speed
    cap19 = [round(float(TM.capUp(a_, b_, c_, d_)), 3) for a_, b_, c_, d_ in (
        (30.0, 15.0, 0.0, 0.0), (10.0, 15.0, 0.0, 0.0), (-5.0, 15.0, 11.8, 0.0), (30.0, 0.0, 11.8, 0.0), (22.0, 15.0, 11.8, 11.8),
        (22.0, 15.0, 11.8, 0.0), (22.0, 15.0, 11.8, 8.0), (5.0, 15.0, 11.8, 8.0), (22.0, 15.0, 11.8, -5.0), (22.0, 15.0, 11.8, float("nan")))]
    check(cap19 == [15.0, 10.0, -5.0, 30.0, 15.0, 9.261, 12.238, 8.0, 10.524, 15.0],
          "R19d (Skyy: 'a little too far, especially if i look down and jump'): capUp - 30 -> 15 on the ground, 10 stays, a downward push untouched, "
          "cap 0 = no cap; in mid-air the jump's rise counts (at its top 15 -> 9.26: the same top as from the ground; rising 8 -> 12.24; falling 5 -> "
          "10.52), a weak hop never cuts the jump's own rise (8 kept), an unknown speed = the plain cap: %s" % cap19)
    fresh19()
    ms19 = MSCc()
    mst19 = JClass("com.hypixel.hytale.protocol.MovementStates")()
    mst19.onGround = False
    ms19.setMovementStates(mst19)
    put(rc, MSCc.getComponentType(), ms19)
    up_air = [round(float(AT.upVy(tst, rc, 22.0, 15.0, 0.0)), 3), round(float(AT.upVy(tst, rc, 22.0, 0.0, 0.0)), 3)]
    mst19.onGround = True
    up_gnd = round(float(AT.upVy(tst, rc, 22.0, 15.0, 0.0)), 3)
    put(rc, MSCc.getComponentType(), None)
    up_none = round(float(AT.upVy(tst, rc, 22.0, 15.0, 0.0)), 3)
    # the same through the real leap (Leap.begin -> hopNow) looking straight down, mid-air at a jump's top; the bow leap keeps its 30 (no cap)
    fresh19()
    guards19(True, True)
    mst19.onGround = False
    put(rc, MSCc.getComponentType(), ms19)
    cast19(1951, pitch=-1.5707964)
    hj_ = [x_ for x_ in instrs19(rc) if x_[1]]
    bow19 = LP.hopNow(tbuf, rc, JArray(JDouble)([0.0, -1.0, 0.0]), 30.0, 0.0)
    put(rc, MSCc.getComponentType(), None)
    LP.STATES.clear()
    check(up_air == [9.261, 22.0] and up_gnd == 15.0 and up_none == 15.0 and len(hj_) == 1 and abs(hj_[0][0][1] - 9.2612) < 1e-3
          and bow19 is not None and abs(float(bow19[1]) - 30.0) < 1e-9,
          "R19d: ArmoryTrav.upVy - mid-air (MovementStates.onGround false, jump 11.8 = the engine default) 22 -> 9.26, cap 0 -> 22 untouched, on the "
          "ground / no movement states -> 15; a wand cast looking straight down at a jump's top pushes up 9.26 (one push); the bow leap's hopNow "
          "(maxUp 0) keeps 30: %s %s %s %s %s" % (up_air, up_gnd, up_none, hj_, None if bow19 is None else round(float(bow19[1]), 3)))
    # the report's numbers (g = the engine's 32 b/s2; jump 11.8 b/s = vanilla JumpForce, its top 2.18 blocks): up speed + height above the ground
    G19, JF19 = 32.0, 11.8
    def hop19(force, maxup, pitch_deg, jump):
        d_ = TM.hopVector(math.cos(math.radians(pitch_deg)), -math.sin(math.radians(pitch_deg)), 0.0, force, False)
        back_, up_ = -float(d_[0]), float(d_[1])
        pre_ = JF19 * JF19 / (2 * G19) if jump else 0.0          # cast at the top of a jump (vy 0, in the air)
        v_ = float(TM.capUp(up_, maxup, JF19 if jump else 0.0, 0.0)) if maxup > 0 else up_
        return round(back_, 2), round(v_, 2), round(pre_ + (v_ * v_ / (2 * G19) if v_ > 0 else 0.0), 2)
    tab19 = {}
    for lbl_, pd_, jp_ in (("flat", 0.0, False), ("45 down", 45.0, False), ("straight down", 90.0, False), ("straight down + jump", 90.0, True),
                           ("45 down + jump", 45.0, True)):
        tab19[lbl_] = {"0.1.15": hop19(30.0, 0.0, pd_, jp_), "0.1.16": hop19(22.0, 15.0, pd_, jp_)}
    check(tab19["straight down"]["0.1.15"][2] > 14.0 and tab19["straight down"]["0.1.16"][2] < 3.6 and tab19["straight down + jump"]["0.1.16"][2] < 3.6
          and tab19["straight down + jump"]["0.1.15"][2] > 16.0 and tab19["flat"]["0.1.16"][0] == 22.0 and tab19["45 down"]["0.1.16"][1] == 15.0,
          "R19d numbers: straight down 0.1.15 > 14 blocks up, 0.1.16 < 3.6; down + jump 0.1.15 > 16, 0.1.16 < 3.6 (a jump never adds); flat back 30 -> 22")
    print("R19d. hop numbers (back b/s, up b/s, blocks up above the ground; g 32, jump 11.8): %s" % json.dumps(tab19))

    # R19e THE ROWS: hop.force 22, hop.maxUp 15 (after hop.hangFall, clamps 0..50), the default file, armory:leap
    fresh19()
    Rows19 = JClass(PKG + "CfgRows")
    k19 = [str(k_) for k_ in Rows19.KEYS]
    d19 = dict(zip(k19, [str(d_) for d_ in Rows19.DEFS]))
    h19 = dict(zip(k19, [str(h_) for h_ in Rows19.HELPS]))
    pr19 = Props()
    pr19.setProperty("hop.maxUp", "99")
    ACfg.apply(pr19)
    c19a = float(ACfg.HOP_MAXUP)
    pr19.setProperty("hop.maxUp", "-3")
    ACfg.apply(pr19)
    c19b = float(ACfg.HOP_MAXUP)
    ACfg.useDefaults()
    dc19 = str(ACfg.DEF_CFG)
    lt19 = str(br.get("armory:leap"))
    check(d19.get("hop.force") == "22" and d19.get("hop.maxUp") == "15" and k19.index("hop.maxUp") == k19.index("hop.hangFall") + 1 and len(h19["hop.maxUp"]) <= 100
          and c19a == 50.0 and c19b == 0.0 and float(ACfg.HOP_FORCE) == 22.0 and float(ACfg.HOP_MAXUP) == 15.0 and "\nhop.force=22\n" in dc19
          and "\nhop.maxUp=15\n" in dc19 and str(ACfg.M16_MARK) in dc19 and str(ACfg.M13_MARK) in dc19
          and lt19.startswith("wand hold: hop 22.0 (up at most 15.0 b/s, a jump never adds), one hop per cast, hang 0.35 s"),
          "R19e: the rows - hop.force 22, hop.maxUp 15 right after hop.hangFall (help %d chars), the loader clamps 99 -> 50 / -3 -> 0, the default file "
          "has 22 + 15 + both markers (a fresh file is never migrated), armory:leap: %s" % (len(h19.get("hop.maxUp", "")), lt19[:110]))

    # R19f THE ONE-TIME UPDATE 30 -> 22 (PROJECT-RULES 4): the text step, then the real migrate016 on a scratch file
    MK16 = str(ACfg.M16_MARK)

    def upd16(t_):
        r_ = ACfg.m16Update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])
    u1 = upd16("a=1\nhop.force=30\nb=2\n")
    u2 = upd16("a=1\r\nhop.force = 30.0\r\n")
    u3 = upd16("hop.force=25\n")
    u4 = upd16("quick.life=20\n")
    u5 = upd16(u1[0])
    u6 = upd16("hop.force=22\n")
    check(u1 == ("a=1\n" + MK16 + "\nhop.force=22\nb=2\n", "hop.force 30 -> 22", [], ["hop.force", "30", "22"])
          and u2 == ("a=1\r\n" + MK16 + "\r\nhop.force = 22\r\n", "hop.force 30.0 -> 22", [], ["hop.force", "30.0", "22"])
          and u3[0] == MK16 + "\nhop.force=25\n" and u3[1] == "" and len(u3[2]) == 1 and "kept (custom) - the 0.1.16 default is 22" in u3[2][0]
          and u4 == ("quick.life=20\n" + MK16 + "\n", "", [], []) and u5 is None and u6 == (MK16 + "\nhop.force=22\n", "", [], []),
          "R19f (PROJECT-RULES 4): an untouched 30 (or 30.0) -> 22 (value text only, CRLF kept), a hand-set 25 KEPT + noted, no line = marker only "
          "(Skyy's live file has none: the default 22 applies), runs once: %s / %s / %s" % (u1, u2, u3))
    mdir16 = os.path.join(SCRATCH, "m16", "mods", "Skyy_SkyyArmory")
    shutil.rmtree(os.path.dirname(os.path.dirname(mdir16)), ignore_errors=True)
    os.makedirs(mdir16)
    mtxt16 = ("# SkyyArmory 0.1.15 test file\r\npart.trav=true\r\n" + str(ACfg.M13_MARK) + "\r\nhop.force=30\r\nquick.life=20\r\n").encode("latin-1")
    open(os.path.join(mdir16, "config.properties"), "wb").write(mtxt16)
    ACfg.DIR = Paths.get(mdir16)
    ACfg.FILE = ACfg.DIR.resolve("config.properties")
    mr16 = str(ACfg.migrate013())          # setup() order: 0.1.3 first (its marker is there - idle), then 0.1.16
    mr16a = str(ACfg.migrate016())
    af16 = open(os.path.join(mdir16, "config.properties"), "rb").read()
    hist16 = os.path.join(mdir16, "config-history")
    baks16 = sorted(f_ for f_ in os.listdir(hist16) if f_.endswith(".bak")) if os.path.isdir(hist16) else []
    log16 = open(os.path.join(mdir16, "config-changes.log"), "rb").read().decode("latin-1") if os.path.isfile(os.path.join(mdir16, "config-changes.log")) else ""
    mr16b = str(ACfg.migrate016())
    af16b = open(os.path.join(mdir16, "config.properties"), "rb").read()
    ACfg.load()
    hf16 = float(ACfg.HOP_FORCE)
    # an old 0.1.2 file (13, no marker): 13 -> 30 (0.1.3) -> 22 (0.1.16) in one start; a hand-set 26 survives both
    open(os.path.join(mdir16, "config.properties"), "wb").write(b"part.trav=true\nhop.force=13\n")
    ACfg.migrate013()
    ACfg.migrate016()
    old13 = open(os.path.join(mdir16, "config.properties"), "rb").read()
    open(os.path.join(mdir16, "config.properties"), "wb").write(b"part.trav=true\nhop.force=26\n")
    ACfg.migrate013()
    ACfg.migrate016()
    own26 = open(os.path.join(mdir16, "config.properties"), "rb").read()
    ACfg.DIR = None
    ACfg.FILE = None
    ACfg.useDefaults()
    check(mr16 == "" and af16 == upd16(mtxt16.decode("latin-1"))[0].encode("latin-1") and b"hop.force=22\r\n" in af16 and baks16
          and open(os.path.join(hist16, baks16[-1]), "rb").read() == mtxt16 and "\tSkyyArmory 0.1.16\t-\tupdate\thop.force\t30\t22\tok" in log16
          and "30 -> 22" in mr16a and mr16b == "" and af16b == af16 and hf16 == 22.0
          and b"\nhop.force=22\n" in old13 and b"\nhop.force=26\n" in own26,
          "R19f (the real ArmoryCfg.migrate016 on a scratch file): History copy = the old bytes, the Undo-able change-log line, CRLF kept, the second "
          "run idle (no churn), the loader reads 22; an old 13 goes 13 -> 30 -> 22 in one start, a hand-set 26 is kept: %s | %s" % (mr16a[:120], log16.strip()[-70:]))
    guards19(True, True)

    # R19g vs the 0.1.15 jar METHOD BY METHOD
    MN19, MO19 = methods_of(JAR), methods_of(OLD115)
    cmp19 = {}
    for c_ in sorted(set(MN19) | set(MO19)):
        if c_ not in MN19 or c_ not in MO19:
            cmp19[c_] = "only in " + ("0.1.16" if c_ in MN19 else "0.1.15")
            continue
        ch_ = sorted(k_ for k_ in set(MN19[c_][0]) | set(MO19[c_][0]) if MN19[c_][0].get(k_) != MO19[c_][0].get(k_))
        fd_ = sorted(set(MN19[c_][1]) ^ set(MO19[c_][1]))
        if ch_ or fd_:
            cmp19[c_] = {"methods": [k_.split("(")[0] for k_ in ch_], "fields": [f_.split(":")[0] for f_ in fd_]}
    plan19 = {"ArmoryTrav": ({"dupHop", "markHop", "jumpOf", "grounded", "upVy", "hop", "added"}, {"LASTHOP", "DUP_MS", "DUPS"}),
              "Leap": ({"hopNow", "begin", "onWandOrb", "fire", "ownShot"}, {"REFIRE_T", "REFIRE_P", "REFIRE_MS", "DUPES", "REFIRE_SEEN", "HOP_LOGGED"}),
              "TravMath": ({"capUp"}, set()),
              "ArmoryCfg": ({"m16Is", "m16Update", "m16Log", "migrate016", "load", "apply", "leapText", "useDefaults", "reloadAll"},
                            {"HOP_MAXUP", "M16_KEY", "M16_OLD", "M16_NEW", "M16_MARK", "M16_MARK_ID", "M16_WHO", "M16_LAST"}),
              "SkyyArmoryPlugin": ({"setup", "shutdown"}, set())}
    bad19 = {}
    for c_, v_ in cmp19.items():
        if c_ in plan19 and isinstance(v_, dict) and set(v_["methods"]) <= plan19[c_][0] and set(v_["fields"]) <= plan19[c_][1]:
            continue
        bad19[c_] = v_
    check(not bad19 and "hop" in cmp19.get("ArmoryTrav", {}).get("methods", []) and "onWandOrb" in cmp19.get("Leap", {}).get("methods", [])
          and "capUp" in cmp19.get("TravMath", {}).get("methods", []) and "migrate016" in cmp19.get("ArmoryCfg", {}).get("methods", []),
          "R19g: 0.1.15 -> 0.1.16 METHOD BY METHOD - only the planned methods / fields differ (ArmoryTrav hop guard + cap, Leap one hop per cast + "
          "the cap, TravMath.capUp, ArmoryCfg the row + migrate016, the plugin's setup / shutdown): %s" % json.dumps(bad19)[:1500])
    print("R19g. vs 0.1.15 method by method: %s" % json.dumps(cmp19)[:1500])
    ACfg.useDefaults()
    TW.ALL.clear()
    reset_buf()
    LP.STATES.clear()
    print("R19. 0.1.16 wand hop: no ApplyForce in any wand chain, the two double-hop causes reproduced (MUTANTS) and fixed (1 push per cast), "
          "a real second cast + the hop job, one cast end to end, the cap (pure + stand-ins + the leap), the rows, the 30 -> 22 update, the 0.1.15 compare")
'''
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R19 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s" % os.path.relpath(TDST, ROOT))
