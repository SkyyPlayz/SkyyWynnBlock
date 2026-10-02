"""Derive SkyyCollections/build_skyycollections_0.2.5.py from the LIVE 0.2.4 (build_skyycollections_0.2.4.py = the tools/deploy_set.py
SET pin; 0.2.4 stays untouched; same style as coll_0_2_4_patch.py: rep() / block() with asserted single anchors, newline-agnostic, the
source's line endings kept - LF today). Edit THIS file, never the generated build script (it is overwritten on every run of this patch).
Run:  python tools/coll_0_2_5_patch.py   then   python SkyyCollections/build_skyycollections_0.2.5.py   (never --deploy: coordinated deploy)
Test: python SkyyCollections/test_skyycollections_0.2.5.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.2.5 = SKYY'S RULE "COINS NEVER SKIP COLLECTIONS OR BAGS" (OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02", R3 LOCKED - it replaces the
2026-09-24 coin-bypass lock and bypass.bagMax; R9 build order: "SkyyCollections: coins never buy tiers / recipes / bags"): coins can buy
items you have not unlocked yet on the Auction House / Bazaar, but can NEVER buy a collection tier, a recipe unlock or a bag.
  1. DEFAULT OFF: bypass.enabled defaults to false - in the default config.properties (bypass.enabled=false under the 0.2.5 marker
     comment), in the loader's code default for a missing line (CollReg.loadConfig: p.getProperty("bypass.enabled", "false")), in the
     static field (CollReg.BYPASS = false until the file is read) and in the Server Setup row. REVIEW FIX (0.2.5 review finding 1): the
     loader reads the value like its Server Setup row (the config kit's CfgRows.validate - the same words, trim and toLowerCase):
     new CollReg.onOff (1 = true / on / yes / 1, 0 = false / off / no / 0, -1 = neither) and CollReg.bypassOn = ON only for an ON
     word, anything else OFF (fail-closed), a word that is neither ON nor OFF logged as a WARN (like bypass.bagMax). An admin's
     hand-edited "yes" / "on" / "1" / "True" keeps the meaning it had; "off" / "no" / "0" now read OFF (0.2.4 read anything but
     "false" as on - they sold tiers while Server Setup said OFF, and "set false" answered "already OFF"), and so do an empty value
     and odd words ("flase", "disabled", "false # off"). The other bool rows (auto, bridge.add.felled) keep 0.2.4's reading.
  2. HIDDEN WHILE OFF: CollPage.buildDetail reads CollReg.BYPASS ONCE per build (one volatile read: an admin switching it while a page
     builds can never make a buy-well append miss its parent). Off = no buy well at all: no BUY button (#SkyyCBuy, binding cbuy), no
     "Buy tier X unlocks - N coins" line (#SkyyCBuyLbl), no unlock info and no "Coin unlocks are turned off on this server." line
     (#SkyyCBuyInfo). 0.2.3's "From:" caption #SkyyCFrom stays where it was; the well's 96 px (its 88 px + the 8 px margin) are left
     empty by a plain spacer, so the body is still filled exactly and the footer does not move. On = 0.2.4's statements in 0.2.4's
     order (the harness compares the engine command lists of 0.2.4 and 0.2.5 one to one). No other view reads the switch. A stale page
     (opened while it was on) or a forged cbuy event is refused by 0.2.4's CollBypass.offer, unchanged ("Coin unlocks are turned off
     on this server." on the result line): no coins taken, nothing saved, nothing logged; the rebuilt page has no buy well.
  3. THE SERVER SETUP ROW STAYS (Collections -> Coin unlocks; every other bypass.* row, bypass.bagMax included, is 0.2.4's): an admin
     can turn coin unlocks back on, and ON is 0.2.4's behaviour exactly (the walls, the prices, bagMax, the two-click buy, bypass.log).
     The row now asks before switching ON (confirm=on: "Turn Coin unlocks ON for everyone on this server? <help>"; a part switch used
     to ask only before OFF) and its help names Skyy's rule; switching it off asks nothing. Label, category, flags (live,part,danger:
     the Mods list still shows "Coin unlocks ON / OFF") and the file key are 0.2.4's. Review (finding 3, Skyy's call - kept as is, the
     safe default): ON is a full admin override, bags included - a bought tier may again unlock Normal / Unique bags up to
     bypass.bagMax (unique). bagMax=none is no way out: CollUnlocks.compute uses it to filter the bags of tiers already bought, so it
     would take bought bags back. If Skyy wants "no bags even when ON", a later version adds a separate buy cap (checked only by
     CollBypass buyable / offer, default none) and leaves bagMax to compute.
  4. NO TAKE-BACKS: tiers players already bought stay unlocked - the BOUGHT rows, "(recipes bought up to tier X)", the Unlocked recipes
     view, coll:fn:tier and the coll:recipes publish (CollUnlocks.compute / CollStore.effTier) never read the switch and stay 0.2.4's
     code byte for byte (the harness proves the published lists equal with the switch on and off, on both jars).
  5. ONE-TIME UPDATE of an existing config.properties (new class CollBypassMig, run(base) in setup() right after CollBagMigrate.run and
     BEFORE CollReg.loadAll and CfgPub.start; the SkyySkills 0.4.11 HealMig machinery method for method, reviewed + live): the pure text
     step mgUpdate on the config kit's own parser (CfgFile.isComment / key / value / end / valStart): when the EFFECTIVE bypass.enabled
     line (the last one = what Properties keeps) is a one-line entry holding exactly the old default text "true", every one-line
     bypass.enabled entry holding "true" gets "false" (value text only: key, separator and CR kept). Anything else is kept: an admin's
     value that leaves coin unlocks on (an ON word other than the exact old default: "yes", "on", "1", "True", a continued line ...) is
     kept and logged once as an INFO line; a value already off (REVIEW FIX: CollBypassMig.isOff = "not ON" by CollReg.onOff, the
     loader's own reading - "false" / "off" / "no" / "0" in any case and every other word) is silent; a missing line stays missing
     (the new code default applies: off) and the INFO line says so. The marker comment MG_MARK goes on its own line above the run of comment lines directly on top of the first
     bypass.enabled entry, else at the top of the file; a file holding MG_MARK_ID in a comment line is never touched again (an admin who
     turns coin unlocks back on later keeps it). Before anything is written: the new text must parse (java.util.Properties) to the same
     keys and values except bypass.enabled (else WARN, untouched); CfgHist.snapshot keeps the old file as a History version ("before the
     0.2.5 coin unlocks update") and the rewrite only happens once config-history really holds those bytes (mgSaved; else WARN,
     untouched, the next start retries); CfgRows.atomicWrite (ISO-8859-1 bytes in and out, every other byte and the line endings kept);
     one config-changes.log line in the kit's scalar-row format ("SkyyCollections 0.2.5", via update, bypass.enabled true -> false,
     ok) so Server Setup -> Changes can Undo it. The 0.2.5 default file carries the marker, so a fresh file never updates. Skyy's live
     file (the 0.2 default, LF, bypass.enabled=true, no config-history yet) gets: the marker line + "false".
     Review (findings 2 and 7, accepted as designed): a config.properties that cannot be updated (read-only / locked, or
     config-history unwritable) stays as it is with one WARN and the loader reads it as it stands - an untouched "true" keeps coin
     unlocks ON until a later start can update it (the in-game test checks for the INFO line and no WARN; the kit's atomicWrite may
     leave a config.properties.tmp next to a read-only file); a missing line becomes OFF through the code default with an INFO line
     only (no config-changes.log line, nothing to Undo - Server Setup turns it back on).
  6. Manifest: "coin unlocks for early tiers" dropped from the description.
Everything else - the counting, the rewards and their paid markers, the bag ladder and CollBagMigrate, CollBypass (the coin path, used
again when an admin turns it on), CollUnlocks, coll:fn:where / count / tier / add, every other page view and template, handleDataEvent,
the commands and permissions, every other Server Setup row - is 0.2.4's (asserted below; the harness compares the class bytes).
Harness (re-runnable, commit-ready): SkyyCollections/test_skyycollections_0.2.5.py - 0.2.4 and 0.2.5 side by side in one bare JVM.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.4.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.5.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.4"
LF = "\n"
s = raw.decode("utf8").replace("\r\n", LF)
OLD = s
# the source must be the generated, checked 0.2.4 (the SET pin)
assert 'VERSION = "0.2.4"' in s and "GENERATED by tools/coll_0_2_4_patch.py from the LIVE 0.2.3" in s, "not the live generated 0.2.4"
assert 'COLL_PAGE_CHECKED = "0b8c336ae94b"' in s, "build_skyycollections_0.2.4.py is not the checked 0.2.4 page"
assert "CollBypassMig" not in s and "BUYOFF" not in s and "coll_det_buyoff" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
BIND0 = [ln for ln in s.split(LF) if ln.lstrip().startswith("bind(ev, ")]
EVB0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 17 and len(EVB0) == 1, (len(BIND0), len(EVB0))


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


def block(a, b, text=None):
    """the text from anchor a (included) to anchor b (excluded) of `text` (default: the CURRENT source)"""
    t = s if text is None else text
    assert t.count(a) == 1 and t.count(b) == 1, (a[:60], b[:60])
    i, j = t.index(a), t.index(b)
    assert i < j, (a[:60], b[:60])
    return t[i:j]


# ================================================================================================ blocks that must stay 0.2.4's
KEEP = [
    block("# ================= CollBypass: coins buy the NEXT tier's recipe unlocks only =================",
          "# ================= PlacedStore (copied from SkyySkills 0.3.2)"),                     # the coin path (used when on)
    block("# ================= CollUnlocks: coll:recipes + summary keys",
          "# ================= CollCredit: the one path every counted item takes ================="),  # coll:recipes publish
    block("# ================= CollData / CollStore: per-profile counts",
          "# ================= 0.2.3 CollBagMigrate:"),                                             # boughtTier / effTier / stats
    block("# ================= 0.2.3 CollBagMigrate:", "# ================= CollRewards:"),
    block("# ================= CollRewards:", "# ================= CollUnlocks:"),
    block("# ================= bridge functions: coll:fn:count", "# ================= CollPage: one inline page"),
    block("public static String rewardTextB(", "# ================= CollDrops:"),                       # BOUGHT row texts
    block('COLL_CATCARD_TPL = r"""', 'COLL_DET_TPL = r"""'),                                       # home / category templates
    block('COLL_RC_TPL = r"""', "def coll_look_java():"),                                         # recipes + build templates
    block('M(page, r"""\npublic void closePage(', "# ================= 0.2.2: the admin config kit"),  # handleDataEvent, openFor
    block("# ================= commands (HANDOFF command rules", "# ================= 1 s saver:"),
    block("# ================= 1 s saver:", "# ================= plugin ================="),
]

