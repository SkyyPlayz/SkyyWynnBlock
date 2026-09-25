r"""Derive SkyyRolls/build_skyyrolls_0.1.5.py from the LIVE 0.1.4 (tools/deploy_set.py pins SkyyRolls 0.1.4).
Run: python tools/rolls_0_1_5_patch.py   then   python SkyyRolls/build_skyyrolls_0.1.5.py   (edit THIS file, never the generated one)

0.1.5 = research/Server-Setup-Spec.md 4.2 (wave 1 of section 7) + the /rolls permission fix that section names.

1. IN-GAME SERVER SETUP (tools/CONFIG-CONTRACT.md, tools/skyycfg.py; Skyy's rule: everything a server owner might change is doable in
   game, and the files stay and always match). SkyyRolls has ONE admin setting family: the Reforge Anvil costs in
   Skyy_SkyyRolls/reforge.properties (cost.<quality id>=<coins>, cost.default for every other quality). Spec 4.2: "Adopt as one table
   `cost` (entry = quality, column `Coins`, add `type`)", int coins 0-1e12, live, category `reforge`. So:
     row  cost | Reforge cost by rarity | reforge | table | "" | 0 | 1000000000000 | int;type;Coins | coins | live
     bind reload@Skyy_SkyyRolls/reforge.properties:cost.;check=Reforge.checkCost        RELOAD = Reforge.load
   - The file name, every key and the value format stay exactly as 0.1.4 wrote and read them (spec 7: the file key never changes).
     Reforge.load (0.1.4, unchanged) stays the one loader: setup() calls it, the /reforge modified-time check (maybeReload) calls it,
     and now the kit calls it after its atomic write (a `reload:` binding: the kit edits only that entry's line in memory, keeps every
     comment / blank line / line ending, writes on HytaleServer.SCHEDULED_EXECUTOR about 500 ms later, then runs the routine outside
     every kit lock). Reforge.load only parses the file into a fresh HashMap and swaps the volatile COSTS reference, so it is safe on
     the scheduler thread while world threads read COSTS.
   - Removing an entry: Reforge.load seeds the built-in ladder (QIDS/QDEF/DEF_OTHER) before it reads the file, so a removed rarity goes
     back to its BUILT-IN cost (never free; 0 = free). The row's help says so. SkyyMenu confirms every remove itself.
   - Not `danger`: spec 4.2 lists the costs as L only (they change what a reforge costs, no coins or items are moved or lost).
   - check=Reforge.checkCost (kit contract: a table's check gets "cost[<entry>]" and the new value, null for a removal; null = fine,
     text = refuse, "?text" = ask first; it runs with no kit lock held):
       * refuses an entry that differs only in upper/lower case from one already in the list ("rare" next to "Rare"): Reforge.load
         lower-cases every quality id, so both lines would describe one rarity and the file order would pick the price;
       * refuses "Default" / "DEFAULT" (type default) and a known quality id in the wrong case (type it exactly: Rare);
       * asks before adding an id that no loaded quality has (a typo would be a dead line; a quality added by a mod later is still
         possible with the confirm);
       * engine lookups fail open (bare JVM, asset API drift): never blocks an admin because the check itself broke - but never
         silently either: each fail-open path (rarity ids unreadable or empty, the table's own entries unreadable, the rarity list
         for the question unbuildable) writes one "[SkyyRolls] reforge cost check ..." WARNING per server run (Reforge.checkWarn;
         once per run, not per call, because an import runs the check for every entry).
   - DEFAULTS = the exact default file text (one Python constant REFORGE_TEXT generates the Java QIDS/QDEF/DEF_OTHER arrays, the Java
     defaultsText() literal and the kit's DEFAULTS, so they can never drift): the kit uses it for export scope "changed" (only entries
     that differ from the default ladder) and to seed the file if it is missing when the kit must write.
   - The default file text gets ONE new comment line ("Admins can also change these in game: SkyWynn Menu -> Server Setup -> Rolls
     (/modconfig).") - only in a file created from now on; an existing reforge.properties is never rewritten until an admin changes an
     entry, and then only that entry's line changes. Costs, messages and the page are otherwise byte-identical to 0.1.4.
   - Publication: PKG.CfgPub.start(getDataDirectory().getParent(), getLogger()) is the LAST statement of setup() (after Reforge.load
     and the command / event registration), so config:def:SkyyRolls + config:fn:SkyyRolls are on the bridge whether or not SkyyMenu
     is installed; shutdown() (new) calls PKG.CfgPub.shutdown() (writes a pending change and log lines now) then super.shutdown().
   - Hand edits keep working exactly as in 0.1.4 (applied the next time someone opens /reforge); the kit also notices them at its next
     write of the file or on Server Setup's Reload, logs them via=file and runs Reforge.load.
   - Admin commands: SkyyRolls has no command that writes a config value (/rolls writes items only), so nothing had to be routed through
     PKG.CfgFn.cmdSet.
   Left out (spec 4.2 "make configurable later"): the rarity-based roll ranges (unbuilt, SkyyGear-Plan.md). Also left as code on
   purpose: the placeholder STATS maxima, the REFORGES name list and DEFAULT_ITEM (Skyy is still designing the SkyyGear stat list; a
   row now would publish a setting that the next SkyyGear version replaces), and no part switch (spec section 3 lists none for
   SkyyRolls).

2. /rolls PERMISSION FIX (spec 4.2 "Fix in the same version: /rolls has no requirePermission although its help says admin ->
   requirePermission("skyyrolls.admin")"). The root RollsCmd and its four subcommands (read, reroll, give, clear) each call
   requirePermission("skyyrolls.admin") - the SkyyRanks 0.1 pattern (root AND every subcommand). Engine facts (HytaleServer.jar
   bytecode, tools/dev/bcfull.py, 2026-09-25): AbstractCommand.requirePermission(String) sets the permission field
   (PermissionQuery.of); setOwner() generates the versioned auto node only while that field is still null, so the explicit node sticks;
   hasPermission(sender) on a subcommand checks its own node and then, because no permission groups are set, the parent's node - both
   skyyrolls.admin now. No command here calls setPermissionGroups, so CommandManager.createVirtualPermissionGroups never puts the node
   into a group (tools/ci/lint.py perm_group_leaks: the root is registered with registerCommand, the subcommands are added by the root,
   neither side grants groups). Result: ordinary players (hytale:Adventurer) still cannot run /rolls (same as 0.1.4), ops ("*") can,
   and the node no longer changes with every version (0.1.4: skyy.0.1.4_skyyrolls.command.rolls...), so a SkyyRanks rank or /perm can
   grant skyyrolls.admin - which is also the node the config kit re-checks for every cost change. /reforge is untouched (player
   command, setPermissionGroups hytale:Adventurer).

3. DEAD CODE: RollsGiveVariantCmd (the "give <itemId>" usage variant) was added with addUsageVariant in 0.1.1 only; since 0.1.2 give reads
   its words from ctx.getInputString() with setAllowsExtraArguments(true) (tools/rolls_0_1_2_patch.py) and nothing adds the variant
   any more - the class was still compiled and shipped. Removed (makeClass, constructor, execute, writeFile).

4. Player Settings (research/Settings-Spec.md): none. Section 3.13 lists SkyyRolls under "No change (admin tool)"; 0.1.4's /reforge page
   only answers the player's own clicks inside the page, the join tooltip refresh only logs, so there is no unprompted sendMessage or
   popup to gate and no switch to register.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.4.py")
dst = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')

# ---------------- docstring ----------------
rep('''"""SkyyRolls 0.1.4 - build script (javassist via jpype).''', '''"""SkyyRolls 0.1.5 - build script (javassist via jpype).''')
rep('''Run:   python build_skyyrolls_0.1.4.py            -> SkyyRolls/SkyyRolls-0.1.4.jar
       python build_skyyrolls_0.1.4.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world''',
    '''Generated by tools/rolls_0_1_5_patch.py from build_skyyrolls_0.1.4.py - edit the patch, not this file.
Run:   python build_skyyrolls_0.1.5.py            -> SkyyRolls/SkyyRolls-0.1.5.jar
       python build_skyyrolls_0.1.5.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world''')
rep('''                         Costs: Skyy_SkyyRolls/reforge.properties (re-read when the file changes).
Commands (ADMIN ONLY, see Permissions below):''',
    '''                         Costs: Skyy_SkyyRolls/reforge.properties (re-read when the file changes); admins also change
                         them in game: SkyWynn Menu -> Server Setup -> Rolls (SkyyMenu 0.3, /modconfig) since 0.1.5.
Commands (ADMIN ONLY - node skyyrolls.admin since 0.1.5, see Permissions below):''')
rep('''0.1.4: /reforge Reforge Anvil page (pick from your gear''',
    '''0.1.5: in-game server setup (research/Server-Setup-Spec.md 4.2, tools/CONFIG-CONTRACT.md): the reforge costs are one table,
  "Reforge cost by rarity", in SkyWynn Menu -> Server Setup -> Rolls, bound to the unchanged cost.<quality>=<coins> lines of
  Skyy_SkyyRolls/reforge.properties (the kit rewrites only the changed line, logs it in Skyy_SkyyRolls/config-changes.log, keeps a
  version in config-history/ and applies it within a second through Reforge.load; node skyyrolls.admin re-checked on every change);
  config:def:SkyyRolls + config:fn:SkyyRolls published at the end of setup(). Nothing is written until an admin changes an entry,
  so costs and files behave exactly like 0.1.4 until then. /rolls fix (spec 4.2): the root and read / reroll / give / clear call
  requirePermission("skyyrolls.admin") (stable across versions, grantable by SkyyRanks) and set no permission groups. The dead
  RollsGiveVariantCmd (never added since 0.1.2) is gone. No player Settings switches (SkyyRolls sends no unprompted messages).
  Details: tools/rolls_0_1_5_patch.py.
0.1.4: /reforge Reforge Anvil page (pick from your gear''')
rep('''Permissions: SkyyRolls is a test spike and /rolls give creates items, so it stays ADMIN-ONLY on purpose: there is NO
  setPermissionGroups(new String[] { "hytale:Adventurer" }) here (unlike the player commands in SkyyEssentials and the other
  Skyy mods). AbstractCommand.setOwner() gives the root, every subcommand and the variant an auto node (plugin base
  "<group>.<name>" lower-cased, spaces -> "_"; a subcommand appends ".<name>", a variant reuses its parent's node):
  skyy.0.1.4_skyyrolls.command.rolls, ...command.rolls.read, ...command.rolls.reroll, ...command.rolls.give, ...command.rolls.clear.
  hasPermission() on a subcommand without permission groups also requires the parent's node. Default players
  (hytale:Adventurer) have none of these; only "*" admins do. The version is part of the node, so it changes on every bump.
"""''',
    '''Permissions (0.1.5): /rolls creates and rewrites items, so it stays ADMIN-ONLY: the root and its subcommands read / reroll /
  give / clear each call requirePermission("skyyrolls.admin") (spec 4.2; until 0.1.4 only the versioned auto node
  skyy.0.1.4_skyyrolls.command.rolls... guarded it although the help said admin). AbstractCommand.setOwner() generates the auto node
  only while the permission is still null (bytecode 2026-09-25), so the explicit node sticks; hasPermission() on a subcommand
  without permission groups needs its own node AND the parent's - both skyyrolls.admin. No /rolls command calls setPermissionGroups,
  so the engine never adds the node to a permission group (tools/ci/lint.py perm_group_leaks): default players (hytale:Adventurer)
  cannot run /rolls, "*" admins can, and a SkyyRanks rank or /perm can grant skyyrolls.admin (the same node the config kit re-checks
  for every reforge cost change in Server Setup).
