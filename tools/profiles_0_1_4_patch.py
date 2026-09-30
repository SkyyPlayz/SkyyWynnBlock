"""Derive SkyyProfiles/build_skyyprofiles_0.1.4.py from the LIVE 0.1.3 (build_skyyprofiles_0.1.3.py = the tools/deploy_set.py SET pin).
Run:  python tools/profiles_0_1_4_patch.py   then   python SkyyProfiles/build_skyyprofiles_0.1.4.py   (never --deploy: coordinated deploy)
Patch chain (the 0.1.3 header): 0.1 -> 0.1.1 (copy + edit) -> tools/profiles_0_1_2_patch.py -> 0.1.2 -> tools/profiles_0_1_3_patch.py ->
0.1.3 -> THIS patch -> 0.1.4. Edit THIS file, never the generated build script.

0.1.4 = the automatic profile limit. Skyy (2026-09-30): "lets make the default profile cap match the number of classes, and we can get
more profiles later with ranks."
  - maxProfiles is a CHOICE now: "auto" (the new default) or a fixed 1-8. auto = the number of classes a player can pick right now,
    read at every use from the SkyyClasses bridge key class:list ("Name:Skill,..." of the ENABLED classes; SkyyClasses puts it in
    setup() since 0.1 - no new key needed): 5 today (Archer, Warrior, Mage, Berserker, Priest) and it grows by itself when Assassin /
    Shaman open. Without SkyyClasses (no class:list) auto = 6, the old fixed number. The limit never goes above CAP_MAX = 8: the
    Profiles list holds 8 profile cards (the old 1-6 clamp is gone - the automatic limit must be able to reach the 7 classes).
  - Rank-based extra profiles come LATER; the hook is read-only and nobody publishes it yet: rank:fn:profileSlots = a
    java.util.function.Function apply(UUID) -> Number (extra slots for that player, >= 0) that a future rank mod may put on the bridge.
    SkyyProfiles adds it to the limit (still at most 8; also on top of a fixed number - whether a fixed number is a hard limit is
    OPEN, decided when a rank mod publishes the key), calls it at each use outside every SkyyProfiles monitor, never caches it, and
    treats a missing function / an exception / a non-number as 0 (one WARN per JVM). Not a permission-node pattern on purpose: an op
    holds "*", so any node like skyyprofiles.slots.<n> would hand every op the maximum.
  - Lowering the limit (or a class closing) never deletes or locks a profile: a player above it keeps and switches every profile
    and is refused only a NEW one ("All N profile slots are used."; list footer "N profiles - this server now allows M ...").
  - One-time migration (ProfCfg.capMigrate, setup(), before the load and before the config kit reads the file; marker
    Skyy_SkyyProfiles/cap-auto.properties, delete = run again): a config.properties that is byte for byte the untouched default
    0.1.1-0.1.3 wrote (maxProfiles=6) becomes the 0.1.4 default (maxProfiles=auto); otherwise a lone "maxProfiles=6" line that
    config-changes.log never mentions becomes "maxProfiles=auto" (every other line kept, the old maxProfiles comment updated); any
    other value (or a 6 that was set in game / by command) is KEPT and logged (server log + the marker's note).
  - Config kit row "Profile limit per player" (choice: Auto - one per class / 1 profile ... 8 profiles; live, danger), help and
    NOTE texts; /profileadmin set maxProfiles auto|1-8 goes through the same kit path. danger stays (Server-Setup-Spec lists
    maxProfiles as L, D; a choice row cannot take confirm=down): SkyyMenu's < / > widget (9 choices) saves every step, so every step
    asks its own confirm.
  - Review fix (2026-09-30): the capMigrate "line" path reads / writes config.properties as ISO-8859-1 (was UTF-8, which turned a
    non-UTF-8 byte of an owner's comment into U+FFFD); the texts it writes and matches are ASCII (asserted).
  - Create Profile page: a new line under the class cards (#SkyyPfSlots): "This is profile N of M - one per class you can play."
    (auto) / "- the limit on this server." (a fixed number) / "- the default limit." (auto without SkyyClasses) (+ " + X from your
    rank" once a rank hook answers); "All M profile slots are used ..." when the page is open while the limit dropped. Profiles list
    footer: "N of M profile slots used (one per class you can play)."
  - The shared SKYY CARD block (identical in SkyyClasses 0.1.9 - tools/classes_0_1_9_patch.py; both patches assert CARD_SHA) is
    92 px high (was 84; Skyy saw the Classes cards' descriptions touch the card's bottom edge). So the list view holds 8 profile
    cards (sub line margin 10 -> 6, info margin 8 -> 4) and the Create Profile list well holds 7 class cards (MAX_CARDS 8 -> 7: the
    whole roster SkyyClasses and the fallback table know; an 8th class a newer SkyyClasses might list is not drawn - one WARN).
Everything else (commands, permissions, files, other config rows, bridge keys, switching / creating profiles, the first-join gates,
every event binding, every 0.1.3 element id) is 0.1.3's - asserted below (KEEP blocks + binding lines).
"""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.3.py")
dst = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.3"' in s and "GENERATED by tools/profiles_0_1_3_patch.py from build_skyyprofiles_0.1.2.py" in s, \
    "build_skyyprofiles_0.1.3.py is not the live 0.1.3"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 8, "0.1.3 has 8 event bindings (all in ProfilePage), found %d" % len(BIND0)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:120])
    s = s.replace(old, new)


def cut(a, b, new=""):
    """replace everything from anchor a (included) up to anchor b (kept) with new; returns the text that was cut"""
    global s
    assert s.count(a) == 1, "cut start count %d: %s" % (s.count(a), a[:120])
    assert s.count(b) == 1, "cut end count %d: %s" % (s.count(b), b[:120])
    i, j = s.index(a), s.index(b)
    assert i < j, "cut anchors out of order: %s / %s" % (a[:60], b[:60])
    old = s[i:j]
    s = s[:i] + new + s[j:]
    return old


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source (for unchanged-block asserts)"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


CARD_START = "# =====================================================================================================================\n# SKYY CARD"
CARD_END = "# ======================================================================= (end of the shared SKYY CARD block)"
# blocks that must come out of this patch byte-identical
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", "\nFRUITS = ["),
        block("\nBAD_UI = set(", "CFG_LINES = [\n"),
        block('F(cfg, "public static volatile long OPEN_DELAY_MS', 'F(cfg, "public static final String[] DEFAULT_LINES'),
        block('    ("promptEveryLogin", "Create page at every login"', "need(CFG_TEXT.count("),
        block("M(cfg, r\"\"\"\npublic static java.util.Map bridge() {", "# 0.1.1: the running values, WITHOUT reading the file"),
        block("# ================= ProfRoster: class cards", "M(sto, r\"\"\"\npublic static String describe(java.util.UUID u) {"),
        block("M(sto, r\"\"\"\npublic static void log(String line) {", "M(sw, r\"\"\"\npublic static String createAndSwitch("),
        block("  if (@PKG@.ProfStore.BUSY.containsKey(u)) return \"A profile switch is already running.\";\n  String mb = markerBlock(u);\n  if (mb != null) return mb;\n  String why = refuse(st, ref, player);",
              "# ================= ProfilePage: Profiles list (view 0) + Create Profile (view 1) ================="),
        block("M(page, r\"\"\"\npublic static String safe(String t) {", "M(page, PF_LIST_JAVA)"),
        block("M(page, r\"\"\"\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {", "    if (data.indexOf(\"pfnew\\\"\") >= 0) {"),
        block("    java.util.ArrayList r = @PKG@.ProfRoster.roster();\n    for (int i = 0; i < r.size() && i < MAX_CARDS; i++) {",
              "M(page, r\"\"\"\npublic static String open("),
        block("# ================= OpenTask: first-join Create Profile page", "public void setup() {"),
        block("  try {\n    java.nio.file.Files.createDirectories(@PKG@.ProfStore.DIR", "if \"--deploy\" in sys.argv:")]