# ================================================================================================ the 0.2.5 texts (plain ASCII)
MG_MARK_ID = "SkyyCollections 0.2.5 coin unlocks"
MG_MARK = ("# %s (Skyy 2026-10-02): coins never skip collections or bags, so coin unlocks are OFF by default (bypass.enabled false) - "
           "tiers bought before stay unlocked" % MG_MARK_ID)
MG_WHO = "SkyyCollections 0.2.5"
# the help names Skyy's rule in the R9 words; SkyyMenu shows it under the row and the kit appends it to the ON question
ROW_HELP = "Off by default: coins never buy tiers, recipes or bags. On: a Buy button. Bought tiers stay."
assert all(32 <= ord(c) < 127 for c in MG_MARK + MG_WHO + ROW_HELP), "the 0.2.5 texts must be plain ASCII"
# a doc comment: starts "# ", has spaces and no "=" (the kit takes only '#key=value' / '#key:value' with ONE value token for a template line)
assert MG_MARK.startswith("# ") and "=" not in MG_MARK and MG_MARK_ID in MG_MARK
assert '"' not in MG_MARK + ROW_HELP and "\\" not in MG_MARK + ROW_HELP
assert len(ROW_HELP) <= 100, "row help %d > 100 characters (tools/skyycfg.py)" % len(ROW_HELP)
_q = "Turn Coin unlocks ON for everyone on this server? " + ROW_HELP
assert len(_q) <= 200, "the confirm question is clipped at 200: %d" % len(_q)

