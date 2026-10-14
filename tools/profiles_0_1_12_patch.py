"""Derive SkyyProfiles/build_skyyprofiles_0.1.12.py from the generated 0.1.11 (build_skyyprofiles_0.1.11.py = the tools/deploy_set.py SET pin).
Edit THIS file, never the generated build script. Harness: python SkyyProfiles/test_skyyprofiles_0.1.12.py [--keep].
Run:  python tools/profiles_0_1_12_patch.py   then   python SkyyProfiles/build_skyyprofiles_0.1.12.py   (never --deploy)

0.1.12 (2026-10-13, Skyy: "make sure admin has no profile cap. (id make the profile names changeable, and have the name show (Class)
(profile name.)"). The 0.1.11 striped locks, files and format are kept:
 A. ADMINS HAVE NO PROFILE CAP: ProfCfg.isAdmin(uuid) = PermissionsModule.get().hasPermission(uuid, "skyyprofiles.admin") (ops have it
    through hytale:Admin's "*"; the same call PlayerRef.hasPermission makes; works for offline players too; false on any error). For an
    admin ProfCfg.capFor(uuid) - the ONE limit every create / restore / page check uses - is ADMIN_LIMIT = MAX_ID (256: every profile
    id there is; ids are never reused, so this is "no cap"); maxProfiles, rank extras and bonus slots do not matter for them. Texts: the
    Profiles footer says "N profiles - admins have no profile limit.", the empty slot card "(admins have no limit)", the Create Profile
    line "This is profile N - admins have no profile limit.", /profiles list "| N profiles (admin - no profile limit)". The list page
    still DRAWS at most LIST_MAX = 16 profile cards (it scrolls); more are named in the footer and in /profiles list. Fix round: for an
    admin the Create new card always stays (a 17th card when 16 are drawn) and the ACTIVE profile is always among the 16 drawn.
 B. RENAME A PROFILE: the ACTIVE profile's card shows a Rename button (vanilla Secondary, where the state word Active was - its name line
    still says " - ACTIVE" in the success green). Rename opens a row in the footer's place (like the delete question): the question
    "New name for <Class> <name>" + a vanilla text field (skyyui text_field, kit look, MaxLength 16, filled with the current name) +
    Save (Primary, save sound) + Cancel (Secondary, cancel sound); Enter in the field = Save. /profiles rename <number or name> <new name>
    renames ANY of the player's live profiles (the new name may have spaces: GREEDY_STRING). NAME RULES (ProfNames.check, the same for
    page and command; creation still picks fruit names, which all pass): 2-16 characters after trimming (runs of spaces become one),
    only A-Z a-z 0-9, space and '-', at least one letter (a name never looks like a profile number), unique among the player's profiles
    (live and deleted, any case; the profile itself excluded - a change of case is allowed) AND never READ the same as another profile
    (fix round: neither the new name nor "<Class> <new name>" may equal another profile's bare name or its "<Class> <name>" - else two
    cards say "Priest Banana"), and no staff-looking names for non-admins (any word admin, administrator, mod, moderator, owner, helper,
    dev, developer, op, operator, console, official; staff / server / system as the FIRST word - "Fire Staff" is fine; a word starting
    with admin / moderator; the letters alone being one of these - "A-d-m-i-n"). A deleted profile is refused ("restore it first").
    Only p.<id>.name changes (ProfStore.rename, under the player's stripe; the check runs again on the fresh copy inside the stripe) -
    the profile KEY, its folder and every other mod's data stay where they are; NO epoch bump (like delete / restore), then publish.
    switches.log: RENAME <uuid> <who> profile <id> <old> -> <new>.
    Page events are matched EXACTLY on the EventData "a" value first (ProfilePage.jsonStr): pfren<id>, pfrnok (+ "@PfName" = the field),
    pfrnno - so a typed name can never be read as another button's payload (0.1.11 matched every other payload with indexOf). Any
    other click closes the rename row.
 C. "<Class> <profile name>" EVERYWHERE THE PROFILE NAME SHOWS (ProfStore.dispName: "Priest Banana"; no class = just the name): the
    Profiles page card name line, the switch and delete questions, the login line "[Profiles] Playing profile Priest Banana.", the switch
    line "[Profiles] Switched to Priest Banana.", the first-profile line, /profiles list and /profileadmin info. BRIDGE: profile:name:<uuid>
    is now that display text, so every mod that already shows profile:name (SkyyMenu tiles, SkyyIslands /island info, SkyyClasses,
    SkyyCoins /balance, SkyyBank, SkyyWardrobe, SkyyAuctions listings) picks it up with no change; NEW profile:pname:<uuid> = the bare
    name (removed with profile:name). profile:list:<uuid> keeps the bare names ("1:Banana:Priest" - its class is a field of its own).
    Commands keep taking the bare name (or the number); /profiles switch|delete|restore|rename also accept the display text.
Saved data: unchanged format (p.<id>.name holds the new name, as it always held the fruit name). Rolling back to 0.1.11 is safe (a renamed
profile simply shows its new name without the class; an admin's extra profiles stay - 0.1.11 refuses only NEW ones above the limit).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.11.py")
dst = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.12.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.11"' in s and "GENERATED by tools/profiles_0_1_11_patch.py" in s and "dispName" not in s, "not the generated 0.1.11 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyProfiles") != "0.1.11":
    print("NOTE: tools/deploy_set.py SET pins SkyyProfiles %s, this patch derives from 0.1.11" % _set.get("SkyyProfiles"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyyProfiles 0.1.11 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.11.py         -> SkyyProfiles/SkyyProfiles-0.1.11.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_11_patch.py from build_skyyprofiles_0.1.10.py (generated by tools/profiles_0_1_10_patch.py from 0.1.9,''',
    '''"""SkyyProfiles 0.1.12 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.12.py         -> SkyyProfiles/SkyyProfiles-0.1.12.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_12_patch.py from build_skyyprofiles_0.1.11.py (generated by tools/profiles_0_1_11_patch.py from 0.1.10,
generated by tools/profiles_0_1_10_patch.py from 0.1.9,''')
rep('''Harness: python SkyyProfiles/test_skyyprofiles_0.1.11.py [--keep]

0.1.11 (2026-10-13)''', '''Harness: python SkyyProfiles/test_skyyprofiles_0.1.12.py [--keep]

''' + HEAD[HEAD.index("0.1.12 (2026-10-13"):HEAD.index("Saved data: unchanged format")].rstrip() + '''
  Full notes in tools/profiles_0_1_12_patch.py.

0.1.11 (2026-10-13)''')
rep('VERSION = "0.1.11"\n', 'VERSION = "0.1.12"\n')

# ---------------------------------------------------------------------------------------------------------------- engine names
rep('''    "DST":   "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
}''', '''    "DST":   "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "PERM":  "com.hypixel.hytale.server.core.permissions.PermissionsModule",          # 0.1.12: ProfCfg.isAdmin (no profile cap for admins)
}''')
rep('''             (T["DST"], "getHealth"), (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["REF"], "isValid"), (T["REF"], "getStore")):
    B.probe(pool, c, m)''', '''             (T["DST"], "getHealth"), (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["REF"], "isValid"), (T["REF"], "getStore"),
             # 0.1.12: admins' no-cap check, the rename command's greedy name, the rename field's value on Save / Enter
             (T["PERM"], "get"), (T["PERM"], "hasPermission"), (T["ATY"], "GREEDY_STRING"), (T["EVD"], "append")):
    B.probe(pool, c, m)