# ================================================================================================ docstring
rep('''"""SkyyProfiles 0.1.3 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.3.py          -> SkyyProfiles/SkyyProfiles-0.1.3.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_3_patch.py from build_skyyprofiles_0.1.2.py (itself generated by tools/profiles_0_1_2_patch.py from
0.1.1, a copy + edit of 0.1) - edit the patch, never this file. Everything below the 0.1.3, 0.1.2 and 0.1.1 blocks is the 0.1 design,
unchanged unless a line says 0.1.1, 0.1.2 or 0.1.3.
''', '''"""SkyyProfiles 0.1.4 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.4.py          -> SkyyProfiles/SkyyProfiles-0.1.4.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_4_patch.py from build_skyyprofiles_0.1.3.py (generated by tools/profiles_0_1_3_patch.py from 0.1.2,
generated by tools/profiles_0_1_2_patch.py from 0.1.1, a copy + edit of 0.1) - edit the patch, never this file. Everything below the
0.1.4, 0.1.3, 0.1.2 and 0.1.1 blocks is the 0.1 design, unchanged unless a line says 0.1.1, 0.1.2, 0.1.3 or 0.1.4.

0.1.4 (2026-09-30, the automatic profile limit - Skyy: "lets make the default profile cap match the number of classes, and we can get
  more profiles later with ranks."):
  - PROFILE LIMIT: config maxProfiles = auto (NEW DEFAULT) or a fixed 1-8 (a choice row now; 0.1.1-0.1.3: an int 1-6, default 6).
    auto = the number of classes a player can pick right now = the distinct names in the SkyyClasses bridge key class:list (its
    ENABLED classes; SkyyClasses puts it in setup() since 0.1): 5 today (Archer, Warrior, Mage, Berserker, Priest), 6 / 7 by itself
    when Assassin / Shaman open. Read at every use (load order never matters). No class:list (SkyyClasses absent) = 6, the old
    fixed number. Never above CAP_MAX = 8 (the Profiles list holds 8 profile cards). ProfCfg.capFor(uuid) is the one limit every
    check uses (the create refusals, /profiles create, the list page, the Create Profile page, /profiles list).
  - RANK HOOK (for LATER, read-only; nobody publishes it yet): rank:fn:profileSlots = java.util.function.Function apply(UUID) ->
    Number = extra profile slots for that player (>= 0), put on the bridge by a future rank mod. Added to the limit (still at most
    8) - to auto AND to a fixed number (fixed 3 + rank 2 = 5; whether a fixed number should be a hard limit instead is OPEN, to
    decide when a rank mod publishes the key); called at each use on the caller's thread, outside every SkyyProfiles monitor,
    never cached; missing / throws / not a number
    = 0 (one WARN per JVM). The provider must answer fast (no I/O), never throw and never call SkyyProfiles back. Deliberately NOT
    a permission-node pattern: an op holds "*", so a node like skyyprofiles.slots.<n> would hand every op the maximum.
  - LOWERING NEVER DELETES OR LOCKS A PROFILE: the limit only refuses a NEW profile. A player above it keeps, sees and switches every
    profile ("N profiles - this server now allows M. You keep them all but cannot create more.").
  - ONE-TIME MIGRATION (ProfCfg.capMigrate in setup(), after upgradeDefault, before the load and before the config kit reads the
    file; marker Skyy_SkyyProfiles/cap-auto.properties with result + note, delete it to run again): config.properties byte for byte
    the untouched default 0.1.1-0.1.3 wrote -> the 0.1.4 default file (maxProfiles=auto); else one "maxProfiles=6" line that
    config-changes.log(.1-.3) never mentions -> "maxProfiles=auto" (the rest of the file byte for byte in any encoding: read and
    written as ISO-8859-1; the old maxProfiles comment line replaced by the new one, CRLF kept); any other value, several
    maxProfiles lines, or a 6 set in game / by command before -> KEPT and logged (server log line + the marker). No players /
    inventories / markers are touched.
  - CONFIG KIT: row maxProfiles "Profile limit per player" = choice auto|Auto - one per class, 1|1 profile ... 8|8 profiles (live,
    danger; field ProfCfg.MAX_SETTING, a String: "auto" or "1".."8"); /profileadmin set maxProfiles auto|<n> takes the same path.
    danger stays (Server-Setup-Spec: maxProfiles L, D; a choice row takes only confirm=always|never): SkyyMenu's < / > widget
    saves every step it passes, so each step asks its own confirm (auto -> 2 = two confirmed steps through 1; < from auto wraps
    to 8). One step to any value: /profileadmin set maxProfiles <n>.
    ProfCfg.load (the RELOAD routine) reads auto or a number (clamped 1-8; "5 profiles" reads as 5; anything else keeps the value).
  - PAGES: Create Profile shows "This is profile N of M - one per class you can play." (#SkyyPfSlots, under the class cards; "- the
    limit on this server." for a fixed number, "- the default limit." for auto without SkyyClasses, + " + X from your rank" with a
    rank hook; "All M profile slots are used - you cannot create another profile." when the limit dropped while it was open). The
    list footer says "N of M profile slots used (one per class you can play)." The shared SKYY CARD is 92 px high (was 84; the same
    block as SkyyClasses 0.1.9 - the Classes cards' two-line descriptions touched the card's bottom edge in game): the list view holds
    8 profile cards (sub margin 10 -> 6, info margin 8 -> 4), the Create Profile list well 7 class cards (MAX_CARDS 8 -> 7 = every
    class SkyyClasses and the fallback roster know; an 8th listed class is not drawn and logs one WARN).
  Event bindings, element ids of 0.1.3, commands, permissions, files, bridge keys and the switch / create code paths are unchanged.
''')
rep('PROFILES: ids "1".."N" per player (config maxProfiles, default 6 since 0.1.1, 1-6).',
    'PROFILES: ids "1".."N" per player (config maxProfiles: 0.1.4 default auto = one per playable class, or a fixed 1-8).')
rep('''  config-changes.log, config-history/   0.1.1: the kit's change log and file versions (tools/CONFIG-CONTRACT.md)
''', '''  config-changes.log, config-history/   0.1.1: the kit's change log and file versions (tools/CONFIG-CONTRACT.md)
  cap-auto.properties      0.1.4: the one-time profile-limit migration marker (migratedAt, result, kept, note, version; delete = run again)
''')