# ================================================================================================ docstring, Run line, version
OLD_HEAD = '''"""SkyyCollections 0.2.4 - build script (javassist via jpype). GENERATED by tools/coll_0_2_4_patch.py from the LIVE 0.2.3
(build_skyycollections_0.2.3.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.3 was derived from 0.2.2 by
tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written
fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything else
follows research/Collections-Spec.md).

0.2.4 (2026-09-29,'''
CHECKED = '''  CHECKED @@CHECKED@@'''
NEW_HEAD = '''"""SkyyCollections 0.2.5 - build script (javassist via jpype). GENERATED by tools/coll_0_2_5_patch.py from the LIVE 0.2.4
(build_skyycollections_0.2.4.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.4 was derived from 0.2.3 by
tools/coll_0_2_4_patch.py; 0.2.3 from 0.2.2 by tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2
by tools/coll_0_2_1_patch.py; 0.2 was written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command
rules are carried over, everything else follows research/Collections-Spec.md).

0.2.5 (2026-10-02, Skyy's decision - OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02" R3 LOCKED, replacing the 2026-09-24 coin-bypass lock
and bypass.bagMax): COINS NEVER SKIP COLLECTIONS OR BAGS - coins can buy items you have not unlocked yet on the Auction House / Bazaar,
but never a collection tier, a recipe unlock or a bag. Full notes: tools/coll_0_2_5_patch.py.
  - Coin unlocks (the "Buy tier X unlocks - N coins" coin bypass, every bypass.* row incl. bypass.bagMax) are OFF by default:
    bypass.enabled default false (default file, loader code default, static field, Server Setup row). The loader reads a value like
    its Server Setup row (review fix, CollReg.onOff / bypassOn): ON only for true / on / yes / 1 (trimmed, any case), anything else
    OFF - off / no / 0 (ON in 0.2.4) included; a word that is neither ON nor OFF is logged as a WARN.
  - While it is off the collection page shows no buy well at all (no BUY button, no "Buy tier ..." line, no unlock info, no "turned
    off" line): "From:" stays, the well's space is left empty, nothing else on any view changes. A stale page / forged cbuy click is
    refused by 0.2.4's CollBypass.offer ("Coin unlocks are turned off on this server."): no coins taken, nothing saved.
  - The Server Setup row stays (Collections -> Coin unlocks): an admin can turn it back on - ON asks first (confirm=on) and is 0.2.4's
    behaviour exactly; off asks nothing.
  - Tiers players already bought stay unlocked (no take-backs): BOUGHT rows, the Unlocked recipes view and the coll:recipes publish
    are 0.2.4's code and never read the switch.
  - One-time update of an existing config.properties (CollBypassMig.run in setup(), after CollBagMigrate.run, before CollReg.loadAll /
    the config kit; the SkyySkills 0.4.11 HealMig machinery): an effective bypass.enabled line still holding the old default "true"
    becomes "false"; an admin's ON value is kept and logged, a value that already reads OFF is left silent (review fix: the loader's
    reading, CollReg.onOff); a missing line stays missing (code default: off); History version first
    (verified), one config-changes.log line (Server Setup -> Changes -> Undo), runs once (marker comment), every other byte and the
    line endings kept.
  - Manifest description: "coin unlocks for early tiers" dropped.
''' + CHECKED + '''
  UNVERIFIED (needs the game): the detail page with coin unlocks off (the empty band where the buy well was - a plain spacer, a markup
    every view already uses), the Server Setup confirm question when switching Coin unlocks ON (SkyyMenu draws the kit's question).

0.2.4 (2026-09-29,'''
rep(OLD_HEAD, NEW_HEAD)
rep("Run:   python build_skyycollections_0.2.4.py          -> SkyyCollections/SkyyCollections-0.2.4.jar",
    "Run:   python build_skyycollections_0.2.5.py          -> SkyyCollections/SkyyCollections-0.2.5.jar")
rep('VERSION = "0.2.4"', 'VERSION = "0.2.5"')

