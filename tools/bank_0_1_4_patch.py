"""Derive SkyyBank/build_skyybank_0.1.4.py from the LIVE 0.1.3 (build_skyybank_0.1.3.py = the tools/deploy_set.py SET pin).
Run:  python tools/bank_0_1_4_patch.py   then   python SkyyBank/build_skyybank_0.1.4.py   (never --deploy: coordinated deploy)
SkyyBank uses patch scripts from 0.1.4 on (0.1.1 - 0.1.3 were copy + edit): edit THIS file, never the generated build script.

0.1.4 = the vanilla UI pass, PILOT of the shared kit tools/skyyui.py (Skyy 2026-09-28: "the new goal for any and all UI added in the
game is for them to look and feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md section 7 "Restyling an
existing page"; research/Skyy-UI-Inventory.md 5.3). Regenerated on kit 1.3 with the pilot review applied (2026-09-29; never
deployed, so the version stays 0.1.4). ONLY THE LOOK OF BankPage CHANGES:
  - the generated script imports skyyui as SUI and calls SUI.verify() before anything else (every vanilla value proven against
    Assets.zip at every build), and puts SUI.kit_id() into the ready log line;
  - BankPage.style() (the custom TextButtonStyle triple) is gone; BankPage.colorOf / textOf become the kit's java_status_methods()
    (same names and signatures; "+" / "-" / "=" in the vanilla success / error / info-blue colours, SUI.STATUS);
  - BankPage.build() keeps 0.1.3's Java prelude and its 7 event bindings VERBATIM (cut out of 0.1.3 by this patch, not retyped) and
    replaces only the markup: a Python function bank_page() in the generated script builds the page from kit calls (page_shell,
    panel "well", label kinds, text_field, button kinds, group, spacer, status_line, separator) and emits the Java with the kit's
    emitters when the BUILD runs (kit fixes reach the page on its next build);
  - review finding 3: only vanilla spacing steps (4 / 6 / 8 / 10 / 12 / 16 px margins, 172 px buttons), no FlexWeight, the page
    height = the sum of its parts (asserted); finding 6: the profile line wraps (two lines); finding 7: the payout line is
    green only for a real payout, label grey for hints, red when the account is unreadable; finding 8: the page code below goes
    into the generated script by @@TOKEN@@ replacement (research/Vanilla-UI-Style-Guide.md 8c), no % template.
  - review 2 (2026-09-29, still never deployed, so still 0.1.4): 1 the payout colour asks a Java helper payoutOn() made from
    gainText()'s own branches, not a text prefix; 2 Deposit all / Withdraw all 200 px wide (WITHDRAW ALL no longer needs
    ShrinkTextToFit); 3 #SkyyBSub / #SkyyBInfo 46 px (two lines with 2 px to spare; page 1100 x 593); 5 the committed harness
    SkyyBank/test_skyybank_0.1.4.py replaces the deleted scratch harness and the CHECKED text says what it checks; 6 BANK_PAGE_ID
    (a hash of the kit-emitted page code) in the ready log line + PAGE_CHECKED below, a build warns and the harness fails when a
    kit change alters the page; kit gap: bank_page() reads each element's outer size back out of the markup (no hand-typed
    margins in the height budget).
Everything else (commands, permissions, BankStore, BankConfig, BankTick, BankJob, texts, amounts, files, bridge keys, jsonStr, typed,
handleDataEvent, openPage) is byte-identical to 0.1.3 - asserted below.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBank", "build_skyybank_0.1.3.py")
dst = os.path.join(ROOT, "SkyyBank", "build_skyybank_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
REG0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
assert len(BIND0) == 7, "0.1.3 has 7 event bindings, found %d" % len(BIND0)
assert "@@" not in s, "0.1.3 already holds a @@ token"


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
    """@@NAME@@ replacement (research/Vanilla-UI-Style-Guide.md 8c): every token of `values` occurs exactly once in the template,
    no value holds a token or "@@" (the build scripts' own @PKG@ / @UCB@ tokens are single-@), and no token is left over."""
    for name, value in values.items():
        tok = "@@%s@@" % name
        assert template.count(tok) == 1, "token %s occurs %d times" % (tok, template.count(tok))
        assert "@@" not in value, "the value for %s holds '@@'" % tok
        template = template.replace(tok, value)
    left = TOKEN_RE.findall(template)
    assert not left, "tokens left unfilled: %s" % left
    return template


# blocks that must come out of this patch byte-identical (everything but the BankPage look + header / version / log line)
KEEP = [block("# ================= BankStore =================", "# ================= BankPage (0.1.3; inline"),
        block("# one string value out of the page event JSON", "PM(r\"\"\"\npublic static String colorOf(String res) {"),
        block("# 2475000 ms -> \"41 min 15 s\"; 7500000 -> \"2 h 5 min\"", "PM(r\"\"\"\npublic void build(@REF@ ref"),
        block("# clicks run on the player's world thread (page events)", "# ================= plugin ================="),
        block("for c in (bs, cfg, tick, job, cmd, cmdA, cmdN, adm, admS, admM, page, pl):", "m = B.manifest(")]

# review finding 7: #SkyyBGain is green only for a payout. Review 2 finding 1 (2026-09-29): the colour is NOT picked from the text
# gainText() returns (a prefix test broke silently on any rewording); it asks a new Java helper payoutOn() next to gainText(), built
# here from gainText()'s own branches: unreadable -> false, interest off -> false, then gainText()'s principal / gain lines copied
# verbatim, a payout = gain > 0. The structure it mirrors is asserted on 0.1.3's (unchanged) gainText, and
# SkyyBank/test_skyybank_0.1.4.py proves at run time that payoutOn() is true exactly when gainText() returns its payout line.
_g = re.search(r'public static String gainText\(boolean readable, long bank, int pct, long max\) \{\n(.*?)\n\}"""\)', s, re.S)
assert _g, "0.1.3 gainText not found"
_rets = re.findall(r"return (.*?);\n", _g.group(1) + "\n")
assert len(_rets) == 5, _rets
assert _rets[0].startswith('"Your bank account cannot be read'), "the first gainText return is the unreadable account"
_gl = _g.group(1).split(LF)
assert len(_gl) == 8, _gl
assert _gl[0].startswith('  if (!readable) return "') and _gl[1].startswith('  if (pct <= 0) return "'), _gl[:2]
assert _gl[2] == "  long principal = bank < max ? bank : max;" and _gl[3] == "  long gain = principal * (long) pct / 100L;", _gl[2:4]
assert _gl[4].startswith('  if (gain > 0L) return "Your next payout: +" + fmt(gain)'), _gl[4]
assert all("return" not in ln or ln.startswith(("  if (bank <= 0L) return ", "  return ")) for ln in _gl[5:]), _gl[5:]
PAYOUT_SRC = LF.join(["public static boolean payoutOn(boolean readable, long bank, int pct, long max) {",
                      "  if (!readable) return false;",
                      "  if (pct <= 0) return false;",
                      _gl[2],
                      _gl[3],
                      "  return gain > 0L;",
                      "}"])

# ================================================================================================ docstring
HEAD_OLD = '''"""SkyyBank 0.1.3 - build script (javassist via jpype).
Run:   python build_skyybank_0.1.3.py            -> SkyyBank/SkyyBank-0.1.3.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
SkyBlock-style bank: /bank (opens the bank page, 0.1.3), /bank balance, /bank status, /bank deposit <n|all|2k|1.5m>,
/bank withdraw <n|all>.

'''
HEAD_NEW = '''"""SkyyBank 0.1.4 - build script (javassist via jpype). GENERATED by tools/bank_0_1_4_patch.py from the LIVE 0.1.3
(build_skyybank_0.1.3.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyybank_0.1.4.py            -> SkyyBank/SkyyBank-0.1.4.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
SkyBlock-style bank: /bank (opens the bank page, 0.1.3), /bank balance, /bank status, /bank deposit <n|all|2k|1.5m>,
/bank withdraw <n|all>.

0.1.4 (2026-09-29, the vanilla UI pass - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and
feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md): the PILOT restyle on the shared kit tools/skyyui.py,
regenerated on kit 1.3 with the pilot review applied (never deployed, so the version stays 0.1.4).
  ONLY THE LOOK OF THE BANK PAGE CHANGED. Commands, permissions, chat texts, amounts, the coins bridge, profiles, interest, files,
  the bridge key bank:<uuid>, every element id of 0.1.3, every b.set target and value, the TextField #SkyyBAmount and its @BAmount
  payload, the 7 event bindings (copied out of 0.1.3 by the patch, not retyped) and the page logic (jsonStr, typed, handleDataEvent:
  Enter never moves coins, keepAmount, rebuilt only after a click, Close = CustomUIPage.close()) are 0.1.3's; the patch asserts it.
  - The build calls SUI.verify() first: every vanilla style value, texture and sound the page uses is proven against Assets.zip
    (read-only) at every build, and a game update that changes one stops the build. KIT_ID (kit version + file hash) is in the ready
    log line. bank_page() runs the kit when this script runs, so a kit fix reaches the page on its next build.
  - Window: the vanilla decorated container (page_shell: the ContainerHeader title bar with its runes and the two gold ornaments, the
    title BANK in the vanilla title style - 15 px Secondary, bold, uppercase, no LetterSpacing, like the deployed SkyyRanks 0.1.1 /
    SkyyVault 0.1.3 titles - and the ContainerPatch body with the container padding 17). The page root is the new #SkyyBankF
    (Anchor Width / Height only, 1100 x 593 - 0.1.3 was 1100 x 680 without a frame; the body is 1066 x 521 inside the frame);
    0.1.3's root #SkyyBank is now the body, so every appendInline target "#SkyyBank" is unchanged. Gone: the dark-blue root panel,
    the gold accent stripe, the big custom title label (the frame title replaces them) and the empty Label spacers.
  - Spacing (pilot review finding 3): only the vanilla steps - Anchor margins of 4 / 6 / 8 / 10 / 12 / 16 px, buttons 172 px wide
    (@DefaultButtonMinWidth) except the two "all" buttons (200 px, below), the wells' own padding 8. No FlexWeight (a "base" probe
    property no deployed Skyy page uses yet): the page height is the sum of its parts. bank_page() reads every element's outer size
    (Width / Height + its Anchor margins) back out of the kit markup and asserts that the body column, each row and each well is
    filled exactly (review 2 kit gap: no hand-typed "+ 12" next to an anchor), and that every Anchor margin it writes is one of
    those steps (plus the 3 px that centres the 38 px text field on the 44 px button row). Where vanilla would use FlexWeight the
    page uses the width it works out to: the amount box takes the rest of the controls row (the InstanceListPage search field),
    and the gap between Refresh and Close is an empty Group, the flex spacer of the WorldEventPanelPage #Footer, with that
    footer's 4 px button margins.
  - Profile line #SkyyBSub (review finding 6): the vanilla wrapped message style (16 px, centred, Wrap true - PrefabEditorExitConfirm,
    the SkyyVault 0.1.3 dialog message), 46 px high = two lines of the game font (2 x 16 x 1.364 = 43.7 px) with 2 px to spare
    (review 2 finding 3: 44 px left no slack), so a long profile name + class wraps instead of being clipped. The text is 0.1.3's
    subText(u).
  - Purse / Bank (#SkyyBPurseBox / #SkyyBBankBox in #SkyyBBal): two vanilla wells (the translucent black inset of WorldEventPanelPage
    #Summary, padding 8) 12 px apart, each with a centred subtitle (the vanilla @Subtitle: 15 px bold uppercase, bottom 10: PURSE /
    BANK), the number (#SkyyBPurse / #SkyyBBalance) in the kit display style (32 px in the Default font, the Hud/TimeLeft timer) and
    a grey caption.
  - Interest (#SkyyBInt): one well with the rate line in the vanilla heading style (18 px bold; one line, no Wrap / WrapMaxLines),
    the next-payout time in the default label style and the payout line #SkyyBGain (16 px bold) coloured by what it says (review
    finding 7): the vanilla success green only for "Your next payout: +N coins", the default label grey for the hints (interest
    switched off, deposit coins to start earning, deposit at least N coins), the vanilla error red when the account file cannot be
    read. The texts are 0.1.3's gainText(). The colour asks the new static helper BankPage.payoutOn(readable, bank, pct, max)
    (review 2 finding 1): gainText()'s own branches, its principal / gain lines copied verbatim by the patch, true = a payout; it
    no longer tests the text for a "Your next payout" prefix, so a rewording cannot turn the line grey. The harness checks
    payoutOn() == "gainText() returned its payout line" on a grid of balances, rates and caps.
  - Controls (#SkyyBCtl, same order): Deposit all | Amount | Deposit | Withdraw | Withdraw all, 16 px between the three groups and
    6 px inside the middle one. Deposit all + Deposit = vanilla Primary buttons (gold), Withdraw + Withdraw all = vanilla Secondary;
    every button has the vanilla hover / press / disabled textures and the vanilla ButtonsLight sounds. Deposit all and Withdraw
    all are 200 px wide (review 2 finding 2): "WITHDRAW ALL" at 17 px bold is about 142 px, more than the 124 px of label room a
    172 px button leaves (2 x 24 px padding), so at 172 it only fitted by ShrinkTextToFit (not yet seen in game) and read smaller
    than its neighbours; 200 px gives 152 px of room (vanilla buttons grow to their label, MinWidth 172). The amount box is the
    vanilla text field (InputBox.png) around #SkyyBAmount, 16 px (the kit look), 278 px wide. Captions under the controls (top 4)
    in the vanilla caption grey, each as wide as its control group.
  - Result line #SkyyBInfo: the kit status line (16 px bold, centred, wraps to two lines, top 12; 46 px high like #SkyyBSub):
    done = vanilla success green, refused = vanilla error red, info (=) = the vanilla info blue #7caacc (BarterPage #RefreshTimer;
    kit 1.3). The chat hint line is a vanilla caption.
  - Footer: the vanilla content separator (1 px, 8 px above and below), then Refresh (Secondary) on the left and Close (Secondary with
    the vanilla cancel sound) on the right, like WorldEventPanelPage's footer. Esc still closes the page (CanDismiss).
  - Uses only what deployed Skyy pages already use inline (LayoutMode Top / Left, fixed widths, Anchor margins, Wrap, the vanilla
    button / input textures, inline Sounds and the title bar of SkyyRanks 0.1.1 / SkyyVault 0.1.3): no WrapMaxLines, LetterSpacing,
    FlexWeight or LayoutMode Center / Right, and no UNVERIFIED (trial) kit element.
  - Kit additions made for this page (skyyui 1.2, tested in tools/skyyui_test.py): group() (a plain layout row / column) and
    status_line(wrap=, max_lines=, anchor=).
  - Page id (review 2 finding 6): the build hashes every piece of BankPage the KIT emits (the build() markup Java and the kit's
    colorOf / textOf) into BANK_PAGE_ID and writes it into the ready log line next to KIT_ID ("ready (skyyui 1.3 <blob>, page
    <id>)"). BANK_PAGE_CHECKED is the page id SkyyBank/test_skyybank_0.1.4.py last passed on (set in tools/bank_0_1_4_patch.py);
    a build whose page differs (a later kit change) prints a WARNING, and the harness fails, until the new page is checked. Rebuild
    right before the coordinated deploy and compare the page id in the log; once 0.1.4 is deployed it is frozen - any later page
    change is a new version with a new patch.
@@CHECKED@@
  UNVERIFIED (needs the game): the whole new look - the kit's "base" look has not been seen in game yet (skyyui probe pages base1,
    base2 and base3: frame + ornaments, button textures / inline Sounds / Disabled state / ShrinkTextToFit, the well, the text
    field, the display number). This page has no runtime fallback: a parse error disconnects on /bank and on the SkyyMenu Bank
    tile. It goes into a test deploy only after Skyy has opened probe pages base1, base2 and base3 cleanly; keep the SET pin at
    0.1.3 until Skyy has seen this page in game.

'''
# what the 0.1.4 build was checked with (review 2 finding 5: every claim here is what the COMMITTED harness
# SkyyBank/test_skyybank_0.1.4.py checks - re-run it, do not trust this text; kept here so a regeneration keeps it)
CHECKED = '''  CHECKED with SkyyBank/test_skyybank_0.1.4.py (committed; re-run it: python SkyyBank/test_skyybank_0.1.4.py) - 2026-09-29, kit
    skyyui 1.3 988889603a0f, page a838d325f680; one JVM with -Xverify:all, HytaleServer.jar, 0.1.3 and 0.1.4 each in its own class
    loader: A all 12 classes of both jars load, verify and initialise. B the 10 classes other than BankPage and SkyyBankPlugin are
    byte-identical to 0.1.3; SkyyBankPlugin is 0.1.3's bytes once its ready-log constant is swapped back; BankPage has 0.1.3's
    fields and 11 methods instruction-identical (constructor, jsonStr, fmt, dur, every, subText, rateText, nextText, gainText,
    typed, handleDataEvent); only build / colorOf / textOf changed, style is gone, payoutOn is new. C payoutOn == "gainText returned
    its payout line" on 2048 inputs. D 10 states x 5 result marks / amount boxes = 50 builds per jar: identical b.set lines (incl.
    #SkyyBAmount.Value) and 7 event bindings; all 1750 appended 0.1.4 markups equal the kit's markup and pass check_markup (50
    check_page), kit colours only, all 25 0.1.3 ids; the payout line green in 30 builds, grey in 15, red in 5 (unreadable account);
    the result line by its mark. E 4 states x 13 clicks through handleDataEvent = 52 per jar: identical result line, amount box,
    purse, bank and rebuilt page after every click. F text fit on the client's NunitoSans tables: all 6 button labels fit (WITHDRAW
    ALL 142 of 152 px), every seen one-line text fits its box, #SkyyBSub / #SkyyBInfo need at most 2 lines (43.6 of 46 px).
    G the page id in the jar's ready log line = the kit's page now = BANK_PAGE_CHECKED.'''
# review 2 finding 6: the page id (BANK_PAGE_ID, a hash of the kit-emitted BankPage code) the harness last passed on
PAGE_CHECKED = "a838d325f680"
rep(HEAD_OLD, fill(HEAD_NEW, {"CHECKED": CHECKED}))

# ================================================================================================ version, kit import, log line
rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')
rep("import skyybuild as B\n", """import skyybuild as B
import skyyui as SUI       # 0.1.4: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line
""")
# the ready log line names the kit AND the page build (review 2 finding 6: BANK_PAGE_ID, set by the page code below)
rep('log("[SkyyBank] {VERSION} ready - /bank (page), interest "',
    'log("[SkyyBank] {VERSION} ready ({KIT_ID}, page {BANK_PAGE_ID}) - /bank (page), interest "')

# ================================================================================================ BankPage: the look only
rep("# ================= BankPage (0.1.3; inline, rebuilt only after a click) =================",
    "# ================= BankPage (0.1.3 logic; 0.1.4 look = the vanilla UI kit tools/skyyui.py; inline, rebuilt only after a click) =================")

# the custom button style helper is replaced by the kit's button styles
cut('PM(r"""\npublic static String style(String bg, String hov, String press, String fg, int fs) {',
    "# one string value out of the page event JSON")

# the result-line colour / text helpers: the kit's (same names, same signatures, vanilla colours)
cut('PM(r"""\npublic static String colorOf(String res) {', '# 2475000 ms -> "41 min 15 s"; 7500000 -> "2 h 5 min"',
    '''# 0.1.4: the result-line helpers are the kit's (same names and signatures as 0.1.3): colorOf picks the vanilla colour by the mark
# ("+" success, "-" error, "=" SUI.STATUS["="] = the vanilla info blue), textOf strips the mark.
for _src in SUI.java_status_methods("colorOf", "textOf"):
    PM(_src)
''')

# build(): keep 0.1.3's prelude and bindings verbatim, replace the markup
OLD_BUILD = cut('PM(r"""\npublic void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {', "# clicks run on the player's world thread (page events)",
                "@@NEWBUILD@@")
_lines = OLD_BUILD.split(LF)
_p0 = [i for i, ln in enumerate(_lines) if ln.startswith("  java.util.UUID u = this.playerRef.getUuid();")]
_p1 = [i for i, ln in enumerate(_lines) if ln.startswith("  long left = @PKG@.BankConfig.LAST")]
assert len(_p0) == 1 and len(_p1) == 1 and _p0[0] < _p1[0], "0.1.3 build prelude not found"
PRELUDE = LF.join(_lines[_p0[0]:_p1[0] + 1])
BINDINGS = LF.join(ln for ln in _lines if "ev.addEventBinding(" in ln)
assert BINDINGS.split(LF) == BIND0
KEEPSET = [ln for ln in _lines if "b.set(\"#SkyyBAmount.Value\"" in ln]
assert KEEPSET == ['  if (this.keepAmount != null && this.keepAmount.length() > 0) b.set("#SkyyBAmount.Value", this.keepAmount);'], KEEPSET
# the 0.1.3 b.set targets and values (Java expressions), to prove 0.1.4 sets the same things
SETS013 = re.findall(r'b\.set\("#(SkyyB[A-Za-z0-9]+)\.Text", (.+?)\);', OLD_BUILD)
assert len(SETS013) == 9, SETS013
IDS013 = sorted(set(re.findall(r"#(SkyyB[A-Za-z0-9]*)", OLD_BUILD)))
assert len(IDS013) == 25, (len(IDS013), IDS013)
# the Java locals the new markup reads (the gain colour) come from the verbatim prelude
for _v in ("boolean readable", "long bank", "int pct", "long max"):
    assert _v in PRELUDE, "0.1.3 prelude lost " + _v

# The page code for the generated script. A RAW template filled by @@TOKEN@@ replacement (review finding 8): no % formatting, so
# nothing in it is doubled; the kit calls inside run when the BUILD runs (every value proven by SUI.verify() then).
NEWBUILD = r'''# review 2 finding 1 (2026-09-29): is gainText()'s line a payout? gainText()'s own branches, its principal / gain lines copied
# verbatim by tools/bank_0_1_4_patch.py. #SkyyBGain's colour asks this helper instead of testing the text for a prefix, so a
# rewording of gainText() cannot turn the payout grey; SkyyBank/test_skyybank_0.1.4.py checks payoutOn(...) == "gainText(...)
# returned its payout line" on a grid of balances, rates and caps (keep the two in step: the harness fails otherwise).
BANK_PAYOUT_SRC = r"""
@@PAYOUTSRC@@"""
PM(BANK_PAYOUT_SRC)
# 0.1.4: the page look from the vanilla UI kit (tools/skyyui.py, research/Vanilla-UI-Style-Guide.md). bank_page() builds the markup
# with kit calls when this script runs (every value proven by SUI.verify() above) and returns the page shell + the b.set lines; the
# Java below keeps 0.1.3's prelude and event bindings verbatim (tools/bank_0_1_4_patch.py copied them out of 0.1.3).
BANK_W, BANK_H = 1100, 593            # page root; the frame takes 38 px of title bar + 2 x 17 px padding: body 1066 x 521
BANK_PREFIX = "SkyyB"                 # every element id starts with it (the 0.1.3 ids already did)
BANK_STEPS = (4, 6, 8, 10, 12, 16)    # the vanilla spacing steps: every Anchor margin bank_page() writes is one of them (asserted)
# review 2 finding 2: "WITHDRAW ALL" (17 px bold) is ~142 px, a 172 px button leaves 172 - 2 x 24 = 124 px of label room; vanilla
# buttons grow to their label (MinWidth 172), so the two "all" buttons are 200 px (152 px of room) - no ShrinkTextToFit needed
BANK_BTN_WIDE = 200
# review 2 finding 3: a box for two wrapped 16 px lines. The game font's line height is 1.364 em (NunitoSans), 2 x 16 x 1.364 =
# 43.7 px: 44 px left no slack, 46 px leaves 2 px (#SkyyBSub and #SkyyBInfo)
BANK_TWO_LINES = 46
# every element id 0.1.3 had - all kept (the Java binds / sets / reads them); bank_page() asserts each one is still created
BANK_IDS_013 = @@IDS@@
# 0.1.3's b.set("#<id>.Text", <Java expression>) lines, unchanged
BANK_SETS_013 = @@SETS@@
# review 2 finding 6: the page id (BANK_PAGE_ID below) that SkyyBank/test_skyybank_0.1.4.py last passed on (tools/bank_0_1_4_patch.py
# PAGE_CHECKED); a build whose kit output makes a different page warns, and the harness fails, until that page is checked
BANK_PAGE_CHECKED = "@@PAGECHECKED@@"


def bank_outer(mk):
    """(outer width, outer height) of a markup's ROOT element, read from its own Anchor: Width + Left + Right (+ 2 x Horizontal /
    Full) and Height + Top + Bottom (+ 2 x Vertical / Full); None where the root sets no Width / Height. KIT-GAP (review 2): the
    kit builders do not report their outer size, so the budget reads it back out of the markup instead of typing "+ 12" by hand."""
    r = SUI.render(mk)
    i = r.index("{")
    j = r.find("{", i + 1)
    own = r[i + 1:] if j < 0 else r[i + 1:j]
    m = re.search(r"Anchor: \(([^)]*)\)", own)
    a = dict((k, int(v)) for k, v in re.findall(r"(Width|Height|Left|Right|Top|Bottom|Horizontal|Vertical|Full): (-?\d+)",
                                                 m.group(1))) if m else {}
    hm = a.get("Left", 0) + a.get("Right", 0) + 2 * (a.get("Horizontal", 0) + a.get("Full", 0))
    vm = a.get("Top", 0) + a.get("Bottom", 0) + 2 * (a.get("Vertical", 0) + a.get("Full", 0))
    return (a["Width"] + hm if "Width" in a else None), (a["Height"] + vm if "Height" in a else None)


def bank_filled(ap, parent, axis, avail, what, cross=None):
    """Assert that the direct children of `parent` fill it exactly: their outer widths (axis "w", a LayoutMode Left row) or outer
    heights (axis "h", a LayoutMode Top column) sum to `avail` px (no FlexWeight filler); cross = the row height every child of a
    Left row must fit in."""
    kids = [bank_outer(mk) for p, mk in ap if p == parent]
    assert kids, "%s has no children" % what
    sizes = [k[0] if axis == "w" else k[1] for k in kids]
    assert None not in sizes, "%s: a child without a fixed %s" % (what, "Width" if axis == "w" else "Height")
    left = SUI.fit(sizes, avail, what)
    assert left == 0, "%s must be filled exactly: %s = %d of %d px" % (what, sizes, sum(sizes), avail)
    if cross is not None:
        assert all(k[1] is not None and k[1] <= cross for k in kids), "%s: a child is taller than the %d px row: %s" % (what, cross, kids)


def bank_page():
    """(shell, sets): BankPage's markup from the kit. Vanilla spacing steps only; the page height is the sum of its parts (the body,
    every row and every well are filled exactly, no FlexWeight - read back out of the markup) - asserted, like every 0.1.3 id and
    b.set target."""
    sh = SUI.page_shell("SkyyBankF", BANK_W, BANK_H, "Bank", body_id="SkyyBank")      # decorated window; the 0.1.3 root is the body
    ap, body, W = sh.appends, sh.body, sh.inner_w
    n_frame = len(ap)
    BTN = SUI.BTN_MIN_W                   # 172: the buttons (@DefaultButtonMinWidth)
    WIDE = BANK_BTN_WIDE                  # 200: Deposit all / Withdraw all (review 2 finding 2)
    PAD = SUI.WELL_PAD                    # 8: the well's own padding (WorldEventPanelPage #Summary)

    # 1. profile / hint line (0.1.3 #SkyyBSub = subText(u)): the vanilla wrapped message (PrefabEditorExitConfirm; the SkyyVault 0.1.3
    #    dialog message), two lines high, so a long profile name + class wraps instead of being clipped (review finding 6)
    ap.append((body, SUI.label("SkyyBSub", "", "message", h=BANK_TWO_LINES, anchor={"bottom": 12})))

    # 2. PURSE and BANK: two wells side by side, 12 apart; in each a centred @Subtitle (bottom 10), the number (the kit display:
    #    32 px, Default font) and a caption
    head_h, num_h, cap_h = 25, 42, 25
    bal_h = head_h + 10 + num_h + cap_h + 2 * PAD
    box_w = (W - 12) // 2
    ap.append((body, SUI.group("SkyyBBal", "Left", h=bal_h, anchor={"bottom": 16})))
    for box, num, head, cap, left in (("SkyyBPurseBox", "SkyyBPurse", "Purse", "coins you carry - lost in part when you die", None),
                                      ("SkyyBBankBox", "SkyyBBalance", "Bank", "coins in the bank - safe when you die", {"left": 12})):
        ap.append(("SkyyBBal", SUI.panel(box, "well", w=box_w, h=bal_h, anchor=left)))
        ap.append((box, SUI.label(None, head, "subtitle", h=head_h, align="Center", anchor={"bottom": 10})))
        ap.append((box, SUI.label(num, "", "display", h=num_h, align="Center")))
        ap.append((box, SUI.label(None, cap, "caption", h=cap_h, align="Center")))

    # 3. interest: one well - the rate (the vanilla heading, one line: no Wrap / WrapMaxLines), the next payout time, the payout line.
    #    #SkyyBGain colour (review finding 7): success green only when gainText() is a payout - asked of payoutOn() (review 2
    #    finding 1), the label grey for its hints, error red when the account file cannot be read. readable / bank / pct / max are
    #    the 0.1.3 prelude's locals.
    int_rows = [28, 26, 26]
    int_h = sum(int_rows) + 2 * PAD
    ap.append((body, SUI.panel("SkyyBInt", "well", h=int_h, anchor={"bottom": 16})))
    ap.append(("SkyyBInt", SUI.label("SkyyBRate", "", "heading", h=int_rows[0], align="Center", wrap=False)))
    ap.append(("SkyyBInt", SUI.label("SkyyBNext", "", "default", h=int_rows[1], align="Center")))
    gain_col = SUI.J('!readable ? "%s" : (payoutOn(readable, bank, pct, max) ? "%s" : "%s")'
                     % (SUI.COLOR["error"], SUI.COLOR["success"], SUI.COLOR["text"]), SUI.COLOR["success"])
    ap.append(("SkyyBInt", SUI.label("SkyyBGain", "", "bold", h=int_rows[2], align="Center", col=gain_col)))

    # 4. controls, 0.1.3's order: Deposit all | Amount | Deposit | Withdraw | Withdraw all (green -> Primary, blue -> Secondary),
    #    16 between the groups, 6 inside the middle one; the amount box takes the rest of the row (InstanceListPage's search field
    #    is FlexWeight 1 - here the fixed width that works out to), centred on the 44 px row
    ctl_h = SUI.BTN_H
    field_w = W - 2 * WIDE - 2 * BTN - 2 * 16 - 2 * 6
    field_top = (ctl_h - SUI.FIELD_H) // 2
    assert field_w >= 240, "the amount box is too narrow: %d px" % field_w
    ap.append((body, SUI.group("SkyyBCtl", "Left", h=ctl_h)))
    ap.append(("SkyyBCtl", SUI.button("SkyyBDepAll", "Deposit all", "primary", w=WIDE, anchor={"right": 16})))
    ap.append(("SkyyBCtl", SUI.text_field("SkyyBAmtBox", "SkyyBAmount", w=field_w, placeholder="Amount", max_length=16,
                                          anchor={"top": field_top, "right": 6})))
    ap.append(("SkyyBCtl", SUI.button("SkyyBDep", "Deposit", "primary", w=BTN, anchor={"right": 6})))
    ap.append(("SkyyBCtl", SUI.button("SkyyBWd", "Withdraw", "secondary", w=BTN, anchor={"right": 16})))
    ap.append(("SkyyBCtl", SUI.button("SkyyBWdAll", "Withdraw all", "secondary", w=WIDE)))

    # 5. captions under the controls, top 4, each as wide as its control group (the middle one is b.set: it has commas and dots)
    capr_h, mid_w = 25, field_w + 6 + BTN + 6 + BTN
    assert SUI.fit([WIDE, 16, mid_w, 16, WIDE], W, "captions row") == 0, "the captions must sit under their controls"
    assert SUI.fit([WIDE, 16, field_w, 6, BTN, 6, BTN, 16, WIDE], W, "controls row") == 0, "the controls row must fill the body width"
    ap.append((body, SUI.group("SkyyBCap", "Left", h=capr_h, anchor={"top": 4})))
    ap.append(("SkyyBCap", SUI.label(None, "your whole purse", "caption", w=WIDE, h=capr_h, align="Center", anchor={"right": 16})))
    ap.append(("SkyyBCap", SUI.label("SkyyBCapMid", "", "caption", w=mid_w, h=capr_h, align="Center", anchor={"right": 16})))
    ap.append(("SkyyBCap", SUI.label(None, "your whole bank", "caption", w=WIDE, h=capr_h, align="Center")))

    # 6. the result line (+ / - / = colours from the kit, two lines) and the chat hint
    ap.append((body, SUI.status_line("SkyyBInfo", "colorOf(this.info)", h=BANK_TWO_LINES, wrap=True, anchor={"top": 12})))
    ap.append((body, SUI.label("SkyyBChat", "", "caption", h=25, align="Center")))

    # 7. footer (WorldEventPanelPage #Footer): content separator (8 above and below), Refresh (right 4) | the flex spacer Group as a
    #    fixed width | Close (left 4; Secondary + the vanilla cancel sound)
    ap.append((body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    ap.append((body, SUI.group("SkyyBBottom", "Left", h=SUI.BTN_H)))
    ap.append(("SkyyBBottom", SUI.button("SkyyBRefresh", "Refresh", "secondary", w=BTN, anchor={"right": 4})))
    ap.append(("SkyyBBottom", SUI.spacer(w=W - 2 * BTN - 2 * 4, h=SUI.BTN_H)))
    ap.append(("SkyyBBottom", SUI.button("SkyyBClose", "Close", "secondary", w=BTN, sound="cancel", anchor={"left": 4})))

    # the budget, read back out of the markup (bank_outer): the body column, every row and every well filled exactly
    bank_filled(ap, body, "h", sh.inner_h, "bank page body (BANK_H = 38 + 2 x 17 + the body)")
    for row, row_h in (("SkyyBBal", bal_h), ("SkyyBCtl", ctl_h), ("SkyyBCap", capr_h), ("SkyyBBottom", SUI.BTN_H)):
        bank_filled(ap, row, "w", W, "row " + row, cross=row_h)
    for well, inner in (("SkyyBPurseBox", bal_h - 2 * PAD), ("SkyyBBankBox", bal_h - 2 * PAD), ("SkyyBInt", int_h - 2 * PAD)):
        bank_filled(ap, well, "h", inner, "well " + well)
    # finding 3: every Anchor margin this page writes (the frame's own values aside) is a vanilla step; and only properties the
    # deployed Skyy pages already use inline (no FlexWeight / WrapMaxLines / LetterSpacing / LayoutMode Center, Right or Full)
    for _p, mk in ap:
        for bad in ("FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Center", "LayoutMode: Right", "LayoutMode: Full"):
            assert bad not in SUI.render(mk), "the bank page must not use %s yet (not on a deployed page): %s" % (bad, mk[:80])
    for _p, mk in ap[n_frame:]:
        for anc in re.findall(r"Anchor: \(([^)]*)\)", SUI.render(mk)):
            for k, v in re.findall(r"(Left|Right|Top|Bottom|Horizontal|Vertical|Full): (-?\d+)", anc):
                assert int(v) in BANK_STEPS or (k, int(v)) in (("Full", 0), ("Top", field_top)), "margin %s: %s is no vanilla step" % (k, v)
    ap.check(BANK_PREFIX)                                            # ids, prefix, no duplicates, parents exist, markup rules
    have = set(i for _p, mk in ap for i in re.findall(r"#([A-Za-z0-9]+)\s*\{", SUI.render(mk)))
    missing = [i for i in BANK_IDS_013 if i not in have]
    assert not missing, "0.1.4 dropped 0.1.3 element ids: %s" % missing
    sets = [(ident, "Text", SUI.J(expr) if not expr.startswith('"') else SUI.java_unlit(expr)) for ident, expr in BANK_SETS_013]
    assert all(ident in have for ident, _pr, _v in sets), "a b.set target is not on the page"
    return sh, sets


BANK_SH, BANK_SET_LINES = bank_page()
BANK_JAVA = "\n".join("  " + ln for ln in BANK_SH.java("b", sets=BANK_SET_LINES).split("\n"))
BANK_BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
@@PRELUDE@@
""" + BANK_JAVA + r"""
@@KEEPSET@@
@@BINDINGS@@
}"""
PM(BANK_BUILD_SRC)
# review 2 finding 6: the page id = a hash of every piece of BankPage that 0.1.4 changed and this build makes (payoutOn, the kit's
# colorOf / textOf, build() with the kit markup): a later kit change that alters the page changes it. It is in the ready log line.
import hashlib
BANK_PAGE_ID = hashlib.sha256("\n".join([BANK_PAYOUT_SRC] + list(SUI.java_status_methods("colorOf", "textOf")) + [BANK_BUILD_SRC])
                              .encode("utf8")).hexdigest()[:12]
if BANK_PAGE_ID == BANK_PAGE_CHECKED:
    print("bank page %s = the page SkyyBank/test_skyybank_0.1.4.py last passed on" % BANK_PAGE_ID)
else:
    print("WARNING: bank page %s is NOT the page SkyyBank/test_skyybank_0.1.4.py last passed on (%s): the kit output changed the page. "
          "Run the harness, then set PAGE_CHECKED in tools/bank_0_1_4_patch.py and regenerate; never deploy an unchecked page"
          % (BANK_PAGE_ID, BANK_PAGE_CHECKED))
'''
rep("@@NEWBUILD@@", fill(NEWBUILD, {"PAYOUTSRC": PAYOUT_SRC, "IDS": repr(IDS013), "SETS": repr(SETS013), "PRELUDE": PRELUDE,
                                    "KEEPSET": KEEPSET[0], "BINDINGS": BINDINGS, "PAGECHECKED": PAGE_CHECKED}))

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
for k in KEEP:
    assert k in s, "a block that must stay 0.1.3's changed: %s" % k[:80]
for c in ("#0b1524", "#ffd070", "#ffe08a", "#142236", "#2a2410", "#101c2c", "#1f5a34", "#2c7a48", "#133a22", "#1d3a5f", "#2f5a8f",
          "#0f2038", "#2a3444", "#3a475c", "#1a2230", "#16263a", "#cfe3ff", "#9fb8d0", "#8fa4b8", "#7fe07f", "#ff8080", "#8fc8ff",
          "#e6ffe8", "#e6f2ff", "TextButtonStyle(Default: (Background: #", "public static String style("):
    assert c not in s, "0.1.3 custom look left in 0.1.4: " + c
for c in ("flex=", "max_lines=", "spacing=", "trial=True", "%%"):     # (the markup itself is checked by bank_page() at build time)
    assert c not in s[s.index("def bank_page():"):s.index("BANK_SH, BANK_SET_LINES")], "bank_page() uses %s" % c
assert "import skyyui as SUI" in s and s.index("SUI.verify()") < s.index("J = B.start()"), "verify() must run before the build"
# review 2 finding 1: no colour is picked from a text prefix any more; payoutOn sits right after gainText, before build()
assert ".startsWith(\"Your next payout" not in s and "BANK_GAIN_PAYOUT" not in s, "the payout colour still tests gainText()'s text"
assert s.index("public static String gainText(") < s.index("public static boolean payoutOn(") < s.index("public void build(@REF@ ref"), \
    "payoutOn must follow gainText and come before build() (javassist: methods before callers)"
assert s.count("public static boolean payoutOn(") == 1 and s.count("payoutOn(readable, bank, pct, max) ? ") == 1, \
    "payoutOn: one definition, used by the one colour expression"
# review 2 finding 6: the page id is in the ready log line and is computed before the plugin section uses it
assert s.index("BANK_PAGE_ID = hashlib") < s.index("ready ({KIT_ID}, page {BANK_PAGE_ID})"), "BANK_PAGE_ID before the log line"
for ident in IDS013:
    assert ('"%s"' % ident) in s or ("#" + ident) in s, "id " + ident
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.1.3 had %d)" % (s.count(LF), OLD.count(LF)))
