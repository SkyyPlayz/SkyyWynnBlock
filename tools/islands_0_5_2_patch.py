"""Derive SkyyIslands/build_skyyislands_0.5.2.py from 0.5.1 (edit THIS file, then regenerate: python tools/islands_0_5_2_patch.py).
Base = 0.5.1 (the 2026-09-25 SECURITY hotfix), NEVER 0.5. 0.5.2 = IN-GAME SERVER SETUP + PLAYER SETTINGS (Skyy's rule: everything a
server owner might change must be doable in game; config.properties stays and always matches). Sources: research/Server-Setup-Spec.md
4.17 (+ sections 1, 3, 7, 5.5 starter kit row) and tools/CONFIG-CONTRACT.md; research/Settings-Spec.md 3.10 (its "next: 0.5.1" is
stale - this is the version after the LIVE 0.5.1).
 - Admin config kit (tools/skyycfg.py, contract v1): config:def:SkyyIslands + config:fn:SkyyIslands published at the END of setup()
   (after IslandCfg.load). Page "Islands", node skyyislands.admin, file Skyy_SkyyIslands/config.properties, every file key unchanged.
   Categories permissions, visits, coop, limits, starter, hub, tech. RELOAD = IslandHooks.reloadCfg (IslandCfg.load + re-parse of the
   cached island settings), used for hand edits and the reload op.
 - Field audit (spec 4.17): every IslandCfg scalar is now public static volatile. DEF_PERM is public static volatile int[] (no longer
   final); load() fills a NEW array and assigns it once, and the 14 defaults.perm.<flag> rows are custom: (IslandHooks.customGet /
   customSet / customRead, copy-on-write under a synchronized method). defaults.visit.mode and tint.resend (int fields behind choices)
   are custom: the same way. defaults.visit.notify is stored 1/0 (row opts 01).
 - Defaults of islands whose owner never changed a value (defaults.perm.*, defaults.visit.mode / limit / notify) are resolved when an
   island file is parsed; IslandSettings now keeps a copy of its properties (raw) and IslandStore.reparseAll() re-parses every cached
   island in memory (no file I/O) after such a change, so they apply at once: flag live (the spec's N would have been untrue - islands
   store no mode/limit/notify until their owner changes it, so a default change reaches them at the next file write anyway).
 - defaults.visit.limit: the loader clamps it to 1-100 (the row range) instead of 1..visit.limitMax. IslandSettings.parse already caps
   every island's limit at visit.limitMax, so the effective limit is identical, and the file and the running value always agree.
 - Starter kit (spec 5.5, the template editor is a later step): starter.kit items row (qty, max 18 entries = the starter chest's 18
   slots) replaces the hard-coded ids/qty in FillTask.starterKit (default = the 0.5.1 kit, same order, same amounts); action "Starter
   kit from my hotbar" (KitHotbarTask on the admin's world thread, then CfgFn.set -> logged, versioned, undoable). New islands and
   resets only. New installs get a starter.kit line in config.properties.
 - Hub: action "Hub point" = /sethub (HubHereTask on the admin's world thread). /sethub itself keeps its texts and now logs to
   config-changes.log (key hub.set, status done) through the kit's log (SetHubCmd.setHere shared by both).
 - /island reload routes config.properties through the kit's reload op (hand edits logged via=file, RELOAD after the pending writes)
   instead of calling IslandCfg.load directly (a value set in the menu a moment ago may still be waiting for the kit's 500 ms save).
 - Player Settings (SkyyMenu 0.2+): islands.protection, islands.hubOnLogin, islands.buildRights, islands.visitPing,
   islands.visitWelcome (category profiles, default ON, registered in setup() via IslandStore.regSetting; notifyOn helper). Only the
   sends are gated: guard cancels, the hub teleport, trust, the visit ping throttle all run as before.
 - Flags that differ from Server-Setup-Spec 4.17 (the spec text is not updated here - its owner decides): defaults.perm.* live,danger
   (spec L; one click changes every island), defaults.visit.mode / limit / notify live (spec N; the re-parse makes live true),
   starter.fromHotbar new,danger (spec N; one click replaces the whole kit), hub.set live,danger (spec: no flag; one click moves /hub and
   every island login for everyone, and hub.set has no Undo). Only the confirmation step is added; no value or default changes.
Review fixes (same version, 2026-09-25):
 - starter.kit: check=IslandHooks.checkKit refuses a kit that needs more than the chest's 18 slots, counted in real slots (the chest
   splits an amount above the item's stack size over several slots, so 18 entries alone did not make a kit fit: the engine's
   canAddItemStacks tests each stack alone, so a too-big kit was placed only in part - the rest lost, logged - and one entry that alone
   needs more than 18 slots, e.g. Soil_Dirt:9999, made every island's kit "no room" forever, retried at each arrival). The late-kit line
   "make room for N stacks" now counts slots (the 0.5.1 kit = 6, unchanged). FillTask builds each ItemStack in its own try (one refused
   stack drops only that entry) and names a kit bigger than the chest in the server log (a hand edit - the menu refuses it).
 - The items check of this mod's kit (emit ITEM_FN=IslandHooks.itemOk) = the live item map + the default kit's own cross-mod id
   Skyy_Accessory_Bag, so reset to default, Undo / restore of a kit that holds it, and typed edits that keep it work without
   SkyyAccessories (the kit refused the row's own default before). Every other id is still checked against the live item map.
 - IslandCfg.load: a failed read keeps the running animals.extra roles in ANIMALS (0.5.1 rebuilt ANIMALS from the built-in roles only,
   so the running set and the page's animals.extra could disagree); the log line says the running values stay.
Defaults = the 0.5.1 values, so nothing changes until an admin or a player changes something.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.1.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


def seg(start, end, must_have, new):
    """Replace s[start : end) (end exclusive, both anchors unique) after checking the old segment is the one we expect."""
    global s
    assert s.count(start) == 1, "segment start not unique: " + start[:90]
    assert s.count(end) == 1, "segment end not unique: " + end[:90]
    i = s.index(start)
    j = s.index(end, i)
    old = s[i:j]
    for m in must_have:
        assert m in old, "segment %r lacks %r" % (start[:50], m[:80])
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------- version, docstring, kit import
rep('VERSION = "0.5.1"', 'VERSION = "0.5.2"')
rep('import skyybuild as B\n', 'import skyybuild as B\nimport skyycfg as CFG   # 0.5.2: the admin config kit (tools/CONFIG-CONTRACT.md)\n')
first = s.index('"""') + 3
s = s[:first] + (
    "0.5.2 (2026-09-25): IN-GAME SERVER SETUP + PLAYER SETTINGS, derived from 0.5.1 by tools/islands_0_5_2_patch.py (edit the patch,\n"
    "  not this file; notes there). Admin config kit (config:def/fn:SkyyIslands, page Islands, node skyyislands.admin): 14 permission\n"
    "  defaults, visit defaults, co-op, limits, starter kit (+ from my hotbar), hub point, tech rows; IslandCfg scalars volatile, DEF_PERM\n"
    "  copy-on-write; /island reload and /sethub go through the kit. Player Settings: islands.protection / hubOnLogin / buildRights /\n"
    "  visitPing / visitWelcome gate only their chat lines. Defaults identical to 0.5.1. Review fixes: starter.kit must fit the 18-slot\n"
    "  chest in real slots (checkKit), one refused kit stack drops only itself, the default kit stays valid without SkyyAccessories.\n") + s[first:]