# ================================================================================================ (1) default OFF: file, field, loader
rep('''CFG = [
    "# SkyyCollections 0.2 settings.''', '''# 0.2.5 (Skyy 2026-10-02, OPEN-QUESTIONS R3 LOCKED): coins never skip collections or bags - coin unlocks are OFF by default. The one-time
# update of an existing config.properties (CollBypassMig) rewrites an untouched bypass.enabled=true once; its marker comment (also in the
# default file below, so a fresh file never updates) is a doc comment with spaces and no "=", which the config kit never takes for a
# "#key=value" template line; CollBypassMig looks for MG_MARK_ID in comment lines only
MG_MARK_ID = "%s"
MG_MARK = "%s"
MG_WHO = "%s"   # the name on the update's config-changes.log line and its History version (a fixed literal)
CFG = [
    "# SkyyCollections 0.2 settings.''' % (MG_MARK_ID, MG_MARK, MG_WHO))
rep('''    "# coin-bypass: buy only the NEXT tier's recipe unlocks (never its coins, XP, score or leaderboard count), one tier at a time",
    "bypass.enabled=true",''', '''    MG_MARK,
    "# coin-bypass: buy only the NEXT tier's recipe unlocks (never its coins, XP, score or leaderboard count), one tier at a time",
    "bypass.enabled=false",''')
rep('"public static volatile boolean BYPASS = true;"', '"public static volatile boolean BYPASS = false;"')
# REVIEW FIX (0.2.5 review finding 1): 0.2.4's loader read anything but "false" as ON - fail-open, and not the config kit's words: with the
# default OFF, "bypass.enabled=off" (no / 0 / an empty value / "flase") sold tiers while Server Setup and the Mods list said OFF, and
# "set false" answered "Coin unlocks is already OFF." The loader now reads the value like its Server Setup row (CfgRows.validate: the
# same words, trim and toLowerCase) and only an ON word turns coin unlocks on. Two CollReg helpers right before loadConfig (methods
# before callers; CollUtil.warn / clip are compiled long before): onOff (also the migration's isOff) and bypassOn (+ the WARN)
rep('''M(reg, r"""
public static String loadConfig() {''', '''# 0.2.5 review fix: a bool setting reads like its Server Setup row (the config kit's CfgRows.validate - the same words, the same trim and
# toLowerCase): 1 = ON (true / on / yes / 1), 0 = OFF (false / off / no / 0), -1 = neither. CollBypassMig.isOff uses it too
M(reg, r"""
public static int onOff(String v) {
  if (v == null) return -1;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return 1;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return 0;
  return -1;
}""")
# 0.2.5 review fix: coin unlocks are ON only for an ON word - off / no / 0 and every other word read OFF (fail-closed: Skyy 2026-10-02,
# coins never skip collections or bags). A word that is neither ON nor OFF is logged (a WARN on each read, like bypass.bagMax's)
M(reg, r"""
public static boolean bypassOn(String v) {
  int r = onOff(v);
  if (r < 0) @PKG@.CollUtil.warn("config.properties: bypass.enabled=" + @PKG@.CollUtil.clip(String.valueOf(v).trim().replace('\\n', ' ').replace('\\r', ' '), 60) + " is not ON or OFF (true, on, yes, 1 / false, off, no, 0) - coin unlocks stay OFF");
  return r == 1;
}""")
M(reg, r"""
public static String loadConfig() {''')
rep('''  BYPASS = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bypass.enabled", "true")).trim());''',
    '''  BYPASS = bypassOn(String.valueOf(p.getProperty("bypass.enabled", "false")));''')

# ================================================================================================ (2) the page: no buy well while off
rep('''/*=BUYROW=*/
  b.set("#SkyyCFrom.Text", "From: " + R.from[c]);
  Object[] o = @PKG@.CollBypass.offer(d, R, c);
  if (o[2] == null) {
    int nt = ((Integer) o[0]).intValue();
    long price = ((Long) o[1]).longValue();
/*=BUYOK=*/
    b.set("#SkyyCBuyLbl.Text", "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins");
    bind(ev, "SkyyCBuy", "cbuy");
    b.set("#SkyyCBuyInfo.Text", @PKG@.CollBypass.unlockText(c, nt));
  } else {
/*=BUYNO=*/
    b.set("#SkyyCBuyInfo.Text", (String) o[2]);
  }
''', '''  boolean buyOn = @PKG@.CollReg.BYPASS;
  if (buyOn) {
/*=BUYROW=*/
  } else {
/*=BUYOFF=*/
  }
  b.set("#SkyyCFrom.Text", "From: " + R.from[c]);
  Object[] o = null;
  if (buyOn) o = @PKG@.CollBypass.offer(d, R, c);
  if (o != null && o[2] == null) {
    int nt = ((Integer) o[0]).intValue();
    long price = ((Long) o[1]).longValue();
/*=BUYOK=*/
    b.set("#SkyyCBuyLbl.Text", "Buy tier " + @PKG@.CollUtil.roman(nt) + " unlocks - " + price + " coins");
    bind(ev, "SkyyCBuy", "cbuy");
    b.set("#SkyyCBuyInfo.Text", @PKG@.CollBypass.unlockText(c, nt));
  } else if (o != null) {
/*=BUYNO=*/
    b.set("#SkyyCBuyInfo.Text", (String) o[2]);
  }
''')
rep('''def coll_det_buyno():
    """Nothing to buy: 0.2.3's refusal text in #SkyyCBuyInfo across the well."""
    return SUI.Appends([("SkyyCBuyRow", SUI.label("SkyyCBuyInfo", "", "default", w=COLL_IW - 2 * SUI.WELL_PAD, h=COLL_BUY_IN,
                                                 align="Center", wrap=True))])
''', '''def coll_det_buyno():
    """Nothing to buy: 0.2.3's refusal text in #SkyyCBuyInfo across the well."""
    return SUI.Appends([("SkyyCBuyRow", SUI.label("SkyyCBuyInfo", "", "default", w=COLL_IW - 2 * SUI.WELL_PAD, h=COLL_BUY_IN,
                                                 align="Center", wrap=True))])


def coll_det_buyoff():
    """0.2.5, coin unlocks OFF (Skyy 2026-10-02: coins never skip collections or bags): no buy well at all. 0.2.3's "From:" caption
    #SkyyCFrom exactly as coll_det_buyrow() appends it, then a plain spacer as tall as the well with its top margin (COLL_BUY_H + 8 =
    96 px), so the body is still filled exactly and the footer stays where it was. No #SkyyCBuy* id, no binding."""
    row = coll_det_buyrow()
    assert [p for p, _m in row] == ["SkyyColl", "SkyyColl"] and "#SkyyCFrom " in SUI.render(row[0][1])
    assert SUI.outer_size(row[1][1]) == (None, COLL_BUY_H + 8), SUI.outer_size(row[1][1])
    ap = SUI.Appends()
    ap.add(row[0][0], row[0][1])
    ap.add("SkyyColl", SUI.spacer(w=COLL_IW, h=COLL_BUY_H + 8))
    return ap
''')
rep('''        put(coll_det_buyrow())
        put(coll_det_buyok() if kw.get("buy", True) else coll_det_buyno())
''', '''        if kw.get("off"):                  # 0.2.5: coin unlocks off - no buy well
            put(coll_det_buyoff())
        else:
            put(coll_det_buyrow())
            put(coll_det_buyok() if kw.get("buy", True) else coll_det_buyno())
''')
rep('''              ("detail", {"tiers": 7, "icon": False, "buy": False}), ("detail", {"tiers": 20}), ("recipes", {"lines": 0}),''',
    '''              ("detail", {"tiers": 7, "icon": False, "buy": False}), ("detail", {"tiers": 20}), ("detail", {"tiers": 10, "off": True}),
              ("detail", {"tiers": 7, "icon": False, "off": True}), ("detail", {"tiers": 20, "off": True}), ("recipes", {"lines": 0}),''')
