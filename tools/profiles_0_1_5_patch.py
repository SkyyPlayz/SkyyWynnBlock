"""Derive SkyyProfiles/build_skyyprofiles_0.1.5.py from the LIVE 0.1.4 (build_skyyprofiles_0.1.4.py = the tools/deploy_set.py SET pin).
Run:  python tools/profiles_0_1_5_patch.py   then   python SkyyProfiles/build_skyyprofiles_0.1.5.py   (never --deploy: coordinated deploy)
Patch chain (the 0.1.4 header): 0.1 -> 0.1.1 (copy + edit) -> tools/profiles_0_1_2_patch.py -> 0.1.2 -> tools/profiles_0_1_3_patch.py ->
0.1.3 -> tools/profiles_0_1_4_patch.py -> 0.1.4 -> THIS patch -> 0.1.5. Edit THIS file, never the generated build script.
Harness: python SkyyProfiles/test_skyyprofiles_0.1.5.py (bare JVM, -Xverify:all; compares 0.1.4 and 0.1.5 side by side).

0.1.5 = DELETE A PROFILE. Skyy (2026-10-01, verbatim): "add a way to delete a profile. (make sure there is a confirm question. then a 6
hour undo window." (OPEN-QUESTIONS LOCKED 2026-10-01: never the active or the last profile; after 6 h the files go to an admin-only
archive, not wiped; Restore works even over the limit.)
  - Profiles list: a non-active profile card shows a small Switch + a small red Delete (vanilla Destructive) in its action column
    (the card's old normal-size Switch stays where the switch question is open for that card); the ACTIVE card shows only "Active"
    (switch first), so the last remaining profile (always the active one) never shows Delete; ProfDel.check refuses both anyway.
  - Delete -> the page's one-row confirm (SUI.confirm_view compact, wraps to two lines, like the switch question): "Delete profile
    <name>? Its island, coins, skills, bags and items will be gone. You have 6 hours to undo this." with Delete (Destructive, the
    vanilla cancel sound) + Cancel (Secondary, cancel sound). Nothing changes before Delete.
  - DELETED-PENDING = players file p.<id>.deleted (time) + p.<id>.until (deadline = time + the window AT DELETE TIME: what the player
    was told stays true when an admin changes the window later). Hidden from switching (switchTo refuses, not in profile:list, never
    the key), shown greyed (the SKYY CARD "off" look + covered icon) with "Deleted - restore it within 5 h 12 min. Then it is gone."
    and Restore (Primary). It frees its slot at once: the limit counts live profiles only (ProfStore.count); a new profile takes a NEW
    id - nextId skips deleted and archived ids, so a new profile can never inherit the deleted one's island / coins / bags.
    Restore within the window removes only those keys = exactly as it was, even above a LOWERED limit (keep, cannot create more) -
    but (review fix) never above max(limit, p.<id>.slots = the live count when it was deleted): delete -> create -> restore cannot
    grow past the limit. A profile past its deadline that could not be archived (a FAILED marker) shows Expired; only an admin restores
    it (/profileadmin archive restore ignores the deadline and the limit).
  - After the window (ProfSweep every 60 s, at join, when /profiles opens, on a late Restore): ARCHIVED - the profile's players-file
    entries are written to Skyy_SkyyProfiles/archive/<uuid>/<id>-<time>/profile.properties, the players file drops them and keeps
    the tombstone gone.<id> (+ gone.<id>.dir) so the id is never reused, then inventories/<key>.json is MOVED there as inventory.json.
    Nothing is ever deleted (a failed attempt removes only its own fresh record + empty folder and warns once per profile).
    /profileadmin archive list <player>, /profileadmin archive restore <player> <name|id|folder> (moves it back; a name taken
    meanwhile gets a new fruit name; a deleted profile not archived yet is restored at once). The window is wall-clock time.
    MAX_ID 64 -> 256 (a deleted / archived id is never reused).
  - Commands: /profiles delete <name|number> (the first run asks, the same command again within 10 s deletes), /profiles restore
    <name|number> - Adventurer group; /profileadmin archive (+ list, restore) - requirePermission + setPermissionGroups(new String[0]).
  - Server Setup > Profiles: deleteUndoHours "Undo window after deleting a profile" (int 1-168 h, default 6, live).
  - Footer: Close (vanilla Secondary + cancel sound) right of the footer text (promised to Skyy; 0.1.4 had only Esc).
  - Bridge: NEW profile:fn:state (Function apply(String storage key) -> "active" | "inactive" | "pending" | "archived" | null) for
    adopters that act on keys other than the active one; delete / restore / archive never bump profile:epoch (the active profile and
    its key never change) and republish profile:list (live profiles only).
The shared SKYY CARD block is NOT changed (asserted: CARD_SHA of SkyyClasses 0.1.9 / SkyyProfiles 0.1.4); the delete / restore
controls are composed outside it (the page passes look / on / its own action column content). Every 0.1.4 event binding stays (same
selector, data and order; pfdel<id> follows its card's pfsw<id>, pfres<id> / pfdelyes / pfdelno / pfclose are new) and every 0.1.4
element id stays; the Create Profile view is unchanged.
"""
import hashlib
import os
import re

UMIN, UMAX, UDEF = 1, 168, 6     # the undo window: bounds + default in hours (= the build constants UNDO_MIN_H / UNDO_MAX_H / DEF_UNDO_H)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.4.py")
dst = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.4"' in s and "GENERATED by tools/profiles_0_1_4_patch.py from build_skyyprofiles_0.1.3.py" in s, \
    "build_skyyprofiles_0.1.4.py is not the live 0.1.4"
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 8, "0.1.4 has 8 event binding lines (all in ProfilePage), found %d" % len(BIND0)


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


# ------------------------------------------------------------------------------------------------ the shared SKYY CARD block: unchanged
CARD_START = "# =====================================================================================================================\n# SKYY CARD"
CARD_END = "# ======================================================================= (end of the shared SKYY CARD block)"
CARD_SHA = "bf659e0208b537a81ac8758d909f81976f03069816ea9dddb300f843a7eaa028"   # = tools/profiles_0_1_4_patch.py + tools/classes_0_1_9_patch.py


def card_sha():
    a, b = s.index(CARD_START), s.index(CARD_END)
    return hashlib.sha256(s[a:b + len(CARD_END)].encode("utf8")).hexdigest()


assert card_sha() == CARD_SHA, "the 0.1.4 SKYY CARD block is not the one SkyyClasses 0.1.9 / SkyyProfiles 0.1.4 carry"

# blocks that must come out of this patch byte-identical (0.1.4's)
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", "\nFRUITS = ["),
        block("# ================= ProfRoster: class cards", "# ================= ProfStore: the profile list per player"),
        block("# ================= ProfKit (0.1.2)", "# ================= ProfSwitch: checks, the switch transaction"),
        block("M(sw, r\"\"\"\npublic static long ago(", "M(sw, r\"\"\"\npublic static String switchTo("),
        block("M(sw, r\"\"\"\npublic static String createAndSwitch(", "# ================= ProfilePage: Profiles list (view 0)"),
        block("PF_BUILD_CREATE = r\"\"\"", "\n\ndef pf_ids_kept(java, view):"),
        block("def profile_create_java():", "PF_LIST_JAVA, PF_LIST_SHELL = profile_list_java()"),
        block("M(page, r\"\"\"\npublic void prepareCreate() {", "M(page, PF_LIST_JAVA)"),
        block("# ================= OpenTask: first-join Create Profile page", "# ================= ProfJoin: the join work"),
        block("# 0.1.1 - config helpers for the admin commands", "C(adm, r\"\"\"\npublic ProfileAdminCmd() {")]

# ================================================================================================ docstring
rep('''"""SkyyProfiles 0.1.4 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.4.py          -> SkyyProfiles/SkyyProfiles-0.1.4.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_4_patch.py from build_skyyprofiles_0.1.3.py (generated by tools/profiles_0_1_3_patch.py from 0.1.2,
generated by tools/profiles_0_1_2_patch.py from 0.1.1, a copy + edit of 0.1) - edit the patch, never this file. Everything below the
0.1.4, 0.1.3, 0.1.2 and 0.1.1 blocks is the 0.1 design, unchanged unless a line says 0.1.1, 0.1.2, 0.1.3 or 0.1.4.
''', '''"""SkyyProfiles 0.1.5 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.5.py          -> SkyyProfiles/SkyyProfiles-0.1.5.jar
       (never --deploy: tools/deploy_set.py is the only deploy path; HANDOFF section 3)
GENERATED by tools/profiles_0_1_5_patch.py from build_skyyprofiles_0.1.4.py (generated by tools/profiles_0_1_4_patch.py from 0.1.3,
generated by tools/profiles_0_1_3_patch.py from 0.1.2, generated by tools/profiles_0_1_2_patch.py from 0.1.1, a copy + edit of 0.1) -
edit the patch, never this file. Everything below the 0.1.5 ... 0.1.1 blocks is the 0.1 design, unchanged unless a line says so.
Harness: python SkyyProfiles/test_skyyprofiles_0.1.5.py

0.1.5 (2026-10-01, DELETE A PROFILE - Skyy: "add a way to delete a profile. (make sure there is a confirm question. then a 6 hour undo
  window."; OPEN-QUESTIONS LOCKED 2026-10-01):
  - PAGE: every profile card that is not the ACTIVE one shows a small Switch + a small red Delete (vanilla Destructive) in its action
    column (where the switch question is open for that card it keeps 0.1.4's normal-size Switch). The active card shows only
    "Active": a player switches first, and the last remaining profile (always the active one) never offers Delete. ProfDel.check
    refuses the active profile, the last profile, a broken players file, a running switch and a failed switch marker anyway.
  - CONFIRM QUESTION: Delete opens the page's one-row confirm (the kit's confirm_view compact, wrapping to two lines, in place of the
    footer - like the switch question): "Delete profile <name>? Its island, coins, skills, bags and items will be gone. You have 6
    hours to undo this." - Delete (Destructive, cancel sound) / Cancel (Secondary, cancel sound). Nothing is changed before Delete.
  - DELETED-PENDING: players file p.<id>.deleted=<time> and p.<id>.until=<deadline> (time + the undo window AT DELETE TIME - the
    deadline the player was told survives restarts and later changes of the window) + p.<id>.slots=<mark> (below). The profile is
    hidden from switching (switchTo refuses it, profile:list leaves it out, profile:fn:key never returns it), shown greyed in the list
    (the SKYY CARD "off" look, covered icon, grey text) with "Deleted - restore it within 5 h 12 min. Then it is gone." and a Restore
    button (Primary). Its slot is free at once: the limit counts LIVE profiles only (ProfStore.count), so the player may create a new
    profile right away - with a NEW id (nextId skips deleted and archived ids: a new profile never inherits the deleted one's island,
    coins, bags, skills ...). RESTORE within the window removes only those three keys - the profile is back exactly as it was.
  - THE LIMIT AND RESTORE (review fix - delete, create, restore used to grow past the limit, up to 64 live profiles): the delete stores
    the mark p.<id>.slots = the live count before the delete (or the highest mark of the player's other deleted profiles, if higher);
    a player Restore needs live < max(limit, mark), else "No free slot for <name> - you have 5 profiles and the limit is 5.
    Delete another profile first." So a profile comes back even ABOVE a lowered limit (6 profiles on a limit of 4: delete any, restore
    them all, in any order - keep, cannot create more), but slots that were freed by a delete and filled by new profiles stay used. An
    admin restore ignores the mark (an admin's call). NOT fixed here (Skyy decides): every NEW profile still gets the starter coins
    (SkyyCoins), the class kit (SkyyClasses) and the island starter chest (SkyyIslands), so delete + create repeats them.
  - OVERDUE BUT NOT ARCHIVED (review fix): a FAILED switch marker that names the key (or a file error) keeps a profile pending past
    its deadline. The player's Restore says "Too late"; the card shows "Deleted - the undo time is over. Ask an admin." with the state
    word Expired (vanilla disabled grey) instead of Restore; /profiles list and the login line no longer offer it; /profileadmin
    archive list names it ("undo window ENDED ... not archived yet"); /profileadmin archive restore brings it back (deadline ignored).
  - ARCHIVE (the window is over; ProfSweep every 60 s, also at join, when /profiles opens and on a late Restore; takes the player's
    BUSY guard like every switch): the profile's players-file entries are written to
    Skyy_SkyyProfiles/archive/<uuid>/<id>-<time>/profile.properties (+ archive.* facts), the players file drops them and keeps the
    tombstone gone.<id>=<time> + gone.<id>.dir=<folder> (the id is never used again), then inventories/<key>.json is MOVED into that
    folder as inventory.json. NOTHING IS EVER DELETED (a move that fails leaves the file in inventories/, where the admin restore finds
    it). A failed switch marker that names that profile's key keeps it pending (an admin needs those snapshots first). An attempt
    that fails before its players-file commit removes what it wrote (the record, its .tmp, the empty folder - never a folder that
    already existed) and warns once per profile until it works (review fix: it used to leave one folder + one WARN per minute).
    ADMIN: /profileadmin archive list <player> (deleted profiles in their window + archived ones, with their folders) and
    /profileadmin archive restore <player> <name|id|folder> (moves the inventory back, puts the entries back, removes the tombstone,
    renames the folder <folder>-restored; a name another profile took meanwhile gets a new fruit name; a deleted profile that is not
    archived yet - in its window or past it - is simply restored, limit or not). The restored profile is inactive; the player
    switches to it.
  - WALL CLOCK: the window is real time (System.currentTimeMillis against the stored deadline). Time with the server off, a host that
    sleeps or a clock set forward all count, so such a window can end early - the profile is then archived at the next start / join /
    sweep and only an admin can bring it back (/profileadmin archive restore).
  - IDS: a deleted or archived id is never used again, so every delete + create uses one up: MAX_ID 64 -> 256 (review).
  - COMMANDS (Adventurer): /profiles delete <name|number> - the first run explains and asks, the SAME command again within 10 s
    deletes (the SkyyGuilds repeat pattern); /profiles restore <name|number>. /profileadmin archive [list|restore] = skyyprofiles.admin
    (requirePermission + setPermissionGroups(new String[0])).
  - SERVER SETUP > Profiles: "Undo window after deleting a profile" = config deleteUndoHours (int 1-168 h, default 6, live; field
    ProfCfg.UNDO_MS*3600000). A config.properties without the line (every 0.1.1-0.1.4 file) runs with 6; the kit appends the line the
    first time it is changed in game.
  - FOOTER: a Close button (vanilla Secondary + cancel sound) right of the footer text (promised to Skyy; 0.1.4 only had Esc). The
    list draws at most CAP_MAX = 8 cards: live profiles first, then deleted ones, then Create new; whatever does not fit is named in
    the footer (/profiles list shows everything).
  - CHAT: the login line also reminds a player of a deleted profile that can still be restored; /profiles list marks it DELETED with
    its time left; /profileadmin info counts archived profiles.
  - OTHER MODS (tools/PROFILES-CONTRACT.md: their per-profile data is keyed by the profile key): a pending / archived key is never the
    active key, so nothing of theirs is touched - SkyyIslands' island world (skyy-island-<key>; profile 1: the original world) stays on
    the server as it is, SkyyAuctions listings and claims of that key stay (claims wait for the key; its open listings stay listed),
    SkyyBank coins stay in that profile's account file (interest keeps paying every account file), SkyySacks / SkyySkills /
    SkyyCollections / SkyyAccessories / SkyyCoins / SkyyClasses (a pending class kit) files stay under the key. A restore (player or
    admin) brings everything back because the key is the same. Bridge: delete / restore / archive never bump profile:epoch (the active
    profile, its key, class and name never change); profile:list lists live profiles only; NEW profile:fn:state = Function
    apply(String storage key) -> "active" | "inactive" | "pending" | "archived" | null (unknown key, or not a String - a UUID is not
    a key) for adopters that act on keys other than the active one (cache hit = no I/O; never throws; never calls out - the KeyFn
    rules). OPEN (review, SkyyIslands follow-up): co-op members of a deleted / archived profile's island keep their access (SkyyIslands
    homeKey does not ask profile:fn:state yet), while the owner cannot manage that island meanwhile.
  - BUSY: a delete / restore refused because the player's BUSY guard is held (a switch, a recovery, another delete / restore, the
    archive sweep) says "Your profiles are busy for a moment (a switch or a clean-up is running) - try again in a few seconds."
  The shared SKYY CARD block is unchanged (CARD_SHA of SkyyClasses 0.1.9 / SkyyProfiles 0.1.4); the 8 event bindings of 0.1.4 keep
  their selector, data and order (new: pfdel<id> after its card's pfsw<id>, pfres<id>, pfdelyes, pfdelno, pfclose); every 0.1.4
  element id stays; the Create Profile view is 0.1.4's.
  UNVERIFIED (needs the game): the small Switch + Delete pair in the 200 px action column and the greyed deleted card as the client
  draws them (also the Expired state word on an overdue card); the destructive confirm row.
''')
rep('''  config-changes.log, config-history/   0.1.1: the kit's change log and file versions (tools/CONFIG-CONTRACT.md)
  cap-auto.properties      0.1.4: the one-time profile-limit migration marker (migratedAt, result, kept, note, version; delete = run again)
  players/<uuid>.properties  username, active, epoch, switches, prompted, p.<id>.name, p.<id>.class, p.<id>.created,
                           p.<id>.lastPlayed (epoch millis), p.<id>.inv=1 (only while that profile is NOT active: its items are on disk)
''', '''  config-changes.log, config-history/   0.1.1: the kit's change log and file versions (tools/CONFIG-CONTRACT.md)
  cap-auto.properties      0.1.4: the one-time profile-limit migration marker (migratedAt, result, kept, note, version; delete = run again)
  players/<uuid>.properties  username, active, epoch, switches, prompted, p.<id>.name, p.<id>.class, p.<id>.created,
                           p.<id>.lastPlayed (epoch millis), p.<id>.inv=1 (only while that profile is NOT active: its items are on disk),
                           0.1.5: p.<id>.deleted + p.<id>.until (a deleted profile in its undo window, epoch millis) +
                           p.<id>.slots (the live-profile mark a player restore may fill up to), gone.<id> + gone.<id>.dir (an
                           archived profile: its id is never used again)
  archive/<uuid>/<id>-<time>/  0.1.5: an archived profile (admin only): profile.properties (its players-file entries + archive.uuid,
                           archive.username, archive.id, archive.key, archive.at, archive.inventory, archive.version) and
                           inventory.json (its inventories/<key>.json, moved); "-restored" appended after an admin restore
''')
rep('''  switches.log             one line per CREATE / SWITCH / ROLLBACK / RECOVER / RECOVER-INCOMPLETE / KIT-MISSED (0.1.2: SkyyClasses did
                           not record the class kit of a new profile) (admin audit trail)''',
    '''  switches.log             one line per CREATE / SWITCH / ROLLBACK / RECOVER / RECOVER-INCOMPLETE / KIT-MISSED (0.1.2: SkyyClasses did
                           not record the class kit of a new profile) / DELETE / RESTORE / ARCHIVE / ADMIN-RESTORE (0.1.5) (admin audit trail)''')