# ---------------------------------------------------------------- engine API probes for the new code
rep('''    B.probe(pool, c, m)

# ---- build-time data: farm animal NPC roles''', '''    B.probe(pool, c, m)
# 0.5.2: the starter kit from the admin's hotbar (SkyyAccessories' verified Player -> Inventory -> getHotbar path)
for c, m in ((T["PLA"], "getInventory"), ("com.hypixel.hytale.server.core.inventory.Inventory", "getHotbar"), (T["IC"], "getCapacity"),
             (T["IC"], "getItemStack"), (T["IS"], "getItemId"),
             # 0.5.2 review: the kit's chest slots (IslandCfg.slotsFor) and this mod's item check (IslandHooks.itemOk)
             ("com.hypixel.hytale.server.core.asset.type.item.config.Item", "getAssetMap"),
             ("com.hypixel.hytale.server.core.asset.type.item.config.Item", "getMaxStack"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset")):
    B.probe(pool, c, m)

# ---- build-time data: farm animal NPC roles''')

# ---------------------------------------------------------------- config.properties default text (new installs)
KIT_DEFAULT = "Bench_WorkBench:1,Wood_Oak_Trunk:10,Soil_Dirt:8,Ingredient_Stick:8,Food_Bread:5,Skyy_Accessory_Bag:1"
rep('''    "# SkyyIslands %s - server settings (admins). Written with the defaults on first run; edit, then /island reload (or restart)." % VERSION,''',
    '''    "# SkyyIslands %s - server settings (admins). Written with the defaults on first run. Change them in game (SkyWynn Menu ->" % VERSION,
    "# Server Setup -> Islands, which keeps this file in step), or edit here, then /island reload (or restart).",''')
rep(r'''CFG_TEXT = "\n".join([''', r'''# 0.5.2: the starter kit that 0.5.1 hard-coded in FillTask.starterKit (same items, order and amounts) = config starter.kit's default
KIT_DEFAULT = "''' + KIT_DEFAULT + r'''"
CFG_TEXT = "\n".join([''')
rep('''    "perm.otherProfileStrict=true",
    "",
])''', '''    "perm.otherProfileStrict=true",
    "# starter kit put in the chest of every NEW island (and after /island reset): item:amount, comma separated, at most 18 stacks",
    "starter.kit=%s" % KIT_DEFAULT,
    "",
])''')

# ---------------------------------------------------------------- new classes
rep('''seen = K("SeenTick")
pl   = K("SkyyIslandsPlugin", T["JP"])''', '''seen = K("SeenTick")
hooks = K("IslandHooks")     # 0.5.2: config kit hooks (custom:/check=/after=/action:/RELOAD)
hht  = K("HubHereTask")      # 0.5.2: "Hub point" action -> /sethub logic on the admin's world thread
kht  = K("KitHotbarTask")    # 0.5.2: "Starter kit from my hotbar" action (world thread)
pl   = K("SkyyIslandsPlugin", T["JP"])''')
rep('''       cfn, guard, g1, g2, g3, g4, g5, g6, g7, ghurt, page, rout, disp, rdy, seen]''',
    '''       cfn, guard, g1, g2, g3, g4, g5, g6, g7, ghurt, page, rout, disp, rdy, seen, hooks, hht, kht]''')

# ---------------------------------------------------------------- IslandStore part 1: Settings-Spec 1.3 helper (creating bridge())
rep('''# tools/PROFILES-CONTRACT.md helper, verbatim: storage key of the player's ACTIVE profile''', r'''# 0.5.2 player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3). No SkyyMenu = no answer = today's behaviour (on).
M(st_, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(st_, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyIslands", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
# tools/PROFILES-CONTRACT.md helper, verbatim: storage key of the player's ACTIVE profile''')

# ---------------------------------------------------------------- IslandCfg: volatile fields, DEF_PERM copy-on-write, new keys
rep('''F(cfg, "public static final int[] DEF_PERM = new int[] { %s };" % ", ".join(str(RANKS.index(f[3])) for f in FLAGS))''',
    '''# 0.5.2 (spec 4.17): volatile, not final - load() and the config kit assign a NEW array (copy on write), never edit elements
F(cfg, "public static volatile int[] DEF_PERM = new int[] { %s };" % ", ".join(str(RANKS.index(f[3])) for f in FLAGS))''')
seg('''for f in ("public static int DEF_MODE = 0;",''', '''M(cfg, r"""
public static int rankOf(String v, int def) {''', ['"public static int INVITE_SECONDS = 60;"', '"public static boolean STRICT_OTHER = true;"',
                                                   'public static volatile java.util.HashSet ANIMALS'],
    '''# 0.5.2 (spec 4.17 field audit): every scalar the config kit binds is public static volatile (Field.setInt/setBoolean writes, visible
# to every thread); STARTER_KIT (starter.kit) and ANIMALS_EXTRA (animals.extra) are new
for f in ("public static volatile int DEF_MODE = 0;", "public static volatile int DEF_LIMIT = 5;", "public static volatile boolean DEF_NOTIFY = true;",
          "public static volatile int LIMIT_MAX = 10;", "public static volatile int COOP_MAX = 5;", "public static volatile boolean ADMINS_INVITE = false;",
          "public static volatile int INVITE_SECONDS = 60;", "public static volatile int TRUSTED_MAX = 20;", "public static volatile int BANS_MAX = 100;",
          "public static volatile int EXPEL_SECONDS = 60;", "public static volatile long RESET_HOURS = 24L;", "public static volatile int RESET_CONFIRM = 20;",
          "public static volatile int TINT_RESEND = 1;",
          # 0.5 review: perm.otherProfileStrict (default true) = someone with a role here on ANOTHER profile only gets doors, seats, mobs
          "public static volatile boolean STRICT_OTHER = true;",
          "public static volatile String BASE_ANIMALS = \\"\\";",
          "public static volatile String ANIMALS_EXTRA = \\"\\";",
          "public static final String DEF_KIT = \\"%s\\";" % KIT_DEFAULT,
          "public static volatile String STARTER_KIT = \\"%s\\";" % KIT_DEFAULT,
          # 0.5.2 review: slots of the starter chest (Furniture_Crude_Chest_Small, Capacity 18 in Assets.zip) = the most a kit may need
          "public static final int KIT_SLOTS = 18;",
          "public static volatile java.util.HashSet ANIMALS = new java.util.HashSet();"):
    F(cfg, f)
''')
rep('''      for (int i = 0; i < FLAG_IDS.length; i++) {
        int r = rankOf(p.getProperty("defaults.perm." + FLAG_IDS[i]), BUILD_PERM[i]);
        if (r < 0) r = 0;
        if (r > 4) r = 4;
        DEF_PERM[i] = r;
      }''', '''      int[] np = new int[FLAG_IDS.length];
      for (int i = 0; i < FLAG_IDS.length; i++) {
        int r = rankOf(p.getProperty("defaults.perm." + FLAG_IDS[i]), BUILD_PERM[i]);
        if (r < 0) r = 0;
        if (r > 4) r = 4;
        np[i] = r;
      }
      DEF_PERM = np;''')
rep('''      DEF_LIMIT = (int) lng(p, "defaults.visit.limit", 5L, 1L, (long) LIMIT_MAX);''',
    '''      DEF_LIMIT = (int) lng(p, "defaults.visit.limit", 5L, 1L, 100L);   // 0.5.2: the row range; IslandSettings.parse caps each island at LIMIT_MAX''')
rep('''      String ex = p.getProperty("animals.extra", "");''', '''      String ex = p.getProperty("animals.extra", "");
      ANIMALS_EXTRA = ex == null ? "" : ex.trim();
      String kit = p.getProperty("starter.kit");
      STARTER_KIT = kit == null ? DEF_KIT : kit.trim();
      read = true;''')