# ================================================================================================ version, data constants
rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')
rep('''DEF_MAX_PROFILES = 6                   # 0.1.1: Skyy locked 6 (2026-09-24), was 4. The 1-6 clamp stays (no way above 6 yet)
''', '''DEF_CAP = "auto"                       # 0.1.4 (Skyy 2026-09-30): maxProfiles default = one profile per class a player can pick right now
CAP_FALLBACK = 6                       # 0.1.4: auto without SkyyClasses (no class:list) = the old fixed default (0.1.1-0.1.3: 6)
CAP_MAX = 8                            # 0.1.4: the highest limit (fixed or auto + rank extras): the Profiles list holds 8 profile cards
RANK_FN = "rank:fn:profileSlots"       # 0.1.4: read-only hook for LATER (a rank mod may publish it; nobody does yet) - see the docstring
''')
rep('''MAX_CARDS = 8                          # 0.1.2: class cards drawn on the Create Profile page AND pfcls<i> payloads handled (0.1.1: 6)
''', '''MAX_CARDS = 7                          # class cards drawn on the Create Profile page AND pfcls<i> payloads handled (0.1.1: 6, 0.1.2 /
                                       # 0.1.3: 8; 0.1.4: 7 - the 92 px SKYY CARD leaves room for 7 = every class SkyyClasses knows)
''')
need_caps = '''need(1 <= CAP_FALLBACK <= CAP_MAX and CAP_MAX >= len(CLASSES), "CAP_MAX must reach every class (the automatic limit grows with them)")
'''
rep('''need(len(CLASSES) <= MAX_CARDS, "the fallback roster has more classes than the Create Profile page draws")
''', '''need(len(CLASSES) <= MAX_CARDS, "the fallback roster has more classes than the Create Profile page draws")
''' + need_caps)

# ================================================================================================ the default config file
OLD_CFG = cut("CFG_LINES = [\n", 'F(cfg, "public static java.nio.file.Path FILE;")', "@@CFG_LINES@@")
_ns = {"DEF_MAX_PROFILES": 6, "DEF_OPEN_DELAY_MS": 2000, "DEF_COMBAT_S": 10, "DEF_KEEP": "Skyy_Menu"}
exec(OLD_CFG, _ns)
CFG_011 = _ns["CFG_LINES"]
assert CFG_011[4] == "maxProfiles=6" and CFG_011[2].startswith("# maxProfiles = profile slots per player (1-6).") and len(CFG_011) == 19
NEW_CAP_COMMENT = [
    "# maxProfiles = profile slots per player: auto = one per class a player can pick right now (the classes SkyyClasses lists as",
    "#   playable - it grows by itself when a class opens; 6 without SkyyClasses) or a fixed number 1-8. Each profile = its own",
    "#   class, island, coins, skills, bags and vanilla inventory.",
]
assert all(ord(c) < 128 for c in "".join(NEW_CAP_COMMENT) + CFG_011[2]), "capMigrate's line path is ISO-8859-1: its texts must be ASCII"
rep("@@CFG_LINES@@", '''# 0.1.4: the default file 0.1.1-0.1.3 wrote (maxProfiles=6), byte for byte - ProfCfg.capMigrate replaces a file still EXACTLY equal to
# it (nobody ever edited it) by the 0.1.4 default below, once (marker cap-auto.properties)
CFG_LINES_011 = %s
CFG_LINES = CFG_LINES_011[:2] + [
    %s,
    %s,
    %s,
] + [CFG_LINES_011[3], "maxProfiles=%%s" %% DEF_CAP] + CFG_LINES_011[5:]
need(CFG_LINES[5] == "#   Lowering it never deletes a profile: players above it keep theirs but cannot create new ones.", "cap comment")
need(all(ord(c) < 128 for c in "".join(CFG_LINES[2:5]) + CFG_LINES_011[2]),
     "the maxProfiles comments must be ASCII (ProfCfg.capMigrate's line path works in ISO-8859-1)")
''' % ("[\n" + "".join("    %r,\n" % ln for ln in CFG_011) + "]", repr(NEW_CAP_COMMENT[0]), repr(NEW_CAP_COMMENT[1]),
       repr(NEW_CAP_COMMENT[2])))

# ================================================================================================ ProfCfg fields
rep('F(cfg, "public static volatile int MAX_PROFILES = %d;" % DEF_MAX_PROFILES)\n',
    '''F(cfg, "public static volatile String MAX_SETTING = %s;" % jstr(DEF_CAP))    # 0.1.4: maxProfiles = "auto" or "1".."8" (the kit row's field)
F(cfg, "public static final int CAP_MAX = %d;" % CAP_MAX)
F(cfg, "public static final int CAP_FALLBACK = %d;" % CAP_FALLBACK)
F(cfg, "public static final String RANK_FN = %s;" % jstr(RANK_FN))
F(cfg, "public static volatile boolean RANK_WARNED = false;")
''')
rep('F(cfg, "public static final String[] OLD_LINES = %s;" % jarr(CFG_LINES_01))\n',
    '''F(cfg, "public static final String[] OLD_LINES = %s;" % jarr(CFG_LINES_01))
F(cfg, "public static final String[] OLD011_LINES = %s;" % jarr(CFG_LINES_011))      # 0.1.4: the untouched 0.1.1-0.1.3 default file
F(cfg, "public static final String OLD_CAP_COMMENT = %s;" % jstr(CFG_LINES_011[2]))   # ... its maxProfiles comment line
F(cfg, "public static final String[] NEW_CAP_COMMENT = %s;" % jarr(CFG_LINES[2:5]))   # the 0.1.4 comment lines that replace it
''')

# ================================================================================================ config kit row + texts
CAP_OPTS = ",".join(["auto|Auto - one per class"] + ["%d|%d profile%s" % (n, n, "" if n == 1 else "s") for n in range(1, 9)])
rep('''    ("maxProfiles", "Profile slots per player", "profiles", "int", str(DEF_MAX_PROFILES), "1", "6", "step=1", "", "live,danger",
     "Lowering it never deletes a profile: players above it keep theirs but cannot create more.",
     "field:ProfCfg.MAX_PROFILES@config.properties:maxProfiles"),''',
    '''    # 0.1.4: a choice - auto (one per class a player can pick, from SkyyClasses' class:list; 6 without it) or a fixed 1-8;
    # danger kept (Server-Setup-Spec: L, D; a choice row takes no confirm=down): SkyyMenu's < / > saves and confirms each step
    ("maxProfiles", "Profile limit per player", "profiles", "choice", DEF_CAP, "", "", CAP_OPTS, "", "live,danger",
     "Auto = one per class players can pick (grows as classes open). Lowering never deletes a profile.",
     "field:ProfCfg.MAX_SETTING@config.properties:maxProfiles"),''')
rep('''CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding)''',
    '''CAP_OPTS = %r
need(CAP_OPTS.split(",")[0].split("|")[0] == DEF_CAP and len(CAP_OPTS.split(",")) == CAP_MAX + 1, "maxProfiles choices: auto + 1..CAP_MAX")
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding)''' % CAP_OPTS)
rep('''need(CFG_TEXT.count("\\nmaxProfiles=%d\\n" % DEF_MAX_PROFILES) == 1 and ("keepItems=%s\\n" % DEF_KEEP) in CFG_TEXT,
     "CFG_TEXT sanity check failed: need exactly one maxProfiles=%d line and a keepItems=%s line" % (DEF_MAX_PROFILES, DEF_KEEP))''',
    '''need(CFG_TEXT.count("\\nmaxProfiles=%s\\n" % DEF_CAP) == 1 and ("keepItems=%s\\n" % DEF_KEEP) in CFG_TEXT,
     "CFG_TEXT sanity check failed: need exactly one maxProfiles=%s line and a keepItems=%s line" % (DEF_CAP, DEF_KEEP))
need("\\n".join(CFG_LINES_011) + "\\n" != CFG_TEXT and CFG_LINES_011.count("maxProfiles=6") == 1, "the 0.1.1 default differs from 0.1.4's")''')
rep('''               NOTE="Slots are 1-6: a way above 6 is not decided yet. Player fixes: /profileadmin info and setclass.",''',
    '''               NOTE="Auto = one profile per playable class (6 without SkyyClasses). Fixes: /profileadmin info, setclass.",''')