rep('''    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 2),
    "BUYOK": coll_java(coll_det_buyok(), 4), "BUYNO": coll_java(coll_det_buyno(), 4),''',
    '''    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 4),
    "BUYOFF": coll_java(coll_det_buyoff(), 4), "BUYOK": coll_java(coll_det_buyok(), 4), "BUYNO": coll_java(coll_det_buyno(), 4),''')
# the page id the harness last passed on, and the harness / patch named in the page-check messages
PAGE_CHECKED = "be0dca34bcb2"   # = COLL_PAGE_ID the harness SkyyCollections/test_skyycollections_0.2.5.py passed on
rep('COLL_PAGE_CHECKED = "0b8c336ae94b"', 'COLL_PAGE_CHECKED = "%s"' % PAGE_CHECKED)
rep("# ---- COLL PAGE BLOCK START (SkyyCollections/test_skyycollections_0.2.4.py execs this block with SUI verified; needs UI_DATA_COLORS)",
    "# ---- COLL PAGE BLOCK START (SkyyCollections/test_skyycollections_0.2.5.py execs this block with SUI verified; needs UI_DATA_COLORS)")
rep("# harness SkyyCollections/test_skyycollections_0.2.4.py last passed on (tools/coll_0_2_4_patch.py PAGE_CHECKED)",
    "# harness SkyyCollections/test_skyycollections_0.2.5.py last passed on (tools/coll_0_2_5_patch.py PAGE_CHECKED)")
rep("the page SkyyCollections/test_skyycollections_0.2.4.py last passed on", "the page SkyyCollections/test_skyycollections_0.2.5.py last passed on", 3)
rep("in tools/coll_0_2_4_patch.py and regenerate", "in tools/coll_0_2_5_patch.py and regenerate", 2)

# ================================================================================================ (3) the Server Setup row
rep('''    ("bypass.enabled", "Coin unlocks", "bypass", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: the Buy button says coin unlocks are turned off. Tiers already bought stay unlocked.",
     "reload@config.properties:bypass.enabled"),''', '''    # 0.2.5 (Skyy 2026-10-02: coins never skip collections or bags): default OFF; switching it ON asks first (confirm=on), off asks nothing
    ("bypass.enabled", "Coin unlocks", "bypass", "bool", "false", "", "", "", "", "live,part,danger",
     "%s",
     "reload@config.properties:bypass.enabled;confirm=on"),''' % ROW_HELP)