# 0.5.2 review: when config.properties can't be read (I/O error, a broken unicode escape) every field keeps its running value - ANIMALS too,
# which 0.5.1 rebuilt from the built-in roles alone; now it keeps the running animals.extra roles, so the running set and the Server
# Setup page (ANIMALS_EXTRA) agree. A good read is unchanged. (No field is assigned before the file is fully parsed, and nothing after
# p.load can throw, so a failed read never leaves a half-updated set.)
rep('''  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) an.add(a[i].trim());
  try {
    if (FILE != null) {''', '''  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) an.add(a[i].trim());
  boolean read = false;
  try {
    if (FILE != null) {''')
rep('''  } catch (Throwable t) { @PKG@.IslandStore.warn("could not read config.properties (defaults used): " + t); }
  ANIMALS = an;''', '''  } catch (Throwable t) { @PKG@.IslandStore.warn("could not read config.properties (the values in use stay - the defaults at startup): " + t); }
  if (!read) {
    String[] ke = ANIMALS_EXTRA == null ? new String[0] : ANIMALS_EXTRA.split(",");
    for (int i = 0; i < ke.length; i++) if (ke[i].trim().length() > 0) an.add(ke[i].trim());
  }
  ANIMALS = an;''')

# IslandCfg helpers + the kit schema, right after the loader (the kit needs the bound fields to exist; hooks are checked at kit.write)
rep('''""".replace("%%CFGTEXT%%", CFG_JAVA))
''', r'''""".replace("%%CFGTEXT%%", CFG_JAVA))
# 0.5.2 starter kit (spec 5.5): starter.kit = "id:amount,..." parsed at use time -> { String[] ids, int[] amounts }; a bad entry (only
# possible through a hand edit - the kit validates typed ones) is skipped with a warning
M(cfg, r"""
public static Object[] kitOf(String k) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  String[] a = k == null ? new String[0] : k.split(",");
  for (int i = 0; i < a.length; i++) {
    String e = a[i].trim();
    if (e.length() == 0) continue;
    String id = e;
    int q = 1;
    int c = e.lastIndexOf(':');
    if (c >= 0) {
      id = e.substring(0, c).trim();
      try { q = Integer.parseInt(e.substring(c + 1).trim()); } catch (Throwable t) { q = -1; }
    }
    if (id.length() == 0 || q < 1 || q > 9999) { @PKG@.IslandStore.warn("config starter.kit: entry '" + e + "' skipped (item:amount, amount 1-9999)"); continue; }
    ids.add(id);
    qs.add(Integer.valueOf(q));
  }
  String[] ra = new String[ids.size()];
  int[] qa = new int[ids.size()];
  for (int i = 0; i < ra.length; i++) { ra[i] = (String) ids.get(i); qa[i] = ((Integer) qs.get(i)).intValue(); }
  return new Object[] { ra, qa };
}""")
M(cfg, r"""
public static Object[] kit() {
  return kitOf(STARTER_KIT);
}""")
# 0.5.2 review: chest slots one kit entry takes. The chest splits an amount above the item's stack size over several slots (the engine's
# add / canAddItemStacks work in getMaxStack units), so "18 entries" alone does not make a kit fit the 18-slot chest. An id the live
# item map does not know counts the way the engine counts it (ItemStack.getItem falls back to Item.UNKNOWN, stack size 100). No item
# map at all (never in game) = one slot per entry: the check never refuses a kit it could not measure; the chest stays the judge.
M(cfg, r"""
public static int slotsFor(String id, int q) {
  if (q < 1) return 0;
  int max = 0;
  try {
    Object a = com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id);
    if (!(a instanceof com.hypixel.hytale.server.core.asset.type.item.config.Item)) a = com.hypixel.hytale.server.core.asset.type.item.config.Item.UNKNOWN;
    max = ((com.hypixel.hytale.server.core.asset.type.item.config.Item) a).getMaxStack();
  } catch (Throwable t) { max = 0; }
  if (max < 1) return 1;
  return (q + max - 1) / max;
}""")
M(cfg, r"""
public static int kitSlots(String[] ids, int[] qty) {
  int n = 0;
  for (int i = 0; i < ids.length && i < qty.length; i++) n += slotsFor(ids[i], qty[i]);
  return n;
}""")
# the late-kit chat line ("make room for N stacks"): the chest slots the kit needs (the 0.5.1 kit = 6, as before)
M(cfg, r"""
public static int kitStacks() {
  Object[] k = kit();
  return kitSlots((String[]) k[0], (int[]) k[1]);
}""")
M(cfg, r"""
public static java.util.HashSet animalSet(String base, String extra) {
  java.util.HashSet an = new java.util.HashSet();
  String[] a = base == null ? new String[0] : base.split(",");
  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) an.add(a[i].trim());
  String[] e = extra == null ? new String[0] : extra.split(",");
  for (int i = 0; i < e.length; i++) if (e[i].trim().length() > 0) an.add(e[i].trim());
  return an;
}""")

# =====================================================================================================================
# 0.5.2 admin config kit (research/Server-Setup-Spec.md 4.17 + 5.5, tools/CONFIG-CONTRACT.md). File keys are the 0.5 keys; row key =
# file key. Hooks live in IslandHooks (compiled near the end; kit.write checks them). Flags: live = applies at once (defaults reach
# every island whose owner never changed that value: IslandStore.reparseAll), new = new islands / resets only, danger = confirm.
# =====================================================================================================================
PERM_OPTS = "visitor|Visitor,trusted|Trusted,member|Member,admin|Admin,owner|Owner"
CFG_CATS = [("permissions", "Permissions"), ("visits", "Visitors"), ("coop", "Co-op"), ("limits", "Limits"),
            ("starter", "Starter kit"), ("hub", "Hub"), ("tech", "Technical")]
CFG_ROWS = []
for f in FLAGS:   # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    CFG_ROWS.append(("defaults.perm." + f[0], "Default: " + f[1], "permissions", "choice", f[3], "", "", PERM_OPTS, "", "live,danger",
                     f[2].rstrip(".") + ". Lowest role allowed on islands whose owner never changed it.",
                     "custom:IslandHooks@config.properties:defaults.perm." + f[0]))
CFG_ROWS += [
    ("defaults.visit.mode", "Default visits", "visits", "choice", "public", "", "", "public|Public,friends|Friends only,closed|Closed", "",
     "live", "Islands whose owner never picked: Friends = co-op members + trusted, Closed = co-op members only.",
     "custom:IslandHooks@config.properties:defaults.visit.mode"),
    ("visit.limitMax", "Highest visitor limit", "visits", "int", "10", "1", "100", "step=1", "", "live",
     "The most visitors an owner can allow at once. Lowering it lowers islands above it.",
     "field:IslandCfg.LIMIT_MAX@config.properties:visit.limitMax;after=IslandHooks.afterDefaults"),
    ("defaults.visit.limit", "Default visitor limit", "visits", "int", "5", "1", "100", "step=1", "", "live",
     "Visitors at once on islands whose owner never changed it (never above the highest limit).",
     "field:IslandCfg.DEF_LIMIT@config.properties:defaults.visit.limit;after=IslandHooks.afterDefaults"),
    ("defaults.visit.notify", "Default visit ping", "visits", "bool", "true", "", "", "01", "", "live",
     "Owner + co-op get a chat line when someone visits (islands whose owner never changed it).",
     "field:IslandCfg.DEF_NOTIFY@config.properties:defaults.visit.notify;after=IslandHooks.afterDefaults"),
    ("coop.maxPlayers", "Co-op size", "coop", "int", "5", "1", "50", "step=1", "", "live",
     "Players per co-op INCLUDING the owner. Lowering it removes nobody; a full co-op can't invite.",
     "field:IslandCfg.COOP_MAX@config.properties:coop.maxPlayers"),
    ("coop.adminsInvite", "Island admins may invite", "coop", "bool", "false", "", "", "", "", "live",
     "Off: only the owner invites. Only the owner kicks, promotes, disbands and resets either way.",
     "field:IslandCfg.ADMINS_INVITE@config.properties:coop.adminsInvite"),
    ("invite.seconds", "Co-op invite time", "coop", "int", "60", "10", "3600", "step=10", "s", "live",
     "How long a co-op invite stays open (new invites).",
     "field:IslandCfg.INVITE_SECONDS@config.properties:invite.seconds"),
    ("trusted.max", "Trusted players per island", "limits", "int", "20", "0", "500", "step=5", "", "live",
     "Lowering it removes nobody; a full list can't trust more.",
     "field:IslandCfg.TRUSTED_MAX@config.properties:trusted.max"),
    ("bans.max", "Bans per island", "limits", "int", "100", "0", "1000", "step=10", "", "live",
     "Lowering it lifts no ban; a full list can't ban more.",
     "field:IslandCfg.BANS_MAX@config.properties:bans.max"),
    ("expel.cooldownSeconds", "Expel block", "limits", "int", "60", "0", "86400", "step=10", "s", "live",
     "An expelled player may not come back for this long.",
     "field:IslandCfg.EXPEL_SECONDS@config.properties:expel.cooldownSeconds"),
    ("reset.cooldownHours", "Time between resets", "limits", "int", "24", "0", "8760", "step=1", "h", "live,danger",
     "Every reset makes a new world and keeps the old one on disk. 0 = no wait.",
     "field:IslandCfg.RESET_HOURS@config.properties:reset.cooldownHours;confirm=down"),
    ("reset.confirmSeconds", "Reset confirm window", "limits", "int", "20", "5", "300", "step=5", "s", "live",
     "Owners repeat /island reset 3 times, each within this time.",
     "field:IslandCfg.RESET_CONFIRM@config.properties:reset.confirmSeconds"),
    ("starter.kit", "Starter kit", "starter", "items", KIT_DEFAULT, "0", "18", "qty", "", "new",
     "Put in the chest of every NEW island and after a reset (18 slots). Existing islands keep theirs.",
     "field:IslandCfg.STARTER_KIT@config.properties:starter.kit;check=IslandHooks.checkKit"),
    ("starter.fromHotbar", "Starter kit from my hotbar", "starter", "action", "", "", "", "Use my hotbar", "", "new,danger",
     "Replaces the starter kit with what is in your 9 hotbar slots now (items and amounts).",
     "action:IslandHooks.kitFromHotbar"),
    ("hub.set", "Hub point", "hub", "action", "", "", "", "Set the hub here", "", "live,danger",
     "Where /hub and island logins send players: where you stand now (not on an island). = /sethub",
     "action:IslandHooks.setHub"),
    ("tint.resend", "Grass colour fix", "tech", "choice", "tints", "", "", "tints|Send tints,chunk|Resend chunks,off|Off", "", "live,adv",
     "After a grass re-tint: send the new colours, resend the whole chunks, or nothing.",
     "custom:IslandHooks@config.properties:tint.resend"),
    ("perm.otherProfileStrict", "Strict other-profile rule", "tech", "bool", "true", "", "", "", "", "live,danger,adv",
     "On: a role held on another profile allows only doors, seats, mobs. Off: only dropping is refused.",
     "field:IslandCfg.STRICT_OTHER@config.properties:perm.otherProfileStrict;confirm=off"),
    ("animals.extra", "Extra farm animal roles", "tech", "text", "", "0", "2000", "", "", "live,adv",
     "NPC role names (pet mods) that count as farm animals, comma separated.",
     "field:IslandCfg.ANIMALS_EXTRA@config.properties:animals.extra;check=IslandHooks.checkAnimals;after=IslandHooks.afterAnimals"),
]
CFG_NOTE = "The island layout is built in until the template editor ships. Owners: /island menu."
# the default kit's Skyy_Accessory_Bag is SkyyAccessories' item, not a vanilla asset: allow it for the build-time default check
KIT_OWN_EXTRA = ["Skyy_Accessory_Bag"]
_assets = CFG._items_from_assets()
CFG_ITEMS = None if _assets is None else (set(_assets) | set(KIT_OWN_EXTRA))
for _x in KIT_OWN_EXTRA:
    assert (_x + ":") in KIT_DEFAULT, "KIT_OWN_EXTRA %s is not in the default kit" % _x
# 0.5.2 review: ... and in game. The kit's items check asks the live item map, so without SkyyAccessories the row's OWN default was
# refused ("Unknown item: Skyy_Accessory_Bag.") on reset to default, on Undo / History restore of a kit that holds it, and on any typed
# edit that kept it. The item check of this mod's kit (emit ITEM_FN, one items row: starter.kit) = the live item map plus the default
# kit's own cross-mod ids, so the 0.5.1 default always stays valid (without SkyyAccessories the chest gets what 0.5.1 put there).
# Compiled BEFORE emit: ITEM_FN is compiled straight into CfgRows.itemOk (not a reflection hook).
M(hooks, r"""
public static boolean itemOk(String id) {
  if (id == null) return false;
  if (@OWNX@) return true;
  return com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id) != null;
}""".replace("@OWNX@", " || ".join('id.equals("%s")' % x for x in KIT_OWN_EXTRA)))
kit = CFG.emit(pool, PKG, MOD="SkyyIslands", TITLE="Islands", VERSION=VERSION, NODE="skyyislands.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyIslands/config.properties"], NOTE=CFG_NOTE, RELOAD="IslandHooks.reloadCfg", KEEP=20,
               DEFAULTS={"config.properties": CFG_TEXT}, ITEMS=CFG_ITEMS, ITEM_FN="IslandHooks.itemOk")
''')