# ================================================================================================ ProfCfg: the limit, the migration
CAP_JAVA = r'''# 0.1.4: THE PROFILE LIMIT. classCount() = the distinct class names in SkyyClasses' class:list (-1 = no list: SkyyClasses absent);
# baseCap() = the fixed number, or auto = classCount() (CAP_FALLBACK without a list), always 1..CAP_MAX; extraSlots(uuid) = the rank
# hook RANK_FN (LATER: nobody publishes it yet; 0 when missing / failing); capFor(uuid) = the ONE limit every check uses. All read the
# bridge at each call (no cache, never throw, no SkyyProfiles monitor held - safe from any thread).
M(cfg, r"""
public static int classCount() {
  try {
    Object o = bridge().get("class:list");
    if (!(o instanceof String)) return -1;
    String s = ((String) o).trim();
    if (s.length() == 0) return -1;
    String[] parts = s.split(",");
    java.util.HashSet seen = new java.util.HashSet();
    for (int i = 0; i < parts.length; i++) {
      String n = parts[i];
      int c = n.indexOf(':');
      if (c >= 0) n = n.substring(0, c);
      n = n.trim().toLowerCase();
      if (n.length() > 0) seen.add(n);
    }
    return seen.size() > 0 ? seen.size() : -1;
  } catch (Throwable t) { return -1; }
}""")
M(cfg, r"""
public static boolean isAuto() {
  String m = MAX_SETTING;
  return m == null || m.trim().length() == 0 || m.trim().equalsIgnoreCase("auto");
}""")
M(cfg, r"""
public static int clampCap(long v) {
  if (v < 1L) return 1;
  if (v > (long) CAP_MAX) return CAP_MAX;
  return (int) v;
}""")
M(cfg, r"""
public static int baseCap() {
  if (!isAuto()) {
    try { return clampCap(Long.parseLong(MAX_SETTING.trim())); } catch (Throwable t) { }
  }
  int n = classCount();
  return clampCap((long) (n > 0 ? n : CAP_FALLBACK));
}""")
M(cfg, r"""
public static void rankWarn(String msg) {
  if (RANK_WARNED) return;
  RANK_WARNED = true;
  warn(msg + " - no extra profile slots from it (logged once)");
}""")
M(cfg, r"""
public static int extraSlots(java.util.UUID u) {
  if (u == null) return 0;
  try {
    Object f = bridge().get(RANK_FN);
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Number) {
      long v = ((Number) r).longValue();
      if (v <= 0L) return 0;
      return v > (long) CAP_MAX ? CAP_MAX : (int) v;
    }
    rankWarn(RANK_FN + " answered " + r + " (not a number)");
  } catch (Throwable t) { rankWarn(RANK_FN + " failed: " + t); }
  return 0;
}""")
M(cfg, r"""
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
}""")
M(cfg, r"""
public static byte[] linesBytes(String[] ls) throws java.io.UnsupportedEncodingException {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ls.length; i++) sb.append(ls[i]).append("\n");
  return sb.toString().getBytes("UTF-8");
}""")
# did the config kit ever log a maxProfiles change (in game, by command, a hand edit it noticed)? config-changes.log + its 3 rotations;
# an unreadable log answers true (keep the owner's value)
M(cfg, r"""
public static boolean changedBefore(java.nio.file.Path dir) {
  String[] names = new String[] { "config-changes.log", "config-changes.log.1", "config-changes.log.2", "config-changes.log.3" };
  for (int k = 0; k < names.length; k++) {
    try {
      java.nio.file.Path f = dir.resolve(names[k]);
      if (java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) {
        String[] ls = new String(java.nio.file.Files.readAllBytes(f), "UTF-8").split("\n");
        for (int i = 0; i < ls.length; i++) {
          String[] c = ls[i].split("\t");
          if (c.length >= 5 && c[4].trim().equals("maxProfiles")) return true;
        }
      }
    } catch (Throwable t) { return true; }
  }
  return false;
}""")
# setup() only, after upgradeDefault, BEFORE load() and before the config kit reads the file: maxProfiles 6 -> auto ONCE (marker
# cap-auto.properties next to config.properties; delete it = run again). Returns the server log line, null = nothing to say.
# The "line" path reads and writes the file as ISO-8859-1 (one char per byte), so every byte it does not replace comes back
# unchanged - also a hand-written comment in another encoding (review fix: a UTF-8 round trip turned a Latin-1 byte into U+FFFD);
# the text it puts in (maxProfiles=auto, NEW_CAP_COMMENT) and the comment it matches (OLD_CAP_COMMENT) are ASCII (asserted).
M(cfg, r"""
public static synchronized String capMigrate() {
  try {
    if (FILE == null) return null;
    java.nio.file.Path dir = FILE.getParent();
    java.nio.file.Path mk = dir.resolve("cap-auto.properties");
    if (java.nio.file.Files.exists(mk, new java.nio.file.LinkOption[0])) return null;
    String result = "";
    String note = "";
    String kept = "";
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      result = "new";
      note = "profile limit: no config.properties yet - it starts with maxProfiles=auto (one profile per class a player can pick)";
    } else {
      byte[] have = java.nio.file.Files.readAllBytes(FILE);
      if (java.util.Arrays.equals(have, linesBytes(OLD011_LINES))) {
        atomicWrite(FILE, linesBytes(DEFAULT_LINES));
        result = "default";
        note = "profile limit: config.properties was the untouched default file - replaced by the new default: maxProfiles 6 -> auto (one profile per class a player can pick - it grows as classes open; 6 without SkyyClasses)";
      } else {
        String text = new String(have, "ISO-8859-1");
        String[] ls = text.split("\n", -1);
        int at = -1;
        int found = 0;
        String val = "";
        for (int i = 0; i < ls.length; i++) {
          String t = ls[i].trim();
          if (t.length() == 0 || t.charAt(0) == '#' || t.charAt(0) == '!') continue;
          int e = -1;
          for (int k = 0; k < t.length() && e < 0; k++) {
            char ch = t.charAt(k);
            if (ch == '=' || ch == ':' || ch == ' ' || ch == '\t') e = k;
          }
          String key = e < 0 ? t : t.substring(0, e);
          if (!key.equals("maxProfiles")) continue;
          String v = e < 0 ? "" : t.substring(e + 1).trim();
          if (v.startsWith("=") || v.startsWith(":")) v = v.substring(1).trim();
          found++;
          at = i;
          val = v;
        }
        if (found == 0) {
          result = "missing";
          note = "profile limit: config.properties has no maxProfiles line - the default auto applies (one profile per class a player can pick)";
        } else if (found > 1) {
          result = "kept";
          kept = val;
          note = "profile limit: config.properties has " + found + " maxProfiles lines - left as they are (the last one counts: " + val + "); the new default is auto = one profile per class a player can pick";
        } else if (val.equalsIgnoreCase("auto")) {
          result = "auto";
          note = "profile limit: maxProfiles is already auto (one profile per class a player can pick)";
        } else if (!val.equals("6")) {
          result = "kept";
          kept = val;
          note = "profile limit: kept maxProfiles=" + val + " (a value an owner set) - the new default is auto = one profile per class a player can pick (Server Setup > Profiles > Profile limit per player, or /profileadmin set maxProfiles auto)";
        } else if (changedBefore(dir)) {
          result = "kept";
          kept = val;
          note = "profile limit: kept maxProfiles=6 (it was set in game or by command before - config-changes.log) - the new default is auto = one profile per class a player can pick (/profileadmin set maxProfiles auto)";
        } else {
          String end = ls[at].endsWith("\r") ? "\r" : "";
          ls[at] = "maxProfiles=auto" + end;
          int com = 0;
          for (int i = 0; i < ls.length; i++) {
            String t = ls[i];
            String e2 = t.endsWith("\r") ? "\r" : "";
            if (e2.length() > 0) t = t.substring(0, t.length() - 1);
            if (t.equals(OLD_CAP_COMMENT)) {
              StringBuilder cb = new StringBuilder();
              for (int k = 0; k < NEW_CAP_COMMENT.length; k++) {
                if (k > 0) cb.append(e2).append("\n");
                cb.append(NEW_CAP_COMMENT[k]);
              }
              ls[i] = cb.append(e2).toString();
              com++;
            }
          }
          StringBuilder nb = new StringBuilder();
          for (int i = 0; i < ls.length; i++) {
            if (i > 0) nb.append("\n");
            nb.append(ls[i]);
          }
          atomicWrite(FILE, nb.toString().getBytes("ISO-8859-1"));
          result = "line";
          note = "profile limit: maxProfiles=6 was never changed - now auto (one profile per class a player can pick - it grows as classes open; 6 without SkyyClasses); every other line of config.properties is kept" + (com > 0 ? " (its maxProfiles comment updated)" : "");
        }
      }
    }
    java.util.Properties m = new java.util.Properties();
    m.setProperty("migratedAt", String.valueOf(System.currentTimeMillis()));
    m.setProperty("result", result);
    if (kept.length() > 0) m.setProperty("kept", kept);
    m.setProperty("note", note);
    m.setProperty("version", "__VER__");
    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    m.store(bo, "SkyyProfiles profile limit migration (0.1.4: an untouched maxProfiles=6 -> auto, once; a value an owner set is kept). Delete = run again at the next start.");
    atomicWrite(mk, bo.toByteArray());
    return note;
  } catch (Throwable t) { warn("profile limit migration failed - it runs again at the next start (config.properties is left as it was unless a line above says otherwise): " + t); return null; }
}""".replace("__VER__", VERSION))
'''
rep("# 0.1.1: the running values, WITHOUT reading the file", CAP_JAVA + "# 0.1.1: the running values, WITHOUT reading the file")
rep('''  return "maxProfiles=" + MAX_PROFILES + " combatSeconds=" + (COMBAT_MS / 1000L) + " islandOnSwitch=" + ISLAND_ON_SWITCH''',
    '''  return "maxProfiles=" + MAX_SETTING + " (" + capNote() + ") combatSeconds=" + (COMBAT_MS / 1000L) + " islandOnSwitch=" + ISLAND_ON_SWITCH''')
