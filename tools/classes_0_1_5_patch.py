"""Derive SkyyClasses/build_skyyclasses_0.1.5.py from 0.1.4 (run: python tools/classes_0_1_5_patch.py, then build the 0.1.5 script).
0.1.5 (in-game server setup, research/Server-Setup-Spec.md 4.15 + 7; player Settings, research/Settings-Spec.md 3.5):
 - ADMIN CONFIG KIT (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md): config:def:SkyyClasses + config:fn:SkyyClasses +
   config:epoch:SkyyClasses, published at the END of setup() after ClassCfg.load(). File Skyy_SkyyClasses/config.properties (same name,
   same keys), node skyyclasses.admin, RELOAD = ClassCfg.load (hand edits found by the kit re-run the mod's own loader and its clamps).
   Shows in SkyyMenu 0.3 Server Setup as "Classes". Rows (row key = file key):
     lock:   requireClass      bool  false  live,danger   field ClassCfg.REQUIRE_CLASS
             unassignedBlocked bool  true   live          field ClassCfg.UNASSIGNED_BLOCKED
     picker: promptEveryLogin  bool  true   live          field ClassCfg.PROMPT_EVERY_LOGIN
             openDelayMillis   int   2000   live,adv      field ClassCfg.OPEN_DELAY_MS (ms, 250-60000 = the loader's clamp, no scale)
             classSwitching    bool  false  ro            custom ClassHooks (no file key: shows ALLOW_SWITCH, can never be set)
   switchCost + cooldownMinutes are NOT rows (spec 4.15: inert while ALLOW_SWITCH=false is code - a trap); the read-only
   "Class switching" row says so. They stay in the file and in the loader exactly as before.
 - /classadmin reload goes through the kit's reload op (hand edits of the rows are logged via=file in config-changes.log and
   applied by ClassCfg.load after the kit's pending writes), then CfgPub.flush() so the reply shows current values, then
   ClassCfg.loadInert() re-reads only the two inert keys (never a bound field, so it cannot undo an in-game change that is
   still waiting for its 500 ms save). Bare /classadmin now prints the values (ClassCfg.summary) instead of re-reading the file
   as a side effect (the same race). /classadmin set|reset|info are player data, not config: unchanged.
 - PLAYER SETTINGS (SkyyMenu 0.2+): ClassCfg.notifyOn / regSetting (Settings-Spec 1.3, mod "SkyyClasses"); setup() registers
   classes.blockedChat + classes.blockedPopup (category combat, labels/help from Settings-Spec 2.2). Gates: first line of
   ClassRules.tell (before the WARNED throttle) and first line inside ClassRules.popup's try (before POPPED), so a hidden line
   never uses up the cooldown of a shown one. DamageLock still blocks the hit whatever the switches say. No SkyyMenu = ON = 0.1.4.
 - Default file text (only written when the file is missing): header mentions Server Setup, one comment line says switchCost /
   cooldownMinutes are unused while switching is off. Keys and values unchanged.
 - --deploy refuses (deploys go through tools/deploy_set.py only).
Defaults are identical to 0.1.4 until an admin changes something.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.4.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
TQ = chr(34) * 3


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


# ---------------------------------------------------------------- version + docstring
rep('VERSION = "0.1.4"', 'VERSION = "0.1.5"')
rep("0.1.4: a POPUP (vanilla notification toast with the weapon's icon)",
    "0.1.5: in-game server setup - the admin config kit (tools/skyycfg.py; SkyyMenu Server Setup -> Classes: requireClass," + LF +
    "  unassignedBlocked, promptEveryLogin, openDelayMillis, read-only Class switching) and the player Settings switches" + LF +
    "  classes.blockedChat / classes.blockedPopup - notes in tools/classes_0_1_5_patch.py." + LF +
    "0.1.4: a POPUP (vanilla notification toast with the weapon's icon)")
rep("Run:   python build_skyyclasses_0.1.3.py            -> SkyyClasses/SkyyClasses-0.1.3.jar" + LF +
    "       python build_skyyclasses_0.1.3.py --deploy   -> also copies to Mods/SkyyClasses.jar and enables it in the HUD mod world",
    "Run:   python build_skyyclasses_0.1.5.py            -> SkyyClasses/SkyyClasses-0.1.5.jar" + LF +
    "       (no --deploy: deploys go through tools/deploy_set.py)")
rep("      Skyy_SkyyClasses/config.properties (switchCost, cooldownMinutes, requireClass, unassignedBlocked, promptEveryLogin, openDelayMillis).",
    "      Skyy_SkyyClasses/config.properties (switchCost, cooldownMinutes, requireClass, unassignedBlocked, promptEveryLogin, openDelayMillis;" + LF +
    "      0.1.5: also edited in game through the config kit - Skyy_SkyyClasses/config-changes.log + config-history/).")
rep("import skyybuild as B" + LF, "import skyybuild as B" + LF + "import skyycfg as CFG" + LF)

# ---------------------------------------------------------------- default file text (written only when the file is missing)
rep('    "# SkyyClasses config - edit, then /classadmin reload (or restart the server)",',
    '    "# SkyyClasses config - edit, then /classadmin reload (or restart the server). Also in game: SkyWynn Menu -> Server Setup -> Classes",')
rep('    "# switchCost = coins to switch class (the first choice is always free). Uses SkyyCoins; 0 = free switching.",',
    '    "# switchCost and cooldownMinutes are unused while class switching is off (design lock: a new class means a new profile)",' + LF +
    '    "# switchCost = coins to switch class (the first choice is always free). Uses SkyyCoins; 0 = free switching.",')
# the old comment still named staves (Mage weapons since 0.1.1); axes / maces / clubs are unassigned since Berserker left in 0.1.2
rep('    "# unassignedBlocked = true: weapons no class owns yet (staves, wands, spellbooks, bombs, guns...) deal no damage for players with a class",',
    '    "# unassignedBlocked = true: weapons no class owns yet (axes, maces, wands, spellbooks, bombs, guns...) deal no damage for players with a class",')

# ---------------------------------------------------------------- player Settings helper (Settings-Spec 1.3), right after the creating bridge()
SETTINGS = LF.join([
    "# 0.1.5: player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3). No SkyyMenu = no answer = on (0.1.4 behaviour).",
    "M(cfg, r" + TQ,
    "public static boolean notifyOn(java.util.UUID u, String key) {",
    "  if (u == null || key == null) return true;",
    "  try {",
    "    Object f = bridge().get(\"settings:fn:get\");",
    "    if (f instanceof java.util.function.Function) {",
    "      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });",
    "      if (r instanceof Boolean) return ((Boolean) r).booleanValue();",
    "    }",
    "  } catch (Throwable t) { }",
    "  return true;",
    "}" + TQ + ")",
    "M(cfg, r" + TQ,
    "public static void regSetting(String key, String label, String cat, boolean def, String help) {",
    "  try {",
    "    Object[] a = new Object[] { \"SkyyClasses\", key, label, cat, Boolean.valueOf(def), help };",
    "    java.util.Map br = bridge();",
    "    br.put(\"settings:def:\" + key, a);",
    "    Object f = br.get(\"settings:fn:register\");",
    "    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);",
    "  } catch (Throwable t) { }",
    "}" + TQ + ")",
    "# 0.1.3: the profile contract helper, verbatim (tools/PROFILES-CONTRACT.md)",
])
rep("# 0.1.3: the profile contract helper, verbatim (tools/PROFILES-CONTRACT.md)", SETTINGS)

# ---------------------------------------------------------------- summary / loadInert / ClassHooks / the kit (after ClassCfg.load)
KIT = LF.join([
    "# 0.1.5: the running values as one line (the same text load() returns) - bare /classadmin prints it instead of re-reading the file",
    "M(cfg, r" + TQ,
    "public static String summary() {",
    "  return \"switchCost=\" + SWITCH_COST + \" cooldownMinutes=\" + COOLDOWN_MIN + \" requireClass=\" + REQUIRE_CLASS",
    "    + \" unassignedBlocked=\" + UNASSIGNED_BLOCKED + \" promptEveryLogin=\" + PROMPT_EVERY_LOGIN + \" openDelayMillis=\" + OPEN_DELAY_MS;",
    "}" + TQ + ")",
    "# 0.1.5: /classadmin reload re-reads ONLY the two keys that are not kit rows (switchCost, cooldownMinutes: inert while ALLOW_SWITCH=false,",
    "# spec 4.15). The kit rows are re-read by the kit's reload op (logged, then ClassCfg.load after the kit's own writes); this never",
    "# touches a bound field, so it cannot undo an in-game change still waiting for its 500 ms save. Same clamps as load().",
    "M(cfg, r" + TQ,
    "public static synchronized void loadInert() {",
    "  try {",
    "    if (FILE == null || !java.nio.file.Files.isRegularFile(FILE, new java.nio.file.LinkOption[0])) return;",
    "    java.util.Properties p = new java.util.Properties();",
    "    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);",
    "    try { p.load(in); } finally { in.close(); }",
    "    long cost = lng(p, \"switchCost\", SWITCH_COST);",
    "    long cd = lng(p, \"cooldownMinutes\", COOLDOWN_MIN);",
    "    if (cost < 0L) cost = 0L;",
    "    if (cd < 0L) cd = 0L;",
    "    SWITCH_COST = cost;",
    "    COOLDOWN_MIN = cd;",
    "  } catch (Throwable t) { warn(\"could not re-read switchCost / cooldownMinutes: \" + t); }",
    "}" + TQ + ")",
    "",
    "# ================= 0.1.5: the admin config kit (research/Server-Setup-Spec.md 4.15; tools/CONFIG-CONTRACT.md) =================",
    "# ClassHooks = the read-only 'Class switching' row (custom:, no file key: it shows ALLOW_SWITCH and can never be set, so a hand-typed",
    "# allowSwitch line in the file can never turn paid switching back on). switchCost / cooldownMinutes are deliberately not rows.",
    "hooks = pool.makeClass(PKG + \".ClassHooks\")",
    "M(hooks, r" + TQ,
    "public static String customGet(String key) {",
    "  if (\"classSwitching\".equals(key)) return @PKG@.ClassCfg.ALLOW_SWITCH ? \"true\" : \"false\";",
    "  return null;",
    "}" + TQ + ")",
    "M(hooks, r" + TQ,
    "public static Object[] customSet(String key, String value) {",
    "  return new Object[] { \"bad\", null, \"Class switching is off in this version (design lock) - a new class means a new profile.\" };",
    "}" + TQ + ")",
    "CFG_CATS = [(\"lock\", \"Weapon lock\"), (\"picker\", \"Class picker\")]",
    "CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key",
    "    (\"requireClass\", \"Require a class for weapons\", \"lock\", \"bool\", str(DEF_REQUIRE_CLASS).lower(), \"\", \"\", \"\", \"\", \"live,danger\",",
    "     \"ON: players without a class deal no weapon damage. OFF: any weapon works for them (no class XP).\",",
    "     \"field:ClassCfg.REQUIRE_CLASS@config.properties:requireClass\"),",
    "    (\"unassignedBlocked\", \"Block weapons no class owns\", \"lock\", \"bool\", str(DEF_UNASSIGNED_BLOCKED).lower(), \"\", \"\", \"\", \"\", \"live\",",
    "     \"ON: weapons no class owns (axes, maces, bombs, guns, wands...) do no damage for anyone with a class.\",",
    "     \"field:ClassCfg.UNASSIGNED_BLOCKED@config.properties:unassignedBlocked\"),",
    "    (\"promptEveryLogin\", \"Class page on every login\", \"picker\", \"bool\", str(DEF_PROMPT_EVERY_LOGIN).lower(), \"\", \"\", \"\", \"\", \"live\",",
    "     \"Without SkyyProfiles: ON opens /class at each login until a class is chosen, OFF only at first join.\",",
    "     \"field:ClassCfg.PROMPT_EVERY_LOGIN@config.properties:promptEveryLogin\"),",
    "    (\"openDelayMillis\", \"Class page open delay\", \"picker\", \"int\", str(DEF_OPEN_DELAY_MS), \"250\", \"60000\", \"step=250\", \"ms\", \"live,adv\",",
    "     \"How long after joining the class page opens (only without SkyyProfiles).\",",
    "     \"field:ClassCfg.OPEN_DELAY_MS@config.properties:openDelayMillis\"),",
    "    (\"classSwitching\", \"Class switching\", \"picker\", \"bool\", \"false\", \"\", \"\", \"\", \"\", \"ro\",",
    "     \"Off (design lock): a new class means a new profile. switchCost and cooldownMinutes do nothing.\",",
    "     \"custom:ClassHooks\"),",
    "]",
    "kit = CFG.emit(pool, PKG, MOD=\"SkyyClasses\", TITLE=\"Classes\", VERSION=VERSION, NODE=\"skyyclasses.admin\", CATS=CFG_CATS, ROWS=CFG_ROWS,",
    "               FILES=[\"Skyy_SkyyClasses/config.properties\"], NOTE=\"Player classes: /classadmin set, reset, info <player>. Weapon rules are code (rebuild).\",",
    "               RELOAD=\"ClassCfg.load\", KEEP=20, DEFAULTS={\"config.properties\": \"\".join(l + \"\\n\" for l in CFG_LINES)})",
    "print(\"config kit: %d rows, files %s\" % (kit.info[\"rows\"], \", \".join(kit.info[\"files\"])))",
    "",
    "# ================= ClassDefs: generated from the Python tables =================",
])
rep("# ================= ClassDefs: generated from the Python tables =================", KIT)

# ---------------------------------------------------------------- player Settings gates (Settings-Spec 3.5): before each message's own throttle
rep("public static void tell(@PR@ pr, java.util.UUID u, String text) {" + LF +
    "  long now = System.currentTimeMillis();",
    "public static void tell(@PR@ pr, java.util.UUID u, String text) {" + LF +
    "  if (!@PKG@.ClassCfg.notifyOn(u, \"classes.blockedChat\")) return;" + LF +
    "  long now = System.currentTimeMillis();")
rep("public static void popup(@PR@ pr, java.util.UUID u, String id, String text) {" + LF +
    "  try {" + LF +
    "    long now = System.currentTimeMillis();",
    "public static void popup(@PR@ pr, java.util.UUID u, String id, String text) {" + LF +
    "  try {" + LF +
    "    if (!@PKG@.ClassCfg.notifyOn(u, \"classes.blockedPopup\")) return;" + LF +
    "    long now = System.currentTimeMillis();")

# ---------------------------------------------------------------- /classadmin reload through the kit; bare /classadmin prints values
rep('C(arel, \'public AdminReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyyClasses/config.properties"); }\')' + LF +
    "M(arel, r" + TQ + LF +
    "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {" + LF +
    "  if (!pr.hasPermission(\"skyyclasses.admin\")) { pr.sendMessage(@MSG@.raw(\"[Classes] no permission (skyyclasses.admin)\")); return; }" + LF +
    "  pr.sendMessage(@MSG@.raw(\"[Classes] config reloaded: \" + @PKG@.ClassCfg.load()));" + LF +
    "}" + TQ + ")",
    'C(arel, \'public AdminReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyyClasses/config.properties"); }\')' + LF +
    "# 0.1.5: the kit's reload op (hand edits logged via=file, ClassCfg.load runs after the kit's pending writes), then flush so the reply" + LF +
    "# shows current values, then the two inert keys (never a bound field)" + LF +
    "M(arel, r" + TQ + LF +
    "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {" + LF +
    "  if (!pr.hasPermission(\"skyyclasses.admin\")) { pr.sendMessage(@MSG@.raw(\"[Classes] no permission (skyyclasses.admin)\")); return; }" + LF +
    "  String k = \"not re-read by the config kit\";" + LF +
    "  try {" + LF +
    "    Object o = new @PKG@.CfgFn().apply(new Object[] { \"reload\", pr.getUuid(), pr.getUsername(), \"command\" });" + LF +
    "    if (o instanceof Object[] && ((Object[]) o).length > 2) k = String.valueOf(((Object[]) o)[2]);" + LF +
    "  } catch (Throwable t) { k = \"the config kit could not re-read it: \" + t; }" + LF +
    "  try { @PKG@.CfgPub.flush(); } catch (Throwable t) { @PKG@.ClassCfg.warn(\"config flush failed: \" + t); }" + LF +
    "  @PKG@.ClassCfg.loadInert();" + LF +
    "  pr.sendMessage(@MSG@.raw(\"[Classes] config reloaded: \" + @PKG@.ClassCfg.summary() + \" (\" + k + \")\"));" + LF +
    "}" + TQ + ")")
rep('  pr.sendMessage(@MSG@.raw("[Classes] classes: " + @PKG@.ClassDefs.listText() + " | config: " + @PKG@.ClassCfg.load()));',
    '  pr.sendMessage(@MSG@.raw("[Classes] classes: " + @PKG@.ClassDefs.listText() + " | config: " + @PKG@.ClassCfg.summary()));')

# ---------------------------------------------------------------- setup(): Settings switches, then the kit at the END (after ClassCfg.load)
rep('  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ClassTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);' + LF,
    '  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ClassTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);' + LF +
    '  @PKG@.ClassCfg.regSetting("classes.blockedChat", "Blocked weapon - chat line", "combat", true, "Only Archers can use bows... - at most every 3 s. The hit is blocked either way");' + LF +
    '  @PKG@.ClassCfg.regSetting("classes.blockedPopup", "Blocked weapon - popup", "combat", true, "The popup with the weapon\'s icon - at most every 1.5 s");' + LF +
    '  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());' + LF)
rep('(@PKG@.ClassCfg.profilesOn() ? "SkyyProfiles found - class per profile" : "SkyyProfiles not loaded yet - class per player") + ")");',
    '(@PKG@.ClassCfg.profilesOn() ? "SkyyProfiles found - class per profile" : "SkyyProfiles not loaded yet - class per player") + "; config also in game: SkyWynn Menu -> Server Setup -> Classes)");')
rep("  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }" + LF + "  super.shutdown();",
    "  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }" + LF +
    "  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }" + LF + "  super.shutdown();")

# ---------------------------------------------------------------- write the hook class + the kit classes; no --deploy
rep("for c in (cfg, defs, st_, rul, afn, gfn, srec, strk, lock, page, opn, rtk, rdy, quit_, ctick, cmd, aset, ares, ainf, arel, adm, pl):" + LF +
    "    c.writeFile(OUT)" + LF +
    'print("classes written")',
    "for c in (cfg, hooks, defs, st_, rul, afn, gfn, srec, strk, lock, page, opn, rtk, rdy, quit_, ctick, cmd, aset, ares, ainf, arel, adm, pl):" + LF +
    "    c.writeFile(OUT)" + LF +
    "kit.write(OUT)" + LF +
    'print("classes written (+%d config kit classes)" % len(kit.classes))')
rep('if "--deploy" in sys.argv:' + LF +
    '    B.deploy(jar, "SkyyClasses.jar")' + LF +
    '    B.enable_in_world("HUD mod", "Skyy:%s SkyyClasses" % VERSION, disable_prefix="Skyy:")',
    'if "--deploy" in sys.argv:' + LF +
    '    raise SystemExit("SkyyClasses: --deploy is not supported here - deploys go through tools/deploy_set.py")')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