# 0.1.12: the exact signatures the new code calls (B.probe checks names only)
pool.get(T["PERM"]).getMethod("hasPermission", "(Ljava/util/UUID;Ljava/lang/String;)Z")
pool.get(T["EVD"]).getMethod("append", "(Ljava/lang/String;Ljava/lang/String;)L%s;" % T["EVD"].replace(".", "/"))''')

# ---------------------------------------------------------------------------------------------------------------- classes
rep('''pres = pool.makeClass(PKG + ".ProfRestoreCmd", pool.get(T["APC"]))   # 0.1.5
''', '''pres = pool.makeClass(PKG + ".ProfRestoreCmd", pool.get(T["APC"]))   # 0.1.5
pren = pool.makeClass(PKG + ".ProfRenameCmd", pool.get(T["APC"]))    # 0.1.12: /profiles rename <number or name> <new name>
''')
rep('''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, hp, pst, sw, clr, dlt, swp, sfn, bfn, page, opn, rec, pj, rtk, svt, rdy, pcon, quit_, pcre, psw, plst, pdel,
       pres, pcmd,''', '''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, hp, pst, sw, clr, dlt, swp, sfn, bfn, page, opn, rec, pj, rtk, svt, rdy, pcon, quit_, pcre, psw, plst, pdel,
       pres, pren, pcmd,''')

# ---------------------------------------------------------------------------------------------------------------- A: admins have no cap
rep('''M(cfg, r"""
public static int capFor(java.util.UUID u) {
  long c = (long) baseCap() + (long) extraSlots(u) + (long) bonusSlots(u);''', '''# 0.1.12 A (Skyy: "make sure admin has no profile cap"): an admin (op = hytale:Admin's "*", or the skyyprofiles.admin node) - the same
# PermissionsModule call PlayerRef.hasPermission makes, by UUID so it also answers for offline players; any error = not an admin
F(cfg, "public static final String ADMIN_NODE = \\"skyyprofiles.admin\\";")
F(cfg, "public static final int ADMIN_LIMIT = %d;" % MAX_ID)        # every profile id there is (ids are never reused) = no cap
M(cfg, r"""
public static boolean isAdmin(java.util.UUID u) {
  if (u == null) return false;
  try {
    @PERM@ m = @PERM@.get();
    return m != null && m.hasPermission(u, ADMIN_NODE);
  } catch (Throwable t) { return false; }
}""")
M(cfg, r"""
public static int capFor(java.util.UUID u) {
  if (isAdmin(u)) return ADMIN_LIMIT;
  long c = (long) baseCap() + (long) extraSlots(u) + (long) bonusSlots(u);''')
rep('''public static String capWhy(java.util.UUID u) {
  String w = !isAuto() ? "the limit on this server" : "one per class";''', '''public static String capWhy(java.util.UUID u) {
  if (isAdmin(u)) return "admins have no profile limit";
  String w = !isAuto() ? "the limit on this server" : "one per class";''')

# ---------------------------------------------------------------------------------------------------------------- B: the name rules
rep('''M(nam, r"""
public static String pick(java.util.Properties p, String avoid) {''', '''# 0.1.12 B: a typed profile name (rename). clean = trimmed, runs of spaces -> one; check = the rules (null = fine) against the players
# file p: 2-16 characters, A-Z a-z 0-9 space '-', a letter, unique among the player's OTHER profiles (live + deleted, any case), and no
# staff-looking word for a non-admin. Fruit names pass every rule.
F(nam, "public static final int NAME_MIN = %d;" % NAME_MIN)
F(nam, "public static final int NAME_MAX = %d;" % NAME_MAX)
F(nam, "public static final String[] STAFF_WORDS = %s;" % jarr(STAFF_WORDS))
F(nam, "public static final String[] STAFF_LEAD = %s;" % jarr(STAFF_LEAD))
F(nam, "public static final String[] STAFF_PREFIX = %s;" % jarr(STAFF_PREFIX))
M(nam, r"""
public static String clean(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  boolean sp = false;
  String t = s.trim();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (Character.isWhitespace(c)) { sp = true; continue; }
    if (sp && sb.length() > 0) sb.append(' ');
    sp = false;
    sb.append(c);
  }
  return sb.toString();
}""")
M(nam, r"""
public static boolean staffLike(String n) {
  if (n == null) return false;
  String low = n.toLowerCase();
  String[] w = low.replace('-', ' ').split(" ");
  for (int i = 0; i < w.length; i++) {
    for (int j = 0; j < STAFF_WORDS.length; j++) if (w[i].equals(STAFF_WORDS[j])) return true;
    for (int j = 0; j < STAFF_PREFIX.length; j++) if (w[i].startsWith(STAFF_PREFIX[j])) return true;
  }
  if (w.length > 0) { for (int j = 0; j < STAFF_LEAD.length; j++) if (w[0].equals(STAFF_LEAD[j])) return true; }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < low.length(); i++) { char c = low.charAt(i); if (c >= 'a' && c <= 'z') sb.append(c); }
  String sq = sb.toString();
  for (int j = 0; j < STAFF_WORDS.length; j++) if (sq.equals(STAFF_WORDS[j])) return true;
  for (int j = 0; j < STAFF_LEAD.length; j++) if (sq.equals(STAFF_LEAD[j])) return true;
  for (int j = 0; j < STAFF_PREFIX.length; j++) if (sq.startsWith(STAFF_PREFIX[j])) return true;
  return false;
}""")
M(nam, r"""
public static String check(java.util.Properties p, String id, String n, boolean admin) {
  if (n == null || n.length() < NAME_MIN || n.length() > NAME_MAX) return "A profile name needs " + NAME_MIN + " to " + NAME_MAX + " characters.";
  boolean letter = false;
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    boolean az = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    if (az) letter = true;
    if (!az && !(c >= '0' && c <= '9') && c != ' ' && c != '-') return "Use only letters, numbers, spaces and - in a profile name.";
  }
  if (!letter) return "A profile name needs at least one letter.";
  if (!admin && staffLike(n)) return "That name looks like a staff title - pick another one.";
  if (p != null) {
    String myc = @PKG@.ProfRoster.canon(p.getProperty("p." + id + ".class", ""));
    String mine = myc.length() > 0 ? myc + " " + n : n;
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      String o = String.valueOf(i);
      if (o.equals(id)) continue;
      String v = p.getProperty("p." + o + ".name");
      if (v == null) continue;
      if (v.equalsIgnoreCase(n)) return "You already have a profile called " + v + ".";
      String oc = @PKG@.ProfRoster.canon(p.getProperty("p." + o + ".class", ""));
      String od = oc.length() > 0 ? oc + " " + v : v;
      // fix round: never two profiles that READ the same (a Mage named "Priest Banana" next to the Priest "Banana")
      if (od.equalsIgnoreCase(n) || v.equalsIgnoreCase(mine) || od.equalsIgnoreCase(mine))
        return "That would look the same as your profile " + od + " - pick another name.";
    }
  }
  return null;
}""")
M(nam, r"""
public static String pick(java.util.Properties p, String avoid) {''')
rep('''FRUITS = ["Apple", "Banana",''', '''# 0.1.12 B: typed profile names (rename) - ProfNames.check
NAME_MIN, NAME_MAX = 2, 16
# fix round (critic: a substring test refused "Fire Staff", "Badminton", "Stafford", "Downer"): STAFF_WORDS = refused as ANY whole
# word; STAFF_LEAD = refused only as the FIRST word ("Staff Bob"; "Fire Staff" is a Monk's weapon); STAFF_PREFIX = refused at the START
# of any word ("Admin123"); and the name squashed to its letters may not BE one of them ("A-d-m-i-n", "Ad Min")
STAFF_WORDS = ["admin", "administrator", "mod", "moderator", "owner", "helper", "dev", "developer", "op", "operator", "console", "official"]
STAFF_LEAD = ["staff", "server", "system"]
STAFF_PREFIX = ["admin", "moderator"]
FRUITS = ["Apple", "Banana",''')

# ---------------------------------------------------------------------------------------------------------------- C: dispName + B: rename (ProfStore)
rep('''M(sto, r"""
public static String listText(java.util.Properties p) {''', '''# 0.1.12 C: what a profile is CALLED wherever it shows - "<Class> <name>" ("Priest Banana"); no class = the name alone
M(sto, r"""
public static String dispName(java.util.Properties p, String id) {
  if (p == null || id == null) return "Profile " + id;
  String n = p.getProperty("p." + id + ".name", "Profile " + id);
  String c = @PKG@.ProfRoster.canon(p.getProperty("p." + id + ".class", ""));
  return c.length() > 0 ? c + " " + n : n;
}""")
# 0.1.12 B: rename = ONE commit under the player's stripe; the rules are checked again on the fresh copy INSIDE the stripe (two renames at
# once can never end with two profiles of one name). null = renamed; else why not (nothing written). Only p.<id>.name changes: no epoch.
M(sto, r"""
public static String rename0(java.util.UUID u, String id, String name, boolean admin) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!live(q, id)) return "You have no such profile.";
  String why = @PKG@.ProfNames.check(q, id, name, admin);
  if (why != null) return why;
  if (name.equals(q.getProperty("p." + id + ".name"))) return null;     // the same name already (a second click / a race): no write
  q.setProperty("p." + id + ".name", name);
  if (!commit(u, q)) return "Could not save the new name - nothing was changed.";
  return null;
}""")
M(sto, r"""
public static String rename(java.util.UUID u, String id, String name, boolean admin) {
  Object l = lockOf(u);
  String r = null;
  synchronized (l) { r = rename0(u, id, name, admin); }
  return r;
}""")
M(sto, r"""
public static String listText(java.util.Properties p) {''')
# bridge: profile:name = the display text (every adopter shows it as it is); profile:pname = the bare name (new)
rep('''    b.remove("profile:name:" + us);
    b.remove("profile:list:" + us);''', '''    b.remove("profile:name:" + us);
    b.remove("profile:pname:" + us);
    b.remove("profile:list:" + us);''')
rep('''    String n = p.getProperty("p." + a + ".name", "");
    if (n.length() > 0) b.put("profile:name:" + us, n); else b.remove("profile:name:" + us);''', '''    String n = p.getProperty("p." + a + ".name", "");
    // 0.1.12 C: profile:name = "<Class> <name>" (Skyy: "have the name show (Class) (profile name"); profile:pname = the bare name
    if (n.length() > 0) { b.put("profile:name:" + us, @PKG@.ProfStore.dispName(p, a)); b.put("profile:pname:" + us, n); }
    else { b.remove("profile:name:" + us); b.remove("profile:pname:" + us); }''')
# resolveId: the number, the bare name, or (0.1.12) the display text
rep('''  if (exists(p, s)) return s;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (exists(p, id) && s.equalsIgnoreCase(p.getProperty("p." + id + ".name", ""))) return id;
  }
  return null;
}""")''', '''  if (exists(p, s)) return s;
  // 0.1.12: the bare name OR the display text "<Class> <name>". Fix round: when two DIFFERENT profiles match (a class set later can make
  // one name read like another profile's), nothing is picked - switch / delete / rename never hit the wrong card; the number still works
  String hit = null;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!exists(p, id)) continue;
    if (s.equalsIgnoreCase(p.getProperty("p." + id + ".name", "")) || s.equalsIgnoreCase(dispName(p, id))) {
      if (hit != null && !hit.equals(id)) return null;
      hit = id;
    }
  }
  return hit;
}""")''')
rep('''M(sto, r"""
public static void log(String line) {
  @PKG@.ProfCfg.appendLine(LOGF, java.time.Instant.now().toString() + " " + line);
}""")''', '''M(sto, r"""
public static void log(String line) {
  @PKG@.ProfCfg.appendLine(LOGF, java.time.Instant.now().toString() + " " + line);
}""")
# 0.1.12 B: the rename itself for the page and the command: "+" done / "-" refused / "=" nothing to do (ProfDel.tell colours)
M(sto, r"""
public static String renameProfile(java.util.UUID u, String who, String id, String raw, boolean admin) {
  if (BROKEN.containsKey(u)) return "-Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = load(u);
  if (id == null || !exists(p, id)) return "-You have no such profile. /profiles list shows yours.";
  String old = p.getProperty("p." + id + ".name", "Profile " + id);
  if (isDel(p, id)) return "-" + old + " is deleted - restore it first (/profiles restore " + old + ").";
  String n = @PKG@.ProfNames.clean(raw);
  if (n.equals(old)) return "=" + dispName(p, id) + " already has that name.";
  String why = rename(u, id, n, admin);
  if (why != null) return "-" + why;
  publish(u);
  log("RENAME " + u + " " + who + " profile " + id + " " + old + " -> " + n);
  return "+" + old + " is now called " + dispName(load(u), id) + ".";
}""")''')
# describe (/profiles list, /profileadmin info): the display text; admins: no slot count
rep('''    String nm = p.getProperty("p." + id + ".name", "?");
    sb.append(id).append(" ").append(nm).append(" - ").append(c.length() == 0 ? "no class" : c);''', '''    String nm = p.getProperty("p." + id + ".name", "?");
    sb.append(id).append(" ").append(dispName(p, id));      // 0.1.12 C: "2 Priest Banana"
    if (c.length() == 0) sb.append(" - no class");''')
rep('''  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.capFor(u);''',
    '''  if (@PKG@.ProfCfg.isAdmin(u)) return sb.toString() + " | " + n + " profiles (admin - no profile limit)";   // 0.1.12 A
  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.capFor(u);''')

# ---------------------------------------------------------------------------------------------------------------- C: chat lines
rep('''  pr.sendMessage(@MSG@.raw("[Profiles] Profile " + name + " created - you are " + @PKG@.ProfRoster.article(cls)''',
    '''  pr.sendMessage(@MSG@.raw("[Profiles] Profile " + @PKG@.ProfStore.dispName(@PKG@.ProfStore.load(u), fid) + " created - you are " + @PKG@.ProfRoster.article(cls)''')
rep('''  pr.sendMessage(@MSG@.raw("[Profiles] Switched to " + toName + (toCls.length() > 0 ? " (" + toCls + ")" : "") + ". Your other inventory is saved with its profile.").color("#8fe39a"));''',
    '''  pr.sendMessage(@MSG@.raw("[Profiles] Switched to " + @PKG@.ProfStore.dispName(p, to) + ". Your other inventory is saved with its profile.").color("#8fe39a"));''')
rep('''      pr.sendMessage(@MSG@.raw("[Profiles] Playing profile " + p.getProperty("p." + act + ".name", act) + (cls.length() > 0 ? " (" + cls + ")" : "") + ". /profiles to switch or create one.").color("#9fd8a2"));''',
    '''      pr.sendMessage(@MSG@.raw("[Profiles] Playing profile " + @PKG@.ProfStore.dispName(p, act) + ". /profiles to switch or create one.").color("#9fd8a2"));''')
rep('''"Playing profile Strawberry (Archer) - when you join");''', '''"Playing profile Archer Strawberry - when you join");''')

# ---------------------------------------------------------------------------------------------------------------- page: list view
rep('''  boolean roomNew = n < max && shown.length < LIST_MAX;''',
    '''  boolean roomNew = n < max && (shown.length < LIST_MAX || adm);     // fix round: an admin always keeps the Create new card''')
rep('''public static String[] shownIds(java.util.Properties p) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < LIST_MAX; i++) {
    String id = String.valueOf(i);
    if (@PKG@.ProfStore.live(p, id)) out.add(id);
  }''', '''public static String[] shownIds(java.util.Properties p) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < LIST_MAX; i++) {
    String id = String.valueOf(i);
    if (@PKG@.ProfStore.live(p, id)) out.add(id);
  }
  // fix round (an admin with more than LIST_MAX live profiles): the ACTIVE profile's card (its Rename) is always drawn - last live place
  String act = @PKG@.ProfStore.activeOf(p);
  if (act != null && @PKG@.ProfStore.live(p, act) && !out.contains(act) && out.size() > 0) out.set(out.size() - 1, act);''')
rep('''  int max = @PKG@.ProfCfg.capFor(u);
  long now = System.currentTimeMillis();
  String[] shown = shownIds(p);''','''  int max = @PKG@.ProfCfg.capFor(u);
  boolean adm = @PKG@.ProfCfg.isAdmin(u);       // 0.1.12 A: no profile limit (texts)
  long now = System.currentTimeMillis();
  String[] shown = shownIds(p);''')
rep('''    String name = p.getProperty("p." + id + ".name", "Profile " + id);
    String cls = @PKG@.ProfRoster.canon(p.getProperty("p." + id + ".class", ""));
    String[] ce = @PKG@.ProfRoster.entry(cls);''', '''    String name = @PKG@.ProfStore.dispName(p, id);      // 0.1.12 C: "Priest Banana"
    String cls = @PKG@.ProfRoster.canon(p.getProperty("p." + id + ".class", ""));
    String[] ce = @PKG@.ProfRoster.entry(cls);''')
rep('''    if (on) {
{{ACTIVE}}
    } else if (over) {''', '''    if (on) {
{{ACTIVE}}
      ev.addEventBinding(@BT@.Activating, "#SkyyPfRen" + id, @EVD@.of("a", "pfren" + id));
    } else if (over) {''')
rep('''    String pn = p.getProperty("p." + this.pending + ".name", "Profile " + this.pending);
    String pc = @PKG@.ProfRoster.canon(p.getProperty("p." + this.pending + ".class", ""));
    String q = "Switch to " + pn + (pc.length() > 0 ? " (" + pc + ")" : "") + "? Your inventory is saved and you go to the island of that profile.";''',
    '''    String q = "Switch to " + @PKG@.ProfStore.dispName(p, this.pending) + "? Your inventory is saved and you go to the island of that profile.";''')
rep('''    String dq = "Delete profile " + safe(p.getProperty("p." + this.delAsk + ".name", "Profile " + this.delAsk)) + "? Its island''',
    '''    String dq = "Delete profile " + safe(@PKG@.ProfStore.dispName(p, this.delAsk)) + "? Its island''')
rep('''    ev.addEventBinding(@BT@.Activating, "#SkyyPfDelNo", @EVD@.of("a", "pfdelno"));
  } else {
    String used = n + " of " + max + " profile slots used (" + @PKG@.ProfCfg.capWhy(u) + ").";
    if (n > max) used = n + " profiles - this server now allows " + max + ". You keep them all but cannot create more.";''',
    '''    ev.addEventBinding(@BT@.Activating, "#SkyyPfDelNo", @EVD@.of("a", "pfdelno"));
  } else if (this.renId != null && @PKG@.ProfStore.live(p, this.renId)) {
    String rq = "New name for " + @PKG@.ProfStore.dispName(p, this.renId) + " - " + @PKG@.ProfNames.NAME_MIN + " to " + @PKG@.ProfNames.NAME_MAX + " letters, numbers or spaces";
{{RENAME}}
    b.set("#SkyyPfRenF.Value", this.renText == null ? "" : this.renText);
    ev.addEventBinding(@BT@.Activating, "#SkyyPfRenOk", @EVD@.of("a", "pfrnok").append("@PfName", "#SkyyPfRenF.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyPfRenF", @EVD@.of("a", "pfrnok").append("@PfName", "#SkyyPfRenF.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyPfRenNo", @EVD@.of("a", "pfrnno"));
  } else {
    String used = n + " of " + max + " profile slots used (" + @PKG@.ProfCfg.capWhy(u) + ").";
    if (n > max) used = n + " profiles - this server now allows " + max + ". You keep them all but cannot create more.";
    if (adm) used = n + " profiles - admins have no profile limit.";     // 0.1.12 A''')
rep('''    new_lines = [{"id": "Tx", "text": 'safe("Empty slot - a new profile starts from zero with the class you pick (" + (max - n) + " free)")',''',
    '''    new_lines = [{"id": "Tx", "text": 'safe("Empty slot - a new profile starts from zero with the class you pick (" + (adm ? "admins have no limit" : (max - n) + " free") + ")")',''')
# the active card: Rename (0.1.11: the state word Active - the name line still says " - ACTIVE")
rep('''        "ACTIVE": SUI.java_append(act, card_state("Active", "success")),''',
    '''        "ACTIVE": SUI.java_append(act, card_button("SkyyPfRen" + ident, "Rename")),     # 0.1.12 B (was the state word Active)''')
rep('''    SUI.assert_proven([swdel, delask, foot, restore], allow=("base", "base4"), what="SkyyProfiles 0.1.5 list view additions")''',
    '''    SUI.assert_proven([swdel, delask, foot, restore], allow=("base", "base4"), what="SkyyProfiles 0.1.5 list view additions")
    # 0.1.12 B: the rename row in the footer's place - the question (wraps) | the kit text field (MaxLength NAME_MAX) | Save | Cancel
    ren_bw, ren_fw, ren_gap = 150, 300, 6
    ren_qw = W - ren_fw - 2 * ren_bw - 3 * ren_gap
    SUI.fit([ren_qw, ren_gap, ren_fw, ren_gap, ren_bw, ren_gap, ren_bw], W, "rename row")
    assert ren_qw >= 300, ren_qw
    ren = SUI.Appends()
    ren.append((body, SUI.group("SkyyPfRenRow", "Left", h=PF_END_H, anchor={"top": 8})))
    ren.append(("SkyyPfRenRow", SUI.label("SkyyPfRenQ", "", "bold", w=ren_qw, h=PF_END_H, col="warning", wrap=True)))
    ren.append(("SkyyPfRenRow", SUI.text_field("SkyyPfRenBox", "SkyyPfRenF", w=ren_fw, max_length=NAME_MAX, placeholder="New name",
                                               anchor={"left": ren_gap, "top": (PF_END_H - SUI.FIELD_H) // 2})))
    ren.append(("SkyyPfRenRow", SUI.button("SkyyPfRenOk", "Save", "primary", w=ren_bw, sound="save",
                                           anchor={"left": ren_gap, "top": (PF_END_H - SUI.BTN_H) // 2})))
    ren.append(("SkyyPfRenRow", SUI.button("SkyyPfRenNo", "Cancel", "secondary", w=ren_bw, sound="cancel",
                                           anchor={"left": ren_gap, "top": (PF_END_H - SUI.BTN_H) // 2})))
    ren.sets.append(("SkyyPfRenQ", "Text", SUI.J("safe(rq)")))
    SUI.assert_proven([ren, card_button("SkyyPfRen1", "Rename")], allow=("base", "base4"), what="SkyyProfiles 0.1.12 rename row")''')
rep('''        "DELASK": delask.java("b"),
        "FOOT": foot.java("b"),
    }''', '''        "DELASK": delask.java("b"),
        "RENAME": ren.java("b"),          # 0.1.12 B
        "FOOT": foot.java("b"),
    }''')
rep('''              "INFO": 2, "CONFIRM": 4, "DELASK": 4, "FOOT": 4}
    java = java_fill(PF_BUILD_LIST,''', '''              "INFO": 2, "CONFIRM": 4, "DELASK": 4, "RENAME": 4, "FOOT": 4}
    java = java_fill(PF_BUILD_LIST,''')
rep('''    for ident_ in ("SkyyPfDelRow", "SkyyPfDelQ", "SkyyPfDelYes", "SkyyPfDelNo", "SkyyPfFootRow", "SkyyPfClose"):
        assert ("#%s {" % ident_) in java, ident_''', '''    for ident_ in ("SkyyPfDelRow", "SkyyPfDelQ", "SkyyPfDelYes", "SkyyPfDelNo", "SkyyPfFootRow", "SkyyPfClose",
                   "SkyyPfRenRow", "SkyyPfRenQ", "SkyyPfRenBox", "SkyyPfRenF", "SkyyPfRenOk", "SkyyPfRenNo"):
        assert ("#%s {" % ident_) in java, ident_
    assert ('#SkyyPfRen" + (id)' in java) and "MaxLength: %d;" % NAME_MAX in java, "0.1.12: the Rename button + the 16-letter field"''')

# ---------------------------------------------------------------------------------------------------------------- page: create view text
rep('''  String slots = !this.first && have >= cap ? "All " + cap + " profile slots are used - you cannot create another profile."
    : "This is profile " + (have + 1) + " of " + cap + " - " + @PKG@.ProfCfg.capWhy(u) + ".";''',
    '''  String slots = !this.first && have >= cap ? "All " + cap + " profile slots are used - you cannot create another profile."
    : "This is profile " + (have + 1) + " of " + cap + " - " + @PKG@.ProfCfg.capWhy(u) + ".";
  if (@PKG@.ProfCfg.isAdmin(u)) slots = "This is profile " + (have + 1) + " - admins have no profile limit.";     // 0.1.12 A''')

# ---------------------------------------------------------------------------------------------------------------- page: state + events
rep('''F(page, "public String delAsk;")       # 0.1.5: the profile id the delete question is open for (null = none)''',
    '''F(page, "public String delAsk;")       # 0.1.5: the profile id the delete question is open for (null = none)
F(page, "public String renId;")        # 0.1.12 B: the profile id the rename row is open for (null = none)
F(page, "public String renText;")      # 0.1.12 B: the text the rename field shows (the current name, or what was typed when refused)''')
rep('''M(page, r"""
public static String[] shownIds(java.util.Properties p) {''', '''# 0.1.12 B: one String value of the event JSON (SkyyBank 0.1.9's reader: quotes, escapes, \\u0000; at most 200 characters); "" = absent
M(page, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(page, r"""
public static String[] shownIds(java.util.Properties p) {''')
rep('''# 0.1.7: the switch confirm (0.1.6's pfyes code, moved)''', '''# 0.1.12 B: the rename clicks, matched EXACTLY on the "a" value (a typed name never reaches the indexOf matching below): pfren<id> opens the
# row for that live profile, pfrnok (Save / Enter; "@PfName" = the field) renames, pfrnno closes it. false = not a rename click.
M(page, r"""
public boolean renameEvent(String a, String data, java.util.UUID u, java.util.Properties p) {
  if (a.equals("pfrnno")) { this.renId = null; this.renText = ""; this.info = ""; rebuild(); return true; }
  if (a.equals("pfrnok")) {
    String id = this.renId;
    String typed = jsonStr(data, "@PfName");
    if (id == null) { rebuild(); return true; }
    String r = @PKG@.ProfStore.renameProfile(u, this.playerRef.getUsername(), id, typed, this.playerRef.hasPermission(@PKG@.ProfCfg.ADMIN_NODE));
    if (r.startsWith("+")) { this.renId = null; this.renText = ""; this.info = r.substring(1); }
    else { this.renText = typed; this.info = r.substring(1); }
    rebuild();
    return true;
  }
  if (a.startsWith("pfren")) {
    String id = a.substring(5);
    this.pending = null;
    this.delAsk = null;
    if (@PKG@.ProfStore.live(p, id)) { this.renId = id; this.renText = p.getProperty("p." + id + ".name", ""); this.info = ""; }
    else { this.renId = null; this.info = "That profile cannot be renamed right now."; }
    rebuild();
    return true;
  }
  return false;
}""")
# 0.1.7: the switch confirm (0.1.6's pfyes code, moved)''')
rep('''    java.util.Properties p = @PKG@.ProfStore.load(u);
    if (deleteEvent(ref, st, data, u, p)) return;''', '''    java.util.Properties p = @PKG@.ProfStore.load(u);
    String a0 = jsonStr(data, "a");                 // 0.1.12 B: rename clicks first, exact match; any other click closes the row
    if (renameEvent(a0, data, u, p)) return;
    this.renId = null;
    if (deleteEvent(ref, st, data, u, p)) return;''')
rep('''  this.reminded = false;
  this.delAsk = null;
  if (view == 1) prepareCreate();''', '''  this.reminded = false;
  this.delAsk = null;
  this.renId = null;
  this.renText = "";
  if (view == 1) prepareCreate();''')

# ---------------------------------------------------------------------------------------------------------------- B: /profiles rename
rep('''C(pcmd, r"""
public ProfilesCmd() {
  super("profiles", "Your profiles (each = its own class, island and inventory): /profiles | create | switch <n> | list | delete <n> | restore <n>");''',
    '''# 0.1.12 B: /profiles rename <number or name> <new name> - any of the player's live profiles; the name may have spaces (GREEDY_STRING)
F(pren, "public @RA@ profArg;")
F(pren, "public @RA@ nameArg;")
C(pren, r"""
public ProfRenameCmd() {
  super("rename", "Rename one of your profiles: /profiles rename <number or name> <new name>");
  this.profArg = withRequiredArg("profile", "profile number (1, 2, ...) or its name", @ATY@.STRING);
  this.nameArg = withRequiredArg("name", "the new name - 2 to 16 letters, numbers, spaces or -", @ATY@.GREEDY_STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(pren, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.UUID u = pr.getUuid();
    String arg = String.valueOf(ctx.get(this.profArg));
    String id = @PKG@.ProfStore.resolveId(u, arg);
    if (id == null) { @PKG@.ProfDel.tell(pr, "-No profile '" + arg + "'. Yours: " + @PKG@.ProfStore.describe(u)); return; }
    @PKG@.ProfDel.tell(pr, @PKG@.ProfStore.renameProfile(u, pr.getUsername(), id, String.valueOf(ctx.get(this.nameArg)), pr.hasPermission(@PKG@.ProfCfg.ADMIN_NODE)));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("/profiles rename failed: " + t); pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profiles rename <number or name> <new name>")); }
}""")
C(pcmd, r"""
public ProfilesCmd() {
  super("profiles", "Your profiles (each = its own class, island and inventory): /profiles | create | switch <n> | list | rename <n> <name> | delete <n> | restore <n>");''')
rep('''  addSubCommand(new @PKG@.ProfRestoreCmd());
}""")''', '''  addSubCommand(new @PKG@.ProfRestoreCmd());
  addSubCommand(new @PKG@.ProfRenameCmd());      // 0.1.12 B
}""")''')

# ---------------------------------------------------------------------------------------------------------------- self-checks
assert s.index("public static boolean isAdmin(") < s.index("public static int capFor("), "definitions before use (isAdmin)"
assert s.index("public static String dispName(") < s.index("public static synchronized void publishLocked("), "dispName before publishLocked"
assert s.index("public static String rename0(") < s.index("public static String rename(java.util.UUID") < s.index("public static String renameProfile("), "order"
assert s.index("public static void log(String line)") < s.index("public static String renameProfile("), "log before renameProfile"
assert s.index("public static String check(java.util.Properties p, String id, String n, boolean admin)") < s.index("public static String rename0("), "check first"
assert s.index("public static String jsonStr(") < s.index("public boolean renameEvent(") < s.index("public void handleDataEvent("), "page order"
assert s.index("addSubCommand(new @PKG@.ProfRenameCmd());") > s.index("public ProfRenameCmd()"), "the command class first"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.11 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.11 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