rep('''    return "config.properties was the untouched file 0.1 wrote - replaced by the 0.1.1 default (maxProfiles 4 -> " + @MAXDEF@ + ", the new default cap)";
  } catch (Throwable t) { warn("could not check config.properties for the untouched 0.1 default (left as it is): " + t); return null; }
}""".replace("@MAXDEF@", str(DEF_MAX_PROFILES)))''',
    '''    return "config.properties was the untouched file 0.1 wrote - replaced by the current default (maxProfiles 4 -> @MAXDEF@: one profile per class a player can pick)";
  } catch (Throwable t) { warn("could not check config.properties for the untouched 0.1 default (left as it is): " + t); return null; }
}""".replace("@MAXDEF@", DEF_CAP))''')
rep('''    long mp = lng(p, "maxProfiles", (long) MAX_PROFILES);
    if (mp < 1L) mp = 1L;
    if (mp > 6L) mp = 6L;
''', '''    String mset = MAX_SETTING;
    String mraw = p.getProperty("maxProfiles");
    if (mraw != null) {
      String mv = mraw.trim();
      int sp = mv.indexOf(' ');
      if (sp > 0) mv = mv.substring(0, sp);
      if (mv.equalsIgnoreCase("auto")) mset = "auto";
      else {
        try { mset = String.valueOf(clampCap(Long.parseLong(mv))); } catch (Throwable t) { }
      }
    }
''')
rep('''    MAX_PROFILES = (int) mp;
''', '''    MAX_SETTING = mset;
''')

# ================================================================================================ the limit at every check
rep('''  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.MAX_PROFILES;''',
    '''  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.capFor(u);''')
rep('''  if (@PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) return "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used.";
  if (@PKG@.ProfStore.BUSY.containsKey(u)) return "A profile switch is already running.";''',
    '''  int cap = @PKG@.ProfCfg.capFor(u);
  if (@PKG@.ProfStore.count(p) >= cap) return "All " + cap + " profile slots are used.";
  if (@PKG@.ProfStore.BUSY.containsKey(u)) return "A profile switch is already running.";''')
rep('''      if (@PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) { this.info = "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used."; rebuild(); return; }''',
    '''      int capn = @PKG@.ProfCfg.capFor(u);
      if (@PKG@.ProfStore.count(p) >= capn) { this.info = "All " + capn + " profile slots are used."; rebuild(); return; }''')
rep('''  if (v == 1 && !first && @PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) return "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used.";''',
    '''  int cap = @PKG@.ProfCfg.capFor(u);
  if (v == 1 && !first && @PKG@.ProfStore.count(p) >= cap) return "All " + cap + " profile slots are used.";''')