# ---------------------------------------------------------------- IslandSettings keeps its properties (for the in-memory re-parse)
rep('''          "public boolean bad;", "public long badAt;"):
    F(sets, f)''', '''          "public boolean bad;", "public long badAt;",
          # 0.5.2: a copy of the parsed properties, so a server default change re-parses the cache without file I/O (reparseAll)
          "public java.util.Properties raw;"):
    F(sets, f)''')
rep('''  @PKG@.IslandSettings s = new @PKG@.IslandSettings();
  s.key = key;
''', '''  @PKG@.IslandSettings s = new @PKG@.IslandSettings();
  s.key = key;
  s.raw = new java.util.Properties();
  s.raw.putAll(p);
''')
rep('''  s.perm = new int[@PKG@.IslandCfg.FLAG_IDS.length];
  for (int i = 0; i < s.perm.length; i++) {
    int r = @PKG@.IslandCfg.rankOf(p.getProperty("perm." + @PKG@.IslandCfg.FLAG_IDS[i]), @PKG@.IslandCfg.DEF_PERM[i]);''',
    '''  s.perm = new int[@PKG@.IslandCfg.FLAG_IDS.length];
  int[] dp = @PKG@.IslandCfg.DEF_PERM;   // 0.5.2: one snapshot (the config kit swaps the whole array)
  for (int i = 0; i < s.perm.length; i++) {
    int r = @PKG@.IslandCfg.rankOf(p.getProperty("perm." + @PKG@.IslandCfg.FLAG_IDS[i]), dp[i]);''')

