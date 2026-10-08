"""Derive SkyyProfiles/build_skyyprofiles_0.1.7.py from the LIVE 0.1.6 (build_skyyprofiles_0.1.6.py = the tools/deploy_set.py SET pin).
Run:  python tools/profiles_0_1_7_patch.py   then   python SkyyProfiles/build_skyyprofiles_0.1.7.py   (never --deploy)
Patch chain: 0.1 -> 0.1.1 (copy + edit) -> profiles_0_1_2_patch.py -> ... -> profiles_0_1_6_patch.py -> 0.1.6 -> THIS patch -> 0.1.7.
Edit THIS file, never the generated build script. Harness: python SkyyProfiles/test_skyyprofiles_0.1.7.py.

0.1.7 = TWO FIXES FROM SKYY'S 2026-10-08 TESTS (docs/answered/ui.md + social.md, 2026-10-08 lines):
  1. THE BIG SWITCH CONFIRMS (Skyy: "the big switch button should work to confirm"). After SWITCH on a profile card that card's button is
     the big highlighted SWITCH and the Confirm / Cancel bar shows at the bottom. A SECOND click on that highlighted SWITCH (pfsw<id> of
     the profile whose switch question is open) now confirms exactly like the bottom CONFIRM (pfyes): both go through the new
     ProfilePage.confirmSwitch (the 0.1.6 pfyes code, moved, unchanged). The bottom bar stays. A SWITCH click on ANOTHER card still only
     moves the question there. DELETE is unchanged: pfdel<id> only asks, only the bottom Delete (pfdelyes) deletes (no double-click
     delete). The page drawing (every element, binding and text) is 0.1.6's.
  2. HEALTH PER PROFILE (Skyy: "damage from the monk carried over to a new assassin profile."). The engine keeps Health on the player
     entity, so a switch carried the old profile's damage into the new one. Now:
     - SWITCH-OUT: the leaving profile's Health RATIO (current / max, 4 decimals, "1" = full) is saved in the players file as
       p.<id>.hp, in the same atomic players-file commit as the switch (ProfStore.setActive). Read on the world thread before the
       inventory swap (ProfHp.leaving). Unreadable stats = no value (= full later).
     - SWITCH-IN: the target's p.<id>.hp is restored as a RATIO of the new maximum (ProfHp.arrive, right after the commit + publish, on
       the world thread). A profile WITHOUT a value - a NEW profile, or any profile from before 0.1.7 - starts FULL: Health, Stamina and
       Mana (each to its own maximum). Never 0, never dead (at least 1 Health), never above the max.
     - SETTLE WINDOW: other mods change the maximum AFTER a switch (SkyyClasses / SkyySkills / SkyyAccessories / SkyyTrees modifiers in
       their 1 s ticks after profile:epoch changes, SkyyGear's armor lock, the engine's armor Recalculate after the inventory swap, the
       /island world transfer). EntityStatValue.putModifier clamps the current value but never scales it (VERIFIED bytecode, SkyyGear
       0.2.9 engine review 1), so a new profile would sit at 100 / 124 once a +24 modifier lands. ProfHp keeps the restored RATIO while
       the maximum settles: every 100 ms on the player's world thread (it follows the player across the /island transfer) it watches
       the max; when the max changes it rewrites the value to ratio x new max. Between max changes it only tracks the player's own
       ratio (damage, regen, drinking a potion all count - the hold never refills a bar that was used). On a max-change step a value
       that went DOWN keeps the last ratio (a clamp under a modifier swap - remove + put - cannot be told from a hit; at worst one
       100 ms window of damage is forgiven, only in the seconds after a switch). It ends when the max has not
       moved for 4 s (at least 8 s after the switch, the 4 s restarting on a world change) or after 45 s, or when the player dies /
       leaves / switches again. Stamina + Mana are held the same way only for a profile without a saved value (start full).
     - SAVED DATA: one new per-profile key p.<id>.hp (players/<uuid>.properties). Absent = full: nothing is migrated, no file is
       rewritten at start (PROJECT-RULES 4: no one-time migration is needed - no old value exists to convert). Delete / archive /
       restore carry it with the other p.<id>.* keys (they copy by prefix). No item, coin or inventory path changes.
     - NOT saved per profile: Stamina / Mana of an existing profile (they refill in seconds), effects, hunger-like stats.
  KEEP: the config kit history goes from KEEP=20 to 10 (AGENT-BRIEF: kit default 10 since 2026-10-05). No command / binding / system /
  bridge key added or removed; the SKYY CARD block is untouched.
  SERVER SETUP (review fix): Profiles > Switching > "Each profile keeps its own Health" = config healthPerProfile (bool, default true,
  live; field ProfCfg.HP_PER_PROFILE). Off = 0.1.6 behaviour (Health carries over; saved p.<id>.hp values are kept, not removed; a
  running hold stops at its next step). A file without the line runs with true; nothing is rewritten at start. The hold timings are
  fixed on purpose (they only cover the other mods' settle time).
"""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.6.py")
dst = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.7.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.6"' in s and "GENERATED by tools/profiles_0_1_6_patch.py from build_skyyprofiles_0.1.5.py" in s, \
    "build_skyyprofiles_0.1.6.py is not the live 0.1.6"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
