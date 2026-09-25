"""Derive SkyyTrees/build_skyytrees_0.2.2.py from build_skyytrees_0.2.1.py (the trees_0_2_1_patch.py style: rep(old, new) with asserted
single anchors, newline-agnostic; 0.2.1 stays untouched and its CRLF line endings are kept). Edit THIS file, not the generated script.
0.2.2 = the SkyyTrees parts of two specs (SkyyTrees 0.2.1 is the LIVE jar, tools/deploy_set.py SET since 2026-09-24 22:53):
 - research/Server-Setup-Spec.md 4.10 + 7 (tools/CONFIG-CONTRACT.md): the admin config registry. trees.properties becomes editable in
   SkyWynn Menu -> Server Setup -> Trees (SkyyMenu 0.3) through the kit tools/skyycfg.py: config:def:SkyyTrees + config:fn:SkyyTrees
   published at the END of setup() (after TreeCfg.load), change log + file history + export / import, /tree reload through the kit.
 - research/Settings-Spec.md 1.3 + 3.2: the player Settings switches trees.bonus + trees.abilities (regSetting in setup, notifyOn gates
   on the three sendMessage calls only, the one-shot /tree quiet move, /tree quiet flips trees.bonus when SkyyMenu is there).
Default behaviour is IDENTICAL to 0.2.1 until an admin changes something (no file key, default, loader or clamp changes).
Run:  python tools/trees_0_2_2_patch.py   then   python SkyyTrees/build_skyytrees_0.2.2.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.1.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.1"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyyTrees 0.2.1 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.py by tools/trees_0_2_1_patch.py - edit the patch, not this file (0.2 stays untouched; 0.2 was
derived from 0.1 by tools/trees_0_2_patch.py).
0.2.1 = HANDOFF feedback round 2''', r'''"""SkyyTrees 0.2.2 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.1.py by tools/trees_0_2_2_patch.py - edit the patch, not this file (0.2.1 stays untouched; 0.2.1 was
derived from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py).
0.2.2 = in-game server setup + player Settings (Skyy 2026-09-24: "everything a server owner might change must be doable in game, config
  files stay and always match"). DEFAULT BEHAVIOUR IS IDENTICAL TO 0.2.1 until an admin changes something: no file key, default,
  loader, clamp, node or message text changed; trees.properties is not written at start (only a first start writes the default file,
  as before, now with one more comment line saying it is editable in game).
  ADMIN CONFIG (research/Server-Setup-Spec.md 4.10 + 7, tools/CONFIG-CONTRACT.md, the kit tools/skyycfg.py):
    - SkyWynn Menu -> Server Setup -> "Trees" (SkyyMenu 0.3, /modconfig): config:def:SkyyTrees + config:fn:SkyyTrees (+ config:epoch)
      are put on the skyy.bridge as the LAST step of setup(), after TreeCfg.load (CfgPub.start); CfgPub.shutdown() in shutdown writes any
      pending change. Admin node skyytrees.admin (the same node /tree reload needs; ops have it through hytale:Admin's "*").
    - File Skyy_SkyyTrees/trees.properties (names and keys unchanged; the kit rewrites only the changed line, comments and order kept,
      every change logged in Skyy_SkyyTrees/config-changes.log, the file's last 20 versions in Skyy_SkyyTrees/config-history/).
    - EVERY key TreeCfg.load reads is bound to a row (build-asserted), so every hand edit is noticed by the kit (logged via=file) and
      applied. All rows bind reload: the kit writes the line, then runs TreeKit.reload = TreeCfg.load (the same loader /tree reload
      runs: parse + clamp, no world access) + TreeAbil.ITEMOK.clear on the scheduler thread; the change applies within about a second.
      No restart rows (every value is read live from the TreeCfg volatile fields).
    - Rows (key, type, flags; L = live, D = danger (asks first), A = advanced):
        general:   tier.levels text L,D (check: 6 whole numbers 0-1000, each >= the one before = the loader's rule) - tokens.first int
                   0-100 L,D - tokens.every int 1-100 L,D - dust.xpPerDust int 1-1e9 L,D - dust.perTree table (file lines
                   dust.xpPerDust.<Tree>, column XP per Dust 1-1e9, add by typing; check: a tree name, capitals matter) L,D -
                   respec.cooldownMinutes int min 0-100000 L - respec.coins int coins 0-1e12 L - feedbackMs int ms 500-600000 L,A -
                   debug.extraTokens int 0-1000 L,D,A - debug.extraDust int 0-1e15 L,D,A
        abilities: ability.disabledWorlds text L - ability.maxRadius int blocks 1-16 L - vein.cooldownSec int s 0-86400 L -
                   feller.cooldownSec int s 0-86400 L - feller.maxPerLayer int 1-256 L - feller.needLeaves bool L - feller.maxHeight
                   int blocks 1-64 L - felled.nodes bool L
        nodes:     nodes.Mining / nodes.Foraging / nodes.Farming / nodes.Cooking / nodes.Acrobatics / nodes.Exploration = one table per
                   tree (file lines <Tree>.<Id>.<field>, one text column "Value", add by typing) L,D
      Ranges = the loader's clamps (typed values are refused, never clamped).
    - SPEC DEVIATIONS (deliberate): (1) spec 4.10's node tables with columns Max|Per level|On plus a nodeCost table Tokens|Dust B are
      built as one key-family table per tree whose entries ARE the file lines (MSpeed.max, MSpeed.per, MSpeed.B, MSpeed.tokens,
      MSpeed.enabled, MVein.base, MGems.items, AGrain.crops ...). trees.properties keeps one line per node field, and a kit table entry
      with 3 columns spread over 3 file lines would have to be a custom: table, which the kit cannot log hand edits for, cannot restore
      from History and whose hand edits the menu's Reload does not apply (CONFIG-CONTRACT "Known limits"). This way every node field -
      also base and the item / crop lists the spec's columns left out - is editable, logged, undoable and restorable. (2) The spec's
      "table dust.xpPerDust" is row dust.perTree (row keys must be unique; the file prefix stays dust.xpPerDust.). (3) dust.xpPerDust,
      dust.perTree and the six nodes.<Tree> tables carry danger (the spec gave no flag): like a Collections curve they move every
      player at once - the Dust rate every Dust balance, a node's tokens / B what every owner has spent (TreeCalc.tokSpent / dustSpent
      recompute it from the current costs, so a raise can make balances negative), its max / per / enabled every owner's effect. A
      danger table asks for every set / add / remove ("Change MSpeed.max in Mining nodes from 25 to 30?"); a check's own "?" question
      replaces that text (one confirm, never two).
    - Node table checks (TreeKit.checkNode, the loader's parse + clamp ranges): max whole 1-100, per number 0-1000 (asks first when a
      percent node gets more than 1 = 100% per level), B whole 0-1e9, tokens whole 0-100, enabled true / false, base number 0-1000
      (Vein Burst, Tree Feller, Double Jump), items = existing item ids, crops = names with a Plant_Crop_<C>_Block block; plain digits /
      a dot decimal, because the loader reads them with Long.parseLong / Double.parseDouble (a typed "2k" or "on" would load as the
      default while the page said it was saved). An unknown node or field, a wrong capital or a Coming-later slot ASKS ("this line would
      do nothing - save it anyway?") instead of refusing, so an export / import / restore carrying old lines (the Acrobatics.RDodge.*
      lines 0.2.1 left in place) never fails. Removing an entry is always allowed: the built-in default applies again.
    - /tree reload (unchanged command: node skyytrees.admin, empty permission-group list): the same re-read as 0.2.1 (item-id
      cache, unreadable player files, TreeCfg.load with its summary) and then the kit's reload op (via=command), which logs every value
      changed by hand in config-changes.log; the reply adds the kit's line ("Read the files again: 1 value changed by hand ...").
    - Header note: node ids and names are the comments in trees.properties; hand edits: /tree reload or Reload file.
  PLAYER SETTINGS (research/Settings-Spec.md 1.3 + 3.2; SkyyMenu 0.2+ /settings, tab Cooking & Trees):
    - setup() registers trees.bonus "Tree bonus totals" and trees.abilities "Vein Burst and Tree Feller" (category cooking, default ON)
      with TreeStore.regSetting (settings:def:<key> + settings:fn:register; the creating bridge()).
    - Gates (only the sendMessage call, never the work): TreeMsg.flush (the aggregated "Tree bonus: ..." line; take() still clears the
      pending totals first, so a hidden line is dropped, not queued), TreeAbil.vein ("Vein Burst! ...") and TreeAbil.feller ("Tree
      Feller! ..."): the break, the cooldown and every drop happen either way.
    - TreeStore.notifyOn = the spec helper: settings:fn:get when SkyyMenu is there (before it, the one-shot moveQuiet: a profile with
      the old /tree quiet=true sets trees.bonus OFF with onlyIfUnset and, on TRUE, clears quiet in that profile file); without SkyyMenu
      trees.bonus = !quiet and trees.abilities = on, exactly 0.2.1. Player files are still only read on world threads (flush, vein,
      feller and /tree quiet all run there).
    - /tree quiet: with settings:fn:set it flips trees.bonus and answers "[Trees] Tree bonus messages hidden/shown. More switches:
      /settings"; without SkyyMenu the 0.2.1 per-profile toggle runs unchanged. Its help text no longer says ability messages always show.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r4-trees, deleted afterwards; 140 checks, 0 fails): all
    31 classes load under -Xverify:all; a fresh start writes the default file, every loaded value equals 0.2.1's defaults and
    CfgPub.start leaves trees.properties byte for byte; config:def header (24 rows, 3 categories); every row reads back its default;
    export changed -> import preview = nothing to change; danger rows ask first and a confirm changes nothing; scalar sets write only
    their line (comments kept) and TreeKit.reload applies them (tokens.every, feller.cooldownSec 10s -> 10000 ms, needLeaves off,
    disabledWorlds list, respec 2min, feedbackMs); range refusals; tier.levels check (5 bad forms refused, equal tiers allowed);
    node tables (62 Mining entries, filter, max / per / enabled / base / items checks, remove -> built-in default and the line gone,
    add back, the ask-first cases: unknown node, wrong capitals, unknown field, base on a non-base node, Coming-later slot, per 2 on a
    percent node); dust.perTree (asks first, own Mining rate, remove Acrobatics -> 2); a hand edit is found by the reload op, logged
    via=file and applied; table changes logged as nodes.Mining[MSpeed.max]; file history + restore preview; export all / changed ->
    import preview = nothing to change; restore / import APPLY refused without an admin UUID (contract); an old 0.2-era file is
    upgraded by the 0.2.1 migration first and its stale Acrobatics.RDodge.* lines are listed, ask first on change, never block an
    export -> import and can be removed; settings: without SkyyMenu trees.bonus = !quiet and trees.abilities = on, settings:def
    written, the quiet move calls settings:fn:set {uuid, trees.bonus, FALSE, TRUE} once and clears quiet + saves, then both
    switches are read from the registry. NOT covered there: the real PermissionsModule / Item asset map / scheduler (in-game steps).
    Review fix (2026-09-25, a second scratch harness, 67 checks, 0 fails): the six node tables are published with danger (13 danger
    rows); a node set / add / remove answers confirm ("Change MSpeed.max in Mining nodes from 25 to 30? ...") and changes nothing, yes
    applies it (TreeCfg.MAX, file line, log nodes.Mining[MSpeed.max]); out-of-range / "off" are refused before any confirm; an unknown
    id asks only its own "would do nothing" question; feller.cooldownSec still saves without one; export all -> import preview =
    nothing to change; the /tree reload order (hand edit, direct TreeCfg.load, kit reload op) logs "1 value changed by hand" and the
    queued second load leaves the same values.
  UNVERIFIED (needs Skyy's in-game test): the Trees page in SkyyMenu 0.3 Server Setup (rows, the node tables' paging / filter / add),
    the settings switches in /settings, the quiet move with a real SkyyMenu, and the kit's scheduler save path in a running server.

=== SkyyTrees 0.2.1 notes (history; still true unless 0.2.2 above says otherwise) ===
0.2.1 = HANDOFF feedback round 2''')
rep('''Run:   python build_skyytrees_0.2.1.py            -> SkyyTrees/SkyyTrees-0.2.1.jar
       python build_skyytrees_0.2.1.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''',
    '''Run:   python build_skyytrees_0.2.2.py            -> SkyyTrees/SkyyTrees-0.2.2.jar
       python build_skyytrees_0.2.2.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''')
rep('import skyybuild as B\n', 'import skyybuild as B\nimport skyycfg as CFG   # 0.2.2: the admin config kit (tools/CONFIG-CONTRACT.md)\n')
rep('VERSION = "0.2.1"', 'VERSION = "0.2.2"')

# ================================================================ default trees.properties: one comment line (a fresh file only)
rep('''      "# Comments must stay on their own lines. A missing key uses the built-in default.",
''', '''      "# Comments must stay on their own lines. A missing key uses the built-in default.",
      "# Also editable in game: SkyWynn Menu -> Server Setup -> Trees (SkyyMenu 0.3). Every change is logged in config-changes.log.",
''')

# ================================================================ TreeStore: the Settings-Spec 1.3 / 3.2 helper (after saveSoon)
after('''M(sto, r"""
public static void saveSoon(String k) {
  dirty(k);
  try { @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.SaveTask(k)); } catch (Throwable t) { }
}""")
''', r'''# 0.2.2 player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3 + 3.2). No SkyyMenu = no answer = 0.2.1 behaviour:
# trees.bonus follows the per-profile quiet flag, trees.abilities is on. moveQuiet = the one-shot move of an old /tree quiet=true into the
# per-player switch (onlyIfUnset); it may read a player file, and every caller runs on a world thread (flush, vein, feller, /tree quiet).
M(sto, r"""
public static synchronized boolean clearQuiet(@PKG@.TreeData d) {
  if (!d.quiet) return false;
  d.quiet = false;
  return true;
}""")
M(sto, r"""
public static void moveQuiet(java.util.UUID u) {
  String k = pkey(u);
  @PKG@.TreeData d = dataK(k, u);
  if (d == null || !d.quiet || d.bad) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  if (!Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "trees.bonus", Boolean.FALSE, Boolean.TRUE }))) return;
  if (clearQuiet(d)) dirty(k);
}""")
M(sto, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      if ("trees.bonus".equals(key)) moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if ("trees.bonus".equals(key)) return !data(u).quiet;
  return true;
}""")
M(sto, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyTrees", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
''')

# ================================================================ the three gated messages (Settings-Spec 3.2 table)
rep('''  if (s == null) return;
  if (@PKG@.TreeStore.data(u).quiet) return;
  pr.sendMessage(@MSG@.raw(s).color("#b8f0a0"));''', '''  if (s == null) return;
  if (!@PKG@.TreeStore.notifyOn(u, "trees.bonus")) return;
  pr.sendMessage(@MSG@.raw(s).color("#b8f0a0"));''')
rep('''  @PKG@.TreeMsg.say(pr, "Vein Burst! +" + n + " ore (ready again in " + (cd / 1000L) + " s)", "#ffc300");''',
    '''  if (@PKG@.TreeStore.notifyOn(u, "trees.abilities")) @PKG@.TreeMsg.say(pr, "Vein Burst! +" + n + " ore (ready again in " + (cd / 1000L) + " s)", "#ffc300");''')
rep('''  @PKG@.TreeMsg.say(pr, "Tree Feller! +" + n + (n == 1 ? " log" : " logs") + " on this level" + (cd > 0L ? " (ready again in " + (cd / 1000L) + " s)" : ""), "#ffc300");''',
    '''  if (@PKG@.TreeStore.notifyOn(u, "trees.abilities")) @PKG@.TreeMsg.say(pr, "Tree Feller! +" + n + (n == 1 ? " log" : " logs") + " on this level" + (cd > 0L ? " (ready again in " + (cd / 1000L) + " s)" : ""), "#ffc300");''')

# ================================================================ /tree quiet: flips trees.bonus when SkyyMenu is there (Settings-Spec 3.2)
after('''  boolean q = @PKG@.TreeStore.flipQuiet(d);
  if (!d.bad) @PKG@.TreeStore.dirty(k);
  return q;
}""")
''', r'''# 0.2.2: with SkyyMenu's settings registry /tree quiet is a shortcut for the trees.bonus switch (notifyOn first = the one-shot quiet
# move, so the flip starts from what the player sees); without it the 0.2.1 per-profile toggle above runs unchanged
M(ops, r"""
public static String quietText(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  java.util.function.Function sf = @PKG@.TreeCalc.fn("settings:fn:set");
  if (sf != null) {
    boolean on = @PKG@.TreeStore.notifyOn(u, "trees.bonus");
    Object r = null;
    try { r = sf.apply(new Object[] { u, "trees.bonus", Boolean.valueOf(!on) }); } catch (Throwable t) { r = null; }
    if (!Boolean.TRUE.equals(r)) return "[Trees] Could not save the setting - try /settings (tab Cooking).";
    return on ? "[Trees] Tree bonus messages hidden. More switches: /settings" : "[Trees] Tree bonus messages shown. More switches: /settings";
  }
  boolean q = quiet(pr);
  return q ? "[Trees] Tree bonus messages hidden. /tree quiet again to show them." : "[Trees] Tree bonus messages shown.";
}""")
''')
rep('''  super("quiet", "Toggle the 'Tree bonus' chat line (ability messages always show)");''',
    '''  super("quiet", "Toggle the 'Tree bonus' chat line (more switches: /settings)");''')
rep('''  boolean q = @PKG@.TreeOps.quiet(pr);
  pr.sendMessage(@MSG@.raw(q ? "[Trees] Tree bonus messages hidden. /tree quiet again to show them." : "[Trees] Tree bonus messages shown."));''',
    '''  pr.sendMessage(@MSG@.raw(@PKG@.TreeOps.quietText(pr)));''')

# ================================================================ the admin config kit (before the commands: they and the plugin use it)
before('''# ================= commands (HANDOFF command rules) =================
''', r'''# ================= 0.2.2: admin config kit (research/Server-Setup-Spec.md 4.10, tools/CONFIG-CONTRACT.md, tools/skyycfg.py) =========
# Every key TreeCfg.load reads is a row (asserted below), so a hand edit of any of them is noticed (logged via=file) and applied. Every row
# binds reload: the kit rewrites the one line, then runs TreeKit.reload (TreeCfg.load = the /tree reload loader, parse + clamp only, no
# world access) on the scheduler thread. The node lines are key-family tables, one per tree, whose entries ARE the file lines
# (<Id>.<field>): trees.properties keeps one line per node field, and a multi-column entry spread over several lines would need a
# custom: table (no hand-edit log, no History restore - CONFIG-CONTRACT "Known limits"). Ranges = the loader's clamps.
CFG_CATS = [("general", "General"), ("abilities", "Abilities"), ("nodes", "Nodes")]
NODE_HELP = "Entry = node id + field: max, per, B, tokens, enabled (+ base, items, crops). Removed = built-in."
CFG_NOTE = "Node ids and names: the comments in trees.properties. Hand edits: /tree reload or Reload file."
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
CFG_ROWS = [
    ("tier.levels", "Tier unlock levels", "general", "text", "1,10,20,30,45,60", "", "60", "", "", "live,danger",
     "Skill level that opens tiers I to VI: 6 whole numbers 0-1000, each at least the one before.", "reload;check=TreeKit.checkTiers"),
    ("tokens.first", "Tokens at skill level 1", "general", "int", "1", "0", "100", "", "", "live,danger",
     "Tokens a player has at level 1 of a skill; then 1 more every N levels (next row).", "reload"),
    ("tokens.every", "Levels per extra token", "general", "int", "5", "1", "100", "", "", "live,danger",
     "One more token every N levels. Fewer tokens can make a balance negative (a respec is then free).", "reload"),
    ("dust.xpPerDust", "Skill XP per Dust", "general", "int", "10", "1", "1000000000", "", "", "live,danger",
     "Dust = total skill XP / this, for every tree without its own rate (Dust rate per tree).", "reload"),
    ("dust.perTree", "Dust rate per tree", "general", "table", "", "1", "1000000000", "int;type;XP per Dust", "", "live,danger",
     "Entry = a tree name (Acrobatics). Removed: Acrobatics 2, Exploration 5, the others the rate above.",
     "reload@trees.properties:dust.xpPerDust.;check=TreeKit.checkDust"),
    ("respec.cooldownMinutes", "Respec cooldown per tree", "general", "int", "10", "0", "100000", "", "min", "live",
     "Minutes before a player can reset the same tree again. 0 = no wait.", "reload"),
    ("respec.coins", "Respec price", "general", "int", "0", "0", "1000000000000", "", "coins", "live",
     "Coins a respec costs (needs SkyyCoins). 0 = free. A negative balance always respecs for free.", "reload"),
    ("feedbackMs", "Tree bonus line every", "general", "int", "2000", "500", "600000", "", "ms", "live,adv",
     "The 'Tree bonus: ...' chat line is sent at most this often per player.", "reload"),
    ("debug.extraTokens", "Test: extra tokens", "general", "int", "0", "0", "1000", "", "", "live,danger,adv",
     "Testing only: extra tokens in every tree for every player. Keep 0 on a real server.", "reload"),
    ("debug.extraDust", "Test: extra Dust", "general", "int", "0", "0", "1000000000000000", "", "", "live,danger,adv",
     "Testing only: extra Dust in every tree for every player. Keep 0 on a real server.", "reload"),
    ("ability.disabledWorlds", "Abilities off in worlds", "abilities", "text", "", "", "2000", "", "", "live",
     "Comma list of world names where Spread, Vein Burst and Tree Feller never run (e.g. the hub).", "reload"),
    ("ability.maxRadius", "Ability reach", "abilities", "int", "6", "1", "16", "", "blocks", "live",
     "Sideways reach of Spread, Vein Burst and Tree Feller (also how high Vein Burst reaches).", "reload"),
    ("vein.cooldownSec", "Vein Burst cooldown", "abilities", "int", "40", "0", "86400", "", "s", "live",
     "Seconds between two Vein Bursts of one player.", "reload"),
    ("feller.cooldownSec", "Tree Feller cooldown", "abilities", "int", "5", "0", "86400", "", "s", "live",
     "Seconds between two Tree Fellers of one player.", "reload"),
    ("feller.maxPerLayer", "Tree Feller max logs", "abilities", "int", "64", "1", "256", "", "", "live",
     "The max level breaks every log of the tree on the cut's level, up to this many.", "reload"),
    ("feller.needLeaves", "Tree Feller needs leaves", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: only wood that touches leaves (natural trees). Placed logs never count either way.", "reload"),
    ("feller.maxHeight", "Leaves check reach", "abilities", "int", "32", "1", "64", "", "blocks", "live",
     "How far above or below the cut the leaves check looks. Nothing up there is broken.", "reload"),
    ("felled.nodes", "Felled logs roll bonuses", "abilities", "bool", "true", "", "", "", "", "live",
     "Logs of a felled tree roll Sap Tapper, Replanter and Pocket Change (SkyySkills 0.4.2).", "reload"),
] + [("nodes." + _tn, _tn + " nodes", "nodes", "table", "", "", "", "text;type;Value", "", "live,danger", NODE_HELP,
      "reload@trees.properties:%s.;check=TreeKit.checkNode" % _tn) for _tn in TREES]
# every key of the default file is bound: exactly (a scalar row) or through a key family (dust.xpPerDust.<Tree>, <Tree>.<Id>.<field>)
_fams = ["dust.xpPerDust."] + [_tn + "." for _tn in TREES]
_exact = set(r[0] for r in CFG_ROWS if r[3] != "table")
for _k in CFG.parse_props(DEFAULTS):
    assert _k in _exact or any(_k.startswith(_p) for _p in _fams), "trees.properties key without a config row: " + _k
assert len(_exact) == 17 and len(CFG_ROWS) == 18 + len(TREES)
KIT = CFG.emit(pool, PKG, MOD="SkyyTrees", TITLE="Trees", VERSION=VERSION, NODE="skyytrees.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyTrees/trees.properties"], NOTE=CFG_NOTE, RELOAD="TreeKit.reload", KEEP=20,
               DEFAULTS={"trees.properties": DEFAULTS}, ITEMS=ITEM_IDS)

# TreeKit: the kit's hooks (check=, the reload routine) and /tree reload. Hooks never throw (the kit also catches) and never touch a
# world; check= answers null = fine, text = refuse, "?text" = ask first (spec 1.4.2). Checks mirror TreeCfg.apply: the same parse
# (Long.parseLong / Double.parseDouble / true|false) and the same ranges, so a value the page accepts is a value the loader uses.
kitc = pool.makeClass(PKG + ".TreeKit")
M(kitc, r"""
public static String entryOf(String key) {
  if (key == null) return null;
  int b = key.indexOf('[');
  if (b < 0 || !key.endsWith("]")) return null;
  return key.substring(b + 1, key.length() - 1).trim();
}""")
M(kitc, r"""
public static String tableOf(String key) {
  if (key == null) return "";
  int b = key.indexOf('[');
  return b < 0 ? key : key.substring(0, b);
}""")
M(kitc, r"""
public static String wholeIn(String v, long lo, long hi, String what) {
  long x = 0L;
  try { x = Long.parseLong(v.trim()); } catch (Throwable t) { return what + " must be a whole number from " + lo + " to " + hi + " (plain digits)."; }
  if (x < lo || x > hi) return what + " must be a whole number from " + lo + " to " + hi + ".";
  return null;
}""")
M(kitc, r"""
public static String numIn(String v, double lo, double hi, String what) {
  double x = 0.0;
  try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { return what + " must be a number from " + @PKG@.TreeDefs.num(lo) + " to " + @PKG@.TreeDefs.num(hi) + " (with a dot, like 0.02)."; }
  if (Double.isNaN(x) || Double.isInfinite(x) || x < lo || x > hi) return what + " must be a number from " + @PKG@.TreeDefs.num(lo) + " to " + @PKG@.TreeDefs.num(hi) + ".";
  return null;
}""")
# the asset map is always there in a running server; if it cannot be asked (not loaded yet) the id is accepted - TreeAbil.itemOk checks
# every id again before anything is given and warns once about an unknown one
M(kitc, r"""
public static boolean itemExists(String id) {
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return true; }
}""")
M(kitc, r"""
public static String listCheck(String v, boolean crops) {
  String[] xs = @PKG@.TreeCfg.split(v);
  if (xs.length == 0) return "List at least one " + (crops ? "crop" : "item id") + " - to stop the node, set its enabled entry to false.";
  for (int k = 0; k < xs.length; k++) {
    String x = xs[k];
    if (crops) { if (!itemExists("Plant_Crop_" + x + "_Block")) return "Unknown crop: " + x + " (there is no Plant_Crop_" + x + "_Block block)."; }
    else if (!itemExists(x)) return "Unknown item: " + x + ".";
  }
  return null;
}""")
# percent nodes (their page value is a %): per above 1 is more than 100% per level - allowed (the loader takes up to 1000), asked first
M(kitc, r"""
public static boolean fraction(int kd) {
  return kd != @K_HP@ && kd != @K_STA@ && kd != @K_RJMP@ && kd != @K_VEIN@ && kd != @K_FELLER@ && kd != @K_SOON@;
}""")
M(kitc, r"""
public static String checkTiers(String key, String value) {
  if (value == null) return null;
  String[] xs = @PKG@.TreeCfg.split(value);
  if (xs.length != 6) return "Needs exactly 6 whole numbers, like 1,10,20,30,45,60 (tiers I to VI).";
  int prev = 0;
  for (int i = 0; i < 6; i++) {
    int v = -1;
    try { v = Integer.parseInt(xs[i]); } catch (Throwable t) { return xs[i] + " is not a whole number - use 6 numbers like 1,10,20,30,45,60."; }
    if (v < 0 || v > 1000) return "Each tier level must be 0 to 1000 (tier " + @PKG@.TreeDefs.roman(i + 1) + " is " + v + ").";
    if (i > 0 && v < prev) return "Tier " + @PKG@.TreeDefs.roman(i + 1) + " (" + v + ") must not be below tier " + @PKG@.TreeDefs.roman(i) + " (" + prev + ").";
    prev = v;
  }
  return null;
}""")
M(kitc, r"""
public static String checkDust(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (e == null) return null;
  for (int t = 0; t < @PKG@.TreeDefs.NT; t++) if (@PKG@.TreeDefs.TREES[t].equals(e)) return null;
  return "?" + e + " is not a tree (Mining, Foraging, Farming, Cooking, Acrobatics, Exploration - capitals matter), so this line would do nothing. Save it anyway?";
}""")
M(kitc, r"""
public static String checkNode(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (e == null) return null;
  String tk = tableOf(key);
  String tn = tk.startsWith("nodes.") ? tk.substring(6) : tk;
  int t = -1;
  for (int k = 0; k < @PKG@.TreeDefs.NT; k++) if (@PKG@.TreeDefs.TREES[k].equals(tn)) t = k;
  if (t < 0) return null;
  int dot = e.lastIndexOf('.');
  String id = dot > 0 ? e.substring(0, dot) : e;
  String f = dot > 0 ? e.substring(dot + 1) : "";
  int i = -1;
  String near = null;
  for (int s = 0; s < 12; s++) {
    int j = t * 12 + s;
    if (@PKG@.TreeDefs.ID[j].equals(id)) i = j;
    else if (@PKG@.TreeDefs.ID[j].equalsIgnoreCase(id)) near = @PKG@.TreeDefs.ID[j];
  }
  if (i < 0) {
    if (near != null) return "?" + e + " does nothing - capitals matter, the node is " + near + " (" + near + "." + f + "). Save it anyway?";
    return "?" + id + " is not a " + tn + " node (the ids are in trees.properties, like " + @PKG@.TreeDefs.ID[t * 12] + ") - this line would do nothing. Save it anyway?";
  }
  if (@PKG@.TreeDefs.soon(i)) return "?" + id + " is a Coming later slot and always off - this line does nothing. Save it anyway?";
  int kd = @PKG@.TreeDefs.KIND[i];
  boolean hasBase = kd == @K_VEIN@ || kd == @K_FELLER@ || kd == @K_DJUMP@;
  String lk = @PKG@.TreeDefs.LISTKEY[i];
  String nm = @PKG@.TreeDefs.NAME[i] + " " + f;
  if (f.equals("max")) return wholeIn(value, 1L, 100L, nm);
  if (f.equals("B")) return wholeIn(value, 0L, 1000000000L, nm);
  if (f.equals("tokens")) return wholeIn(value, 0L, 100L, nm);
  if (f.equals("per")) {
    String r = numIn(value, 0.0, 1000.0, nm);
    if (r != null) return r;
    double x = Double.parseDouble(value.trim());
    if (fraction(kd) && x > 1.0) return "?" + nm + " " + value.trim() + " is " + @PKG@.TreeDefs.pct(x) + " per level (0.02 = 2%). Save it anyway?";
    return null;
  }
  if (f.equals("enabled")) {
    String b = value.trim();
    if (b.equalsIgnoreCase("true") || b.equalsIgnoreCase("false")) return null;
    return nm + " must be true or false.";
  }
  if (f.equals("base")) {
    if (hasBase) return numIn(value, 0.0, 1000.0, nm);
    return "?Only Vein Burst, Tree Feller and Double Jump use base - " + e + " does nothing. Save it anyway?";
  }
  if (lk.length() > 0 && f.equals(lk)) return listCheck(value, lk.equals("crops"));
  return "?" + f + " is not a field of " + id + " (max, per, B, tokens, enabled" + (hasBase ? ", base" : "") + (lk.length() > 0 ? ", " + lk : "") + ") - this line would do nothing. Save it anyway?";
}""")
# RELOAD (kit.write checks it): after every kit write, and for every hand edit the kit notices
M(kitc, r"""
public static void reload() {
  @PKG@.TreeCfg.load();
  @PKG@.TreeAbil.ITEMOK.clear();
}""")
# /tree reload: the 0.2.1 re-read (item-id cache, unreadable player files, TreeCfg.load and its summary), then the kit's reload op, which
# logs every value changed by hand (via=file) and, when it found any, queues the reload routine once more on the save task (harmless:
# TreeCfg.load is synchronized and re-parses the same file into the same values). The direct TreeCfg.load stays on purpose: it keeps the
# 0.2.1 reply (the loader summary) and applies the file even when the kit has nothing new to merge.
M(kitc, r"""
public static String reloadCmd(@PR@ pr) {
  @PKG@.TreeAbil.ITEMOK.clear();
  int bad = @PKG@.TreeStore.dropBad();
  String sum = @PKG@.TreeCfg.load();
  String k = "";
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) k = " " + String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { k = ""; }
  return "[Trees] trees.properties reloaded: " + sum + (bad > 0 ? "; " + bad + " unreadable player file(s) will be read again" : "") + "." + k;
}""")

''')
rep('''  @PKG@.TreeAbil.ITEMOK.clear();
  int bad = @PKG@.TreeStore.dropBad();
  pr.sendMessage(@MSG@.raw("[Trees] trees.properties reloaded: " + @PKG@.TreeCfg.load() + (bad > 0 ? "; " + bad + " unreadable player file(s) will be read again" : "")));''',
    '''  pr.sendMessage(@MSG@.raw(@PKG@.TreeKit.reloadCmd(pr)));''')

# ================================================================ plugin: switches in setup, kit published LAST, flushed at shutdown
rep('''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyTrees] @VERSION@ ready - /tree; " + sum + "; " + sk);
}""".replace("@VERSION@", VERSION))''', '''  @PKG@.TreeStore.regSetting("trees.bonus", "Tree bonus totals", "cooking", true, "Tree bonus: +2 Copper Ore, extra drops x1, +3 coins");
  @PKG@.TreeStore.regSetting("trees.abilities", "Vein Burst and Tree Feller", "cooking", true, "Vein Burst! +6 ore (ready again in 40 s)");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyTrees] @VERSION@ ready - /tree; " + sum + "; " + sk + "; server settings: SkyWynn Menu -> Server Setup -> Trees");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@VERSION@", VERSION))''')
rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
''', '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, fx, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, vcmd, qcmd, rcmd, cmd, pl)
for c in ALL:
    c.writeFile(OUT)
print("classes written:", len(ALL))''', '''ALL = (defs, cfg, dat, sto, stk, calc, fx, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, kitc, vcmd, qcmd, rcmd, cmd, pl)
for c in ALL:
    c.writeFile(OUT)
KIT.write(OUT)   # deferred kit checks (TreeKit hooks + reload routine exist with the right signatures), then the 7 Cfg* classes
print("classes written:", len(ALL) + 7)''')

# ================================================================ manifest text
rep('''Per profile with SkyyProfiles (optional). Reads SkyySkills through the skyy bridge; zero dependencies."''',
    '''Per profile with SkyyProfiles (optional). Server settings editable in game (SkyyMenu 0.3 Server Setup). Reads SkyySkills through the skyy bridge; zero dependencies."''')

# ================================================================ sanity
assert 'VERSION = "0.2.2"' in s and "DERIVED from build_skyytrees_0.2.1.py by tools/trees_0_2_2_patch.py" in s
assert s.count("import skyycfg as CFG") == 1 and s.count("KIT = CFG.emit(") == 1 and s.count("KIT.write(OUT)") == 1
# publish at the END of setup (after TreeCfg.load and everything else), flush at shutdown
_su = s[s.index("public void setup() {"):s.index('}""".replace("@VERSION@", VERSION))')]
assert _su.index("String sum = @PKG@.TreeCfg.load();") < _su.index("@PKG@.CfgPub.start(") and _su.rstrip().endswith("@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());")
assert s.count("@PKG@.CfgPub.start(") == 1 and s.count("try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }") == 1
# every key the loader (TreeCfg.apply) reads is a config row (scalar) or inside a key-family table
_ap = s[s.index("public static void apply(java.util.Properties p) {"):s.index("public static void writeAtomic(byte[] data)")]
_read = set(re.findall(r'(?:lng|str|dbl|bool)\(p, "([A-Za-z.]+)"', _ap))
_rows = set(re.findall(r'^    \("([a-z][A-Za-z.]+)", "', s[s.index("CFG_ROWS = ["):s.index("KIT = CFG.emit(")], re.M))
assert _read - {"dust.xpPerDust."} <= _rows and "dust.xpPerDust." in _read and len(_read) == 18, (_read, _rows)
assert 'reload@trees.properties:dust.xpPerDust.;' in s and '"reload@trees.properties:%s.;check=TreeKit.checkNode" % _tn' in s
# danger on every row that moves every player at once: the token / Dust rows and all six node tables (costs are recomputed from the
# current TreeCfg.TOK / B for every owner, max / per / enabled change every owner's effect)
assert s.count('"text;type;Value", "", "live,danger", NODE_HELP,') == 1 and s.count('"int;type;XP per Dust", "", "live,danger",') == 1
assert 'String k = @PKG@.TreeDefs.TREES[i / 12] + "." + @PKG@.TreeDefs.ID[i] + ".";' in _ap   # the node key family = <Tree>.<Id>.<field>
# the settings: two switches, three gated sends, the quiet move, no ungated quiet check left
assert s.count('regSetting("trees.bonus"') == 1 and s.count('regSetting("trees.abilities"') == 1
assert s.count('notifyOn(u, "trees.abilities")') == 2 and s.count('if (!@PKG@.TreeStore.notifyOn(u, "trees.bonus")) return;') == 1
assert "TreeStore.data(u).quiet) return;" not in s and s.count('Boolean.FALSE, Boolean.TRUE }') == 1
# unchanged engine / command rules
assert s.count("registerSystem(") == 2   # one registerSystem per class: TreeDmgSys + TreeTick
assert s.count('setPermissionGroups(new String[] { "hytale:Adventurer" })') == 3 and s.count("setPermissionGroups(new String[0])") == 1
assert s.count('  requirePermission("skyytrees.admin");') == 1   # the /tree reload constructor (the 0.1 notes mention it once more)
assert "--deploy" in s   # the script keeps its optional deploy switch; workflows never pass it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2.1
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
