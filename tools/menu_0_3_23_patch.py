"""Derive SkyyMenu/build_skyymenu_0.3.23.py from the LIVE SkyyMenu 0.3.22 (python tools/menu_0_3_23_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_22_patch.py -> 0.3.22 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.23. The harness SkyyMenu/test_skyymenu_0.3.23.py is its own file.

0.3.23 = THE ADMIN PAGE (research/Admin-Page-Plan.md; Skyy 2026-10-14 "Run everything you can in parallel. I want everything on your
list done by 5 pm" - the RESUME 'Next' item "admin page"): one in-game page with a button for the admin commands the SET mods already
have, tabs Server / Economy / Players / Diagnostics. Plan defaults taken: option A (every button DISPATCHES the existing command as the
admin through the engine's CommandManager.handleCommand - the /su pattern the menu tiles use; nothing is re-implemented), option C status
text from the bridge where a mod publishes one (auction:count, bazaar:products), danger buttons confirm (the SAME button again within
10 s - task text; the plan's 5 s was a default), a player picker (the online players, < and >) and one Text box (item / zone / listing /
guild ids). Every button is drawn ONLY while the viewer passes the engine's own permission check of the exact command node the button
runs (the command resolved by name, its sub-commands walked, the usage variant picked by the argument count, then
AbstractCommand.hasPermission(player) - what the engine itself checks before it runs the line); the page itself needs skyymenu.modconfig
(re-checked on every draw and click). Opened by /modconfig admin (the /modconfig <mod> usage variant; no new command) and by an "Admin"
button on Server Setup's mod list (it takes the 140 px spacer left of the search box: no other element moves). Vanilla look from the
shared kit tools/skyyui.py (the Sky Window kit is not ready - task text), 1160 x 960, fits 1080, no tooltips, no timers.
The button table OPS (below, inserted into the build script) was checked against the REAL command classes of the SET jars (constructed
in a JVM: names, sub-commands, usage variants, requirePermission nodes) and every dispatch line goes through the engine's own parser in
the harness. Left out on purpose: /shardadmin <action> <player> and /rebirthadmin crashtest <n> - their GREEDY_STRING usage variant is
picked by the token count, so a two-word argument is refused by the engine parser ("wrong number of required parameters"; quoted it
arrives WITH the quotes) - a SkyyShards / SkyyRebirth bug, reported; the one-word /rebirthadmin status | dryrun | backups | recover work.
Also left out of the plan (research/Admin-Page-Plan.md section 1 Diagnostics + section 2): "Recent warnings" (the page cannot read the
world log - no bridge key, and reading log files from a page is new I/O), "Economy snapshot" (no published coins / bank totals key to
read; the Economy-Audit numbers are a separate job), "Sound test" (/soundtest does not exist yet), the "Search" box (paging instead: at
most 2 pages per tab) and the "Mods" tab link (the footer's "Server Setup" button opens the mod list). Status text: AH paused / running,
merchants out and fishing status have no bridge key, so "AH status" (bare /ahadmin, prints "paused true/false") is a button instead.
Fix round (critics, same day): a literal word of a line is a SUB-COMMAND only up to O_DEPTH (the rest are arguments - e.g. "npc list" =
sub npc + argument list); a missing sub-command (an older mod) or an argument count no usage variant takes HIDES the button instead of
falling back to the parent; every button (not only danger ones) swallows a repeat of the same line within 400 ms (a duplicated
Activating event never spawns two airdrops); a danger click after the 10 s window says the window ran out and arms again.
No saved data, no new key, no new command. ROUND_PINS = {}.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.22.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.23.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.22"' in s and "0.3.22: THE SHARDS TILE" in s and "OpsPage" not in s, "not the generated 0.3.22 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.22":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.22" % _set.get("SkyyMenu"))

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.22: THE SHARDS TILE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.23: THE ADMIN PAGE (notes: tools/menu_0_3_23_patch.py; research/Admin-Page-Plan.md): OpsPage - one kit page (tools/skyyui.py), tabs
       Server / Economy / Players / Diagnostics, a button per admin command of the SET mods (table OPS). A button DISPATCHES the existing
       command as the admin (CommandManager.handleCommand, never re-implemented) and is drawn only while the engine's own
       hasPermission of that exact command node passes; the page needs skyymenu.modconfig. Danger buttons: the same button again
       within 10 s. Player picker (< >) + one Text box. Status text from the bridge (auction:count, bazaar:products). Opened by
       /modconfig admin and Server Setup's "Admin" button. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.23.py.
0.3.22: THE SHARDS TILE''')
rep('VERSION = "0.3.22"\n', 'VERSION = "0.3.23"\n')
rep('''                  "/modconfig (or /serversetup) - (admin) change every mod's settings in game"]},''',
    '''                  "/modconfig (or /serversetup) - (admin) change every mod's settings in game",
                  "/modconfig admin - (admin) the Admin page: buttons for the admin commands"]},   # 0.3.23''')

# ---------------------------------------------------------------------------------------------------------------- the OPS table + markup
OPS_BLOCK = r'''
# ================= 0.3.23 THE ADMIN PAGE (research/Admin-Page-Plan.md; tools/menu_0_3_23_patch.py): data + markup =================
# OPS = one row per button: (tab, button label, command line, permission node of the command, mod, confirm, Text box hint, bridge status
# key). {p} = the picked online player, {t} = the Text box. The line is DISPATCHED as the admin (CommandManager.handleCommand); the
# button shows only while the engine's hasPermission of that exact command (sub-commands walked, the usage variant by argument count)
# passes. Every row was read from the real command classes of the SET jars (harness phase O re-checks names, sub-commands, variants,
# nodes and runs every line through the engine's parser). mod "Hytale" = an engine command (its node is generated by the engine).
# Adding a button = one line here.
OPS_TABS = ["Server", "Economy", "Players", "Diagnostics"]
OPS_DIAG = 3
OPS = [
    # ---- Server
    (0, "Server Setup", "modconfig", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (0, "Set hub here", "sethub", "skyyislands.admin", "SkyyIslands", True, "", ""),
    (0, "Warps editor", "warpadmin", "skyyessentials.admin", "SkyyEssentials", False, "", ""),
    (0, "Reload islands", "island reload", "skyyislands.admin", "SkyyIslands", False, "", ""),
    (0, "Zone info", "zone info", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Reload zones", "zone reload", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Go to zone", "zone {t}", "skyyworldgen.admin", "SkyyWorldGen", False, "zone id", ""),
    (0, "Leave zone", "zone leave", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Zone landing here", "zone setlanding", "skyyworldgen.admin", "SkyyWorldGen", True, "", ""),
    (0, "Trade log", "tradeadmin log", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Player trade log", "tradeadmin log {p}", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Trade settings", "tradeadmin config", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Reload trades", "tradeadmin reload", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Return trade items", "tradeadmin return {p}", "skyyessentials.tradeadmin", "SkyyEssentials", True, "", ""),
    (0, "Player rank", "rankadmin player {p}", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Sync ranks", "rankadmin sync", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Reload ranks", "rankadmin reload", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Death penalty", "deathpenalty", "skyycoins.admin", "SkyyCoins", False, "", ""),
    (0, "Bank interest", "bankconfig", "skyybank.admin", "SkyyBank", False, "", ""),
    (0, "Reload skills", "skills reload", "skyyskills.admin", "SkyySkills", False, "", ""),
    (0, "Reload trees", "tree reload", "skyytrees.admin", "SkyyTrees", False, "", ""),
    (0, "Reload collections", "collections reload", "skyycollections.admin", "SkyyCollections", False, "", ""),
    (0, "Reload accessories", "accessories reload", "skyyaccessories.admin", "SkyyAccessories", False, "", ""),
    (0, "Reload mobs", "mobs reload", "skyymobs.admin", "SkyyMobs", False, "", ""),
    # ---- Economy
    (1, "AH status", "ahadmin", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "AH listings", "ahadmin list", "skyyauctions.admin", "SkyyAuctions", False, "", "auction:count"),
    (1, "Player listings", "ahadmin list {p}", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Pause AH", "ahadmin pause", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Resume AH", "ahadmin resume", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Reload AH", "ahadmin reload", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Listing info", "ahadmin info {t}", "skyyauctions.admin", "SkyyAuctions", False, "listing id", ""),
    (1, "Remove listing", "ahadmin remove {t}", "skyyauctions.admin", "SkyyAuctions", True, "listing id", ""),
    (1, "My AH close preview", "ahadmin closeall", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Close my AH listings", "ahadmin closeall confirm", "skyyauctions.admin", "SkyyAuctions", True, "", ""),
    (1, "Bazaar item info", "bazaaradmin info {t}", "skyybazaar.admin", "SkyyBazaar", False, "item id", "bazaar:products"),
    (1, "Reset item price", "bazaaradmin reset {t}", "skyybazaar.admin", "SkyyBazaar", True, "item id", ""),
    (1, "Reload bazaar", "bazaaradmin reload", "skyybazaar.admin", "SkyyBazaar", False, "", ""),
    (1, "Vault info", "vaultadmin info {p}", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Open vault", "vaultadmin open {p}", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Vault settings", "vaultadmin config", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Reload vault", "vaultadmin reload", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "List merchants", "merchantadmin list", "skyymerchants.admin", "SkyyMerchants", False, "", ""),
    (1, "Move merchant", "merchantadmin move {t}", "skyymerchants.admin", "SkyyMerchants", False, "zone id", ""),
    (1, "Spawn merchant", "merchantadmin spawn {t}", "skyymerchants.admin", "SkyyMerchants", False, "zone id", ""),
    (1, "Remove merchant", "merchantadmin remove {t}", "skyymerchants.admin", "SkyyMerchants", True, "zone id", ""),
    (1, "Void bags resume", "pdadmin resume {p}", "skyysacks.admin", "SkyySacks", True, "", ""),
    # ---- Players
    (2, "Class info", "classadmin info {p}", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Class kit", "classadmin kit {p}", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Reset class", "classadmin reset {p}", "skyyclasses.admin", "SkyyClasses", True, "", ""),
    (2, "Reload classes", "classadmin reload", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Profile info", "profileadmin info {p}", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Archived profiles", "profileadmin archive list {p}", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Profile settings", "profileadmin config", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Reload profiles", "profileadmin reload", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Quest check", "questadmin check", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Player quests", "questadmin list {p}", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Repay quests", "questadmin repay {p}", "skyyquests.admin", "SkyyQuests", True, "", ""),
    (2, "Reload quests", "questadmin reload", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest NPCs", "questadmin npc list", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest Board here", "questadmin npc add board", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Marlow here", "questadmin npc add marlow", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest places", "questadmin place list", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Mining spot here", "questadmin place set hub.mining", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Foraging spot here", "questadmin place set hub.foraging", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Farming spot here", "questadmin place set hub.farming", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Fishing spot here", "questadmin place set hub.fishing", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Explore stats", "exploreadmin stats", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Airdrop here", "exploreadmin airdrop", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Explore checklist", "exploreadmin check list", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Explore spots", "exploreadmin spot list", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Reload exploration", "exploreadmin reload", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Player pets", "petadmin list {p}", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Pet kinds", "petadmin kinds", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Pet sweep status", "petadmin sweep", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Requip info", "requipadmin info {p}", "skyywardrobe.admin", "SkyyWardrobe", False, "", ""),
    (2, "Repair requip", "requipadmin repair {p}", "skyywardrobe.admin", "SkyyWardrobe", True, "", ""),
    (2, "Reload requip", "requipadmin reload", "skyywardrobe.admin", "SkyyWardrobe", False, "", ""),
    (2, "Fishing status", "fishadmin status", "skyyfishing.admin", "SkyyFishing", False, "", ""),
    (2, "Reload cooking", "cookadmin reload", "skyycooking.admin", "SkyyCooking", False, "", ""),
    (2, "Reload party", "partyadmin reload", "skyyparty.admin", "SkyyParty", False, "", ""),
    (2, "Guild info", "guildadmin info {t}", "skyyguilds.admin", "SkyyGuilds", False, "guild tag or id", ""),
    (2, "Guild settings", "guildadmin config", "skyyguilds.admin", "SkyyGuilds", False, "", ""),
    (2, "Reload guilds", "guildadmin reload", "skyyguilds.admin", "SkyyGuilds", False, "", ""),
    (2, "Rebirth status", "rebirthadmin status", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Rebirth dry run", "rebirthadmin dryrun", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Rebirth backups", "rebirthadmin backups", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Recover rebirths", "rebirthadmin recover", "skyyrebirth.admin", "SkyyRebirth", True, "", ""),
    # ---- Diagnostics (engine commands; their nodes are the engine's own generated ones)
    (3, "CPU stats", "server stats cpu", "", "Hytale", False, "", ""),
    (3, "Memory stats", "server stats memory", "", "Hytale", False, "", ""),
    (3, "Server version", "version", "", "Hytale", False, "", ""),
    (3, "Who is online", "who", "", "Hytale", False, "", ""),
    (3, "Plugin list", "plugin list", "", "Hytale", False, "", ""),
]
OPS_STATUS_KEYS = ("auction:count", "bazaar:products")
# how many literal words after the command name are SUB-COMMANDS (default: all of them); the rest of the line is arguments. The harness
# walks the real SET command trees and checks every row's depth. A missing sub-command (an older mod) hides the button.
OPS_DEPTH_EXCEPT = {
    "ahadmin closeall confirm": 1,
    "questadmin npc list": 1, "questadmin npc add board": 1, "questadmin npc add marlow": 1, "questadmin place list": 1,
    "questadmin place set hub.mining": 1, "questadmin place set hub.foraging": 1, "questadmin place set hub.farming": 1,
    "questadmin place set hub.fishing": 1,
}


# commands that take their action as an ARGUMENT (/merchantadmin <action> [zone], not sub-commands): every literal word is an argument
OPS_ARG_ROOTS = ("merchantadmin", "pdadmin", "petadmin", "requipadmin", "fishadmin", "rebirthadmin")
# commands that read their own input line (setAllowsExtraArguments(true), fewer required arguments than the line has words; the harness
# checks this against the real field): the engine takes the line as long as it has at least the required words
OPS_EXTRA_ROOTS = ("pdadmin",)


def ops_depth(line):
    lit = [w for w in line.split(" ")[1:] if not w.startswith("{")]
    d = 0 if line.split(" ")[0] in OPS_ARG_ROOTS else OPS_DEPTH_EXCEPT.get(line, len(lit))
    assert 0 <= d <= len(lit), line
    return d
OPS_SUB = "Each button runs the real admin command as you - the answer shows in your chat."
OPS_NOACCESS = "-You need the permission skyymenu.modconfig for the Admin page."
OPS_TEXT_HINT = "item zone listing or guild id"
OPS_TEXT_MAX = 64
OPS_CONFIRM_MS = 10000                 # the danger button's second click must come within 10 s (task text)
OPS_DOUBLE_MS = 400                    # a second click this fast is one double-click (or a duplicated event), not a confirm
OPS_W, OPS_H = 1160, 960
OPS_ROWS = 12                          # button rows per page; 2 buttons per row
OPS_PER = OPS_ROWS * 2
OPS_BTN_W = 252
OPS_ROW_GAP = 6
OPS_CELL_GAP = 12
OPS_HELP_FS = 15
OPS_LINE_H, OPS_LINE_GAP = 30, 4       # Diagnostics info lines
OPS_LINE_MAX = 104                     # an info line is cut into pieces of at most this many characters (at ", ")

# the table: labels / lines / nodes / mods; each command root + node against the SET script of its mod (the harness checks the real classes)
_ops_labels = [o[1] for o in OPS]
assert len(set(_ops_labels)) == len(_ops_labels), "OPS labels must be unique"
_set_live = dict(_LIVE)
for _o in OPS:
    _tab, _lab, _line, _node, _mod, _conf, _hint, _st = _o
    assert 0 <= _tab < len(OPS_TABS) and isinstance(_conf, bool), _o
    assert SUI.TEXT_OK.fullmatch(_lab), "OPS label with unproven characters: " + _lab
    assert re.match(r"^[a-z]+( [a-z0-9.]+| \{p\}| \{t\})*$", _line), "OPS line: " + _line
    assert _line.count("{p}") <= 1 and _line.count("{t}") <= 1 and not ("{p}" in _line and "{t}" in _line), _line
    assert ("{t}" in _line) == bool(_hint), "OPS: a {t} row needs its Text box hint (and only then): " + _line
    assert _st in ("",) + OPS_STATUS_KEYS, _o
    if _mod == "Hytale":
        assert _node == "" and _tab == OPS_DIAG, _o
        continue
    assert _NODE_RE.match(_node), "OPS node: " + _node
    assert _mod in _set_live, "OPS: %s is not in the SET" % _mod
    _sp = _script(_mod, _set_live[_mod])
    assert os.path.isfile(_sp), "OPS: no SET script for %s: %s" % (_mod, _sp)
    _stx = open(_sp, encoding="utf-8").read()
    _root = _line.split(" ")[0]
    assert ('super("%s"' % _root) in _stx or ('"%s", "' % _root) in _stx, "OPS: %s %s has no command /%s" % (_mod, _set_live[_mod], _root)
    assert ('"%s"' % _node) in _stx, "OPS: %s %s never names the node %s" % (_mod, _set_live[_mod], _node)
    for _w in _line.split(" ")[1:]:
        if not _w.startswith("{"):
            assert ('"%s"' % _w) in _stx or (" %s " % _w) in _stx or ("| %s" % _w) in _stx, "OPS: %s never mentions %r (%s)" % (_mod, _w, _line)


def ops_help(o):
    """the help text next to a button: the command it runs ({p} = <player>, {t} = <hint>)"""
    return "/" + o[2].replace("{p}", "<player>").replace("{t}", "<" + o[6] + ">")


def ops_page():
    """the Admin page's markup pieces: shell (the frame), parts (body pieces by name, each (parent, markup)), the per-button markups"""
    J = SUI.J
    sh = SUI.page_shell("SkyyOpsF", OPS_W, OPS_H, "Admin", body_id="SkyyOps")
    IW, WP = sh.inner_w, SUI.WELL_PAD
    BH = SUI.BTN_H
    P = {}
    P["sub"] = ("SkyyOps", SUI.label("SkyyOpsSub", "", "caption", h=24, size=OPS_HELP_FS))
    P["tabs"] = ("SkyyOps", SUI.group("SkyyOpsTabs", "Left", h=BH, anchor={"top": 8, "bottom": 8}))
    P["pick"] = ("SkyyOps", SUI.group("SkyyOpsPick", "Left", h=BH, anchor={"bottom": 8}))
    rows_h = OPS_ROWS * (BH + OPS_ROW_GAP)
    P["list"] = ("SkyyOps", SUI.panel("SkyyOpsList", "well", h=rows_h + 2 * WP))
    P["msg"] = ("SkyyOps", SUI.status_line("SkyyOpsMsg", color_expr="colorOf(this.info)", h=44, wrap=True))
    P["sep"] = ("SkyyOps", SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    P["foot"] = ("SkyyOps", SUI.group("SkyyOpsFoot", "Left", h=BH))
    left = sh.fit([SUI.outer_size(P[k][1])[1] for k in ("sub", "tabs", "pick", "list", "msg", "sep", "foot")])
    assert left >= 0, "admin page parts do not fit"
    # tabs: equal widths, 5 px apart; the active one Primary (the stats page rule)
    tab_w = (IW - (len(OPS_TABS) - 1) * SUI.TAB_GAP) // len(OPS_TABS)
    tabs = []
    for i, name in enumerate(OPS_TABS):
        anc = {"right": SUI.TAB_GAP} if i < len(OPS_TABS) - 1 else None
        tabs.append(("SkyyOpsTabs", SUI.choose(J("this.tab == %d" % i), SUI.button("SkyyOpsTab%d" % i, name, "primary", w=tab_w, anchor=anc),
                                                SUI.button("SkyyOpsTab%d" % i, name, "secondary", w=tab_w, anchor=anc))))
    # the picker row: Player < name > | Text [box] Clear - filled exactly
    g = 6
    pw = {"plab": 80, "pprev": 72, "pname": 268, "pnext": 72, "gap": 24, "tlab": 56, "clr": 120}
    field_w = IW - (pw["plab"] + pw["pprev"] + g + pw["pname"] + g + pw["pnext"] + pw["gap"] + pw["tlab"] + pw["clr"] + g)
    assert field_w >= 300, "the Text box is too narrow: %d" % field_w
    pick = [("SkyyOpsPick", SUI.label(None, "Player", "bold", w=pw["plab"], h=BH)),
            ("SkyyOpsPick", SUI.button("SkyyOpsPPrev", "<", "secondary", w=pw["pprev"], anchor={"right": g})),
            ("SkyyOpsPick", SUI.label("SkyyOpsPName", "", "bold", w=pw["pname"], h=BH, align="Center")),
            ("SkyyOpsPick", SUI.button("SkyyOpsPNext", ">", "secondary", w=pw["pnext"], anchor={"left": g})),
            ("SkyyOpsPick", SUI.spacer(w=pw["gap"], h=BH)),
            ("SkyyOpsPick", SUI.label(None, "Text", "bold", w=pw["tlab"], h=BH)),
            ("SkyyOpsPick", SUI.text_field("SkyyOpsArgBox", "SkyyOpsArg", w=field_w, h=BH, placeholder=OPS_TEXT_HINT, max_length=OPS_TEXT_MAX)),
            ("SkyyOpsPick", SUI.button("SkyyOpsClr", "Clear", "secondary", w=pw["clr"], anchor={"left": g}))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in pick) == IW, "the picker row is not filled exactly"
    # the button grid: rows of two cells (button | gap | help text)
    row_w = IW - 2 * WP
    cell_w = (row_w - OPS_CELL_GAP) // 2
    help_w = cell_w - OPS_BTN_W - 10
    rid, cid = J("r", "0"), J("c", "0")
    grid = {
        "row": ("SkyyOpsList", SUI.group("SkyyOpsR" + rid, "Left", h=BH, anchor={"bottom": OPS_ROW_GAP})),
        "cell": ("SkyyOpsR" + rid, SUI.choose(J("c % 2 == 0"), SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=BH, anchor={"right": OPS_CELL_GAP}),
                                              SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=BH))),
        "gap": ("SkyyOpsC" + cid, SUI.spacer(w=10, h=BH)),
        "help": ("SkyyOpsC" + cid, SUI.label("SkyyOpsH" + cid, "", "caption", w=help_w, h=BH, size=OPS_HELP_FS)),
        "line": ("SkyyOpsList", SUI.label("SkyyOpsI" + J("k", "0"), "", "default", w=row_w, h=OPS_LINE_H, size=OPS_HELP_FS + 1,
                                          anchor={"bottom": OPS_LINE_GAP})),
    }
    # one button per OPS row (static ids SkyyOpsA<n>: each button is drawn once per page); a danger button is Destructive, its armed
    # look (the first click) says "Press again"
    btn, armed = [], []
    for n_, o in enumerate(OPS):
        btn.append(SUI.button("SkyyOpsA%d" % n_, o[1], "destructive" if o[5] else "secondary", w=OPS_BTN_W))
        armed.append(SUI.button("SkyyOpsA%d" % n_, "Press again", "destructive", w=OPS_BTN_W))
    # the footer: < SkyWynn Menu, Server Setup, < Prev, page, Next >, filler, Close - filled exactly
    fw = {"menu": 220, "setup": 190, "prev": 120, "page": 150, "next": 120, "close": SUI.BTN_MIN_W}
    fill = IW - (fw["menu"] + g + fw["setup"] + g + fw["prev"] + fw["page"] + fw["next"] + fw["close"])
    assert fill >= 0, "the admin footer is wider than the page"
    foot = [("SkyyOpsFoot", SUI.button("SkyyOpsMenu", "< SkyWynn Menu", "secondary", w=fw["menu"], anchor={"right": g})),
            ("SkyyOpsFoot", SUI.button("SkyyOpsSetup", "Server Setup", "secondary", w=fw["setup"], anchor={"right": g})),
            ("SkyyOpsFoot", SUI.button("SkyyOpsPrev", "< Prev", "secondary", w=fw["prev"])),
            ("SkyyOpsFoot", SUI.label("SkyyOpsPage", "", "bold", w=fw["page"], h=BH, align="Center")),
            ("SkyyOpsFoot", SUI.button("SkyyOpsNext", "Next >", "secondary", w=fw["next"])),
            ("SkyyOpsFoot", SUI.spacer(w=fill, h=BH)),
            ("SkyyOpsFoot", SUI.button("SkyyOpsClose", "Close", "secondary", sound="cancel", w=fw["close"]))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in foot) == IW, "the admin footer is not filled exactly"
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only)
    chk = SUI.Appends(list(sh.appends))
    for k in ("sub", "tabs", "pick", "list", "msg", "sep", "foot"):
        chk.append(P[k])
    chk.extend(tabs)
    chk.extend(pick)
    for k in ("row", "cell", "gap"):
        chk.append(grid[k])
    chk.append(("SkyyOpsC" + cid, btn[0]))
    chk.append(grid["help"])
    chk.append(grid["line"])
    chk.extend(foot)
    chk.check("SkyyOps")
    SUI.assert_proven(chk, what="admin page")
    SUI.assert_proven(btn + armed, what="admin page buttons")
    for mk in btn + armed:
        SUI.check_markup(mk)
    assert OPS_H <= SUI.MAX_PAGE_H and OPS_H - SUI.DECO_TOP - SUI.DECO_BOTTOM <= 1080, "the admin page with its ornaments must fit 1080 px"
    # every fixed text fits: help lines (with the widest status), the sub line, the info lines
    for o in OPS:
        h_ = ops_help(o) + ((" - 99,999 open" if o[7] == "auction:count" else " - 9,999 items") if o[7] else "")
        assert SUI.text_width(h_, OPS_HELP_FS) <= help_w, "help text too wide for its cell: " + h_
    assert SUI.text_width(OPS_SUB, OPS_HELP_FS) <= IW, "sub line too wide"
    assert SUI.text_width("Not running: SkyyAccessories, SkyyCollections, SkyyExploration, SkyyMerchants, SkyyWardrobe,", OPS_HELP_FS + 1) <= row_w
    return sh, P, tabs, pick, grid, btn, armed, foot, left, cell_w, help_w