# ================================================================================================ the shared SKYY CARD block
CARD_SHA_OLD = "85a047857ef2762641fb7045aee6f5ce9acd4e1ded05f55ba4a2a7496445f7d5"      # SkyyProfiles 0.1.3 / SkyyClasses 0.1.8
OLD_CARD = cut(CARD_START, CARD_END, "@@CARD@@") + CARD_END
s = s.replace("@@CARD@@" + CARD_END, "@@CARD@@", 1)
assert hashlib.sha256(OLD_CARD.encode("utf8")).hexdigest() == CARD_SHA_OLD, "the 0.1.3 SKYY CARD block is not the one 0.1.3 shipped"
CARD_BLOCK = r'''# =====================================================================================================================
# SKYY CARD - the ONE shared card component (research/Skyy-UI-Inventory.md 5.5, 5.17 and section 6 "Class cards"): the class
# cards of SkyyClasses' ClassPage and of SkyyProfiles' Create Profile page, SkyyProfiles' profile cards and its empty-slot card.
# Built from kit calls only (tools/skyyui.py). THE SAME BLOCK is in SkyyClasses 0.1.9 and SkyyProfiles 0.1.4: both patches
# (tools/classes_0_1_9_patch.py, tools/profiles_0_1_4_patch.py) insert it and assert its hash - change it in both together
# (0.1.8 / 0.1.3 carried the same block with CARD_H 84).
# A card is one row of a list well (the vanilla #000000(0.15) list inset, padding 4): Group <card> (LayoutMode Left) = a 4 px status
# bar <card>Bar + the card body <card>In (the state background; side by side, so a look without a bar is one plain colour) holding
# the item cells (the vanilla BarterTradeRow slot border with an ItemIcon) | the text column (up to three label lines, their Text
# is b.set) | the action column (a vanilla button or a state word, appended by the page). Only
# properties the deployed pages already use: LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour
# backgrounds, ItemIcon with an inline ItemId, Wrap (no FlexWeight, no WrapMaxLines, no LayoutMode Center / Full).
# =====================================================================================================================
CARD_H = 92                 # card height: the text lines (name 24 + line two 20 + line three 40 = 84; card_java centres them, so
                            # 4 px stay free above and below) - 0.1.9 / 0.1.4 (Skyy 2026-09-30, seen in game): at 84 the two-line
                            # descriptions (Archer, Berserker, Priest) ran to the card's bottom edge: the three lines really take
                            # 24.6 + 21.8 + 40.9 = 87.3 px at the client's Nunito Sans line height (1.364 em)
CARD_GAP = 4                # space under each card (the OverrideRespawnPointButton option rows: 50 + 4)
CARD_BAR = 4                # status bar at the left edge (WorldEventListRow #StatusBar: 4 px)
CARD_FRAME = 64             # item cell border (BarterTradeRow slot border #1a2530, padding 2) around a 60 px ItemIcon
CARD_CELL = CARD_FRAME + 8  # one icon cell: an 8 px gap + the frame
CARD_ACT_W = 200            # action column: a vanilla normal button (172 = @DefaultButtonMinWidth) centred in it
CARD_BTN_W = SUI.BTN_MIN_W
CARD_PAD_R = 12             # space right of the action column
CARD_LIST_PAD = SUI.WELL_LIST_PAD   # the list well's padding (WorldEventPanelPage #ListContainer: 4)
# card looks: (background, status bar), kit colour names
CARD_LOOKS = {
    "selected": ("rowPressed", "selected"),    # your class / the picked class / the active profile: the WorldEventListRow pressed
                                               # step #182a40(0.9) + its selected blue #4274a5 as the bar (review fix: the active
                                               # tint #7a9cc6(0.25) put the Berserker red at 2.6:1 and the disabled grey at 2.7:1;
                                               # on the pressed step every card text is >= 3.4:1; vanilla's solid #4274a5 row
                                               # would drop the class colours to 1.1-2:1)
    "pending": ("rowHover", "warning"),        # waiting for Confirm: the hovered row #132033(0.8) + the confirm question yellow bar
    "normal": ("row", "row"),                  # the WorldEventListRow panel #101925(0.55); the bar in the card colour = no bar
    "off": ("cardDisabled", "cardDisabled"),   # coming later: BarterTradeRow's disabled card #1a1e24 (+ grey text, covered icons)
    "empty": ("well", "well"),                 # an empty slot: one more step of the list well tone
}


def card_list_h(rows):
    """The height of a list well holding `rows` cards (padding 4 + rows x (card + gap))."""
    return 2 * CARD_LIST_PAD + rows * (CARD_H + CARD_GAP)


def card_list(ident, h, anchor=None):
    """The list well the cards go into (a vanilla panel "well", LayoutMode Top, padding 4)."""
    return SUI.panel(ident, "well", h=h, pad=CARD_LIST_PAD, anchor=anchor)


def card_text_w(w, icon_max):
    """The text column width of a w px card with icon_max item cells."""
    tw = w - CARD_BAR - icon_max * CARD_CELL - CARD_ACT_W - CARD_PAD_R
    SUI.fit([CARD_BAR, icon_max * CARD_CELL, tw, CARD_ACT_W, CARD_PAD_R], w, "card width")
    assert tw >= 240, "card text column too narrow: %d px" % tw
    return tw


def _card_in(outer, *kids):
    """kit markup `outer` with the kit markups `kids` placed inside it (before its closing brace)."""
    assert outer.endswith("}") and kids, outer[:60]
    return outer[:-1] + " ".join(kids) + " }"


def _card_col(col, on):
    """A line colour: a kit colour name or a J(java expr, sample) data colour; with on (a Java boolean expression) the vanilla
    disabled grey when it is false."""
    c = SUI.color(col)
    if on is None:
        return c
    sample = SUI.render(c) if SUI.has_j(c) else c
    return SUI.J("(%s) ? (%s) : %s" % (on, SUI.java_value(c), SUI.java_lit(SUI.COLOR["disabled"])), sample)


def _card_look(look, var):
    """(java declarations, background, bar) for a static look name or [(look, java boolean), ..., last look]."""
    if isinstance(look, str):
        bg, bar = CARD_LOOKS[look]
        return [], SUI.color(bg), SUI.color(bar)
    conds, last = list(look[:-1]), look[-1]
    assert conds and isinstance(last, str), look
    e_bg, e_bar = SUI.java_lit(SUI.color(CARD_LOOKS[last][0])), SUI.java_lit(SUI.color(CARD_LOOKS[last][1]))
    for name, cond in reversed(conds):
        e_bg = "(%s) ? %s : (%s)" % (cond, SUI.java_lit(SUI.color(CARD_LOOKS[name][0])), e_bg)
        e_bar = "(%s) ? %s : (%s)" % (cond, SUI.java_lit(SUI.color(CARD_LOOKS[name][1])), e_bar)
    first = CARD_LOOKS[conds[0][0]]
    decl = ["String %sBg = %s;" % (var, e_bg), "String %sBar = %s;" % (var, e_bar)]
    return decl, SUI.J(var + "Bg", SUI.color(first[0])), SUI.J(var + "Bar", SUI.color(first[1]))


def _card_cell(fid, item, on):
    """One item cell: an 8 px gap + the slot border (padding 2) with the ItemIcon; the coming-later look lays the vanilla
    sold-out cover (BarterTradeRow #0a0e12(0.75)) over it. With on: both looks, picked in the Java (choose)."""
    cell = SUI.group(None, None, w=CARD_CELL, h=CARD_H)
    frame = SUI.item_frame(fid, CARD_FRAME, anchor={"left": CARD_CELL - CARD_FRAME, "top": (CARD_H - CARD_FRAME) // 2})
    icon = SUI.item_icon(None, item, CARD_FRAME - 4, anchor={"left": 0, "top": 0})
    live = _card_in(cell, _card_in(frame, icon))
    if on is None:
        return live
    cover = SUI.group(None, None, anchor={"full": 0}, extra="Background: %s" % SUI.COLOR["cardOverlay"])
    return SUI.choose(SUI.J(on), live, _card_in(cell, _card_in(frame, icon, cover)))


def card_java(ids, w, look, lines, icons=None, icon_item=None, icon_max=1, on=None, var="card", k="k", b="b"):
    """Java statements that append ONE card (they go inside the page's Java loop; ids / texts / colours may be J() values):
      ids       {"list": the list well, "card", "icons" (None = <card>Ics), "text", "act"} - the page's OLD element ids
      w         the card width (the list well's inner width)
      look      a CARD_LOOKS name, or [(look, java boolean), ..., last look name]: the first true condition wins
      lines     [{"id": suffix, "text": java String expression, "kind": label kind, "h": px, "col": kit colour name or
                J(java expr, sample), "wrap": bool, "tag": {"id", "text", "col", "w", "kind"}}] - the label is <card><suffix>; a tag
                is a second, right-aligned label on the same row (<card><tag id>, the row <card><suffix>Row)
      icons     a Java String[] expression (one cell per entry, at most icon_max; icon_item = J(item id of entry k)), or
                icons=None and icon_item = J(one item id): one cell
      on        a Java boolean: false = the coming-later look (grey text, covered icons); None = always on
    The page appends the action column content (card_button / card_state) into ids["act"] afterwards."""
    card, text, act = ids["card"], ids["text"], ids["act"]
    icons_id = ids.get("icons") or card + "Ics"
    tw = card_text_w(w, icon_max)
    decl, bg, bar = _card_look(look, var)
    out = list(decl)
    body = card + "In"
    out.append(SUI.java_append(ids["list"], SUI.group(card, "Left", h=CARD_H, anchor={"bottom": CARD_GAP}), b))
    out.append(SUI.java_append(card, SUI.group(card + "Bar", None, w=CARD_BAR, h=CARD_H, extra="Background: %s" % bar), b))
    out.append(SUI.java_append(card, SUI.group(body, "Left", w=w - CARD_BAR, h=CARD_H, extra="Background: %s" % bg), b))
    out.append(SUI.java_append(body, SUI.group(icons_id, "Left", w=icon_max * CARD_CELL, h=CARD_H), b))
    if icons is None:
        out.append(SUI.java_append(icons_id, _card_cell(card + "F0", icon_item, on), b))
    else:
        out.append("for (int %s = 0; %s < %s.length && %s < %d; %s++) {" % (k, k, icons, k, icon_max, k))
        out.append("  " + SUI.java_append(icons_id, _card_cell(card + "F" + SUI.J(k), icon_item, on), b))
        out.append("}")
    top = SUI.fit([ln["h"] for ln in lines], CARD_H, "card text lines") // 2
    out.append(SUI.java_append(body, SUI.group(text, "Top", w=tw, h=CARD_H, pad={"top": top} if top else None), b))
    sets = []
    for ln in lines:
        lid, col = card + ln["id"], _card_col(ln["col"], on)
        tag = ln.get("tag")
        if tag is None:
            out.append(SUI.java_append(text, SUI.label(lid, "", ln["kind"], h=ln["h"], col=col, wrap=ln.get("wrap", False)), b))
        else:
            row, tid = card + ln["id"] + "Row", card + tag["id"]
            out.append(SUI.java_append(text, SUI.group(row, "Left", h=ln["h"]), b))
            out.append(SUI.java_append(row, SUI.label(lid, "", ln["kind"], w=tw - tag["w"], h=ln["h"], col=col, wrap=False), b))
            out.append(SUI.java_append(row, SUI.label(tid, "", tag.get("kind", "default"), w=tag["w"], h=ln["h"],
                                                      col=_card_col(tag["col"], on), align="End", wrap=False), b))
        sets.append(SUI.java_set(lid, "Text", SUI.J(ln["text"]), b))
        if tag is not None:
            sets.append(SUI.java_set(tid, "Text", SUI.J(tag["text"]), b))
    out.extend(sets)
    out.append(SUI.java_append(body, SUI.group(act, "Top", w=CARD_ACT_W, h=CARD_H, pad={"top": (CARD_H - SUI.BTN_H) // 2,
                                                                                            "left": (CARD_ACT_W - CARD_BTN_W) // 2}), b))
    return "\n".join(out)


def card_button(ident, text, kind="secondary", sound=None):
    """The card's action button: a vanilla normal text button (172 x 44) - append it into the card's action column."""
    return SUI.button(ident, text, kind, w=CARD_BTN_W, sound=sound)


def card_state(text, kind):
    """A state word in the action column instead of a button: Selected / Active = the vanilla success green, Locked / Coming
    soon / Coming later = the vanilla disabled grey (both bold, centred where the button would be)."""
    return SUI.label(None, text, kind, w=CARD_BTN_W, h=SUI.BTN_H, align="Center", bold=True)


def java_block(src, indent):
    """Java statements re-indented by `indent` spaces (for pasting kit output into a method template)."""
    return "\n".join((" " * indent + ln) if ln.strip() else ln for ln in src.split("\n"))


def java_fill(tpl, parts):
    """A Java method template with {{NAME}} placeholders filled with the kit-built Java in parts (each placeholder used at least
    once, none left over)."""
    out = tpl
    for name, java in parts.items():
        tok = "{{" + name + "}}"
        assert tok in out, "unused Java part " + name
        out = out.replace(tok, java)
    left = re.findall(r"\{\{[A-Z0-9]+\}\}", out)
    assert not left, "unfilled Java placeholder: %s" % left
    return out
# ======================================================================= (end of the shared SKYY CARD block)'''
CARD_SHA = "bf659e0208b537a81ac8758d909f81976f03069816ea9dddb300f843a7eaa028"     # the SAME value in tools/classes_0_1_9_patch.py: the card block is one component in both mods
assert hashlib.sha256(CARD_BLOCK.encode("utf8")).hexdigest() == CARD_SHA, "the SKYY CARD block differs from SkyyClasses 0.1.9's"
_d = [ln for ln in CARD_BLOCK.split(LF) if ln not in OLD_CARD.split(LF)]
assert len(_d) == 7 and "CARD_H = 92 " in "".join(_d) and len(CARD_BLOCK.split(LF)) == len(OLD_CARD.split(LF)) + 3, _d
rep("@@CARD@@", CARD_BLOCK)

