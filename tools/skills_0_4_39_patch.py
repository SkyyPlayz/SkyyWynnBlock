"""Derive SkyySkills/build_skyyskills_0.4.39.py from the LIVE generated SkyySkills/build_skyyskills_0.4.38.py (= the tools/deploy_set.py SET
pin; 0.4.38 came from 0.4.37 by tools/skills_0_4_38_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.38 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_39_patch.py   then   python SkyySkills/build_skyyskills_0.4.39.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.39.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.39 (2026-10-14) = REBIRTH WRAP-UP + SOUND PASS round 2, the SkyySkills part (Skyy 2026-10-14 ~18:30, picking "7. Rebirth wrap-up:
... mods start using the tree's stat nodes" and "6. Sound pass rounds 2-4 ... skills, gear, classes" from the main session's list:
"do 1. 3. 6. 7. 8. and 9. ill start testing soon"):
  (1) REBIRTH STATS (research/cloud/Rebirth-Spec.md 3.1: +3 % all stats per rebirth, cap +30 %; the Class arm's stat nodes). New class
      RbStat. Once a second per player (Perks.tick, world thread, right after the Overall Level modifiers) it asks SkyyRebirth's
      rebirth:fn:stat apply(Object[] { UUID, name }) (the ACTIVE profile) for "all", "health", "mana" and "classxp" and posts:
        max Health  = all + health (Vitality, Greater Vitality)   key skyyskill_rebirthhp
        max Mana    = all + mana (Focus, Greater Focus)            key skyyskill_rebirthmana
        max Stamina = all                                          key skyyskill_rebirthstamina
      each a StaticModifier(MAX, ADDITIVE) = round(flat x percent / 100, 2 decimals), flat = the stat type's max + every OTHER additive
      MAX modifier (SkyySkills' own perks / Overall / class power, armour, food) - our three keys and SkyyAccessories' percent keys
      (skyyacc_*) left out, so two percent layers never feed each other (the SkyyAccessories 0.4 recipe: the engine SUMS every
      MULTIPLICATIVE amount into one factor, so MULTIPLICATIVE is never used). Class XP: SkillBonus.xpBonus adds classxp / 100 for the
      class slots (Class Wisdom), on top of the tree bonus and inside its 0..5 clamp, also when bridge.bonus.xpSkills does not list
      the class (the Stats page shows it with the rest). Rules: no SkyyRebirth (no rebirth:fn:stat) or rebirth.stats=false = 0 = the
      three modifiers removed; SkyyRebirth still reading that profile's file (no answer) = the last values kept (never a false drop);
      rebirths n = 0 and no stat node = 0 everywhere (everyone today: rebirth is OFF). Each percent is clamped 0..200.
      PER PROFILE (tools/PROFILES-CONTRACT.md rules 2 + 4; fix round): RbStat.CUR holds { the pkey the values belong to, the values }.
      After a profile switch, while SkyyRebirth has no answer yet for the NEW profile, the old profile's values are NOT used: the three
      modifiers are removed and Class Wisdom gives 0 until the new profile answers (at login with no cached values the saved modifiers
      are left alone - never a false drop).
      LEFT FOR SkyyGear (the gear6 round reads rebirth:fn:stat itself): "damage" (all + Might / Greater Might) and "defense" (all +
      Guard / Greater Guard). The Swift Brewing / Smithing / Cooking nodes are crafting speed (no pipeline in any mod yet).
      Server Setup -> Skills -> General: "Rebirth stat boosts" (rebirth.stats, default on, live).
  (2) SOUNDS (research/Sound-Pass-Plan.md; round 1's pattern, tools/quests_0_3_1_patch.py QSnd): ONE helper SkSnd, 2D to that player
      only (SoundUtil.playSoundEvent2dToPlayer, category UI), never throws, the id checked against the game's SoundEvent map (a
      missing id = one WARN, nothing played), at most one sound of a kind per player per 0.5 s. Vanilla ids (build-checked in
      Assets.zip):
        skill level up    SFX_Workbench_Upgrade_Complete_Default   SkillXp.gain4, once per award that levels up (not per level)
        Overall level up  SFX_Memories_Unlock_Local                Overall.levelUp - shares the "level" slot, so it plays INSTEAD of
                                                                  the skill sting when both happen at once
        perfect dodge     SFX_Ability_Wind_Strike_Imbue_Local      PDodge.perfect, once per perfect-dodge roll
      Muted for a player when the matching chat line is off for them (skills.levelUp, skills.overallUp + overall.chat,
      skills.perfectDodge - "a muted message class is a muted sound") or when the bridge key settings:sounds:<uuid> is Boolean FALSE
      (the per-player switch: absent / TRUE = play; SkyyMenu's /settings writes it). Server Setup -> Skills -> new category "Sounds"
      (7 rows, live): "Sounds" (master) + per sound on / off and its id (text, max 120, check= SkSnd.check: letters / digits / _ and a
      sound event the game has; empty = that sound off). Try ids with SkyyMenu's /soundtest.
  CONFIG: a fresh xp.properties lists sounds.enabled, sound.<level|overall|dodge>, sound.<..>.id and rebirth.stats; an existing file
  without them reads the same defaults (no migration, nothing rewritten). No saved-data change, no new command, no new bridge key
  written (two read: rebirth:fn:stat, settings:sounds:<uuid>). The rebirth participant rebirth:part:skills is unchanged.
  ROLLBACK to 0.4.38: safe for data, BUT the three skyyskill_rebirth* modifiers are saved with the player and 0.4.38 never removes
  them (none exist until rebirth points / stat nodes are used or someone has rebirthed). Before rolling back: switch Server Setup ->
  Skills -> General -> "Rebirth stat boosts" OFF (or /rebirthadmin refund class) with the players online, wait ~2 s (the 1 s tick
  removes them), then roll back. The sound / rebirth.stats lines are ignored by 0.4.38.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.38.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.39.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.38"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.38"' in s and "derived from the generated 0.4.37 by tools/skills_0_4_38_patch.py" in s, "not the live generated 0.4.38"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert 'rbcm = pool.makeClass(PKG + ".RbCoinMig")' in s and "SkSnd" not in s and "RbStat" not in s, "not 0.4.38"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.39 (2026-10-14)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.38 - build script (derived from the generated 0.4.37 by tools/skills_0_4_38_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.39 - build script (derived from the generated 0.4.38 by tools/skills_0_4_39_patch.py - edit the patch, not this file;
0.4.38 was derived from the generated 0.4.37 by tools/skills_0_4_38_patch.py;
''')
rep('''0.4.38 (2026-10-14) = ECONOMY ROUND econ38, the SkyySkills part''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.39.py.
0.4.38 (2026-10-14) = ECONOMY ROUND econ38, the SkyySkills part''')
rep('VERSION = "0.4.38"', 'VERSION = "0.4.39"')

# ---------------------------------------------------------------- the classes
rep('''rbcm = pool.makeClass(PKG + ".RbCoinMig")      # 0.4.38: the one-time rebirth.coinFactor 0.9 -> 0.8 update of an existing xp.properties
''', '''rbcm = pool.makeClass(PKG + ".RbCoinMig")      # 0.4.38: the one-time rebirth.coinFactor 0.9 -> 0.8 update of an existing xp.properties
snd39 = pool.makeClass(PKG + ".SkSnd")         # 0.4.39: the sound helper (level up, Overall level up, perfect dodge)
rbs39 = pool.makeClass(PKG + ".RbStat")        # 0.4.39: SkyyRebirth's stat boosts -> max Health / Mana / Stamina + class XP
''')

# ---------------------------------------------------------------- the default xp.properties block (fresh files list it)
SOUNDS = [  # (key part, label, field, default id, help <= 100)
    ("level", "Skill level up", "LEVEL", "SFX_Workbench_Upgrade_Complete_Default", "A skill or class skill levels up. Off for players who hide level-ups."),
    ("overall", "Overall Level up", "OVL", "SFX_Memories_Unlock_Local", "Your Overall Level goes up (plays instead of the skill level up sound)."),
    ("dodge", "Perfect dodge", "DODGE", "SFX_Ability_Wind_Strike_Imbue_Local", "A roll right before a hit blocks it (once per roll)."),
]
rep('''G37_KEYS = [_ln.split("=", 1)[0] for _ln in G37_L if not _ln.startswith("#")]
assert len(G37_KEYS) == len(set(G37_KEYS)) == 11
DEFAULTS = "\\n".join(L) + "\\n"
''', '''G37_KEYS = [_ln.split("=", 1)[0] for _ln in G37_L if not _ln.startswith("#")]
assert len(G37_KEYS) == len(set(G37_KEYS)) == 11
# 0.4.39 (tools/skills_0_4_39_patch.py): the sounds + the rebirth stat switch; a missing key reads the same code default (no migration)
SND39 = %r
with zipfile.ZipFile(ASSETS) as z:
    SOUND_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))
for _s39 in SND39:
    assert _s39[3] in SOUND_IDS and all(c_.isalnum() or c_ == "_" for c_ in _s39[3]), "0.4.39: sound event %%s is not in Assets.zip" %% _s39[3]
G39_L = ["# ---------- Sounds and rebirth stats (SkyySkills 0.4.39) ----------",
         "# Comments must stay on their own lines.",
         "# SOUNDS: vanilla sound event ids played to that player only (try them in game with /soundtest); an empty id = that sound off.",
         "# A player who hides a chat line in /settings (or mutes sounds there) hears no sound for it. The Overall Level up sound plays",
         "# instead of the skill one when both happen at once.",
         "sounds.enabled=true"] + sum([["sound.%%s=true" %% _s39[0], "sound.%%s.id=%%s" %% (_s39[0], _s39[3])] for _s39 in SND39], []) + [
         "# REBIRTH STATS: true = SkyyRebirth's stat boosts (+3 percent all stats per rebirth, the Class arm's stat nodes) raise max",
         "# Health, Mana and Stamina and Class Wisdom raises class XP. Damage and defense come from SkyyGear.",
         "rebirth.stats=true"]
L.append("")
L.extend(G39_L)
G39_DEFAULTS = "\\n".join(G39_L) + "\\n"
assert all(ord(ch) < 128 for ch in G39_DEFAULTS) and '"' not in G39_DEFAULTS and "\\\\" not in G39_DEFAULTS and all(len(_ln) <= 140 for _ln in G39_L if _ln.startswith("#"))
assert not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in G39_L), "a comment looks like a template line"
G39_KEYS = [_ln.split("=", 1)[0] for _ln in G39_L if not _ln.startswith("#")]
assert len(G39_KEYS) == len(set(G39_KEYS)) == 8
DEFAULTS = "\\n".join(L) + "\\n"
''' % (SOUNDS,))

# ---------------------------------------------------------------- part 1 (before SkillCfg.load and the config kit): fields, read, the check= hook
PART1 = r'''# ================= 0.4.39 SkSnd part 1 + RbStat part 1: fields, the xp.properties read, the pure helpers, the Server Setup check= hook
# (compiled before SkillCfg.load and CFG.emit, which call them). SkSnd = the ONE sound helper (round 1's QSnd recipe): pick() = the id when
# the master switch and that sound are on (else null = silent), idx() = the game's SoundEvent index (Integer.MIN_VALUE = no such event),
# gate() = at most one sound per key per GAP_MS. RbStat.ON = rebirth.stats.
for _d39 in ["public static volatile boolean ON = true;"] + sum([["public static volatile boolean %s = true;" % _s39[2],
                                                                   "public static volatile String %s_ID = %s;" % (_s39[2], json.dumps(_s39[3]))] for _s39 in SND39], []):
    snd39.addField(CtField.make(_d39, snd39))
for _d39 in ("java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap()",
             "java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap()",
             "java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong()",
             "java.util.concurrent.atomic.AtomicLong MUTED = new java.util.concurrent.atomic.AtomicLong()",
             "long GAP_MS = 500L"):
    snd39.addField(CtField.make("public static final %s;" % _d39, snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String idOf(java.util.Properties p, String k, String d) {
  String v = p == null ? null : p.getProperty(k);
  return v == null ? d : v.trim();
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "sounds.enabled", true);
''' + "\n".join('''  %s = @PKG@.SkillCfg.bool(p, "sound.%s", true);
  %s_ID = idOf(p, "sound.%s.id", %s);''' % (_s[2], _s[0], _s[2], _s[0], '"%s"' % _s[3]) for _s in SOUNDS) + r'''
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = @SEV@.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Coins_Land).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = @SEV@.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String check(String key, String value) {
  return err(value);
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String pick(boolean master, boolean on, String id) {
  if (!master || !on || id == null) return null;
  String v = id.trim();
  return v.length() == 0 ? null : v;
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String one(boolean on, String id) {
  return on && id != null && id.length() > 0 ? id : "off";
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "off";
  return "on (level up " + one(LEVEL, LEVEL_ID) + ", Overall " + one(OVL, OVL_ID) + ", perfect dodge " + one(DODGE, DODGE_ID) + "; settings:sounds:<uuid> FALSE mutes a player)";
}"""), snd39))
for _d39 in ("public static volatile boolean ON = true;", "public static volatile boolean WARNED = false;",
             "public static final java.util.concurrent.ConcurrentHashMap CUR = new java.util.concurrent.ConcurrentHashMap();",
             "public static final java.util.concurrent.atomic.AtomicLong ASKS = new java.util.concurrent.atomic.AtomicLong();",
             'public static final String KH = "skyyskill_rebirthhp";', 'public static final String KM = "skyyskill_rebirthmana";',
             'public static final String KS = "skyyskill_rebirthstamina";', "public static final double MAXPCT = 200.0;"):
    rbs39.addField(CtField.make(_d39, rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "rebirth.stats", true);
  if (!ON) CUR.clear();
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double clampPct(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
  return v > MAXPCT ? MAXPCT : v;
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return ON ? "on (rebirth:fn:stat -> max Health / Mana / Stamina + class XP; damage / defense: SkyyGear)" : "off";
}"""), rbs39))
'''
rep('''# the perfect-dodge window: age = ms since the roll began, -1 = no roll / cannot tell
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean inWindow(long age, long win) {''', PART1 + '''# the perfect-dodge window: age = ms since the roll began, -1 = no roll / cannot tell
pdg.addMethod(CtNewMethod.make(J14(r"""
public static boolean inWindow(long age, long win) {''')

# ---------------------------------------------------------------- SkillCfg.load reads them
rep('''    {PKG}.Farm3.read(p);        // 0.4.37: Orchard routing + the Farming average (orchard.ids, overall.farmingAverage)
''', '''    {PKG}.Farm3.read(p);        // 0.4.37: Orchard routing + the Farming average (orchard.ids, overall.farmingAverage)
    {PKG}.SkSnd.read(p);        // 0.4.39: sounds (sounds.enabled, sound.<level|overall|dodge>[.id])
    {PKG}.RbStat.read(p);       // 0.4.39: rebirth stat boosts (rebirth.stats)
''')

# ---------------------------------------------------------------- SkSnd part 2 (after SkillStore.bridge / notifyOn, before Overall / gain4 / PDodge.perfect)
PART2 = r'''# ================= 0.4.39 SkSnd part 2: play (world thread callers; never throws) =================
# muted(u) = the per-player switch: bridge settings:sounds:<uuid> Boolean FALSE (absent / TRUE = play; SkyyMenu's /settings writes it).
# playTo: valid player, not muted, the id in the game's SoundEvent map (a missing id = one WARN per id), the per player + kind gate,
# then ONE PlaySoundEvent2D packet to that player (category UI - the engine's own discovery sting call).
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  try { return Boolean.FALSE.equals(@PKG@.SkillStore.bridge().get("settings:sounds:" + u.toString())); } catch (Throwable t) { return false; }
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean playTo(@PR@ pr, String id, String tag) {
  if (pr == null || id == null) return false;
  try {
    if (!pr.isValid()) return false;
    java.util.UUID u = pr.getUuid();
    if (muted(u)) { MUTED.incrementAndGet(); return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) @PKG@.SkillCfg.warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Skills -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(u) + "|" + tag, System.currentTimeMillis())) return false;
    @SNU@.playSoundEvent2dToPlayer(pr, i, @SCAT@.UI);
    PLAYED.incrementAndGet();
    return true;
  } catch (Throwable t) {
    if (WARNED.putIfAbsent("#failed", Boolean.TRUE) == null) @PKG@.SkillCfg.warn("could not play a sound (logged once): " + t);
    return false;
  }
}"""), snd39))
# the three moments; the callers already checked the player's chat switch (level / overall), dodge checks skills.perfectDodge here
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean level(@PR@ pr) {
  return playTo(pr, pick(ON, LEVEL, LEVEL_ID), "level");
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean overall(@PR@ pr) {
  return playTo(pr, pick(ON, OVL, OVL_ID), "level");
}"""), snd39))
snd39.addMethod(CtNewMethod.make(J14(r"""
public static boolean dodge(@PR@ pr, java.util.UUID u) {
  String id = pick(ON, DODGE, DODGE_ID);
  if (id == null || !@PKG@.SkillStore.notifyOn(u, "skills.perfectDodge")) return false;
  return playTo(pr, id, "dodge");
}"""), snd39))
'''
rep('''# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
''', PART2 + '''# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
''')

# ---------------------------------------------------------------- RbStat part 2 (after Overall.typeMax, before SkillBonus.xpBonus and Perks.tick)
PART3 = r'''# ================= 0.4.39 RbStat part 2: SkyyRebirth's stat boosts (rebirth:fn:stat) on the stats SkyySkills owns =================
# fetch(u) = { max Health %, max Mana %, max Stamina %, class XP % } from rebirth:fn:stat apply(Object[] { UUID, name }) for "all" (the
# per-rebirth boost + Void Ascendant), "health", "mana", "classxp" (the Class arm's nodes); zeros = nothing (no SkyyRebirth, the switch off);
# null = SkyyRebirth has no answer yet (still reading that profile's file) -> the last values stay. Memory only, never throws.
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double ask(java.util.function.Function f, java.util.UUID u, String name) {
  ASKS.incrementAndGet();
  Object r = f.apply(new Object[] { u, name });
  if (r instanceof Number) {
    double d = ((Number) r).doubleValue();
    return (Double.isNaN(d) || Double.isInfinite(d)) ? 0.0 : d;
  }
  return Double.NaN;
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double[] fetch(java.util.UUID u) {
  double[] z = new double[4];
  if (!ON || u == null) return z;
  Object f = @PKG@.SkillStore.bridge().get("rebirth:fn:stat");
  if (!(f instanceof java.util.function.Function)) return z;
  try {
    java.util.function.Function fn = (java.util.function.Function) f;
    double all = ask(fn, u, "all");
    if (Double.isNaN(all)) return null;
    double hp = ask(fn, u, "health");
    double mn = ask(fn, u, "mana");
    double cx = ask(fn, u, "classxp");
    if (Double.isNaN(hp) || Double.isNaN(mn) || Double.isNaN(cx)) return null;
    z[0] = clampPct(all + hp);
    z[1] = clampPct(all + mn);
    z[2] = clampPct(all);
    z[3] = clampPct(cx);
    return z;
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; @PKG@.SkillCfg.warn("rebirth:fn:stat (SkyyRebirth) failed - the last rebirth stats stay (logged once): " + t); }
    return null;
  }
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double[] cached(java.util.UUID u, String pk) {
  Object o = CUR.get(u);
  if (!(o instanceof Object[])) return null;
  Object[] e = (Object[]) o;
  if (e.length < 2 || !(e[1] instanceof double[])) return null;
  if (pk == null || !pk.equals(e[0])) return new double[4];
  return (double[]) e[1];
}"""), rbs39))
# fix round: CUR = UUID -> { pkey, values } (PROFILES-CONTRACT rules 2 + 4): a profile switch never carries the old profile's values
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double[] refresh(java.util.UUID u) {
  if (u == null) return null;
  String pk = @PKG@.SkillStore.pkey(u);
  double[] v = fetch(u);
  if (v != null) { CUR.put(u, new Object[] { pk, v }); return v; }
  return cached(u, pk);
}"""), rbs39))
# the class XP fraction (Class Wisdom) for SkillBonus.xpBonus - the value of the player's last 1 s tick (no bridge call per XP award)
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static double classXp(java.util.UUID u) {
  if (!ON || u == null) return 0.0;
  double[] v = cached(u, @PKG@.SkillStore.pkey(u));
  return v == null ? 0.0 : v[3] / 100.0;
}"""), rbs39))
# the modifier keys a percent layer must never feed on: our three + SkyyAccessories' percent layer (skyyacc_*)
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static boolean skip(Object k) {
  if (!(k instanceof String)) return true;
  String s = (String) k;
  return s.equals(KH) || s.equals(KM) || s.equals(KS) || s.startsWith("skyyacc_");
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static float flatMax(@ESV@ v, int idx) {
  float base = @PKG@.Overall.typeMax(idx);
  java.util.Map mods = v.getModifiers();
  if (mods == null) return base;
  java.util.Iterator it = mods.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (skip(k)) continue;
    Object o = mods.get(k);
    if (!(o instanceof @SMO@)) continue;
    @SMO@ sm = (@SMO@) o;
    if (sm.getTarget() != @MTG@.MAX || sm.getCalculationType() != @CAL@.ADDITIVE) continue;
    base = base + sm.getAmount();
  }
  return base;
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static float amount(float flat, double pct) {
  if (!(pct > 0.0) || !(flat > 0.0f)) return 0.0f;
  return (float) Math.round((double) flat * pct) / 100.0f;
}"""), rbs39))
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static void put(@ESM@ m, int idx, String key, double pct) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float amt = amount(flatMax(v, idx), pct);
  @MOD@ cur = m.getModifier(idx, key);
  if (amt <= 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
  @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
  if (cur != null && cur.equals(want)) return;
  m.putModifier(idx, key, want);
}"""), rbs39))
# world thread, Perks.tick once a second after the Overall modifiers
rbs39.addMethod(CtNewMethod.make(J14(r"""
public static void tick(java.util.UUID u, @ESM@ m) {
  if (m == null || u == null) return;
  try {
    double[] v = refresh(u);
    if (v == null) return;
    put(m, @DST@.getHealth(), KH, v[0]);
    put(m, @DST@.getMana(), KM, v[1]);
    put(m, @DST@.getStamina(), KS, v[2]);
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; @PKG@.SkillCfg.warn("rebirth stat tick failed (logged once): " + t); }
  }
}"""), rbs39))
'''
rep('''# ================= ClassMana part 2 (0.4.15): the per-player amount (Perks.ovl), the Stats page line, the /skills mana line =================
''', PART3 + '''# ================= ClassMana part 2 (0.4.15): the per-player amount (Perks.ovl), the Stats page line, the /skills mana line =================
''')

# ---------------------------------------------------------------- the callers
# Overall level up sound (only where the chat line is shown: overall.chat + the player's skills.overallUp)
rep('''    pr.sendMessage({MSG}.raw("OVERALL LEVEL UP  " + before + " -> " + after + (bonus.length() > 0 ? " " + bonus : "")).color("#ffe08a"));
''', '''    pr.sendMessage({MSG}.raw("OVERALL LEVEL UP  " + before + " -> " + after + (bonus.length() > 0 ? " " + bonus : "")).color("#ffe08a"));
    {PKG}.SkSnd.overall(pr);   // 0.4.39: the Overall sting (the "level" slot - the skill sting after it is skipped)
''')
# skill level up sound: once per award, AFTER Overall.levelUp (an Overall level up takes the slot first)
rep('''    {PKG}.Overall.levelUp(pr, u, skill, Math.min(r[0], tmax), Math.min(r[1], tmax));
''', '''    {PKG}.Overall.levelUp(pr, u, skill, Math.min(r[0], tmax), Math.min(r[1], tmax));
    if (lvOn) {PKG}.SkSnd.level(pr);   // 0.4.39: the level-up sting (skills.levelUp shown = sound on)
''')
# perfect dodge sound: once per perfect-dodge roll (mark = one reward per roll)
rep('''  if (!mark(u, now)) return 0L;
''', '''  if (!mark(u, now)) return 0L;
  @PKG@.SkSnd.dodge(pr, u);   // 0.4.39: the perfect dodge sound (skills.perfectDodge shown = sound on)
''')
# the rebirth stat modifiers, once a second after the Overall modifiers
rep('''    ovl(u, pr, cb, ref, m);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("perk tick failed (logged once): " + t); }}''',
    '''    ovl(u, pr, cb, ref, m);
    {PKG}.RbStat.tick(u, m);   // 0.4.39: SkyyRebirth's stat boosts on max Health / Mana / Stamina
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("perk tick failed (logged once): " + t); }}''')
# Class Wisdom: class XP for the class slots, inside the 0..5 clamp, also when the class is not a Wisdom skill
rep('''public static double xpBonus(java.util.UUID u, int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  if (!{PKG}.SkillDefs.boostable(slot)) return 0.0;
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;
  if (slot >= on.length || !on[slot]) return 0.0;
  double s = sum(u, "xp." + key(slot));
  if (s <= 0.0) return 0.0;''', '''public static double xpBonus(java.util.UUID u, int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  if (!{PKG}.SkillDefs.boostable(slot)) return 0.0;
  double rb = {PKG}.SkillDefs.isClass(slot) ? {PKG}.RbStat.classXp(u) : 0.0;   // 0.4.39: Class Wisdom (rebirth:fn:stat classxp)
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;
  double s = (slot >= on.length || !on[slot]) ? 0.0 : sum(u, "xp." + key(slot));
  s = s + rb;
  if (s <= 0.0) return 0.0;''')
# players who left
rep('''    {PKG}.PDodge.retain(online);   // 0.4.37: perfect dodge state of players who left
''', '''    {PKG}.PDodge.retain(online);   // 0.4.37: perfect dodge state of players who left
    {PKG}.RbStat.CUR.keySet().retainAll(online);   // 0.4.39: the rebirth stats of players who left
''')

# ---------------------------------------------------------------- Server Setup
rep('''("power", "Class Power"), ("crafting", "Crafting")]   # 0.4.25: + Class Power''',
    '''("power", "Class Power"), ("crafting", "Crafting"),
            ("sounds", "Sounds")]   # 0.4.25: + Class Power; 0.4.39: + Sounds''')
_rows = ['''    # 0.4.39: the sounds (master + per sound on / off and its id) and the rebirth stat switch - G39_KEYS order
    ("sounds.enabled", "Sounds", "sounds", "bool", "true", "", "", "", "", "live",
     "Off = SkyySkills plays no sound. Players can mute sounds in /settings. Try ids with /soundtest.", "reload"),''']
for _s in SOUNDS:
    _rows.append('''    ("sound.%s", "%s sound", "sounds", "bool", "true", "", "", "", "", "live",
     "%s", "reload"),''' % (_s[0], _s[1], _s[4]))
    _rows.append('''    ("sound.%s.id", "%s sound id", "sounds", "text", "%s", "", "120", "", "", "live",
     "A vanilla sound event id (try it with /soundtest). Empty = no sound.", "reload;check=SkSnd.check"),''' % (_s[0], _s[1], _s[3]))
_rows.append('''    ("rebirth.stats", "Rebirth stat boosts", "general", "bool", "true", "", "", "", "", "live",
     "On: SkyyRebirth's stat boosts raise max Health, Mana, Stamina and class XP.", "reload"),''')
rep('''     "On: the Overall Level counts Farming as the average of Farming, Ranching and Orchard.", "reload"),
]''', '''     "On: the Overall Level counts Farming as the average of Farming, Ranching and Orchard.", "reload"),
''' + "\n".join(_rows) + '''
]''')
rep('''assert [_r[0] for _r in CFG_ROWS][-11:] == G37_KEYS
''', '''assert [_r[0] for _r in CFG_ROWS][-19:-8] == G37_KEYS   # 0.4.39: the 8 G39 rows follow
for _k39 in G39_KEYS:   # 0.4.39: every new key a row once, row default = the default file (= the code default)
    _r39 = [_r for _r in CFG_ROWS if _r[0] == _k39]
    assert len(_r39) == 1 and _dp.get(_k39) is not None and ("\\n" + _k39 + "=" + _dp[_k39] + "\\n") in ("\\n" + G39_DEFAULTS), _k39
assert [_r[0] for _r in CFG_ROWS][-8:] == G39_KEYS
''')
rep('''assert len(CFG_ROWS) == 241, ("0.4.37: + 11 rows''', '''assert len(CFG_ROWS) == 249, ("0.4.39: + 8 rows (sounds 7, rebirth.stats); 0.4.37: + 11 rows''')
rep('''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS + "\\n" + KXP_DEFAULTS + "\\n" + P25_DEFAULTS + "\\n" + G37_DEFAULTS)''',
    '''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS + "\\n" + KXP_DEFAULTS + "\\n" + P25_DEFAULTS + "\\n" + G37_DEFAULTS + "\\n" + G39_DEFAULTS)   # 0.4.39: + G39''')

# ---------------------------------------------------------------- the two new classes are written into the jar
rep("""          rbcm):   # 0.4.38: + RbCoinMig;""", """          rbcm, snd39, rbs39):   # 0.4.39: + SkSnd, RbStat; 0.4.38: + RbCoinMig;""")
# ---------------------------------------------------------------- the ready line
rep('''"; perfect dodge " + {PKG}.PDodge.text() + "''', '''"; perfect dodge " + {PKG}.PDodge.text() + "; sounds " + {PKG}.SkSnd.text() + "; rebirth stats " + {PKG}.RbStat.text() + "''')

# ---------------------------------------------------------------- checks
_i = s.index
assert _i('snd39 = pool.makeClass') < _i("public static String check(String key, String value) {\n  return err(value);") < _i("kit = CFG.emit(pool, PKG")
assert _i("rbs39.addField") < _i("{PKG}.RbStat.read(p);") and _i("snd39.addField") < _i("{PKG}.SkSnd.read(p);")
assert _i("public static boolean overall(@PR@ pr)") < _i("{PKG}.SkSnd.overall(pr);") < _i("if (lvOn) {PKG}.SkSnd.level(pr);")
assert _i("public static boolean dodge(@PR@ pr") < _i("@PKG@.SkSnd.dodge(pr, u);")
assert _i("public static float typeMax(int idx)") < _i("public static float flatMax(@ESV@ v, int idx)") < _i("public static double xpBonus(") < _i("{PKG}.RbStat.tick(u, m);")
assert s.count("registerSystem(") == S0.count("registerSystem(") and s.count("registerCommand(") == S0.count("registerCommand(")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.38 lines changed outside the planned places: %r" % _bad[:5]
if os.path.exists(dst):
    os.remove(dst)
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.38,", len(_gone), "0.4.38 lines replaced;", len(OLDS), "anchors")