# ================================================================================================ version, data constants
rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')
rep('''RANK_FN = "rank:fn:profileSlots"       # 0.1.4: read-only hook for LATER (a rank mod may publish it; nobody does yet) - see the docstring
''', '''RANK_FN = "rank:fn:profileSlots"       # 0.1.4: read-only hook for LATER (a rank mod may publish it; nobody does yet) - see the docstring
DEF_UNDO_H = %d                         # 0.1.5 (Skyy 2026-10-01: "then a 6 hour undo window"): config deleteUndoHours default
UNDO_MIN_H, UNDO_MAX_H = %d, %d        # 0.1.5: the window is 1 h to 7 days (Server Setup row bounds; the loader clamps the same)
''' % (UDEF, UMIN, UMAX) + '''SWEEP_S = 60                           # 0.1.5: ProfSweep looks for ended undo windows every 60 s (also at join and when /profiles opens)
ASK_MS = 10000                         # 0.1.5: /profiles delete <name> must be repeated within 10 s (the SkyyGuilds repeat rule)
''')
# 0.1.5 (review): every delete + create uses an id up for good (deleted and archived ids are never reused - other mods keep data under
# the key), so 64 ids could run out ("No free profile id.") after about 60 cycles; the id loops are cheap
rep('''MAX_ID = 64                            # highest profile id ever scanned in a player file
''', '''MAX_ID = 256                           # highest profile id ever scanned in a player file (0.1.5: 64 -> 256 - a deleted or archived id
                                       # is never used again, so every delete + create uses one up)
''')
rep('''need(1 <= CAP_FALLBACK <= CAP_MAX and CAP_MAX >= len(CLASSES), "CAP_MAX must reach every class (the automatic limit grows with them)")
''', '''need(1 <= CAP_FALLBACK <= CAP_MAX and CAP_MAX >= len(CLASSES), "CAP_MAX must reach every class (the automatic limit grows with them)")
need(UNDO_MIN_H <= DEF_UNDO_H <= UNDO_MAX_H and UNDO_MIN_H >= 1, "the undo window default lies inside its bounds (and is never 0)")
''')

# ================================================================================================ the default config file: + deleteUndoHours
rep('''] + [CFG_LINES_011[3], "maxProfiles=%s" % DEF_CAP] + CFG_LINES_011[5:]
''', '''] + [CFG_LINES_011[3], "maxProfiles=%s" % DEF_CAP] + CFG_LINES_011[5:] + [
    # 0.1.5: the undo window after deleting a profile (a file without these lines - every 0.1.1-0.1.4 file - runs with the default)
    "# deleteUndoHours = how many hours a deleted profile can be restored (%d-%d). After that its files move to" % (UNDO_MIN_H, UNDO_MAX_H),
    "#   Skyy_SkyyProfiles/archive (never wiped) - an admin can still bring it back (/profileadmin archive).",
    "deleteUndoHours=%d" % DEF_UNDO_H,
]
need(CFG_LINES[-1] == "deleteUndoHours=%d" % DEF_UNDO_H and all(ord(c) < 128 for c in "".join(CFG_LINES[-3:])), "deleteUndoHours lines")
''')

# ================================================================================================ ProfCfg: UNDO_MS, windowText, load, summary
rep('''F(cfg, "public static volatile String KEEP = %s;" % jstr(DEF_KEEP))
''', '''F(cfg, "public static volatile String KEEP = %s;" % jstr(DEF_KEEP))
F(cfg, "public static volatile long UNDO_MS = %dL;" % (DEF_UNDO_H * 3600000))    # 0.1.5: the undo window after a delete (deleteUndoHours)
''')
rep('''     "field:ProfCfg.MAX_SETTING@config.properties:maxProfiles"),
''', '''     "field:ProfCfg.MAX_SETTING@config.properties:maxProfiles"),
    # 0.1.5 (Skyy 2026-10-01: "then a 6 hour undo window"): how long a deleted profile can be restored; a deadline already given to a
    # player keeps (it is stored with the deletion), so live is safe
    ("deleteUndoHours", "Undo window after deleting a profile", "profiles", "int", str(DEF_UNDO_H), str(UNDO_MIN_H), str(UNDO_MAX_H),
     "step=1", "h", "live", "Hours a deleted profile can be restored. Then it moves to the admin archive (never wiped).",
     "field:ProfCfg.UNDO_MS*3600000@config.properties:deleteUndoHours"),
''')
rep('''need("\\n".join(CFG_LINES_011) + "\\n" != CFG_TEXT and CFG_LINES_011.count("maxProfiles=6") == 1, "the 0.1.1 default differs from 0.1.4's")''',
    '''need("\\n".join(CFG_LINES_011) + "\\n" != CFG_TEXT and CFG_LINES_011.count("maxProfiles=6") == 1, "the 0.1.1 default differs from 0.1.4's")
need(CFG_TEXT.count("\\ndeleteUndoHours=%d\\n" % DEF_UNDO_H) == 1, "CFG_TEXT: one deleteUndoHours line (0.1.5)")''')
rep('''# 0.1.1: the running values, WITHOUT reading the file''', '''# 0.1.5: "6 hours" / "1 hour" - the undo window as the confirm question, the chat lines and the page say it
M(cfg, r"""
public static String windowText() {
  long h = UNDO_MS / 3600000L;
  if (h < 1L) h = 1L;
  return h + (h == 1L ? " hour" : " hours");
}""")
# 0.1.1: the running values, WITHOUT reading the file''')
rep('''    + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS;''',
    '''    + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS + " deleteUndoHours=" + (UNDO_MS / 3600000L);''')
rep('''    long nb = lng(p, "newProfileBackpack", (long) NEW_BACKPACK);
    if (nb < -1L) nb = -1L;
    if (nb > 256L) nb = 256L;
''', '''    long nb = lng(p, "newProfileBackpack", (long) NEW_BACKPACK);
    if (nb < -1L) nb = -1L;
    if (nb > 256L) nb = 256L;
    long uh = lng(p, "deleteUndoHours", UNDO_MS / 3600000L);
    if (uh < @UMIN@L) uh = @UMIN@L;
    if (uh > @UMAX@L) uh = @UMAX@L;
'''.replace("@UMIN@", str(UMIN)).replace("@UMAX@", str(UMAX)))
rep('''    NEW_BACKPACK = (int) nb;
''', '''    NEW_BACKPACK = (int) nb;
    UNDO_MS = uh * 3600000L;
''')

# ================================================================================================ ProfStore: live / deleted / archived ids
rep('''M(sto, r"""
public static boolean exists(java.util.Properties p, String id) {
  if (p == null || id == null) return false;
  return p.getProperty("p." + id + ".name") != null || p.getProperty("p." + id + ".class") != null;
}""")
M(sto, r"""
public static int count(java.util.Properties p) {
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (exists(p, String.valueOf(i))) n++;
  return n;
}""")
M(sto, r"""
public static String nextId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (!exists(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")
M(sto, r"""
public static String lowestId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (exists(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")''', '''M(sto, r"""
public static boolean exists(java.util.Properties p, String id) {
  if (p == null || id == null) return false;
  return p.getProperty("p." + id + ".name") != null || p.getProperty("p." + id + ".class") != null;
}""")
# 0.1.5: exists = the id holds a profile (live OR deleted-pending); live = a profile that is not deleted (switchable, counts for the
# limit, can be active / the key); isDel = deleted, in its undo window (p.<id>.deleted); gone = archived (tombstone gone.<id>: the id
# is never used again, so a new profile can never inherit an archived profile's data in the other mods)
M(sto, r"""
public static boolean isDel(java.util.Properties p, String id) {
  return exists(p, id) && p.getProperty("p." + id + ".deleted") != null;
}""")
M(sto, r"""
public static boolean live(java.util.Properties p, String id) {
  return exists(p, id) && p.getProperty("p." + id + ".deleted") == null;
}""")
M(sto, r"""
public static boolean gone(java.util.Properties p, String id) {
  return p != null && id != null && p.getProperty("gone." + id) != null;
}""")
M(sto, r"""
public static int count(java.util.Properties p) {
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (live(p, String.valueOf(i))) n++;
  return n;
}""")
M(sto, r"""
public static int pendingCount(java.util.Properties p) {
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (isDel(p, String.valueOf(i))) n++;
  return n;
}""")
M(sto, r"""
public static int goneCount(java.util.Properties p) {
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (gone(p, String.valueOf(i))) n++;
  return n;
}""")
M(sto, r"""
public static String nextId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (!exists(p, String.valueOf(i)) && !gone(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")
M(sto, r"""
public static String lowestId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (live(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")''')
rep('''  a = a.trim();
  return exists(p, a) ? a : null;''', '''  a = a.trim();
  return live(p, a) ? a : null;''')
