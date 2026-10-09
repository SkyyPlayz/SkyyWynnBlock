"""Derive SkyyProfiles/build_skyyprofiles_0.1.9.py from the generated 0.1.8 (build_skyyprofiles_0.1.8.py = the tools/deploy_set.py SET pin).
Edit THIS file, never the generated build script. Harness: python SkyyProfiles/test_skyyprofiles_0.1.9.py --dir <empty scratch folder>.
Run:  python tools/profiles_0_1_9_patch.py   then   python SkyyProfiles/build_skyyprofiles_0.1.9.py   (never --deploy)

0.1.9 = THE PROFILE CAP = THE NUMBER OF CLASSES (Skyy LOCKED 2026-10-08, docs/answered/social.md popup batch 5: "profile cap should match
the number of classes. ( upgrade: ranks and earn in game later)" -> cap = class count, 8 with Spellblade, instead of 6 / 7).

  - AUTO LIMIT (maxProfiles=auto, the default since 0.1.4 and Skyy's live value): auto = the number of CLASSES IN THE GAME = the distinct
    names of the fallback roster (now 8 with the SPELLBLADE) united with SkyyClasses' class:list (aliases folded: Shaman = Monk).
    0.1.4-0.1.8 counted only class:list (the classes SkyyClasses lists as PLAYABLE today: 7) and used 6 without SkyyClasses. Now:
    8 with SkyyClasses 0.1.15, 8 without SkyyClasses (= the "Server Setup default of 8": the fallback roster), and it grows by itself
    when SkyyClasses lists a ninth class. ProfCfg.classCount() is that union; the old count is kept as ProfCfg.listCount() (only the
    capNote text uses it: "auto = 8 - one per class (7 playable in SkyyClasses)"). A FIXED base stays clamped 1..CAP_MAX = 8 (the fixed
    choices 1-8 are unchanged); auto itself is clamped to LIMIT_MAX = 16 (a ninth SkyyClasses class gives 9).
  - SPELLBLADE CARD (fallback roster, enabled=false = "Coming later"; Skyy LOCKED 2026-10-08 the name, research/classes/Spellblade.md):
    skill Battlemagic (the page's PROPOSED name - display only, the card is greyed and cannot be picked), two-handed swords (Spectral +
    Flame longsword icons), colour #6fd0d8. With SkyyClasses it stays greyed until SkyyClasses lists Spellblade in class:list; nothing
    else can pick it (/profiles create refuses a coming-later class as before; /profileadmin setclass still may - an admin fix).
  - NO MIGRATION (PROJECT-RULES 4): the live default row maxProfiles stays "auto" - only what auto counts changed. A fixed number an
    owner set (1-8, by hand, in game or by command) is kept exactly as it is.
  - BONUS SLOTS HOOK (Skyy: "upgrade: ranks and earn in game later" - the earn method is OPEN, this is only the hook, default 0):
    players-file key bonusSlots=<n> per player (absent = 0), set by /profileadmin bonus <player|uuid> <0-16> (skyyprofiles.admin;
    logged BONUS in switches.log) or by another mod through the NEW bridge function profile:fn:bonusSlots = Function:
    apply(UUID) -> Integer (the player's bonus, 0 when none); apply(Object[] { UUID, Number n }) -> Integer (sets it to n clamped
    0..16; 0 removes the key) or null (bad arguments, players file unreadable / could not be written). Never throws, never calls out;
    file I/O only under SkyyProfiles' store lock. The limit is now capFor(u) = base + rank:fn:profileSlots + bonus, at most
    LIMIT_MAX = 16 (0.1.4-0.1.8: at most 8). Texts add " + N bonus" ("This is profile 9 of 9 - one per class + 1 bonus.").
  - PAGES (fit 1080 - the window stays 1100 x 980): both lists are vanilla SCROLLING list wells now (the kit's scroll_list(well=True) =
    LayoutMode TopScrolling + @DefaultScrollbarStyle; vanilla never paginates) with the SAME visible heights as 0.1.8: the Profiles list
    shows 8 profile cards, the Create Profile list 7 class cards; more scroll. The cards are 12 px narrower (room for the 6 px scrollbar
    + its 6 px spacing). The Create Profile page draws up to MAX_CARDS = 12 class cards (0.1.4-0.1.8: 7 - the Spellblade is the 8th);
    the Profiles list draws up to LIST_MAX = 16 cards (0.1.5-0.1.8: 8 - live profiles first, then deleted ones, then Create new), so
    a player with bonus slots sees every profile and the Create new card.
  - Texts: capWhy auto = "one per class" (was "one per class you can play" - the Spellblade counts but is not playable yet); the
    Server Setup row help + note and the maxProfiles comment of a NEW config.properties say 8 / one per class.
  Unchanged: every element id, event binding and payload; switch / create / delete / restore / archive code; players-file keys other
  than the new optional bonusSlots; every bridge key other than the new profile:fn:bonusSlots; the SKYY CARD block (CARD_SHA).
  ROLLBACK 0.1.9 -> 0.1.8: safe (0.1.8 ignores bonusSlots; the limit falls back to 7 - nobody loses a profile, players above 7 keep
  theirs but cannot create more). BEFORE rolling back, set every bonus to 0 (/profileadmin bonus <player> 0): 0.1.8's page draws at most
  8 cards, so a player with bonus slots and more than 8 profiles would not SEE the 9th+ (or a deleted one) on /profiles - the data
  stays and /profiles switch <name> still works.
  FIXER (critic round): /profileadmin bonus refuses a uuid / name with no players file that is not online (no orphan file); its reply
  names the player (or "Your ..." for yourself) instead of the raw uuid; capMigrate's one-time log notes say 8 / "one profile per class of the game"
  (were "6 without SkyyClasses" / "a player can pick").
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.8.py")
dst = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.9.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.8"' in s and "GENERATED by tools/profiles_0_1_8_patch.py from build_skyyprofiles_0.1.7.py" in s, "not the generated 0.1.8"
assert "Spellblade" not in s and "bonusSlots" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:120])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyProfiles 0.1.8 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.8.py          -> SkyyProfiles/SkyyProfiles-0.1.8.jar''',
    '''"""SkyyProfiles 0.1.9 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.9.py          -> SkyyProfiles/SkyyProfiles-0.1.9.jar''')
rep('''GENERATED by tools/profiles_0_1_8_patch.py from build_skyyprofiles_0.1.7.py (generated by tools/profiles_0_1_7_patch.py from 0.1.6,''',
    '''GENERATED by tools/profiles_0_1_9_patch.py from build_skyyprofiles_0.1.8.py (generated by tools/profiles_0_1_8_patch.py from 0.1.7,
generated by tools/profiles_0_1_7_patch.py from 0.1.6,''')
rep('''Harness: python SkyyProfiles/test_skyyprofiles_0.1.8.py

0.1.8 (2026-10-09''', '''Harness: python SkyyProfiles/test_skyyprofiles_0.1.9.py --dir <empty folder inside tools/dev/scratch/>

0.1.9 (2026-10-09, Skyy LOCKED 2026-10-08 "profile cap should match the number of classes. ( upgrade: ranks and earn in game later)"):
  maxProfiles=auto (the default; no migration) = the classes in the game = the fallback roster (8 with the new Spellblade card, greyed
  'coming later') united with SkyyClasses' class:list -> 8 today, with or without SkyyClasses. Bonus slots hook: players-file
  bonusSlots (/profileadmin bonus <player> <n>, bridge profile:fn:bonusSlots), limit = base + rank + bonus <= 16. Both page lists
  scroll (vanilla TopScrolling well; same visible 8 / 7 cards, window still 1100 x 980). Full notes in tools/profiles_0_1_9_patch.py.

0.1.8 (2026-10-09''')
rep('VERSION = "0.1.8"\n', 'VERSION = "0.1.9"\n')

# ---------------------------------------------------------------------------------------------------------------- data
rep('''    {"name": "Monk", "skill": "Zen", "color": "#f08a30", "enabled": True, "role": "Self-speed disruptor",
     "desc": "Fast melee fighter. A bo staff strikes with reach - quick hand wraps and heavy gauntlets.",
     "icons": ["Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"], "weapon_text": "Bo Staves / Wraps / Gauntlets"},
]''', '''    {"name": "Monk", "skill": "Zen", "color": "#f08a30", "enabled": True, "role": "Self-speed disruptor",
     "desc": "Fast melee fighter. A bo staff strikes with reach - quick hand wraps and heavy gauntlets.",
     "icons": ["Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"], "weapon_text": "Bo Staves / Wraps / Gauntlets"},
    # 0.1.9 (Skyy LOCKED 2026-10-08 the name "spellblade"; research/classes/Spellblade.md): the 8th class - NOT playable yet ("Coming
    # later"; SkyyClasses does not list it). It counts for the automatic profile limit (Skyy: cap = class count, 8 with Spellblade).
    # The skill name Battlemagic is the class page's PROPOSED name (shown greyed only).
    {"name": "Spellblade", "skill": "Battlemagic", "color": "#6fd0d8", "enabled": False, "role": "Melee mage",
     "desc": "Melee mage. Wide sweeping arcs with two-handed swords - keep attacking to build Momentum and swing faster.",
     "icons": ["Weapon_Longsword_Spectral", "Weapon_Longsword_Flame"], "weapon_text": "Two-handed swords"},
]''')
rep('''UI_DATA_COLORS = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30", "#c9d6e2"]''',
    '''UI_DATA_COLORS = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30", "#6fd0d8", "#c9d6e2"]''')
rep('''CAP_FALLBACK = 6                       # 0.1.4: auto without SkyyClasses (no class:list) = the old fixed default (0.1.1-0.1.3: 6)
CAP_MAX = 8                            # 0.1.4: the highest limit (fixed or auto + rank extras): the Profiles list holds 8 profile cards
''', '''CAP_FALLBACK = 8                       # 0.1.9: auto when no class is known at all (never: the fallback roster has 8); 0.1.4-0.1.8: 6
CAP_MAX = 8                            # 0.1.4: the highest BASE limit (fixed 1-8 or auto); 0.1.9: the Profiles list SHOWS 8 cards at once
LIMIT_MAX = 16                         # 0.1.9: the highest TOTAL limit (base + rank extras + bonus slots); 0.1.4-0.1.8: CAP_MAX
BONUS_FN = "profile:fn:bonusSlots"     # 0.1.9: bridge Function (SkyyProfiles' own): a player's bonus profile slots (players file)
''')
rep('''MAX_CARDS = 7                          # class cards drawn on the Create Profile page AND pfcls<i> payloads handled (0.1.1: 6, 0.1.2 /
                                       # 0.1.3: 8; 0.1.4: 7 - the 92 px SKYY CARD leaves room for 7 = every class SkyyClasses knows)
''', '''MAX_CARDS = 12                         # class cards drawn on the Create Profile page AND pfcls<i> payloads handled (0.1.1: 6, 0.1.2 /
                                       # 0.1.3: 8; 0.1.4-0.1.8: 7; 0.1.9: 12 - the list scrolls, 7 cards visible at once)
CREATE_ROWS = 7                        # 0.1.9: class cards VISIBLE at once in the Create Profile list (its height = 0.1.8's well)
LIST_MAX = LIMIT_MAX                   # 0.1.9: profile cards drawn on the Profiles list (it scrolls; CAP_MAX = 8 visible at once)
''')
rep('''need(len(CLASSES) <= MAX_CARDS, "the fallback roster has more classes than the Create Profile page draws")
need(1 <= CAP_FALLBACK <= CAP_MAX and CAP_MAX >= len(CLASSES), "CAP_MAX must reach every class (the automatic limit grows with them)")
''', '''need(len(CLASSES) <= MAX_CARDS, "the fallback roster has more classes than the Create Profile page draws")
need(1 <= CAP_FALLBACK <= CAP_MAX and CAP_MAX >= len(CLASSES), "CAP_MAX must reach every class (the automatic limit grows with them)")
need(CAP_MAX <= LIMIT_MAX == LIST_MAX and CREATE_ROWS <= MAX_CARDS, "0.1.9: limits / list sizes")
''')
rep('''need([c["name"] for c in CLASSES] == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"], "fallback roster order (0.1.6: Shaman -> Monk)")
need(all(c["enabled"] for c in CLASSES), "0.1.6: all seven playable (Skyy LOCKED 2026-10-07)")
need(len(CLASSES) == MAX_CARDS, "0.1.6: the seven classes fill the Create Profile page's seven cards")
''', '''need([c["name"] for c in CLASSES] == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"],
     "fallback roster order (0.1.6: Shaman -> Monk; 0.1.9: + Spellblade)")
need(all(c["enabled"] for c in CLASSES[:7]) and not CLASSES[7]["enabled"], "0.1.6: seven playable; 0.1.9: the Spellblade is coming later")
need(len(CLASSES) == 8, "0.1.9: eight classes (Skyy 2026-10-08: the cap = the number of classes, 8 with Spellblade)")
''')
rep('''    for _c in CLASSES[5:]:
        need(''', '''    for _c in CLASSES[5:7]:       # 0.1.9: the Spellblade is not in SkyyClasses yet
        need(''')

# ---------------------------------------------------------------------------------------------------------------- config file + kit texts
rep('''    '# maxProfiles = profile slots per player: auto = one per class a player can pick right now (the classes SkyyClasses lists as',
    '#   playable - it grows by itself when a class opens; 6 without SkyyClasses) or a fixed number 1-8. Each profile = its own',
    '#   class, island, coins, skills, bags and vanilla inventory.',
''', '''    '# maxProfiles = profile slots per player: auto = one per class in the game (8 with the Spellblade - it grows by itself when',
    '#   SkyyClasses adds a class; a player may also have bonus slots) or a fixed number 1-8. Each profile = its own',
    '#   class, island, coins, skills, bags and vanilla inventory.',
''')
rep('''     "Auto = one per class players can pick (grows as classes open). Lowering never deletes a profile.",''',
    '''     "Auto = one per class in the game (8 with Spellblade). Lowering never deletes a profile.",''')
# fixer: the one-time capMigrate log notes (0.1.4) still said "6 without SkyyClasses" - auto is 8 without SkyyClasses now
rep("one profile per class a player can pick - it grows as classes open; 6 without SkyyClasses)",
    "one profile per class in the game - 8 with the Spellblade, also without SkyyClasses; it grows when SkyyClasses adds a class)", count=2)
rep("one profile per class a player can pick", "one profile per class of the game", count=8)   # fixer: the other capMigrate / upgradeDefault notes
rep('''               NOTE="Auto = one profile per playable class (6 without SkyyClasses). Fixes: /profileadmin info, setclass.",''',
    '''               NOTE="Auto = one profile per class (8 with Spellblade). Extra: /profileadmin bonus. Fixes: info, setclass.",''')

# ---------------------------------------------------------------------------------------------------------------- ProfCfg: fields + the limit
rep('''F(cfg, "public static final int CAP_FALLBACK = %d;" % CAP_FALLBACK)
''', '''F(cfg, "public static final int CAP_FALLBACK = %d;" % CAP_FALLBACK)
F(cfg, "public static final int LIMIT_MAX = %d;" % LIMIT_MAX)                 # 0.1.9: base + rank + bonus, at most this
F(cfg, "public static final String BONUS_FN = %s;" % jstr(BONUS_FN))           # 0.1.9
F(cfg, "public static volatile boolean BONUS_WARNED = false;")                # 0.1.9
# 0.1.9: the classes this build knows (the fallback roster, lower case) + the alias table, for classCount() (ProfCfg is compiled before
# ProfRoster, so the names are its own copy of the same data)
F(cfg, "public static final String[] KNOWN = %s;" % jarr([c["name"].lower() for c in CLASSES]))
F(cfg, "public static final String[] KNOWN_ALIAS_FROM = %s;" % jarr([a.lower() for a, _ in CLASS_ALIASES]))
F(cfg, "public static final String[] KNOWN_ALIAS_TO = %s;" % jarr([n.lower() for _, n in CLASS_ALIASES]))
''')
rep('''# 0.1.4: THE PROFILE LIMIT. classCount() = the distinct class names in SkyyClasses' class:list (-1 = no list: SkyyClasses absent);
# baseCap() = the fixed number, or auto = classCount() (CAP_FALLBACK without a list), always 1..CAP_MAX; extraSlots(uuid) = the rank
# hook RANK_FN (LATER: nobody publishes it yet; 0 when missing / failing); capFor(uuid) = the ONE limit every check uses. All read the
# bridge at each call (no cache, never throw, no SkyyProfiles monitor held - safe from any thread).
M(cfg, r"""
public static int classCount() {''', '''# 0.1.4: THE PROFILE LIMIT. 0.1.9: listCount() = the distinct class names in SkyyClasses' class:list (-1 = no list: SkyyClasses absent;
# 0.1.4-0.1.8 called it classCount); classCount() = the classes in the GAME = the fallback roster (8 with the Spellblade) + every other
# class:list name (aliases folded) - Skyy 2026-10-08: the cap = the number of classes; baseCap() = the fixed number, or auto =
# classCount() (CAP_FALLBACK only if it were 0), always 1..CAP_MAX; extraSlots(uuid) = the rank hook RANK_FN (LATER: nobody publishes
# it yet; 0 when missing / failing); bonusSlots(uuid) = 0.1.9's bonus hook (BONUS_FN, the player's bonusSlots); capFor(uuid) = the ONE
# limit every check uses (at most LIMIT_MAX). All read the bridge at each call (no cache, never throw, no SkyyProfiles monitor held -
# safe from any thread).
M(cfg, r"""
public static int listCount() {''')
rep('''    return seen.size() > 0 ? seen.size() : -1;
  } catch (Throwable t) { return -1; }
}""")
M(cfg, r"""
public static boolean isAuto() {''', '''    return seen.size() > 0 ? seen.size() : -1;
  } catch (Throwable t) { return -1; }
}""")
M(cfg, r"""
public static String knownName(String n) {
  if (n == null) return "";
  String s = n.trim().toLowerCase();
  for (int i = 0; i < KNOWN_ALIAS_FROM.length && i < KNOWN_ALIAS_TO.length; i++) if (KNOWN_ALIAS_FROM[i].equals(s)) return KNOWN_ALIAS_TO[i];
  return s;
}""")
M(cfg, r"""
public static int classCount() {
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < KNOWN.length; i++) seen.add(KNOWN[i]);
  try {
    Object o = bridge().get("class:list");
    if (o instanceof String) {
      String[] parts = ((String) o).split(",");
      for (int i = 0; i < parts.length; i++) {
        String n = parts[i];
        int c = n.indexOf(':');
        if (c >= 0) n = n.substring(0, c);
        n = knownName(n);
        if (n.length() > 0) seen.add(n);
      }
    }
  } catch (Throwable t) { }
  return seen.size();
}""")
M(cfg, r"""
public static boolean isAuto() {''')
# 0.1.9: auto is clamped to LIMIT_MAX (a ninth class gives 9 - the list scrolls); a FIXED number stays 1..CAP_MAX (the choices 1-8)
rep('''  int n = classCount();
  return clampCap((long) (n > 0 ? n : CAP_FALLBACK));
}""")''', '''  long a = (long) classCount();
  if (a < 1L) a = (long) CAP_FALLBACK;
  return a > (long) LIMIT_MAX ? LIMIT_MAX : (int) a;
}""")''')
rep('''M(cfg, r"""
public static int capFor(java.util.UUID u) {
  long c = (long) baseCap() + (long) extraSlots(u);
  return c > (long) CAP_MAX ? CAP_MAX : (int) c;
}""")
M(cfg, r"""
public static String capWhy(java.util.UUID u) {
  String w = !isAuto() ? "the limit on this server" : (classCount() > 0 ? "one per class you can play" : "the default limit");
  int ex = extraSlots(u);
  if (ex > 0) w = w + " + " + ex + " from your rank";
  return w;
}""")
M(cfg, r"""
public static String capNote() {
  if (!isAuto()) return "fixed " + baseCap();
  if (classCount() > 0) return "auto = " + baseCap() + " - one per playable class";
  return "auto = " + baseCap() + " until SkyyClasses lists its classes";
}""")''', '''# 0.1.9: the bonus hook - SkyyProfiles' own bridge Function BONUS_FN (BonusFn: the players file's bonusSlots); missing = 0 silently
# (SkyyProfiles not set up yet / a harness), a wrong answer or a throw = 0 with one WARN per JVM - the rank hook's rules
M(cfg, r"""
public static void bonusWarn(String msg) {
  if (BONUS_WARNED) return;
  BONUS_WARNED = true;
  warn(msg + " - no bonus profile slots from it (logged once)");
}""")
M(cfg, r"""
public static int bonusSlots(java.util.UUID u) {
  if (u == null) return 0;
  try {
    Object f = bridge().get(BONUS_FN);
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Number) {
      long v = ((Number) r).longValue();
      if (v <= 0L) return 0;
      return v > (long) LIMIT_MAX ? LIMIT_MAX : (int) v;
    }
    if (r != null) bonusWarn(BONUS_FN + " answered " + r + " (not a number)");
  } catch (Throwable t) { bonusWarn(BONUS_FN + " failed: " + t); }
  return 0;
}""")
M(cfg, r"""
public static int capFor(java.util.UUID u) {
  long c = (long) baseCap() + (long) extraSlots(u) + (long) bonusSlots(u);
  return c > (long) LIMIT_MAX ? LIMIT_MAX : (int) c;
}""")
M(cfg, r"""
public static String capWhy(java.util.UUID u) {
  String w = !isAuto() ? "the limit on this server" : "one per class";
  int ex = extraSlots(u);
  if (ex > 0) w = w + " + " + ex + " from your rank";
  int bo = bonusSlots(u);
  if (bo > 0) w = w + " + " + bo + " bonus";
  return w;
}""")
M(cfg, r"""
public static String capNote() {
  if (!isAuto()) return "fixed " + baseCap();
  int l = listCount();
  return "auto = " + baseCap() + " - one per class (" + (l > 0 ? l + " playable in SkyyClasses" : "SkyyClasses not loaded") + ")";
}""")''')

# ---------------------------------------------------------------------------------------------------------------- ProfStore: bonusSlots
rep('''M(sto, r"""
public static synchronized void touch(java.util.UUID u) {''', '''# 0.1.9: bonus profile slots (players file bonusSlots, absent = 0; never negative, at most LIMIT_MAX). setBonus = one atomic commit
# under the store lock like setClass (refused while the file is unreadable); 0 removes the key. Nothing is published: capFor reads it.
M(sto, r"""
public static int bonusOf(java.util.Properties p) {
  long v = num(p, "bonusSlots");
  if (v <= 0L) return 0;
  return v > (long) @PKG@.ProfCfg.LIMIT_MAX ? @PKG@.ProfCfg.LIMIT_MAX : (int) v;
}""")
M(sto, r"""
public static synchronized boolean setBonus(java.util.UUID u, int n) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (n <= 0) q.remove("bonusSlots");
  else q.setProperty("bonusSlots", String.valueOf(n > @PKG@.ProfCfg.LIMIT_MAX ? @PKG@.ProfCfg.LIMIT_MAX : n));
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized void touch(java.util.UUID u) {''')

# ---------------------------------------------------------------------------------------------------------------- BonusFn + AdmBonusCmd
rep('''pl   = pool.makeClass(PKG + ".SkyyProfilesPlugin", pool.get(T["JP"]))''',
    '''bfn  = pool.makeClass(PKG + ".BonusFn")                              # 0.1.9: bridge profile:fn:bonusSlots
abon = pool.makeClass(PKG + ".AdmBonusCmd", pool.get(T["APC"]))      # 0.1.9: /profileadmin bonus <player> <n>
pl   = pool.makeClass(PKG + ".SkyyProfilesPlugin", pool.get(T["JP"]))''')
rep('''M(sfn, r"""
public Object apply(Object o) {
  try {
    if (o instanceof String) return @PKG@.ProfDel.state((String) o);
  } catch (Throwable t) { }
  return null;
}""")
''', '''M(sfn, r"""
public Object apply(Object o) {
  try {
    if (o instanceof String) return @PKG@.ProfDel.state((String) o);
  } catch (Throwable t) { }
  return null;
}""")

# ================= BonusFn (0.1.9): bridge profile:fn:bonusSlots =================
# apply(UUID) -> Integer bonus slots (0 = none); apply(Object[] { UUID, Number n }) -> Integer (set to n, clamped 0..LIMIT_MAX; 0 removes
# the key) or null (bad arguments, unreadable players file, write failed). For a future rank / "earn it in game" mod (Skyy 2026-10-08:
# "upgrade: ranks and earn in game later" - the method is OPEN). Never throws, never calls another mod; I/O only under the store lock.
bfn.addInterface(pool.get("java.util.function.Function"))
C(bfn, "public BonusFn() { }")
M(bfn, r"""
public Object apply(Object o) {
  try {
    if (o instanceof java.util.UUID) return Integer.valueOf(@PKG@.ProfStore.bonusOf(@PKG@.ProfStore.load((java.util.UUID) o)));
    if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof Number)) return null;
      java.util.UUID u = (java.util.UUID) a[0];
      long v = ((Number) a[1]).longValue();
      if (v < 0L) v = 0L;
      if (v > (long) @PKG@.ProfCfg.LIMIT_MAX) v = (long) @PKG@.ProfCfg.LIMIT_MAX;
      int was = @PKG@.ProfStore.bonusOf(@PKG@.ProfStore.load(u));
      if (!@PKG@.ProfStore.setBonus(u, (int) v)) return null;
      if (was != (int) v) @PKG@.ProfStore.log("BONUS " + u + " " + was + " -> " + v + " (bridge)");
      return Integer.valueOf((int) v);
    }
  } catch (Throwable t) { }
  return null;
}""")
''')
rep('''C(aarc, r"""
public AdmArchiveCmd() {''', '''# 0.1.9: /profileadmin bonus <player|uuid> <0-16> - a player's bonus profile slots (the hook for ranks / earning them in game later).
# run() is the whole logic (the harness executes it); execute() adds the permission check and the target's chat line.
F(abon, "public @RA@ playerArg;")
F(abon, "public @RA@ numArg;")
C(abon, r"""
public AdmBonusCmd() {
  super("bonus", "(admin) Extra profile slots for one player: /profileadmin bonus <player|uuid> <0-@LIM@> (0 removes them)");
  requirePermission("skyyprofiles.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "player name (online, or seen before) or uuid", @ATY@.STRING);
  this.numArg = withRequiredArg("slots", "bonus profile slots 0-@LIM@ (added to the limit)", @ATY@.STRING);
}""".replace("@LIM@", str(LIMIT_MAX)))
M(abon, r"""
public static String run(String who, String n, String by) {
  java.util.UUID t = @PKG@.ProfStore.resolve(who);
  if (t == null) return "Unknown player - use a name (online or seen before) or a uuid.";
  int v = -1;
  try { v = Integer.parseInt(n == null ? "" : n.trim()); } catch (Throwable e) { v = -1; }
  if (v < 0 || v > @PKG@.ProfCfg.LIMIT_MAX) return "Bonus slots must be a whole number 0-" + @PKG@.ProfCfg.LIMIT_MAX + " (0 removes them).";
  java.util.Properties p = @PKG@.ProfStore.load(t);
  String nm = p.getProperty("username");
  if (nm != null && nm.trim().length() == 0) nm = null;
  if (nm == null) {
    try { @PR@ op = @UNI@.get().getPlayer(t); if (op != null) nm = op.getUsername(); } catch (Throwable e) { nm = null; }
  }
  if (nm == null && p.isEmpty()) return "Unknown player - use a name (online or seen before) or a uuid.";
  if (nm == null) nm = who.trim();
  int was = @PKG@.ProfStore.bonusOf(p);
  if (!@PKG@.ProfStore.setBonus(t, v)) return "Could not save the change (see the server log).";
  @PKG@.ProfStore.log("BONUS " + t + " (" + nm + ") " + was + " -> " + v + " by " + by);
  boolean self = by != null && by.equalsIgnoreCase(nm);
  return "+" + (self ? "Your bonus profile slots" : "Bonus profile slots for " + nm) + ": " + was + " -> " + v + ". " + (self ? "Your" : "Their") + " limit is now " + @PKG@.ProfCfg.capFor(t) + " (" + @PKG@.ProfCfg.capWhy(t) + "). " + @PKG@.ProfStore.describe(t);
}""")
M(abon, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
    String r = run(String.valueOf(ctx.get(this.playerArg)), String.valueOf(ctx.get(this.numArg)), pr.getUsername());
    boolean ok = r.startsWith("+");
    pr.sendMessage(@MSG@.raw("[Profiles] " + (ok ? r.substring(1) : r)));
    if (ok) {
      java.util.UUID t = @PKG@.ProfStore.resolve(String.valueOf(ctx.get(this.playerArg)));
      @PR@ tp = t == null ? null : @UNI@.get().getPlayer(t);
      if (tp != null && tp.isValid() && !t.equals(pr.getUuid())) tp.sendMessage(@MSG@.raw("[Profiles] An admin changed your profile slots - you can have " + @PKG@.ProfCfg.capFor(t) + " profiles now.").color("#ffc800"));
    }
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profileadmin bonus <player|uuid> <0-@LIM@>")); }
}""".replace("@LIM@", str(LIMIT_MAX)))
C(aarc, r"""
public AdmArchiveCmd() {''')
rep('''  super("profileadmin", "(admin) /profileadmin info <player> | setclass <player> <n> <class> | archive list|restore | config | set <setting> <value> | reload");''',
    '''  super("profileadmin", "(admin) /profileadmin info <player> | setclass <player> <n> <class> | bonus <player> <n> | archive list|restore | config | set <setting> <value> | reload");''')
rep('''  addSubCommand(new @PKG@.AdmArchiveCmd());
}""")''', '''  addSubCommand(new @PKG@.AdmArchiveCmd());
  addSubCommand(new @PKG@.AdmBonusCmd());       // 0.1.9
}""")''')
rep('''  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin info <player|uuid> | setclass <player|uuid> <profile> <class> | archive list <player> | archive restore <player> <name> | config | set <setting> <value|default> | reload"));''',
    '''  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin info <player|uuid> | setclass <player|uuid> <profile> <class> | bonus <player|uuid> <slots> | archive list <player> | archive restore <player> <name> | config | set <setting> <value|default> | reload"));''')
rep('''  @PKG@.ProfCfg.bridge().put("profile:fn:state", new @PKG@.StateFn());     // 0.1.5
''', '''  @PKG@.ProfCfg.bridge().put("profile:fn:state", new @PKG@.StateFn());     // 0.1.5
  @PKG@.ProfCfg.bridge().put(@PKG@.ProfCfg.BONUS_FN, new @PKG@.BonusFn());  // 0.1.9: bonus profile slots (players file bonusSlots)
''')
rep('''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, hp, sw, clr, dlt, swp, sfn, page,''',
    '''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, hp, sw, clr, dlt, swp, sfn, bfn, page,''')
rep('''       pres, pcmd, ainf, acls, arel, acfg, aset, aarl, aarr, aarc, adm, pl)''',
    '''       pres, pcmd, ainf, acls, arel, acfg, aset, aarl, aarr, abon, aarc, adm, pl)''')

# ---------------------------------------------------------------------------------------------------------------- pages: scrolling lists
rep('''# 0.1.4: the SKYY CARD is 92 px high (was 84): the list view holds CAP_MAX = 8 profile cards (sub margin 10 -> 6, info margin 8 -> 4),
# the Create Profile well 7 class cards (MAX_CARDS) + the new limit line #SkyyPfSlots ("This is profile N of M - ...") under them;
# every limit in both views is ProfCfg.capFor(u) (auto = one per playable class; rank extras later).''',
    '''# 0.1.4: the SKYY CARD is 92 px high (was 84): the list view holds CAP_MAX = 8 profile cards (sub margin 10 -> 6, info margin 8 -> 4),
# the Create Profile well 7 class cards (MAX_CARDS) + the new limit line #SkyyPfSlots ("This is profile N of M - ...") under them;
# every limit in both views is ProfCfg.capFor(u) (auto = one per playable class; rank extras later).
# 0.1.9: both wells SCROLL (the kit's scroll_list(well=True): vanilla TopScrolling + @DefaultScrollbarStyle, padding 4 = the old
# panel well) at the same heights (8 profile cards / CREATE_ROWS = 7 class cards visible); every card is PF_SCROLL_W = 12 px narrower
# (the 6 px scrollbar + its 6 px spacing). The list draws up to LIST_MAX cards, the Create Profile page up to MAX_CARDS.''')
rep('''PF_CLOSE_GAP = 12                       # 0.1.5: footer text | 12 px | Close
''', '''PF_CLOSE_GAP = 12                       # 0.1.5: footer text | 12 px | Close
PF_SCROLL_W = SUI.SCROLL_SIZE + SUI.SCROLL_SPACING   # 0.1.9: room for the scroll list's scrollbar (6 + 6 px) right of the cards


def scroll_well(ident, h):
    """0.1.9: the cards' list well as a vanilla SCROLLING list (TopScrolling + @DefaultScrollbarStyle on the well tone, padding 4 =
    card_list's panel well) - vanilla never paginates."""
    assert CARD_LIST_PAD == SUI.WELL_LIST_PAD
    return SUI.scroll_list(ident, h=h, well=True, pad=CARD_LIST_PAD)
''')
rep('''  boolean roomNew = n < max && shown.length < @PKG@.ProfCfg.CAP_MAX;''',
    '''  boolean roomNew = n < max && shown.length < LIST_MAX;''')
rep('''    cw = W - 2 * CARD_LIST_PAD
    ident = SUI.J("id", "1")''', '''    cw = W - 2 * CARD_LIST_PAD - PF_SCROLL_W      # 0.1.9: the list scrolls
    ident = SUI.J("id", "1")''')
rep('''        "LIST": SUI.java_append(body, card_list("SkyyPfList", list_h)),''',
    '''        "LIST": SUI.java_append(body, scroll_well("SkyyPfList", list_h)),      # 0.1.9: scrolls (8 visible)''')
rep('''    """ProfilePage.buildCreate(): PF_BUILD_CREATE with its {{parts}} built from kit calls. The list well holds MAX_CARDS cards
    (0.1.4: 7 at the 92 px card height), then the limit line; the heights fill the body exactly (asserted)."""
    heights = [PF_NAME_H + 8, PF_CSUB_H + 8, card_list_h(MAX_CARDS), 8 + PF_SLOTS_H, 8 + PF_END_H, 8 + PF_INFO_H]''',
    '''    """ProfilePage.buildCreate(): PF_BUILD_CREATE with its {{parts}} built from kit calls. The list well shows CREATE_ROWS cards
    (0.1.4: 7 at the 92 px card height; 0.1.9: it scrolls, up to MAX_CARDS), then the limit line; the heights fill the body exactly."""
    heights = [PF_NAME_H + 8, PF_CSUB_H + 8, card_list_h(CREATE_ROWS), 8 + PF_SLOTS_H, 8 + PF_END_H, 8 + PF_INFO_H]''')
rep('''    body, W = sh.body, sh.inner_w
    cw = W - 2 * CARD_LIST_PAD
    i = SUI.J("i")''', '''    body, W = sh.body, sh.inner_w
    cw = W - 2 * CARD_LIST_PAD - PF_SCROLL_W      # 0.1.9: the list scrolls
    i = SUI.J("i")''')
rep('''        "LIST": SUI.java_append(body, card_list("SkyyPfList", card_list_h(MAX_CARDS))),''',
    '''        "LIST": SUI.java_append(body, scroll_well("SkyyPfList", card_list_h(CREATE_ROWS))),     # 0.1.9: scrolls (7 visible)''')
rep('''print("profiles page %dx%d (body %dx%d): list view (%d profile cards) + Create Profile (%d class cards), cards %d px, kit %s"
      % (PF_W, PF_H, PF_LIST_SHELL.inner_w, PF_LIST_SHELL.inner_h, CAP_MAX, MAX_CARDS, CARD_H, SUI.kit_id()))
print("profile limit: default %s (one per class SkyyClasses lists as playable; %d without SkyyClasses), fixed 1-%d, rank hook %s (read only)"
      % (DEF_CAP, CAP_FALLBACK, CAP_MAX, RANK_FN))''',
    '''print("profiles page %dx%d (body %dx%d): list view (%d of up to %d profile cards visible, scrolls) + Create Profile (%d of up to %d class"
      " cards visible, scrolls), cards %d px, kit %s" % (PF_W, PF_H, PF_LIST_SHELL.inner_w, PF_LIST_SHELL.inner_h, CAP_MAX, LIST_MAX,
                                                          CREATE_ROWS, MAX_CARDS, CARD_H, SUI.kit_id()))
print("profile limit: default %s (one per class in the game: %d known here + any other SkyyClasses class), fixed 1-%d, + rank hook %s"
      " + bonus %s, total at most %d" % (DEF_CAP, len(CLASSES), CAP_MAX, RANK_FN, BONUS_FN, LIMIT_MAX))''')
rep('''F(page, "public static final int MAX_CARDS = %d;" % MAX_CARDS)      # cards drawn + pfcls<i> handled (0.1.1: 6, 0.1.2-0.1.3: 8, 0.1.4: 7)
''', '''F(page, "public static final int MAX_CARDS = %d;" % MAX_CARDS)      # cards drawn + pfcls<i> handled (0.1.1: 6, 0.1.2-0.1.3: 8, 0.1.4: 7, 0.1.9: 12)
F(page, "public static final int LIST_MAX = %d;" % LIST_MAX)        # 0.1.9: profile cards drawn on the (scrolling) list (0.1.5-0.1.8: CAP_MAX 8)
''')
rep('''  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < @PKG@.ProfCfg.CAP_MAX; i++) {''',
    '''  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < LIST_MAX; i++) {''', count=2)
rep('''m = B.manifest("SkyyProfiles", VERSION, "SkyWynn profiles (SkyBlock style): each profile is its own save - class (Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk; picked at creation,''',
    '''m = B.manifest("SkyyProfiles", VERSION, "SkyWynn profiles (SkyBlock style): one profile per class - each is its own save - class (Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk; Spellblade later; picked at creation,''')

# ---------------------------------------------------------------------------------------------------------------- self-checks
_code = s[s.index('VERSION = "0.1.9"'):]
assert "card_list(\"SkyyPfList\"" not in _code, "0.1.9: both lists scroll"
assert _code.count("scroll_well(\"SkyyPfList\"") == 2
assert "ProfCfg.CAP_MAX" not in _code, "0.1.9: no page / check uses CAP_MAX as the total limit"
_u = s
for _new, _old, _n in reversed(CHANGES):
    assert _u.count(_new) == _n, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.1.8 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.8 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
