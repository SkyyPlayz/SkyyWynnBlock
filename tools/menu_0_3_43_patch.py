"""Derive SkyyMenu/build_skyymenu_0.3.43.py from the LIVE SkyyMenu 0.3.42 (python tools/menu_0_3_43_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_42_patch.py -> 0.3.42 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.43. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.42 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.43.py is its own file.

0.3.43 (2026-10-22) = THE 0.3.42 REVIEW FOLLOW-UP (lean round): Stats page element units + two Walk key (Left Alt) safeguards.
  Skyy (2026-10-22): "they were able to tie the menu to Left alt" + "just pressing Lalt is fine..." (0.3.42 deployed); "keep going down the
  list. dont stop until the entire list is done".
  1. STATS PAGE % ON THE ELEMENT LINES: the Combat list's "Elemental Damage" row (Earth / Thunder / Water / Fire / Air) and "Raw Elemental
     Damage" row (Raw Thunder / Raw Water / Raw Elemental) show their total and every part with "%" - the SET SkyyGear (0.3.35+) marks
     these 8 stats ("w", "%"): "+N % of the hit". ST_ELEM / ST_RAW carry a unit like ST_GEAR; StatsCalc.ELEM_U / RAW_U; groupRow takes
     the units (the total gets the group's unit when all its parts share one). The build cross-check against the SET SkyyGear stat table now
     checks the unit of EVERY row the page shows (0.3.42: ST_GEAR only - the 8 element keys were checked for LIVE, not for the unit).
  2. WALK COOLDOWN STAMPED ONLY ON A REAL OPEN: 0.3.42 stamped the per-player Walk cooldown (state s[4]) in walkStep at every rising edge,
     so an Alt press ignored over an open page (or refused) still blocked the next press for 400 ms. Now walkStep only CHECKS the cooldown;
     HotkeyOpen stamps s[4] (MenuHotkey.opened) right after it opened the Menu by the Walk key. HotkeyOpen gets the player's state array
     (new constructor HotkeyOpen(pr, walk, s)) and re-checks the cooldown on the world thread (a second open queued before the first ran -
     a very fast tap whose release fell back, below - is dropped silently, WALK_COOLED + 1).
  3. TOGGLE-WALK SAFEGUARD: with a TOGGLE walk key one press turns walking on (rising edge) and the next turns it off (FALLING edge). If a
     press was ignored (a page open) walking stayed on, so the player's next press only turned it off and opened nothing. Now the state
     long[6] carries s[5] = "a Walk press is owed an open": set at every rising edge (Server Setup row on), cleared by any open through
     HotkeyOpen (MenuHotkey.opened); on the FALLING edge an owed press fires ONE fallback open (s[5] cleared first: at most once per press)
     with the same cooldown and the same world-thread checks (page open = ignored silently, window / dead / profile busy = refused, the
     player's switch). Held Walk stays exactly 0.3.42: the press opens, the release finds nothing owed (the open cleared it) - one open per
     press, no flicker; a release while the press's own open is still queued fires a fallback that the cooldown / open page drops silently.
     Row off (menu.walkKey false) = nothing owed. Limit: a pure toggle key after a SUCCESSFUL open still needs two presses for the next open
     (the release-press is indistinguishable from a held key's release - the safeguard is exactly the "ignored press" case).
  No new command, permission, page, setting, config line, bridge key or saved data. ROLLBACK to 0.3.42: safe.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.42.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.43.py"))
assert P.has('VERSION = "0.3.42"\n') and P.has("tools/menu_0_3_42_patch.py") and P.has("walkStep") and not P.has("WALK_COOLED"), \
    "not the generated SkyyMenu 0.3.42 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.43: the 0.3.42 review follow-up (notes: tools/menu_0_3_43_patch.py): the Stats page's element + raw element lines show "%" (unit
       cross-check on every shown SkyyGear stat); the Walk cooldown is stamped only when the Menu really opened; a Walk press owed an open
       (ignored over a page) opens on the falling edge too (toggle walk keys), at most once per press.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.43.py.
''')
P.rep('VERSION = "0.3.42"\n', 'VERSION = "0.3.43"\n')

# ---- 1: the element lines carry SkyyGear's unit (0.3.35+: "%"), the cross-check covers every shown row's unit
P.rep('''ST_ELEM = [("fEarth", "Earth"), ("fThunder", "Thunder"), ("fWater", "Water"), ("fFire", "Fire"), ("fAir", "Air")]
ST_RAW = [("rThunder", "Thunder"), ("rWater", "Water"), ("rElem", "Elemental")]
''', '''# 0.3.43: (key, short label, unit) - SkyyGear 0.3.35+ marks the 8 element lines ("w", "%"): "+N % of the hit"
ST_ELEM = [("fEarth", "Earth", "%"), ("fThunder", "Thunder", "%"), ("fWater", "Water", "%"), ("fFire", "Fire", "%"), ("fAir", "Air", "%")]
ST_RAW = [("rThunder", "Thunder", "%"), ("rWater", "Water", "%"), ("rElem", "Elemental", "%")]
assert len(set(u for _k, _s, u in ST_ELEM)) == 1 and len(set(u for _k, _s, u in ST_RAW)) == 1, "0.3.43: one unit per element group (the total row)"
''')
P.rep('''    for _k, _lab, _short, _u in ST_GEAR + [(k, l, l, "") for k, l in ST_ELEM + ST_RAW]:
        assert _k in _grows, "SkyyGear %s has no stat %s any more" % (_gear_ver, _k)
        assert _grows[_k][2] == "1", "SkyyGear %s: %s is not a LIVE stat (the Stats page hides planned stats)" % (_gear_ver, _k)
        if _k in [g[0] for g in ST_GEAR]:
            assert _grows[_k][1] == _u, "SkyyGear %s: %s unit %r, the page says %r" % (_gear_ver, _k, _grows[_k][1], _u)
''', '''    for _k, _lab, _short, _u in ST_GEAR + [(k, l, l, u) for k, l, u in ST_ELEM + ST_RAW]:
        assert _k in _grows, "SkyyGear %s has no stat %s any more" % (_gear_ver, _k)
        assert _grows[_k][2] == "1", "SkyyGear %s: %s is not a LIVE stat (the Stats page hides planned stats)" % (_gear_ver, _k)
        assert _grows[_k][1] == _u, "SkyyGear %s: %s unit %r, the page says %r" % (_gear_ver, _k, _grows[_k][1], _u)   # 0.3.43: every shown row
''')
P.rep('''F(scl, "public static final String[] RAW_S = %s;" % jarr([g[1] for g in ST_RAW]))
''', '''F(scl, "public static final String[] RAW_S = %s;" % jarr([g[1] for g in ST_RAW]))
F(scl, "public static final String[] ELEM_U = %s;" % jarr([g[2] for g in ST_ELEM]))   # 0.3.43
F(scl, "public static final String[] RAW_U = %s;" % jarr([g[2] for g in ST_RAW]))     # 0.3.43
''')
P.rep('''public static void groupRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, String[] keys, String[] shorts, String name, boolean always) {
  double t = 0.0;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < keys.length; k++) {
    double v = get(g, keys[k]) + get(a, keys[k]);
    t = t + v;
    part(sb, shorts[k], v, "");
  }
  if (Math.abs(t) < 0.05 && !always) return;
  if (sb.length() == 0) sb.append("none - it comes from weapons");
  add(rows, name, num(t), sb.toString());
}""")''', '''public static void groupRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, String[] keys, String[] shorts, String[] units, String name, boolean always) {
  double t = 0.0;
  StringBuilder sb = new StringBuilder();
  String tu = units != null && units.length > 0 && units[0] != null ? units[0] : "";
  for (int k = 0; k < keys.length; k++) {
    double v = get(g, keys[k]) + get(a, keys[k]);
    t = t + v;
    String u = units != null && k < units.length && units[k] != null ? units[k] : "";
    if (!u.equals(tu)) tu = "";
    part(sb, shorts[k], v, u);
  }
  if (Math.abs(t) < 0.05 && !always) return;
  if (sb.length() == 0) sb.append("none - it comes from weapons");
  add(rows, name, num(t) + tu, sb.toString());
}""")''')
P.rep('''  groupRow(rows, g, a, ELEM_K, ELEM_S, "Elemental Damage", true);
  groupRow(rows, g, a, RAW_K, RAW_S, "Raw Elemental Damage", false);''', '''  groupRow(rows, g, a, ELEM_K, ELEM_S, ELEM_U, "Elemental Damage", true);      // 0.3.43: with SkyyGear's "%"
  groupRow(rows, g, a, RAW_K, RAW_S, RAW_U, "Raw Elemental Damage", false);''')

# ---- 2 + 3: the Walk edge - cooldown checked here, stamped by a real open; the falling-edge fallback for an owed press
P.rep('''# over a window, while dead or profile-busy. forget() (MenuQuit) drops a leaving player's state at once.
''', '''# over a window, while dead or profile-busy. forget() (MenuQuit) drops a leaving player's state at once.
# 0.3.43: long[6] - [5] = a Walk press is owed an open (set at each rising edge, cleared by any open through HotkeyOpen = opened()). walkStep
# only CHECKS the cooldown (cooling()); opened() stamps [4] when the Walk key really opened the Menu. A FALLING edge with an owed press fires
# one fallback open ([5] cleared first) - the toggle-walk case: a press ignored over a page left walking on, the next press turns it off.
''')
P.rep('''public static boolean walkStep(long[] s, boolean walk, long now) {
  boolean was = s[3] != 0L;
  s[3] = walk ? 1L : 0L;
  if (!walk || was) return false;
  if (!@PKG@.MenuCfg.WALK_KEY) return false;
  long cd = @PKG@.MenuCfg.WALK_COOLDOWN_MS;
  if (s[4] != 0L && now >= s[4] && now - s[4] < cd) return false;
  s[4] = now;
  return true;
}""")''', '''public static boolean cooling(long[] s, long now) {
  if (s == null || s.length < 5 || s[4] == 0L || now < s[4]) return false;
  return now - s[4] < @PKG@.MenuCfg.WALK_COOLDOWN_MS;
}""")
M(mhk, r"""
public static void opened(long[] s, boolean walk, long now) {
  if (s == null || s.length < 6) return;
  s[5] = 0L;
  if (walk) s[4] = now;
}""")
M(mhk, r"""
public static boolean walkStep(long[] s, boolean walk, long now) {
  boolean was = s[3] != 0L;
  s[3] = walk ? 1L : 0L;
  if (walk == was) return false;
  if (!@PKG@.MenuCfg.WALK_KEY) { s[5] = 0L; return false; }
  if (walk) s[5] = 1L;
  else {
    if (s[5] == 0L) return false;
    s[5] = 0L;
  }
  return !cooling(s, now);
}""")''')
P.rep('''      s = new long[5];
      ST.put(ref, s);''', '''      s = new long[6];
      ST.put(ref, s);''')
P.rep('''    w.execute(new @PKG@.HotkeyOpen(pr, walkFire && !crouchFire));''', '''    w.execute(new @PKG@.HotkeyOpen(pr, walkFire && !crouchFire, s));''')
P.rep('''F(hko, "public static volatile long WALK_SKIPPED = 0L;")    # 0.3.42: a page was open - ignored silently
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; this.walk = false; }")
C(hko, "public HotkeyOpen(@PR@ pr, boolean walk) { this.pr = pr; this.walk = walk; }")''', '''F(hko, "public static volatile long WALK_SKIPPED = 0L;")    # 0.3.42: a page was open - ignored silently
F(hko, "public long[] hs;")                                 # 0.3.43: the player's MenuHotkey state (null = not from the tick)
F(hko, "public static volatile long WALK_COOLED = 0L;")     # 0.3.43: a queued Walk open inside the cooldown - dropped silently
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; this.walk = false; this.hs = null; }")
C(hko, "public HotkeyOpen(@PR@ pr, boolean walk) { this.pr = pr; this.walk = walk; this.hs = null; }")
C(hko, "public HotkeyOpen(@PR@ pr, boolean walk, long[] hs) { this.pr = pr; this.walk = walk; this.hs = hs; }")''')
P.rep('''    if (this.walk) { if (!wantedWalk(this.pr.getUuid())) return; }
    else if (!wanted(this.pr.getUuid())) return;''', '''    if (this.walk) { if (!wantedWalk(this.pr.getUuid())) return; }
    else if (!wanted(this.pr.getUuid())) return;
    if (this.walk && @PKG@.MenuHotkey.cooling(this.hs, System.currentTimeMillis())) { WALK_COOLED = WALK_COOLED + 1L; return; }   // 0.3.43''')
P.rep('''    if (this.walk) WALK_OPENED = WALK_OPENED + 1L;''', '''    if (this.walk) WALK_OPENED = WALK_OPENED + 1L;
    @PKG@.MenuHotkey.opened(this.hs, this.walk, System.currentTimeMillis());   // 0.3.43: the cooldown starts at a REAL open; nothing owed''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.43 adds no system / command"
P.finish()