rep('''  if (exists(q, id)) return false;
  String now = String.valueOf(System.currentTimeMillis());''', '''  if (exists(q, id) || gone(q, id)) return false;
  String now = String.valueOf(System.currentTimeMillis());''')
rep('''  if (!exists(q, to)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("active", to);''', '''  if (!live(q, to)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("active", to);''')
STORE_DEL = r'''# 0.1.5: delete / restore / archive / admin restore - each one atomic players-file commit under the store lock (copy-on-write like
# create / setActive); none of them changes "active" or the epoch (the active profile and its key never change)
# p.<id>.slots (review fix: delete -> create -> restore must not grow past the limit) = the live count the player had when they deleted
# it, or the highest mark of their other deleted profiles if that is higher: a player restore is allowed while live < max(limit, mark),
# so a LOWERED limit still lets every deleted profile come back (in any order), but freed slots that were refilled do not
M(sto, r"""
public static long slotsMark(java.util.Properties q) {
  long m = (long) count(q);
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!isDel(q, id)) continue;
    long s = num(q, "p." + id + ".slots");
    if (s > m) m = s;
  }
  return m;
}""")
M(sto, r"""
public static synchronized boolean markDeleted(java.util.UUID u, String id, long at, long until) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!live(q, id) || id.equals(activeOf(q))) return false;
  q.setProperty("p." + id + ".slots", String.valueOf(slotsMark(q)));
  q.setProperty("p." + id + ".deleted", String.valueOf(at));
  q.setProperty("p." + id + ".until", String.valueOf(until));
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized boolean unDelete(java.util.UUID u, String id) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!isDel(q, id)) return false;
  q.remove("p." + id + ".deleted");
  q.remove("p." + id + ".until");
  q.remove("p." + id + ".slots");
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized boolean archiveCommit(java.util.UUID u, String id, long at, String dir) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!isDel(q, id)) return false;
  String pre = "p." + id + ".";
  java.util.Iterator it = new java.util.ArrayList(q.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(pre)) q.remove(k);
  }
  q.setProperty("gone." + id, String.valueOf(at));
  q.setProperty("gone." + id + ".dir", dir);
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized boolean restoreCommit(java.util.UUID u, String id, java.util.Properties rec, String name) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (exists(q, id)) return false;
  String pre = "p." + id + ".";
  java.util.Iterator it = rec.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(pre)) q.setProperty(k, rec.getProperty(k));
  }
  q.remove(pre + "deleted");
  q.remove(pre + "until");
  q.remove(pre + "slots");
  if (name != null && name.length() > 0) q.setProperty(pre + "name", name);
  q.remove("gone." + id);
  q.remove("gone." + id + ".dir");
  return commit(u, q);
}""")
'''
rep('''M(sto, r"""
public static String listText(java.util.Properties p) {''', STORE_DEL + '''M(sto, r"""
public static String listText(java.util.Properties p) {''')
rep('''    String id = String.valueOf(i);
    if (!exists(p, id)) continue;
    if (sb.length() > 0) sb.append(",");''', '''    String id = String.valueOf(i);
    if (!live(p, id)) continue;
    if (sb.length() > 0) sb.append(",");''')
# describe (/profiles list, /profileadmin info): deleted profiles marked with their time left; the slots count live profiles
OLD_DESCRIBE = cut('M(sto, r"""\npublic static String describe(java.util.UUID u) {', 'M(sto, r"""\npublic static void log(String line) {', "@@DESCRIBE@@")
assert "slots \" + n + \"/\" + @PKG@.ProfCfg.capFor(u);" in OLD_DESCRIBE
rep("@@DESCRIBE@@", r'''# 0.1.5: the deadline of a deleted profile (p.<id>.until; a hand-written p.<id>.deleted without it: deleted + the current window)
M(sto, r"""
public static long untilOf(java.util.Properties p, String id) {
  long t = num(p, "p." + id + ".until");
  if (t > 0L) return t;
  long d = num(p, "p." + id + ".deleted");
  return d > 0L ? d + @PKG@.ProfCfg.UNDO_MS : 0L;
}""")
M(sto, r"""
public static String fmtLeft(long ms) {
  if (ms < 60000L) return "less than a minute";
  long m = ms / 60000L;
  long h = m / 60L;
  m = m - h * 60L;
  if (h == 0L) return m + " min";
  return h + " h" + (m > 0L ? " " + m + " min" : "");
}""")
M(sto, r"""
public static String describe(java.util.UUID u) {
  java.util.Properties p = load(u);
  String act = activeOf(p);
  long now = System.currentTimeMillis();
  StringBuilder sb = new StringBuilder();
  int n = 0;
  int shown = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!exists(p, id)) continue;
    if (shown > 0) sb.append(" | ");
    shown++;
    String c = p.getProperty("p." + id + ".class", "");
    String nm = p.getProperty("p." + id + ".name", "?");
    sb.append(id).append(" ").append(nm).append(" - ").append(c.length() == 0 ? "no class" : c);
    if (isDel(p, id)) {
      if (untilOf(p, id) <= now) sb.append(" - DELETED (the undo time is over - only an admin can bring it back)");
      else sb.append(" - DELETED (restore within ").append(fmtLeft(untilOf(p, id) - now)).append(": /profiles restore ").append(nm).append(")");
      continue;
    }
    n++;
    if (id.equals(act)) sb.append(" - ACTIVE");
    else sb.append(" - last played ").append(fmtAgo(num(p, "p." + id + ".lastPlayed")));
  }
  if (shown == 0) return "no profiles yet";
  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.capFor(u);
}""")
''')

# ================================================================================================ ProfSwitch: a deleted profile is no target
rep('''  if (to == null || !@PKG@.ProfStore.exists(p, to)) return "You have no such profile. /profiles list shows yours.";
  if (to.equals(from)) return "You are already on that profile.";''',
    '''  if (to == null || !@PKG@.ProfStore.exists(p, to)) return "You have no such profile. /profiles list shows yours.";
  if (@PKG@.ProfStore.isDel(p, to)) return p.getProperty("p." + to + ".name", "That profile") + " is deleted - restore it first (/profiles restore " + p.getProperty("p." + to + ".name", to) + ").";
  if (to.equals(from)) return "You are already on that profile.";''')
# createFirst: profile 1 = the legacy uuid files; if id 1 is taken by a deleted / archived profile (only after hand edits: a player can
# never delete their last live profile) the first profile takes a new id instead of inheriting that profile's data
rep('''  if (name == null || name.length() == 0 || @PKG@.ProfNames.used(p, name)) name = @PKG@.ProfNames.pick(p, null);
  if (!@PKG@.ProfStore.create(u, "1", name, cls, true)) return "Could not save your profile - try again or ask an admin.";
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("CREATE " + u + " " + pr.getUsername() + " profile 1 " + name + " " + cls + " (first profile = existing data)");''',
    '''  if (name == null || name.length() == 0 || @PKG@.ProfNames.used(p, name)) name = @PKG@.ProfNames.pick(p, null);
  String fid = (@PKG@.ProfStore.exists(p, "1") || @PKG@.ProfStore.gone(p, "1")) ? @PKG@.ProfStore.nextId(p) : "1";
  if (fid == null) return "No free profile id.";
  if (!@PKG@.ProfStore.create(u, fid, name, cls, true)) return "Could not save your profile - try again or ask an admin.";
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("CREATE " + u + " " + pr.getUsername() + " profile " + fid + " " + name + " " + cls + (fid.equals("1") ? " (first profile = existing data)" : " (first live profile; id 1 is deleted or archived)"));''')
rep('''  @PKG@.ProfKit.kitNew(u, @PKG@.ProfStore.keyFor(u, "1"), cls);
  return null;''', '''  @PKG@.ProfKit.kitNew(u, @PKG@.ProfStore.keyFor(u, fid), cls);
  return null;''')