# ================================================================================================ ProfilePage: the limit on both views
rep('''# 0.1.3 (the vanilla UI pass): ProfilePage's look = the vanilla UI kit + the shared SKYY CARD above. profile_list_java() and''',
    '''# 0.1.4: the SKYY CARD is 92 px high (was 84): the list view holds CAP_MAX = 8 profile cards (sub margin 10 -> 6, info margin 8 -> 4),
# the Create Profile well 7 class cards (MAX_CARDS) + the new limit line #SkyyPfSlots ("This is profile N of M - ...") under them;
# every limit in both views is ProfCfg.capFor(u) (auto = one per playable class; rank extras later).
# 0.1.3 (the vanilla UI pass): ProfilePage's look = the vanilla UI kit + the shared SKYY CARD above. profile_list_java() and''')
rep('''PF_NAME_H, PF_CSUB_H = SUI.BTN_SMALL_H, 44                    # create view: name row (a small button), sub line (two lines)
''', '''PF_NAME_H, PF_CSUB_H = SUI.BTN_SMALL_H, 44                    # create view: name row (a small button), sub line (two lines)
PF_LSUB_GAP, PF_LINFO_GAP = 6, 4        # 0.1.4: list view margins under the sub line / above the info line (0.1.3: 10 / 8) - 8 cards fit
PF_SLOTS_H = 24                         # 0.1.4: create view - the limit line under the class cards (one 15 px caption line, 8 above)
''')
# list view: the limit of this player, the footer names where it comes from
rep('''  int max = @PKG@.ProfCfg.MAX_PROFILES;''', '''  int max = @PKG@.ProfCfg.capFor(u);''')
rep('''    String used = n + " of " + max + " profile slots used.";''',
    '''    String used = n + " of " + max + " profile slots used (" + @PKG@.ProfCfg.capWhy(u) + ").";''')
rep('''    list_h = sh.inner_h - (PF_SUB_H + 10) - (8 + PF_INFO_H) - (8 + PF_END_H)
    assert list_h >= card_list_h(6), "the list well must hold 6 profile cards (%d px)" % list_h
    assert sh.fit([PF_SUB_H + 10, list_h, 8 + PF_INFO_H, 8 + PF_END_H]) == 0''',
    '''    list_h = sh.inner_h - (PF_SUB_H + PF_LSUB_GAP) - (PF_LINFO_GAP + PF_INFO_H) - (8 + PF_END_H)
    assert list_h >= card_list_h(CAP_MAX), "the list well must hold CAP_MAX = %d profile cards (%d px)" % (CAP_MAX, list_h)
    assert sh.fit([PF_SUB_H + PF_LSUB_GAP, list_h, PF_LINFO_GAP + PF_INFO_H, 8 + PF_END_H]) == 0''')