# ================================================================================================ (5) CollBypassMig: the one-time update
rep('''bmig = K("CollBagMigrate")   # 0.2.3: rewards.properties bag lines -> the rarity ladder (once)
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, rew,''', '''bmig = K("CollBagMigrate")   # 0.2.3: rewards.properties bag lines -> the rarity ladder (once)
bpm = K("CollBypassMig")     # 0.2.5: an untouched bypass.enabled=true -> false in config.properties (once; methods after the config kit)
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, bpm, rew,''')
MIG = r'''# ================= 0.2.5 CollBypassMig: the one-time coin unlocks update of an existing config.properties (Skyy 2026-10-02) =================
# setup() only, right after CollBagMigrate.run and BEFORE CollReg.loadAll and CfgPub.start. The SkyySkills 0.4.11 HealMig machinery method
# for method (reviewed + live; SkyyClasses 0.1.10 migrate0110 / SkyyGear 0.1.1 before it): pure text step mgUpdate on the config kit's own
# parser (CfgFile.isComment / key / value / end / valStart), a Properties check (only bypass.enabled may differ), CfgHist.snapshot + mgSaved
# (no rewrite unless config-history really holds the old bytes), CfgRows.atomicWrite, one config-changes.log line (Server Setup -> Changes
# -> Undo), one INFO line (+ one per kept admin value). Plain java.* + the kit's classes: a bare JVM runs it on scratch copies.
def _jlit(x):
    assert '"' not in x and "\\" not in x and "\n" not in x, x
    return '"' + x + '"'
for _d in ('public static final String[] MG_KEY = new String[] { "bypass.enabled" };',
           'public static final String[] MG_OLD = new String[] { "true" };',
           'public static final String[] MG_NEW = new String[] { "false" };',
           "public static final String MG_MARK = %s;" % _jlit(MG_MARK),
           "public static final String MG_MARK_ID = %s;" % _jlit(MG_MARK_ID),
           "public static final String MG_WHO = %s;" % _jlit(MG_WHO)):
    F(bpm, _d)
assert "bypass.enabled=false" in CFG and CFG.index(MG_MARK) == CFG.index("bypass.enabled=false") - 2, "the default file carries the marker"
M(bpm, r"""
public static int mgIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < MG_KEY.length; i++) if (MG_KEY[i].equals(k)) return i;
  return -1;
}""")
# the loader's reading (review fix: CollReg.onOff, = the Server Setup row): coin unlocks are ON only for an ON word (true / on / yes / 1,
# trimmed, any case) - so a value is already off unless it is an ON word: false / off / no / 0 and every other word are silent here, and
# only a real ON value is kept and logged ("coin unlocks stay ON")
M(bpm, r"""
public static boolean isOff(String v) {
  return @PKG@.CollReg.onOff(v) != 1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line
# (nothing to do). Else { new text, "bypass.enabled true -> false" or "", String[] kept notes, String[] { key, old, new }*, Boolean missing }.
# The key whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the old text "true" is updated: every
# one-line entry of it holding "true" gets "false" (value text only: key, separator and CR stay). Anything else is kept: a value that
# leaves coin unlocks on (an ON word: noted), a value already off (isOff: silent), a missing line (missing = true). Marker: on its own line above the first
# bypass.enabled entry - above the whole run of comment lines directly on top of it - else above line 0. Lines are scanned from the start
# of a logical line, so a continued entry's tail is never taken for a comment. Never throws for any text.
M(bpm, r"""
public static Object[] mgUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MG_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MG_MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int m = mgIdx(@PKG@.CfgFile.key(s));
    if (first < 0 && m >= 0) { first = k; above = run >= 0 ? run : k; }
    if (m >= 0) {
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    run = -1;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  boolean missing = false;
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) { missing = true; continue; }
    if (!multi[i] && eff[i].equals(MG_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(MG_KEY[i]).append(' ').append(MG_OLD[i]).append(" -> ").append(MG_NEW[i]);
      rows.add(MG_KEY[i]);
      rows.add(MG_OLD[i]);
      rows.add(MG_NEW[i]);
    } else if (!isOff(eff[i])) {
      kept.add(MG_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (an admin's value: coin unlocks stay ON on this server) - the 0.2.5 default is " + MG_NEW[i] + " (Skyy 2026-10-02: coins never skip collections or bags; Server Setup -> Collections -> Coin unlocks)");
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = mgIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(MG_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + MG_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MG_MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MG_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]), Boolean.valueOf(missing) };
}""")
# the update may change nothing but bypass.enabled: both texts as java.util.Properties - same keys, same values, the updated key exactly its
# new value (a marker line can never change a value; this guards the parser corner cases)
M(bpm, r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] rows) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (a.size() != b.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      for (int i = 0; i + 2 < rows.length; i += 3) if (rows[i].equals(k)) want = rows[i + 2];
      String got = b.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""")
M(bpm, r"""
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/config.properties")) return k;
  return -1;
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyCollections)
M(bpm, r"""
public static void mgKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.CollUtil.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds a copy with exactly these
# bytes (the new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log
M(bpm, r"""
public static boolean mgSaved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
M(bpm, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + MG_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(): the file before this update becomes a History version (KEEP 20, verified by mgSaved before the rewrite), the new text is written
# with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line for the updated key, one INFO line (+ one per kept value). Returns the
# INFO line(s) joined by \n ("" = nothing done: no file - CollReg.loadConfig writes the 0.2.5 default with the marker -, marker already
# there, or a failure - WARN, file untouched, retried at the next start)
M(bpm, r"""
public static synchronized String run(java.nio.file.Path base) {
  if (base == null) return "";
  java.nio.file.Path f = base.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] rows = (String[]) r[3];
    if (!sameAfter(old, data, rows)) {
      @PKG@.CollUtil.warn("config.properties NOT updated for the 0.2.5 coin unlocks: the update would change more than the bypass.enabled line (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), MG_WHO, "before the 0.2.5 coin unlocks update");
    if (!mgSaved(fi, old)) {
      @PKG@.CollUtil.warn("config.properties NOT updated for the 0.2.5 coin unlocks: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    boolean missing = ((Boolean) r[4]).booleanValue();
    String msg = null;
    if (chg.length() > 0) msg = "config.properties: coin unlocks are OFF now (Skyy 2026-10-02: coins never skip collections or bags): " + chg + " (the old file is in config-history; Server Setup -> Changes can undo it; tiers bought before stay unlocked)";
    else if (missing) msg = "config.properties has no bypass.enabled line: coin unlocks follow the 0.2.5 default - OFF (0.2.5 coin unlocks marker added; the old file is in config-history)";
    else if (kept.length > 0) msg = "config.properties: bypass.enabled holds an admin's value - kept, coin unlocks stay ON (0.2.5 coin unlocks marker added; the old file is in config-history)";
    else msg = "config.properties: bypass.enabled was already off - no value changed (0.2.5 coin unlocks marker added; the old file is in config-history)";
    @PKG@.CollUtil.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.CollUtil.info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.CollUtil.warn("could not update config.properties for the 0.2.5 coin unlocks (the file is used as it is): " + t);
    return "";
  }
}""")

'''
rep("# ================= plugin =================\n", MIG + "# ================= plugin =================\n")