# ================================================================================================ ProfDel + ProfSweep + StateFn (new)
DEL_JAVA = r'''# ================= ProfDel (0.1.5): delete with an undo window, restore, the admin archive =================
# Skyy 2026-10-01: "add a way to delete a profile. (make sure there is a confirm question. then a 6 hour undo window."
# Per-player mutual exclusion = ProfStore.BUSY (the switch / recovery / marker-clear guard): delete, restore, archive and admin
# restore each take it (putIfAbsent; a busy player is refused or retried by the next sweep), so none of them runs beside a switch of
# that player or beside each other. None of them touches the live vanilla inventory (a deleted profile is never the active one: its
# items are in inventories/<key>.json), none changes the active profile, the key or the epoch, and none calls another mod.
# INDEX = players with a deleted profile waiting (built at setup from players/*.properties, kept on delete / restore / archive):
# ProfSweep only looks at them. ASK = the /profiles delete repeat ("uuid:id" -> deadline).
F(dlt, "public static java.nio.file.Path ARCDIR;")
F(dlt, "public static final java.util.concurrent.ConcurrentHashMap INDEX = new java.util.concurrent.ConcurrentHashMap();")
F(dlt, "public static final java.util.concurrent.ConcurrentHashMap ASK = new java.util.concurrent.ConcurrentHashMap();")
F(dlt, "public static final long ASK_MS = %dL;" % ASK_MS)
F(dlt, "public static final java.util.concurrent.atomic.AtomicBoolean MARKER_WARNED = new java.util.concurrent.atomic.AtomicBoolean(false);")
# review fix: an archive attempt that keeps failing warns once per profile ("uuid:id"; cleared when it works), not every 60 s
F(dlt, "public static final java.util.concurrent.ConcurrentHashMap ARC_WARNED = new java.util.concurrent.ConcurrentHashMap();")
F(dlt, "public static final java.util.concurrent.atomic.AtomicInteger ARC_WARNS = new java.util.concurrent.atomic.AtomicInteger(0);")
M(dlt, r"""
public static String nameOf(java.util.Properties p, String id) {
  return p.getProperty("p." + id + ".name", "Profile " + id);
}""")
# the player's BUSY guard is taken by switches, crash recovery, deletes, restores and the archive sweep - say so (review: not "a switch")
M(dlt, r"""
public static String busyText() {
  return "Your profiles are busy for a moment (a switch or a clean-up is running) - try again in a few seconds.";
}""")
M(dlt, r"""
public static void pub(java.util.UUID u) {
  try { @PKG@.ProfStore.publish(u); } catch (Throwable t) { @PKG@.ProfCfg.warn("publish for " + u + " after a profile delete / restore failed: " + t); }
}""")
# review fix (delete -> create -> restore grew past the limit): a player restore needs live < max(limit, p.<id>.slots) - the mark the
# delete stored (ProfStore.slotsMark); null = there is room. An admin restore ignores it (an admin's decision). cap = ProfCfg.capFor,
# resolved by the caller BEFORE it takes the BUSY guard (capFor may ask a rank mod's bridge function)
M(dlt, r"""
public static String slotBlock(java.util.Properties p, String id, int cap) {
  int n = @PKG@.ProfStore.count(p);
  long had = @PKG@.ProfStore.num(p, "p." + id + ".slots");
  long room = had > (long) cap ? had : (long) cap;
  if ((long) n < room) return null;
  return "No free slot for " + nameOf(p, id) + " - you have " + n + " profiles and the limit is " + cap + ". Delete another profile first.";
}""")
M(dlt, r"""
public static void warnArc(java.util.UUID u, String id, String msg) {
  if (ARC_WARNED.putIfAbsent(u + ":" + id, Boolean.TRUE) != null) return;
  ARC_WARNS.incrementAndGet();
  @PKG@.ProfCfg.warn(msg + " (logged once for this profile until it works)");
}""")
# an archive attempt that failed before its players-file commit: remove only what it wrote itself (the record, its .tmp, the empty
# folder) - the profile is still complete in the players file; a folder that holds anything else stays
M(dlt, r"""
public static void cleanDir(java.nio.file.Path dir) {
  try { java.nio.file.Files.deleteIfExists(dir.resolve("profile.properties.tmp")); } catch (Throwable t) { }
  try { java.nio.file.Files.deleteIfExists(dir.resolve("profile.properties")); } catch (Throwable t) { }
  try { java.nio.file.Files.deleteIfExists(dir); } catch (Throwable t) { }
}""")
# why a profile may NOT be deleted right now (null = it may); the page shows Delete only where this is null
M(dlt, r"""
public static String checkState(java.util.UUID u, java.util.Properties p, String id) {
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  if (id == null || !@PKG@.ProfStore.exists(p, id)) return "You have no such profile. /profiles list shows yours.";
  String nm = nameOf(p, id);
  if (@PKG@.ProfStore.isDel(p, id)) return nm + " is already deleted - /profiles restore " + nm + " brings it back.";
  String act = @PKG@.ProfStore.activeOf(p);
  if (act == null) return "Create your first profile first (/profiles create).";
  if (id.equals(act)) return "You are playing " + nm + " right now - switch to another profile first and then delete it.";
  if (@PKG@.ProfStore.count(p) <= 1) return nm + " is your last profile - it cannot be deleted.";
  String mb = @PKG@.ProfSwitch.markerBlock(u);
  if (mb != null) return mb;
  return null;
}""")
M(dlt, r"""
public static String check(java.util.UUID u, java.util.Properties p, String id) {
  String w = checkState(u, p, id);
  if (w != null) return w;
  if (@PKG@.ProfStore.BUSY.containsKey(u)) return busyText();
  return null;
}""")
# INDEX upkeep: an entry is only dropped while holding BUSY (a delete puts it under BUSY), so a delete running beside it never loses it
M(dlt, r"""
public static void reindex(java.util.UUID u) {
  try {
    if (@PKG@.ProfStore.BROKEN.containsKey(u)) return;
    if (@PKG@.ProfStore.pendingCount(@PKG@.ProfStore.load(u)) > 0) { INDEX.put(u, Boolean.TRUE); return; }
    if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return;
    try {
      if (@PKG@.ProfStore.pendingCount(@PKG@.ProfStore.load(u)) == 0) INDEX.remove(u);
      else INDEX.put(u, Boolean.TRUE);
    } finally { @PKG@.ProfStore.BUSY.remove(u); }
  } catch (Throwable t) { }
}""")
M(dlt, r"""
public static String delete(java.util.UUID u, String who, String id) {
  java.util.Properties p = @PKG@.ProfStore.load(u);
  String why = check(u, p, id);
  if (why != null) return why;
  if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return busyText();
  String r = null;
  try {
    p = @PKG@.ProfStore.load(u);
    r = checkState(u, p, id);
    if (r == null) {
      String nm = nameOf(p, id);
      String cls = p.getProperty("p." + id + ".class", "");
      long now = System.currentTimeMillis();
      long until = now + @PKG@.ProfCfg.UNDO_MS;
      if (!@PKG@.ProfStore.markDeleted(u, id, now, until)) r = "Could not save the change - nothing was deleted. Try again or ask an admin.";
      else {
        INDEX.put(u, Boolean.TRUE);
        @PKG@.ProfStore.log("DELETE " + u + " " + who + " profile " + id + " " + nm + " " + cls + " key " + @PKG@.ProfStore.keyFor(u, id) + " undo until " + java.time.Instant.ofEpochMilli(until));
      }
    }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("delete of profile " + id + " of " + u + " failed: " + t); r = "Could not delete the profile - see the server log."; }
  @PKG@.ProfStore.BUSY.remove(u);
  if (r == null) pub(u);
  return r;
}""")
# a move inside Skyy_SkyyProfiles (same volume: an atomic rename); never replaces an existing file; 5 x 20 ms retries on Windows
# sharing violations (the atomicWrite rule)
M(dlt, r"""
public static void moveFile(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {
  if (java.nio.file.Files.exists(to, new java.nio.file.LinkOption[0])) throw new java.nio.file.FileAlreadyExistsException(to.toString());
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[0]);
      return;
    } catch (java.nio.file.FileAlreadyExistsException e) {
      throw e;
    } catch (java.nio.file.NoSuchFileException e) {
      throw e;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
# BUSY held by the caller. Order: the record (a copy of the entries) -> the players file (entries out, tombstone in: the profile is
# archived from here on) -> the inventory file moved in. A crash after the commit leaves inventories/<key>.json where it was (its id
# is tombstoned, so nothing else can ever use that key) - archive list says so and the admin restore takes it from there.
M(dlt, r"""
public static boolean archiveLocked(java.util.UUID u, String id, long now) throws java.io.IOException {
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (!@PKG@.ProfStore.isDel(p, id) || @PKG@.ProfStore.untilOf(p, id) > now) return false;
  String key = @PKG@.ProfStore.keyFor(u, id);
  java.util.Properties m = @PKG@.ProfSwitch.readMarker(u);
  if (m != null && "failed".equals(m.getProperty("stage", "")) && (key.equals(m.getProperty("fromKey", "")) || key.equals(m.getProperty("toKey", "")))) {
    if (MARKER_WARNED.compareAndSet(false, true)) @PKG@.ProfCfg.warn("deleted profile " + id + " of " + u + " stays pending: a FAILED switch marker names its snapshot " + key + " (an admin checks switching/" + u + ".properties first; logged once)");
    return false;
  }
  String nm = nameOf(p, id);
  String cls = p.getProperty("p." + id + ".class", "");
  String dn = id + "-" + now;
  java.nio.file.Path dir = ARCDIR.resolve(u.toString()).resolve(dn);
  if (java.nio.file.Files.exists(dir, new java.nio.file.LinkOption[0])) throw new java.nio.file.FileAlreadyExistsException(dir.toString() + " (an archive folder of that name exists - left alone)");
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path inv = @PKG@.ProfInv.fileOf(key);
  boolean hadInv = java.nio.file.Files.exists(inv, new java.nio.file.LinkOption[0]);
  java.util.Properties rec = new java.util.Properties();
  String pre = "p." + id + ".";
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(pre)) rec.setProperty(k, p.getProperty(k));
  }
  rec.setProperty("archive.uuid", u.toString());
  rec.setProperty("archive.username", p.getProperty("username", ""));
  rec.setProperty("archive.id", id);
  rec.setProperty("archive.key", key);
  rec.setProperty("archive.at", String.valueOf(now));
  rec.setProperty("archive.inventory", hadInv ? "inventory.json" : "none");
  rec.setProperty("archive.version", "__VER__");
  java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
  rec.store(bo, "SkyyProfiles archived profile (its undo window ended) - /profileadmin archive restore <player> <name> brings it back");
  java.nio.file.Path rf = dir.resolve("profile.properties");
  try { @PKG@.ProfCfg.atomicWrite(rf, bo.toByteArray()); }
  catch (java.io.IOException e) { cleanDir(dir); throw e; }
  catch (RuntimeException e) { cleanDir(dir); throw e; }
  if (!@PKG@.ProfStore.archiveCommit(u, id, now, dn)) {
    cleanDir(dir);
    warnArc(u, id, "could not archive profile " + id + " of " + u + " (players file not saved) - it stays deleted-pending and the next sweep tries again");
    return false;
  }
  String where = hadInv ? " (with its inventory)" : " (it had no saved inventory)";
  if (hadInv) {
    try { moveFile(inv, dir.resolve("inventory.json")); }
    catch (Throwable t) {
      where = " (its inventory could NOT be moved and stays in inventories/" + key + ".json - the admin restore finds it there)";
      @PKG@.ProfCfg.warn("archived profile " + id + " of " + u + " but " + inv + " could not be moved into " + dir + ": " + t);
    }
  }
  @PKG@.ProfStore.log("ARCHIVE " + u + " " + p.getProperty("username", "?") + " profile " + id + " " + nm + " " + cls + " key " + key + " -> archive/" + u + "/" + dn + where);
  return true;
}""".replace("__VER__", VERSION))
M(dlt, r"""
public static int expirePlayer(java.util.UUID u, long now) {
  int n = 0;
  try {
    if (u == null || ARCDIR == null) return 0;
    java.util.Properties p = @PKG@.ProfStore.load(u);
    if (@PKG@.ProfStore.BROKEN.containsKey(u)) return 0;
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      String id = String.valueOf(i);
      if (!@PKG@.ProfStore.isDel(p, id) || @PKG@.ProfStore.untilOf(p, id) > now) continue;
      if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) break;
      boolean ok = false;
      try { ok = archiveLocked(u, id, now); }
      catch (Throwable t) { warnArc(u, id, "archiving profile " + id + " of " + u + " failed (it stays deleted-pending; retried by the next sweep): " + t); }
      @PKG@.ProfStore.BUSY.remove(u);
      if (ok) { n++; ARC_WARNED.remove(u + ":" + id); }
    }
    reindex(u);
  } catch (Throwable t) { @PKG@.ProfCfg.warn("expiry check for " + u + " failed: " + t); }
  return n;
}""")
M(dlt, r"""
public static String restore(java.util.UUID u, String who, String id) {
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (id == null || !@PKG@.ProfStore.exists(p, id)) return "You have no such profile. /profiles list shows yours.";
  String nm = nameOf(p, id);
  if (!@PKG@.ProfStore.isDel(p, id)) return nm + " is not deleted.";
  String late = "Too late - the undo time of " + nm + " is over. Only an admin can bring it back now.";
  if (@PKG@.ProfStore.untilOf(p, id) <= System.currentTimeMillis()) { expirePlayer(u, System.currentTimeMillis()); return late; }
  int cap = @PKG@.ProfCfg.capFor(u);
  if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return busyText();
  String r = null;
  try {
    p = @PKG@.ProfStore.load(u);
    String full = @PKG@.ProfStore.isDel(p, id) ? slotBlock(p, id, cap) : null;
    if (!@PKG@.ProfStore.isDel(p, id)) r = nm + " is not deleted.";
    else if (@PKG@.ProfStore.untilOf(p, id) <= System.currentTimeMillis()) r = late;
    else if (full != null) r = full;
    else if (!@PKG@.ProfStore.unDelete(u, id)) r = "Could not save the change - try again or ask an admin.";
    else @PKG@.ProfStore.log("RESTORE " + u + " " + who + " profile " + id + " " + nm + " key " + @PKG@.ProfStore.keyFor(u, id));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("restore of profile " + id + " of " + u + " failed: " + t); r = "Could not restore the profile - see the server log."; }
  @PKG@.ProfStore.BUSY.remove(u);
  if (r == null) { reindex(u); pub(u); }
  else if (r == late) expirePlayer(u, System.currentTimeMillis());
  return r;
}""")
M(dlt, r"""
public static int expireDue(long now) {
  int n = 0;
  java.util.ArrayList ks = new java.util.ArrayList(INDEX.keySet());
  for (int i = 0; i < ks.size(); i++) n = n + expirePlayer((java.util.UUID) ks.get(i), now);
  return n;
}""")
# setup(): which players have a deleted profile waiting (the deadlines are in their files, so a restart keeps every timer)
M(dlt, r"""
public static int scanIndex() {
  int n = 0;
  try {
    java.nio.file.Path d = @PKG@.ProfStore.DIR;
    if (d == null || !java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return 0;
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d, "*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it.next();
        String fn = f.getFileName().toString();
        java.util.UUID u = null;
        try { u = java.util.UUID.fromString(fn.substring(0, fn.length() - 11)); } catch (Throwable t) { u = null; }
        if (u != null) {
          java.util.Properties q = null;
          try { q = @PKG@.ProfStore.readPath(f); } catch (Throwable t) { q = null; }
          if (q != null && @PKG@.ProfStore.pendingCount(q) > 0) { INDEX.put(u, Boolean.TRUE); n++; }
        }
      }
    } finally { ds.close(); }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not scan players/ for deleted profiles (they are checked at join and when /profiles opens): " + t); }
  return n;
}""")
# join: a player whose only profiles are deleted ones (players file edited by hand - a player can never delete the last live one)
# gets the newest of them back, so they always have a live profile and the key is never a deleted profile's
M(dlt, r"""
public static void repairNoLive(java.util.UUID u) {
  try {
    java.util.Properties p = @PKG@.ProfStore.load(u);
    if (@PKG@.ProfStore.BROKEN.containsKey(u) || @PKG@.ProfStore.count(p) > 0 || @PKG@.ProfStore.pendingCount(p) == 0) return;
    String best = null;
    long bt = -1L;
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      String id = String.valueOf(i);
      long t = @PKG@.ProfStore.num(p, "p." + id + ".deleted");
      if (@PKG@.ProfStore.isDel(p, id) && t >= bt) { best = id; bt = t; }
    }
    if (best != null && @PKG@.ProfStore.unDelete(u, best)) {
      @PKG@.ProfCfg.warn("player " + u + " had no profile left except deleted ones (players file edited by hand?) - restored profile " + best + " " + nameOf(p, best));
      @PKG@.ProfStore.log("RESTORE " + u + " (join repair: no live profile left) profile " + best + " " + nameOf(p, best));
      reindex(u);
    }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("join repair (deleted profiles) failed for " + u + ": " + t); }
}""")
M(dlt, r"""
public static String pendingNote(java.util.Properties p) {
  String first = null;
  int n = 0;
  long now = System.currentTimeMillis();
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!@PKG@.ProfStore.isDel(p, id) || @PKG@.ProfStore.untilOf(p, id) <= now) continue;
    n++;
    if (first == null) first = id;
  }
  if (first == null) return null;
  String nm = nameOf(p, first);
  return "Your deleted profile " + nm + " can still be restored for " + @PKG@.ProfStore.fmtLeft(@PKG@.ProfStore.untilOf(p, first) - System.currentTimeMillis()) + ": /profiles restore " + nm + (n > 1 ? " (" + (n - 1) + " more - /profiles list)" : "") + ".";
}""")
# the archive records of one player: Object[] { folder Path, profile.properties }, by folder name; "-restored" folders are history
M(dlt, r"""
public static java.util.ArrayList records(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (ARCDIR == null || u == null) return out;
  java.nio.file.Path d = ARCDIR.resolve(u.toString());
  if (!java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return out;
  java.util.ArrayList names = new java.util.ArrayList();
  try {
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d);
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        java.nio.file.Path x = (java.nio.file.Path) it.next();
        String nm = x.getFileName().toString();
        if (!nm.endsWith("-restored") && java.nio.file.Files.isRegularFile(x.resolve("profile.properties"), new java.nio.file.LinkOption[0])) names.add(nm);
      }
    } finally { ds.close(); }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not list " + d + ": " + t); }
  java.util.Collections.sort(names);
  for (int i = 0; i < names.size(); i++) {
    java.nio.file.Path x = d.resolve((String) names.get(i));
    try { out.add(new Object[] { x, @PKG@.ProfStore.readPath(x.resolve("profile.properties")) }); }
    catch (Throwable t) { @PKG@.ProfCfg.warn("could not read " + x + ": " + t); }
  }
  return out;
}""")
M(dlt, r"""
public static java.util.ArrayList archiveText(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Properties p = @PKG@.ProfStore.load(u);
  long now = System.currentTimeMillis();
  String un = p.getProperty("username", u.toString());
  int pend = 0;
  int over = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!@PKG@.ProfStore.isDel(p, id)) continue;
    long until = @PKG@.ProfStore.untilOf(p, id);
    String head = "  " + id + " " + nameOf(p, id) + " (" + p.getProperty("p." + id + ".class", "no class") + ") - deleted " + @PKG@.ProfStore.fmtAgo(@PKG@.ProfStore.num(p, "p." + id + ".deleted"));
    if (until <= now) {
      over++;
      out.add(head + ", undo window ENDED " + @PKG@.ProfStore.fmtAgo(until) + " but it is not archived yet (a FAILED switch marker names it, or a file error - server log; archived once that is fixed). The player cannot restore it any more - /profileadmin archive restore can.");
    } else {
      pend++;
      out.add(head + ", undo window ends in " + @PKG@.ProfStore.fmtLeft(until - now) + " (the player can still /profiles restore it)");
    }
  }
  java.util.ArrayList rs = records(u);
  for (int i = 0; i < rs.size(); i++) {
    Object[] r = (Object[]) rs.get(i);
    java.nio.file.Path x = (java.nio.file.Path) r[0];
    java.util.Properties q = (java.util.Properties) r[1];
    String id = q.getProperty("archive.id", "?");
    String key = q.getProperty("archive.key", "");
    boolean inv = java.nio.file.Files.exists(x.resolve("inventory.json"), new java.nio.file.LinkOption[0]);
    boolean left = !inv && key.length() > 0 && java.nio.file.Files.exists(@PKG@.ProfInv.fileOf(key), new java.nio.file.LinkOption[0]);
    String what = inv ? "inventory saved" : (left ? "inventory still in inventories/" + key + ".json" : ("none".equals(q.getProperty("archive.inventory", "")) ? "no inventory (never played)" : "inventory MISSING"));
    out.add("  " + id + " " + q.getProperty("p." + id + ".name", "?") + " (" + q.getProperty("p." + id + ".class", "no class") + ") - archived " + @PKG@.ProfStore.fmtDate(@PKG@.ProfStore.num(q, "archive.at")) + " - " + what + " - folder " + x.getFileName());
  }
  out.add(0, un + ": " + pend + " deleted profile(s) in their undo window, " + (over > 0 ? over + " past it (not archived yet), " : "") + rs.size() + " archived (Skyy_SkyyProfiles/archive/" + u + "). Restore: /profileadmin archive restore " + un + " <name, number or folder>");
  return out;
}""")
# BUSY held by the caller: the inventory back first, then the entries (a failed commit moves the inventory back again)
M(dlt, r"""
public static String adminRestoreLocked(java.util.UUID u, java.nio.file.Path dir, java.util.Properties rec, String admin) throws java.io.IOException {
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "-That player's profile file could not be read (server log) - nothing was changed.";
  String id = rec.getProperty("archive.id", "");
  String key = @PKG@.ProfStore.keyFor(u, id);
  if (id.length() == 0 || !key.equals(rec.getProperty("archive.key", key)) || rec.getProperty("p." + id + ".name") == null) return "-The archive record " + dir + " is damaged (archive.id / archive.key / name) - nothing was changed.";
  if (@PKG@.ProfStore.exists(p, id)) return "-Profile id " + id + " of that player is in use - check players/" + u + ".properties by hand (nothing was changed).";
  String nm = rec.getProperty("p." + id + ".name", "Profile " + id);
  String name = nm;
  if (@PKG@.ProfNames.used(p, nm)) name = @PKG@.ProfNames.pick(p, null);
  java.nio.file.Path inv = @PKG@.ProfInv.fileOf(key);
  java.nio.file.Path ain = dir.resolve("inventory.json");
  boolean want = "1".equals(rec.getProperty("p." + id + ".inv")) || "inventory.json".equals(rec.getProperty("archive.inventory", ""));
  boolean moved = false;
  if (java.nio.file.Files.exists(ain, new java.nio.file.LinkOption[0])) {
    if (java.nio.file.Files.exists(inv, new java.nio.file.LinkOption[0])) return "-Both " + ain + " and " + inv + " exist - check them by hand (nothing was changed).";
    moveFile(ain, inv);
    moved = true;
  } else if (want && !java.nio.file.Files.exists(inv, new java.nio.file.LinkOption[0])) {
    return "-The saved inventory of " + nm + " is missing (" + ain + ") - nothing was changed.";
  }
  if (!@PKG@.ProfStore.restoreCommit(u, id, rec, name)) {
    if (moved) { try { moveFile(inv, ain); } catch (Throwable t) { @PKG@.ProfCfg.warn("could not move " + inv + " back to " + ain + ": " + t); } }
    return "-Could not save players/" + u + ".properties - nothing was changed.";
  }
  try { moveFile(dir, dir.resolveSibling(dir.getFileName().toString() + "-restored")); }
  catch (Throwable t) { @PKG@.ProfCfg.warn("restored profile " + id + " of " + u + " but could not rename " + dir + " (it would be listed again; rename it by hand): " + t); }
  @PKG@.ProfStore.log("ADMIN-RESTORE " + u + " profile " + id + " " + nm + (name.equals(nm) ? "" : " as " + name) + " key " + key + " from archive/" + u + "/" + dir.getFileName() + " by " + admin);
  return "+Restored profile " + name + (name.equals(nm) ? "" : " (it was called " + nm + " - another profile has that name now)") + " (number " + id + "). It is not active - the player switches to it in /profiles.";
}""")
M(dlt, r"""
public static String adminRestore(java.util.UUID u, String arg, String admin) {
  if (u == null || arg == null || arg.trim().length() == 0) return "-Usage: /profileadmin archive restore <player> <name, number or folder>";
  String a = arg.trim();
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "-That player's profile file could not be read (server log).";
  // a deleted profile that is not archived yet: back at once - also past its deadline (review fix: a FAILED switch marker or a file
  // error can keep it pending after the window; the player's Restore says "too late" then) and above the limit (an admin's call)
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!@PKG@.ProfStore.isDel(p, id) || !(a.equals(id) || a.equalsIgnoreCase(nameOf(p, id)))) continue;
    if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return "-That player's profiles are busy for a moment (a switch or a clean-up) - try again in a few seconds.";
    String e = null;
    int done = 0;
    try {
      java.util.Properties q = @PKG@.ProfStore.load(u);
      if (@PKG@.ProfStore.isDel(q, id)) {
        boolean late = @PKG@.ProfStore.untilOf(q, id) <= System.currentTimeMillis();
        if (!@PKG@.ProfStore.unDelete(u, id)) e = "-Could not save players/" + u + ".properties - nothing was changed.";
        else {
          done = late ? 2 : 1;
          @PKG@.ProfStore.log("ADMIN-RESTORE " + u + " profile " + id + " " + nameOf(q, id) + " key " + @PKG@.ProfStore.keyFor(u, id) + " (deleted, " + (late ? "past its undo window but not archived yet" : "in its undo window") + ") by " + admin);
        }
      }
    } catch (Throwable t) { @PKG@.ProfCfg.warn("admin restore of profile " + id + " of " + u + " failed: " + t); e = "-Could not restore it (see the server log): " + t.getMessage(); }
    @PKG@.ProfStore.BUSY.remove(u);
    if (e != null) return e;
    if (done > 0) {
      reindex(u);
      pub(u);
      return "+Restored " + nameOf(p, id) + (done == 2 ? " - its undo window had ended but it was not archived yet." : " - it was still in its undo window.") + " It is not active - the player switches to it in /profiles.";
    }
    break;   // archived meanwhile: the archive records below have it
  }
  java.util.ArrayList rs = records(u);
  Object[] hit = null;
  int hits = 0;
  for (int i = 0; i < rs.size(); i++) {
    Object[] r = (Object[]) rs.get(i);
    java.util.Properties q = (java.util.Properties) r[1];
    String id = q.getProperty("archive.id", "");
    String dn = ((java.nio.file.Path) r[0]).getFileName().toString();
    if (a.equals(id) || a.equalsIgnoreCase(q.getProperty("p." + id + ".name", "")) || a.equalsIgnoreCase(dn)) { hit = r; hits++; }
  }
  if (hits == 0) return "-No deleted or archived profile '" + a + "' for that player - /profileadmin archive list <player> shows them.";
  if (hits > 1) return "-" + hits + " archived profiles match '" + a + "' - use the folder name from /profileadmin archive list <player>.";
  if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return "-That player's profiles are busy for a moment (a switch or a clean-up) - try again in a few seconds.";
  String r = null;
  try { r = adminRestoreLocked(u, (java.nio.file.Path) hit[0], (java.util.Properties) hit[1], admin); }
  catch (Throwable t) { @PKG@.ProfCfg.warn("admin restore for " + u + " failed: " + t); r = "-Could not restore it (see the server log): " + t.getMessage(); }
  @PKG@.ProfStore.BUSY.remove(u);
  if (r != null && r.startsWith("+")) pub(u);
  return r;
}""")
# /profiles delete <name>: the first run asks, the SAME command again within 10 s deletes (marks: + done, - refused, = a question)
M(dlt, r"""
public static String cmdDelete(java.util.UUID u, String who, String arg) {
  String id = @PKG@.ProfStore.resolveId(u, arg);
  if (id == null) return "-No profile '" + arg + "'. Yours: " + @PKG@.ProfStore.describe(u);
  java.util.Properties p = @PKG@.ProfStore.load(u);
  String why = check(u, p, id);
  if (why != null) { ASK.remove(u + ":" + id); return "-" + why; }
  String nm = nameOf(p, id);
  String cls = p.getProperty("p." + id + ".class", "");
  String k = u + ":" + id;
  long now = System.currentTimeMillis();
  Object t = ASK.get(k);
  if (!(t instanceof Long) || ((Long) t).longValue() < now) {
    ASK.put(k, Long.valueOf(now + ASK_MS));
    return "=Delete profile " + nm + (cls.length() > 0 ? " (" + cls + ")" : "") + "? Its island, coins, skills, bags and items will be gone. You have " + @PKG@.ProfCfg.windowText() + " to undo this (/profiles restore " + nm + "). Type /profiles delete " + nm + " again within " + (ASK_MS / 1000L) + " s to confirm.";
  }
  ASK.remove(k);
  String err = delete(u, who, id);
  if (err != null) return "-" + err;
  return "+Profile " + nm + " is deleted. /profiles restore " + nm + " brings it back within " + @PKG@.ProfCfg.windowText() + " - after that it is gone.";
}""")
M(dlt, r"""
public static String cmdRestore(java.util.UUID u, String who, String arg) {
  String id = @PKG@.ProfStore.resolveId(u, arg);
  if (id == null) return "-No profile '" + arg + "'. Yours: " + @PKG@.ProfStore.describe(u);
  String nm = nameOf(@PKG@.ProfStore.load(u), id);
  String err = restore(u, who, id);
  if (err != null) return "-" + err;
  int c = @PKG@.ProfStore.count(@PKG@.ProfStore.load(u));
  int cap = @PKG@.ProfCfg.capFor(u);
  return "+Profile " + nm + " is back - exactly as it was. /profiles switch " + nm + " plays it." + (c > cap ? " You now have " + c + " profiles - more than the " + cap + " this server allows - so you cannot create another one." : "");
}""")
M(dlt, r"""
public static void tell(@PR@ pr, String r) {
  if (pr == null || r == null) return;
  String col = "#8fe39a";
  String t = r;
  if (r.startsWith("-")) { col = "#ff9d6b"; t = r.substring(1); }
  else if (r.startsWith("=")) { col = "#ffc800"; t = r.substring(1); }
  else if (r.startsWith("+")) t = r.substring(1);
  pr.sendMessage(@MSG@.raw("[Profiles] " + t).color(col));
}""")
# profile:fn:state - what a storage key is now: "active" (the key profile:fn:key returns), "inactive" (a live profile), "pending"
# (deleted, in its undo window), "archived", or null (not a SkyyProfiles key). Same cost rules as profile:fn:key: a cache hit is no I/O,
# a miss reads that players file under the store lock; never throws, never calls out.
M(dlt, r"""
public static String state(String key) {
  if (key == null || key.length() < 36) return null;
  java.util.UUID u = null;
  try { u = java.util.UUID.fromString(key.substring(0, 36)); } catch (Throwable t) { return null; }
  if (!u.toString().equals(key.substring(0, 36))) return null;
  String rest = key.substring(36);
  String id = null;
  if (rest.length() == 0) id = "1";
  else if (rest.startsWith("-p")) {
    id = rest.substring(2);
    try { int n = Integer.parseInt(id); if (n < 2 || !String.valueOf(n).equals(id)) return null; } catch (Throwable t) { return null; }
  } else return null;
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.live(p, id)) return id.equals(@PKG@.ProfStore.keyId(p)) ? "active" : "inactive";
  if (@PKG@.ProfStore.isDel(p, id)) return "pending";
  if (@PKG@.ProfStore.gone(p, id)) return "archived";
  if (id.equals("1") && @PKG@.ProfStore.keyId(p) == null) return "active";
  return null;
}""")

# ================= ProfSweep (0.1.5): every 60 s, archive the deleted profiles whose undo window ended (scheduler thread) =================
swp.addInterface(pool.get("java.lang.Runnable"))
C(swp, "public ProfSweep() { }")
M(swp, r"""
public void run() {
  try {
    int n = @PKG@.ProfDel.expireDue(System.currentTimeMillis());
    if (n > 0) @PKG@.ProfCfg.info("archived " + n + " deleted profile(s) whose undo window ended (Skyy_SkyyProfiles/archive; /profileadmin archive list <player>)");
  } catch (Throwable t) { @PKG@.ProfCfg.warn("deleted-profile sweep failed: " + t); }
}""")

# ================= StateFn (0.1.5): bridge profile:fn:state =================
# a String storage key only; anything else (a UUID too - it is not a key: profile:fn:key turns it into one) answers null (review tidy:
# a UUID used to answer quietly for profile 1's key)
sfn.addInterface(pool.get("java.util.function.Function"))
C(sfn, "public StateFn() { }")
M(sfn, r"""
public Object apply(Object o) {
  try {
    if (o instanceof String) return @PKG@.ProfDel.state((String) o);
  } catch (Throwable t) { }
  return null;
}""")

'''
rep("# ================= ProfilePage: Profiles list (view 0) + Create Profile (view 1) =================",
    DEL_JAVA + "# ================= ProfilePage: Profiles list (view 0) + Create Profile (view 1) =================")