rep('''             h=PF_SUB_H, align="Center", anchor={"bottom": 10})''', '''             h=PF_SUB_H, align="Center", anchor={"bottom": PF_LSUB_GAP})''')
rep('''        "INFO": "\\n".join([SUI.java_append(body, SUI.label("SkyyPfInfo", "", "info", h=PF_INFO_H, bold=True, align="Center",
                                                            anchor={"top": 8})),
                           SUI.java_set("SkyyPfInfo", "Text", SUI.J("safe(this.info)"))]),
        "CONFIRM": confirm.java("b"),''',
    '''        "INFO": "\\n".join([SUI.java_append(body, SUI.label("SkyyPfInfo", "", "info", h=PF_INFO_H, bold=True, align="Center",
                                                            anchor={"top": PF_LINFO_GAP})),
                           SUI.java_set("SkyyPfInfo", "Text", SUI.J("safe(this.info)"))]),
        "CONFIRM": confirm.java("b"),''')
# create view: the 7-card well, the limit line, the hidden-class warning
rep('''  int shown = r.size() < MAX_CARDS ? r.size() : MAX_CARDS;''',
    '''  int shown = r.size() < MAX_CARDS ? r.size() : MAX_CARDS;
  if (r.size() > MAX_CARDS) warnHidden(r.size());''')
rep('''  String q = this.pickClass == null ? "Select a class to continue."''',
    '''  int have = @PKG@.ProfStore.count(p);
  int cap = @PKG@.ProfCfg.capFor(u);
  String slots = !this.first && have >= cap ? "All " + cap + " profile slots are used - you cannot create another profile."
    : "This is profile " + (have + 1) + " of " + cap + " - " + @PKG@.ProfCfg.capWhy(u) + ".";
{{SLOTS}}
  String q = this.pickClass == null ? "Select a class to continue."''')
rep('''    """ProfilePage.buildCreate(): PF_BUILD_CREATE with its {{parts}} built from kit calls. The list well holds MAX_CARDS cards
    (0.1.2 drew at most 8 - its 'tight' variant is not needed any more); the heights fill the body exactly (asserted)."""
    heights = [PF_NAME_H + 8, PF_CSUB_H + 8, card_list_h(MAX_CARDS), 8 + PF_END_H, 8 + PF_INFO_H]''',
    '''    """ProfilePage.buildCreate(): PF_BUILD_CREATE with its {{parts}} built from kit calls. The list well holds MAX_CARDS cards
    (0.1.4: 7 at the 92 px card height), then the limit line; the heights fill the body exactly (asserted)."""
    heights = [PF_NAME_H + 8, PF_CSUB_H + 8, card_list_h(MAX_CARDS), 8 + PF_SLOTS_H, 8 + PF_END_H, 8 + PF_INFO_H]''')
rep('''        "SELECT": SUI.java_append(act, card_button(pick, "Select")),''',
    '''        "SELECT": SUI.java_append(act, card_button(pick, "Select")),
        "SLOTS": "\\n".join([SUI.java_append(body, SUI.label("SkyyPfSlots", "", "caption", h=PF_SLOTS_H, align="Center",
                                                             anchor={"top": 8})),
                            SUI.java_set("SkyyPfSlots", "Text", SUI.J("safe(slots)"))]),''')
rep('''    indent = {"SHELL": 2, "NAMEROW": 2, "SUB": 2, "LIST": 2, "CARD": 4, "LATER": 6, "SELECTED": 6, "SELECT": 6, "MAKEFIRST": 6,
              "MAKE": 6, "WAITFIRST": 6, "WAIT": 6, "INFO": 2}''',
    '''    indent = {"SHELL": 2, "NAMEROW": 2, "SUB": 2, "LIST": 2, "CARD": 4, "LATER": 6, "SELECTED": 6, "SELECT": 6, "MAKEFIRST": 6,
              "MAKE": 6, "WAITFIRST": 6, "WAIT": 6, "INFO": 2, "SLOTS": 2}''')
rep('''print("profiles page %dx%d (body %dx%d): list view + Create Profile (%d class cards), kit %s"
      % (PF_W, PF_H, PF_LIST_SHELL.inner_w, PF_LIST_SHELL.inner_h, MAX_CARDS, SUI.kit_id()))''',
    '''print("profiles page %dx%d (body %dx%d): list view (%d profile cards) + Create Profile (%d class cards), cards %d px, kit %s"
      % (PF_W, PF_H, PF_LIST_SHELL.inner_w, PF_LIST_SHELL.inner_h, CAP_MAX, MAX_CARDS, CARD_H, SUI.kit_id()))
print("profile limit: default %s (one per class SkyyClasses lists as playable; %d without SkyyClasses), fixed 1-%d, rank hook %s (read only)"
      % (DEF_CAP, CAP_FALLBACK, CAP_MAX, RANK_FN))''')
rep('''F(page, "public static final int MAX_CARDS = %d;" % MAX_CARDS)      # 0.1.2: cards drawn + pfcls<i> handled (0.1.1: 6)
''', '''F(page, "public static final int MAX_CARDS = %d;" % MAX_CARDS)      # cards drawn + pfcls<i> handled (0.1.1: 6, 0.1.2-0.1.3: 8, 0.1.4: 7)
F(page, "public static volatile boolean HIDDEN_WARNED = false;")    # 0.1.4
M(page, r"""
public static void warnHidden(int n) {
  if (HIDDEN_WARNED) return;
  HIDDEN_WARNED = true;
  @PKG@.ProfCfg.warn("the class list has " + n + " classes - the Create Profile page shows the first " + MAX_CARDS + " (a newer SkyyProfiles shows more; logged once)");
}""")
''')

# ================================================================================================ setup(): the migration, once
rep('''  String up = @PKG@.ProfCfg.upgradeDefault();
  String cfgText = @PKG@.ProfCfg.load();
  if (up != null) @PKG@.ProfCfg.info(up);''', '''  String up = @PKG@.ProfCfg.upgradeDefault();
  String capm = @PKG@.ProfCfg.capMigrate();     // 0.1.4: maxProfiles 6 -> auto once (before the load and before the config kit reads the file)
  String cfgText = @PKG@.ProfCfg.load();
  if (up != null) @PKG@.ProfCfg.info(up);
  if (capm != null) @PKG@.ProfCfg.info(capm);''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.3's changed: %s" % k[:80]
assert "MAX_PROFILES" not in s.split('"""\nimport sys', 1)[1].replace("DEF_MAX_PROFILES\": 6", ""), "a MAX_PROFILES use is left"
assert "DEF_MAX_PROFILES" not in s.split('"""\nimport sys', 1)[1], "DEF_MAX_PROFILES is left in the code"
assert s.count("@PKG@.ProfCfg.capFor(u)") == 6, s.count("@PKG@.ProfCfg.capFor(u)")   # describe, createAndSwitch, list, create, pfnew, open
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("public static int capFor(") < s.index("public static String summary()") < s.index("public static synchronized String load()")
assert s.index("public static synchronized String capMigrate()") < s.index("public static synchronized String upgradeDefault()")
assert s.index("capMigrate();") > s.index("upgradeDefault();") and s.index("capMigrate();") < s.index("String cfgText = @PKG@.ProfCfg.load();")
assert s.index("public static void warnHidden(") < s.index("M(page, PF_CREATE_JAVA)")
assert re.search(r"CAP_OPTS = 'auto\|Auto - one per class,1\|1 profile,2\|2 profiles,.*8\|8 profiles'", s)
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.3 had %d)" % (s.count(LF), OLD.count(LF)))