OPS_SH, OPS_P, OPS_TABS_MK, OPS_PICK_MK, OPS_GRID, OPS_BTN, OPS_ARMED, OPS_FOOT, OPS_LEFT, OPS_CELL_W, OPS_HELP_W = ops_page()
OPS_ROWS_FIT = (OPS_ROWS * (SUI.BTN_H + OPS_ROW_GAP))                      # the list well's inner height
OPS_SHELL_JAVA = OPS_SH.java("b")
OPS_PART_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_P.items())
OPS_TABS_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in OPS_TABS_MK)
OPS_PICK_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in OPS_PICK_MK)
OPS_GRID_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_GRID.items())
OPS_FOOT_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in OPS_FOOT)
# the SET this menu is built with (Diagnostics compares the running versions with it; SkyyMenu = this build)
OPS_SET = [(m, (VERSION if m == "SkyyMenu" else v)) for m, v in _LIVE]
print("admin page: %d x %d, %d buttons (%s), %d per page, %d px left in the body, kit %s"
      % (OPS_W, OPS_H, len(OPS), ", ".join("%s %d" % (t, len([o for o in OPS if o[0] == i])) for i, t in enumerate(OPS_TABS)), OPS_PER, OPS_LEFT, SUI_KIT_ID))
'''
rep('''print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))
''', '''print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))
''' + OPS_BLOCK)

# ---------------------------------------------------------------------------------------------------------------- engine members used
rep('''# 0.3.10: every engine member the Stats page uses
''', '''# 0.3.23: every engine member the Admin page uses (the command tree walk + the permission check of the exact node)
for c, m in ((T["ACM"], "getSubCommand"), (T["ACM"], "getVariantByArgCount"), (T["ACM"], "hasPermission"), (T["CMGR"], "handleCommand"),
             (T["CMGR"], "resolveCommand"), (T["ACM"], "getRequiredArguments"), (T["UNI"], "getPlayers"), (T["PR"], "getUsername")):
    B.probe(pool, c, m)