# ================================================================================================ ProfilePage: the list view (0.1.5)
rep('''PF_SLOTS_H = 24                         # 0.1.4: create view - the limit line under the class cards (one 15 px caption line, 8 above)
''', '''PF_SLOTS_H = 24                         # 0.1.4: create view - the limit line under the class cards (one 15 px caption line, 8 above)
PF_SW_W, PF_DEL_W = SUI.ROW_ACTION_W, 88   # 0.1.5: the small Switch + Delete pair (vanilla row action width 92; "DELETE" needs 85 at 14 px)
PF_CLOSE_GAP = 12                       # 0.1.5: footer text | 12 px | Close
''')
OLD_LIST_T = cut('PF_BUILD_LIST = r"""', 'PF_BUILD_CREATE = r"""', r'''PF_BUILD_LIST = r"""
public void buildList(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties p) {
  String act = @PKG@.ProfStore.activeOf(p);
  int n = @PKG@.ProfStore.count(p);
  int max = @PKG@.ProfCfg.capFor(u);
  long now = System.currentTimeMillis();
  String[] shown = shownIds(p);
  int nd = @PKG@.ProfStore.pendingCount(p);
  int liveShown = 0;
  int delShown = 0;
  boolean roomNew = n < max && shown.length < @PKG@.ProfCfg.CAP_MAX;
{{SHELL}}
{{SUB}}
{{LIST}}
  for (int j = 0; j < shown.length; j++) {
    String id = shown[j];
    boolean on = id.equals(act);
    boolean del = @PKG@.ProfStore.isDel(p, id);
    boolean over = del && @PKG@.ProfStore.untilOf(p, id) <= now;
    boolean pend = id.equals(this.pending);
    boolean ask = id.equals(this.delAsk);
    boolean canDel = !on && !del && !pend && act != null && n > 1;
    if (del) delShown++; else liveShown++;
    String name = p.getProperty("p." + id + ".name", "Profile " + id);
    String cls = p.getProperty("p." + id + ".class", "");
    String[] ce = @PKG@.ProfRoster.entry(cls);
    String color = ce == null ? "#c9d6e2" : ce[3];
    String line2 = cls.length() == 0 ? "No class - an admin can set it" : cls + " - combat skill " + @PKG@.ProfRoster.skillOf(cls);
    String line3 = over ? "Deleted - the undo time is over. Ask an admin."
      : del ? "Deleted - restore it within " + @PKG@.ProfStore.fmtLeft(@PKG@.ProfStore.untilOf(p, id) - now) + ". Then it is gone."
      : "Created " + @PKG@.ProfStore.fmtDate(@PKG@.ProfStore.num(p, "p." + id + ".created")) + " - "
      + (on ? "playing now" : "last played " + @PKG@.ProfStore.fmtAgo(@PKG@.ProfStore.num(p, "p." + id + ".lastPlayed")));
{{CARD}}
    if (on) {
{{ACTIVE}}
    } else if (over) {
{{EXPIRED}}
    } else if (del) {
{{RESTORE}}
      ev.addEventBinding(@BT@.Activating, "#SkyyPfRes" + id, @EVD@.of("a", "pfres" + id));
    } else if (!canDel) {
{{SWITCH}}
      ev.addEventBinding(@BT@.Activating, "#SkyyPfSw" + id, @EVD@.of("a", "pfsw" + id));
    } else {
{{SWDEL}}
      ev.addEventBinding(@BT@.Activating, "#SkyyPfSw" + id, @EVD@.of("a", "pfsw" + id));
      ev.addEventBinding(@BT@.Activating, "#SkyyPfDel" + id, @EVD@.of("a", "pfdel" + id));
    }
  }
  if (roomNew) {
{{NEWCARD}}
    ev.addEventBinding(@BT@.Activating, "#SkyyPfNew", @EVD@.of("a", "pfnew"));
  }
{{INFO}}
  if (this.pending != null && @PKG@.ProfStore.live(p, this.pending) && !this.pending.equals(act)) {
    String pn = p.getProperty("p." + this.pending + ".name", "Profile " + this.pending);
    String pc = p.getProperty("p." + this.pending + ".class", "");
    String q = "Switch to " + pn + (pc.length() > 0 ? " (" + pc + ")" : "") + "? Your inventory is saved and you go to the island of that profile.";
{{CONFIRM}}
    ev.addEventBinding(@BT@.Activating, "#SkyyPfYes", @EVD@.of("a", "pfyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPfNo", @EVD@.of("a", "pfno"));
  } else if (this.delAsk != null && @PKG@.ProfStore.live(p, this.delAsk) && !this.delAsk.equals(act)) {
    String dq = "Delete profile " + safe(p.getProperty("p." + this.delAsk + ".name", "Profile " + this.delAsk)) + "? Its island, coins, skills, bags and items will be gone. You have " + @PKG@.ProfCfg.windowText() + " to undo this.";
{{DELASK}}
    ev.addEventBinding(@BT@.Activating, "#SkyyPfDelYes", @EVD@.of("a", "pfdelyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPfDelNo", @EVD@.of("a", "pfdelno"));
  } else {
    String used = n + " of " + max + " profile slots used (" + @PKG@.ProfCfg.capWhy(u) + ").";
    if (n > max) used = n + " profiles - this server now allows " + max + ". You keep them all but cannot create more.";
    String foot = used + " Switching saves your inventory and takes you to the island of the other profile. Not while in combat.";
    if (nd > 0) foot = foot + " A deleted profile does not use a slot.";
    if (n > liveShown) foot = foot + " " + (n - liveShown) + " more profiles - /profiles list shows them.";
    if (nd > delShown) foot = foot + " " + (nd - delShown) + " more deleted - /profiles list shows them.";
    if (n < max && !roomNew) foot = foot + " New profile - /profiles create.";
{{FOOT}}
    ev.addEventBinding(@BT@.Activating, "#SkyyPfClose", @EVD@.of("a", "pfclose"));
  }
}"""
''')
# the 0.1.4 template's own statements are all still here (only the loop head, the card flags and the new branches changed)
for ln in ['    String q = "Switch to " + pn + (pc.length() > 0 ? " (" + pc + ")" : "") + "? Your inventory is saved and you go to the island of that profile.";',
           '    ev.addEventBinding(@BT@.Activating, "#SkyyPfSw" + id, @EVD@.of("a", "pfsw" + id));',
           '    ev.addEventBinding(@BT@.Activating, "#SkyyPfNew", @EVD@.of("a", "pfnew"));',
           '    String foot = used + " Switching saves your inventory and takes you to the island of the other profile. Not while in combat.";',
           '    if (n > max) used = n + " profiles - this server now allows " + max + ". You keep them all but cannot create more.";']:
    assert ln in OLD_LIST_T, ln
