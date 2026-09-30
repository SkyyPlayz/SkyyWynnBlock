"""Derive SkyyGuilds/build_skyyguilds_0.1.4.py from the LIVE 0.1.3 (build_skyyguilds_0.1.3.py = the tools/deploy_set.py SET pin).
Run:  python tools/guilds_0_1_4_patch.py   then   python SkyyGuilds/build_skyyguilds_0.1.4.py   (never --deploy: coordinated deploy)
SkyyGuilds is patch-based since 0.1.3 (tools/guilds_0_1_3_patch.py): edit THIS file, never the generated build script.

0.1.4 = the vanilla UI pass, batch B2 (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and feel
vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 7, 13; research/Skyy-UI-Inventory.md 5.12) PLUS ONE
isolated behaviour fix:
  A. LOOK ONLY - GuildPage (/guild: the not-in-a-guild view, the guild view, the bank log view) is rebuilt on the shared kit
     tools/skyyui.py (1.4): the generated script imports skyyui as SUI, calls SUI.verify() before anything else and puts SUI.kit_id()
     and the page id (GUILD_PAGE_ID, a hash of the kit-emitted page Java) into the ready log line. GuildPage.style() (the custom button
     triples) is gone; the result line colour comes from the kit's java_status_methods() as GuildPage.colorOf - only the colour method
     is compiled (review 2026-09-29: the kit's textOf was dead code in the page; infoLabel's text stays GuildStore.textOf, 0.1.3's, and
     GuildStore's own colorOf / textOf stay for the chat lines). buildNone / buildGuild / buildLog / infoLabel are generated at BUILD time from Java
     templates that keep every 0.1.3 statement that is not markup WORD FOR WORD (asserted below: multiset of whole lines, with the few
     changed lines listed in CHANGED), every event binding in its order, every EventData string, every b.set target and value, every
     0.1.3 element id; only the appends changed. Everything else (GuildStore, GCfg, GHooks, DayTask, GuildTick, commands, config kit
     rows, files, bridge keys, handleDataEvent, build, jsonStr, safe, two) is byte-identical to 0.1.3 - asserted (KEEP blocks).
     Disclosed text differences (kit rule: static inline text is [A-Za-z0-9 <>/-]; a TextButton's Text cannot be b.set until probe
     page 20 "button-text" is seen): the armed Kick button reads "Sure" (0.1.3 "Sure?") and the armed Make leader button "Confirm"
     (0.1.3 "Confirm?"); the label "Set a daily limit:" moved from inline text to a b.set line on the new label #SkyyGLimLbl.
     KNOWN, kept on purpose (review 2026-09-29): the result line under an armed button still says "Click Sure? ..." / "Click
     Confirm? ..." (handleDataEvent is 0.1.3's byte for byte); once probe page 20 passes, the next version puts the "?" back on the
     buttons (SUI.button(..., trial=True) there) so both texts match again. Also 0.1 behaviour, unchanged: an armed button is not
     redrawn when its 10 s run out (no periodic page updates), so a click after 10 s arms it again instead of acting.
     Review 2026-09-29 look fix: the Admin rank text is the kit's info blue #7caacc (was accentHover #96b8e0: contrast only
     1.26 : 1 against the Member value colour #b7cedd; info gives 1.52 : 1 and still 7.1 : 1 on the row colour #101925).
  B. FIX (not look-only, separately tested): changing the admin setting xpSkills while the server runs credited an ADDED skill's whole
     saved XP at the next check (XpTask kept ONE summed baseline per member, so the added skill's saved XP looked like a gain: up to
     xpMaxPerCheck 10,000,000 skill XP x 10 % = 1,000,000 guild XP per member), and a REMOVED skill swallowed the other skills' gains of
     that check (the sum dropped). XpTask now keeps a baseline PER SKILL (XpTask.stepSkills; a skill is keyed by its SkyySkills storage
     slot, GCfg.skillSlot, so Archery -> Archer keeps its baseline; an unknown name by its lower-case text): a skill added to xpSkills
     mid-run is baselined at the member's current XP on its first check (only XP earned after it was added counts), a removed skill
     stops counting and its baseline is dropped (re-adding it later baselines again: no retroactive credit), the skills that stayed
     keep counting their own gains. With an unchanged list the guild XP is exactly 0.1.3's (the per-skill deltas sum to the old
     total delta; fractions, xpMaxPerCheck, the profile / guild keyed baseline and the SkyySkills-older-than-0.4 level fallback are
     unchanged). SkyyGuilds/test_skyyguilds_0.1.4.py part C reproduces the 0.1.3 behaviour and proves the fix.
     XpTask.total() (the summed reading the 0.1.2 / 0.1.3 notes of the build docstring describe) is no longer called; it stays in the
     class unchanged so XpTask's diff is exactly check() + 3 new methods (review 2026-09-29: drop it in a later cleanup).
  Review 2 (2026-09-29, second review of 0.1.4; look only - no binding, EventData, text, id or behaviour change):
    - finding 5 (tight boxes): the column widths are re-split so the widest texts fit, asserted at BUILD time by guild_fits()
      (SUI.text_width with the label kind's own size / bold / uppercase) and re-measured by the harness on texts the real Java makes
      (states "widest texts" / "widest log"): member table Member 260 -> 326 px (a 16-letter name of W - the widest letter - on any
      row, or 16 x m + "  (you)" on your own row), Rank 110 -> 86, Guild XP added 160 -> 150, Taken today 140 -> 142 (1e15 coins =
      the highest maxBank), Status the rest 106 -> 72 (the sum and the Leader / Admin actions head position are unchanged); bank log
      table When 160 -> 130, Player 240 -> 330 (16 x W), What 500 -> 440, Bank after unchanged; summary row: the XP caption 575 -> 585
      px (xpSharePercent 1000 + a 13-digit guild XP), the bank / online line 575 -> 565 (maxBank 1e15 + maxMembers 500). Still
      clipped, on purpose: your own row when your name is 16 capital Ws ("(you)" adds 54 px), numbers past the config maxima.
    - finding 6: the dead variable parts_h in guild_view_none() is gone.
    - finding 3: the build prints "guild page <id> = the page ... last passed on" when it made the checked page (the SkyyBank 0.1.4 /
      SkyyCollections 0.2.4 pattern), else the WARNING - every build log shows one of the two; the kit version assert names the kit
      files that must be committed together with this mod's files (a checkout without kit 1.4 stops there instead of building).
"""
import collections
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyGuilds", "build_skyyguilds_0.1.3.py")
dst = os.path.join(ROOT, "SkyyGuilds", "build_skyyguilds_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.3"' in s and "GENERATED by tools/guilds_0_1_3_patch.py" in s, "build_skyyguilds_0.1.3.py is not the live 0.1.3"
assert "@@" not in s, "0.1.3 already holds a @@ token"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 27, "0.1.3 has 27 event binding lines (all in GuildPage), found %d" % len(BIND0)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


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


TOKEN_RE = re.compile(r"@@[A-Z0-9]+@@")


def fill(template, values):
    """@@NAME@@ replacement (research/Vanilla-UI-Style-Guide.md 8c): every token occurs exactly once, no value holds "@@", none left."""
    for name, value in values.items():
        tok = "@@%s@@" % name
        assert template.count(tok) == 1, "token %s occurs %d times" % (tok, template.count(tok))
        assert "@@" not in value, "the value for %s holds '@@'" % tok
        template = template.replace(tok, value)
    left = TOKEN_RE.findall(template)
    assert not left, "tokens left unfilled: %s" % left
    return template


# blocks that must come out of this patch byte-identical (everything but the docstring head, VERSION, the kit import, the data
# colours, GuildPage's look, XpTask.check (fix B) and the ready log line)
KEEP = [block("\nHERE = os.path.dirname(os.path.abspath(__file__))", "# ================= XpTask (the member's own world thread)"),
        block("# total XP over GCfg.SKILLS through skill:fn:xp; -1 = SkyySkills has no skill:fn:xp",
              "# one check for one player (also used by the bare-JVM test with a null PlayerRef): returns the guild XP added"),
        block('M(xpt, r"""\npublic void run() {', "# ================= GuildPage (inline, rebuilt only after a click) ================="),
        block("# 0.1.1: view 0 = the guild page, 1 = the full bank log (Expand)", 'M(page, r"""\npublic static String style('),
        block('# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr', 'M(page, r"""\npublic void infoLabel('),
        block('M(page, r"""\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {', 'getLogger().at(java.util.logging.Level.INFO).log("[SkyyGuilds] @VERSION@ ready'),
        block('M(pl, r"""\nprotected void shutdown() {', "B.assemble(jar, man, OUT)")]

# ================================================================================================ docstring
HEAD_OLD = '''"""SkyyGuilds 0.1.3 - build script (javassist via jpype). GENERATED by tools/guilds_0_1_3_patch.py from the LIVE 0.1.2
(build_skyyguilds_0.1.2.py, the tools/deploy_set.py SET pin) - edit the patch, never this file (0.1.2 and 0.1.1 were copy + edit).
Run:   python build_skyyguilds_0.1.3.py          -> SkyyGuilds/SkyyGuilds-0.1.3.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
'''
HEAD_NEW = '''"""SkyyGuilds 0.1.4 - build script (javassist via jpype). GENERATED by tools/guilds_0_1_4_patch.py from the LIVE 0.1.3
(build_skyyguilds_0.1.3.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyguilds_0.1.4.py          -> SkyyGuilds/SkyyGuilds-0.1.4.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)

0.1.4 (2026-09-29, the vanilla UI pass batch B2 - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to
look and feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md) + ONE isolated fix (B):
  A. ONLY THE LOOK OF THE /guild PAGE CHANGED, on the shared kit tools/skyyui.py (1.4). Commands, aliases, permissions, config keys and
     rows, files, bridge keys, the Settings switches, every element id of 0.1.3, the 27 event binding lines (copied out of 0.1.3 by the
     patch, not retyped; same order, same EventData), every b.set target and value, the page state (pageNo, logPage, view, keep*,
     confirm / confirmUntil, rowIds - "the click acts on what the player saw") and handleDataEvent are 0.1.3's; the patch asserts it.
     - The build calls SUI.verify() first: every vanilla style value, texture and sound the page uses is proven against Assets.zip
       (read-only) at every build; KIT_ID (kit version + file hash) and the page id GUILD_PAGE_ID are in the ready log line.
       guild_page() runs the kit when this script runs, so a kit fix reaches the page on its next build (GUILD_PAGE_CHECKED warns).
     - Window: the vanilla decorated container (ContainerHeader title bar with runes + the two gold ornaments, the ContainerPatch
       body, padding 17), 1200 wide in all three views (0.1.3: 1120); 0.1.3's root #SkyyGuild is the body now, the new root is
       #SkyyGuildF (Anchor Width / Height only). The window title is the guild name [TAG] (guild view: 0.1.3's #SkyyGTitle is the
       title label), "name [TAG] - guild bank log" (log view: #SkyyGLogTitle) and GUILDS (not in a guild). Gone: the dark-blue root,
       the gold accent stripe, the big custom titles, the empty Label spacers, the solid-colour button triples.
     - Guild view (1200 x 967): a vanilla summary well (#SkyyGSum: level / season / rank line, the XP text over a flat vanilla
       progress bar - track #1a2030, fill #aa7c4a, the fill only when > 0 px - and "members add N %" | "Guild bank ... Online ..."),
       the member table = section-style column heads + 7 fixed-width WorldEventListRow rows on the vanilla list well (#SkyyGList;
       your own row in the pressed-row step, a green status bar = online, rank colours gold / info blue / value, online / offline in the
       vanilla success green / disabled grey), row actions as small vanilla buttons (Promote / Demote Secondary, Kick Destructive -
       armed "Sure", Make leader Secondary - armed "Confirm" Destructive), the kit pager (small Secondary "< Prev" / "Next >", the
       vanilla Disabled look at the ends; handleDataEvent still clamps), the invite box + Invite (Primary) and the amount box +
       Deposit (Primary) / Withdraw (Secondary) on vanilla text fields, the hint (caption grey), the limits line (wraps to two lines),
       the Leader's limit row (Set Admin limit / Set Member limit Secondary), the bank log head (section label, Expand log small
       Secondary) and the newest 3 log lines in a well, the result line (vanilla success / error / info-blue by the + / - / = mark,
       two lines), a content separator and the footer: Refresh (Secondary) on the left, Leave guild / Disband guild (Destructive;
       armed "Click again to leave" / "Click again to DISBAND") on the right.
       Member columns (review 2): Member 326, Rank 86, Guild XP added 150, Taken today 142, Status 72 px - a 16-letter name of W on
       any row and 16 x m + "  (you)" on your own row fit; the XP caption 585 px (xpSharePercent 1000, a 13-digit guild XP) and the
       bank / online line 565 px (maxBank 1e15, maxMembers 500) fit. guild_fits() asserts these widest texts at every build.
     - Log view: the 15-row bank log table on the list well (#SkyyGLList; When 130 / Player 330 / What 440 / Bank after 242 px heads;
       deposits success green, withdrawals gold, limit changes info blue, payouts warning yellow), the kit pager ("< Newer" /
       "Older >"), the note, the result line, Refresh on the left and "< Back to guild" (Secondary + the vanilla cancel sound) on the
       right.
     - Not in a guild (1200 x 604): the message, a pending invite as the kit's one-row in-page confirm (#SkyyGInvRow: the question in
       the vanilla confirm yellow, Accept = Primary + save sound, Decline = Secondary + cancel sound), CREATE A GUILD (subtitle) +
       the centred name box + Create guild (Primary), the rule caption, COMMANDS (subtitle) + the 5 command lines in a well, the
       result line, Refresh.
     - Every body is filled exactly (the heights are read back out of the markup, SUI.used_height; a view that shows less - no
       pager, no Leader row, no invite - fills the same space with an empty Group), the page roots are <= 980 px high, and only
       properties the deployed pages already use (SUI.assert_proven: no FlexWeight, WrapMaxLines, LetterSpacing, LayoutMode
       Center / Right / Full, nothing UNVERIFIED / trial).
     - Disclosed text differences (kit rule: static inline text is [A-Za-z0-9 <>/-]; a TextButton's Text is not b.set until probe
       page 20 "button-text" is seen): the armed Kick button says "Sure" (0.1.3 "Sure?"), the armed Make leader button "Confirm"
       (0.1.3 "Confirm?"); "Set a daily limit:" is now b.set on the new label #SkyyGLimLbl (0.1.3: inline text).
     - Known and kept (review 2026-09-29): the result line under an armed button still says "Click Sure? within 10 s ..." / "Click
       Confirm? within 10 s ..." (handleDataEvent is 0.1.3's byte for byte) - the "?" goes back on the buttons once probe page 20
       passes. 0.1 behaviour, unchanged: an armed button is not redrawn when its 10 s run out (no periodic page updates), so a click
       after 10 s arms it again instead of acting.
     - GuildPage gains only the kit's colorOf (the result line colour); its text stays GuildStore.textOf (0.1.3).
  B. FIX - xpSkills changed while the server runs (HANDOFF log 2026-09-25 08:24, open since 0.1.2): XpTask kept ONE summed baseline per
     member, so a skill ADDED to xpSkills mid-run counted its whole saved XP as a gain at the next check (up to xpMaxPerCheck
     10,000,000 skill XP x 10 % = 1,000,000 guild XP per member), and a REMOVED skill made the sum drop and swallowed the other skills'
     gains of that check. XpTask.check now keeps a baseline PER SKILL (XpTask.totals / skillKey / stepSkills): a skill is keyed by its
     SkyySkills storage slot (GCfg.skillSlot: Archery and Archer share one) or, for a name SkyySkills does not list, its lower-case
     text. A newly added skill is baselined at the member's current XP (only XP earned after it was added counts); a removed skill
     stops counting and its baseline is dropped (added again later = a fresh baseline, no retroactive credit); the other skills keep
     counting their own gains across the change. With an unchanged list the result is exactly 0.1.3's (the per-skill deltas sum to
     0.1.3's total delta), and fractions, xpMaxPerCheck, the profile + guild keyed baseline and the level fallback (SkyySkills
     older than 0.4) are unchanged. XpTask.total() - the summed reading the 0.1.2 / 0.1.3 notes below describe - is no longer
     called; it stays unchanged in the class so XpTask differs from 0.1.3 only by check() and the 3 new methods (drop it later).
@@CHECKED@@
  UNVERIFIED (needs the game): the whole new look - the kit's "base" look (probe pages base1 / base2 / base3) and the kit 1.4 blocks
    (probe page 19 "base4") have not been seen in game yet; this page has no runtime fallback (a parse error disconnects on /guild and
    on the SkyyMenu Guild tile), so it goes into a test deploy only after Skyy has opened base1-3 AND base4 cleanly - keep the SET pin
    at 0.1.3 until then. Fix B needs a real SkyySkills: change Server Setup > Guilds > Skills that count while two members are online.
  BEFORE ANY DEPLOY (review 2, finding 3): this script runs the kit when it runs, so a later kit edit changes the page and the build
    still ends 'assembled' (it prints "guild page <id> = the page ... last passed on" or a WARNING "... is NOT the page ..."; tools/
    deploy_set.py --check does not compare page ids). Commit tools/skyyui.py 1.4 + tools/skyyui_test.py + research/Vanilla-UI-Style-
    Guide.md together with the SkyyGuilds files, and re-run SkyyGuilds/test_skyyguilds_0.1.4.py right before a deploy (its part G
    fails on a page-id mismatch) - the in-game ready line must name the page id in CHECKED above.
'''
CHECKED = '''  CHECKED with SkyyGuilds/test_skyyguilds_0.1.4.py (committed; re-run it: python SkyyGuilds/test_skyyguilds_0.1.4.py - the
    harness is the source of truth, not this text) - 2026-09-29 (after the review 2 fixes), kit skyyui 1.4 ac93356c4c60, page
    8ae0b80a1870: 66731 ok, 0 fail. The in-game ready line reads "0.1.4 ready (skyyui 1.4 ac93356c4c60, page 8ae0b80a1870)".
    One JVM (-Xverify:all, HytaleServer.jar, 0.1.3 and 0.1.4 each in its own class loader): A all 48 classes of both jars load,
    verify and initialise. B 42 classes byte-identical to 0.1.3; GCfg / CfgFn / CfgRows / manifest.json = 0.1.3 once "0.1.4" is
    written back; SkyyGuildsPlugin = 0.1.3 once the ready constant is swapped back; GuildPage: only infoLabel / buildNone /
    buildGuild / buildLog changed, style gone, colorOf new (the kit's textOf is not compiled), <init> / safe / jsonStr / two / build
    / handleDataEvent instruction-identical; XpTask: only check changed, totals / skillKey / stepSkills new. C fix B, 8 scenarios on
    both jars through XpTask.check + GCfg.reloadSkills: an added skill 0.1.3 +500,000 (+1,000,000 at the xpMaxPerCheck cap), 0.1.4
    +0; removed + re-added 0.1.3 [0, 0, 1, 270, 10], 0.1.4 [0, 100, 1, 0, 10]; an unknown future name 0.1.3 +700, 0.1.4 +0; alias
    rename, a 60-step random walk (two members, fractions, decreases), a profile switch and the level fallback identical. D 31 page
    states x 2 jars (20 + 8 pager boundaries: an Admin on both member pages, a Leader with exactly 7 members = no pager, page 2 of 8
    members, a Member on page 2, 15 log moves = no pager, 16 moves on page 2, a Member viewing the log; + 3 widest-text states,
    review 2: 16-letter names of W / m, 500 members online, xpSharePercent 1000, a 13-digit guild XP, 1e15 coins - guild view, log
    view, invite): 329 bindings, 1024 b.set lines (+ the disclosed #SkyyGLimLbl) and 1441 visible texts (2 disclosed armed labels)
    identical, 1720 0.1.3 ids kept; 1266 0.1.4 markups through check_markup, check_page, set-after-append, assert_proven, kit
    colours only (2722), roots 1200 x 967 / 604 and every body filled exactly, 64 member rows measured, the pager shown / hidden
    with its page text and row count at each boundary, the rank texts gold / info blue / value (one colour per rank, three
    different). E 132 clicks through handleDataEvent in 2 sessions: identical results, keep boxes, views, purses, guilds, invites
    and rebuilt pages after every click. F 694 button labels / texts / column heads fit (text_width, the client's font tables;
    fullest: taken today 1e15, 16 x W, the bank line at 1e15 + 500 members 99 %, the log player and the XP line at 1000 % 98 %),
    and the 8 widest texts guild_fits() asserts were shown by the real Java. G the page id in the ready line = the kit's page now
    = GUILD_PAGE_CHECKED.'''
rep(HEAD_OLD, fill(HEAD_NEW, {"CHECKED": CHECKED}))

# the GUILD XP paragraph of the old docstring describes the summed baseline: say what 0.1.4 does
rep('''  x xpSharePercent (10) / 100 goes to the guild (fractions carry over), capped at xpMaxPerCheck skill XP per check. The baseline is
  keyed by profile key + guild id, so a profile switch or joining a guild is a new baseline (no credit for XP earned elsewhere); the
  first check after a join / restart only records the baseline (up to one check of XP is not counted after a server restart).''',
    '''  x xpSharePercent (10) / 100 goes to the guild (fractions carry over), capped at xpMaxPerCheck skill XP per check. The baseline is
  keyed by profile key + guild id, so a profile switch or joining a guild is a new baseline (no credit for XP earned elsewhere); the
  first check after a join / restart only records the baseline (up to one check of XP is not counted after a server restart).
  0.1.4: the baseline is kept PER SKILL (one value per SkyySkills slot of the list), so an xpSkills change while the server runs
  never credits an added skill's saved XP: an added skill starts at the member's current XP, a removed one stops counting.''')

# ================================================================================================ version, kit import, data colours
rep('\nVERSION = "0.1.3"\n', '''
VERSION = "0.1.4"
# 0.1.4: DATA colours for the vanilla UI kit's lint (research/Vanilla-UI-Style-Guide.md section 5): the [Guild] chat line colours
# (Message.color in GuildStore - chat, not page chrome; unchanged since 0.1)
UI_DATA_COLORS = ["#ffd070", "#cfe3ff", "#8fe39a", "#ffe08a", "#ff9d6b", "#9fb8d0", "#7fe0a0"]
''')
rep('assert tuple(int(x) for x in getattr(CFG, "KIT_VERSION", "1.0").split(".")) >= (1, 1), "SkyyGuilds 0.1.3 needs config kit 1.1+"\n',
    'assert tuple(int(x) for x in getattr(CFG, "KIT_VERSION", "1.0").split(".")) >= (1, 1), "SkyyGuilds 0.1.3 needs config kit 1.1+"\n'
    'import skyyui as SUI       # 0.1.4: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"\n'
    'SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift\n'
    'KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line\n'
    'assert tuple(int(x) for x in SUI.KIT_VERSION.split(".")) >= (1, 4), ("SkyyGuilds 0.1.4 needs the vanilla UI kit 1.4+ (static blocks, "\n'
    '    "used_height, text_width): tools/skyyui.py 1.4, tools/skyyui_test.py and research/Vanilla-UI-Style-Guide.md are committed together "\n'
    '    "with this script - this checkout has kit %s" % SUI.KIT_VERSION)\n')

# ================================================================================================ B. XpTask.check: per-skill baselines
OLD_CHECK = '''# one check for one player (also used by the bare-JVM test with a null PlayerRef): returns the guild XP added
M(xpt, r"""
public static long check(java.util.UUID u) {
  String gid = @PKG@.GuildStore.gidOf(u.toString());
  if (gid == null) return 0L;
  long t = total(u);
  String mode = "x";
  if (t < 0L) { t = levels(u); mode = "l"; }
  if (t < 0L) return 0L;
  String key = @PKG@.GuildStore.pkey(u) + "|" + gid + "|" + mode;
  long d = step(key, t);
  if (d <= 0L) return 0L;
  if (d > @PKG@.GCfg.MAX_DELTA) d = @PKG@.GCfg.MAX_DELTA;
  long gain = mode.equals("x") ? share(key, d, (double) @PKG@.GCfg.SHARE) : d * @PKG@.GCfg.LEVEL_FALLBACK;
  if (gain <= 0L) return 0L;
  return @PKG@.GuildStore.addXp(gid, u.toString(), gain);
}""")
'''
NEW_CHECK = '''# 0.1.4 (fix B, xpSkills changed while the server runs): the XP of EACH skill of the list the check was called with (the same reading
# as total(): skill:fn:xp per name, only positive values count); null = SkyySkills has no skill:fn:xp
M(xpt, r"""
public static long[] totals(java.util.UUID u, String[] sk) {
  Object f = @PKG@.GuildStore.bridge().get("skill:fn:xp");
  if (!(f instanceof java.util.function.Function)) return null;
  long[] out = new long[sk.length];
  for (int i = 0; i < sk.length; i++) {
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, sk[i] });
    long v = 0L;
    if (r instanceof Number) v = ((Number) r).longValue();
    out[i] = v > 0L ? v : 0L;
  }
  return out;
}""")
# 0.1.4: a skill's baseline key - its SkyySkills storage slot (GCfg.skillSlot, the SKILL_NAMES table: Archery and Archer share one), or
# its lower-case name when SkyySkills does not list it
M(xpt, r"""
public static String skillKey(String name) {
  String lx = name == null ? "" : name.trim().toLowerCase();
  int s = @PKG@.GCfg.skillSlot(lx);
  return s >= 0 ? "s" + s : "n:" + lx;
}""")
# 0.1.4: the delta since the last check PER SKILL (BASE key -> HashMap skill key -> Long XP). A skill with no baseline yet (added to
# xpSkills since the last check) is only baselined (0 counted), a skill no longer listed is dropped (it stops counting; listed again
# later = a fresh baseline). -1 = first sight of this key (baseline only, as step()). With an unchanged list the sum equals step()'s
# total delta exactly (the same values, summed per skill).
M(xpt, r"""
public static synchronized long stepSkills(String key, String[] sk, long[] v) {
  Object o = BASE.get(key);
  java.util.HashMap last = o instanceof java.util.HashMap ? (java.util.HashMap) o : null;
  java.util.HashMap now = new java.util.HashMap();
  long d = 0L;
  for (int i = 0; i < sk.length; i++) {
    String id = skillKey(sk[i]);
    now.put(id, Long.valueOf(v[i]));
    if (last == null) continue;
    Object p = last.get(id);
    if (p instanceof Long) d = d + (v[i] - ((Long) p).longValue());
  }
  BASE.put(key, now);
  return last == null ? -1L : d;
}""")
# one check for one player (also used by the bare-JVM test with a null PlayerRef): returns the guild XP added. 0.1.4: one snapshot of
# GCfg.SKILLS per check, per-skill baselines (stepSkills); the level fallback (no skill:fn:xp) keeps 0.1.3's summed step()
M(xpt, r"""
public static long check(java.util.UUID u) {
  String gid = @PKG@.GuildStore.gidOf(u.toString());
  if (gid == null) return 0L;
  String[] sk = @PKG@.GCfg.SKILLS;
  long[] v = totals(u, sk);
  long t = 0L;
  String mode = "x";
  if (v == null) { t = levels(u); mode = "l"; }
  if (t < 0L) return 0L;
  String key = @PKG@.GuildStore.pkey(u) + "|" + gid + "|" + mode;
  long d = v != null ? stepSkills(key, sk, v) : step(key, t);
  if (d <= 0L) return 0L;
  if (d > @PKG@.GCfg.MAX_DELTA) d = @PKG@.GCfg.MAX_DELTA;
  long gain = mode.equals("x") ? share(key, d, (double) @PKG@.GCfg.SHARE) : d * @PKG@.GCfg.LEVEL_FALLBACK;
  if (gain <= 0L) return 0L;
  return @PKG@.GuildStore.addXp(gid, u.toString(), gain);
}""")
'''
rep(OLD_CHECK, NEW_CHECK)

# ================================================================================================ A. GuildPage: the look only
rep("# ================= GuildPage (inline, rebuilt only after a click) =================",
    "# ================= GuildPage (0.1.3 logic; 0.1.4 look = the vanilla UI kit tools/skyyui.py; inline, rebuilt only after a click) =================")
# the custom button style helper goes (the kit's button styles replace it)
cut('M(page, r"""\npublic static String style(String bg, String hov, String press, String fg, int fs) {',
    "# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr")
# infoLabel .. buildLog: replaced by the page block (the Java is generated at build time from the templates below)
OLD_LOOK = cut('M(page, r"""\npublic void infoLabel(', 'M(page, r"""\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {',
               "@@PAGE@@")


def old_method(name):
    """the Java body lines of one 0.1.3 GuildPage method (from its signature line to the closing brace)"""
    m = re.search(r'M\(page, r"""\n(public void %s\(.*?\n\})"""\)' % name, OLD_LOOK, re.S)
    assert m, "0.1.3 method %s not found" % name
    return m.group(1).split(LF)


OLDM = dict((n, old_method(n)) for n in ("infoLabel", "buildNone", "buildGuild", "buildLog"))
# every 0.1.3 element id per view (kept; the page builder asserts each one is still created, the harness checks it at run time)
IDS = {}
for _n in ("buildNone", "buildGuild", "buildLog"):
    IDS[_n] = sorted(set(re.findall(r"#(SkyyG[A-Za-z0-9]*)", LF.join(OLDM[_n] + OLDM["infoLabel"]))))
assert len(IDS["buildNone"]) == 15 and len(IDS["buildGuild"]) == 49 and len(IDS["buildLog"]) == 20, dict((k, len(v)) for k, v in IDS.items())
# the page's 27 bindings are the file's 27
assert [ln for n in ("buildNone", "buildGuild", "buildLog") for ln in OLDM[n] if "ev.addEventBinding(" in ln] == BIND0
# GuildStore.helpLines() has 5 lines: the command well is sized for them (asserted, so a longer list needs a new page budget)
_hl = re.search(r'public static String\[\] helpLines\(\) \{\n  return new String\[\] \{\n(.*?)\n  \};', s, re.S)
assert _hl and _hl.group(1).count('\n') + 1 == 5, "helpLines() is not 5 lines"

PAGE_BLOCK = r'''# ================= 0.1.4: GuildPage's look = the vanilla UI kit (tools/skyyui.py, research/Vanilla-UI-Style-Guide.md) =================
# guild_page() builds every view's markup with kit calls when this script runs (every value proven by SUI.verify() above) and fills
# the Java templates GUILD_*_TPL: 0.1.3's statements (state, texts, b.set lines, the 27 event bindings) are kept word for word
# (tools/guilds_0_1_4_patch.py asserts it); only the appends are new. {{NAME}} = a place for kit-emitted Java.
GUILD_W = 1200                                   # every view (0.1.3: 1120); the frame adds 38 px of title bar + 2 x 17 px padding
GUILD_PREFIX = "SkyyG"                           # every element id starts with it (the 0.1.3 ids already did)
GUILD_IN = GUILD_W - 2 * SUI.CONTENT_PAD         # 1166: the body's inner width
GUILD_TWO = 46                                   # two wrapped 16 px lines (2 x 16 x 1.364 = 43.7 px) + 2 spare (SkyyBank 0.1.4)
GUILD_INFO_TOP, GUILD_SEP = 6, SUI.SEP_MARGIN    # the result line's top margin; the content separator's 8 above / below
GUILD_BTN = SUI.BTN_MIN_W                        # 172: a normal vanilla button (@DefaultButtonMinWidth)
# ---- guild view
GUILD_ROWS, GUILD_ROW_H, GUILD_ROW_GAP = 7, 40, SUI.ROW_GAP   # buildGuild's per = 7; WorldEventListRow is 42 + 3 (40 keeps <= 980)
GUILD_ROW_W = GUILD_IN - 2 * SUI.WELL_LIST_PAD   # 1158: a row inside the list well
GUILD_PRO_W, GUILD_KICK_W, GUILD_LEAD_W, GUILD_ACT_GAP = 110, SUI.ROW_ACTION_W, 140, 4      # small row actions, Left 4 (#ActionA)
GUILD_ACT_W = {2: 3 * GUILD_ACT_GAP + GUILD_PRO_W + GUILD_KICK_W + GUILD_LEAD_W, 1: GUILD_ACT_GAP + GUILD_KICK_W, 0: 0}
GUILD_PW = dict((k, GUILD_ROW_W - v) for k, v in GUILD_ACT_W.items())   # the row panel width by the viewer's rank
GUILD_ROW_PAD, GUILD_BAR = 8, 12                 # row panel padding left / right 8; the status bar 4 + its 8 px gap
# review 2 (finding 5): the columns are split so the widest texts fit (guild_fits asserts each one at build time): Member = a 16-letter
# name of W (the widest letter) or 16 x m + "  (you)" on your own row, Taken today = 1e15 coins (the highest maxBank); Status the rest
GUILD_COLS = [("Member", 326), ("Rank", 86), ("Guild XP added", 150), ("Taken today", 142)]
GUILD_COLS = GUILD_COLS + [("Status", GUILD_PW[2] - 2 * GUILD_ROW_PAD - GUILD_BAR - sum(w for _t, w in GUILD_COLS))]
GUILD_ACT_HEAD_W = 350                           # the "Leader actions" / "Admin actions" head, right-aligned over the buttons
GUILD_SUM_IN = GUILD_IN - 2 * SUI.WELL_PAD       # 1150: inside the summary well
GUILD_XPTXT_W = 585                              # "Members add N% ..." (left) | the bank / online line (right, GUILD_SUM_IN - this)
# the widest runtime texts of the fixed-width boxes (review 2, finding 5; the Java formats of buildGuild / buildLog / GuildStore, at
# the config maxima: xpSharePercent 1000, maxBank 1e15, maxMembers 500; a 13-digit guild XP; Hytale names up to 16 letters)
GUILD_NAME_WIDE = "W" * 16                       # the widest 16-letter name (every row but your own, the log's Player)
GUILD_NAME_YOU = "m" * 16 + "  (you)"            # your own row: 16 x the widest letter after W + buildGuild's own suffix
GUILD_XPTXT_WIDE = "Members add 1000% of the skill XP they earn to the guild. Total guild XP: 9999.99b"
GUILD_STATS_WIDE = "Guild bank: 1,000,000,000,000,000 coins          Online: 500 / 500 members"
GUILD_TAKEN_WIDE = "1000000.00b coins"               # GuildStore.fmt(1e15) + " coins"
GUILD_WHAT_WIDE = "set the Member daily limit: 1,000,000,000,000,000 coins"
GUILD_BANK_WIDE = "1,000,000,000,000,000 coins"
GUILD_SUB_H, GUILD_BARTXT_H, GUILD_BAR_H, GUILD_BAR_GAP, GUILD_SUMROW_H = 26, 22, 10, 6, 28
GUILD_HEAD_H = 28
GUILD_INV_W, GUILD_INVBTN_W, GUILD_AMT_W = 280, 150, 240
GUILD_LIM_LBL_W, GUILD_LIM_BOX_W, GUILD_LIMA_W, GUILD_LIMM_W = 150, 200, 200, 215
GUILD_LOGHDR_W, GUILD_LOGCNT_W, GUILD_EXPAND_W = 170, 300, 130
GUILD_LOG_LINE_H, GUILD_LOG_PAD = 22, 6
GUILD_LEAVE_W, GUILD_DISBAND_W = 250, 280        # "CLICK AGAIN TO LEAVE" 200 px / "CLICK AGAIN TO DISBAND" 224 px of 17 px label + 2 x 24
# ---- log view
GUILD_LROWS, GUILD_LROW_H = 15, 37               # buildLog's per = 15
GUILD_LCOLS = [("When", 130), ("Player", 330), ("What", 440)]      # review 2: Player = GUILD_NAME_WIDE, What = GUILD_WHAT_WIDE
GUILD_LCOLS = GUILD_LCOLS + [("Bank after", GUILD_ROW_W - 2 * GUILD_ROW_PAD - sum(w for _t, w in GUILD_LCOLS))]
GUILD_BACK_W = 200                               # "< BACK TO GUILD" 150 px of label + 2 x 24
# ---- not in a guild
GUILD_NAME_W, GUILD_CREATE_W = 460, 200
GUILD_HELP_LINES, GUILD_HELP_H = 5, 24           # GuildStore.helpLines() (5 lines, asserted by the patch)
# the Admin rank text (Leader gold, Member value #b7cedd): the kit's info blue #7caacc - review 2026-09-29: accentHover #96b8e0 was
# too close to value to tell the ranks apart by colour at a glance (guild_row_markup asserts the three are distinct)
GUILD_RANK_ADMIN = "info"
# the colours of a log line's "what" (0.1.3: its own green / orange / blue / gold): kit colour names
GUILD_LOG_COLS = {"deposited": "success", "withdrew": "gold", "set the": "info", "other": "warning"}
# every element id 0.1.3 had, per view - all kept (guild_page() asserts each one is still created)
GUILD_IDS_013 = @@IDS@@
# the page id (GUILD_PAGE_ID below) that SkyyGuilds/test_skyyguilds_0.1.4.py last passed on (tools/guilds_0_1_4_patch.py
# PAGE_CHECKED); a build whose kit output makes a different page warns, and the harness fails, until that page is checked
GUILD_PAGE_CHECKED = "@@PAGECHECKED@@"

GUILD_INFO_TPL = r"""
public void infoLabel(@UCB@ b) {
{{INFO}}
  b.set("#SkyyGInfo.Text", @PKG@.GuildStore.textOf(this.info));
}"""

GUILD_NONE_TPL = r"""
public void buildNone(@UCB@ b, @UEB@ ev, java.util.UUID u) {
{{SHELL}}
{{NONETXT}}
  b.set("#SkyyGNoneTxt.Text", "You are not in a guild yet. A guild shares a bank, levels up from its members' skill XP and has its own chat.");
  int fillH = {{INVH}};
  Object[] inv = @PKG@.GuildStore.inviteFor(u);
  if (inv != null) {
    long secs = ((Long) inv[5]).longValue() / 1000L;
    String tg = ((String) inv[1]).length() > 0 ? " [" + inv[1] + "]" : "";
{{INVROW}}
    b.set("#SkyyGInvTxt.Text", "Invite to " + inv[0] + tg + " (level " + inv[2] + ", " + inv[3] + " members) from " + inv[4] + " - " + (secs / 60L) + ":" + two(secs % 60L) + " left");
    ev.addEventBinding(@BT@.Activating, "#SkyyGAccept", @EVD@.of("a", "accept"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGDecline", @EVD@.of("a", "decline"));
    fillH = 0;
  }
{{CREATE}}
  if (this.keepName != null && this.keepName.length() > 0) b.set("#SkyyGName.Value", this.keepName);
  ev.addEventBinding(@BT@.Validating, "#SkyyGName", @EVD@.of("a", "create").append("@GName", "#SkyyGName.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyGCreate", @EVD@.of("a", "create").append("@GName", "#SkyyGName.Value"));
{{RULE}}
  b.set("#SkyyGRule.Text", "3 to 24 letters, digits and spaces. Every guild name is unique. You become its Leader.");
{{HELPHEAD}}
  String[] help = @PKG@.GuildStore.helpLines();
  for (int i = 0; i < help.length; i++) {
{{HELPLINE}}
    b.set("#SkyyGHelp" + i + ".Text", @PKG@.GuildStore.textOf(help[i]));
  }
  if (fillH > 0) {{FILL}}
  infoLabel(b);
{{FOOT}}
  ev.addEventBinding(@BT@.Activating, "#SkyyGRefresh", @EVD@.of("a", "refresh"));
}"""

GUILD_GUILD_TPL = r"""
public void buildGuild(@UCB@ b, @UEB@ ev, java.util.UUID u, Object[] s) {
  String name = (String) s[0];
  String tag = (String) s[1];
  long xp = ((Long) s[2]).longValue();
  long bank = ((Long) s[3]).longValue();
  int my = ((Integer) s[4]).intValue();
  java.util.ArrayList rows = (java.util.ArrayList) s[5];
  java.util.ArrayList log = (java.util.ArrayList) s[6];
  long sx = ((Long) s[7]).longValue();
  int season = ((Integer) s[8]).intValue();
  int onl = ((Integer) s[9]).intValue();
  long limA = ((Long) s[11]).longValue();
  long limM = ((Long) s[12]).longValue();
  String usage = (String) s[13];
  String dayT = (String) s[14];
  long myLim = my >= 2 ? -1L : (my == 1 ? limA : limM);
  boolean canWd = myLim != 0L;
  String us = u.toString();
  long[] li = @PKG@.GuildStore.levelInfo(xp);
{{SHELL}}
  b.set("#SkyyGTitle.Text", name + (tag.length() > 0 ? "  [" + tag + "]" : ""));
{{SUB}}
  b.set("#SkyyGSub.Text", "Guild level " + li[0] + "     Season " + season + ": " + @PKG@.GuildStore.fmt(sx) + " guild XP     You are " + (my == 1 ? "an " : "the ") + @PKG@.GuildStore.rankName(my));
  int bw = {{BARW}};
  int fill = li[2] > 0L ? (int) ((long) bw * li[1] / li[2]) : 0;
  if (fill < 0) fill = 0;
  if (fill > bw) fill = bw;
{{BAR}}
  b.set("#SkyyGBarTxt.Text", @PKG@.GuildStore.fmt(li[1]) + " / " + @PKG@.GuildStore.fmt(li[2]) + " XP to level " + (li[0] + 1L));
{{XPTXT}}
  b.set("#SkyyGXpTxt.Text", "Members add " + @PKG@.GCfg.SHARE + "% of the skill XP they earn to the guild. Total guild XP: " + @PKG@.GuildStore.fmt(xp));
{{STATS}}
  b.set("#SkyyGStats.Text", "Guild bank: " + @PKG@.GuildStore.num(bank) + " coins          Online: " + onl + " / " + rows.size() + " members");
{{HEADS}}
  b.set("#SkyyGMemAct.Text", my == 2 ? "Leader actions" : (my == 1 ? "Admin actions" : ""));
  int per = 7;
  int pages = (rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  this.rowIds = new java.util.ArrayList();
  int pw = my == 2 ? {{PW2}} : (my == 1 ? {{PW1}} : {{PW0}});
  for (int i = start; i < rows.size() && i < start + per; i++) {
    String[] r = (String[]) rows.get(i);
    int idx = i - start;
    this.rowIds.add(r[0]);
    int rr = Integer.parseInt(r[2]);
    boolean on = "1".equals(r[4]);
    boolean me = r[0].equals(us);
    long took = @PKG@.GuildStore.parseLong(r[5], 0L);
    String rid = "#SkyyGRow" + idx;
{{ROW}}
    b.set("#SkyyGRowName" + idx + ".Text", r[1] + (me ? "  (you)" : ""));
    b.set("#SkyyGRowRank" + idx + ".Text", @PKG@.GuildStore.rankName(rr));
    b.set("#SkyyGRowXp" + idx + ".Text", @PKG@.GuildStore.fmt(@PKG@.GuildStore.parseLong(r[3], 0L)) + " XP");
    b.set("#SkyyGRowDay" + idx + ".Text", took > 0L ? @PKG@.GuildStore.fmt(took) + " coins" : "-");
    b.set("#SkyyGRowOn" + idx + ".Text", on ? "online" : "offline");
    boolean canKick = !me && rr < my && my >= 1;
    if (my == 2 && !me) {
      if (rr == 0) {
{{PRO}}
        ev.addEventBinding(@BT@.Activating, "#SkyyGPro" + idx, @EVD@.of("a", "promote:" + idx));
      } else {
{{DEM}}
        ev.addEventBinding(@BT@.Activating, "#SkyyGDem" + idx, @EVD@.of("a", "demote:" + idx));
      }
    }
    if (canKick) {
      boolean ck = this.confirm.equals("kick:" + r[0]);
{{KICK}}
      ev.addEventBinding(@BT@.Activating, "#SkyyGKick" + idx, @EVD@.of("a", "kick:" + idx));
    }
    if (my == 2 && !me) {
      boolean cl = this.confirm.equals("lead:" + r[0]);
{{LEAD}}
      ev.addEventBinding(@BT@.Activating, "#SkyyGLead" + idx, @EVD@.of("a", "lead:" + idx));
    }
  }
  if (pages > 1) {
{{PAGER}}
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    ev.addEventBinding(@BT@.Activating, "#SkyyGPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGNext", @EVD@.of("a", "next"));
  } else {
{{NOPAGER}}
  }
{{ACTROW}}
  if (my >= 1) {
{{INVBOX}}
    if (this.keepInvite != null && this.keepInvite.length() > 0) b.set("#SkyyGInvite.Value", this.keepInvite);
{{INVBTN}}
    ev.addEventBinding(@BT@.Validating, "#SkyyGInvite", @EVD@.of("a", "invite").append("@GInvite", "#SkyyGInvite.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyGInviteBtn", @EVD@.of("a", "invite").append("@GInvite", "#SkyyGInvite.Value"));
{{INVGAP}}
  } else {
{{NOINV}}
  }
{{AMTBOX}}
  if (this.keepAmount != null && this.keepAmount.length() > 0) b.set("#SkyyGAmount.Value", this.keepAmount);
{{DEP}}
  ev.addEventBinding(@BT@.Activating, "#SkyyGDep", @EVD@.of("a", "deposit").append("@GAmount", "#SkyyGAmount.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyGAmount", @EVD@.of("a", "amount").append("@GAmount", "#SkyyGAmount.Value"), false);
  if (canWd) {
{{WD}}
    ev.addEventBinding(@BT@.Activating, "#SkyyGWd", @EVD@.of("a", "withdraw").append("@GAmount", "#SkyyGAmount.Value"));
  }
{{HINT}}
  b.set("#SkyyGHint.Text", (my >= 1 ? "Invite: an online player's name.   " : "") + "Amounts: 500, 2k, 1.5m or all - coins come from and go to your purse." + (canWd ? "" : "  Your rank can't withdraw right now (daily limit 0)."));
{{LIMTXT}}
  b.set("#SkyyGLimTxt.Text", "Withdraw limits per game day:  Admins " + @PKG@.GuildStore.limText(limA) + "  -  Members " + @PKG@.GuildStore.limText(limM) + "        You: " + usage + "   (" + dayT + ")");
  if (my == 2) {
{{LIMROW}}
    b.set("#SkyyGLimLbl.Text", "Set a daily limit:");
{{LIMBOX}}
    if (this.keepLimit != null && this.keepLimit.length() > 0) b.set("#SkyyGLimit.Value", this.keepLimit);
{{LIMBTNS}}
    b.set("#SkyyGLimHint.Text", "0 = no withdrawing, none = no limit");
    ev.addEventBinding(@BT@.Validating, "#SkyyGLimit", @EVD@.of("a", "limit").append("@GLimit", "#SkyyGLimit.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyGLimA", @EVD@.of("a", "limadmin").append("@GLimit", "#SkyyGLimit.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGLimM", @EVD@.of("a", "limmember").append("@GLimit", "#SkyyGLimit.Value"));
  }
{{LOGHDR}}
  b.set("#SkyyGLogCnt.Text", log.size() == 0 ? "empty" : "newest " + (log.size() < 3 ? log.size() : 3) + " of " + log.size() + " kept");
  ev.addEventBinding(@BT@.Activating, "#SkyyGExpand", @EVD@.of("a", "expand"));
  int shown = 0;
  for (int i = log.size() - 1; i >= 0 && shown < 3; i--) {
{{LOGLINE}}
    b.set("#SkyyGLog" + shown + ".Text", "   " + @PKG@.GuildStore.logText((String) log.get(i)));
    shown++;
  }
  if (shown == 0) {
{{LOGEMPTY}}
    b.set("#SkyyGLog0.Text", "   No deposits or withdrawals yet.");
    shown = 1;
  }
  int fillH = {{SLACK}} + (my == 2 ? 0 : {{LIMROWH}});
  if (fillH > 0) {{FILL}}
  infoLabel(b);
{{FOOT}}
  ev.addEventBinding(@BT@.Activating, "#SkyyGRefresh", @EVD@.of("a", "refresh"));
  boolean cLeave = this.confirm.equals("leave");
{{LEAVE}}
  ev.addEventBinding(@BT@.Activating, "#SkyyGLeave", @EVD@.of("a", "leave"));
  if (my == 2) {
    boolean cDis = this.confirm.equals("disband");
{{DISBAND}}
    ev.addEventBinding(@BT@.Activating, "#SkyyGDisband", @EVD@.of("a", "disband"));
  }
}"""

GUILD_LOG_TPL = r"""
public void buildLog(@UCB@ b, @UEB@ ev, java.util.UUID u, Object[] s) {
  String name = (String) s[0];
  String tag = (String) s[1];
  long bank = ((Long) s[3]).longValue();
  java.util.ArrayList log = (java.util.ArrayList) s[6];
  long limA = ((Long) s[11]).longValue();
  long limM = ((Long) s[12]).longValue();
  String usage = (String) s[13];
  String dayT = (String) s[14];
{{SHELL}}
  b.set("#SkyyGLogTitle.Text", name + (tag.length() > 0 ? "  [" + tag + "]" : "") + "  -  guild bank log");
{{SUB}}
  b.set("#SkyyGLogSub.Text", "Guild bank: " + @PKG@.GuildStore.num(bank) + " coins     " + log.size() + " bank moves kept, newest first");
{{LIM}}
  b.set("#SkyyGLogLim.Text", "Withdraw limits per game day:  Admins " + @PKG@.GuildStore.limText(limA) + "  -  Members " + @PKG@.GuildStore.limText(limM) + "        You: " + usage + "   (" + dayT + ")");
{{HEADS}}
  int per = 15;
  int pages = (log.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.logPage >= pages) this.logPage = pages - 1;
  if (this.logPage < 0) this.logPage = 0;
{{LIST}}
  int shown = 0;
  for (int k = 0; k < per; k++) {
    int i = log.size() - 1 - (this.logPage * per + k);
    if (i < 0) break;
    String[] lp = @PKG@.GuildStore.logParts((String) log.get(i));
    String w = lp[2];
    String col = {{LOGCOL}};
    String rid = "#SkyyGLRow" + k;
{{ROW}}
    b.set("#SkyyGLWhen" + k + ".Text", lp[0]);
    b.set("#SkyyGLWho" + k + ".Text", lp[1]);
    b.set("#SkyyGLWhat" + k + ".Text", w);
    b.set("#SkyyGLBank" + k + ".Text", lp[3].length() > 0 ? lp[3] + " coins" : "");
    shown++;
  }
  if (shown == 0) {
{{EMPTY}}
    b.set("#SkyyGLEmpty.Text", "No deposits or withdrawals yet.");
  }
  if (pages > 1) {
{{PAGER}}
    b.set("#SkyyGLPageTxt.Text", "Page " + (this.logPage + 1) + " / " + pages);
    ev.addEventBinding(@BT@.Activating, "#SkyyGLPrev", @EVD@.of("a", "lprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGLNext", @EVD@.of("a", "lnext"));
  } else {
{{NOPAGER}}
  }
{{NOTE}}
  b.set("#SkyyGLNote.Text", "The guild keeps its last " + @PKG@.GCfg.LOG_KEEP + " bank moves. Every move ever made is also in the server's banklog.log.");
{{SLACKFILL}}
  infoLabel(b);
{{FOOT}}
  ev.addEventBinding(@BT@.Activating, "#SkyyGBack", @EVD@.of("a", "back"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGRefresh", @EVD@.of("a", "refresh"));
}"""


def guild_in(outer, *kids):
    """kit markup `outer` (ending with its closing brace) with the kit markups `kids` placed inside it (KIT-GAP: skyyui._inside is
    private; the kit's own blocks compose the same way)"""
    assert outer.endswith("}") and kids, outer[:60]
    return outer[:-1] + " ".join(kids) + " }"


def guild_block(src, indent):
    """Java statements re-indented by `indent` spaces (kit output pasted into a method template)"""
    return "\n".join((" " * indent + ln) if ln.strip() else ln for ln in src.split("\n"))


def guild_fill(tpl, parts):
    """a Java template with {{NAME}} places filled with kit-built Java (each place used once, none left over). A place alone on its
    line gets the indent of the next statement line (+ 2 when that line closes a block); a place inside a line goes in as it is."""
    out = tpl
    for name, java in parts.items():
        tok = "{{" + name + "}}"
        assert out.count(tok) == 1, "Java part %s: %d places" % (name, out.count(tok))
        i = out.index(tok)
        ls = out.rfind("\n", 0, i) + 1
        le = out.find("\n", i)
        if out[ls:i] == "" and out[i + len(tok):le if le >= 0 else len(out)] == "":
            nxt = next((ln for ln in out[le + 1:].split("\n") if not re.fullmatch(r"\{\{[A-Z0-9]+\}\}", ln)), "") if le >= 0 else ""
            ind = len(nxt) - len(nxt.lstrip(" ")) + (2 if nxt.strip().startswith("}") else 0)
            body = guild_block(java, ind) if java else ""
        else:
            body = java
        out = out[:i] + body + out[i + len(tok):]
    left = re.findall(r"\{\{[A-Z0-9]+\}\}", out)
    assert not left, "unfilled Java place: %s" % left
    return out


def guild_java(ap):
    """Java append statements for (parent, markup) pairs: SUI.java_add (the append + its b.set lines)"""
    return "\n".join(SUI.java_add(p, mk) for p, mk in ap)


def guild_has_ids(java, ids, what):
    """every 0.1.3 id of a view is still created by its new Java (static "#Id {" or runtime "#Id" + (i) forms)"""
    stems = [re.sub(r"\d+$", "", i) for i in ids]
    missing = [i for i, st in zip(ids, stems) if ("#%s {" % i) not in java and ('#%s" + (' % st) not in java]
    assert not missing, "%s: 0.1.4 no longer creates the 0.1.3 id(s) %s" % (what, missing)


def guild_font(kind):
    """(px size, bold, uppercase, font) of a kit label kind as SUI.label renders it (SUI.LABELS, SUI.LABEL_MORE, SUI.fs)"""
    vs, _kc, kb, ku = SUI.LABELS[kind][:4]
    return SUI.fs(vs), bool(kb), bool(ku), SUI.LABEL_MORE.get(kind, (None,))[0] or "Default"


def guild_fits(text, kind, w, what):
    """review 2 (finding 5): a runtime (b.set) text at its widest fits its one-line box of label kind `kind`, w px wide - measured
    with the client's font tables (SUI.text_width). KIT-GAP: label(fit=True) only measures static text. Returns the share used."""
    size, bold, upper, font = guild_font(kind)
    need = SUI.text_width(text, size, bold, font, upper)
    assert need <= w, "%s: %r needs %.0f px, its box is %d px" % (what, text, need, w)
    return need / float(w)


def guild_view_none():
    """not in a guild: (java, shell, check appends, markups)"""
    W = GUILD_IN
    ap = SUI.Appends()
    none_txt = SUI.label("SkyyGNoneTxt", "", "message", h=26, anchor={"bottom": 10})
    inv = SUI.confirm_view("SkyyGuild", "SkyyGInvRow", W, question="", yes_text="Accept", no_text="Decline", compact=True, wrap=True,
                           ids={"box": "SkyyGInvRow", "question": "SkyyGInvTxt", "yes": "SkyyGAccept", "no": "SkyyGDecline"})
    create_head = SUI.label(None, "Create a guild", "subtitle", h=25, align="Center", anchor={"top": 16, "bottom": 8})
    used = GUILD_NAME_W + 6 + GUILD_CREATE_W
    create_row = SUI.button_row("SkyyGCreateRow", align="center", used=used, avail=W)
    name_box = SUI.text_field("SkyyGNameBox", "SkyyGName", w=GUILD_NAME_W, placeholder="Guild name", max_length=24,
                              anchor={"top": (SUI.BTN_H - SUI.FIELD_H) // 2})
    create_btn = SUI.button("SkyyGCreate", "Create guild", "primary", w=GUILD_CREATE_W, anchor={"left": 6})
    rule = SUI.label("SkyyGRule", "", "caption", h=25, align="Center", anchor={"top": 4})
    help_head = SUI.label(None, "Commands", "subtitle", h=25, align="Center", anchor={"top": 16, "bottom": 8})
    help_box = SUI.panel("SkyyGHelpBox", "well", h=GUILD_HELP_LINES * GUILD_HELP_H + 2 * SUI.WELL_PAD)
    help_line = SUI.label("SkyyGHelp" + SUI.J("i"), "", "default", h=GUILD_HELP_H)
    info = SUI.status_line("SkyyGInfo", "colorOf(this.info)", h=GUILD_TWO, wrap=True, anchor={"top": GUILD_INFO_TOP})
    sep = SUI.separator("content", anchor={"top": GUILD_SEP, "bottom": GUILD_SEP})
    foot = SUI.group("SkyyGBottom", "Left", h=SUI.BTN_H)
    refresh = SUI.button("SkyyGRefresh", "Refresh", "secondary", w=GUILD_BTN)
    body = [none_txt] + [mk for _p, mk in inv if _p == "SkyyGuild"] + [create_head, create_row, rule, help_head, help_box, info, sep, foot]
    inner_h = sum(SUI.outer_size(mk)[1] for mk in body)
    H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + inner_h
    sh = SUI.page_shell("SkyyGuildF", GUILD_W, H, "Guilds", body_id="SkyyGuild")
    # the check appends: the tallest state (an invite waiting), in the order the Java appends them
    ap.extend(sh.appends)
    ap.add("SkyyGuild", none_txt)
    ap.extend(inv)
    for p, mk in (("SkyyGuild", create_head), ("SkyyGuild", create_row), ("SkyyGCreateRow", name_box), ("SkyyGCreateRow", create_btn),
                  ("SkyyGuild", rule), ("SkyyGuild", help_head), ("SkyyGuild", help_box)):
        ap.add(p, mk)
    for k in range(GUILD_HELP_LINES):
        ap.add("SkyyGHelpBox", SUI.label("SkyyGHelp%d" % k, "", "default", h=GUILD_HELP_H))
    for p, mk in (("SkyyGuild", info), ("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh)):
        ap.add(p, mk)
    assert SUI.fit([SUI.used_height(ap, "SkyyGuild")], sh.inner_h, "guild page (not in a guild)") == 0
    assert SUI.used_width(ap, "SkyyGCreateRow") == used and SUI.fit([used + create_row.left], W, "create row") >= 0
    fill_sp = SUI.spacer(h=SUI.J("fillH", str(inv.h)))
    parts = {
        "SHELL": sh.java("b"),
        "NONETXT": SUI.java_append("SkyyGuild", none_txt),
        "INVH": str(inv.h),
        "INVROW": inv.java("b"),
        "CREATE": guild_java([("SkyyGuild", create_head), ("SkyyGuild", create_row), ("SkyyGCreateRow", name_box),
                              ("SkyyGCreateRow", create_btn)]),
        "RULE": SUI.java_append("SkyyGuild", rule),
        "HELPHEAD": guild_java([("SkyyGuild", help_head), ("SkyyGuild", help_box)]),
        "HELPLINE": SUI.java_append("SkyyGHelpBox", help_line),
        "FILL": SUI.java_append("SkyyGuild", fill_sp),
        "FOOT": guild_java([("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh)]),
    }
    java = guild_fill(GUILD_NONE_TPL, parts)
    guild_has_ids(java + GUILD_INFO_SRC, GUILD_IDS_013["buildNone"], "buildNone")
    marks = [mk for _p, mk in ap] + [help_line, fill_sp]
    return java, sh, ap, marks


def guild_row_markup():
    """one member row (the Java loop appends it with J() values): a fixed-width WorldEventListRow panel (no FlexWeight) whose width
    depends on the viewer's rank (pw), a status bar (green = online), the 5 cells with their 0.1.3 ids"""
    i = SUI.J("idx")
    assert len(set(SUI.norm_color(SUI.color(c)) for c in ("gold", GUILD_RANK_ADMIN, "value"))) == 3, "the rank colours must differ"
    bg = SUI.color_by([("me", "rowPressed")], "row")
    panel = SUI.panel("SkyyGRowP" + i, "row", w=SUI.J("pw", str(GUILD_PW[2])), h=GUILD_ROW_H, layout="Left",
                      pad={"left": GUILD_ROW_PAD, "right": GUILD_ROW_PAD}, bg=bg)
    ws = [w for _t, w in GUILD_COLS]
    # review 2: the widest texts of each cell (the kinds below are the cells' own)
    for text, kind, w, what in ((GUILD_NAME_WIDE, "rowName", ws[0], "member name"), (GUILD_NAME_YOU, "rowName", ws[0], "your name"),
                                ("Leader", "bold", ws[1], "rank"), ("Admin", "bold", ws[1], "rank"), ("Member", "bold", ws[1], "rank"),
                                ("9999.99b XP", "default", ws[2], "guild XP added"), (GUILD_TAKEN_WIDE, "default", ws[3], "taken today"),
                                ("online", "default", ws[4], "status"), ("offline", "default", ws[4], "status")):
        guild_fits(text, kind, w, what)
    cells = [SUI.status_bar("SkyyGRowBar" + i, on=SUI.J("on"), col="success"),
             SUI.label("SkyyGRowName" + i, "", "rowName", w=ws[0], h=GUILD_ROW_H, col=SUI.color_by([("on", "rowName")], "rowSub")),
             SUI.label("SkyyGRowRank" + i, "", "bold", w=ws[1], h=GUILD_ROW_H,
                       col=SUI.color_by([("rr == 2", "gold"), ("rr == 1", GUILD_RANK_ADMIN)], "value")),
             SUI.label("SkyyGRowXp" + i, "", "default", w=ws[2], h=GUILD_ROW_H, col="value"),
             SUI.label("SkyyGRowDay" + i, "", "default", w=ws[3], h=GUILD_ROW_H, col=SUI.color_by([("took > 0L", "gold")], "disabled")),
             SUI.label("SkyyGRowOn" + i, "", "default", w=ws[4], h=GUILD_ROW_H, col=SUI.color_by([("on", "success")], "disabled"))]
    row = SUI.group("SkyyGRow" + i, "Left", h=GUILD_ROW_H, anchor={"bottom": GUILD_ROW_GAP})
    # the Leader's panel (the narrowest) holds the bar + the 5 cells exactly: read back out of the markup
    assert SUI.fit([sum(SUI.outer_size(c)[0] for c in cells)], GUILD_PW[2] - 2 * GUILD_ROW_PAD, "member row panel") == 0
    assert all(SUI.outer_size(c)[1] in (None, GUILD_ROW_H) for c in cells)
    return guild_in(row, guild_in(panel, *cells))


def guild_view_guild():
    """the guild view: (java, shell, check appends of the tallest state - the Leader with 2+ member pages -, markups)"""
    W = GUILD_IN
    ap = SUI.Appends()
    i = SUI.J("idx")
    # summary well: the level / season / rank line, the XP text over the bar, "members add ..." | the bank + online line
    sum_h = 2 * SUI.WELL_PAD + GUILD_SUB_H + GUILD_BARTXT_H + GUILD_BAR_H + GUILD_BAR_GAP + GUILD_SUMROW_H
    summ = SUI.panel("SkyyGSum", "well", h=sum_h, anchor={"bottom": 6})
    sub = SUI.label("SkyyGSub", "", "default", h=GUILD_SUB_H, align="Center")
    bartxt = SUI.label("SkyyGBarTxt", "", "bold", h=GUILD_BARTXT_H, align="Center")
    bar = SUI.stat_bar("SkyyGBar", GUILD_SUM_IN, GUILD_BAR_H, SUI.J("fill", str(GUILD_SUM_IN // 2)), anchor={"bottom": GUILD_BAR_GAP})
    sumrow = SUI.group("SkyyGSumRow", "Left", h=GUILD_SUMROW_H)
    xptxt = SUI.label("SkyyGXpTxt", "", "caption", w=GUILD_XPTXT_W, h=GUILD_SUMROW_H)
    stats = SUI.label("SkyyGStats", "", "gold", w=GUILD_SUM_IN - GUILD_XPTXT_W, h=GUILD_SUMROW_H, align="End")
    guild_fits(GUILD_XPTXT_WIDE, "caption", GUILD_XPTXT_W, "#SkyyGXpTxt")
    guild_fits(GUILD_STATS_WIDE, "gold", GUILD_SUM_IN - GUILD_XPTXT_W, "#SkyyGStats")
    # member table: column heads (+ the actions head, right-aligned over the buttons) and the 7-row list well
    for t, w in GUILD_COLS:
        guild_fits(t, "section", w, "member column head")
    spec = SUI.column_spec(GUILD_COLS, avail=GUILD_PW[2], pad_left=GUILD_ROW_PAD + GUILD_BAR)
    heads = spec.heads("SkyyGMemHdr", h=GUILD_HEAD_H, outside=SUI.WELL_LIST_PAD)
    head_used = SUI.WELL_LIST_PAD + GUILD_ROW_PAD + GUILD_BAR + spec.total
    act_head = SUI.label("SkyyGMemAct", "", "section", w=GUILD_ACT_HEAD_W, h=GUILD_HEAD_H, align="End",
                         anchor={"left": W - SUI.WELL_LIST_PAD - head_used - GUILD_ACT_HEAD_W})     # ends over the last button
    lst = SUI.list_well("SkyyGList", w=W, rows=GUILD_ROWS, row_h=GUILD_ROW_H, gap=GUILD_ROW_GAP)
    row = guild_row_markup()
    pro = SUI.button("SkyyGPro" + i, "Promote", "secondary", "small", w=GUILD_PRO_W, h=GUILD_ROW_H, anchor={"left": GUILD_ACT_GAP})
    dem = SUI.button("SkyyGDem" + i, "Demote", "secondary", "small", w=GUILD_PRO_W, h=GUILD_ROW_H, anchor={"left": GUILD_ACT_GAP})
    kick = SUI.choose(SUI.J("ck"),
                      SUI.button("SkyyGKick" + i, "Sure", "destructive", "small", w=GUILD_KICK_W, h=GUILD_ROW_H, anchor={"left": GUILD_ACT_GAP}),
                      SUI.button("SkyyGKick" + i, "Kick", "destructive", "small", w=GUILD_KICK_W, h=GUILD_ROW_H, anchor={"left": GUILD_ACT_GAP}))
    lead = SUI.choose(SUI.J("cl"),
                      SUI.button("SkyyGLead" + i, "Confirm", "destructive", "small", w=GUILD_LEAD_W, h=GUILD_ROW_H,
                                 anchor={"left": GUILD_ACT_GAP}),
                      SUI.button("SkyyGLead" + i, "Make leader", "secondary", "small", w=GUILD_LEAD_W, h=GUILD_ROW_H,
                                 anchor={"left": GUILD_ACT_GAP}))
    pager = SUI.pager("SkyyGuild", "SkyyGNav", W, text=None, prev_on=SUI.J("this.pageNo > 0"), next_on=SUI.J("this.pageNo < pages - 1"),
                      ids={"row": "SkyyGNav", "prev": "SkyyGPrev", "page": "SkyyGPageTxt", "next": "SkyyGNext"})
    nopager = SUI.spacer(h=pager.h)
    # the invite + bank controls row (Invite / Deposit = Primary, Withdraw = Secondary; the text fields centred on the 44 px row)
    ftop = (SUI.BTN_H - SUI.FIELD_H) // 2
    act = SUI.group("SkyyGAct", "Left", h=SUI.BTN_H, anchor={"top": 8})
    inv_w = GUILD_INV_W + 6 + GUILD_INVBTN_W
    bank_w = GUILD_AMT_W + 6 + GUILD_BTN + 6 + GUILD_BTN
    gap = W - inv_w - bank_w
    assert gap >= 60, gap
    invbox = SUI.text_field("SkyyGInvBox", "SkyyGInvite", w=GUILD_INV_W, placeholder="Player name", max_length=32, anchor={"top": ftop})
    invbtn = SUI.button("SkyyGInviteBtn", "Invite", "primary", w=GUILD_INVBTN_W, anchor={"left": 6})
    invgap = SUI.spacer(w=gap, h=SUI.BTN_H)
    noinv = SUI.spacer(w=inv_w + gap, h=SUI.BTN_H)
    amtbox = SUI.text_field("SkyyGAmtBox", "SkyyGAmount", w=GUILD_AMT_W, placeholder="Amount", max_length=16, anchor={"top": ftop})
    dep = SUI.button("SkyyGDep", "Deposit", "primary", w=GUILD_BTN, anchor={"left": 6})
    wd = SUI.button("SkyyGWd", "Withdraw", "secondary", w=GUILD_BTN, anchor={"left": 6})
    hint = SUI.label("SkyyGHint", "", "caption", h=25, align="Center")
    limtxt = SUI.label("SkyyGLimTxt", "", "bold", h=GUILD_TWO, align="Center", wrap=True)
    # the Leader's limit row
    limrow = SUI.group("SkyyGLimRow", "Left", h=SUI.BTN_H, anchor={"top": 6})
    limlbl = SUI.label("SkyyGLimLbl", "", "bold", w=GUILD_LIM_LBL_W, h=SUI.BTN_H, align="End", anchor={"right": 10})
    limbox = SUI.text_field("SkyyGLimBox", "SkyyGLimit", w=GUILD_LIM_BOX_W, placeholder="5k  0  or none", max_length=16, anchor={"top": ftop})
    lima = SUI.button("SkyyGLimA", "Set Admin limit", "secondary", w=GUILD_LIMA_W, anchor={"left": 6})
    limm = SUI.button("SkyyGLimM", "Set Member limit", "secondary", w=GUILD_LIMM_W, anchor={"left": 6})
    lim_rest = W - GUILD_LIM_LBL_W - 10 - GUILD_LIM_BOX_W - 6 - GUILD_LIMA_W - 6 - GUILD_LIMM_W - 12
    limhint = SUI.label("SkyyGLimHint", "", "caption", w=lim_rest, h=SUI.BTN_H, anchor={"left": 12})
    # the bank log head + the newest 3 lines in a well
    loghdr = SUI.group("SkyyGLogHdr", "Left", h=SUI.BTN_SMALL_H, anchor={"top": 8})
    loghead = SUI.label(None, "Guild bank log", "section", w=GUILD_LOGHDR_W, h=SUI.BTN_SMALL_H)
    logcnt = SUI.label("SkyyGLogCnt", "", "caption", w=GUILD_LOGCNT_W, h=SUI.BTN_SMALL_H)
    loggap = SUI.spacer(w=W - GUILD_LOGHDR_W - GUILD_LOGCNT_W - GUILD_EXPAND_W, h=SUI.BTN_SMALL_H)
    expand = SUI.button("SkyyGExpand", "Expand log", "secondary", "small", w=GUILD_EXPAND_W)
    logbox = SUI.panel("SkyyGLogBox", "well", h=3 * GUILD_LOG_LINE_H + 2 * GUILD_LOG_PAD, pad=GUILD_LOG_PAD)
    logline = SUI.label("SkyyGLog" + SUI.J("shown"), "", "default", h=GUILD_LOG_LINE_H)
    logempty = SUI.label("SkyyGLog0", "", "default", h=GUILD_LOG_LINE_H, col="caption")
    # the result line, the separator, the footer (Refresh left; Leave / Disband right: the gap before them is by the viewer's rank)
    info = SUI.status_line("SkyyGInfo", "colorOf(this.info)", h=GUILD_TWO, wrap=True, anchor={"top": GUILD_INFO_TOP})
    sep = SUI.separator("content", anchor={"top": GUILD_SEP, "bottom": GUILD_SEP})
    foot = SUI.group("SkyyGBottom", "Left", h=SUI.BTN_H)
    refresh = SUI.button("SkyyGRefresh", "Refresh", "secondary", w=GUILD_BTN)
    gap_lead = W - GUILD_BTN - GUILD_LEAVE_W - 6 - GUILD_DISBAND_W
    gap_other = W - GUILD_BTN - GUILD_LEAVE_W
    gapr = SUI.spacer(w=SUI.J("my == 2 ? %d : %d" % (gap_lead, gap_other), str(gap_lead)), h=SUI.BTN_H)
    leave = SUI.choose(SUI.J("cLeave"), SUI.button("SkyyGLeave", "Click again to leave", "destructive", w=GUILD_LEAVE_W),
                       SUI.button("SkyyGLeave", "Leave guild", "destructive", w=GUILD_LEAVE_W))
    disband = SUI.choose(SUI.J("cDis"), SUI.button("SkyyGDisband", "Click again to DISBAND", "destructive", w=GUILD_DISBAND_W, anchor={"left": 6}),
                         SUI.button("SkyyGDisband", "Disband guild", "destructive", w=GUILD_DISBAND_W, anchor={"left": 6}))
    # the page height = the sum of the tallest state's parts (the Leader, 2+ member pages): read back out of the markup
    body = [summ, heads, lst, None, act, hint, limtxt, limrow, loghdr, logbox, info, sep, foot]
    inner_h = sum(SUI.outer_size(mk)[1] for mk in body if mk is not None) + pager.h
    H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + inner_h
    sh = SUI.page_shell("SkyyGuildF", GUILD_W, H, "", body_id="SkyyGuild", title_id="SkyyGTitle")
    limrow_h = SUI.outer_size(limrow)[1]
    # the check appends: the Leader view with a pager, 7 rows (Leader looking at 6 others + himself), 3 log lines
    ap.extend(sh.appends)
    for p, mk in (("SkyyGuild", summ), ("SkyyGSum", sub), ("SkyyGSum", bartxt), ("SkyyGSum", bar.full), ("SkyyGSum", sumrow),
                  ("SkyyGSumRow", xptxt), ("SkyyGSumRow", stats), ("SkyyGuild", heads), ("SkyyGMemHdr", act_head), ("SkyyGuild", lst)):
        ap.add(p, mk)
    for k in range(GUILD_ROWS):
        ap.add("SkyyGList", re.sub(r"(#SkyyGRow[A-Za-z]*)0\b", lambda m: m.group(1) + str(k), SUI.render(row)))
        if k > 0:
            for b_ in (pro if k % 2 else dem, kick.b, lead.b):
                ap.add("SkyyGRow%d" % k, re.sub(r"(#SkyyG(?:Pro|Dem|Kick|Lead))0\b", lambda m: m.group(1) + str(k), SUI.render(b_)))
    ap.extend(pager)
    for p, mk in (("SkyyGuild", act), ("SkyyGAct", invbox), ("SkyyGAct", invbtn), ("SkyyGAct", invgap), ("SkyyGAct", amtbox),
                  ("SkyyGAct", dep), ("SkyyGAct", wd), ("SkyyGuild", hint), ("SkyyGuild", limtxt), ("SkyyGuild", limrow),
                  ("SkyyGLimRow", limlbl), ("SkyyGLimRow", limbox), ("SkyyGLimRow", lima), ("SkyyGLimRow", limm), ("SkyyGLimRow", limhint),
                  ("SkyyGuild", loghdr), ("SkyyGLogHdr", loghead), ("SkyyGLogHdr", logcnt), ("SkyyGLogHdr", loggap),
                  ("SkyyGLogHdr", expand), ("SkyyGuild", logbox)):
        ap.add(p, mk)
    for k in range(3):
        ap.add("SkyyGLogBox", SUI.label("SkyyGLog%d" % k, "", "default", h=GUILD_LOG_LINE_H))
    for p, mk in (("SkyyGuild", info), ("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh),
                  ("SkyyGBottom", SUI.spacer(w=gap_lead, h=SUI.BTN_H)), ("SkyyGBottom", leave.b), ("SkyyGBottom", disband.b)):
        ap.add(p, mk)
    # the budgets: the body column, every row and every well filled exactly (read back out of the markup)
    assert SUI.fit([SUI.used_height(ap, "SkyyGuild")], sh.inner_h, "guild view body") == 0
    assert SUI.fit([SUI.used_height(ap, "SkyyGSum")], sum_h - 2 * SUI.WELL_PAD, "summary well") == 0
    assert SUI.fit([SUI.used_height(ap, "SkyyGList")], lst.inner_h, "member list") == 0
    assert SUI.fit([SUI.used_height(ap, "SkyyGLogBox")], 3 * GUILD_LOG_LINE_H, "log well") == 0
    for rid, avail in (("SkyyGSumRow", GUILD_SUM_IN), ("SkyyGAct", W), ("SkyyGLimRow", W), ("SkyyGLogHdr", W), ("SkyyGBottom", W)):
        assert SUI.fit([SUI.used_width(ap, rid)], avail, "row " + rid) == 0, rid
    for k in range(1, GUILD_ROWS):      # the row panel is inside the row markup; the Leader's 3 buttons are appended after it
        assert SUI.fit([GUILD_PW[2], SUI.used_width(ap, "SkyyGRow%d" % k)], GUILD_ROW_W, "member row") == 0
    # the heads: the column heads (inside their Markup) + the actions head end exactly where the rows end (the well's inner edge)
    assert SUI.outer_size(act_head)[0] + head_used == W - SUI.WELL_LIST_PAD and SUI.outer_size(heads)[1] == SUI.outer_size(act_head)[1]
    assert gap_other >= 0 and gap_lead >= 0 and lim_rest >= 240
    fill_sp = SUI.spacer(h=SUI.J("fillH", str(limrow_h)))
    parts = {
        "SHELL": sh.java("b"),
        "SUB": guild_java([("SkyyGuild", summ), ("SkyyGSum", sub)]),
        "BARW": str(GUILD_SUM_IN),
        "BAR": "\n".join([SUI.java_append("SkyyGSum", bartxt), SUI.java_append("SkyyGSum", bar.choose())]),
        "XPTXT": guild_java([("SkyyGSum", sumrow), ("SkyyGSumRow", xptxt)]),
        "STATS": SUI.java_append("SkyyGSumRow", stats),
        "HEADS": guild_java([("SkyyGuild", heads), ("SkyyGMemHdr", act_head), ("SkyyGuild", lst)]),
        "PW2": str(GUILD_PW[2]), "PW1": str(GUILD_PW[1]), "PW0": str(GUILD_PW[0]),
        "ROW": SUI.java_append("SkyyGList", row),
        "PRO": SUI.java_append("SkyyGRow" + i, pro),
        "DEM": SUI.java_append("SkyyGRow" + i, dem),
        "KICK": SUI.java_append("SkyyGRow" + i, kick),
        "LEAD": SUI.java_append("SkyyGRow" + i, lead),
        "PAGER": pager.java("b"),
        "NOPAGER": SUI.java_append("SkyyGuild", nopager),
        "ACTROW": SUI.java_append("SkyyGuild", act),
        "INVBOX": SUI.java_append("SkyyGAct", invbox),
        "INVBTN": SUI.java_append("SkyyGAct", invbtn),
        "INVGAP": SUI.java_append("SkyyGAct", invgap),
        "NOINV": SUI.java_append("SkyyGAct", noinv),
        "AMTBOX": SUI.java_append("SkyyGAct", amtbox),
        "DEP": SUI.java_append("SkyyGAct", dep),
        "WD": SUI.java_append("SkyyGAct", wd),
        "HINT": SUI.java_append("SkyyGuild", hint),
        "LIMTXT": SUI.java_append("SkyyGuild", limtxt),
        "LIMROW": guild_java([("SkyyGuild", limrow), ("SkyyGLimRow", limlbl)]),
        "LIMBOX": SUI.java_append("SkyyGLimRow", limbox),
        "LIMBTNS": guild_java([("SkyyGLimRow", lima), ("SkyyGLimRow", limm), ("SkyyGLimRow", limhint)]),
        "LOGHDR": guild_java([("SkyyGuild", loghdr), ("SkyyGLogHdr", loghead), ("SkyyGLogHdr", logcnt), ("SkyyGLogHdr", loggap),
                              ("SkyyGLogHdr", expand), ("SkyyGuild", logbox)]),
        "LOGLINE": SUI.java_append("SkyyGLogBox", logline),
        "LOGEMPTY": SUI.java_append("SkyyGLogBox", logempty),
        "SLACK": "0",
        "LIMROWH": str(limrow_h),
        "FILL": SUI.java_append("SkyyGuild", fill_sp),
        "FOOT": guild_java([("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh)]),
        "LEAVE": "\n".join([SUI.java_append("SkyyGBottom", gapr), SUI.java_append("SkyyGBottom", leave)]),
        "DISBAND": SUI.java_append("SkyyGBottom", disband),
    }
    java = guild_fill(GUILD_GUILD_TPL, parts)
    guild_has_ids(java + GUILD_INFO_SRC, GUILD_IDS_013["buildGuild"], "buildGuild")
    marks = ([mk for _p, mk in ap] + [row, pro, dem, kick, lead, bar.empty, nopager, noinv, logline, logempty, fill_sp, gapr, leave,
                                      disband])
    return java, sh, ap, marks


def guild_log_row_markup():
    """one bank log row: a fixed-width row panel (vanilla lists do not alternate their rows) with the 4 cells and their 0.1.3 ids"""
    k = SUI.J("k")
    ws = [w for _t, w in GUILD_LCOLS]
    # review 2: the widest texts of each cell (GuildStore.logParts formats; the kinds below are the cells' own)
    for text, kind, w, what in (("12-31 23:59", "default", ws[0], "log when"), (GUILD_NAME_WIDE, "rowName", ws[1], "log player"),
                                (GUILD_WHAT_WIDE, "default", ws[2], "log what"), (GUILD_BANK_WIDE, "default", ws[3], "log bank after")):
        guild_fits(text, kind, w, what)
    for t, w in GUILD_LCOLS:
        guild_fits(t, "section", w, "log column head")
    row = SUI.panel("SkyyGLRow" + k, "row", h=GUILD_LROW_H, layout="Left", pad={"left": GUILD_ROW_PAD, "right": GUILD_ROW_PAD},
                    anchor={"bottom": GUILD_ROW_GAP})
    cells = [SUI.label("SkyyGLWhen" + k, "", "default", w=ws[0], h=GUILD_LROW_H),
             SUI.label("SkyyGLWho" + k, "", "rowName", w=ws[1], h=GUILD_LROW_H),
             SUI.label("SkyyGLWhat" + k, "", "default", w=ws[2], h=GUILD_LROW_H, col=SUI.J("col", SUI.COLOR["success"])),
             SUI.label("SkyyGLBank" + k, "", "default", w=ws[3], h=GUILD_LROW_H, col="value")]
    assert SUI.fit([sum(SUI.outer_size(c)[0] for c in cells)], GUILD_ROW_W - 2 * GUILD_ROW_PAD, "log row") == 0
    return guild_in(row, *cells)


def guild_view_log(H):
    """the bank log view (the same window size as the guild view): (java, shell, check appends, markups)"""
    W = GUILD_IN
    ap = SUI.Appends()
    sub = SUI.label("SkyyGLogSub", "", "default", h=GUILD_SUB_H, align="Center")
    lim = SUI.label("SkyyGLogLim", "", "bold", h=GUILD_TWO, align="Center", wrap=True)
    spec = SUI.column_spec(GUILD_LCOLS, avail=GUILD_ROW_W, pad_left=GUILD_ROW_PAD)
    heads = spec.heads("SkyyGLogCols", h=GUILD_HEAD_H, outside=SUI.WELL_LIST_PAD)
    lst = SUI.list_well("SkyyGLList", w=W, rows=GUILD_LROWS, row_h=GUILD_LROW_H, gap=GUILD_ROW_GAP)
    row = guild_log_row_markup()
    empty = SUI.label("SkyyGLEmpty", "", "default", h=40, align="Center", col="caption")
    pager = SUI.pager("SkyyGuild", "SkyyGLNav", W, text=None, prev_on=SUI.J("this.logPage > 0"),
                      next_on=SUI.J("this.logPage < pages - 1"), prev_text="< Newer", next_text="Older >",
                      ids={"row": "SkyyGLNav", "prev": "SkyyGLPrev", "page": "SkyyGLPageTxt", "next": "SkyyGLNext"})
    nopager = SUI.spacer(h=pager.h)
    note = SUI.label("SkyyGLNote", "", "caption", h=25, align="Center")
    info = SUI.status_line("SkyyGInfo", "colorOf(this.info)", h=GUILD_TWO, wrap=True, anchor={"top": GUILD_INFO_TOP})
    sep = SUI.separator("content", anchor={"top": GUILD_SEP, "bottom": GUILD_SEP})
    foot = SUI.group("SkyyGBottom", "Left", h=SUI.BTN_H)
    refresh = SUI.button("SkyyGRefresh", "Refresh", "secondary", w=GUILD_BTN)
    backgap = SUI.spacer(w=W - GUILD_BTN - GUILD_BACK_W, h=SUI.BTN_H)
    back = SUI.button("SkyyGBack", "< Back to guild", "secondary", w=GUILD_BACK_W, sound="cancel")
    sh = SUI.page_shell("SkyyGuildF", GUILD_W, H, "", body_id="SkyyGuild", title_id="SkyyGLogTitle")
    used = sum(SUI.outer_size(mk)[1] for mk in (sub, lim, heads, lst, note, info, sep, foot)) + pager.h
    slack = SUI.fit([used], sh.inner_h, "log view body")
    slackfill = SUI.spacer(h=slack) if slack else None
    ap.extend(sh.appends)
    for p, mk in (("SkyyGuild", sub), ("SkyyGuild", lim), ("SkyyGuild", heads), ("SkyyGuild", lst)):
        ap.add(p, mk)
    for kk in range(GUILD_LROWS):
        ap.add("SkyyGLList", re.sub(r"(#SkyyGL[A-Za-z]*)0\b", lambda m: m.group(1) + str(kk), SUI.render(row)))
    ap.extend(pager)
    ap.add("SkyyGuild", note)
    if slackfill:
        ap.add("SkyyGuild", slackfill)
    for p, mk in (("SkyyGuild", info), ("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh), ("SkyyGBottom", backgap),
                  ("SkyyGBottom", back)):
        ap.add(p, mk)
    assert SUI.fit([SUI.used_height(ap, "SkyyGuild")], sh.inner_h, "log view body") == 0
    assert SUI.fit([SUI.used_height(ap, "SkyyGLList")], lst.inner_h, "log list") == 0
    assert SUI.fit([SUI.used_width(ap, "SkyyGBottom")], W, "log footer") == 0
    logcol = SUI.color_by([('w.startsWith("deposited")', GUILD_LOG_COLS["deposited"]), ('w.startsWith("withdrew")', GUILD_LOG_COLS["withdrew"]),
                           ('w.startsWith("set the")', GUILD_LOG_COLS["set the"])], GUILD_LOG_COLS["other"])
    parts = {
        "SHELL": sh.java("b"),
        "SUB": SUI.java_append("SkyyGuild", sub),
        "LIM": SUI.java_append("SkyyGuild", lim),
        "HEADS": SUI.java_add("SkyyGuild", heads),
        "LIST": SUI.java_append("SkyyGuild", lst),
        "LOGCOL": SUI.java_expr(logcol),
        "ROW": SUI.java_append("SkyyGLList", row),
        "EMPTY": SUI.java_append("SkyyGLList", empty),
        "PAGER": pager.java("b"),
        "NOPAGER": SUI.java_append("SkyyGuild", nopager),
        "NOTE": SUI.java_append("SkyyGuild", note),
        "SLACKFILL": SUI.java_append("SkyyGuild", slackfill) if slackfill else "",
        "FOOT": guild_java([("SkyyGuild", sep), ("SkyyGuild", foot), ("SkyyGBottom", refresh), ("SkyyGBottom", backgap),
                            ("SkyyGBottom", back)]),
    }
    java = guild_fill(GUILD_LOG_TPL, parts)
    guild_has_ids(java + GUILD_INFO_SRC, GUILD_IDS_013["buildLog"], "buildLog")
    marks = [mk for _p, mk in ap] + [row, empty, nopager]
    return java, sh, ap, marks


# GuildPage.colorOf: the vanilla result colours. Only the colour method goes into the page (review 2026-09-29: the kit's textOf was
# never called - infoLabel's text is GuildStore.textOf, 0.1.3's)
GUILD_STATUS_SRC = SUI.java_status_methods("colorOf", "textOf")[:1]


def guild_page():
    """{"info", "none", "guild", "log": Java source, "views": {name: (shell, appends)}, "id": GUILD_PAGE_ID}: GuildPage's look from
    the kit. Every body filled exactly, every 0.1.3 id kept, only proven properties (assert_proven), the markup rules (check_page)."""
    global GUILD_INFO_SRC
    info = SUI.status_line("SkyyGInfo", "colorOf(this.info)", h=GUILD_TWO, wrap=True, anchor={"top": GUILD_INFO_TOP})
    GUILD_INFO_SRC = guild_fill(GUILD_INFO_TPL, {"INFO": SUI.java_append("SkyyGuild", info)})
    none_java, none_sh, none_ap, none_mk = guild_view_none()
    guild_java_src, guild_sh, guild_ap, guild_mk = guild_view_guild()
    log_java, log_sh, log_ap, log_mk = guild_view_log(guild_sh.h)
    for sh in (none_sh, guild_sh, log_sh):
        SUI.assert_page_size(sh.w, sh.h)
    for name, ap in (("none", none_ap), ("guild", guild_ap), ("log", log_ap)):
        ap.check(GUILD_PREFIX)
    SUI.assert_proven(none_mk + guild_mk + log_mk + [info], what="GuildPage")
    srcs = list(GUILD_STATUS_SRC) + [GUILD_INFO_SRC, none_java, guild_java_src, log_java]
    pid = hashlib.sha256("\n".join(srcs).encode("utf8")).hexdigest()[:12]
    return {"info": GUILD_INFO_SRC, "none": none_java, "guild": guild_java_src, "log": log_java,
            "views": {"none": (none_sh, none_ap), "guild": (guild_sh, guild_ap), "log": (log_sh, log_ap)}, "id": pid}


GUILD_INFO_SRC = ""
GUILD_PAGE = guild_page()
GUILD_PAGE_ID = GUILD_PAGE["id"]
for _src in GUILD_STATUS_SRC:
    M(page, _src)
M(page, GUILD_PAGE["info"])
M(page, GUILD_PAGE["none"])
M(page, GUILD_PAGE["guild"])
M(page, GUILD_PAGE["log"])
T["KITID"] = KIT_ID
T["PAGEID"] = GUILD_PAGE_ID
print("guild page %s: views %s, kit %s" % (GUILD_PAGE_ID, ", ".join("%s %dx%d" % (k, v[0].w, v[0].h) for k, v in sorted(GUILD_PAGE["views"].items())),
                                           KIT_ID))
# review 2 (finding 3): every build log says one of the two (the SkyyBank 0.1.4 / SkyyCollections 0.2.4 pattern)
if GUILD_PAGE_ID == GUILD_PAGE_CHECKED:
    print("guild page %s = the page SkyyGuilds/test_skyyguilds_0.1.4.py last passed on" % GUILD_PAGE_ID)
else:
    print("WARNING: guild page %s is NOT the page SkyyGuilds/test_skyyguilds_0.1.4.py last passed on (%s): the kit output changed the "
          "page. Run the harness, then set PAGE_CHECKED in tools/guilds_0_1_4_patch.py and regenerate; never deploy an unchecked page"
          % (GUILD_PAGE_ID, GUILD_PAGE_CHECKED))
'''
# review: the page id the harness last passed on (GUILD_PAGE_ID of the checked build; 20f02e4828ae before the first 2026-09-29 review
# fixes: colorOf only, Admin rank colour info; bec59fc40964 before review 2: the column widths and the summary row split, finding 5)
PAGE_CHECKED = "8ae0b80a1870"
IDS_SRC = "{\n" + "".join("    %r: %r,\n" % (k, v) for k, v in sorted(IDS.items())) + "}"
rep("@@PAGE@@", fill(PAGE_BLOCK, {"IDS": IDS_SRC, "PAGECHECKED": PAGE_CHECKED}) + "\n")
rep('import sys, os, re\n', 'import sys, os, re, hashlib\n')

# ---- 0.1.3's statements that are not markup must all be in the 0.1.4 templates, word for word (a multiset of whole lines)
# dropped: every append line, the style() lines, the old heads style string; CHANGED: the lines below (each one replaced on purpose)
CHANGED = {
    "  String col = @PKG@.GuildStore.colorOf(this.info);": "infoLabel: the colour is the page's own kit colorOf(this.info) in the markup",
    "  int bw = 1072;": "buildGuild: the bar is as wide as the summary well (GUILD_SUM_IN)",
    '    String rc = rr == 2 ? "#ffd060" : (rr == 1 ? "#8fc8ff" : "#c8d4e0");': "buildGuild: rank colour = kit colour names in the row markup",
    '    String col = w.startsWith("deposited") ? "#8fe39a" : (w.startsWith("withdrew") ? "#ffb070" : (w.startsWith("set the") ? "#8fc8ff" : "#ffe08a"));':
        "buildLog: the same four cases in kit colours (GUILD_LOG_COLS)",
    "  } else if (shown < per) {": "buildLog: the list well has a fixed height - no filler for a short last page",
}
_tpls = [ln[:-3] if ln.endswith('}"""') else ln for ln in PAGE_BLOCK.split(LF)]     # a template's closing brace carries the quotes
for _n in ("infoLabel", "buildNone", "buildGuild", "buildLog"):
    _kept = [ln for ln in OLDM[_n][1:] if ln.strip() and "b.appendInline(" not in ln and " = style(\"#" not in ln
             and not ln.startswith('  String hs = "Style:') and ln not in CHANGED]
    _missing = collections.Counter(_kept) - collections.Counter(_tpls)
    assert not _missing, "%s: 0.1.3 lines missing from the 0.1.4 template: %s" % (_n, list(_missing))
_changed_found = [c for c in CHANGED if any(c == ln for n in OLDM for ln in OLDM[n])]
assert sorted(_changed_found) == sorted(CHANGED), "a CHANGED line is not in 0.1.3: %s" % sorted(set(CHANGED) - set(_changed_found))
assert [ln for ln in _tpls if "ev.addEventBinding(" in ln] == BIND0, "binding lines / order changed in the templates"

# ================================================================================================ ready log line: kit + page id
rep('getLogger().at(java.util.logging.Level.INFO).log("[SkyyGuilds] @VERSION@ ready - /guild (page), /gc, /guildadmin; ',
    'getLogger().at(java.util.logging.Level.INFO).log("[SkyyGuilds] @VERSION@ ready (@KITID@, page @PAGEID@) - /guild (page), /gc, /guildadmin; ')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "command / system registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.3's changed: %s" % k[:80]
_page = s[s.index("# ================= GuildPage (0.1.3 logic"):s.index('M(page, r"""\npublic void build(@REF@ ref')]
for c in ("#0b1524", "#ffd070", "#ffe08a", "#1d3a5f", "#2f5a8f", "#0f2038", "#1f5a34", "#2c7a48", "#133a22", "#5a2424", "#7a3030",
          "#3a1414", "#7a3a10", "#3a2f5f", "#54448a", "#16263a", "#142030", "#22324a", "#58c070", "public static String style(",
          "TextButtonStyle(Default: (Background: #"):
    assert c not in _page, "0.1.3 custom look left in the 0.1.4 page: " + c
for c in ("flex=", "max_lines=", "spacing=", "trial=True", "%%"):
    assert c not in PAGE_BLOCK, "the page block uses %s" % c
# review 2026-09-29: GuildPage compiles only the kit's colorOf (its textOf would be dead code next to GuildStore.textOf)
assert PAGE_BLOCK.count('SUI.java_status_methods("colorOf", "textOf")[:1]') == 1 and "M(page, _src)" in PAGE_BLOCK
assert '"accentHover"' not in PAGE_BLOCK, "the Admin rank colour is GUILD_RANK_ADMIN (info)"
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
assert s.index("public static String skillKey(String name) {") < s.index("public static synchronized long stepSkills(") \
    < s.index("public static long check(java.util.UUID u) {"), "XpTask: methods before callers"
assert s.index("public static int skillSlot(String lower) {") < s.index("public static String skillKey(String name) {"), "GCfg.skillSlot first"
assert s.index("GUILD_PAGE = guild_page()") < s.index('T["PAGEID"] = GUILD_PAGE_ID') < s.index("ready (@KITID@, page @PAGEID@)")
assert s.index("def guild_view_none():") < s.index("GUILD_PAGE = guild_page()") < s.index('M(page, r"""\npublic void build(@REF@ ref')
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in ident, "UI id with an underscore: " + ident
assert "B.deploy(" not in s and "enable_in_world(" not in s
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.3 had %d; line endings %s)" % (s.count(LF), OLD.count(LF), "CRLF" if NL == CR + LF else "LF"))