# ---------------------------------------------------------------- IslandStore part 2: re-parse, kit log line, reload through the kit
rep('''M(st_, r"""
public static synchronized void bump() {
  ISLAND_EPOCH = ISLAND_EPOCH + 1L;
  try { bridge().put("island:epoch", Long.valueOf(ISLAND_EPOCH)); } catch (Throwable t) { }
}""")
''', '''M(st_, r"""
public static synchronized void bump() {
  ISLAND_EPOCH = ISLAND_EPOCH + 1L;
  try { bridge().put("island:epoch", Long.valueOf(ISLAND_EPOCH)); } catch (Throwable t) { }
}""")
# 0.5.2: a server default changed (config kit or RELOAD) -> every cached island is parsed again from its own properties copy (memory
# only, under that island's monitor), so defaults.perm.* / defaults.visit.* / visit.limitMax apply at once. A 'bad' placeholder stays.
M(st_, r"""
public static boolean reparse0(String key) {
  Object o = SETTINGS.get(key);
  if (!(o instanceof @PKG@.IslandSettings)) return false;
  @PKG@.IslandSettings c = (@PKG@.IslandSettings) o;
  if (c.bad || c.raw == null) return false;
  SETTINGS.put(key, @PKG@.IslandSettings.parse(key, c.raw));
  return true;
}""")
M(st_, r"""
public static int reparseAll() {
  int n = 0;
  java.util.ArrayList keys = new java.util.ArrayList(SETTINGS.keySet());
  for (int i = 0; i < keys.size(); i++) {
    String key = (String) keys.get(i);
    boolean done = false;
    try { synchronized (lockOf(key)) { done = reparse0(key); } } catch (Throwable t) { done = false; }
    if (done) n++;
  }
  bump();
  return n;
}""")
# 0.5.2: a change that is not a config row (the hub point) goes into the kit's config-changes.log like the rows (status done: no Undo)
M(st_, r"""
public static void cfgLog(java.util.UUID who, String name, String via, String key, String old, String nw) {
  try {
    @PKG@.CfgLog.add(who, name, via, key, old, nw, "done");
    @PKG@.CfgFile.bump();
    @PKG@.CfgFile.logSoon();
  } catch (Throwable t) { }
}""")
''')
seg('''M(st_, r"""
public static String reloadText() {''', '''# world= switch; when a reset is pending for this key''', ['@PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);', 'int[] r = reloadAll();'],
    r'''# 0.5.2: config.properties goes through the config kit's reload op (hand edits logged via=file; the RELOAD routine runs AFTER the kit's
# pending writes, so a value set in the menu a moment ago is never read back stale); island files are re-read here as before
M(st_, r"""
public static String reloadText(java.util.UUID who, String name) {
  String k = "";
  if (@PKG@.CfgPub.STARTED) {
    try {
      Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, name, "command" });
      if (o instanceof Object[] && ((Object[]) o).length > 2) k = String.valueOf(((Object[]) o)[2]);
      else k = "config.properties was not re-read (see the server log).";
    } catch (Throwable t) { k = "config.properties was not re-read: " + t; }
  } else {
    @PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);
    reparseAll();
    k = "Re-read config.properties.";
  }
  int[] r = reloadAll();
  int n = 0;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid()) { publish(p.getUuid()); n++; }
    }
  } catch (Throwable t) { }
  bump();
  info("reload: config: " + k + " " + r[1] + " of " + r[0] + " island files re-read" + (r[2] > 0 ? ", " + r[2] + " UNREADABLE (their last good copy stays in use)" : "") + ", " + n + " online players republished");
  return (r[2] > 0 ? "-" : "+") + "Config: " + k + " Island files: " + r[1] + " of " + r[0] + " re-read" + (r[2] > 0 ? " - " + r[2] + " could not be read (their last good copy stays in use - see the server log)" : "") + ". " + n + " online players updated.";
}""")
''')

# visit ping per receiver (Settings-Spec 3.10: the island's visit.notify AND the receiver's islands.visitPing); online check first so an
# offline member's settings file is never read
seg('''# chat line to the island's owner and co-op members who are online (any profile), minus up to two players''',
    '''# =====================================================================================================================
# IslandPerms: flag ids''', ['public static void notifyIsland(String ok, String text, String color, java.util.UUID ex1, java.util.UUID ex2) {'],
    r'''# chat line to the island's owner and co-op members who are online (any profile), minus up to two players; 0.5.2: skey = a player Settings
# switch each receiver must have on (null = always sent)
M(st_, r"""
public static void notifyIslandKey(String ok, String text, String color, java.util.UUID ex1, java.util.UUID ex2, String skey) {
  try {
    @PKG@.IslandSettings s = settings(ok);
    java.util.HashSet done = new java.util.HashSet();
    java.util.UUID ou = ownerUuid(ok);
    if (ou != null && !ou.equals(ex1) && !ou.equals(ex2)) {
      done.add(ou);
      @PR@ op = online(ou);
      if (op != null && (skey == null || notifyOn(ou, skey))) say(op, text, color);
    }
    String[] m = split(s.members);
    for (int i = 0; i < m.length; i++) {
      java.util.UUID mu = ownerUuid(m[i]);
      if (mu == null || mu.equals(ex1) || mu.equals(ex2) || done.contains(mu)) continue;
      done.add(mu);
      @PR@ mp = online(mu);
      if (mp != null && (skey == null || notifyOn(mu, skey))) say(mp, text, color);
    }
  } catch (Throwable t) { }
}""")
M(st_, r"""
public static void notifyIsland(String ok, String text, String color, java.util.UUID ex1, java.util.UUID ex2) {
  notifyIslandKey(ok, text, color, ex1, ex2, null);
}""")

''')

# ---------------------------------------------------------------- player Settings gates (only the sends)
rep('''    @PKG@.IslandStore.WARNED.put(u, Long.valueOf(now));
    @PKG@.IslandStore.say(pr, denyText(owner, s, rank, u, flag, extra), "#ff9d6b");''',
    '''    @PKG@.IslandStore.WARNED.put(u, Long.valueOf(now));
    if (@PKG@.IslandStore.notifyOn(u, "islands.protection")) @PKG@.IslandStore.say(pr, denyText(owner, s, rank, u, flag, extra), "#ff9d6b");''')
rep('''        @PKG@.IslandStore.say(pr, "[Island] Visiting " + on + "'s island - PvP " + (s.pvp ? "ON" : "off") + " - visitors may: " + @PKG@.IslandPerms.visitorAllowedText(s) + ".", "#cfe3ff");''',
    '''        if (@PKG@.IslandStore.notifyOn(u, "islands.visitWelcome")) @PKG@.IslandStore.say(pr, "[Island] Visiting " + on + "'s island - PvP " + (s.pvp ? "ON" : "off") + " - visitors may: " + @PKG@.IslandPerms.visitorAllowedText(s) + ".", "#cfe3ff");''')
rep('''            @PKG@.IslandStore.notifyIsland(owner, "[Island] " + pr.getUsername() + " is visiting your island. /island menu (Visitors tab) to expel or ban.", "#ffe08a", u, null);''',
    '''            @PKG@.IslandStore.notifyIslandKey(owner, "[Island] " + pr.getUsername() + " is visiting your island. /island menu (Visitors tab) to expel or ban.", "#ffe08a", u, null, "islands.visitPing");''')