# ================================================================================================ setup(): run the update, the ready line
rep('''  String bm = @PKG@.CollBagMigrate.run(base);
  String s = @PKG@.CollReg.loadAll();''', '''  String bm = @PKG@.CollBagMigrate.run(base);
  String cm = @PKG@.CollBypassMig.run(base);   // 0.2.5: an untouched bypass.enabled=true -> false (once; History first; Undo in Server Setup)
  String s = @PKG@.CollReg.loadAll();''')
READY_OLD = '''log("[SkyyCollections] 0.2.4 ready (""" + KIT_ID + ", page " + COLL_PAGE_ID + r""") - item collections, Magic Bag unlocks by rarity, /collections, admin settings in SkyWynn Menu -> Server Setup (/modconfig); migration + recipe check run at start; " + s + "; " + bm + (bb.length() > 0 ? "; " + bb : ""));'''
READY_NEW = '''log("[SkyyCollections] 0.2.5 ready (""" + KIT_ID + ", page " + COLL_PAGE_ID + r""") - item collections, Magic Bag unlocks by rarity, /collections, admin settings in SkyWynn Menu -> Server Setup (/modconfig); migration + recipe check run at start; " + s + "; " + bm + (bb.length() > 0 ? "; " + bb : "") + (cm.length() > 0 ? "; " + cm.replace('\\n', ' ') : ""));'''
rep(READY_OLD, READY_NEW)

# ================================================================================================ (6) manifest
rep("including the Magic Bag rarities (Mining bags from Iron Ore); coin unlocks for early tiers; leaderboards.",
    "including the Magic Bag rarities (Mining bags from Iron Ore); leaderboards.")

# ================================================================================================ CHECKED (what the harness proved)
# every claim is what the COMMITTED harness SkyyCollections/test_skyycollections_0.2.5.py checks - re-run it instead of trusting this
CHECKED_TEXT = '''with SkyyCollections/test_skyycollections_0.2.5.py (committed; re-run it: python SkyyCollections/test_skyycollections_0.2.5.py) -
    2026-10-02 (after the review fix), kit skyyui 1.4 ac93356c4c60, page be0dca34bcb2, 37330 checks, 0 fails (the same harness on
    the pre-fix jar, its direct onOff probe skipped: 198 fails - B, C, E4 and M catch finding 1); one JVM with -Xverify:all,
    HytaleServer.jar, 0.2.4 and 0.2.5 each in its own class loader (a fresh 0.2.5 loader per server start): A all 47 / 48 classes
    load, verify and initialise. B 42 classes
    byte-identical, CfgFn version constants only; method level only CollReg <clinit> (exactly BYPASS true -> false), loadConfig
    (exactly the bypass.enabled statement: now bypassOn(String.valueOf(getProperty("bypass.enabled", "false"))), every other
    instruction and try range the same), configText + the new CollReg onOff / bypassOn (nothing else added), CollPage buildDetail,
    SkyyCollectionsPlugin setup, CfgRows <clinit> (+ header version only); new CollBypassMig. C statusColor on 16 result texts;
    configText = 0.2.4's + the marker + false; the static default off; loadConfig on 33 files: 0.2.5 reads ON exactly when the
    config kit's own CfgRows.validate (Server Setup) does - 11 files; 0.2.4 read 20 of them differently (no line, off / no / 0 in any
    case, a tab / spaces, a continued "off", empty, odd words), all OFF now; one WARN (one line, clipped) for each of the 10 words
    that are neither ON nor OFF, none otherwise; every other setting reads the same on both jars; CollBypassMig.isOff = not ON.
    D 810 page builds (202 on + 203 off states x 2 jars) through the engine's UICommandBuilder / UIEventBuilder on the real registry:
    ON every command list, binding and page state identical to 0.2.4 (37436 commands); OFF identical except the 128 collection
    views = 0.2.4 minus the buy well (the 96 px spacer, no cbuy); no OFF page shows a buy / coin-unlock text (the scan finds 0.2.4's
    line), the BOUGHT rows stay; 12083 markups in 242 distinct pages through check_markup / check_page / assert_proven, 1951 layout
    checks. E 170 clicks: ON the 0.2.4 sequences identical (page, purse, counts file, bypass.log); OFF 5 forged Buy clicks refused,
    purse and files unchanged; an admin turning it on through the kit (asked first) gets 0.2.4's buy exactly, off again hides it;
    E4 hand-edited off / no / 0 / OFF / flase / empty value: the loader and the kit read OFF, no buy well, 24 forged clicks refused
    (no coins, nothing saved), "set false" = already OFF, "set true" asks first (0.2.4 read off / no / 0 as ON). K 28 rows: only
    bypass.enabled changed (default false, help, confirm=on); get / set / export through the kit. M CollBypassMig on scratch copies
    of Skyy's live folder (start 1: the marker + false, History = the old bytes, 1 Undo line; start 2 nothing; Undo -> true
    sticks), 21 edited files twice each (on / 1 / yes / True / a continued true kept and logged; off / no / 0 / OFF / flase / an
    empty value / a last "off" line silent), history unwritable (retried), a value Properties cannot read (untouched), a fresh
    folder. U coll:recipes identical on both jars with the switch on and off (13 / 14 ids, bagMax unique / legendary). F 884 texts
    fit (NunitoSans). G the page id in the jar = the kit's page now = COLL_PAGE_CHECKED.'''