SYS0 = [ln for ln in s.split(LF) if "registerSystem(" in ln]
CARD_START = "# =====================================================================================================================\n# SKYY CARD"
CARD_END = "# ======================================================================= (end of the shared SKYY CARD block)"
CARD_SHA = "bf659e0208b537a81ac8758d909f81976f03069816ea9dddb300f843a7eaa028"   # = profiles_0_1_4 .. 0_1_6 / classes_0_1_9..14 patches


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


_card = block(CARD_START, CARD_END) + CARD_END
assert hashlib.sha256(_card.encode("utf8")).hexdigest() == CARD_SHA, "the SKYY CARD block is not the shared one"
_list_view = block("PF_BUILD_LIST = r\"\"\"", "# 0.1.5: the delete / restore / close clicks")   # the page drawing - must stay 0.1.6's

# ================================================================================================ docstring, version
rep('''"""SkyyProfiles 0.1.6 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.6.py          -> SkyyProfiles/SkyyProfiles-0.1.6.jar''',
    '''"""SkyyProfiles 0.1.7 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.7.py          -> SkyyProfiles/SkyyProfiles-0.1.7.jar''')
rep('''GENERATED by tools/profiles_0_1_6_patch.py from build_skyyprofiles_0.1.5.py (generated by tools/profiles_0_1_5_patch.py from 0.1.4,''',
    '''GENERATED by tools/profiles_0_1_7_patch.py from build_skyyprofiles_0.1.6.py (generated by tools/profiles_0_1_6_patch.py from 0.1.5,
generated by tools/profiles_0_1_5_patch.py from 0.1.4,''')
rep('''Harness: python SkyyProfiles/test_skyyprofiles_0.1.6.py
''', '''Harness: python SkyyProfiles/test_skyyprofiles_0.1.7.py

0.1.7 (2026-10-08, Skyy's tests): (1) a second click on the highlighted SWITCH of the card whose switch question is open confirms the
  switch like the bottom CONFIRM (ProfilePage.confirmSwitch; DELETE still needs the bottom Delete). (2) Health per profile: the leaving
  profile's Health ratio is saved as p.<id>.hp in the switch commit; the target's ratio is restored (no value = a new / pre-0.1.7
  profile = full Health, Stamina and Mana) and held while other mods' max modifiers settle (ProfHp, world thread, <= 45 s). Config kit
  KEEP 20 -> 10. Full notes in tools/profiles_0_1_7_patch.py.
''')
rep('VERSION = "0.1.6"', 'VERSION = "0.1.7"')
rep('RELOAD="ProfCfg.load", KEEP=20,', 'RELOAD="ProfCfg.load", KEEP=10,')