"""''')

# ---------------- imports + probes ----------------
rep('''import skyybuild as B
''', '''import skyybuild as B
import skyycfg as CFG      # 0.1.5: the admin config kit (tools/CONFIG-CONTRACT.md)
''')
rep('''(AC, "setPermissionGroups"), (IC, "setItemStackForSlot"),''', '''(AC, "setPermissionGroups"), (AC, "requirePermission"), (IC, "setItemStackForSlot"),''')

# ---------------- 3. dead RollsGiveVariantCmd ----------------
rep('''gvc = pool.makeClass(PKG + ".RollsGiveVariantCmd", pool.get(APC))
''', '')
rep('''# ================= /rolls give <itemId>  (usage variant of give: description-only constructor) =================
gvc.addField(CtField.make(f"public {RA} itemArg;", gvc))
gvc.addConstructor(CtNewConstructor.make(f"""
public RollsGiveVariantCmd() {{
  super("Give this item with random rolls");
  this.itemArg = withRequiredArg("itemId", "Item id, e.g. Weapon_Longsword_Copper", {ATY}.STRING);
}}""", gvc))
gvc.addMethod(CtNewMethod.make(f"""
{EXEC}
  Object v = ctx.get(this.itemArg);
  String id = v == null ? "" : String.valueOf(v).trim();
  if (id.length() == 0) id = {PKG}.Rolls.DEFAULT_ITEM;
  {PKG}.Rolls.run(store, ref, pr, "give", id);
}}""", gvc))

''', '')

# ---------------- 1. one source for the default costs + file text ----------------
rep('''F(rfg, "public static volatile java.nio.file.Path FILE;")''',
    r'''# 0.1.5: ONE source for the built-in cost ladder, the default reforge.properties text (Java defaultsText() below) and the config
# kit's DEFAULTS (tools/CONFIG-CONTRACT.md: the default entries of a key-family table, export scope "changed"). The text is 0.1.4's
# first-start file plus one comment line about the in-game page; keys and values are unchanged.
REF_QIDS = ["Junk", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
REF_QDEF = [100, 250, 500, 1000, 2500, 5000]
REF_OTHER = 1000
REFORGE_TEXT = ("# SkyyRolls - Reforge Anvil (/reforge) cost in coins, by the item's quality (rarity) id.\n"
                "# Coins are taken through SkyyCoins before the reroll and refunded if the reroll fails. 0 = free.\n"
                "# Quality ids = Server/Item/Qualities (Junk, Common, Uncommon, Rare, Epic, Legendary; mods can add more).\n"
                "# cost.default is used for every other quality (Tool, Technical, ...).\n"
                "# This file is re-read automatically when it changes (checked every time someone opens /reforge).\n"
                "# Admins can also change these in game: SkyWynn Menu -> Server Setup -> Rolls (/modconfig).\n"
                + "".join("cost.%s=%d\n" % (q, c) for q, c in zip(REF_QIDS, REF_QDEF)) + "cost.default=%d\n" % REF_OTHER)
assert len(REF_QIDS) == len(REF_QDEF) and all(0 <= c <= 10 ** 12 for c in REF_QDEF + [REF_OTHER])


def _jlit(txt):
    return '"' + txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


F(rfg, "public static volatile java.nio.file.Path FILE;")''')
rep('''F(rfg, 'public static final String[] QIDS = new String[] { "Junk", "Common", "Uncommon", "Rare", "Epic", "Legendary" };')
F(rfg, "public static final long[] QDEF = new long[] { 100L, 250L, 500L, 1000L, 2500L, 5000L };")
F(rfg, "public static final long DEF_OTHER = 1000L;")''',
    '''F(rfg, "public static final String[] QIDS = " + _jstr(REF_QIDS) + ";")
F(rfg, "public static final long[] QDEF = new long[] { " + ", ".join("%dL" % c for c in REF_QDEF) + " };")
F(rfg, "public static final long DEF_OTHER = %dL;" % REF_OTHER)''')
rep(r'''M(rfg, """
public static String defaultsText() {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyRolls - Reforge Anvil (/reforge) cost in coins, by the item's quality (rarity) id.\\n");
  sb.append("# Coins are taken through SkyyCoins before the reroll and refunded if the reroll fails. 0 = free.\\n");
  sb.append("# Quality ids = Server/Item/Qualities (Junk, Common, Uncommon, Rare, Epic, Legendary; mods can add more).\\n");
  sb.append("# cost.default is used for every other quality (Tool, Technical, ...).\\n");
  sb.append("# This file is re-read automatically when it changes (checked every time someone opens /reforge).\\n");
  for (int i = 0; i < QIDS.length; i++) sb.append("cost." + QIDS[i] + "=" + QDEF[i] + "\\n");
  sb.append("cost.default=" + DEF_OTHER + "\\n");
  return sb.toString();
}""")''',
    '''M(rfg, "public static String defaultsText() { return " + _jlit(REFORGE_TEXT) + "; }")   # 0.1.5: = REFORGE_TEXT (kit DEFAULTS)''')

# ---------------- 1. the config kit + the cost table's check hook (after the Reforge helpers, before the page) ----------------
rep('''# ================= 0.1.4 ReforgePage (inline, rebuilt only after a click) =================''',
    r'''# ================= 0.1.5 admin config kit (research/Server-Setup-Spec.md 4.2, tools/CONFIG-CONTRACT.md) =================
# SkyWynn Menu -> Server Setup -> Rolls (SkyyMenu 0.3, /modconfig) shows ONE table: "Reforge cost by rarity" = the key family
# cost.<quality id>=<coins> of Skyy_SkyyRolls/reforge.properties (file, keys and value format unchanged). Bound reload@: the kit edits
# only that entry's line, writes the file atomically on the scheduler, logs + versions the change, then runs Reforge.load (the loader
# setup() and the /reforge modified-time check already use) - live within about a second. Entries are typed (add mode "type"); a
# removed entry = that quality's BUILT-IN cost (Reforge.load seeds QIDS/QDEF/DEF_OTHER first); 0 = free; 0..1e12 = Reforge.load's
# clamp. Not danger (spec 4.2: L). Design notes: tools/rolls_0_1_5_patch.py.
CFG_FILE = "Skyy_SkyyRolls/reforge.properties"
CFG_CATS = [("reforge", "Reforge")]
CFG_ROWS = [
    # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("cost", "Reforge cost by rarity", "reforge", "table", "", "0", "1000000000000", "int;type;Coins", "coins", "live",
     "Coins per /reforge by rarity id. default = every rarity without its own entry. 0 = free.",
     "reload@" + CFG_FILE + ":cost.;check=Reforge.checkCost"),
]
kit = CFG.emit(pool, PKG, MOD="SkyyRolls", TITLE="Rolls", VERSION=VERSION, NODE="skyyrolls.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE], NOTE="Removing a rarity puts it back on its built-in cost. Hand edits also apply when /reforge opens.",
               RELOAD="Reforge.load", KEEP=20, DEFAULTS={CFG_FILE: REFORGE_TEXT})
# check=Reforge.checkCost (tools/CONFIG-CONTRACT.md: a table's check gets "cost[<entry>]" and the new value, null for a removal;
# null = fine, text = refuse, "?text" = ask first; it runs with no kit lock held, so it may read the table through the kit's own
# function). Reforge.load lower-cases every quality id, so "rare" next to "Rare" would be two lines for one rarity and the file order
# would pick the price: refused. Engine lookups fail open (qualityMatch answers the typed id itself when it cannot read the engine),
# but never silently: every fail-open path writes ONE WARNING line per server run and per kind through checkWarn (0 = the rarity ids
# could not be read / the list is empty, 1 = the table's own entries could not be read, 2 = the rarity list for the "Add anyway?"
# question could not be built). One line per run, not per call, because an import runs the check once per entry.
F(rfg, "public static final boolean[] CHECKWARN = new boolean[3];")
M(rfg, """
public static void checkWarn(int k, String what) {
  if (k < 0 || k >= CHECKWARN.length || CHECKWARN[k]) return;
  CHECKWARN[k] = true;
  @PKG@.Rolls.warn("reforge cost check (Server Setup -> Rolls): " + what + " (logged once per server run)");
}""")
M(rfg, """
public static String qualityMatch(String e) {
  try {
    java.util.Iterator it = @IQ@.getAssetMap().getAssetMap().keySet().iterator();
    int n = 0;
    while (it.hasNext()) {
      Object k = it.next();
      if (k == null) continue;
      n++;
      if (String.valueOf(k).equalsIgnoreCase(e)) return String.valueOf(k);
    }
    if (n == 0) {
      checkWarn(0, "the item rarity list is empty - rarity ids are accepted as typed, without the case / unknown-rarity check");
      return e;
    }
    return null;
  } catch (Throwable t) {
    checkWarn(0, "could not read the item rarity ids (" + t + ") - rarity ids are accepted as typed, without the case / unknown-rarity check");
    return e;
  }
}""")
M(rfg, """
public static String knownQualities() {
  StringBuilder sb = new StringBuilder();
  try {
    java.util.ArrayList ids = new java.util.ArrayList();
    java.util.Iterator it = @IQ@.getAssetMap().getAssetMap().keySet().iterator();
    while (it.hasNext()) { Object k = it.next(); if (k != null) ids.add(String.valueOf(k)); }
    java.util.Collections.sort(ids);
    for (int i = 0; i < ids.size(); i++) { if (sb.length() > 0) sb.append(", "); sb.append((String) ids.get(i)); }
  } catch (Throwable t) {
    checkWarn(2, "could not list the item rarity ids (" + t + ") - the Add-anyway question shows no rarity list");
  }
  return sb.toString();
}""")
M(rfg, """
public static String checkCost(String key, String value) {
  if (key == null || value == null) return null;
  int a = key.indexOf('[');
  int z = key.lastIndexOf(']');
  if (a < 0 || z <= a + 1) return null;
  String e = key.substring(a + 1, z);
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "keys", "cost", "" });
    if (o instanceof Object[] && ((Object[]) o).length > 0 && ((Object[]) o)[0] instanceof String[]) {
      String[] ks = (String[]) ((Object[]) o)[0];
      for (int i = 0; i < ks.length; i++) {
        if (ks[i] != null && !ks[i].equals(e) && ks[i].equalsIgnoreCase(e))
          return "The list already has " + ks[i] + " - change that entry instead (upper and lower case are the same rarity here).";
      }
    } else checkWarn(1, "config:fn keys cost answered " + String.valueOf(o) + " - the upper / lower case duplicate check is skipped");
  } catch (Throwable t) {
    checkWarn(1, "could not read the current cost entries (" + t + ") - the upper / lower case duplicate check is skipped");
  }
  if (e.equalsIgnoreCase("default")) {
    if (!e.equals("default")) return "Type default in lower case - it is the cost of every rarity without its own entry.";
    return null;
  }
  String m = qualityMatch(e);
  if (m == null) {
    String k = knownQualities();
    return "?No item rarity is called " + e + " on this server" + (k.length() > 0 ? " (rarities: " + k + ")" : "") + ". Add it anyway?";
  }
  if (!m.equals(e)) return "The rarity id is " + m + " - type it exactly like that.";
  return null;
}""")

# ================= 0.1.4 ReforgePage (inline, rebuilt only after a click) =================''')

# ---------------- 2. /rolls permission fix ----------------
rep('''rdc.addConstructor(CtNewConstructor.make('public RollsReadCmd() { super("read", "Show the rolls on the item in your hand"); }', rdc))''',
    '''rdc.addConstructor(CtNewConstructor.make('public RollsReadCmd() { super("read", "Show the rolls on the item in your hand"); requirePermission("skyyrolls.admin"); }', rdc))''')
rep('''rrc.addConstructor(CtNewConstructor.make('public RollsRerollCmd() { super("reroll", "Re-roll the item in your hand (same slot)"); }', rrc))''',
    '''rrc.addConstructor(CtNewConstructor.make('public RollsRerollCmd() { super("reroll", "Re-roll the item in your hand (same slot)"); requirePermission("skyyrolls.admin"); }', rrc))''')
rep('''clc.addConstructor(CtNewConstructor.make('public RollsClearCmd() { super("clear", "Remove the rolls from the item in your hand (keeps the item, durability and other data)"); }', clc))''',
    '''clc.addConstructor(CtNewConstructor.make('public RollsClearCmd() { super("clear", "Remove the rolls from the item in your hand (keeps the item, durability and other data)"); requirePermission("skyyrolls.admin"); }', clc))''')
rep('''  super("give", "Give an item with random rolls: /rolls give [item name or id] (default Weapon_Longsword_Copper)");
  setAllowsExtraArguments(true);''',
    '''  super("give", "Give an item with random rolls: /rolls give [item name or id] (default Weapon_Longsword_Copper)");
  requirePermission("skyyrolls.admin");
  setAllowsExtraArguments(true);''')
rep('''  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear");
''', '''  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear");
  requirePermission("skyyrolls.admin");   // 0.1.5 (spec 4.2): a stable admin node; no permission groups anywhere under /rolls
''')

# ---------------- plugin: publish the kit LAST in setup(), flush it in shutdown() ----------------
rep('''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /reforge (players) opens the Reforge Anvil; /rolls [read] | reroll | give [itemId] | clear (admin only); tooltip = base value (+roll)");
}}""", pl))''',
    '''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /reforge (players) opens the Reforge Anvil; /rolls [read] | reroll | give [itemId] | clear (node skyyrolls.admin); tooltip = base value (+roll); reforge costs also in SkyWynn Menu -> Server Setup -> Rolls");
  // 0.1.5: admin config kit LAST, after the costs were loaded: publishes config:def:SkyyRolls + config:fn:SkyyRolls (CONFIG-CONTRACT)
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}   // 0.1.5: a pending cost change + its log line are written now
  super.shutdown();
}}""", pl))''')
rep('''for c in (rl, rfg, rpg, rfc, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):
    c.writeFile(OUT)
print("classes written")''',
    '''for c in (rl, rfg, rpg, rfc, rdc, rrc, clc, gvr, cmd, rft, rdy, pl):
    c.writeFile(OUT)
kit.write(OUT)      # 0.1.5: deferred kit checks (Reforge.load, Reforge.checkCost signatures), then the 7 Cfg* classes
print("classes written (+%d config kit)" % len(kit.classes))''')
rep('''/reforge Reforge Anvil page (coins via SkyyCoins, optional); /rolls admin tools. Zero dependencies."''',
    '''/reforge Reforge Anvil page (coins via SkyyCoins, optional), costs editable in game (SkyWynn Menu Server Setup); /rolls admin tools. Zero dependencies."''')

# ---------------- self-checks ----------------
assert "gvc" not in s and "RollsGiveVariantCmd()" not in s and '".RollsGiveVariantCmd"' not in s, "dead variant still referenced"
assert s.count('requirePermission("skyyrolls.admin")') == 5 + 2, s.count('requirePermission("skyyrolls.admin")')   # 5 ctors + 2 docstring mentions
assert "setPermissionGroups(new String[] { \"hytale:Adventurer\" });   // COMMAND RULES" in s   # /reforge untouched
assert s.count("CfgPub.start(") == 1 and s.count("kit.write(OUT)") == 1

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