rep("@@CHECKED@@", CHECKED_TEXT)

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "registrations changed"
assert [ln for ln in s.split(LF) if ln.lstrip().startswith("bind(ev, ")] == BIND0, "the bind(ev, ...) calls changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == EVB0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.2.4's changed: %s" % k[:80]
assert s.count("@PKG@.CollReg.BYPASS") == 2, "BYPASS is read by CollBypass.offer and CollPage.buildDetail only"
assert s.count("CollBypassMig.run(base)") == 1 and s.index("CollBagMigrate.run(base)") < s.index("CollBypassMig.run(base)") \
    < s.index("String s = @PKG@.CollReg.loadAll();") < s.index("@PKG@.CfgPub.start(")
assert s.index("kit = SCFG.emit(") < s.index("public static synchronized String run(java.nio.file.Path base)") < s.index("public void setup()")
assert s.index("MG_MARK = ") < s.index("CFG = [") and 'MG_MARK,\n    "# coin-bypass:' in s
# review fix: the loader and the migration read bypass.enabled through CollReg.onOff (defined before both callers); the other bool rows
# (auto, bridge.add.felled) keep 0.2.4's reading
_code = s[s.index('"""', 3) + 3:]          # the script after its docstring (the CHECKED text names the call)
assert _code.count("public static int onOff(String v)") == 1 and _code.count("public static boolean bypassOn(String v)") == 1
assert _code.count("bypassOn(") == 2 and _code.count("onOff(v)") == 2 and _code.count("@PKG@.CollReg.onOff(v) != 1") == 1
assert s.index("public static int onOff(String v)") < s.index("public static boolean bypassOn(String v)") < s.index("public static String loadConfig()")
assert s.count('  BYPASS = bypassOn(String.valueOf(p.getProperty("bypass.enabled", "false")));') == 1
assert '  AUTO = "true".equalsIgnoreCase(String.valueOf(p.getProperty("auto", "false")).trim());' in s
assert '  boolean felled = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bridge.add.felled", "true")).trim());' in s
# every 0.2.4 line is still there except the ones this patch replaced on purpose (a guard against a stray edit)
_gone = [ln for ln in set(OLD.split(LF)) if ln not in set(s.split(LF))]
_ALLOWED_GONE = {
    '"""SkyyCollections 0.2.4 - build script (javassist via jpype). GENERATED by tools/coll_0_2_4_patch.py from the LIVE 0.2.3',
    "(build_skyycollections_0.2.3.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.3 was derived from 0.2.2 by",
    "tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written",
    "fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything else",
    "follows research/Collections-Spec.md).",
    "Run:   python build_skyycollections_0.2.4.py          -> SkyyCollections/SkyyCollections-0.2.4.jar",
    'VERSION = "0.2.4"',
    '    "bypass.enabled=true",',
    '          "public static volatile boolean BYPASS = true;", "public static volatile double BYP_MULT = 5.0;",',
    '  BYPASS = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("bypass.enabled", "true")).trim());',
    "  Object[] o = @PKG@.CollBypass.offer(d, R, c);",
    "  if (o[2] == null) {",
    "  } else {",
    "        put(coll_det_buyrow())",
    '        put(coll_det_buyok() if kw.get("buy", True) else coll_det_buyno())',
    '              ("detail", {"tiers": 7, "icon": False, "buy": False}), ("detail", {"tiers": 20}), ("recipes", {"lines": 0}),',
    '    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 2),',
    '    "BUYOK": coll_java(coll_det_buyok(), 4), "BUYNO": coll_java(coll_det_buyno(), 4),',
    'COLL_PAGE_CHECKED = "0b8c336ae94b"',
    "# ---- COLL PAGE BLOCK START (SkyyCollections/test_skyycollections_0.2.4.py execs this block with SUI verified; needs UI_DATA_COLORS)",
    "# harness SkyyCollections/test_skyycollections_0.2.4.py last passed on (tools/coll_0_2_4_patch.py PAGE_CHECKED)",
    '    print("collections page %s = the page SkyyCollections/test_skyycollections_0.2.4.py last passed on" % COLL_PAGE_ID)',
    '    raise SystemExit("collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.4.py last passed on (%s) and "',
    '                     "in tools/coll_0_2_4_patch.py and regenerate" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))',
    '    print("WARNING: collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.4.py last passed on (%s): the kit "',
    '          "output changed the page. Run the harness, then set PAGE_CHECKED in tools/coll_0_2_4_patch.py and regenerate; never deploy "',
    '    ("bypass.enabled", "Coin unlocks", "bypass", "bool", "true", "", "", "", "", "live,part,danger",',
    '     "Off: the Buy button says coin unlocks are turned off. Tiers already bought stay unlocked.",',
    '     "reload@config.properties:bypass.enabled"),',
    "ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy,",
}
_gone_other = sorted(ln for ln in _gone if ln not in _ALLOWED_GONE and "0.2.4 ready" not in ln and "coin unlocks for early tiers" not in ln)
assert not _gone_other, "0.2.4 lines lost by accident: %s" % _gone_other[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2.4 had %d)" % (s.count(LF), OLD.count(LF)))