# ================================================================================================ Server Setup row (review fix, LOW)
# PROJECT-RULES 4 "Everything a server owner might change is editable in game": Server Setup > Profiles > Switching gets the on/off
# switch healthPerProfile (bool, default true, live; field ProfCfg.HP_PER_PROFILE). OFF = 0.1.6 behaviour: Health carries over a switch,
# nothing is restored or held, and the saved p.<id>.hp values are left as they are (not removed). A config.properties without the line
# (every file from before 0.1.7, Skyy's included) runs with true; nothing is rewritten at start; the kit appends the line the first
# time it is changed in game (the 0.1.5 deleteUndoHours precedent). The hold timings (ProfHp STEP / MIN / CALM / MAX_MS) stay fixed on
# purpose: they only cover how long the other mods take to settle their max modifiers - nothing an owner tunes.
rep('''F(cfg, "public static volatile String KEEP = %s;" % jstr(DEF_KEEP))
''', '''F(cfg, "public static volatile String KEEP = %s;" % jstr(DEF_KEEP))
F(cfg, "public static volatile boolean HP_PER_PROFILE = true;")    # 0.1.7: healthPerProfile (each profile keeps its own Health)
''')
rep('''need(CFG_LINES[-1] == "deleteUndoHours=%d" % DEF_UNDO_H''', '''CFG_LINES_016 = list(CFG_LINES)
CFG_LINES = CFG_LINES + [
    # 0.1.7: Health per profile (a file without these lines - every 0.1.1-0.1.6 file - runs with true)
    "# healthPerProfile = true: a switch saves the leaving profile's Health and restores the other profile's own (a new profile starts",
    "#   full). false: Health carries over a switch (as before 0.1.7).",
    "healthPerProfile=true",
]
need(CFG_LINES_016[-1] == "deleteUndoHours=%d" % DEF_UNDO_H''')
rep('''     "field:ProfCfg.ISLAND_ON_SWITCH@config.properties:islandOnSwitch"),
''', '''     "field:ProfCfg.ISLAND_ON_SWITCH@config.properties:islandOnSwitch"),
    # 0.1.7 (Skyy 2026-10-08 "damage from the monk carried over to a new assassin profile."): live - a switch reads it at the time
    ("healthPerProfile", "Each profile keeps its own Health", "switching", "bool", "true", "", "", "", "", "live",
     "On: each profile keeps its own Health; a new profile starts full. Off: Health carries over a switch.",
     "field:ProfCfg.HP_PER_PROFILE@config.properties:healthPerProfile"),
''')
rep('''" deleteUndoHours=" + (UNDO_MS / 3600000L);''', '''" deleteUndoHours=" + (UNDO_MS / 3600000L)
    + " healthPerProfile=" + HP_PER_PROFILE;''')
rep('''    PER_PROFILE_BACKPACK = bool(p, "perProfileBackpack", PER_PROFILE_BACKPACK);
''', '''    PER_PROFILE_BACKPACK = bool(p, "perProfileBackpack", PER_PROFILE_BACKPACK);
    HP_PER_PROFILE = bool(p, "healthPerProfile", HP_PER_PROFILE);
''')

# ================================================================================================ engine tokens + probes
rep('''    "TR":    "com.hypixel.hytale.server.core.modules.time.TimeResource",
}''', '''    "TR":    "com.hypixel.hytale.server.core.modules.time.TimeResource",
    "ESM":   "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",                    # 0.1.7: Health per profile
    "ESV":   "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST":   "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
}''')
rep('''             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
    B.probe(pool, c, m)''', '''             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"),
             # 0.1.7: Health per profile (ProfHp)
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESM"], "setStatValue"), (T["ESV"], "get"), (T["ESV"], "getMax"),
             (T["DST"], "getHealth"), (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["REF"], "isValid"), (T["REF"], "getStore")):
    B.probe(pool, c, m)''')

# ================================================================================================ the new class
rep('''sw   = pool.makeClass(PKG + ".ProfSwitch")
''', '''sw   = pool.makeClass(PKG + ".ProfSwitch")
hp   = pool.makeClass(PKG + ".ProfHp")                               # 0.1.7: Health per profile (save on switch-out, restore + settle)
''')
rep('''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, sw, clr, dlt,''', '''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, hp, sw, clr, dlt,''')

# ================================================================================================ ProfStore.setActive: the leaving ratio
rep('''M(sto, r"""
public static synchronized boolean setActive(java.util.UUID u, String from, String to) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!live(q, to)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("active", to);
  if (from != null && exists(q, from) && !from.equals(to)) {
    q.setProperty("p." + from + ".lastPlayed", now);
    q.setProperty("p." + from + ".inv", "1");
  }''', '''# 0.1.7: hp = the leaving profile's Health ratio ("0.5234", "1" = full; ProfHp.leaving) -> p.<from>.hp in the same commit; null (stats
# unreadable) removes an older value (= full at the next switch-in); "" (healthPerProfile off) leaves a saved value as it is. The
# 3-argument form (the join repair: no leaving profile) = null.
M(sto, r"""
public static synchronized boolean setActive(java.util.UUID u, String from, String to, String hp) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!live(q, to)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("active", to);
  if (from != null && exists(q, from) && !from.equals(to)) {
    q.setProperty("p." + from + ".lastPlayed", now);
    q.setProperty("p." + from + ".inv", "1");
    if (hp == null) q.remove("p." + from + ".hp"); else if (hp.length() > 0) q.setProperty("p." + from + ".hp", hp);
  }''')