OLD_LIST_PY = cut("def profile_list_java():", "def profile_create_java():", r'''def profile_list_java():
    """ProfilePage.buildList(): PF_BUILD_LIST with its {{parts}} built from kit calls; the list well fills the body.
    0.1.5: the card loop draws shownIds(p) (live profiles, then deleted ones, at most CAP_MAX cards with Create new); a deleted card =
    the SKYY CARD "off" look (on = !del: grey text, covered icon) + Restore (past its deadline but not archived yet: the state word
    Expired, no Restore - only an admin can bring it back); a live non-active card = the small Switch + Delete pair
    (SWDEL) unless the switch question is open for it (0.1.4's normal Switch); the delete question = confirm_view compact
    (Destructive Delete + Cancel, wraps to two lines) in the footer's place; the footer = the caption + Close (Secondary, cancel)."""
    sh = SUI.page_shell("SkyyPfF", PF_W, PF_H, "Profiles", body_id="SkyyPf")
    body, W = sh.body, sh.inner_w
    list_h = sh.inner_h - (PF_SUB_H + PF_LSUB_GAP) - (PF_LINFO_GAP + PF_INFO_H) - (8 + PF_END_H)
    assert list_h >= card_list_h(CAP_MAX), "the list well must hold CAP_MAX = %d profile cards (%d px)" % (CAP_MAX, list_h)
    assert sh.fit([PF_SUB_H + PF_LSUB_GAP, list_h, PF_LINFO_GAP + PF_INFO_H, 8 + PF_END_H]) == 0
    cw = W - 2 * CARD_LIST_PAD
    ident = SUI.J("id", "1")
    act = "SkyyPfAct" + ident
    ids = {"list": "SkyyPfList", "card": "SkyyPfCard" + ident, "text": "SkyyPfTxt" + ident, "act": act}
    name_col = SUI.J('on ? "%s" : "%s"' % (SUI.COLOR["success"], SUI.COLOR["rowName"]), SUI.COLOR["success"])
    lines = [{"id": "Nm", "text": 'safe(name + (on ? " - ACTIVE" : (del ? " - DELETED" : "")))', "kind": "rowName", "h": 24,
              "col": name_col},
             {"id": "L2", "text": "safe(line2)", "kind": "fieldLabel", "h": 20, "col": SUI.J("color", CLASSES[0]["color"])},
             {"id": "L3", "text": "safe(line3)", "kind": "rowSub", "h": 20, "col": "rowSub"}]
    sw = "SkyyPfSw" + ident
    new_ids = {"list": "SkyyPfList", "card": "SkyyPfNewCard", "text": "SkyyPfNewTxt", "act": "SkyyPfNewAct"}
    new_lines = [{"id": "Tx", "text": 'safe("Empty slot - a new profile starts from zero with the class you pick (" + (max - n) + " free)")',
                  "kind": "default", "h": 44, "col": "text", "wrap": True}]
    confirm = pf_row(body, "SkyyPfConfirm", SUI.J("safe(q)"), "SkyyPfYes", "SkyyPfNo", "Confirm", "Cancel", 180, 180, wrap=True)
    assert confirm.h == 8 + PF_END_H
    # 0.1.5: the small Switch + Delete pair in the card's action column (the block's column: 200 wide, padding left 14 / top 24 for a
    # 44 px button -> the pair fills its 186 px and sits 6 px lower, centred on the card)
    act_inner = CARD_ACT_W - (CARD_ACT_W - CARD_BTN_W) // 2
    assert PF_SW_W + 6 + PF_DEL_W == act_inner == 186, (PF_SW_W, PF_DEL_W, act_inner)
    swrow = "SkyyPfSwRow" + ident
    swdel = SUI.Appends()
    swdel.append((act, SUI.group(swrow, "Left", w=act_inner, h=SUI.BTN_SMALL_H, anchor={"top": (SUI.BTN_H - SUI.BTN_SMALL_H) // 2})))
    swdel.append((swrow, SUI.button(sw, "Switch", "secondary", "small", w=PF_SW_W)))
    swdel.append((swrow, SUI.button("SkyyPfDel" + ident, "Delete", "destructive", "small", w=PF_DEL_W, anchor={"left": 6})))
    restore = card_button("SkyyPfRes" + ident, "Restore", "primary")
    # 0.1.5: the delete question - the kit's one-row confirm in the footer's place (like the switch question), Destructive yes
    delask = SUI.confirm_view(body, "SkyyPfDelRow", W, question=SUI.J("dq"), yes_text="Delete", no_text="Cancel",
                              yes_kind="destructive", yes_w=180, no_w=180, compact=True, top=8, wrap=True,
                              ids={"box": "SkyyPfDelRow", "question": "SkyyPfDelQ", "yes": "SkyyPfDelYes", "no": "SkyyPfDelNo"})
    assert delask.h == 8 + PF_END_H and len(delask.sets) == 1, (delask.h, delask.sets)
    # 0.1.5: the footer row = the caption (wraps, left) + Close (Secondary, cancel sound) - WorldEventPanelPage's footer Close
    fw = W - CARD_BTN_W - PF_CLOSE_GAP
    foot = SUI.Appends()
    foot.append((body, SUI.group("SkyyPfFootRow", "Left", h=PF_END_H, anchor={"top": 8})))
    foot.append(("SkyyPfFootRow", SUI.label("SkyyPfFoot", "", "caption", w=fw, h=PF_END_H, wrap=True)))
    foot.append(("SkyyPfFootRow", SUI.button("SkyyPfClose", "Close", "secondary", w=CARD_BTN_W, sound="cancel",
                                             anchor={"left": PF_CLOSE_GAP, "top": (PF_END_H - SUI.BTN_H) // 2})))
    foot.sets.append(("SkyyPfFoot", "Text", SUI.J("safe(foot)")))
    SUI.assert_proven([swdel, delask, foot, restore], allow=("base", "base4"), what="SkyyProfiles 0.1.5 list view additions")
    sub = SUI.Appends()
    sub.text(body, "SkyyPfSub", "Each profile is its own save - class, island, coins, skills, bags and inventory.", "default",
             h=PF_SUB_H, align="Center", anchor={"bottom": PF_LSUB_GAP})
    parts = {
        "SHELL": sh.java("b"),
        "SUB": sub.java("b"),
        "LIST": SUI.java_append(body, card_list("SkyyPfList", list_h)),
        "CARD": card_java(ids, cw, [("selected", "on"), ("pending", "pend || ask"), ("off", "del"), "normal"], lines,
                          icon_item=SUI.J("safe(@PKG@.ProfRoster.iconOf(cls))", CLASSES[0]["icons"][0]), icon_max=1, on="!del"),
        "ACTIVE": SUI.java_append(act, card_state("Active", "success")),
        # review fix: a deleted card past its deadline (still pending: a FAILED switch marker or a file error stopped the archive) has
        # no Restore - only an admin can bring it back - the 0.1.4 "Coming later" state word (vanilla disabled grey) instead
        "EXPIRED": SUI.java_append(act, card_state("Expired", "disabled")),
        "RESTORE": SUI.java_append(act, restore),
        "SWITCH": SUI.java_append(act, SUI.choose(SUI.J("pend"), card_button(sw, "Switch", "primary"), card_button(sw, "Switch"))),
        "SWDEL": swdel.java("b"),
        "NEWCARD": "\n".join([card_java(new_ids, cw, "empty", new_lines, icon_item=SUI.J("@PKG@.ProfRoster.NEW_ICON", NEW_ICON),
                                        icon_max=1, var="newCard"),
                              SUI.java_append("SkyyPfNewAct", card_button("SkyyPfNew", "Create new", "primary"))]),
        "INFO": "\n".join([SUI.java_append(body, SUI.label("SkyyPfInfo", "", "info", h=PF_INFO_H, bold=True, align="Center",
                                                            anchor={"top": PF_LINFO_GAP})),
                           SUI.java_set("SkyyPfInfo", "Text", SUI.J("safe(this.info)"))]),
        "CONFIRM": confirm.java("b"),
        "DELASK": delask.java("b"),
        "FOOT": foot.java("b"),
    }
    sh.appends.check(PF_PREFIX)
    indent = {"SHELL": 2, "SUB": 2, "LIST": 2, "CARD": 4, "ACTIVE": 6, "EXPIRED": 6, "RESTORE": 6, "SWITCH": 6, "SWDEL": 6, "NEWCARD": 4,
              "INFO": 2, "CONFIRM": 4, "DELASK": 4, "FOOT": 4}
    java = java_fill(PF_BUILD_LIST, dict((k, java_block(v, indent[k])) for k, v in parts.items()))
    pf_ids_kept(java, "list")
    for ident_ in ("SkyyPfDel", "SkyyPfRes", "SkyyPfSwRow"):
        assert ('#%s" + (id)' % ident_) in java, ident_
    for ident_ in ("SkyyPfDelRow", "SkyyPfDelQ", "SkyyPfDelYes", "SkyyPfDelNo", "SkyyPfFootRow", "SkyyPfClose"):
        assert ("#%s {" % ident_) in java, ident_
    return java, sh


''')
for frag in ['"ACTIVE": SUI.java_append(act, card_state("Active", "success")),',
             '"SWITCH": SUI.java_append(act, SUI.choose(SUI.J("pend"), card_button(sw, "Switch", "primary"), card_button(sw, "Switch"))),',
             'confirm = pf_row(body, "SkyyPfConfirm", SUI.J("safe(q)"), "SkyyPfYes", "SkyyPfNo", "Confirm", "Cancel", 180, 180, wrap=True)',
             '"LIST": SUI.java_append(body, card_list("SkyyPfList", list_h)),']:
    assert frag in OLD_LIST_PY, frag          # 0.1.4's parts that 0.1.5 keeps word for word