assert str(pool.get(T["ACM"]).getMethod("getVariantByArgCount", "(I)L%s;" % T["ACM"].replace(".", "/")).getName()) == "getVariantByArgCount"
assert str(pool.get(T["ACM"]).getMethod("hasPermission", "(Lcom/hypixel/hytale/server/core/command/system/CommandSender;)Z").getName()) == "hasPermission"
assert pool.get(T["PR"]).subtypeOf(pool.get("com.hypixel.hytale.server.core.command.system.CommandSender")), "0.3.23: PlayerRef is a CommandSender"
# 0.3.10: every engine member the Stats page uses
''')

# ---------------------------------------------------------------------------------------------------------------- the class
rep('''stc  = mk("StatsCmd", T["APC"])
''', '''stc  = mk("StatsCmd", T["APC"])
ops  = mk("OpsPage", T["PAGE"])     # 0.3.23: the Admin page (research/Admin-Page-Plan.md)
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, pl)''',
    '''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, pl)''')

# OpsPage data + fields + constructor right after AdminPage's constructor (AdminPage.openOps and the page's Server Setup button use each
# other's constructors - constructors first, methods after)
OPS_CTOR = r'''
# ================= 0.3.23 OpsPage (the Admin page): data, fields, constructor (methods after the AdminPage section) =================
F(ops, "public static final String[] O_TABS = %s;" % jarr(OPS_TABS))
F(ops, "public static final int O_DIAG = %d;" % OPS_DIAG)
F(ops, "public static final int[] O_TAB = %s;" % jints([o[0] for o in OPS]))
F(ops, "public static final String[] O_LABEL = %s;" % jarr([o[1] for o in OPS]))
F(ops, "public static final String[] O_LINE = %s;" % jarr([o[2] for o in OPS]))
F(ops, "public static final String[] O_NODE = %s;" % jarr([o[3] for o in OPS]))
F(ops, "public static final String[] O_MOD = %s;" % jarr([o[4] for o in OPS]))
F(ops, "public static final boolean[] O_CONF = %s;" % jbools([o[5] for o in OPS]))
F(ops, "public static final int[] O_DEPTH = %s;" % jints([ops_depth(o[2]) for o in OPS]))
F(ops, "public static final boolean[] O_EXTRA = %s;" % jbools([o[2].split(" ")[0] in OPS_EXTRA_ROOTS for o in OPS]))
F(ops, "public static final String[] O_HINT = %s;" % jarr([o[6] for o in OPS]))
F(ops, "public static final String[] O_STAT = %s;" % jarr([o[7] for o in OPS]))
F(ops, "public static final String[] O_HELP = %s;" % jarr([ops_help(o) for o in OPS]))
F(ops, "public static final String[] O_MK = %s;" % jarr([SUI.render(m) for m in OPS_BTN]))
F(ops, "public static final String[] O_MKA = %s;" % jarr([SUI.render(m) for m in OPS_ARMED]))
F(ops, "public static final String[] O_SETMOD = %s;" % jarr([m for m, v in OPS_SET]))
F(ops, "public static final String[] O_SETVER = %s;" % jarr([v for m, v in OPS_SET]))
F(ops, "public static final int PER = %d;" % OPS_PER)
F(ops, "public static final int WELL_H = %d;" % OPS_ROWS_FIT)
F(ops, "public static final int ROW_H = %d;" % (SUI.BTN_H + OPS_ROW_GAP))
F(ops, "public static final int LINE_H = %d;" % (OPS_LINE_H + OPS_LINE_GAP))
F(ops, "public static final int LINE_MAX = %d;" % OPS_LINE_MAX)
F(ops, "public static final int TEXT_MAX = %d;" % OPS_TEXT_MAX)
F(ops, "public static final long CONFIRM_MS = %dL;" % OPS_CONFIRM_MS)
F(ops, "public static final long DOUBLE_MS = %dL;" % OPS_DOUBLE_MS)
F(ops, "public static final String SUB = %s;" % jstr(OPS_SUB))
F(ops, "public static final String NOACCESS = %s;" % jstr(OPS_NOACCESS))
for f in ("public int tab;", "public int pg;", "public String arg;", "public String pick;", "public String info;", "public int armed;",
          "public long armedAt;", "public String armedLine;", "public int lastI;", "public long lastAt;", "public String lastLine;", "public boolean field;", "public java.util.Map test;"):
    F(ops, f)