rep('''  q.setProperty("switches", String.valueOf(num(q, "switches") + 1L));
  return commit(u, q);
}""")
''', '''  q.setProperty("switches", String.valueOf(num(q, "switches") + 1L));
  return commit(u, q);
}""")
M(sto, r"""
public static boolean setActive(java.util.UUID u, String from, String to) {
  return setActive(u, from, to, null);
}""")
''')

# ================================================================================================ ProfHp
HP_JAVA = r'''
# ================= ProfHp (0.1.7): Health per profile - Skyy 2026-10-08 "damage from the monk carried over to a new assassin profile." ==
# SWITCH-OUT: leaving() reads the player's Health ratio (world thread, before the inventory swap) -> ProfStore.setActive writes it as
# p.<from>.hp in the switch commit. SWITCH-IN: arrive() (world thread, after the commit + publish) restores the target's ratio of the
# CURRENT max at once and then HOLDS that ratio while the max settles: other mods put their max modifiers in their 1 s ticks after the
# epoch change, SkyyGear's armor lock and the engine's armor Recalculate follow the inventory swap, and /island moves the player to
# another world. EntityStatValue.putModifier clamps the current value but never scales it (VERIFIED bytecode, SkyyGear 0.2.9 engine
# review 1) - without the hold a new profile would show 100 / 124 once a +24 modifier lands. The hold runs every STEP_MS on the
# player's own world thread (it hops worlds like RecoverTask), rewrites a held stat ONLY when its max changed (ratio x new max: damage,
# regen and potions between two max changes are the player's own and are tracked, never refilled), and ends when no held max moved
# for CALM_MS (at least MIN_MS after the switch; the calm restarts on a world change), after MAX_MS, or when the player dies, leaves
# or switches again (HOLD: one hold per player, a newer one replaces it). No saved value (a NEW profile or one from before 0.1.7) =
# full Health, Stamina and Mana (each held at full the same way); a saved value = that Health ratio, Stamina / Mana untouched.
# Never 0 Health, never revives (a dead player stops the hold), never above the max.
# s[] of one held stat = { held 1/0, ratio, last max seen, first step done 1/0, max changed this step 1/0, last value seen / written }
hp.addInterface(pool.get("java.lang.Runnable"))
F(hp, "public static final java.util.concurrent.ConcurrentHashMap HOLD = new java.util.concurrent.ConcurrentHashMap();")
F(hp, "public static long STEP_MS = 100L;")
F(hp, "public static long MIN_MS = 8000L;")
F(hp, "public static long CALM_MS = 4000L;")
F(hp, "public static long MAX_MS = 45000L;")
F(hp, "public static boolean WARNED = false;")
F(hp, "public @PR@ pr;")
F(hp, "public java.util.UUID u;")
F(hp, "public float[] sh;")
F(hp, "public float[] ss;")
F(hp, "public float[] sm;")
F(hp, "public long start;")
F(hp, "public long calm;")
F(hp, "public boolean onWorld;")
F(hp, "public boolean moved;")
F(hp, "public java.util.UUID hopWorld;")
F(hp, "public java.util.UUID lastWorld;")
C(hp, r"""
public ProfHp(@PR@ pr, float ratio, boolean fill) {
  this.pr = pr;
  this.u = pr == null ? null : pr.getUuid();
  float f = fill ? 1.0f : 0.0f;
  this.sh = new float[] { 1.0f, ratio, 0.0f, 0.0f, 0.0f, 0.0f };
  this.ss = new float[] { f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f };
  this.sm = new float[] { f, 1.0f, 0.0f, 0.0f, 0.0f, 0.0f };
  this.start = System.currentTimeMillis();
  this.calm = this.start;
  this.onWorld = false;
  this.moved = false;
  this.hopWorld = null;
  this.lastWorld = null;
}""")
M(hp, r"""
public static void warnOnce(String msg) {
  if (WARNED) return;
  WARNED = true;
  @PKG@.ProfCfg.warn(msg);
}""")
M(hp, r"""
public static float clamp01(float x) {
  if (!(x > 0.0f)) return 0.0f;
  return x > 1.0f ? 1.0f : x;
}""")
# a saved p.<id>.hp -> the ratio to restore; missing / unreadable / <= 0 / NaN = full (1), above 1 = 1
M(hp, r"""
public static float parse(String v) {
  if (v == null) return 1.0f;
  try {
    float f = Float.parseFloat(v.trim());
    if (f > 1.0f) return 1.0f;
    if (f > 0.0f) return f;
  } catch (Throwable t) { }
  return 1.0f;
}""")
# the ratio -> its p.<id>.hp text: "1" (full) or "0.dddd" (never "0.0000": at least 0.0001); null for nothing to save (<= 0, NaN)
M(hp, r"""
public static String text(float r) {
  if (!(r > 0.0f)) return null;
  if (r >= 1.0f) return "1";
  long k = Math.round((double) r * 10000.0);
  if (k < 1L) k = 1L;
  if (k >= 10000L) return "1";
  String d = String.valueOf(k);
  while (d.length() < 4) d = "0" + d;
  return "0." + d;
}""")
# the ratio a stat really has now. Same max as last step: cur / max (damage, regen, potions: the player's own). The max moved: the engine
# clamps the value under a smaller max and never scales it, and between two steps the max may have dropped and come back (a modifier
# swapped: remove, then put - SkyyClasses' class Mana, a 0 max in between) - so a value that went DOWN on a max-change step cannot be
# told apart from a clamp: the last ratio is kept (at worst one 100 ms window of damage is forgiven, only in the first seconds after a
# switch). A value that went UP keeps its gain: cur / last max.
M(hp, r"""
public static float ratioNow(float cur, float max, float lastMax, float lastR, float lastCur) {
  if (!(max > 0.0f)) return clamp01(lastR);
  if (!(lastMax > 0.0f) || Math.abs(max - lastMax) <= 0.001f) return clamp01(cur / max);
  if (cur > lastCur + 0.001f) return clamp01(cur / lastMax);
  return clamp01(lastR);
}""")
# one step of one held stat (pure - the harness drives it with a stand-in stat map): returns the value to write, or -1 = leave it
M(hp, r"""
public static float step(float cur, float max, float[] s, float floor) {
  s[4] = 0.0f;
  if (s[0] < 0.5f || !(max > 0.0f)) return -1.0f;
  boolean first = s[3] < 0.5f;
  float r = first ? clamp01(s[1]) : ratioNow(cur, max, s[2], s[1], s[5]);
  boolean changed = first || (s[2] > 0.0f && Math.abs(max - s[2]) > 0.001f);
  s[1] = r;
  s[2] = max;
  s[3] = 1.0f;
  s[5] = cur;
  if (!changed) return -1.0f;
  s[4] = 1.0f;
  float want = r * max;
  if (want < floor) want = floor;
  if (want > max) want = max;
  if (Math.abs(want - cur) <= 0.001f) return -1.0f;
  s[5] = want;
  return want;
}""")
M(hp, r"""
public boolean one(@ESM@ m, int idx, float[] s, float floor) {
  if (idx < 0 || s[0] < 0.5f) return false;
  @ESV@ v = m.get(idx);
  if (v == null) return false;
  float w = step(v.get(), v.getMax(), s, floor);
  if (s[4] > 0.5f) this.moved = true;
  if (w < 0.0f) return false;
  m.setStatValue(idx, w);
  return true;
}""")
# one hold step on a stat map; false = stop (the player is dead: never revive)
M(hp, r"""
public boolean applyMap(@ESM@ m) {
  this.moved = false;
  if (m == null) return true;
  int hi = @DST@.getHealth();
  @ESV@ hv = hi < 0 ? null : m.get(hi);
  if (hv != null && !(hv.get() > 0.0f)) return false;
  one(m, hi, this.sh, 1.0f);
  one(m, @DST@.getStamina(), this.ss, 0.0f);
  one(m, @DST@.getMana(), this.sm, 0.0f);
  return true;
}""")
M(hp, r"""
public boolean apply(@ST@ st, @REF@ ref) {
  if (st.getComponent(ref, @DEATH@.getComponentType()) != null) return false;
  return applyMap((@ESM@) st.getComponent(ref, @ESM@.getComponentType()));
}""")
M(hp, r"""
public void stop() {
  if (this.u != null) HOLD.remove(this.u, this);
}""")
M(hp, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(hp, r"""
public void run() {
  try {
    if (this.u == null || HOLD.get(this.u) != this) return;
    if (!@PKG@.ProfCfg.HP_PER_PROFILE) { stop(); return; }      // switched off in Server Setup: stop holding
    long now = System.currentTimeMillis();
    if (now - this.start >= MAX_MS || this.pr == null || !this.pr.isValid()) { stop(); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { later(STEP_MS); return; }
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }
    java.util.UUID nowWorld = this.pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.hopWorld)) { later(STEP_MS); return; }
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) { later(STEP_MS); return; }
    if (!nowWorld.equals(this.lastWorld)) { this.lastWorld = nowWorld; this.calm = now; }
    if (!apply(r.getStore(), r)) { stop(); return; }
    if (this.moved) this.calm = now;
    if (now - this.start >= MIN_MS && now - this.calm >= CALM_MS) { stop(); return; }
    later(STEP_MS);
  } catch (Throwable t) { stop(); warnOnce("the Health hold after a profile switch stopped for " + this.u + ": " + t); }
}""")
# the hold for one player (replaces an older one); saved = the target profile's p.<id>.hp (null = none = full Health, Stamina, Mana)
M(hp, r"""
public static @PKG@.ProfHp begin(@PR@ pr, String saved) {
  @PKG@.ProfHp h = new @PKG@.ProfHp(pr, parse(saved), saved == null);
  if (h.u != null) HOLD.put(h.u, h);
  return h;
}""")
# SWITCH-IN (world thread, after the players-file commit + publish): restore now, then hold while the max settles. healthPerProfile
# off (Server Setup): nothing - Health carries over as before 0.1.7
M(hp, r"""
public static void arrive(@ST@ st, @REF@ ref, @PR@ pr, String saved) {
  try {
    if (!@PKG@.ProfCfg.HP_PER_PROFILE) { if (pr != null && pr.getUuid() != null) HOLD.remove(pr.getUuid()); return; }
    @PKG@.ProfHp h = begin(pr, saved);
    if (!h.apply(st, ref)) { h.stop(); return; }
    h.calm = System.currentTimeMillis();
    h.later(STEP_MS);
  } catch (Throwable t) { warnOnce("could not restore Health after a profile switch: " + t); }
}""")
# SWITCH-OUT: the ratio to save for the leaving profile (a running hold's own tracking when its max just moved); null = unreadable
M(hp, r"""
public static String leavingMap(@ESM@ m, java.util.UUID u) {
  if (m == null) return null;
  int hi = @DST@.getHealth();
  if (hi < 0) return null;
  @ESV@ v = m.get(hi);
  if (v == null) return null;
  float cur = v.get();
  float max = v.getMax();
  if (!(cur > 0.0f) || !(max > 0.0f)) return null;
  float r = cur / max;
  Object o = u == null ? null : HOLD.get(u);
  if (o instanceof @PKG@.ProfHp) {
    float[] s = ((@PKG@.ProfHp) o).sh;
    if (s[3] > 0.5f) r = ratioNow(cur, max, s[2], s[1], s[5]);
  }
  return text(clamp01(r));
}""")
M(hp, r"""
public static String leaving(@ST@ st, @REF@ ref, java.util.UUID u) {
  if (!@PKG@.ProfCfg.HP_PER_PROFILE) return "";      // healthPerProfile off: the saved value stays as it is
  try { return leavingMap((@ESM@) st.getComponent(ref, @ESM@.getComponentType()), u); }
  catch (Throwable t) { warnOnce("could not read Health for a profile switch of " + u + ": " + t); return null; }
}""")

# ================= ProfSwitch: checks, the switch transaction, creation, crash recovery ================='''
rep('''
# ================= ProfSwitch: checks, the switch transaction, creation, crash recovery =================''', HP_JAVA)