rep('''      @PKG@.IslandStore.say(pr, "[Island] Welcome to " + on + "'s island - you are Trusted here (you may build).", "#8fc8ff");''',
    '''      if (@PKG@.IslandStore.notifyOn(u, "islands.visitWelcome")) @PKG@.IslandStore.say(pr, "[Island] Welcome to " + on + "'s island - you are Trusted here (you may build).", "#8fc8ff");''')
rep('''  @PKG@.IslandStore.say(target, "[Island] " + pr.getUsername() + " trusted you on " + on + "'s island: you may build there (/island visit " + on + "). Your own /island does not change.", "#8fc8ff");''',
    '''  if (@PKG@.IslandStore.notifyOn(tu, "islands.buildRights")) @PKG@.IslandStore.say(target, "[Island] " + pr.getUsername() + " trusted you on " + on + "'s island: you may build there (/island visit " + on + "). Your own /island does not change.", "#8fc8ff");''')
rep('''    if (@PKG@.HubCmd.sendToHub(st, r, pr, w)) pr.sendMessage(@MSG@.raw("[Island] Welcome back! You start in the hub - /island takes you home."));''',
    '''    boolean sent = @PKG@.HubCmd.sendToHub(st, r, pr, w);   // 0.5.2: the teleport never depends on the player's setting
    if (sent && @PKG@.IslandStore.notifyOn(pr.getUuid(), "islands.hubOnLogin")) pr.sendMessage(@MSG@.raw("[Island] Welcome back! You start in the hub - /island takes you home."));''')

# ---------------------------------------------------------------- starter kit from config
rep('''    String[] ids = new String[] { "Bench_WorkBench", "Wood_Oak_Trunk", "Soil_Dirt", "Ingredient_Stick", "Food_Bread", "Skyy_Accessory_Bag" };
    int[] qty = new int[] { 1, 10, 8, 8, 5, 1 };''', '''    Object[] kit = @PKG@.IslandCfg.kit();   // 0.5.2: config starter.kit (default = the 0.5.1 kit, same order and amounts)
    String[] ids = (String[]) kit[0];
    int[] qty = (int[]) kit[1];
    if (ids.length == 0) { @PKG@.IslandStore.info("starter kit is empty (config starter.kit) - nothing put in the chest in " + world.getName()); return 0; }''')
# 0.5.2 review: every kit entry is built in its own try (a stack the engine refuses - ItemStack(id, qty) throws for id "Empty", only
# reachable through a hand edit - drops that entry with a warning instead of the whole kit); the add loop walks the stacks that were
# built. A kit that needs more slots than the chest has (possible only through a hand edit: checkKit refuses it in game) is named in
# the server log, since no island can ever get it. With the 0.5.1 kit every line below behaves as before.
seg('''    java.util.ArrayList all = new java.util.ArrayList();
    for (int i = 0; i < ids.length; i++) all.add(new @IS@(ids[i], qty[i]));''', '''    @PKG@.IslandStore.info("starter kit placed in " + world.getName() + " (" + n + " of " + ids.length + " stacks"''',
    ['boolean room = true;', 'int lost = 0;', 'c.addItemStack((@IS@) all.get(i));', '} catch (Throwable t) { @PKG@.IslandStore.warn("starter kit item " + ids[i]'],
    '''    java.util.ArrayList all = new java.util.ArrayList();
    java.util.ArrayList at = new java.util.ArrayList();   // 0.5.2 review: index into ids / qty of each stack in all
    for (int i = 0; i < ids.length; i++) {
      try { all.add(new @IS@(ids[i], qty[i])); at.add(Integer.valueOf(i)); }
      catch (Throwable t) { @PKG@.IslandStore.warn("config starter.kit: " + ids[i] + " x " + qty[i] + " skipped (the game refused that stack: " + t + ")"); }
    }
    if (all.isEmpty()) { @PKG@.IslandStore.info("starter kit: no usable stack in config starter.kit - nothing put in the chest in " + world.getName()); return 0; }
    // 0.5 review: the late-kit path fills a chest players may already use - nothing is added unless the WHOLE kit fits (-2 = kept
    // for a later arrival, the island is not marked); every item's leftover is still checked and logged by id and quantity
    boolean room = true;
    try { room = c.canAddItemStacks(all); } catch (Throwable t) { room = true; }
    if (!room) {
      int need = @PKG@.IslandCfg.kitSlots(ids, qty);
      int cap = -1;
      try { cap = c.getCapacity(); } catch (Throwable t) { cap = -1; }
      if (cap > 0 && need > cap) @PKG@.IslandStore.warn("config starter.kit needs " + need + " chest slots but the starter chest has " + cap + " - no island can get it: make the kit smaller (Server Setup -> Islands -> Starter kit, or edit the file + /island reload)");
      @PKG@.IslandStore.info("starter kit: the chest in " + world.getName() + " has no room for the " + all.size() + " kit stacks - kept for a later arrival");
      return -2;
    }
    int lost = 0;
    for (int k = 0; k < all.size(); k++) {
      int i = ((Integer) at.get(k)).intValue();
      try {
        @ISTX@ tx = c.addItemStack((@IS@) all.get(k));
        int left = qty[i];
        if (tx != null) {
          @IS@ rem = tx.getRemainder();
          int rq = (rem == null || rem.isEmpty()) ? 0 : rem.getQuantity();
          left = tx.succeeded() ? rq : (rq > 0 ? rq : qty[i]);
        }
        if (left < qty[i]) n++;
        if (left > 0) { lost += left; @PKG@.IslandStore.warn("starter kit in " + world.getName() + ": " + left + " x " + ids[i] + " did not fit in the chest"); }
      } catch (Throwable t) { @PKG@.IslandStore.warn("starter kit item " + ids[i] + " (" + qty[i] + ") not placed: " + t); }
    }
''')
rep('''"[Island] Your starter kit is waiting: make room for 6 stacks in the chest your island started with''',
    '''"[Island] Your starter kit is waiting: make room for " + @PKG@.IslandCfg.kitStacks() + " stacks in the chest your island started with''')

# ---------------------------------------------------------------- /island reload through the kit
rep('''    @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.reloadText());''',
    '''    @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.reloadText(pr.getUuid(), pr.getUsername()));''')