C(ops, r"""
public OpsPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab < 0 || tab >= O_TABS.length ? 0 : tab;
  this.pg = 0;
  this.arg = "";
  this.pick = null;
  try { this.pick = pr == null ? null : pr.getUsername(); } catch (Throwable t) { this.pick = null; }
  this.info = "";
  this.armed = -1;
  this.armedAt = 0L;
  this.armedLine = "";
  this.lastI = -1;
  this.lastAt = 0L;
  this.lastLine = "";
  this.field = false;
  this.test = null;
}""")
'''
rep('''
# ================= 0.3 AdmSaveTask: export copies written on the scheduler (never on the world thread) + the imports folder =================''',
    OPS_CTOR + '''
# ================= 0.3 AdmSaveTask: export copies written on the scheduler (never on the world thread) + the imports folder =================''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup: the Admin button
rep('''M(apg, r"""
public void openMenu(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
  } catch (Throwable t) { @MU@.warn("could not open the SkyWynn Menu: " + t); }
}""")''', '''M(apg, r"""
public void openMenu(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
  } catch (Throwable t) { @MU@.warn("could not open the SkyWynn Menu: " + t); }
}""")
# 0.3.23: the mod list's "Admin" button opens the Admin page (replaces this page; never close-then-open)
M(apg, r"""
public void openOps(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.OpsPage(this.playerRef, 0));
  } catch (Throwable t) { @MU@.warn("could not open the Admin page: " + t); }
}""")''')
rep('''  b.appendInline("#SkyyAdmSearch", spc(140, 50));
  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 520, 50, 60, q, "search settings and editors");''',
    '''  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmOps", 130, 50, "Admin", @MD@.ADM_BS));
  bind(ev, "SkyyAdmOps", "aops");
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 520, 50, 60, q, "search settings and editors");''')
rep('''  if (a.equals("amods")) { toList(); return false; }
  if (a.equals("aback")) {''', '''  if (a.equals("amods")) { toList(); return false; }
  if (a.equals("aops")) { openOps(ref, st); return true; }
  if (a.equals("aback")) {''')

# ---------------------------------------------------------------------------------------------------------------- /modconfig admin
rep('''public AdminModCmd() {
  super("Open one mod's settings in Server Setup: /modconfig <mod>");''', '''public AdminModCmd() {
  super("Open one mod's settings in Server Setup: /modconfig <mod> (/modconfig admin = the Admin page)");''')
rep('''  try { a = String.valueOf(ctx.get(this.modArg)); } catch (Throwable t) { a = null; }
  @PKG@.AdminPage.openFor(pr, store, ref, a);''', '''  try { a = String.valueOf(ctx.get(this.modArg)); } catch (Throwable t) { a = null; }
  if (a != null && a.trim().equalsIgnoreCase("admin")) { @PKG@.OpsPage.openFor(pr, store, ref); return; }   // 0.3.23
  @PKG@.AdminPage.openFor(pr, store, ref, a);''')

# ---------------------------------------------------------------------------------------------------------------- OpsPage methods
OPS_METHODS = r'''
# ================= 0.3.23 OpsPage methods (the Admin page). Seams: rootCmd / can / pageOk / dispatch / online / now / liveVer / redraw /
# closeNow / openMenu / openSetup - the ONLY methods that touch the engine or another page; `test` (always null in game) lets the
# bare-JVM harness hand in real command objects, a model sender, online names and the clock. No timers, no periodic updates.
for _m in SUI.java_status_methods():
    M(ops, _m)
M(ops, r"""
public long now() {
  if (this.test != null && this.test.get("now") instanceof Long) return ((Long) this.test.get("now")).longValue();
  return System.currentTimeMillis();
}""")
M(ops, r"""
public @ACM@ rootCmd(String name) {
  if (name == null) return null;
  if (this.test != null) {
    Object o = this.test.get("cmd:" + name.toLowerCase());
    return o instanceof @ACM@ ? (@ACM@) o : null;
  }
  return @MU@.cmd(name);
}""")
M(ops, r"""
public boolean can(@ACM@ c) {
  if (c == null) return false;
  try {
    if (this.test != null) {
      Object s = this.test.get("sender");
      return s instanceof com.hypixel.hytale.server.core.command.system.CommandSender && c.hasPermission((com.hypixel.hytale.server.core.command.system.CommandSender) s);
    }
    return this.playerRef != null && c.hasPermission(this.playerRef);
  } catch (Throwable t) { return false; }
}""")
M(ops, r"""
public boolean pageOk() {
  if (this.test != null) return Boolean.TRUE.equals(this.test.get("page"));
  return @MU@.isAdmin(this.playerRef);
}""")
M(ops, r"""
public String liveVer(String mod) {
  if (this.test != null) { Object o = this.test.get("ver:" + mod); return o instanceof String ? (String) o : null; }
  return @MU@.liveVersion(mod);
}""")
M(ops, r"""
public String[] online() {
  if (this.test != null) { Object o = this.test.get("online"); return o instanceof String[] ? (String[]) o : new String[0]; }
  java.util.ArrayList rows = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      String n = p.getUsername();
      if (n == null || n.length() == 0) continue;
      rows.add(n.toLowerCase() + "\t" + n);
    }
  } catch (Throwable t) { }
  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String r = (String) rows.get(i); out[i] = r.substring(r.indexOf('\t') + 1); }
  return out;
}""")
M(ops, r"""
public boolean dispatch(String line) {
  if (this.test != null) {
    Object l = this.test.get("ran");
    if (l instanceof java.util.List) ((java.util.List) l).add(line);
    return !Boolean.TRUE.equals(this.test.get("fail"));
  }
  try {
    @CMGR@.get().handleCommand(this.playerRef, line);
    return true;
  } catch (Throwable t) { @MU@.warn("the Admin page could not run /" + line + ": " + t); return false; }
}""")
M(ops, r"""
public String who() {
  try { String n = this.playerRef == null ? null : this.playerRef.getUsername(); return n == null ? "?" : n; } catch (Throwable t) { return "?"; }
}""")
M(ops, r"""
public void redraw() {
  if (this.test != null) { Object n = this.test.get("redraws"); this.test.put("redraws", Integer.valueOf(n instanceof Integer ? ((Integer) n).intValue() + 1 : 1)); return; }
  rebuild();
}""")
M(ops, r"""
public void closeNow(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "close"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @MU@.warn("could not close the Admin page: " + t); }
}""")
M(ops, r"""
public void openMenu(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "menu"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
  } catch (Throwable t) { @MU@.warn("could not open the SkyWynn Menu: " + t); }
}""")
M(ops, r"""
public void openSetup(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "setup"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.AdminPage(this.playerRef, "list", (String) null));
  } catch (Throwable t) { @MU@.warn("could not open Server Setup: " + t); }
}""")
# ---- the command a button runs: the root by name, its O_DEPTH sub-commands walked (a missing one = an older mod = null, hidden), then
# the command itself when it takes exactly the remaining argument count (or at most it, for an O_EXTRA command), else its usage variant for that count, else null (hidden) -
# the command object whose hasPermission the engine checks before it runs exactly this line
M(ops, r"""
public @ACM@ leaf(int i) {
  if (i < 0 || i >= O_LINE.length) return null;
  String[] w = O_LINE[i].split(" ");
  @ACM@ c = rootCmd(w[0]);
  if (c == null) return null;
  int k = 1;
  while (k <= O_DEPTH[i] && k < w.length) {
    @ACM@ s = null;
    try { s = c.getSubCommand(w[k]); } catch (Throwable t) { s = null; }
    if (s == null) return null;
    c = s;
    k++;
  }
  int n = w.length - k;
  int req = -1;
  try { req = c.getRequiredArguments().size(); } catch (Throwable t) { req = -1; }
  if (req == n || (O_EXTRA[i] && req >= 0 && req <= n)) return c;
  @ACM@ v = null;
  try { v = c.getVariantByArgCount(n); } catch (Throwable t) { v = null; }
  return v;
}""")
M(ops, r"""
public boolean visible(int i) {
  return can(leaf(i));
}""")
M(ops, r"""
public int[] visibleOn(int t) {
  int n = 0;
  boolean[] v = new boolean[O_TAB.length];
  for (int i = 0; i < O_TAB.length; i++) { if (O_TAB[i] == t && visible(i)) { v[i] = true; n++; } }
  int[] out = new int[n];
  int k = 0;
  for (int i = 0; i < O_TAB.length; i++) if (v[i]) { out[k] = i; k++; }
  return out;
}""")
M(ops, r"""
public static int num(String s) {
  try { return Integer.parseInt(s); } catch (Throwable t) { return -1; }
}""")
M(ops, r"""
public static boolean okText(String s) {
  if (s == null || s.length() == 0 || s.length() > TEXT_MAX) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == ':' || c == '-';
    if (!ok) return false;
  }
  return true;
}""")
M(ops, r"""
public int pickIndex(String[] on) {
  if (this.pick == null) return -1;
  for (int j = 0; j < on.length; j++) if (on[j].equalsIgnoreCase(this.pick)) return j;
  return -1;
}""")
M(ops, r"""
public String picked() {
  String[] on = online();
  int j = pickIndex(on);
  return j < 0 ? null : on[j];
}""")
M(ops, r"""
public void cyclePick(int d) {
  String[] on = online();
  if (on.length == 0) { this.pick = null; return; }
  int j = pickIndex(on);
  if (j < 0) j = d > 0 ? 0 : on.length - 1;
  else j = (j + d + on.length) % on.length;
  this.pick = on[j];
}""")
# the exact line a button dispatches, or null (this.info says what is missing)
M(ops, r"""
public String expand(int i) {
  String line = O_LINE[i];
  if (line.indexOf("{p}") >= 0) {
    String p = picked();
    if (p == null) { this.info = "-Pick an online player first (the < and > next to Player)."; return null; }
    if (!okText(p)) { this.info = "-That player name cannot be typed into a command."; return null; }
    line = line.replace("{p}", p);
  }
  if (line.indexOf("{t}") >= 0) {
    String a = this.arg == null ? "" : this.arg.trim();
    if (a.length() == 0) { this.info = "-Type the " + O_HINT[i] + " into the Text box first."; return null; }
    if (!okText(a)) { this.info = "-The Text box takes letters, digits and _ . : - only (" + TEXT_MAX + " at most), no spaces."; return null; }
    line = line.replace("{t}", a);
  }
  return line;
}""")
M(ops, r"""
public boolean armedNow(int i) {
  long d = now() - this.armedAt;
  return this.armed == i && d >= 0L && d <= CONFIRM_MS;
}""")
M(ops, r"""
public void run(int i) {
  if (i < 0 || i >= O_LINE.length) return;
  if (!visible(i)) { this.armed = -1; this.info = "-You cannot run that command (no permission, or its mod is not on this server)."; return; }
  String line = expand(i);
  if (line == null) { this.armed = -1; return; }
  long t = now();
  long dl = t - this.lastAt;
  if (this.lastI == i && line.equals(this.lastLine) && dl >= 0L && dl < DOUBLE_MS) return;
  if (O_CONF[i]) {
    long d = t - this.armedAt;
    boolean same = this.armed == i && line.equals(this.armedLine) && d >= 0L;
    if (same && d < DOUBLE_MS) return;
    if (!same || d > CONFIRM_MS) {
      this.armed = i;
      this.armedAt = t;
      this.armedLine = line;
      if (same) this.info = "=The 10 s ran out. Press " + O_LABEL[i] + " again within 10 s to run /" + line;
      else this.info = "=Press " + O_LABEL[i] + " again within 10 s to run /" + line;
      return;
    }
  }
  this.armed = -1;
  this.armedLine = "";
  this.lastI = i;
  this.lastAt = t;
  this.lastLine = line;
  if (dispatch(line)) {
    this.info = "+Ran /" + line + " - the answer is in your chat.";
    @MU@.info("Admin page: " + who() + " ran /" + line);
  } else this.info = "-/" + line + " could not be run.";
}""")
M(ops, r"""
public static String statusOf(String key) {
  if (key == null || key.length() == 0) return "";
  Object o = null;
  try { java.util.Map b = @MU@.bridge(); o = b == null ? null : b.get(key); } catch (Throwable t) { o = null; }
  if (o == null) return "";
  if (key.equals("auction:count") && o instanceof Number) return ((Number) o).longValue() + " open";
  if (key.equals("bazaar:products")) return @MU@.csvCount(o) + " items";
  return "";
}""")
M(ops, r"""
public String helpOf(int i) {
  String s = statusOf(O_STAT[i]);
  return O_HELP[i] + (s.length() > 0 ? " - " + s : "");
}""")
M(ops, r"""
public static void addWrapped(java.util.ArrayList out, String head, String list) {
  String line = head;
  String[] parts = list.split(", ");
  for (int i = 0; i < parts.length; i++) {
    String add = (line.equals(head) ? "" : ", ") + parts[i];
    if (line.length() + add.length() > LINE_MAX && !line.equals(head)) { out.add(line + ","); line = "    " + parts[i]; }
    else line = line + add;
  }
  out.add(line);
}""")
M(ops, r"""
public String[] diagLines() {
  java.util.ArrayList out = new java.util.ArrayList();
  int run = 0;
  StringBuilder off = new StringBuilder();
  StringBuilder other = new StringBuilder();
  for (int k = 0; k < O_SETMOD.length; k++) {
    String v = liveVer(O_SETMOD[k]);
    if (v == null) { if (off.length() > 0) off.append(", "); off.append(O_SETMOD[k]); continue; }
    run++;
    if (!v.equals(O_SETVER[k])) { if (other.length() > 0) other.append(", "); other.append(O_SETMOD[k]).append(' ').append(v).append(" (set ").append(O_SETVER[k]).append(')'); }
  }
  out.add("Skyy mods running: " + run + " of the " + O_SETMOD.length + " in the set this menu was built with.");
  if (off.length() > 0) addWrapped(out, "Not running: ", off.toString());
  if (other.length() > 0) addWrapped(out, "Other version: ", other.toString());
  out.add("Players online: " + online().length);
  String ah = statusOf("auction:count");
  out.add("Auction House: " + (ah.length() > 0 ? ah : "no count published"));
  String bz = statusOf("bazaar:products");
  out.add("Bazaar: " + (bz.length() > 0 ? bz : "no item list published"));
  return (String[]) out.toArray(new String[0]);
}""")
# the Text box's EventData key "@OpsArg" (the at sign is the build's token marker, so it is made here - AdminPage.at's way)
M(ops, r"""
public static String argKey() {
  return String.valueOf((char) 64) + "OpsArg";
}""")
M(ops, r"""
public @EVD@ evd(String a) {
  @EVD@ d = @EVD@.of("a", a);
  if (this.field) d = d.append(argKey(), "#SkyyOpsArg.Value");
  return d;
}""")
M(ops, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  boolean ok = pageOk();
  if (this.tab < 0 || this.tab >= O_TABS.length) this.tab = 0;
  int[] vis = ok ? visibleOn(this.tab) : new int[0];
  int pages = vis.length <= 0 ? 1 : (vis.length + PER - 1) / PER;
  if (this.pg >= pages) this.pg = pages - 1;
  if (this.pg < 0) this.pg = 0;
  this.field = ok;
""" + "\n".join("  " + ln for ln in OPS_SHELL_JAVA.split("\n")) + r"""
  """ + OPS_PART_JAVA["sub"] + r"""
  b.set("#SkyyOpsSub.Text", ok ? SUB : textOf(NOACCESS));
  if (ok) {
    """ + OPS_PART_JAVA["tabs"] + r"""
""" + "\n".join("    " + ln for ln in OPS_TABS_JAVA.split("\n")) + r"""
    for (int t = 0; t < O_TABS.length; t++) ev.addEventBinding(@BT@.Activating, "#SkyyOpsTab" + t, evd("ot" + t));
    """ + OPS_PART_JAVA["pick"] + r"""
""" + "\n".join("    " + ln for ln in OPS_PICK_JAVA.split("\n")) + r"""
    String[] on = online();
    int pj = pickIndex(on);
    b.set("#SkyyOpsPName.Text", pj < 0 ? (on.length == 0 ? "nobody online" : "nobody picked") : on[pj] + "  (" + (pj + 1) + " of " + on.length + ")");
    if (this.arg != null && this.arg.length() > 0) b.set("#SkyyOpsArg.Value", this.arg);
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPPrev", evd("pprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPNext", evd("pnext"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsClr", evd("clr"));
  }
  """ + OPS_PART_JAVA["list"] + r"""
  int from = this.pg * PER;
  int n = vis.length - from;
  if (n > PER) n = PER;
  if (n < 0) n = 0;
  for (int c = 0; c < n; c++) {
    int r = c / 2;
    int i = vis[from + c];
    if (c % 2 == 0) {
      """ + OPS_GRID_JAVA["row"] + r"""
    }
    """ + OPS_GRID_JAVA["cell"] + r"""
    b.appendInline("#SkyyOpsC" + c, armedNow(i) ? O_MKA[i] : O_MK[i]);
    """ + OPS_GRID_JAVA["gap"] + r"""
    """ + OPS_GRID_JAVA["help"] + r"""
    b.set("#SkyyOpsH" + c + ".Text", helpOf(i));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsA" + i, evd("op" + i));
  }
  String[] dl = new String[0];
  if (ok && this.tab == O_DIAG && this.pg == 0) dl = diagLines();
  else if (ok && vis.length == 0) dl = new String[] { "No button on this tab for you: none of its commands is on this server, or your permissions do not include them." };
  int used = ((n + 1) / 2) * ROW_H;
  for (int k = 0; k < dl.length; k++) {
    if (used + (k + 1) * LINE_H > WELL_H) break;
    """ + OPS_GRID_JAVA["line"] + r"""
    b.set("#SkyyOpsI" + k + ".Text", dl[k]);
  }
  """ + OPS_PART_JAVA["msg"] + r"""
  b.set("#SkyyOpsMsg.Text", textOf(ok ? this.info : NOACCESS));
  """ + OPS_PART_JAVA["sep"] + r"""
  """ + OPS_PART_JAVA["foot"] + r"""
""" + "\n".join("  " + ln for ln in OPS_FOOT_JAVA.split("\n")) + r"""
  b.set("#SkyyOpsPage.Text", "Page " + (this.pg + 1) + " of " + pages);
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsMenu", evd("menu"));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsSetup", evd("setup"));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsPrev", evd("gprev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsNext", evd("gnext"));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsClose", evd("close"));
}""")
M(ops, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @MU@.jstr(data, "a", 40);
    if (data.indexOf("\"" + argKey() + "\"") >= 0) this.arg = @MU@.jstr(data, argKey(), TEXT_MAX);
    if (a.equals("close")) { closeNow(ref, st); return; }
    if (a.equals("menu")) { openMenu(ref, st); return; }
    if (!pageOk()) { this.info = NOACCESS; this.armed = -1; redraw(); return; }
    if (a.equals("setup")) { openSetup(ref, st); return; }
    if (a.startsWith("ot")) {
      int t = num(a.substring(2));
      if (t >= 0 && t < O_TABS.length) { this.tab = t; this.pg = 0; this.armed = -1; this.info = ""; }
    } else if (a.equals("gprev")) { if (this.pg > 0) this.pg = this.pg - 1; }
    else if (a.equals("gnext")) this.pg = this.pg + 1;
    else if (a.equals("pprev")) cyclePick(-1);
    else if (a.equals("pnext")) cyclePick(1);
    else if (a.equals("clr")) this.arg = "";
    else if (a.startsWith("op")) run(num(a.substring(2)));
    redraw();
  } catch (Throwable t) { @MU@.warn("admin page click failed: " + t); }
}""")
# /modconfig admin (the /modconfig <mod> usage variant; skyymenu.modconfig) and nothing else opens it; runs on the player's world thread
M(ops, r"""
public static void openFor(@PR@ pr, @ST@ store, @REF@ ref) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    p.getPageManager().openCustomPage(ref, store, new @PKG@.OpsPage(pr, 0));
  } catch (Throwable t) {
    @MU@.warn("/modconfig admin failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[Admin] Could not open the Admin page.")); } catch (Throwable t2) { }
  }
}""")
'''
rep('''
# ================= /modconfig (alias /serversetup) + the usage variant /modconfig <mod>; admins only (requirePermission, HANDOFF rule 1) =================''',
    OPS_METHODS + '''
# ================= /modconfig (alias /serversetup) + the usage variant /modconfig <mod>; admins only (requirePermission, HANDOFF rule 1) =================''')

# ---------------------------------------------------------------------------------------------------------------- done
assert s.count("OpsPage") >= 6 and s.count('mk("OpsPage"') == 1, "0.3.23: the changes"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.22 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.22 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