rep('''F(page, "public boolean reminded;")
''', '''F(page, "public boolean reminded;")
F(page, "public String delAsk;")       # 0.1.5: the profile id the delete question is open for (null = none)
''')
# the cards the list view draws: live profiles (id order), then deleted ones, at most CAP_MAX (the list well holds CAP_MAX cards)
rep('''M(page, PF_LIST_JAVA)
''', '''M(page, r"""
public static String[] shownIds(java.util.Properties p) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < @PKG@.ProfCfg.CAP_MAX; i++) {
    String id = String.valueOf(i);
    if (@PKG@.ProfStore.live(p, id)) out.add(id);
  }
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID && out.size() < @PKG@.ProfCfg.CAP_MAX; i++) {
    String id = String.valueOf(i);
    if (@PKG@.ProfStore.isDel(p, id)) out.add(id);
  }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
M(page, PF_LIST_JAVA)
''')
DEL_EVENT = r'''# 0.1.5: the delete / restore / close clicks (pfdel<id>, pfdelyes, pfdelno, pfres<id>, pfclose); false = not one of them
M(page, r"""
public boolean deleteEvent(@REF@ ref, @ST@ st, String data, java.util.UUID u, java.util.Properties p) {
  if (data.indexOf("pfclose\"") >= 0) { closeSelf(ref, st); return true; }
  if (data.indexOf("pfdelno\"") >= 0) { this.delAsk = null; this.info = ""; rebuild(); return true; }
  if (data.indexOf("pfdelyes\"") >= 0) {
    String id = this.delAsk;
    this.delAsk = null;
    if (id == null) { rebuild(); return true; }
    String nm = p.getProperty("p." + id + ".name", "Profile " + id);
    String err = @PKG@.ProfDel.delete(u, this.playerRef.getUsername(), id);
    this.info = err != null ? err : nm + " is deleted. Restore it within " + @PKG@.ProfCfg.windowText() + " - after that it is gone.";
    rebuild();
    return true;
  }
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (data.indexOf("pfdel" + i + "\"") >= 0) {
      String why = @PKG@.ProfDel.check(u, p, id);
      this.pending = null;
      if (why != null) { this.delAsk = null; this.info = why; }
      else { this.delAsk = id; this.info = ""; }
      rebuild();
      return true;
    }
    if (data.indexOf("pfres" + i + "\"") >= 0) {
      String nm = p.getProperty("p." + id + ".name", "Profile " + id);
      String err = @PKG@.ProfDel.restore(u, this.playerRef.getUsername(), id);
      this.delAsk = null;
      this.pending = null;
      if (err != null) this.info = err;
      else {
        int c = @PKG@.ProfStore.count(@PKG@.ProfStore.load(u));
        int cap = @PKG@.ProfCfg.capFor(u);
        this.info = nm + " is back - exactly as it was." + (c > cap ? " You now have " + c + " profiles - more than the " + cap + " allowed - so you cannot create more." : "");
      }
      rebuild();
      return true;
    }
  }
  return false;
}""")
'''
rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', DEL_EVENT + '''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')
rep('''    java.util.Properties p = @PKG@.ProfStore.load(u);
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      if (data.indexOf("pfsw" + i + "\\"") < 0) continue;
      String id = String.valueOf(i);
      this.pending = @PKG@.ProfStore.exists(p, id) ? id : null;
      this.info = "";''', '''    java.util.Properties p = @PKG@.ProfStore.load(u);
    if (deleteEvent(ref, st, data, u, p)) return;
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      if (data.indexOf("pfsw" + i + "\\"") < 0) continue;
      String id = String.valueOf(i);
      this.pending = @PKG@.ProfStore.live(p, id) ? id : null;
      this.delAsk = null;
      this.info = "";''')
rep('''      this.view = 1;
      this.pending = null;
      this.info = "";
      prepareCreate();''', '''      this.view = 1;
      this.pending = null;
      this.delAsk = null;
      this.info = "";
      prepareCreate();''')
rep('''  this.reminded = false;
  if (view == 1) prepareCreate();''', '''  this.reminded = false;
  this.delAsk = null;
  if (view == 1) prepareCreate();''')
# open(): an ended undo window is archived before the page shows (the list never offers Restore for a profile that is past it)
rep('''  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  boolean first = @PKG@.ProfStore.activeOf(p) == null;''', '''  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  @PKG@.ProfDel.expirePlayer(u, System.currentTimeMillis());
  java.util.Properties p = @PKG@.ProfStore.load(u);
  boolean first = @PKG@.ProfStore.activeOf(p) == null;''')

# ================================================================================================ join + login line
rep('''  @PKG@.ProfStore.noteLogin(u, pr.getUsername());
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.activeOf(p) == null && @PKG@.ProfStore.count(p) > 0) {''', '''  @PKG@.ProfStore.noteLogin(u, pr.getUsername());
  @PKG@.ProfDel.expirePlayer(u, System.currentTimeMillis());     // 0.1.5: an undo window that ended while the server was down
  @PKG@.ProfDel.repairNoLive(u);                                  // 0.1.5: only deleted profiles left (hand edit) -> the newest back
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.activeOf(p) == null && @PKG@.ProfStore.count(p) > 0) {''')
rep('''    if (@PKG@.ProfCfg.notifyOn(u, "profiles.loginStatus"))
      pr.sendMessage(@MSG@.raw("[Profiles] Playing profile " + p.getProperty("p." + act + ".name", act) + (cls.length() > 0 ? " (" + cls + ")" : "") + ". /profiles to switch or create one.").color("#9fd8a2"));''',
    '''    if (@PKG@.ProfCfg.notifyOn(u, "profiles.loginStatus"))
      pr.sendMessage(@MSG@.raw("[Profiles] Playing profile " + p.getProperty("p." + act + ".name", act) + (cls.length() > 0 ? " (" + cls + ")" : "") + ". /profiles to switch or create one.").color("#9fd8a2"));
    String dn = @PKG@.ProfDel.pendingNote(p);      // 0.1.5: a deleted profile that can still be restored (not a switchable message: the clock runs)
    if (dn != null) pr.sendMessage(@MSG@.raw("[Profiles] " + dn).color("#ffc800"));''')

# ================================================================================================ commands
CMD_JAVA = r'''# 0.1.5: /profiles delete <name|number> (the same command again within 10 s confirms) and /profiles restore <name|number>
F(pdel, "public @RA@ profArg;")
C(pdel, r"""
public ProfDeleteCmd() {
  super("delete", "Delete one of your profiles (it can be restored for a few hours): /profiles delete <name or number>, then again to confirm");
  this.profArg = withRequiredArg("profile", "profile name or number", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(pdel, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PKG@.ProfDel.tell(pr, @PKG@.ProfDel.cmdDelete(pr.getUuid(), pr.getUsername(), String.valueOf(ctx.get(this.profArg))));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("/profiles delete failed: " + t); pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profiles delete <name or number>")); }
}""")
F(pres, "public @RA@ profArg;")
C(pres, r"""
public ProfRestoreCmd() {
  super("restore", "Bring back a profile you deleted (within its undo window): /profiles restore <name or number>");
  this.profArg = withRequiredArg("profile", "profile name or number", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(pres, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PKG@.ProfDel.tell(pr, @PKG@.ProfDel.cmdRestore(pr.getUuid(), pr.getUsername(), String.valueOf(ctx.get(this.profArg))));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("/profiles restore failed: " + t); pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profiles restore <name or number>")); }
}""")
'''
rep('''C(pcmd, r"""
public ProfilesCmd() {
  super("profiles", "Your profiles (each = its own class, island and inventory): /profiles | create | switch <n> | list");
  addAliases(new String[] { "profile" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.ProfCreateCmd());
  addSubCommand(new @PKG@.ProfSwitchCmd());
  addSubCommand(new @PKG@.ProfListCmd());
}""")''', CMD_JAVA + '''C(pcmd, r"""
public ProfilesCmd() {
  super("profiles", "Your profiles (each = its own class, island and inventory): /profiles | create | switch <n> | list | delete <n> | restore <n>");
  addAliases(new String[] { "profile" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.ProfCreateCmd());
  addSubCommand(new @PKG@.ProfSwitchCmd());
  addSubCommand(new @PKG@.ProfListCmd());
  addSubCommand(new @PKG@.ProfDeleteCmd());
  addSubCommand(new @PKG@.ProfRestoreCmd());
}""")''')
rep('''      + (@PKG@.ProfStore.BROKEN.containsKey(t) ? " | FILE UNREADABLE" : "") + (@PKG@.ProfSwitch.readMarker(t) != null ? " | switch marker present (switching/" + t + ".properties)" : "")));''',
    '''      + (@PKG@.ProfStore.BROKEN.containsKey(t) ? " | FILE UNREADABLE" : "") + (@PKG@.ProfSwitch.readMarker(t) != null ? " | switch marker present (switching/" + t + ".properties)" : "")
      + (@PKG@.ProfStore.goneCount(p) > 0 ? " | " + @PKG@.ProfStore.goneCount(p) + " archived (/profileadmin archive list)" : "")));''')