# ---------------------------------------------------------------- /sethub: shared with the "Hub point" action, logged through the kit
seg('''M(shub, r"""
protected void execute(''', '''# ================= login routing (0.2.1) + arrival (0.5)''', ['@PKG@.IslandStore.saveHub(world.getName()'],
    r'''# 0.5.2: the /sethub logic, shared with the config kit's "Hub point" action (HubHereTask); same texts as 0.5.1, and a successful move is
# written to config-changes.log (key hub.set, status done) so the Server Setup Changes view shows it
M(shub, r"""
public static String setHere(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world, String via) {
  if (@PKG@.IslandStore.isIslandWorld(world.getName())) return "[Island] The hub cannot be inside an island world.";
  @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
  if (tc == null || tc.getTransform() == null) return "[Island] Could not read your position.";
  @TRF@ t = tc.getTransform();
  org.joml.Vector3d p = t.getPosition();
  @R3F@ r = t.getRotation();
  String hw = @PKG@.IslandStore.HUB_WORLD;
  double[] hp = @PKG@.IslandStore.HUB_POS;
  String was = (hw == null || hp == null) ? "(not set)" : hw + " " + (int) hp[0] + "," + (int) hp[1] + "," + (int) hp[2];
  @PKG@.IslandStore.saveHub(world.getName(), p.x, p.y, p.z, r == null ? 0f : r.x, r == null ? 0f : r.y, r == null ? 0f : r.z);
  @PKG@.IslandStore.cfgLog(pr.getUuid(), pr.getUsername(), via, "hub.set", was, world.getName() + " " + (int) p.x + "," + (int) p.y + "," + (int) p.z);
  return "[Island] Hub set here in world '" + world.getName() + "' (" + (int) p.x + ", " + (int) p.y + ", " + (int) p.z + "). /hub and island logins now come here.";
}""")
M(shub, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    pr.sendMessage(@MSG@.raw(setHere(store, ref, pr, world, "command")));
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("/sethub failed: " + t);
    pr.sendMessage(@MSG@.raw("[Island] Could not set the hub: " + t.getMessage()));
  }
}""")

# ================= 0.5.2: world-thread tasks for the config kit's actions, then IslandHooks (the kit's hooks; kit.write checks them) =====
hht.addInterface(pool.get("java.lang.Runnable"))
F(hht, "public @PR@ pr;")
F(hht, "public String worldName;")
F(hht, "public String via;")
C(hht, "public HubHereTask(@PR@ p, String wn, String v) { this.pr = p; this.worldName = wn; this.via = v; }")
M(hht, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) { @PKG@.IslandStore.tell(pr, "-You changed worlds before the hub was set - nothing changed. Try again."); return; }
    @REF@ ref = pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    pr.sendMessage(@MSG@.raw(@PKG@.SetHubCmd.setHere(st, ref, pr, w, this.via)));
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("hub point action failed: " + t);
    @PKG@.IslandStore.tell(pr, "-Could not set the hub - the server log has the details.");
  }
}""")
kht.addInterface(pool.get("java.lang.Runnable"))
F(kht, "public @PR@ pr;")
F(kht, "public String worldName;")
F(kht, "public java.util.UUID who;")
F(kht, "public String name;")
F(kht, "public String via;")
C(kht, "public KitHotbarTask(@PR@ p, String wn, java.util.UUID u, String n, String v) { this.pr = p; this.worldName = wn; this.who = u; this.name = n; this.via = v; }")
# the 9 hotbar stacks as "id:amount,..." (the same id twice is added up, max 9999; item metadata is not kept - spec 5.5), null = empty
M(kht, r"""
public static String hotbarText(@PLA@ p) {
  com.hypixel.hytale.server.core.inventory.Inventory inv = p.getInventory();
  if (inv == null) return null;
  @IC@ hb = inv.getHotbar();
  if (hb == null) return null;
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  short cap = hb.getCapacity();
  for (short sl = 0; sl < cap; sl++) {
    @IS@ it = hb.getItemStack(sl);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id == null || id.length() == 0) continue;
    int q = it.getQuantity();
    Object had = m.get(id);
    if (had instanceof Integer) q = q + ((Integer) had).intValue();
    if (q > 9999) q = 9999;
    if (q < 1) q = 1;
    m.put(id, Integer.valueOf(q));
  }
  if (m.isEmpty()) return null;
  StringBuilder sb = new StringBuilder();
  java.util.Iterator e = m.keySet().iterator();
  while (e.hasNext()) {
    String k = (String) e.next();
    if (sb.length() > 0) sb.append(',');
    sb.append(k).append(':').append(((Integer) m.get(k)).intValue());
  }
  return sb.toString();
}""")
M(kht, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) { @PKG@.IslandStore.tell(pr, "-You changed worlds before your hotbar was read - the starter kit was not changed. Try again."); return; }
    @REF@ ref = pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.IslandStore.tell(pr, "-Could not read your hotbar - the starter kit was not changed."); return; }
    String text = hotbarText(p);
    if (text == null) { @PKG@.IslandStore.tell(pr, "-Your hotbar is empty - put the starter kit in your 9 hotbar slots, then try again. Nothing was changed."); return; }
    Object[] r = @PKG@.CfgFn.set("starter.kit", text, this.who, this.name, "yes", this.via);
    String stt = (r == null || r.length < 3) ? "error" : String.valueOf(r[0]);
    String msg = (r == null || r.length < 3) ? "Could not change the starter kit - see the server log." : String.valueOf(r[2]);
    @PKG@.IslandStore.tell(pr, ((stt.equals("ok") || stt.equals("restart")) ? "+" : "-") + msg);
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("starter kit from hotbar failed: " + t);
    @PKG@.IslandStore.tell(pr, "-Something went wrong - the server log has the details.");
  }
}""")
M(hooks, r"""public static Object[] R(String st, String v, String m) { return new Object[] { st, v, m }; }""")
M(hooks, r"""
public static int permIndex(String key) {
  if (key == null || !key.startsWith("defaults.perm.")) return -1;
  return @PKG@.IslandCfg.flagIndex(key.substring(14));
}""")
M(hooks, r"""
public static String tintName(int m) {
  if (m == 0) return "off";
  if (m == 2) return "chunk";
  return "tints";
}""")
# the loader's rule: off -> 0, chunk -> 2, anything else -> 1 (tints)
M(hooks, r"""
public static int tintOf(String v) {
  String t = v == null ? "tints" : v.trim().toLowerCase();
  if (t.equals("off")) return 0;
  if (t.equals("chunk")) return 2;
  return 1;
}""")
# copy on write (spec 4.17): readers only ever see a whole array
M(hooks, r"""
public static synchronized void permPut(int i, int r) {
  int[] a = @PKG@.IslandCfg.DEF_PERM;
  int[] n = new int[a.length];
  System.arraycopy(a, 0, n, 0, a.length);
  n[i] = r;
  @PKG@.IslandCfg.DEF_PERM = n;
}""")
M(hooks, r"""
public static String customGet(String key) {
  int i = permIndex(key);
  if (i >= 0) { int[] a = @PKG@.IslandCfg.DEF_PERM; return @PKG@.IslandCfg.rankName(a[i]); }
  if ("defaults.visit.mode".equals(key)) return @PKG@.IslandCfg.modeName(@PKG@.IslandCfg.DEF_MODE);
  if ("tint.resend".equals(key)) return tintName(@PKG@.IslandCfg.TINT_RESEND);
  return null;
}""")
# the kit validated the value against the row's choice list already; the 4th element is the file line the kit writes, versions and logs
M(hooks, r"""
public static Object[] customSet(String key, String value) {
  String v = value == null ? "" : value.trim().toLowerCase();
  int i = permIndex(key);
  if (i >= 0) {
    int r = @PKG@.IslandCfg.rankOf(v, -1);
    if (r < 0 || r > 4) return R("bad", null, "Must be visitor, trusted, member, admin or owner.");
    permPut(i, r);
    @PKG@.IslandStore.reparseAll();
    String c1 = @PKG@.IslandCfg.rankName(r);
    return new Object[] { "ok", c1, null, new String[] { key, c1 } };
  }
  if ("defaults.visit.mode".equals(key)) {
    int m = @PKG@.IslandCfg.modeOf(v, -1);
    if (m < 0) return R("bad", null, "Must be public, friends or closed.");
    @PKG@.IslandCfg.DEF_MODE = m;
    @PKG@.IslandStore.reparseAll();
    String c2 = @PKG@.IslandCfg.modeName(m);
    return new Object[] { "ok", c2, null, new String[] { key, c2 } };
  }
  if ("tint.resend".equals(key)) {
    if (!v.equals("tints") && !v.equals("chunk") && !v.equals("off")) return R("bad", null, "Must be tints, chunk or off.");
    @PKG@.IslandCfg.TINT_RESEND = tintOf(v);
    return new Object[] { "ok", v, null, new String[] { key, v } };
  }
  return R("unknown", null, "Unknown setting: " + key + ".");
}""")
# History restore: the value a file copy stands for, read the way IslandCfg.load reads it
M(hooks, r"""
public static String customRead(String key, java.util.Map fileValues) {
  Object o = fileValues == null ? null : fileValues.get(key);
  String raw = (o instanceof String) ? (String) o : null;
  int i = permIndex(key);
  if (i >= 0) {
    int r = @PKG@.IslandCfg.rankOf(raw, @PKG@.IslandCfg.BUILD_PERM[i]);
    if (r < 0) r = 0;
    if (r > 4) r = 4;
    return @PKG@.IslandCfg.rankName(r);
  }
  if ("defaults.visit.mode".equals(key)) return @PKG@.IslandCfg.modeName(@PKG@.IslandCfg.modeOf(raw, 0));
  if ("tint.resend".equals(key)) return tintName(tintOf(raw));
  return null;
}""")
M(hooks, r"""
public static String checkAnimals(String key, String value) {
  if (value == null) return null;
  String[] a = value.split(",");
  for (int i = 0; i < a.length; i++) {
    String e = a[i].trim();
    if (e.length() == 0) continue;
    boolean ok = e.length() <= 64;
    for (int k = 0; ok && k < e.length(); k++) {
      char c = e.charAt(k);
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) ok = false;
    }
    if (!ok) return "Role names are letters, digits and _ (comma separated) - not: " + @PKG@.IslandStore.cleanName(e) + (e.length() > 32 ? "..." : "") + ".";
  }
  return null;
}""")
# 0.5.2 review: starter.kit check= (typed values, "Use my hotbar", reset to default, import, History restore / Undo): the kit must fit
# the 18-slot starter chest counted in real slots (an amount above the item's stack size takes several), or no island could get it
M(hooks, r"""
public static String checkKit(String key, String value) {
  if (value == null) return null;
  Object[] k = @PKG@.IslandCfg.kitOf(value);
  int need = @PKG@.IslandCfg.kitSlots((String[]) k[0], (int[]) k[1]);
  if (need > @PKG@.IslandCfg.KIT_SLOTS) return "That kit needs " + need + " chest slots, but the starter chest has " + @PKG@.IslandCfg.KIT_SLOTS + " (an amount above an item's stack size takes more than one slot).";
  return null;
}""")
M(hooks, r"""
public static void afterDefaults(String key) {
  @PKG@.IslandStore.reparseAll();
}""")
M(hooks, r"""
public static void afterAnimals(String key) {
  @PKG@.IslandCfg.ANIMALS = @PKG@.IslandCfg.animalSet(@PKG@.IslandCfg.BASE_ANIMALS, @PKG@.IslandCfg.ANIMALS_EXTRA);
}""")
# the kit's RELOAD (hand edits, the reload op): the loader parses config.properties into the fields (no world access), then the cache
M(hooks, r"""
public static void reloadCfg() {
  @PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);
  @PKG@.IslandStore.reparseAll();
}""")
M(hooks, r"""
public static @WLD@ worldOf(@PR@ pr) {
  try {
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return null;
    @WLD@ w = @UNI@.get().getWorld(wu);
    return (w != null && w.isAlive()) ? w : null;
  } catch (Throwable t) { return null; }
}""")
# actions need the admin's position / hotbar: schedule on their world thread and answer "working on it" (contract guarantee 3).
# via "menu": the kit's action hook contract is (UUID who, String name) - it passes no via. The kit logs the action line itself with
# the real via (CfgFn.opAction); the follow-up line (hub.set / starter.kit) says menu = SkyyMenu, the only caller of opAction today.
M(hooks, r"""
public static Object[] setHub(java.util.UUID who, String name) {
  @PR@ pr = @PKG@.IslandStore.online(who);
  if (pr == null) return R("bad", null, "Only an admin who is in game can use this: stand where the hub should be (or type /sethub there).");
  @WLD@ w = worldOf(pr);
  if (w == null) return R("error", null, "Could not find your world - try /sethub.");
  if (@PKG@.IslandStore.isIslandWorld(w.getName())) return R("bad", null, "The hub cannot be inside an island world - go where the hub should be first.");
  w.execute(new @PKG@.HubHereTask(pr, w.getName(), "menu"));
  return R("ok", null, "Setting the hub where you stand now - the chat shows where.");
}""")
M(hooks, r"""
public static Object[] kitFromHotbar(java.util.UUID who, String name) {
  @PR@ pr = @PKG@.IslandStore.online(who);
  if (pr == null) return R("bad", null, "Only an admin who is in game can use this: put the kit in your hotbar first.");
  @WLD@ w = worldOf(pr);
  if (w == null) return R("error", null, "Could not find your world - try again in a moment.");
  w.execute(new @PKG@.KitHotbarTask(pr, w.getName(), who, name, "menu"));
  return R("ok", null, "Reading your hotbar - the new starter kit is shown in the chat in a moment.");
}""")

''')

