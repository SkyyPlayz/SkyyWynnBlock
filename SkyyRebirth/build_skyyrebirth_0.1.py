"""SkyyRebirth 0.1 - build script (javassist via jpype). A NEW small mod: the rebirth (New Game+) module, round R2 of
research/cloud/Rebirth-Spec.md section 6 (Skyy's answers: docs/answered/economy.md 2026-10-13 REBIRTH lines, which win).
Run:   python SkyyRebirth/build_skyyrebirth_0.1.py   -> SkyyRebirth/SkyyRebirth-0.1.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyRebirth/test_skyyrebirth_0.1.py --dir tools/dev/scratch/<yours>/rb   (bare JVM, -Xverify:all, every code path executed)

SKYY'S WORDS: Q1 "Yes (Recommended)" = its own small jar now, a module inside the merged character mod at the SkyyCore merge (it only
talks through the bridge, so the move needs no code change); Q3 "acrobatics yes, exploration, no."; Q11 "recommended curve. (tracks xp
gained past max lvl, for bonus points.)"; Q12 "+10 levels, +1 rank (Recommended)"; Q13 "10 (Recommended)"; Q16 "Per profile". Existing
mods checked (spec 0 + this round's look at CurseForge / the Mods folder): no Hytale mod does prestige / rebirth - we build our own.

WHAT 0.1 IS (the whole feature is OFF by default - Server Setup -> Rebirth -> "Rebirth (whole feature)"):
  - The rebirth COUNTER and the per-profile FILES (spec 4.2): Skyy_SkyyRebirth/players/<pkey>.properties with n, pts.<Arm>, spent.<Arm>,
    node.<id>, title, cos.<n>, lastTx, hist.<n>. 0.1 only READS them (nobody can rebirth yet - the two-phase commit is R3); RbStore.save
    (atomic tmp + move, refused for an unreadable file) is there for R3 and the harness. A profile file is read OFF the world thread
    (the SkyyRebirth-IO thread; until it is read the profile counts as 0 rebirths), cached per pkey, never re-read while cached.
    Skyy_SkyyRebirth/journal/ is reserved for R3's journal (not created).
  - The BRIDGE KEYS of the spec's data model (4.3), java.lang types only, never throwing:
      rebirth:n:<uuid>        Integer rebirths of the ACTIVE profile (published for online players every 5 s = republished after a
                              profile:epoch switch; removed when the player leaves; fix 2: ABSENT while a newly active profile's file is
                              still being read - never a false 0 and never the previous profile's count)
      rebirth:fn:count        apply(String pkey or UUID) -> Integer (null while the profile's file is still being read)
      rebirth:fn:cap          apply(Object[] { pkey or UUID, String kind, Integer today's cap }) -> Integer cap: today's + caps.levels x n
                              (kind = a skill / class skill name), + caps.ranks x n (kind collection / rank), Exploration NEVER rises
                              (it never resets, Q3); no base = null; n counts at most rebirth.max (a hand-edited n=50 raises
                              nothing past max x the rise). NOTE: Object[] has THREE elements (the spec 4.3 row says {pkey, skill} -
                              the base is needed; the spec row is to be updated by the main session). The caps follow the SAVED
                              count even while rebirth.on is false: switching the feature off never takes earned caps away. cap / node / dustmult answer null while the profile's file is still being
                              read (SkyySkills then asks again in 250 ms instead of keeping 'no raise' for 5 s). SkyySkills 0.4.35 asks it per profile (cached 5 s there).
      rebirth:fn:node         apply(Object[] { pkey or UUID, String node id }) -> Integer level (0 = not bought)
      rebirth:fn:dustmult     apply(Object[] { pkey or UUID, String tree }) -> Double: (n >= 1 ? dust.first : 1) x (1 + dust.perNode x the
                              level of node <Arm>.dust) - spec 3.4 / Q4 "first rebirth gives 2x all dust"; Acrobatics / Exploration
                              (no arm) get the first-rebirth factor only
      rebirth:busy:<uuid>     Boolean, the ACTIVE profile is inside a rebirth (published with rebirth:n:<uuid>; 0.1: always false)
      rebirth:fn:busy         apply(pkey or UUID) -> Boolean (0.1: always false - no rebirth can run)
      rebirth:fn:decision     apply(String txid) -> "unknown" (0.1 has no journal)
      rebirth:version         "0.1" (removed at shutdown)
  - /rebirth (every player when rebirth is ON; ADMINS (skyyrebirth.admin) only while it is OFF - view only): ONE page with the Nexus of
    the Void in the middle of the 8-arm tree (Class at the top, then Foraging, Mining, Smithing, Alchemy, Farming, Fishing, Cooking
    clockwise - research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md 1.2), and on the left "Your rebirth": the requirement checklist
    (spec 2.1: rebirth switched on, class at max class level, rebirths left, not in combat, on your island or at the hub; open Bazaar /
    AH orders = an info line until R4's Continue button) and what you would get (points per arm by the spec 3.5 curve from skill:fn:run,
    caps, title; every left-panel line is ONE line, measured at build time). HOVER the Nexus = the same checklist + rewards in full as its tooltip (TooltipText b.set like vanilla MemoriesPage; the inline
    TextTooltipStyle is the kit's UNVERIFIED "tooltip" probe - the left panel shows everything too, so nothing depends on it). NO rebirth
    button (R3). The tree nodes are drawn as locked discs (88 = 8 arms x rows 3 / 3 / 2 / 2 / 1) at their final places - THE PROBE of
    "can the radiating tree be drawn on one page" (see THE PROBE below). No diagonal lines (the UI cannot rotate; spec 5 item 2 = line
    pictures, which need the kit to verify a mod texture first) and no Nexus picture (same reason: skyyui only allows the vanilla
    textures it verifies) - the Nexus is a dark disc with its name.
  - Server Setup (tools/skyycfg.py, KEEP=10): rebirth.on (false; switching it ON asks to confirm), rebirth.max 10, caps.levels 10,
    caps.ranks 1, dust.first 2, dust.perNode 0.25.
THE PROBE (radiating tree on one inline page): page 1120 x 952 (the widest verified page size); tree canvas 810 x 880, centre
  (405, 440), rows at radius 169 / 221 / 274 / 325 / 371 (the page spec's 178 / 233 / 288 / 342 / 390 x 0.95 to fit 810 wide), nodes 28 px
  (keystone 34; the mockup's 36 / 44 px squares overlap on the diagonal arms at this size), sideways -48 / 0 / +48 (3 nodes) and -30 / +30
  (2 nodes), arm chips 80 x 22 at radius 107 (N / E / S / W) and 124 (diagonals), the Nexus 120 x 120. The build asserts every node inside the canvas and at least
  6 px between any two nodes, chips and the Nexus; it prints the element count and the inline markup size, and the harness builds the
  page into a real CustomPage packet and compares its size with the protocol's CustomPage.MAX_SIZE.
NOT in 0.1 (later rounds, spec section 6): the rebirth itself + /rebirthadmin (R3), Continue / auto-close orders (R4), tree buying /
  points / titles / cosmetics / stat boost (R8), every participant mod (R5-R9).
"""
import sys, os, re, json, zipfile, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()
KIT_ID = SUI.kit_id()
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.rebirth"
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "EST":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PM":   "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    "PKG":  PKG,
    "VERSION": VERSION,
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
for c, m in ((T["PM"], "get"), (T["PM"], "hasPermission"), (T["UNI"], "get"), (T["UNI"], "getPlayers"), (T["UNI"], "getDefaultWorld"),
             (T["UNI"], "getWorld"), (T["WLD"], "getName"), (T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "isValid"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["EST"], "getWorld"), (T["ST"], "getExternalData"),
             (T["ST"], "getComponent"), (PB, "shutdown"), (PB, "getDataDirectory"), (PB, "getCommandRegistry"), (PB, "getLogger"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "setPermissionGroups"),
             (T["MSG"], "raw"), (T["MSG"], "color"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"),
             (T["EVD"], "of"), (T["BT"], "Activating"), (T["PAGE"], "close"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "build"),
             (PGM, "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def jlit(s):
    return json.dumps(s)


def mk(name, sup=None, ifaces=()):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    for i in ifaces:
        c.addInterface(pool.get(i))
    return c


# ================= the 8 arms (spec 2.3, Q2) in page order: Class at the top, then clockwise (Rebirth-Page-Spec 1.2) =================
# (name, skill:fn:run skill, points base B (spec 3.5: 12 Class, 8 each skill), colour = data colour (the SkyySkills row colours; Class gold))
UI_DATA_COLORS = ["#E8A93B", "#8fe08a", "#8fc8ff", "#c0c8d0", "#7fe0d0", "#f0d060", "#6fb7e8", "#ffb070",   # lint: data colours - the 8 arms,
                  "#121825", "#0b1224(0.92)", "#0b0818", "#2a1f3d"]                                       # a locked node, a chip, the Nexus asleep / awake
ARMS = [(n, k, b, c) for (n, k, b), c in zip([("Class", "class", 12), ("Foraging", "foraging", 8), ("Mining", "mining", 8),
                                               ("Smithing", "smithing", 8), ("Alchemy", "alchemy", 8), ("Farming", "farming", 8),
                                               ("Fishing", "fishing", 8), ("Cooking", "cooking", 8)], UI_DATA_COLORS[:8])]
NODE_LOCKED, CHIP_BG, NEXUS_SLEEP, NEXUS_AWAKE = UI_DATA_COLORS[8:12]
GOOD, BAD, INFO, GOLD, MUTED, WARN = (SUI.COLOR["success"], SUI.COLOR["error"], SUI.COLOR["info"], SUI.COLOR["gold"], SUI.COLOR["text"],
                                      SUI.COLOR["warning"])

# ================= config text (the kit's DEFAULTS and the mod's own first-run file are the same text) =================
CONFIG_TEXT = "\n".join([
    "# SkyyRebirth settings (research/cloud/Rebirth-Spec.md). Change them in game: SkyWynn Menu -> Server Setup -> Rebirth, or edit here.",
    "# rebirth.on = the whole rebirth feature. false (default): players cannot open /rebirth; admins (skyyrebirth.admin) can view it.",
    "# SkyyRebirth 0.1 never resets anything (no rebirth button yet).",
    "rebirth.on=false",
    "# rebirth.max = how many rebirths one profile can do (Skyy: 10 at launch).",
    "rebirth.max=10",
    "# caps.levels = class + skill level caps rise this much per rebirth (Exploration never). caps.ranks = the collection rank cap rise.",
    "caps.levels=10",
    "caps.ranks=1",
    "# dust.first = the Dust multiplier from the first rebirth on (all Dust). dust.perNode = + this per level of an arm's Dust node.",
    "dust.first=2",
    "dust.perNode=0.25",
    "",
])

# ================= RbCfg fields (the kit binds them, so they exist before CFG.emit) =================
cfg = mk("RbCfg")
for f in ("public static volatile boolean ON = false;", "public static volatile int MAX = 10;", "public static volatile int LEVELS = 10;",
          "public static volatile int RANKS = 1;", "public static volatile double DUST_FIRST = 2.0;", "public static volatile double DUST_NODE = 0.25;",
          "public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;", "public static @LOG@ LOG;",
          "public static volatile java.util.Map BRIDGE;", "public static volatile java.util.function.Function PERM_TEST;",
          "public static volatile String HUB_TEST;", "public static volatile java.util.ArrayList TEST_ONLINE;",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT)):
    F(cfg, f)

# ================= the admin config kit (tools/CONFIG-CONTRACT.md) =================
CATS = [("rebirth", "Rebirth"), ("rewards", "Rewards")]
ROWS = [
    ("rebirth.on", "Rebirth (whole feature)", "rebirth", "bool", "false", "", "", "", "", "live,danger",
     "Off: only admins can view /rebirth. 0.1 has no rebirth button yet - nothing is ever reset.",
     "field:RbCfg.ON@config.properties:rebirth.on;confirm=on"),
    ("rebirth.max", "Max rebirths per profile", "rebirth", "int", "10", "1", "100", "", "", "live",
     "How many rebirths one profile can do (Skyy: 10 at launch).", "field:RbCfg.MAX@config.properties:rebirth.max"),
    ("caps.levels", "Level cap rise per rebirth", "rewards", "int", "10", "0", "100", "", "", "live",
     "Class + skill level caps rise this much per rebirth. Exploration never rises.",
     "field:RbCfg.LEVELS@config.properties:caps.levels"),
    ("caps.ranks", "Collection rank cap rise", "rewards", "int", "1", "0", "10", "", "", "live",
     "Collection rank cap rise per rebirth (for SkyyCollections, later round).", "field:RbCfg.RANKS@config.properties:caps.ranks"),
    ("dust.first", "Dust multiplier from rebirth 1", "rewards", "dec", "2", "1", "10", "", "x", "live",
     "All Dust is multiplied by this from the first rebirth on (Skyy: 2x).", "field:RbCfg.DUST_FIRST@config.properties:dust.first"),
    ("dust.perNode", "Dust per Dust node level", "rewards", "dec", "0.25", "0", "5", "", "", "live",
     "Each level of an arm's Dust node adds this to that arm's Dust multiplier.", "field:RbCfg.DUST_NODE@config.properties:dust.perNode"),
]
kit = CFG.emit(pool, PKG, MOD="SkyyRebirth", TITLE="Rebirth", VERSION=VERSION, NODE="skyyrebirth.admin", CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyRebirth/config.properties"], NOTE="Rebirth is off by default. 0.1 shows /rebirth only - no rebirth button yet.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= RbCfg methods: logging, the cached bridge, pkey, admin check, the config loader =================
M(cfg, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyRebirth] " + m); else System.out.println("[SkyyRebirth] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyRebirth] " + m); else System.out.println("[SkyyRebirth] WARNING " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnOnce(String key, String m) {
  if (key != null && WARNED.putIfAbsent(key, Boolean.TRUE) == null) warn(m);
}""")
M(cfg, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
# research/Code-Structure-Audit.md 1: the map is resolved once and kept (no System.class lock on later calls)
M(cfg, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")
# tools/PROFILES-CONTRACT.md helper, verbatim
M(cfg, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(cfg, r"""
public static boolean isAdmin(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.function.Function f = PERM_TEST;
    if (f != null) return Boolean.TRUE.equals(f.apply(u));
    return @PM@.get().hasPermission(u, "skyyrebirth.admin");
  } catch (Throwable t) { return false; }
}""")
# the hub = the server's default world (SkyyIslands' /hub returns there)
M(cfg, r"""
public static String hubName() {
  String h = HUB_TEST;
  if (h != null) return h;
  try { @WLD@ w = @UNI@.get().getDefaultWorld(); return w == null ? null : w.getName(); } catch (Throwable t) { return null; }
}""")
M(cfg, r"""
public static java.util.ArrayList online() {
  if (TEST_ONLINE != null) return new java.util.ArrayList(TEST_ONLINE);
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null) out.add(p.getUuid());
    }
  } catch (Throwable t) { }
  return out;
}""")
M(cfg, r"""
public static boolean bool(String v, boolean d) {
  if (v == null) return d;
  String s = v.trim().toLowerCase();
  if (s.equals("true") || s.equals("on") || s.equals("yes") || s.equals("1")) return true;
  if (s.equals("false") || s.equals("off") || s.equals("no") || s.equals("0")) return false;
  return d;
}""")
M(cfg, r"""
public static int intOf(String v, int d, int lo, int hi) {
  int x = d;
  if (v != null) { try { x = Integer.parseInt(v.trim()); } catch (Throwable t) { x = d; } }
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
M(cfg, r"""
public static double decOf(String v, double d, double lo, double hi) {
  double x = d;
  if (v != null) { try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { x = d; } }
  if (Double.isNaN(x)) x = d;
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
M(cfg, r"""
public static String num(double d) {
  long r = Math.round(d * 100.0);
  if (r % 100L == 0L) return String.valueOf(r / 100L);
  if (r % 10L == 0L) return (r / 100L) + "." + ((r % 100L) / 10L);
  return (r / 100L) + "." + ((r % 100L) < 10L ? "0" : "") + (r % 100L);
}""")
M(cfg, r"""
public static boolean writeDefaults() {
  try {
    if (FILE == null || java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return false;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    return true;
  } catch (Throwable t) { warn("could not write the default config.properties: " + t); return false; }
}""")
M(cfg, r"""
public static String loadCfg(boolean first) {
  java.util.Properties p = new java.util.Properties();
  boolean wrote = first && writeDefaults();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) { warn("config.properties could not be read - defaults are used: " + t); }
  ON = bool(p.getProperty("rebirth.on"), false);
  MAX = intOf(p.getProperty("rebirth.max"), 10, 1, 100);
  LEVELS = intOf(p.getProperty("caps.levels"), 10, 0, 100);
  RANKS = intOf(p.getProperty("caps.ranks"), 1, 0, 10);
  DUST_FIRST = decOf(p.getProperty("dust.first"), 2.0, 1.0, 10.0);
  DUST_NODE = decOf(p.getProperty("dust.perNode"), 0.25, 0.0, 5.0);
  return (wrote ? "default config.properties written; " : "") + "rebirth " + (ON ? "ON" : "OFF") + ", max " + MAX + ", caps +" + LEVELS + " levels / +" + RANKS + " rank per rebirth, Dust x" + num(DUST_FIRST) + " from rebirth 1 (+" + num(DUST_NODE) + " per node level)";
}""")
# ================= RbStore: Skyy_SkyyRebirth/players/<pkey>.properties (spec 4.2), read off the world thread, cached per pkey =================
# CACHE pkey -> Properties (never changed after it is put: a save puts a new copy); LOADING = queued reads; BAD = files that could not be
# read (they count as 0 rebirths and are never overwritten); IO = the SkyyRebirth-IO thread (null = read on the caller: tests / not started)
load = mk("RbLoad", None, ("java.lang.Runnable", "java.util.concurrent.ThreadFactory"))
st = mk("RbStore")
for f in ("public static java.nio.file.Path DIR;",
          "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LOADING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile java.util.concurrent.ExecutorService IO = null;", "public static final Object LOCK = new Object();",
          "public static final java.util.Properties EMPTY = new java.util.Properties();",
          "public static final java.util.concurrent.atomic.AtomicLong LOADS = new java.util.concurrent.atomic.AtomicLong();",
          "public static volatile String LAST_THREAD = \"\";"):
    F(st, f)
M(st, r"""
public static boolean validKey(String k) {
  return k != null && k.length() >= 36 && k.length() <= 48 && k.matches("[0-9a-fA-F-]{36}(-p[0-9]{1,4})?");
}""")
# a key from a bridge argument: a UUID (its ACTIVE profile), a valid pkey String, or the first element of an Object[]
M(cfg, r"""
public static String keyOf(Object o) {
  if (o instanceof Object[]) { Object[] a = (Object[]) o; o = a.length > 0 ? a[0] : null; }
  if (o instanceof java.util.UUID) return pkey((java.util.UUID) o);
  if (o instanceof String) { String s = ((String) o).trim(); return @PKG@.RbStore.validKey(s) ? s : null; }
  return null;
}""")

M(st, r"""
public static java.util.Properties readNow(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    java.util.Properties p = new java.util.Properties();
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
    BAD.remove(k);
    return p;
  } catch (Throwable t) {
    BAD.put(k, Boolean.TRUE);
    @PKG@.RbCfg.warnOnce("read:" + k, "could not read players/" + k + ".properties - that profile counts as 0 rebirths and the file is never overwritten: " + t);
    return null;
  }
}""")
M(st, r"""
public static java.util.Properties loadNow(String k) {
  java.util.Properties p = readNow(k);
  if (p == null) p = EMPTY;
  CACHE.put(k, p);
  LOADING.remove(k);
  LOADS.incrementAndGet();
  LAST_THREAD = Thread.currentThread().getName();
  return p;
}""")
F(load, "public String k;")
C(load, "public RbLoad(String k) { this.k = k; }")
M(load, r"""
public void run() {
  try { if (this.k != null) @PKG@.RbStore.loadNow(this.k); } catch (Throwable t) { @PKG@.RbStore.LOADING.remove(this.k); @PKG@.RbCfg.warn("profile read failed: " + t); }
}""")
M(load, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyRebirth-IO");
  t.setDaemon(true);
  return t;
}""")
M(st, r"""
public static java.util.Properties get(String k) {
  if (!validKey(k) || DIR == null) return EMPTY;
  Object o = CACHE.get(k);
  if (o != null) return (java.util.Properties) o;
  java.util.concurrent.ExecutorService e = IO;
  if (e == null) return loadNow(k);
  if (LOADING.putIfAbsent(k, Boolean.TRUE) == null) {
    try { e.execute(new @PKG@.RbLoad(k)); } catch (Throwable t) { LOADING.remove(k); }
  }
  return EMPTY;
}""")
M(st, r"""
public static int num(java.util.Properties p, String key) {
  if (p == null || key == null) return 0;
  String v = p.getProperty(key);
  if (v == null) return 0;
  try {
    int x = Integer.parseInt(v.trim());
    if (x < 0) return 0;
    return x > 1000 ? 1000 : x;
  } catch (Throwable t) { return 0; }
}""")
M(st, "public static int n(String k) { return num(get(k), \"n\"); }")
# true = the profile's file is read (or there is no data folder / a bad key = nothing to read); false = queued on SkyyRebirth-IO (get starts it)
M(st, r"""
public static boolean ready(String k) {
  if (!validKey(k) || DIR == null) return true;
  if (CACHE.containsKey(k)) return true;
  get(k);
  return CACHE.containsKey(k);
}""")
M(st, "public static int node(String k, String id) { return id == null ? 0 : num(get(k), \"node.\" + id.trim()); }")
M(st, "public static int pts(String k, String arm) { return arm == null ? 0 : num(get(k), \"pts.\" + arm); }")
M(st, r"""
public static void moveInto(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {
  try {
    java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (java.nio.file.AtomicMoveNotSupportedException e) {
    java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
}""")
M(st, r"""
public static String writeNow(String k, java.util.Properties p) {
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyRebirth @VERSION@ - one profile (research/cloud/Rebirth-Spec.md 4.2)"); } finally { out.close(); }
    moveInto(tmp, DIR.resolve(k + ".properties"));
    return null;
  } catch (Throwable t) { return "could not write players/" + k + ".properties: " + t; }
}""")
# one writer at a time (the RbStore class monitor; one call inside)
M(st, "public static synchronized String writeLocked(String k, java.util.Properties p) { return writeNow(k, p); }")
# null = written (and cached); else the reason. An unreadable file is never overwritten (its data would be lost).
M(st, r"""
public static String save(String k, java.util.Properties p) {
  if (!validKey(k) || p == null || DIR == null) return "bad profile key or no data folder";
  if (BAD.containsKey(k)) return "players/" + k + ".properties could not be read - not overwritten";
  java.util.Properties c = new java.util.Properties();
  c.putAll(p);
  String r = writeLocked(k, c);
  if (r == null) CACHE.put(k, c);
  return r;
}""")
M(st, r"""
public static void start() {
  IO = java.util.concurrent.Executors.newSingleThreadExecutor(new @PKG@.RbLoad(null));
}""")
M(st, r"""
public static void stop() {
  java.util.concurrent.ExecutorService e = IO;
  IO = null;
  if (e == null) return;
  try { e.shutdown(); } catch (Throwable t) { }
  try { e.awaitTermination(2000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")

# ================= RbMath: the pure numbers (spec 3.1 / 3.4 / 3.5) =================
mth = mk("RbMath")
F(mth, "public static final String[] ARMS = new String[] { %s };" % ", ".join('"%s"' % a[0] for a in ARMS))
F(mth, "public static final String[] ARM_SKILL = new String[] { %s };" % ", ".join('"%s"' % a[1] for a in ARMS))
F(mth, "public static final int[] ARM_B = new int[] { %s };" % ", ".join(str(a[2]) for a in ARMS))
M(mth, r"""
public static boolean rankKind(String kind) {
  if (kind == null) return false;
  String t = kind.trim().toLowerCase();
  return t.equals("rank") || t.equals("collection") || t.startsWith("collection.");
}""")
# the cap for `kind` at n rebirths: Exploration never rises (Q3); a collection rank +caps.ranks, everything else +caps.levels per rebirth
M(mth, r"""
public static int cap(int base, String kind, int n) {
  if (n <= 0 || kind == null || kind.trim().equalsIgnoreCase("Exploration")) return base;
  long per = (long) (rankKind(kind) ? @PKG@.RbCfg.RANKS : @PKG@.RbCfg.LEVELS);
  long v = (long) base + per * (long) n;
  return v > 2000000000L ? 2000000000 : (int) v;
}""")
# the arm a Dust tree belongs to (null = no arm: Acrobatics, Exploration, the class)
M(mth, r"""
public static String dustArm(String tree) {
  if (tree == null) return null;
  String t = tree.trim();
  for (int i = 1; i < ARMS.length; i++) if (ARMS[i].equalsIgnoreCase(t)) return ARMS[i];
  return null;
}""")
M(mth, r"""
public static double dust(int n, int nodeLevel) {
  double m = n >= 1 ? @PKG@.RbCfg.DUST_FIRST : 1.0;
  int lv = nodeLevel < 0 ? 0 : nodeLevel;
  return m * (1.0 + @PKG@.RbCfg.DUST_NODE * (double) lv);
}""")
# spec 3.5 (Skyy Q11 "recommended curve"): r = run XP / XP to the cap; under 0.25 pays 0; floor(B x sqrt(min(r, 16)))
M(mth, r"""
public static int points(long run, long toCap, int b) {
  if (run <= 0L || toCap <= 0L || b <= 0) return 0;
  double r = (double) run / (double) toCap;
  if (r < 0.25) return 0;
  if (r > 16.0) r = 16.0;
  return (int) Math.floor((double) b * Math.sqrt(r));
}""")
M(mth, r"""
public static String roman(int n) {
  String[] r = new String[] { "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X" };
  return n >= 1 && n <= 10 ? r[n - 1] : String.valueOf(n);
}""")

# ================= RbFn: the bridge functions (mode 0 count, 1 cap, 2 node, 3 dustmult, 4 busy, 5 decision). Any thread, never throws =================
fnc = mk("RbFn", None, ("java.util.function.Function",))
F(fnc, "public int mode;")
F(st, "public static final java.util.concurrent.ConcurrentHashMap BUSY = new java.util.concurrent.ConcurrentHashMap();")
C(fnc, "public RbFn(int m) { this.mode = m; }")
M(fnc, r"""
public Object apply(Object o) {
  try {
    if (this.mode == 5) return "unknown";
    String k = @PKG@.RbCfg.keyOf(o);
    if (k == null) return null;
    if (this.mode == 4) return Boolean.valueOf(@PKG@.RbStore.BUSY.containsKey(k));
    if (!@PKG@.RbStore.ready(k)) return null;   // still reading the file - no answer (SkyySkills retries; never a cached 'no raise'; fix 2: never a false 0 count)
    if (this.mode == 0) return Integer.valueOf(@PKG@.RbStore.n(k));
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[1] instanceof String)) return null;
    String s = (String) a[1];
    if (this.mode == 1) {
      if (a.length < 3 || !(a[2] instanceof Number)) return null;
      int nn = @PKG@.RbStore.n(k);
      int mx = @PKG@.RbCfg.MAX;
      if (nn > mx) nn = mx;   // fix 2: a hand-edited n past rebirth.max never raises a cap past max x the rise
      return Integer.valueOf(@PKG@.RbMath.cap(((Number) a[2]).intValue(), s, nn));
    }
    if (this.mode == 2) return Integer.valueOf(@PKG@.RbStore.node(k, s));
    if (this.mode == 3) {
      String arm = @PKG@.RbMath.dustArm(s);
      int lv = arm == null ? 0 : @PKG@.RbStore.node(k, arm + ".dust");
      return Double.valueOf(@PKG@.RbMath.dust(@PKG@.RbStore.n(k), lv));
    }
    return null;
  } catch (Throwable t) { return null; }
}""")

# ================= RbPub: rebirth:n:<uuid> for online players (every 5 s: a profile switch is picked up; a leaver's key removed) =================
pub = mk("RbPub")
F(pub, "public static final java.util.concurrent.ConcurrentHashMap PUB = new java.util.concurrent.ConcurrentHashMap();")
F(pub, "public static final java.util.concurrent.ConcurrentHashMap PKEY = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> the pkey whose n is published
M(pub, r"""
public static void publish(java.util.UUID u) {
  if (u == null) return;
  String k = @PKG@.RbCfg.pkey(u);
  java.util.Map b = @PKG@.RbCfg.bridge();
  String key = "rebirth:n:" + u.toString();
  if (@PKG@.RbStore.ready(k)) {
    Integer n = Integer.valueOf(@PKG@.RbStore.n(k));
    if (!n.equals(b.get(key))) b.put(key, n);
    PKEY.put(u, k);
  } else if (!k.equals(PKEY.get(u))) {
    b.remove(key);   // fix 2: a newly active profile's file is still being read - no value (never a false 0 / the previous profile's count)
    PKEY.remove(u);
  }
  Boolean busy = Boolean.valueOf(@PKG@.RbStore.BUSY.containsKey(k));
  String bk = "rebirth:busy:" + u.toString();
  if (!busy.equals(b.get(bk))) b.put(bk, busy);
  PUB.put(u, Boolean.TRUE);
}""")
M(pub, r"""
public static void clearAll() {
  java.util.Iterator it = PUB.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    PKEY.remove(u);
    try { @PKG@.RbCfg.bridge().remove("rebirth:n:" + u.toString()); @PKG@.RbCfg.bridge().remove("rebirth:busy:" + u.toString()); } catch (Throwable t) { }
  }
}""")
M(pub, r"""
public static int tick() {
  java.util.ArrayList on = @PKG@.RbCfg.online();
  java.util.HashSet set = new java.util.HashSet();
  for (int i = 0; i < on.size(); i++) {
    java.util.UUID u = (java.util.UUID) on.get(i);
    set.add(u);
    try { publish(u); } catch (Throwable t) { }
  }
  java.util.Iterator it = PUB.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    if (set.contains(u)) continue;
    it.remove();
    PKEY.remove(u);
    @PKG@.RbCfg.bridge().remove("rebirth:n:" + u.toString());
    @PKG@.RbCfg.bridge().remove("rebirth:busy:" + u.toString());
  }
  return set.size();
}""")
tick = mk("RbTick", None, ("java.lang.Runnable",))
C(tick, "public RbTick() { }")
M(tick, r"""
public void run() {
  try { @PKG@.RbPub.tick(); } catch (Throwable t) { @PKG@.RbCfg.warnOnce("tick", "the rebirth:n publish tick failed (logged once): " + t); }
}""")

# ================= RbCheck: the requirement checklist + what a rebirth would give (spec 2.1 / 3.1 / 3.5), from other mods' bridge keys =================
chk = mk("RbCheck")
M(chk, r"""
public static Object[] run(java.util.UUID u, String skill) {
  try {
    Object f = @PKG@.RbCfg.bridge().get("skill:fn:run");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, skill });
    if (!(r instanceof Object[]) || ((Object[]) r).length < 4) return null;
    return (Object[]) r;
  } catch (Throwable t) { return null; }
}""")
# ms left in combat (SkyySkills skill:fn:combat), -1 = unknown (no SkyySkills)
M(chk, r"""
public static long combatMs(java.util.UUID u) {
  try {
    Object f = @PKG@.RbCfg.bridge().get("skill:fn:combat");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof Number ? ((Number) r).longValue() : -1L;
  } catch (Throwable t) { return -1L; }
}""")
# 1 = your own island (owner / admin / member - SkyyIslands island:role:fn), 2 = the hub (the default world), 0 = elsewhere, -1 = unknown
M(chk, r"""
public static int place(java.util.UUID u, String world) {
  if (world == null) return -1;
  try {
    Object f = @PKG@.RbCfg.bridge().get("island:role:fn");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, world });
      if ("owner".equals(r) || "admin".equals(r) || "member".equals(r)) return 1;
    }
  } catch (Throwable t) { }
  String h = @PKG@.RbCfg.hubName();
  return h != null && h.equals(world) ? 2 : 0;
}""")
# Object[]{ String[6] texts, String[6] colours, Boolean all met } - every text ONE line of the 236 px left panel (fix round: the build
# measures the longest form of each with the kit's text_lines, the harness the real ones at the widest numbers)
M(chk, r"""
public static Object[] reqs(java.util.UUID u, String world, int n) {
  String[] t = new String[6];
  String[] c = new String[6];
  boolean all = true;
  if (@PKG@.RbCfg.ON) { t[0] = "OK  Rebirth is switched on"; c[0] = "@GOOD@"; }
  else { t[0] = "NO  Rebirth is switched off"; c[0] = "@BAD@"; all = false; }
  Object[] r = run(u, "class");
  if (r != null && r[0] instanceof Number && r[1] instanceof Number) {
    int lv = ((Number) r[0]).intValue();
    int cap = ((Number) r[1]).intValue();
    boolean ok = lv >= cap;
    t[1] = (ok ? "OK" : "NO") + "  Class level " + lv + " / " + cap;
    c[1] = ok ? "@GOOD@" : "@BAD@";
    if (!ok) all = false;
  } else {
    t[1] = "NO  " + (@PKG@.RbCfg.bridge().get("skill:fn:run") instanceof java.util.function.Function ? "Choose a class first" : "Needs SkyySkills 0.4.35+");
    c[1] = "@BAD@";
    all = false;
  }
  int max = @PKG@.RbCfg.MAX;
  boolean left = n < max;
  t[2] = (left ? "OK" : "NO") + "  Rebirths done " + n + " / " + max;
  c[2] = left ? "@GOOD@" : "@BAD@";
  if (!left) all = false;
  long ms = combatMs(u);
  if (ms > 0L) { t[3] = "NO  In combat - wait " + ((ms + 999L) / 1000L) + " s"; c[3] = "@BAD@"; all = false; }
  else { t[3] = "OK  Not in combat"; c[3] = "@GOOD@"; }
  int p = place(u, world);
  if (p == 1) { t[4] = "OK  On your island"; c[4] = "@GOOD@"; }
  else if (p == 2) { t[4] = "OK  At the hub"; c[4] = "@GOOD@"; }
  else { t[4] = "NO  Go to your island or hub"; c[4] = "@BAD@"; all = false; }
  t[5] = "--  Bazaar / AH: later update";
  c[5] = "@INFO@";
  return new Object[] { t, c, Boolean.valueOf(all) };
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@INFO@", INFO))
# Object[]{ String[8] arm lines, String[8] colours, String the short extra line (left panel), Integer total points, String the full extra
# line (the Nexus tooltip), Boolean at the max }. At the max (n >= rebirth.max) nothing more can be gained: every arm "-  max reached".
M(chk, r"""
public static Object[] gains(java.util.UUID u, int n) {
  String[] t = new String[@PKG@.RbMath.ARMS.length];
  String[] c = new String[t.length];
  int total = 0;
  boolean maxed = n >= @PKG@.RbCfg.MAX;
  for (int i = 0; i < t.length; i++) {
    Object[] r = null;
    if (!maxed) r = run(u, @PKG@.RbMath.ARM_SKILL[i]);
    String nm = @PKG@.RbMath.ARMS[i];
    if (maxed) {
      t[i] = nm + "  -  max reached";
      c[i] = "@MUTED@";
    } else if (r != null && r[2] instanceof Number && r[3] instanceof Number) {
      int p = @PKG@.RbMath.points(((Number) r[2]).longValue(), ((Number) r[3]).longValue(), @PKG@.RbMath.ARM_B[i]);
      total += p;
      t[i] = nm + "  +" + (p == 0 ? "0 (under 25 %)" : String.valueOf(p) + (p == 1 ? " point" : " points"));
      c[i] = p > 0 ? "@GOLD@" : "@MUTED@";
    } else {
      t[i] = nm + "  -  " + (i == 0 ? "choose a class" : (nm.equals("Fishing") ? "no skill yet" : "no skill data"));
      c[i] = "@MUTED@";
    }
  }
  if (maxed) return new Object[] { t, c, "Max rebirths reached", Integer.valueOf(0), "Max rebirths reached - nothing more to gain", Boolean.TRUE };
  String dust = n == 0 ? ", Dust x" + @PKG@.RbCfg.num(@PKG@.RbCfg.DUST_FIRST) : "";
  String x = "Caps +" + @PKG@.RbCfg.LEVELS + " levels, Void-Touched " + @PKG@.RbMath.roman(n + 1) + dust;
  String xl = "Caps +" + @PKG@.RbCfg.LEVELS + " levels (Exploration stays), collections +" + @PKG@.RbCfg.RANKS + " rank, title Void-Touched " + @PKG@.RbMath.roman(n + 1) + (n == 0 ? ", all Dust x" + @PKG@.RbCfg.num(@PKG@.RbCfg.DUST_FIRST) : "");
  return new Object[] { t, c, x, Integer.valueOf(total), xl, Boolean.FALSE };
}""".replace("@GOLD@", GOLD).replace("@MUTED@", MUTED))
# the Nexus hover text (plain text, one fact per line - the vanilla TextTooltip is one wrapped label)
M(chk, r"""
public static String tip(int n, Object[] req, Object[] gain) {
  StringBuilder sb = new StringBuilder();
  boolean maxed = n >= @PKG@.RbCfg.MAX;
  sb.append("NEXUS OF THE VOID\n");
  if (maxed) sb.append("Max rebirths reached (").append(n).append(" of ").append(@PKG@.RbCfg.MAX).append(") - the void has nothing more to give\n\nREQUIREMENTS\n");
  else sb.append("Rebirth ").append(n + 1).append(" of ").append(@PKG@.RbCfg.MAX).append(" - the void imprints your soul\n\nREQUIREMENTS\n");
  String[] t = (String[]) req[0];
  for (int i = 0; i < t.length; i++) sb.append(t[i]).append('\n');
  sb.append("Open Bazaar / AH orders are checked by the Continue button (a later update)\n");
  if (!maxed) {
    sb.append("\nWHAT YOU WOULD GET\n");
    String[] g = (String[]) gain[0];
    for (int i = 0; i < g.length; i++) sb.append(g[i]).append('\n');
    Object xl = gain.length > 4 ? gain[4] : gain[2];
    sb.append(String.valueOf(xl)).append('\n');
  }
  sb.append('\n');
  if (maxed) sb.append("This profile has done every rebirth this server allows.");
  else sb.append(Boolean.TRUE.equals(req[2]) ? "Every requirement is met - the rebirth button comes in a later update." : "Not ready yet - the NO lines above are what is missing.");
  return sb.toString();
}""")

# ================= RbUI: the page markup (tools/skyyui.py - vanilla look; inline only; ids SkyyRb..., no underscores) =================
P = "SkyyRb"
PW, PH = 1120, 952
sh = SUI.page_shell(P, PW, PH, title="Rebirth - Nexus of the Void", kind="decorated", layout="Left")
ap = sh.appends
LW, GAP = 260, 16
CW, CH = sh.inner_w - LW - GAP, sh.inner_h
assert (CW, CH) == (810, 880), (CW, CH)
ap.append((sh.body, SUI.panel(P + "Left", "simple", w=LW, h=CH, layout="Top")))
ap.append((sh.body, SUI.spacer(w=GAP)))
ap.append((sh.body, SUI.panel(P + "Canvas", "well", w=CW, h=CH, layout=None, pad=0)))
L, CV = "#" + P + "Left", "#" + P + "Canvas"
J_ = SUI.J
used = []
used.append(ap.add(L, SUI.label(P + "Head", "Your rebirth", "panelTitle", h=30)))
# FIX ROUND (critic: wrapped texts overflowed their fixed rows): every dynamic row holds the LONGEST text its Java can make at the widest
# numbers (rebirth.max 100, caps.levels 100, a class level 1000 / 1000, combat 9999 s) in its rows x the kit's line height, measured
# with skyyui.text_lines at the panel's inner width (260 - 2 x 12 padding) less 8 px of slack. The harness measures the real texts too.
LIN_W = LW - 24 - 8
FIT = {   # row id -> (size, bold, lines, the longest texts)
    "State": (14, True, 1, ["Nexus asleep", "Nexus awake"]),
    "Count": (14, False, 1, ["Rebirths 100 / 100"]),
    "Off": (13, False, 1, ["Rebirth is OFF (admin view)"]),
    "Req": (13, False, 1, ["OK  Rebirth is switched on", "NO  Rebirth is switched off", "NO  Class level 1000 / 1000",
                           "NO  Choose a class first", "NO  Needs SkyySkills 0.4.35+", "NO  Rebirths done 100 / 100",
                           "NO  In combat - wait 9999 s", "OK  Not in combat", "OK  On your island", "OK  At the hub",
                           "NO  Go to your island or hub", "--  Bazaar / AH: later update"]),
    "Arm": (13, False, 1, [a[0] + t_ for a in ARMS for t_ in ("  +0 (under 25 %)", "  +48 points", "  +1 point", "  -  choose a class",
                                                               "  -  no skill yet", "  -  no skill data", "  -  max reached")]),
    "Extra": (13, False, 2, ["Caps +100 levels, Void-Touched 100, Dust x10", "Caps +100 levels, Void-Touched VIII", "Max rebirths reached"]),
    "Note": (12, False, 1, ["Hover the Nexus for the full list."]),
}
ROW_H = {}
for _r, (_sz, _bd, _ln, _txts) in FIT.items():
    _lh = SUI.line_height(SUI.fs(_sz), bold=_bd)
    ROW_H[_r] = int(math.ceil(_lh * _ln))
    for _t in _txts:
        _n = SUI.text_lines(_t, LIN_W, SUI.fs(_sz), bold=_bd)
        assert _n <= _ln, "left panel row %s: %r takes %d lines (%d px) in %d px" % (_r, _t, _n, int(SUI.text_width(_t, SUI.fs(_sz), bold=_bd)), LIN_W)
ap.text(L, P + "State", J_("this.state", "Nexus asleep"), "default", size=14, bold=True, h=ROW_H["State"], col=J_("this.stateCol", WARN))
ap.text(L, P + "Count", J_("this.count", "Rebirths 0 / 10"), "default", size=14, h=ROW_H["Count"])
ap.text(L, P + "Off", J_("this.off", "Rebirth is OFF (admin view)"), "default", size=13, h=ROW_H["Off"], col=BAD)
ap.text(L, None, "Requirements", "section", anchor={"top": 6, "bottom": 2})
for _i in range(6):
    ap.text(L, P + "Req%d" % _i, J_("this.rt[%d]" % _i, "OK  Not in combat"), "default", size=13, h=ROW_H["Req"],
            col=J_("this.rc[%d]" % _i, GOOD))
ap.text(L, None, "What you would get", "section", anchor={"top": 6, "bottom": 2})
for _i in range(len(ARMS)):
    ap.text(L, P + "Arm%d" % _i, J_("this.at[%d]" % _i, "Mining  +8 points"), "default", size=13, h=ROW_H["Arm"], col=J_("this.ac[%d]" % _i, GOLD))
ap.text(L, P + "Extra", J_("this.extra", "Caps +10 levels, Void-Touched I, Dust x2"), "default", size=13, wrap=True, h=ROW_H["Extra"], col=INFO)
ap.text(L, P + "Note", "Hover the Nexus for the full list.", "caption", h=ROW_H["Note"])
ap.append((L, SUI.button(P + "Close", "Close", "secondary", w=LW - 24, sound="cancel", anchor={"top": 8})))
_left_h = SUI.used_height(ap, L)
assert _left_h <= CH - 24, "left panel %d px > %d" % (_left_h, CH - 24)

# ---- the radiating tree (THE PROBE): every node a locked disc at its final place
CX, CY = CW // 2, CH // 2
RADII = [169, 221, 274, 325, 371]
ROWN = [3, 3, 2, 2, 1]
SIDE = {3: (-48, 0, 48), 2: (-30, 30), 1: (0,)}
NODE, KEY, CHIP_W, CHIP_H, NEX = 28, 34, 80, 22, 120
CHIP_R = (107, 124)   # arm name chips: the cardinal arms closer in, the diagonal ones further out (no chip touches another)
boxes, nodes = [], []
for _a, (_nm, _sk, _b, _col) in enumerate(ARMS):
    _ang = math.radians(45 * _a)
    _ux, _uy = math.sin(_ang), -math.cos(_ang)
    _px, _py = math.cos(_ang), math.sin(_ang)
    for _r, (_rad, _n) in enumerate(zip(RADII, ROWN)):
        for _off in SIDE[_n]:
            _s = KEY if _r == 4 else NODE
            _x = CX + _ux * _rad + _px * _off
            _y = CY + _uy * _rad + _py * _off
            _l, _t = int(round(_x - _s / 2.0)), int(round(_y - _s / 2.0))
            nodes.append((_a, _r, _l, _t, _s))
            boxes.append(("node %s r%d" % (_nm, _r + 1), _l, _t, _s, _s))
    _cx, _cy = CX + _ux * CHIP_R[_a % 2], CY + _uy * CHIP_R[_a % 2]
    boxes.append(("chip " + _nm, int(round(_cx - CHIP_W / 2.0)), int(round(_cy - CHIP_H / 2.0)), CHIP_W, CHIP_H))
boxes.append(("nexus", CX - NEX // 2, CY - NEX // 2, NEX, NEX))
assert len(nodes) == 88, len(nodes)
for _nm, _l, _t, _w, _h in boxes:
    assert _l >= 4 and _t >= 4 and _l + _w <= CW - 4 and _t + _h <= CH - 4, "%s outside the canvas: %s" % (_nm, (_l, _t, _w, _h))
_min_gap = 10 ** 9
for _i in range(len(boxes)):
    for _j in range(_i + 1, len(boxes)):
        _a1, _b1 = boxes[_i], boxes[_j]
        _gx = max(_b1[1] - (_a1[1] + _a1[3]), _a1[1] - (_b1[1] + _b1[3]))
        _gy = max(_b1[2] - (_a1[2] + _a1[4]), _a1[2] - (_b1[2] + _b1[4]))
        _g = max(_gx, _gy)
        assert _g >= 6, "%s and %s are %d px apart (< 6)" % (_a1[0], _b1[0], _g)
        _min_gap = min(_min_gap, _g)
for _k, (_a, _r, _l, _t, _s) in enumerate(nodes):
    ap.append((CV, SUI.group(P + "N%d" % _k, layout=None, w=_s, h=_s, anchor={"left": _l, "top": _t}, bg=NODE_LOCKED)))
for _a, (_nm, _sk, _b, _col) in enumerate(ARMS):
    _ang = math.radians(45 * _a)
    _cx, _cy = CX + math.sin(_ang) * CHIP_R[_a % 2], CY - math.cos(_ang) * CHIP_R[_a % 2]
    ap.append((CV, SUI.label(P + "Chip%d" % _a, _nm.upper(), "section", size=12, w=CHIP_W, h=CHIP_H, align="Center", col=_col,
                             anchor={"left": int(round(_cx - CHIP_W / 2.0)), "top": int(round(_cy - CHIP_H / 2.0))},
                             extra="Background: %s;" % CHIP_BG)))
ap.append((CV, SUI.group(P + "Nexus", layout="Top", w=NEX, h=NEX, anchor={"left": CX - NEX // 2, "top": CY - NEX // 2},
                         bg=J_('this.awake ? "%s" : "%s"' % (NEXUS_AWAKE, NEXUS_SLEEP), NEXUS_SLEEP),
                         extra=SUI.tooltip("Nexus of the Void", trial=True))))
NX = "#" + P + "Nexus"
ap.append((NX, SUI.label(P + "NexusName", "NEXUS", "strong", w=NEX, h=24, align="Center", anchor={"top": 30})))
ap.append((NX, SUI.label(P + "NexusSub", "OF THE VOID", "caption", w=NEX, h=18, align="Center")))
ap.text(NX, P + "NexusSt", J_("this.nexusSt", "asleep"), "default", size=13, bold=True, w=NEX, h=20, align="Center", col=J_("this.stateCol", WARN))
ap.text(CV, P + "Foot", "Rebirth tree - 8 arms. Nodes open in a later update.", "caption", w=CW, h=22, align="Center",
        anchor={"left": 0, "top": CH - 30})
sh.appends.check(P)
SUI.assert_proven(sh.appends.markups(), allow=("tooltip",), what="SkyyRebirth /rebirth page")
PAGE_JAVA = sh.java("b")
_markup_bytes = sum(len(SUI.render(mk_)) for _p, mk_ in ap)
print("THE PROBE (radiating tree on one page): %d elements appended (%d tree nodes, 8 chips, the Nexus), inline markup %d bytes, "
      "%d b.set lines; canvas %d x %d, node %d px / keystone %d px, closest gap between two drawn things %d px; left panel %d / %d px"
      % (len(ap), len(nodes), _markup_bytes, len(sh.all_sets()), CW, CH, NODE, KEY, _min_gap, _left_h, CH - 24))

# ================= RbPage: /rebirth (view only in 0.1; no rebirth button) =================
page = mk("RbPage", T["PAGE"])
for f in ("public java.util.UUID me;", "public boolean testMode;", "public String world;", "public String[] rt;", "public String[] rc;",
          "public String[] at;", "public String[] ac;", "public String extra;", "public String state;", "public String stateCol;",
          "public String count;", "public String off;", "public String tip;", "public String nexusSt;", "public boolean awake;",
          "public int n;"):
    F(page, f)
C(page, r"""
public RbPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.me = pr == null ? null : pr.getUuid();
  this.testMode = false;
}""")
# harness only (no PlayerRef in a bare JVM): the same page for a UUID in a named world; never sends anything
C(page, r"""
public RbPage(java.util.UUID u, String world) {
  super((@PR@) null, @LIFE@.CanDismiss);
  this.me = u;
  this.world = world;
  this.testMode = true;
}""")
M(page, r"""
public static String worldOf(@ST@ st) {
  try {
    Object ext = st == null ? null : st.getExternalData();
    if (ext instanceof @EST@) { @WLD@ w = ((@EST@) ext).getWorld(); if (w != null) return w.getName(); }
  } catch (Throwable t) { }
  return null;
}""")
M(page, r"""
public void fill(@ST@ st) {
  java.util.UUID u = this.me;
  String w = this.testMode ? this.world : worldOf(st);
  this.n = @PKG@.RbStore.n(@PKG@.RbCfg.pkey(u));
  Object[] req = @PKG@.RbCheck.reqs(u, w, this.n);
  Object[] gain = @PKG@.RbCheck.gains(u, this.n);
  this.rt = (String[]) req[0];
  this.rc = (String[]) req[1];
  this.at = (String[]) gain[0];
  this.ac = (String[]) gain[1];
  this.extra = (String) gain[2];
  this.awake = Boolean.TRUE.equals(req[2]);
  this.state = this.awake ? "Nexus awake" : "Nexus asleep";
  this.stateCol = this.awake ? "@GOOD@" : "@WARN@";
  this.nexusSt = this.awake ? "awake" : "asleep";
  this.count = "Rebirths " + this.n + " / " + @PKG@.RbCfg.MAX;
  this.off = @PKG@.RbCfg.ON ? "" : "Rebirth is OFF (admin view)";
  this.tip = @PKG@.RbCheck.tip(this.n, req, gain);
}""".replace("@GOOD@", GOOD).replace("@WARN@", WARN))
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  fill(st);
@PAGE_JAVA@
  b.set("#SkyyRbNexus.TooltipText", this.tip);
  ev.addEventBinding(@BT@.Activating, "#SkyyRbClose", @EVD@.of("a", "close"));
}""".replace("@PAGE_JAVA@", PAGE_JAVA))
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  if (data == null || this.testMode) return;
  if (data.indexOf("close") >= 0) close();
}""")

# ================= /rebirth (every player while rebirth is ON; admins only while it is OFF - view only) =================
cmd = mk("RbCmd", T["APC"])
C(cmd, r"""
public RbCmd() {
  super("rebirth", "The Nexus of the Void - your rebirth requirements and what a rebirth would give");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(cmd, r"""
public static String gate(java.util.UUID u) {
  if (@PKG@.RbCfg.ON) return null;
  if (@PKG@.RbCfg.isAdmin(u)) return null;
  return "[Rebirth] Rebirth is not switched on on this server yet.";
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String no = gate(pr.getUuid());
    if (no != null) { pr.sendMessage(@MSG@.raw(no).color("#ffcc00")); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    p.getPageManager().openCustomPage(ref, store, new @PKG@.RbPage(pr));
  } catch (Throwable t) {
    @PKG@.RbCfg.warn("/rebirth failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[Rebirth] Something went wrong - the server log has the details.").color("#ff6b6b")); } catch (Throwable t2) { }
  }
}""")

# ================= plugin =================
pl = mk("SkyyRebirthPlugin", T["JP"])
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyRebirthPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.RbCfg.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyRebirth");
  @PKG@.RbCfg.DIR = dir;
  @PKG@.RbCfg.FILE = dir.resolve("config.properties");
  String c = @PKG@.RbCfg.loadCfg(true);
  @PKG@.RbStore.DIR = dir.resolve("players");
  @PKG@.RbStore.start();
  java.util.Map b = @PKG@.RbCfg.bridge();
  b.put("rebirth:fn:count", new @PKG@.RbFn(0));
  b.put("rebirth:fn:cap", new @PKG@.RbFn(1));
  b.put("rebirth:fn:node", new @PKG@.RbFn(2));
  b.put("rebirth:fn:dustmult", new @PKG@.RbFn(3));
  b.put("rebirth:fn:busy", new @PKG@.RbFn(4));
  b.put("rebirth:fn:decision", new @PKG@.RbFn(5));
  b.put("rebirth:version", "@VERSION@");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  getCommandRegistry().registerCommand(new @PKG@.RbCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.RbTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRebirth] @VERSION@ ready (@KITID@) - rebirth is " + (@PKG@.RbCfg.ON ? "ON: /rebirth for every player" : "OFF: /rebirth for admins only (view; Server Setup - Rebirth switches it on)") + "; NO rebirth button yet (round R3), nothing is ever reset; bridge rebirth:n:<uuid> + rebirth:busy:<uuid> + rebirth:fn:count / cap / node / dustmult / busy / decision (caps +" + @PKG@.RbCfg.LEVELS + " levels per rebirth, Exploration never; SkyySkills 0.4.35+ reads them); " + c + "; data in " + dir);
}""".replace("@KITID@", KIT_ID))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.RbStore.stop(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.RbPub.clearAll(); } catch (Throwable t) { }
  java.util.Map b = @PKG@.RbCfg.bridge();
  try { b.remove("rebirth:fn:count"); b.remove("rebirth:fn:cap"); b.remove("rebirth:fn:node"); b.remove("rebirth:fn:dustmult"); b.remove("rebirth:fn:busy"); b.remove("rebirth:fn:decision"); b.remove("rebirth:version"); } catch (Throwable t) { }
  super.shutdown();
}""")

ALL = [cfg, load, st, mth, fnc, pub, tick, chk, page, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written:", len(ALL) + len(kit.classes), "(%d kit)" % len(kit.classes))

jar = os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)
man = B.manifest("SkyyRebirth", VERSION, "SkyWynn Rebirth (New Game+), first part - OFF by default. The rebirth counter and per-profile rebirth files, the cross-mod keys other Skyy mods read (rebirth count, raised level caps: +10 class / skill levels per rebirth, Exploration never; collection rank caps; the Dust multiplier) and /rebirth: the Nexus of the Void in the middle of the 8-arm rebirth tree, with the requirement checklist (class at max level, rebirths left, not in combat, on your island or at the hub) and the points each arm would get. View only: no rebirth button yet, nothing is ever reset. Server Setup: Rebirth (admins can view /rebirth while it is off). Zero dependencies; reads SkyySkills 0.4.35+ for levels.", PKG + ".SkyyRebirthPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyRebirth jar must not ship .ui files (inline pages only): %s" % _bad)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyRebirth: --deploy is not supported here - deploys go through tools/deploy_set.py")