ADM_JAVA = r'''# 0.1.5: /profileadmin archive list <player> | restore <player> <name|number|folder> (skyyprofiles.admin; groups cleared on purpose)
F(aarl, "public @RA@ playerArg;")
C(aarl, r"""
public AdmArchListCmd() {
  super("list", "(admin) A player's deleted and archived profiles: /profileadmin archive list <player|uuid>");
  requirePermission("skyyprofiles.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "player name (online, or seen before) or uuid", @ATY@.STRING);
}""")
M(aarl, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
    java.util.UUID t = @PKG@.ProfStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Profiles] Unknown player - use a name (online or seen before) or a uuid.")); return; }
    @PKG@.ProfDel.expirePlayer(t, System.currentTimeMillis());
    java.util.ArrayList ls = @PKG@.ProfDel.archiveText(t);
    for (int i = 0; i < ls.size(); i++) pr.sendMessage(@MSG@.raw((i == 0 ? "[Profiles] " : "") + (String) ls.get(i)));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profileadmin archive list <player|uuid>")); }
}""")
F(aarr, "public @RA@ playerArg;")
F(aarr, "public @RA@ profArg;")
C(aarr, r"""
public AdmArchResCmd() {
  super("restore", "(admin) Bring back a deleted or archived profile: /profileadmin archive restore <player|uuid> <name, number or folder>");
  requirePermission("skyyprofiles.admin");
  setPermissionGroups(new String[0]);
  this.playerArg = withRequiredArg("player", "player name (online, or seen before) or uuid", @ATY@.STRING);
  this.profArg = withRequiredArg("profile", "profile name, number or archive folder (/profileadmin archive list)", @ATY@.STRING);
}""")
M(aarr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
    java.util.UUID t = @PKG@.ProfStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Profiles] Unknown player - use a name (online or seen before) or a uuid.")); return; }
    String r = @PKG@.ProfDel.adminRestore(t, String.valueOf(ctx.get(this.profArg)), pr.getUsername());
    @PKG@.ProfDel.tell(pr, r);
    if (r != null && r.startsWith("+")) {
      @PR@ tp = @UNI@.get().getPlayer(t);
      if (tp != null && tp.isValid() && !t.equals(pr.getUuid())) tp.sendMessage(@MSG@.raw("[Profiles] An admin restored one of your deleted profiles - /profiles shows it.").color("#ffc800"));
    }
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profileadmin archive restore <player|uuid> <name, number or folder>")); }
}""")
C(aarc, r"""
public AdmArchiveCmd() {
  super("archive", "(admin) Deleted profiles: /profileadmin archive list <player> | restore <player> <name>");
  requirePermission("skyyprofiles.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.AdmArchListCmd());
  addSubCommand(new @PKG@.AdmArchResCmd());
}""")
M(aarc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin archive list <player> | restore <player> <name, number or folder> - deleted profiles stay restorable by the player for " + @PKG@.ProfCfg.windowText() + ", then they move to Skyy_SkyyProfiles/archive (never wiped)."));
}""")
'''
rep('''C(adm, r"""
public ProfileAdminCmd() {
  super("profileadmin", "(admin) /profileadmin info <player> | setclass <player> <n> <class> | config | set <setting> <value> | reload");
  requirePermission("skyyprofiles.admin");
  addSubCommand(new @PKG@.AdmInfoCmd());
  addSubCommand(new @PKG@.AdmSetClassCmd());
  addSubCommand(new @PKG@.AdmReloadCmd());
  addSubCommand(new @PKG@.AdmConfigCmd());
  addSubCommand(new @PKG@.AdmSetCmd());
}""")''', ADM_JAVA + '''C(adm, r"""
public ProfileAdminCmd() {
  super("profileadmin", "(admin) /profileadmin info <player> | setclass <player> <n> <class> | archive list|restore | config | set <setting> <value> | reload");
  requirePermission("skyyprofiles.admin");
  addSubCommand(new @PKG@.AdmInfoCmd());
  addSubCommand(new @PKG@.AdmSetClassCmd());
  addSubCommand(new @PKG@.AdmReloadCmd());
  addSubCommand(new @PKG@.AdmConfigCmd());
  addSubCommand(new @PKG@.AdmSetCmd());
  addSubCommand(new @PKG@.AdmArchiveCmd());
}""")''')
rep('''  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin info <player|uuid> | setclass <player|uuid> <profile> <class> | config | set <setting> <value|default> | reload"));''',
    '''  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin info <player|uuid> | setclass <player|uuid> <profile> <class> | archive list <player> | archive restore <player> <name> | config | set <setting> <value|default> | reload"));''')

# ================================================================================================ classes, plugin setup / shutdown
rep('''adm  = pool.makeClass(PKG + ".ProfileAdminCmd", pool.get(T["APC"]))
''', '''adm  = pool.makeClass(PKG + ".ProfileAdminCmd", pool.get(T["APC"]))
dlt  = pool.makeClass(PKG + ".ProfDel")                              # 0.1.5: delete / restore / archive
swp  = pool.makeClass(PKG + ".ProfSweep")                            # 0.1.5: the 60 s undo-window sweep
sfn  = pool.makeClass(PKG + ".StateFn")                              # 0.1.5: bridge profile:fn:state
pdel = pool.makeClass(PKG + ".ProfDeleteCmd", pool.get(T["APC"]))    # 0.1.5
pres = pool.makeClass(PKG + ".ProfRestoreCmd", pool.get(T["APC"]))   # 0.1.5
aarl = pool.makeClass(PKG + ".AdmArchListCmd", pool.get(T["APC"]))   # 0.1.5
aarr = pool.makeClass(PKG + ".AdmArchResCmd", pool.get(T["APC"]))    # 0.1.5
aarc = pool.makeClass(PKG + ".AdmArchiveCmd", pool.get(T["APC"]))    # 0.1.5
''')
rep('''C(pl, "public SkyyProfilesPlugin(@JPI@ init) { super(init); }")
''', '''C(pl, "public SkyyProfilesPlugin(@JPI@ init) { super(init); }")
F(pl, "public java.util.concurrent.ScheduledFuture sweeper;")      # 0.1.5
''')
rep('''  @PKG@.ProfStore.LOGF = base.resolve("switches.log");
''', '''  @PKG@.ProfStore.LOGF = base.resolve("switches.log");
  @PKG@.ProfDel.ARCDIR = base.resolve("archive");          // 0.1.5: archived profiles (admin only; created on the first archive)
''')
rep('''  @PKG@.ProfCfg.bridge().put("profile:fn:key", new @PKG@.KeyFn());
''', '''  int waiting = @PKG@.ProfDel.scanIndex();                 // 0.1.5: players with a deleted profile in its undo window (deadlines are in their files)
  @PKG@.ProfCfg.bridge().put("profile:fn:key", new @PKG@.KeyFn());
  @PKG@.ProfCfg.bridge().put("profile:fn:state", new @PKG@.StateFn());     // 0.1.5
''')
rep('''    + (markers > 0 ? "; " + markers + " interrupted switch(es) will be finished or rolled back when those players join" : ""));''',
    '''    + (markers > 0 ? "; " + markers + " interrupted switch(es) will be finished or rolled back when those players join" : "")
    + "; deleted profiles: undo window " + @PKG@.ProfCfg.windowText() + (waiting > 0 ? ", " + waiting + " player(s) with one waiting" : ""));
  try { this.sweeper = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.ProfSweep(), 5L, __SWEEP__L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.ProfCfg.warn("could not start the deleted-profile sweep (windows still end at join and when /profiles opens): " + t); }''')
rep('''}""".replace("__VER__", VERSION).replace("__KIT__", KIT_ID))''', '''}""".replace("__VER__", VERSION).replace("__KIT__", KIT_ID).replace("__SWEEP__", str(SWEEP_S)))''')
rep('''protected void shutdown() {
  try {
    int n = @PKG@.ClearLater.clearAllNow();''', '''protected void shutdown() {
  try { if (this.sweeper != null) this.sweeper.cancel(false); } catch (Throwable t) { }
  try {
    int n = @PKG@.ClearLater.clearAllNow();''')
rep('''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, sw, clr, page, opn, rec, pj, rtk, svt, rdy, pcon, quit_, pcre, psw, plst, pcmd, ainf, acls, arel,
       acfg, aset, adm, pl)''', '''ALL = (cfg, ros, pkit, nam, sto, pub, kfn, inv, sw, clr, dlt, swp, sfn, page, opn, rec, pj, rtk, svt, rdy, pcon, quit_, pcre, psw, plst, pdel,
       pres, pcmd, ainf, acls, arel, acfg, aset, aarl, aarr, aarc, adm, pl)''')
rep('''m = B.manifest("SkyyProfiles", VERSION, "SkyWynn profiles (SkyBlock style): each profile is its own save - class (Archer, Warrior, Mage, Berserker or Priest; picked at creation, locked, with its class kit from SkyyClasses), island, coins, skills, bags and vanilla inventory. /profiles. Zero dependencies; SkyyClasses and SkyyIslands are used when present.", PKG + ".SkyyProfilesPlugin")''',
    '''m = B.manifest("SkyyProfiles", VERSION, "SkyWynn profiles (SkyBlock style): each profile is its own save - class (Archer, Warrior, Mage, Berserker or Priest; picked at creation, locked, with its class kit from SkyyClasses), island, coins, skills, bags and vanilla inventory. /profiles. A deleted profile can be restored for 6 hours (admins keep an archive). Zero dependencies; SkyyClasses and SkyyIslands are used when present.", PKG + ".SkyyProfilesPlugin")''')

# ================================================================================================ checks on the result
assert card_sha() == CARD_SHA, "the shared SKYY CARD block changed - it must stay SkyyClasses 0.1.9's"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.4's changed: %s" % k[:80]
assert s.count("registerCommand(") == REG0, "command registrations changed (the new commands are sub-commands)"
BIND1 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
for ln in BIND0:
    assert ln.strip() in [x.strip() for x in BIND1], "a 0.1.4 event binding is gone: %s" % ln.strip()
NEW_BIND = sorted(set(x.strip() for x in BIND1) - set(x.strip() for x in BIND0))
assert len(NEW_BIND) == 5 and all(any(t in x for x in NEW_BIND) for t in ('"pfres" + id', '"pfdel" + id', '"pfdelyes"', '"pfdelno"', '"pfclose"')), NEW_BIND
CLAMP = "    if (uh < %dL) uh = %dL;" % (UMIN, UMIN) + LF + "    if (uh > %dL) uh = %dL;" % (UMAX, UMAX) + LF
assert s.count("UNDO_MIN_H, UNDO_MAX_H = %d, %d " % (UMIN, UMAX)) == 1 and CLAMP in s, "loader clamp = the row bounds"
# order: callers after callees (javassist compiles each method against what the pool already has)
assert s.index("public static boolean live(") < s.index("public static int count(") < s.index("public static String activeOf(")
assert s.index("public static long untilOf(") < s.index("public static String fmtLeft(") < s.index("public static String describe(")
assert s.index("public static Object[] recoverPlan(") < s.index("public static String checkState(") < s.index("public static String[] shownIds(")
assert s.index("public static void moveFile(") < s.index("public static boolean archiveLocked(") < s.index("public static int expirePlayer(") \
    < s.index("public static String restore(") < s.index("public static String adminRestore(") < s.index("public static String cmdDelete(")
# the review fixes: helpers before their callers
assert s.index("public static int count(") < s.index("public static long slotsMark(") < s.index("public static synchronized boolean markDeleted(")
assert s.index("public static String busyText()") < s.index("public static String check(") < s.index("public static String delete(")
assert s.index("public static void pub(") < s.index("public static String slotBlock(") < s.index("public static void warnArc(") \
    < s.index("public static void cleanDir(") < s.index("public static String delete(") < s.index("public static boolean archiveLocked(")
assert "ProfStore.publish" not in s[s.index("public static String delete("):s.index("public static String cmdDelete(")], \
    "ProfDel publishes through pub() (a thrown publish must not skip the page rebuild)"
assert s.count('"EXPIRED"') == 2 and s.count("{{EXPIRED}}") == 1
assert s.index("public static String[] shownIds(") < s.index("M(page, PF_LIST_JAVA)") < s.index("public boolean deleteEvent(") \
    < s.index("public void handleDataEvent(")
assert s.index("public static String windowText()") < s.index("public static String summary()")
assert s.index("public AdmArchListCmd()") < s.index("public AdmArchiveCmd()") < s.index("public ProfileAdminCmd()")
assert s.index("public ProfDeleteCmd()") < s.index("public ProfilesCmd()")
assert s.index("@PKG@.ProfDel.scanIndex();") > s.index("java.nio.file.Files.createDirectories(@PKG@.ProfStore.DIR")
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.4 had %d)" % (s.count(LF), OLD.count(LF)))