# ---------------------------------------------------------------- plugin: register the switches, publish the kit LAST; flush on shutdown
rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  boolean tpl = false;''', '''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  // 0.5.2 player Settings (research/Settings-Spec.md 2.2 / 3.10): labels and help lines exactly as specified, category profiles, default ON
  @PKG@.IslandStore.regSetting("islands.protection", "Island protection warnings", "profiles", true, "You can only build on islands you are a member of - at most every 3 s");
  @PKG@.IslandStore.regSetting("islands.hubOnLogin", "Hub on login", "profiles", true, "Welcome back! You start in the hub - when you log in on an island");
  @PKG@.IslandStore.regSetting("islands.buildRights", "Build rights given to you", "profiles", true, "Steve gave you build rights on their island");
  @PKG@.IslandStore.regSetting("islands.visitPing", "Visitors on your island", "profiles", true, "Steve is visiting your island - the island's Visit ping must be on too");
  @PKG@.IslandStore.regSetting("islands.visitWelcome", "Welcome when you visit", "profiles", true, "What visitors may do, when you arrive on someone's island");
  boolean tpl = false;''')
rep('''template SkyyIsland " + (tpl ? "found" : "NOT FOUND - check Server/Instances in the jar") + ")");
}""".replace("%%ANIMALS%%", ANIMALS_CSV))''', '''template SkyyIsland " + (tpl ? "found" : "NOT FOUND - check Server/Instances in the jar") + ")");
  // 0.5.2: admin config kit - config:def:SkyyIslands + config:fn:SkyyIslands, at the END of setup(), after IslandCfg.load (never throws)
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("%%ANIMALS%%", ANIMALS_CSV))''')
rep('''    b.remove("island:perm:fn"); b.remove("island:role:fn"); b.remove("island:owner:fn"); b.remove("island:coop:fn");
  } catch (Throwable t) { }
  super.shutdown();''', '''    b.remove("island:perm:fn"); b.remove("island:role:fn"); b.remove("island:owner:fn"); b.remove("island:coop:fn");
  } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }   // 0.5.2: pending config writes + change-log lines now
  super.shutdown();''')
rep('''for c in ALL + SUBS + [pl]:
    c.writeFile(OUT)
print("classes written:", len(ALL + SUBS) + 1)''', '''for c in ALL + SUBS + [pl]:
    c.writeFile(OUT)
kit.write(OUT)   # 0.5.2: deferred hook checks (IslandHooks custom/check/after/action/RELOAD), then the 7 kit classes
print("classes written:", len(ALL + SUBS) + 1 + len(kit.classes), "(%d kit)" % len(kit.classes))''')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