# ================================================================================================ the switch transaction
rep('''  org.bson.BsonDocument cur = @PKG@.ProfInv.capture(st, ref, u, from, fromKey);
  int saved = @PKG@.ProfInv.slotCount(cur);''', '''  org.bson.BsonDocument cur = @PKG@.ProfInv.capture(st, ref, u, from, fromKey);
  int saved = @PKG@.ProfInv.slotCount(cur);
  String hpOut = @PKG@.ProfHp.leaving(st, ref, u);     // 0.1.7: the leaving profile's Health ratio (before the armor swap)''')
rep('''  if (!@PKG@.ProfStore.setActive(u, from, to)) {
    boolean ok2''', '''  if (!@PKG@.ProfStore.setActive(u, from, to, hpOut)) {
    boolean ok2''')
rep('''  @PKG@.ClearLater.arm(u);
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("SWITCH " + u''', '''  @PKG@.ClearLater.arm(u);
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfHp.arrive(st, ref, pr, p.getProperty("p." + to + ".hp"));   // 0.1.7: its own Health (none = a new profile = full)
  @PKG@.ProfStore.log("SWITCH " + u''')

# ================================================================================================ the page: the big SWITCH confirms
rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', '''# 0.1.7: the switch confirm (0.1.6's pfyes code, moved): the bottom CONFIRM (pfyes) AND a second click on the highlighted SWITCH of the
# card whose question is open (pfsw<that id>, Skyy 2026-10-08 "the big switch button should work to confirm")
M(page, r"""
public void confirmSwitch(@REF@ ref, @ST@ st) {
  String to = this.pending;
  this.pending = null;
  if (to == null) { rebuild(); return; }
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (player == null) return;
  String err = @PKG@.ProfSwitch.switchTo(st, ref, this.playerRef, player, to);
  if (err != null) { this.info = err; rebuild(); }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')
rep('''      if (data.indexOf("pfsw" + i + "\\"") < 0) continue;
      String id = String.valueOf(i);
      this.pending = @PKG@.ProfStore.live(p, id) ? id : null;''', '''      if (data.indexOf("pfsw" + i + "\\"") < 0) continue;
      String id = String.valueOf(i);
      if (id.equals(this.pending)) { confirmSwitch(ref, st); return; }   // 0.1.7: the highlighted SWITCH again = CONFIRM
      this.pending = @PKG@.ProfStore.live(p, id) ? id : null;''')
rep('''    if (data.indexOf("pfyes\\"") >= 0) {
      String to = this.pending;
      this.pending = null;
      if (to == null) { rebuild(); return; }
      @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (player == null) return;
      String err = @PKG@.ProfSwitch.switchTo(st, ref, this.playerRef, player, to);
      if (err != null) { this.info = err; rebuild(); }
      return;
    }''', '''    if (data.indexOf("pfyes\\"") >= 0) { confirmSwitch(ref, st); return; }''')

# ================================================================================================ texts
rep('''A deleted profile can be restored for 6 hours (admins keep an archive).''',
    '''A deleted profile can be restored for 6 hours (admins keep an archive). Each profile keeps its own Health.''')

# ================================================================================================ checks
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
assert [ln for ln in s.split(LF) if "registerSystem(" in ln] == SYS0, "system registrations changed"
_card2 = block(CARD_START, CARD_END) + CARD_END
assert _card2 == _card, "the SKYY CARD block must stay the shared one"
assert block("PF_BUILD_LIST = r\"\"\"", "# 0.1.5: the delete / restore / close clicks") == _list_view, "the list view drawing must stay 0.1.6's"
# javassist: every method before its callers
assert s.index("public static synchronized boolean setActive(java.util.UUID u, String from, String to, String hp)") < \
    s.index("public static boolean setActive(java.util.UUID u, String from, String to) {") < s.index("@PKG@.ProfStore.setActive(u, null, low)")
assert s.index("public static String leaving(") < s.index("public static String switchLocked(")
assert s.index("public static void arrive(") < s.index("public static String switchLocked(")
assert s.index("public static float step(") < s.index("public boolean one(") < s.index("public boolean applyMap(") < s.index("public boolean apply(")
assert s.index("public boolean apply(") < s.index("public void run() {\n  try {\n    if (this.u == null") < s.index("public static void arrive(")
assert s.index("public ProfHp(") < s.index("public static @PKG@.ProfHp begin(")
assert s.index("public void confirmSwitch(") < s.index("public void handleDataEvent(")
assert "KEEP=20" not in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.6 had %d)" % (s.count(LF), OLD.count(LF)))
