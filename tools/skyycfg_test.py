"""Bare-JVM test harness for tools/skyycfg.py (research/Server-Setup-Spec.md 8.2 a-j, plus 8.1.3 and 8.1.4).

    python tools/skyycfg_test.py [--dir <scratch folder>] [--keep]

Phase 1 (this process): javassist builds two sample mods on the kit - SkyyCfgTest (every row type and binding, test hooks for the
permission and item checks) and SkyyCfgPlain (the real PermissionsModule / Item paths, no reload routine) - and runs the schema checks
that must FAIL (unit rule, 01 rule, bad defaults, missing hooks, part without danger, confirm= misuse, overlapping file keys, custom:
without a file) and two that must BUILD (plural MS names, camelCase ms fields). Phase 2 (a child process: a fresh JVM with -Xverify:all and
HytaleServer.jar on the classpath) loads every class and drives every op against real files in the scratch folder.
Default scratch folder: tools/dev/scratch/skyycfg-test (git-ignored), deleted at the end unless --keep. Exit code 1 on any failure.
In a bare JVM HytaleServer cannot initialise, so the kit's saves run on its fallback daemon threads; CfgPub.flush() is used to make
the tests deterministic. The in-game scheduler path (HytaleServer.SCHEDULED_EXECUTOR) is the same code with a different executor.
"""
import os, sys, re, shutil, subprocess, time, zlib, base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(HERE, "dev", "scratch", "skyycfg-test")))
KEEP = "--keep" in sys.argv

CONFIG_TEXT = """# SkyyCfgTest config - edit, then /cfgtest reload (or change it in game: SkyWynn Menu -> Server Setup)
# interestPercent = percent paid each payout (0-100)
interestPercent=2

# inviteSeconds = how long an invite stays open
inviteSeconds=60
spread=0.10
greeting=Hello
part.shop=true
defaults.visit.notify=1
starter.kit=Food_Bread:5
openMode=page
maxPages=10
paused=false
chat.priority=30000
penaltyMin=10
penaltyMax=25
build=x
# the end
"""
XP_TEXT = """# XP config
multiplier=1.0
feedbackMs=1500
block.Ore_Iron=Mining:5
block.Ore_Copper=Mining:3
# chest.xp.Chest_Small=500
# chests.enabled=false stops XP from chests (a doc comment, not a template)
"""
ITEMS = ["Food_Bread", "Ore_Iron", "Ore_Copper", "Ore_Gold", "Wood_Oak_Trunk"]
CATS = [("parts", "Parts"), ("main", "Main"), ("items", "Items"), ("coins", "Coins"), ("xp", "XP"), ("tools", "Tools")]
ROWS = [
    ("part.shop", "Shop", "parts", "bool", "true", "", "", "", "", "live,part,danger", "Off: the shop is closed. Nothing is deleted.",
     "field:TestCfg.FLAG@config.properties:part.shop"),
    ("bank.interestPercent", "Interest per payout", "main", "int", "2", "0", "100", "step=1", "%", "live,danger",
     "Percent of the bank balance paid each payout.", "field:TestCfg.PERCENT@config.properties:interestPercent"),
    ("party.inviteSeconds", "Invite time", "main", "int", "60", "15", "600", "step=5", "s", "live", "How long a party invite stays open.",
     "field:TestCfg.INVITE_MS*1000@config.properties:inviteSeconds"),
    ("bazaar.spread", "Spread", "main", "dec", "0.10", "0", "0.9", "", "", "live,danger", "Gap between buy and sell prices.",
     "field:TestCfg.SPREAD@config.properties:spread"),
    ("msg.greeting", "Greeting", "main", "text", "Hello", "1", "40", "", "", "live", "Shown on join.",
     "field:TestCfg.GREETING@config.properties:greeting;check=TestCust.check"),
    ("visit.notify", "Visit notify", "main", "bool", "true", "", "", "01", "", "new", "Tell island owners about visitors.",
     "field:TestCfg.NOTIFY@config.properties:defaults.visit.notify"),
    ("kit.items", "Starter kit", "items", "items", "Food_Bread:5", "0", "9", "qty", "", "new", "Items in the starter chest.",
     "field:TestCfg.KIT@config.properties:starter.kit"),
    ("vault.openMode", "Open mode", "main", "choice", "page", "", "", "page|Page view,chest|Chest window", "", "live", "How /vault opens.",
     "field:TestCfg.MODE@config.properties:openMode"),
    ("coins.payMax", "Largest pay", "coins", "int", "0", "0", "1000000000000000", "", "coins", "live", "0 = no cap.",
     "field:TestCfg.BIG@config.properties:payMax"),
    ("vault.maxPages", "Max pages", "main", "int", "10", "1", "1000", "", "", "live,danger", "Refused below the highest page in use.",
     "field:TestCfg.MAXPAGES@config.properties:maxPages;check=TestCust.check;after=TestCust2.afterSet"),
    ("ah.paused", "Auction House paused", "main", "bool", "false", "", "", "", "", "live,danger", "Stops listing and buying.",
     "field:TestCfg.PAUSED@config.properties:paused;confirm=on"),
    ("chat.priority", "Chat priority", "main", "int", "30000", "0", "100000", "", "", "restart,adv", "Chat formatter order.",
     "field:TestCfg.PRIO@config.properties:chat.priority"),
    ("coins.penalty", "Death penalty", "coins", "range", "10-25", "0", "100", "", "%", "live,danger", "Share of the purse lost on death.",
     "custom:TestCust@config.properties:penaltyMin,penaltyMax"),
    ("xp.multiplier", "XP multiplier", "xp", "dec", "1.0", "0", "100", "", "x", "live,danger", "Every XP gain times this.",
     "reload@xp.properties:multiplier"),
    ("xp.feedbackMs", "Feedback time", "xp", "int", "1500", "0", "10000", "", "ms", "live,adv", "", "reload@xp.properties:feedbackMs"),
    ("xp.block", "Block XP", "xp", "table", "", "0", "100000", "text|int;both;Skill|XP", "", "live", "XP per block.",
     "reload@xp.properties:block.;sep=:;entry=item"),
    ("xp.template", "Small chest XP", "xp", "int", "5", "0", "100000", "", "", "live", "", "reload@xp.properties:chest.xp.Chest_Small"),
    ("xp.quiet", "Quiet XP", "xp", "bool", "false", "", "", "01", "", "live", "No XP messages.", "reload@xp.properties:quiet"),
    ("coins.tags", "Tags", "coins", "table", "", "0", "100", "text|int;type;Label|Weight", "", "live,danger", "A custom: table.",
     "custom:TestCust@config.properties"),
    ("tools.resetAll", "Reset everything", "tools", "action", "", "", "", "Reset all", "", "danger", "Puts every value back.",
     "action:TestCust.resetAll"),
    ("tools.purge", "Purge cache", "tools", "action", "", "", "", "Purge cache", "", "", "Clears cached values.",
     "action:TestCust.purge;check=TestCust.check"),
    ("xp.startBonus", "Start bonus", "xp", "int", "0", "0", "100", "", "", "restart", "XP given once at start.",
     "reload@xp.properties:startBonus"),
    ("xp.alias", "Command aliases", "xp", "table", "", "", "", "text;type;Command", "", "restart,danger", "Registered at start.",
     "reload@xp.properties:alias.;confirm=never"),
    ("tools.editor", "Shop editor", "tools", "link", "", "", "", "shopadmin", "", "", "Opens the shop editor.", ""),
    ("info.build", "Build", "tools", "text", "x", "", "", "", "", "ro", "Read-only.", "field:TestCfg.BUILD@config.properties:build"),
]
FILES = ["Skyy_SkyyCfgTest/config.properties", "Skyy_SkyyCfgTest/xp.properties"]


# =====================================================================================================================  phase 1: build
def build():
    import skyybuild as B
    import skyycfg as CFG
    J = B.start()
    pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
    out = os.path.join(SCRATCH, "classes")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    def mk(name, fields=(), methods=(), iface=None, ctors=()):
        c = pool.makeClass(name)
        if iface:
            c.addInterface(pool.get(iface))
        for f in fields:
            c.addField(CtField.make(f, c))
        for s in ctors:
            c.addConstructor(CtNewConstructor.make(s, c))
        for m in methods:
            c.addMethod(CtNewMethod.make(m, c))
        return c

    # ---------------- 8.1.4: schemas that must stop the build
    neg_ok = [0]

    EXPECT = {"ms field bound": "needs *1000", "bool row without 01": "needs opts '01'", "unit ms row": "must bind a millisecond field",
              "wrong scale": "needs *1000", "max x scale": "does not fit the int field", "default outside": "does not pass its own row",
              "unknown flag": "unknown flag", "field not volatile": "must be public static volatile", "duplicate key": "duplicate key",
              "reload routine": "needs a public static method", "choice default": "does not pass its own row", "label over": "label must be",
              "camelCase ms field": "needs *1000", "part without danger": "needs the danger flag too",
              "confirm= without danger": "has no danger flag", "confirm=on on an int row": "is for bool rows",
              "confirm=up on an action": "take confirm=always or confirm=never only", "choice label over": "a choice label must be 1-20",
              "overlapping table prefixes": "overlap in", "scalar file key inside a table family": "inside the key family",
              "two rows bind one file key": "one row per file key", "custom: without a file": "must name its file"}

    def must_fail(what, pkg, fields, rows, defaults=None, files=("Skyy_SkyyNeg/config.properties",), reload=None, hooks_after=None):
        mk(pkg + ".NegCfg", fields=fields)
        want = [v for k, v in EXPECT.items() if what.startswith(k)][0]
        try:
            kit = CFG.emit(pool, pkg, MOD="SkyyNeg", TITLE="Neg", VERSION="0.1", NODE="skyyneg.admin", CATS=[("main", "Main")], ROWS=rows,
                           FILES=list(files), DEFAULTS=defaults, RELOAD=reload, ITEMS=set(ITEMS))
            if hooks_after:
                kit.check()
        except CFG.CfgError as e:
            msg = str(e)[len("skyycfg: "):]
            if want not in msg:
                raise SystemExit("NEGATIVE CHECK FAILED FOR THE WRONG REASON: %s -> %s" % (what, msg[:300]))
            print("  ok, refused:", what, "->", msg[:150])
            neg_ok[0] += 1
            return
        raise SystemExit("NEGATIVE CHECK DID NOT FAIL: " + what)

    print("8.1.4 schema checks that must fail:")
    must_fail("ms field bound to unit s without *1000", "com.skyy.neg1", ["public static volatile long INVITE_MS = 60000L;"],
              [("p.invite", "Invite", "main", "int", "60", "15", "600", "", "s", "live", "", "field:NegCfg.INVITE_MS@config.properties:inviteSeconds")])
    must_fail("bool row without 01 over a default file that writes 1", "com.skyy.neg2", ["public static volatile boolean N = true;"],
              [("v.notify", "Notify", "main", "bool", "true", "", "", "", "", "live", "", "field:NegCfg.N@config.properties:notify")],
              defaults={"config.properties": "notify=1\n"})
    must_fail("unit ms row bound to a field that is not a millisecond field", "com.skyy.neg3", ["public static volatile long DELAY = 5L;"],
              [("p.delay", "Delay", "main", "int", "5", "0", "100", "", "ms", "live", "", "field:NegCfg.DELAY@config.properties:delay")])
    must_fail("wrong scale (*100) on a millisecond field with unit s", "com.skyy.neg4", ["public static volatile long INVITE_MS = 60000L;"],
              [("p.invite", "Invite", "main", "int", "60", "15", "600", "", "s", "live", "", "field:NegCfg.INVITE_MS*100@config.properties:inviteSeconds")])
    must_fail("max x scale does not fit an int field", "com.skyy.neg5", ["public static volatile int TIMEOUT_MS = 1000;"],
              [("p.t", "Timeout", "main", "int", "1", "0", "3000000", "", "s", "live", "", "field:NegCfg.TIMEOUT_MS*1000@config.properties:t")])
    must_fail("default outside its own range", "com.skyy.neg6", ["public static volatile int P = 1;"],
              [("p.p", "P", "main", "int", "500", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:p")])
    must_fail("unknown flag", "com.skyy.neg7", ["public static volatile int P = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live,fast", "", "field:NegCfg.P@config.properties:p")])
    must_fail("field not volatile", "com.skyy.neg8", ["public static int P = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:p")])
    must_fail("duplicate key", "com.skyy.neg9", ["public static volatile int P = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:p"),
               ("p.p", "Q", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:q")])
    must_fail("reload routine that does not exist (deferred check)", "com.skyy.neg10", ["public static volatile int P = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live", "", "reload:NegCfg.nope@config.properties:p")], hooks_after=True)
    must_fail("choice default not in the list", "com.skyy.neg11", ["public static volatile String M = \"a\";"],
              [("p.m", "M", "main", "choice", "zz", "", "", "a|A,b|B", "", "live", "", "field:NegCfg.M@config.properties:m")])
    must_fail("label over 40 characters", "com.skyy.neg12", ["public static volatile int P = 1;"],
              [("p.p", "P" * 41, "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:p")])
    must_fail("camelCase ms field (inviteMs) bound to unit s without *1000", "com.skyy.neg13", ["public static volatile long inviteMs = 60000L;"],
              [("p.invite", "Invite", "main", "int", "60", "15", "600", "", "s", "live", "", "field:NegCfg.inviteMs@config.properties:inviteSeconds")])
    must_fail("part without danger (a part switch that would never ask)", "com.skyy.neg14", ["public static volatile boolean B = true;"],
              [("part.x", "X", "main", "bool", "true", "", "", "", "", "live,part", "", "field:NegCfg.B@config.properties:part.x")])
    must_fail("confirm= without danger (a silently ignored override)", "com.skyy.neg15", ["public static volatile boolean B = false;"],
              [("p.b", "B", "main", "bool", "false", "", "", "", "", "live", "", "field:NegCfg.B@config.properties:b;confirm=on")])
    must_fail("confirm=on on an int row", "com.skyy.neg16", ["public static volatile int P = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live,danger", "", "field:NegCfg.P@config.properties:p;confirm=on")])
    must_fail("confirm=up on an action row", "com.skyy.neg17", ["public static volatile int P = 1;"],
              [("t.go", "Go", "main", "action", "", "", "", "Go", "", "danger", "", "action:NegCfg.go;confirm=up")])
    must_fail("choice label over 20 characters", "com.skyy.neg18", ["public static volatile String M = \"a\";"],
              [("p.m", "M", "main", "choice", "a", "", "", "a|A,b|" + "B" * 21, "", "live", "", "field:NegCfg.M@config.properties:m")])
    must_fail("overlapping table prefixes (combat. and combat.role) in one file", "com.skyy.neg19", ["public static volatile int P = 1;"],
              [("t.a", "A", "main", "table", "", "", "", "int;type;XP", "", "live", "", "reload@config.properties:combat."),
               ("t.b", "B", "main", "table", "", "", "", "int;type;XP", "", "live", "", "reload@config.properties:combat.role")],
              reload="NegCfg.reload")
    must_fail("scalar file key inside a table family", "com.skyy.neg20", ["public static volatile int P = 1;"],
              [("t.a", "A", "main", "table", "", "", "", "int;type;XP", "", "live", "", "reload@config.properties:bank."),
               ("p.p", "P", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:bank.rate")],
              reload="NegCfg.reload")
    must_fail("two rows bind one file key", "com.skyy.neg21", ["public static volatile int P = 1;", "public static volatile int Q = 1;"],
              [("p.p", "P", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.P@config.properties:rate"),
               ("p.q", "Q", "main", "int", "1", "0", "100", "", "", "live", "", "field:NegCfg.Q@config.properties:rate")])
    must_fail("custom: without a file in a mod with two FILES", "com.skyy.neg22", ["public static volatile int P = 1;"],
              [("p.r", "R", "main", "range", "1-2", "0", "10", "", "", "live", "", "custom:NegCfg")],
              files=("Skyy_SkyyNeg/a.properties", "Skyy_SkyyNeg/b.properties"))

    # ---------------- schemas that must BUILD (a build check must not be too eager)
    pos_ok = [0]

    def must_pass(what, pkg, fields, rows, files=("Skyy_SkyyPos/config.properties",)):
        mk(pkg + ".PosCfg", fields=fields)
        try:
            CFG.emit(pool, pkg, MOD="SkyyPos", TITLE="Pos", VERSION="0.1", NODE="skyypos.admin", CATS=[("main", "Main")], ROWS=rows,
                     FILES=list(files), ITEMS=set(ITEMS))
        except CFG.CfgError as e:
            raise SystemExit("POSITIVE CHECK REFUSED: %s -> %s" % (what, str(e)[:300]))
        print("  ok, built:", what)
        pos_ok[0] += 1

    print("schemas that must build:")
    must_pass("plural field names ending in the letters MS (MAX_ITEMS, DEFAULT_TEAMS) are not millisecond fields", "com.skyy.pos1",
              ["public static volatile int MAX_ITEMS = 9;", "public static volatile long DEFAULT_TEAMS = 2L;"],
              [("p.items", "Max items", "main", "int", "9", "1", "64", "", "", "live", "", "field:PosCfg.MAX_ITEMS@config.properties:maxItems"),
               ("p.teams", "Teams", "main", "int", "2", "1", "8", "", "", "live", "", "field:PosCfg.DEFAULT_TEAMS@config.properties:teams")])
    must_pass("camelCase and MILLIS millisecond fields with the right unit and scale", "com.skyy.pos2",
              ["public static volatile long delayMs = 500L;", "public static volatile long graceMillis = 60000L;"],
              [("p.delay", "Delay", "main", "int", "500", "0", "10000", "", "ms", "live", "", "field:PosCfg.delayMs@config.properties:delayMs"),
               ("p.grace", "Grace", "main", "int", "1", "0", "60", "", "min", "live", "", "field:PosCfg.graceMillis*60000@config.properties:graceMinutes")])

    # ---------------- sample mod 1: SkyyCfgTest
    P = "com.skyy.cfgtest"
    mk(P + ".TestPerm", fields=[
        "public static final java.util.Set OK = java.util.Collections.synchronizedSet(new java.util.HashSet());",
        "public static final java.util.Set ITEMS = new java.util.HashSet(java.util.Arrays.asList(new String[] { %s }));" % ", ".join('"%s"' % i for i in ITEMS),
    ], methods=[
        "public static boolean has(java.util.UUID u, String node) { return u != null && OK.contains(u); }",
        "public static boolean item(String id) { return ITEMS.contains(id); }",
    ])
    mk(P + ".TestCfg", fields=[
        "public static java.nio.file.Path FILE;", "public static java.nio.file.Path FILE2;",
        "public static volatile boolean FLAG = true;", "public static volatile int PERCENT = 2;", "public static volatile long INVITE_MS = 60000L;",
        "public static volatile double SPREAD = 0.1;", "public static volatile String GREETING = \"Hello\";", "public static volatile int NOTIFY = 1;",
        "public static volatile String KIT = \"Food_Bread:5\";", "public static volatile String MODE = \"page\";", "public static volatile long BIG = 0L;",
        "public static volatile int MAXPAGES = 10;", "public static volatile boolean PAUSED = false;", "public static volatile int PRIO = 30000;",
        "public static volatile String BUILD = \"x\";", "public static volatile long PMIN = 10L;", "public static volatile long PMAX = 25L;",
        "public static volatile double XPMULT = 1.0;", "public static volatile int FEEDBACK = 1500;", "public static volatile int RELOADS = 0;",
    ], methods=[
        r"""public static java.util.Properties props(java.nio.file.Path p) {
  java.util.Properties pr = new java.util.Properties();
  try { java.io.InputStream in = java.nio.file.Files.newInputStream(p, new java.nio.file.OpenOption[0]); try { pr.load(in); } finally { in.close(); } } catch (Throwable t) { }
  return pr;
}""",
        r"""public static long lng(java.util.Properties p, String k, long d) { try { String v = p.getProperty(k); if (v == null) return d; return Long.parseLong(v.trim()); } catch (Throwable t) { return d; } }""",
        # like a mod's own load(): clamps, seconds -> ms, "anything except 0 is on"
        r"""public static void load() {
  java.util.Properties p = props(FILE);
  long pc = lng(p, "interestPercent", 2L); if (pc < 0L) pc = 0L; if (pc > 100L) pc = 100L; PERCENT = (int) pc;
  INVITE_MS = lng(p, "inviteSeconds", 60L) * 1000L;
  try { SPREAD = Double.parseDouble(p.getProperty("spread", "0.1").trim()); } catch (Throwable t) { }
  GREETING = p.getProperty("greeting", "Hello").trim();
  FLAG = !"false".equalsIgnoreCase(p.getProperty("part.shop", "true").trim());
  if ("0".equals(p.getProperty("defaults.visit.notify", "1").trim())) NOTIFY = 0; else NOTIFY = 1;
  KIT = p.getProperty("starter.kit", "Food_Bread:5").trim();
  MODE = p.getProperty("openMode", "page").trim();
  long mp = lng(p, "maxPages", 10L); if (mp < 1L) mp = 1L; if (mp > 1000L) mp = 1000L; MAXPAGES = (int) mp;
  PAUSED = "true".equalsIgnoreCase(p.getProperty("paused", "false").trim());
  PRIO = (int) lng(p, "chat.priority", 30000L);
  BUILD = p.getProperty("build", "x").trim();
  BIG = lng(p, "payMax", 0L);
  PMIN = lng(p, "penaltyMin", 10L); PMAX = lng(p, "penaltyMax", 25L);
}""",
        r"""public static void loadXp() {
  java.util.Properties p = props(FILE2);
  try { XPMULT = Double.parseDouble(p.getProperty("multiplier", "1.0").trim()); } catch (Throwable t) { }
  FEEDBACK = (int) lng(p, "feedbackMs", 1500L);
}""",
        r"""public static void reload() { RELOADS = RELOADS + 1; load(); loadXp(); }""",
    ])
    mk(P + ".TestCust", fields=["public static volatile int ACTIONS = 0;", "public static final java.util.TreeMap TAGS = new java.util.TreeMap();",
                                "public static volatile int PURGES = 0;", "public static volatile boolean PURGEBLOCK = false;"], methods=[
        r"""public static String customGet(String key) {
  if (key.startsWith("coins.tags[")) return (String) TAGS.get(key.substring(11, key.length() - 1));
  if (!key.equals("coins.penalty")) return null;
  long a = com.skyy.cfgtest.TestCfg.PMIN; long b = com.skyy.cfgtest.TestCfg.PMAX;
  if (a == b) return String.valueOf(a);
  return a + "-" + b;
}""",
        r"""public static Object[] customSet(String key, String value) {
  if (key.startsWith("coins.tags[")) {
    String e = key.substring(11, key.length() - 1);
    if (value == null) { TAGS.remove(e); return new Object[] { "ok", "", "Tag removed.", new String[] { "tag." + e, null } }; }
    TAGS.put(e, value);
    return new Object[] { "ok", value, "Tag saved.", new String[] { "tag." + e, value.replace('|', ':') } };
  }
  if (!key.equals("coins.penalty")) return new Object[] { "unknown", null, "no such key" };
  int d = value.indexOf('-');
  long a = 0L; long b = 0L;
  if (d < 0) { a = Long.parseLong(value); b = a; } else { a = Long.parseLong(value.substring(0, d)); b = Long.parseLong(value.substring(d + 1)); }
  com.skyy.cfgtest.TestCfg.PMIN = a; com.skyy.cfgtest.TestCfg.PMAX = b;
  return new Object[] { "ok", value, "Death penalty: " + value + "% - saved.", new String[] { "penaltyMin", String.valueOf(a), "penaltyMax", String.valueOf(b) } };
}""",
        r"""public static String[] customKeys(String table) { return (String[]) TAGS.keySet().toArray(new String[0]); }""",
        r"""public static String customRead(String key, java.util.Map m) {
  Object a = m.get("penaltyMin"); Object b = m.get("penaltyMax");
  if (a == null || b == null) return null;
  if (a.equals(b)) return (String) a;
  return a + "-" + b;
}""",
        r"""public static String check(String key, String value) {
  if (key.equals("vault.maxPages") && value != null && Long.parseLong(value) < 7L) return "Lower than the highest page a player already uses (7).";
  if (key.equals("msg.greeting") && "?".equals(value)) return "?Really set the greeting to a question mark?";
  if (key.equals("tools.purge")) { if (value != null) return "an action's check gets no value"; if (PURGEBLOCK) return "A purge is already running."; return "?Purge every cached value?"; }
  return null;
}""",
        r"""public static Object[] resetAll(java.util.UUID who, String name) { ACTIONS = ACTIONS + 1; return new Object[] { "ok", "", "Reset done by " + name + "." }; }""",
        r"""public static Object[] purge(java.util.UUID who, String name) { PURGES = PURGES + 1; return new Object[] { "ok", "", "Purged." }; }""",
    ])
    kit = CFG.emit(pool, P, MOD="SkyyCfgTest", TITLE="Config test", VERSION="0.1", NODE="skyycfgtest.admin", CATS=CATS, ROWS=ROWS,
                   FILES=FILES, NOTE="Harness sample for tools/skyycfg.py.", RELOAD="TestCfg.reload", KEEP=20, ALIASES=["SkyyOldTest"],
                   DEFAULTS={"config.properties": CONFIG_TEXT, "xp.properties": XP_TEXT}, ITEMS=set(ITEMS),
                   PERM_FN="TestPerm.has", ITEM_FN="TestPerm.item")
    # compiled AFTER emit: proves hooks are resolved by reflection and checked at kit.write()
    mk(P + ".TestCust2", fields=["public static volatile int AFTER = 0;", "public static volatile String LASTKEY = null;"], methods=[
        "public static void afterSet(String key) { AFTER = AFTER + 1; LASTKEY = key; }"])
    stress = mk(P + ".TestStress", iface="java.lang.Runnable",
                fields=["public int seed;", "public int n;", "public volatile int errors;", "public volatile int done;", "public volatile String last;"],
                ctors=["public TestStress(int s, int n) { this.seed = s; this.n = n; }"],
                methods=[r"""public void run() {
  java.util.Map b = (java.util.Map) System.getProperties().get("skyy.bridge");
  java.util.function.Function f = (java.util.function.Function) b.get("config:fn:SkyyCfgTest");
  java.util.UUID who = java.util.UUID.fromString("00000000-0000-0000-0000-00000000000a");
  java.util.Random r = new java.util.Random((long) this.seed);
  long end = System.currentTimeMillis() + 10000L;
  for (int k = 0; k < this.n && System.currentTimeMillis() < end; k++) {
    try {
      int op = r.nextInt(8);
      Object res = null;
      if (op == 0) res = f.apply(new Object[] { "get", "bank.interestPercent" });
      else if (op == 1) res = f.apply(new Object[] { "set", "bank.interestPercent", String.valueOf(r.nextInt(101)), who, "T" + this.seed, "yes", "menu" });
      else if (op == 2) res = f.apply(new Object[] { "set", "party.inviteSeconds", String.valueOf(15 + r.nextInt(586)), who, "T" + this.seed, "yes", "menu" });
      else if (op == 3) res = f.apply(new Object[] { "set", "xp.multiplier", String.valueOf(r.nextInt(100)) + ".5", who, "T" + this.seed, "yes", "menu" });
      else if (op == 4) res = f.apply(new Object[] { "tset", "xp.block", "Ore_Iron", "Mining|" + r.nextInt(1000), who, "T" + this.seed, "yes" });
      else if (op == 5) res = f.apply(new Object[] { "keys", "xp.block", "" });
      else if (op == 6) res = f.apply(new Object[] { "get", "xp.multiplier" });
      else res = f.apply(new Object[] { "status" });
      if (res == null) { this.errors = this.errors + 1; this.last = "null for op " + op; }
      else if (res instanceof Object[] && ((Object[]) res).length == 3 && "error".equals(((Object[]) res)[0])) { this.errors = this.errors + 1; this.last = String.valueOf(((Object[]) res)[2]); }
      this.done = this.done + 1;
    } catch (Throwable t) { this.errors = this.errors + 1; this.last = t.toString(); }
  }
}"""])
    kit.write(out)
    for n in ("TestPerm", "TestCfg", "TestCust", "TestCust2", "TestStress"):
        pool.get(P + "." + n).writeFile(out)
    # ---------------- sample mod 2: SkyyCfgPlain (real PermissionsModule + Item paths, no reload routine: the kit clamps hand edits)
    P2 = "com.skyy.cfgplain"
    mk(P2 + ".PlainCfg", fields=["public static volatile int LIMIT = 5;", "public static volatile String KIT = \"\";"])
    kit2 = CFG.emit(pool, P2, MOD="SkyyCfgPlain", TITLE="Plain", VERSION="0.1", NODE="skyycfgplain.admin", CATS=[("main", "Main")],
                    FILES=["Skyy_SkyyCfgPlain/config.properties"], ITEMS=set(ITEMS), ROWS=[
                        ("limit", "Limit", "main", "int", "5", "1", "50", "", "", "live", "", "field:PlainCfg.LIMIT"),
                        ("kit", "Kit", "main", "items", "", "0", "9", "", "", "live", "", "field:PlainCfg.KIT")])
    kit2.write(out)
    pool.get(P2 + ".PlainCfg").writeFile(out)
    jar = os.path.join(SCRATCH, "cfgkit-samples.jar")
    B.assemble(jar, B.manifest("SkyyCfgTest", "0.1", "skyycfg harness samples", P + ".TestCfg"), out)
    print("phase 1: %d negative checks refused as expected, %d positive checks built, %d + %d kit classes built" % (
        neg_ok[0], pos_ok[0], len(kit.classes), len(kit2.classes)))
    return jar


# =====================================================================================================================  phase 2: run
FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def run(jar):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "--enable-native-access=ALL-UNNAMED", classpath=[B.SERVER_JAR, jar], convertStrings=True)
    from jpype import JClass, JArray, JObject
    import zipfile
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return
    P = "com.skyy.cfgtest."
    Rows, Pub, CFile, Log = JClass(P + "CfgRows"), JClass(P + "CfgPub"), JClass(P + "CfgFile"), JClass(P + "CfgLog")
    TestCfg, TestPerm, TestCust, TestCust2, Stress = (JClass(P + "TestCfg"), JClass(P + "TestPerm"), JClass(P + "TestCust"),
                                                      JClass(P + "TestCust2"), JClass(P + "TestStress"))
    UUID, Paths, Integer, System = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer"), JClass("java.lang.System")
    Props, FIS, ISR, Thread = JClass("java.util.Properties"), JClass("java.io.FileInputStream"), JClass("java.io.InputStreamReader"), JClass("java.lang.Thread")
    A = UUID.fromString("00000000-0000-0000-0000-00000000000a")
    Bp = UUID.fromString("00000000-0000-0000-0000-00000000000b")
    TestPerm.OK.add(A)
    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyCfgTest")
    os.makedirs(home)
    cfgp, xpp = os.path.join(home, "config.properties"), os.path.join(home, "xp.properties")
    open(cfgp, "w", newline="\n").write(CONFIG_TEXT)
    open(xpp, "w", newline="\r\n").write(XP_TEXT)          # CRLF file: line endings must survive
    TestCfg.FILE = Paths.get(cfgp)
    TestCfg.FILE2 = Paths.get(xpp)
    TestCfg.reload()
    Pub.start(Paths.get(mods), None)
    bridge = Rows.bridge()
    fn = bridge.get("config:fn:SkyyCfgTest")
    check(fn is not None, "config:fn published")

    def op(*args):
        a = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            a[i] = x
        return fn.apply(a)

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def st(r):
        return str(r[0]) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def setv(k, v, who=A, confirm="yes", via="menu", name="Skyy"):
        return R(op("set", k, v, who, name, confirm, via))

    def ftext(p):
        return open(p, "rb").read().decode("latin-1")

    def fprops(p, utf8=False):
        pr = Props()
        s = FIS(p)
        try:
            if utf8:
                pr.load(ISR(s, "UTF-8"))
            else:
                pr.load(s)
        finally:
            s.close()
        return pr

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    def settle():
        # saves are serialised by the save lock, but reload routines run after it, maybe on a fallback thread: wait them out
        Pub.flush()
        time.sleep(0.4)
        Pub.flush()

    # ---------------- B. header
    hdr = bridge.get("config:def:SkyyCfgTest")
    check(hdr is not None and len(hdr) == 10 and str(hdr[0]) == "1" and str(hdr[1]) == "SkyyCfgTest" and str(hdr[3]) == "0.1"
          and str(hdr[4]) == "skyycfgtest.admin", "header elements 0-4")
    check(list(hdr[5]) == [c for c, _ in CATS] and len(hdr[7]) == len(ROWS) and all(len(r) == 11 for r in hdr[7]), "header cats + rows")
    check(str(hdr[8]) == ",".join(FILES) and str(hdr[9]).startswith("Harness"), "header files + note")
    check(str(bridge.get("config:epoch:SkyyCfgTest")) == "0", "epoch starts at 0")
    print("B. header ok")

    # ---------------- C. (8.2 a) get / set per type
    check(get("bank.interestPercent") == "2" and get("party.inviteSeconds") == "60" and get("bazaar.spread") == "0.1"
          and get("visit.notify") == "true" and get("coins.penalty") == "10-25" and get("xp.multiplier") == "1"
          and get("xp.block") == "" and get("tools.editor") == "" and get("xp.quiet") == "false", "initial gets %s %s %s" % (get("bazaar.spread"), get("coins.penalty"), get("xp.multiplier")))
    r = setv("part.shop", "false", confirm="")
    check(r[0] == "confirm" and r[2].startswith("Turn Shop OFF for everyone on this server?") and TestCfg.FLAG, "part OFF asks first: %s" % (r,))
    r = setv("part.shop", "false")
    check(r == ("ok", "false", "Shop: OFF - saved (applies now).") and not TestCfg.FLAG, "part OFF with yes: %s" % (r,))
    r = setv("part.shop", "true", confirm="")
    check(r[0] == "ok" and TestCfg.FLAG, "part ON asks nothing: %s" % (r,))
    check(setv("bank.interestPercent", "150")[0:2] == ("bad", None) and "from 0 to 100%" in setv("bank.interestPercent", "150")[2], "int out of range")
    check(setv("bank.interestPercent", "abc")[0] == "bad" and setv("bank.interestPercent", "2.5")[0] == "bad", "int wrong type")
    # INFO line + confirm text
    bos = JClass("java.io.ByteArrayOutputStream")()
    old_out = System.out
    System.setOut(JClass("java.io.PrintStream")(bos, True, "UTF-8"))
    r = setv("bank.interestPercent", "3", confirm="")
    check(r[0] == "confirm" and r[2].startswith("Change Interest per payout from 2% to 3%?"), "danger confirm text: %s" % (r,))
    check(TestCfg.PERCENT == 2, "confirm changed nothing")
    r = setv("bank.interestPercent", "3")
    System.setOut(old_out)
    check(r == ("ok", "3", "Interest per payout: 3% - saved (applies now).") and TestCfg.PERCENT == 3, "int set: %s" % (r,))
    check("[SkyyCfgTest] config bank.interestPercent 2 -> 3 by Skyy (menu)" in str(bos.toString("UTF-8")), "INFO line format")
    check(setv("bank.interestPercent", "3")[0] == "ok" and "already" in setv("bank.interestPercent", "3")[2], "same value = already")
    for typed, want in (("2k", "2000"), ("1.5m", "1500000"), ("1,000", "1000"), ("10k coins", "10000")):
        r = setv("coins.payMax", typed)
        check(r[0] == "ok" and r[1] == want and TestCfg.BIG == int(want), "int typed %r -> %s (%s)" % (typed, want, r))
    r = setv("bazaar.spread", "0.25")
    check(r[0] == "ok" and r[1] == "0.25" and abs(TestCfg.SPREAD - 0.25) < 1e-12, "dec set %s" % (r,))
    check(setv("bazaar.spread", "1.5")[0] == "bad", "dec out of range")
    r = setv("msg.greeting", "  Hi there  ")
    check(r[0] == "ok" and r[1] == "Hi there" and TestCfg.GREETING == "Hi there", "text trimmed %s" % (r,))
    check(setv("msg.greeting", "")[0] == "bad", "text min length")
    r = setv("msg.greeting", "?", confirm="")
    check(r == ("confirm", None, "Really set the greeting to a question mark?"), "check hook ?question asks: %s" % (r,))
    r = setv("vault.openMode", "Chest window")
    check(r[0] == "ok" and r[1] == "chest" and TestCfg.MODE == "chest", "choice by label %s" % (r,))
    r = setv("vault.openMode", "x")
    check(r[0] == "bad" and "Page view, Chest window" in r[2], "choice bad %s" % (r,))
    r = setv("kit.items", "Food_Bread:3, Ore_Iron:2")
    check(r[0] == "ok" and r[1] == "Food_Bread:3,Ore_Iron:2" and TestCfg.KIT == "Food_Bread:3,Ore_Iron:2", "items %s" % (r,))
    check(setv("kit.items", "Nope_Item:1")[2] == "Unknown item: Nope_Item.", "items unknown id")
    check(setv("kit.items", "Food_Bread:0")[0] == "bad" and setv("kit.items", "Food_Bread,Food_Bread")[0] == "bad", "items qty / duplicate")
    check(setv("kit.items", "Skyy_*")[0] == "bad", "items * without prefix opt")
    r = setv("coins.penalty", "5%-10%", confirm="")
    check(r[0] == "confirm" and "from 10%-25% to 5%-10%" in r[2], "range confirm %s" % (r,))
    r = setv("coins.penalty", "5%-10%")
    check(r[0] == "ok" and r[1] == "5-10" and TestCfg.PMIN == 5 and TestCfg.PMAX == 10 and get("coins.penalty") == "5-10", "custom range %s" % (r,))
    check(setv("coins.penalty", "30-10")[0] == "bad" and setv("coins.penalty", "5-200")[0] == "bad", "range order / bound")
    r = setv("xp.multiplier", "2.5")
    check(r[0] == "ok" and r[1] == "2.5" and get("xp.multiplier") == "2.5", "reload row set %s" % (r,))
    check(setv("xp.feedbackMs", "2000")[0] == "ok", "ms reload row")
    r = setv("vault.maxPages", "5")
    check(r == ("bad", None, "Lower than the highest page a player already uses (7)."), "check hook refuses %s" % (r,))
    a0 = TestCust2.AFTER
    r = setv("vault.maxPages", "20")
    check(r[0] == "ok" and TestCfg.MAXPAGES == 20 and TestCust2.AFTER == a0 + 1 and str(TestCust2.LASTKEY) == "vault.maxPages", "after hook %s" % (r,))
    check(setv("ah.paused", "true", confirm="")[0] == "confirm", "confirm=on asks when pausing")
    setv("ah.paused", "true")
    check(setv("ah.paused", "false", confirm="")[0] == "ok" and not TestCfg.PAUSED, "confirm=on: unpausing asks nothing")
    r = setv("chat.priority", "31000")
    check(r[0] == "restart" and "after a server restart" in r[2] and TestCfg.PRIO == 30000 and get("chat.priority") == "31000", "restart row %s" % (r,))
    s = [str(x) for x in op("status")]
    check(s[0] == "restart" and s[1].startswith("1 change"), "status restart %s" % s)
    check(setv("info.build", "y")[0] == "bad", "ro refused")
    check(setv("nope.key", "1")[0] == "unknown", "unknown key")
    check(setv("tools.editor", "x")[0] == "bad" and setv("xp.block", "x")[0] == "bad", "link / table have no value")
    check(setv("bank.interestPercent", "4", who=Bp)[0] == "denied", "denied without the node")
    check(setv("bank.interestPercent", "4", who=None)[0] == "denied", "null who via menu denied")
    r = setv("bank.interestPercent", "4", who=None, via="command", name="Ghost")
    check(r[0] == "denied" and TestCfg.PERCENT == 3, "null who via command denied (a UUID lookup bug is not the console) %s" % (r,))
    r = setv("bank.interestPercent", "4", who=None, via="console", name=None)
    check(r[0] == "ok" and TestCfg.PERCENT == 4, "console (null who, via console) %s" % (r,))
    check(any(l.endswith("\tconsole\t-\tconsole\tbank.interestPercent\t3\t4\tok") for l in logs()), "console change logged by console, via=console")
    Fn = JClass(P + "CfgFn")
    check(str(Fn.cmdSet("bank.interestPercent", "5", None, "Ghost")) == "Could not tell who sent this command - nothing was changed."
          and TestCfg.PERCENT == 4, "cmdSet refuses a null UUID instead of treating it as the console")
    check(str(Fn.cmdSetConsole("bank.interestPercent", "4")) == "Interest per payout is already 4%.", "cmdSetConsole passes the permission gate")
    check(str(Fn.cmdSet("bank.interestPercent", "4", Bp, "B")).startswith("Changing SkyyCfgTest needs"), "cmdSet re-checks the node")
    r = setv("bazaar.spread", None)
    check(r[0] == "ok" and r[1] == "0.1", "null value = default %s" % (r,))
    r = R(op("action", "tools.resetAll", A, "Skyy", ""))
    check(r[0] == "confirm" and r[2].startswith("Reset all? Puts every value back."), "action confirm %s" % (r,))
    r = R(op("action", "tools.resetAll", A, "Skyy", "yes"))
    check(r == ("ok", "", "Reset done by Skyy.") and TestCust.ACTIONS == 1, "action ok %s" % (r,))
    check(R(op("action", "tools.resetAll", Bp, "B", "yes"))[0] == "denied", "action denied")
    ep = int(str(bridge.get("config:epoch:SkyyCfgTest")))
    check(ep >= 15, "epoch counts changes (%d)" % ep)
    print("C. get/set per type done")

    # ---------------- D. (8.2 b) garbage never throws
    garbage = [None, "x", JArray(JObject)(0), [1], ["nope"], ["set"], ["set", 5, "1", A, "n", "", "menu"], ["set", "bank.interestPercent", 5, A, "n", "", "menu"],
               ["set", "bank.interestPercent", "5", "notauuid", "n", "", "menu"], ["get"], ["get", None], ["get", 7], ["keys"], ["keys", "bank.interestPercent", ""],
               ["tset", "xp.block"], ["add", "xp.block", None, None, A, "n", "yes"], ["remove", "xp.block", "Ore_Iron"], ["action"], ["action", 1, A, "n", "yes"],
               ["reload"], ["reload", "x", "n"], ["export", 5], ["export", "weird"], ["import", "garbage", A, "n", "apply"], ["import", "SKYY1.SkyyCfgTest.!!!.00", A, "n", "preview"],
               ["import", None, A, "n", "preview"], ["restore", "../../x#1", A, "n", "preview"], ["restore", "Skyy_SkyyCfgTest~config.properties#20260101-000000-000", A, "n", "apply"],
               ["log", "abc"], ["log", Integer.valueOf(-5)], ["versions", "extra"], ["status", 1, 2]]
    thrown = 0
    for g in garbage:
        try:
            if isinstance(g, list):
                a = JArray(JObject)(len(g))
                for i, x in enumerate(g):
                    a[i] = x
                res = fn.apply(a)
            else:
                res = fn.apply(g)
            if res is not None and hasattr(res, "__len__") and len(res) == 3 and str(res[0]) == "error" and "internal" in str(res[2]):
                FAILS.append("internal error for %r" % (g,))
        except Exception as e:
            thrown += 1
            FAILS.append("garbage threw %r: %s" % (g, e))
    check(thrown == 0, "no garbage input throws")
    print("D. %d garbage inputs, none threw" % len(garbage))

    # ---------------- E. (8.2 c) line-preserving write-through
    Pub.flush()
    before = CONFIG_TEXT.split("\n")
    after = ftext(cfgp).split("\n")
    changed_keys = {"interestPercent", "spread", "greeting", "part.shop", "starter.kit", "openMode", "maxPages", "paused", "chat.priority",
                    "penaltyMin", "penaltyMax"}
    ok_lines = True
    for i, line in enumerate(before):
        k = line.split("=", 1)[0] if ("=" in line and not line.startswith("#")) else None
        if k in changed_keys:
            ok_lines &= after[i].startswith(k + "=")
        else:
            ok_lines &= after[i] == line
    check(ok_lines, "comments, blank lines and key order unchanged (only changed values differ)")
    tail = after[len(before) - 1:]
    check("# ---- changed in game (SkyWynn Menu) ----" in tail and any(l.startswith("payMax=") for l in tail), "new key appended under the header: %s" % tail)
    check(after.count("# ---- changed in game (SkyWynn Menu) ----") == 1, "one header")
    check("interestPercent=4" in after and "spread=0.1" in after and "penaltyMin=5" in after and "defaults.visit.notify=1" in after, "values written")
    r = setv("xp.template", "7")
    settle()
    xl = ftext(xpp).split("\r\n")
    check("chest.xp.Chest_Small=7" in xl and xl.index("chest.xp.Chest_Small=7") == XP_TEXT.split("\n").index("# chest.xp.Chest_Small=500"), "template line uncommented in place")
    check(any(l.startswith("# chests.enabled=false stops") for l in xl), "doc comment kept (not a template)")
    check(ftext(xpp).count("\r\n") == len(xl) - 1 and "\n" not in ftext(xpp).replace("\r\n", ""), "CRLF line endings kept")
    check("multiplier=2.5" in xl and TestCfg.XPMULT == 2.5 and TestCfg.FEEDBACK == 2000, "reload routine ran after the write (XPMULT %s)" % TestCfg.XPMULT)
    r = setv("msg.greeting", "Gr\u00fc\u00dfe \u2603 Welt")
    Pub.flush()
    raw = open(cfgp, "rb").read()
    check(b"greeting=Gr\\u00fc\\u00dfe \\u2603 Welt" in raw and all(b < 128 for b in raw), "non-ASCII written as \\uXXXX")
    check(str(fprops(cfgp).getProperty("greeting")) == "Gr\u00fc\u00dfe \u2603 Welt" and str(fprops(cfgp, True).getProperty("greeting")) == "Gr\u00fc\u00dfe \u2603 Welt",
          "ISO-8859-1 and UTF-8 readers see the same value")
    setv("msg.greeting", "  lead")
    Pub.flush()
    check(str(fprops(cfgp).getProperty("greeting")) == "lead", "trimmed text (leading space escaped if any)")
    print("E. line-preserving write done")

    # ---------------- F. (8.2 d) hand edit between two sets
    setv("bank.interestPercent", "5")
    Pub.flush()
    t = ftext(cfgp).replace("maxPages=20", "maxPages=50").replace("# the end", "# the end\n# a hand-written comment")
    open(cfgp, "w", newline="\n").write(t)
    st_ = os.stat(cfgp)
    os.utime(cfgp, (st_.st_atime, st_.st_mtime + 5))
    r0 = TestCfg.RELOADS
    setv("vault.openMode", "page")
    settle()
    t2 = ftext(cfgp)
    check("maxPages=50" in t2 and "openMode=page" in t2 and "interestPercent=5" in t2 and "# a hand-written comment" in t2, "hand edit and in-game value both survive")
    check(TestCfg.MAXPAGES == 50 and TestCfg.RELOADS > r0, "hand edit applied through the mod's reload routine")
    L = logs()
    check(any("\tfile\t-\tfile\tvault.maxPages\t20\t50\tok" in l for l in L), "log has the via=file line")
    # a hand edit the mod's loader clamps is logged status=clamped
    t = ftext(cfgp).replace("interestPercent=5", "interestPercent=250")
    open(cfgp, "w", newline="\n").write(t)
    os.utime(cfgp, (st_.st_atime, st_.st_mtime + 11))
    R(op("reload", A, "Skyy"))
    settle()
    check(TestCfg.PERCENT == 100 and any("\tbank.interestPercent\t250\t100\tclamped" in l for l in logs()), "loader clamp logged status=clamped")
    setv("bank.interestPercent", "5")
    Pub.flush()
    print("F. hand edits done")

    # ---------------- G. (8.2 e) unreadable files
    w0 = Rows.WARNS
    Pub.flush()
    xbytes = open(xpp, "rb").read()
    os.remove(xpp)
    os.makedirs(xpp)
    r = R(op("reload", A, "Skyy"))
    check(r[0] == "error" and "xp.properties cannot be read" in r[2], "reload of a folder-named file -> error %s" % (r,))
    s = [str(x) for x in op("status")]
    check(s[0] == "unreadable", "status unreadable %s" % s)
    check(setv("xp.multiplier", "3")[0] == "error", "change to the unreadable file refused")
    check(setv("bank.interestPercent", "6")[0] == "ok", "the other file still works")
    check(op("export", "all") is None, "export refused while unreadable")
    Pub.flush()
    check(os.path.isdir(xpp) and os.listdir(xpp) == [], "folder untouched")
    check(Rows.WARNS == w0 + 1, "exactly one warning (%d)" % (Rows.WARNS - w0))
    os.rmdir(xpp)
    open(xpp, "wb").write(xbytes)
    r = R(op("reload", A, "Skyy"))
    settle()
    check(r[0] == "ok" and str(op("status")[0]) in ("ok", "restart"), "reload after the fix %s" % (r,))
    # exclusive lock: the pending change waits, the file is never overwritten
    import msvcrt
    Pub.flush()
    w0 = Rows.WARNS
    cbytes = open(cfgp, "rb").read()
    h = open(cfgp, "r+b")
    msvcrt.locking(h.fileno(), msvcrt.LK_NBLCK, len(cbytes))
    r = setv("bank.interestPercent", "7")
    check(r[0] == "ok", "change accepted in memory before the lock is seen")
    Pub.flush()
    s = [str(x) for x in op("status")]
    check(s[0] == "unreadable", "locked file -> unreadable %s" % s)
    check(setv("bank.interestPercent", "8")[0] == "error", "further change refused while locked")
    Pub.flush()
    check(Rows.WARNS == w0 + 1, "locked file: exactly one warning (%d)" % (Rows.WARNS - w0))
    h.seek(0)
    msvcrt.locking(h.fileno(), msvcrt.LK_UNLCK, len(cbytes))
    h.close()
    check(open(cfgp, "rb").read() == cbytes, "locked file untouched byte for byte")
    R(op("reload", A, "Skyy"))
    settle()
    check("interestPercent=7" in ftext(cfgp) and get("bank.interestPercent") == "7", "the waiting change is written after the fix")
    # readable but not replaceable (another handle without delete sharing): status unsaved, kept in memory, written once possible
    w0 = Rows.WARNS
    h = open(cfgp, "rb")
    r = setv("bank.interestPercent", "8")
    Pub.flush()
    s = [str(x) for x in op("status")]
    check(r[0] == "ok" and s[0] == "unsaved" and "retrying every 30 s" in s[1] and get("bank.interestPercent") == "8", "failed write -> unsaved %s" % s)
    check("interestPercent=7" in ftext(cfgp) and Rows.WARNS == w0 + 1, "failed write: file unchanged, one warning")
    r = setv("bank.interestPercent", "9")
    Pub.flush()
    check(r[0] == "ok" and Rows.WARNS == w0 + 1, "further changes still accepted while unsaved, no second warning")
    h.close()
    Pub.flush()
    s = [str(x) for x in op("status")]
    check(s[0] != "unsaved" and "interestPercent=9" in ftext(cfgp), "saved once the handle is gone %s" % s)
    print("G. unreadable files done")

    # ---------------- H. (8.2 f) history, restore, undo of the restore, two files
    hdir = os.path.join(home, "config-history")
    for n in range(25):
        setv("bank.interestPercent", str(10 + n))
        Pub.flush()
    baks = [f for f in os.listdir(hdir) if f.startswith("Skyy_SkyyCfgTest~config.properties.") and f.endswith(".bak")]
    check(len(baks) == 20, "20 copies kept of 25+ changes (%d)" % len(baks))
    vers = [str(v) for v in op("versions")]
    check(all(len(v.split("\t")) == 5 for v in vers) and all(v.split("\t")[1] in FILES for v in vers), "versions name their file")
    check(sum(1 for v in vers if v.split("\t")[1] == FILES[0]) == 20, "max 20 per file")
    target = [v for v in vers if v.split("\t")[1] == FILES[0]][5]
    tid = target.split("\t")[0]
    old_val = fprops(os.path.join(hdir, tid.split("#")[0] + "." + tid.split("#")[1] + ".bak")).getProperty("interestPercent")
    r = R(op("restore", tid, A, "Skyy", "preview"))
    check(r[0] == "ok" and ("Interest per payout: 34% -> " + str(old_val) + "%") in r[2], "restore preview lists the difference %s" % (r,))
    check(get("bank.interestPercent") == "34", "preview changed nothing")
    newest_before = [str(v) for v in op("versions")][0].split("\t")[0]
    r = R(op("restore", tid, A, "Skyy", "apply"))
    Pub.flush()
    check(r[0] == "ok" and get("bank.interestPercent") == str(old_val) and TestCfg.PERCENT == int(str(old_val)), "restore applied %s" % (r,))
    vers2 = [str(v) for v in op("versions")]
    check(vers2[0].split("\t")[0] != newest_before and "before restore by Skyy" in vers2[0], "restore made its own version: %s" % vers2[0])
    r = R(op("restore", vers2[0].split("\t")[0], A, "Skyy", "apply"))
    Pub.flush()
    check(r[0] == "ok" and get("bank.interestPercent") == "34", "undo of the restore %s" % (r,))
    check(any("\tbank.interestPercent\t" in l and "\trestore\t" in l for l in logs()), "restore logged via=restore")
    setv("xp.multiplier", "4")
    setv("bank.interestPercent", "35")
    Pub.flush()
    vers3 = [str(v) for v in op("versions")]
    check(any(v.split("\t")[1] == FILES[1] for v in vers3[:3]) and any(v.split("\t")[1] == FILES[0] for v in vers3[:3]), "both files have versions")
    xb = open(xpp, "rb").read()
    cfg_ver = [v for v in vers3 if v.split("\t")[1] == FILES[0]][0].split("\t")[0]
    r = R(op("restore", cfg_ver, A, "Skyy", "apply"))
    Pub.flush()
    check(r[0] == "ok" and get("bank.interestPercent") == "34" and open(xpp, "rb").read() == xb, "restoring file 1 leaves file 2 byte for byte")
    check(R(op("restore", cfg_ver, Bp, "B", "apply"))[0] == "denied", "restore apply needs the node")
    print("H. history done")

    # ---------------- I. (8.2 g, 8.1.3) export / import
    for scope in ("changed", "all"):
        code = str(op("export", scope))
        check(code.startswith("SKYY1.SkyyCfgTest.") and len(code.split(".")) == 4, "export %s shape" % scope)
        r = R(op("import", code, A, "Skyy", "preview"))
        check(r[0] == "ok" and r[1] == "0", "export %s -> import preview: 0 changes %s" % (scope, r))
    setv("bank.interestPercent", "42")
    setv("vault.openMode", "chest")
    R(op("add", "xp.block", "Ore_Gold", "Mining|8", A, "Skyy", "yes"))
    code = str(op("export", "changed"))
    setv("bank.interestPercent", "2")
    setv("vault.openMode", "page")
    R(op("remove", "xp.block", "Ore_Gold", A, "Skyy", "yes"))
    r = R(op("import", code, A, "Skyy", "preview"))
    check(r[0] == "ok" and r[1] == "3" and "Interest per payout: 2% -> 42%" in r[2] and "Block XP: Ore_Gold added (Mining / 8)" in r[2], "import preview lists changes %s" % (r,))
    check(R(op("import", code, Bp, "B", "apply"))[0] == "denied", "import apply needs the node")
    r = R(op("import", code, A, "Skyy", "apply"))
    Pub.flush()
    check(r[0] == "ok" and get("bank.interestPercent") == "42" and get("vault.openMode") == "chest" and "block.Ore_Gold=Mining:8" in ftext(xpp), "import applied %s" % (r,))
    bad = code[:-1] + ("0" if code[-1] != "0" else "1")
    check(R(op("import", bad, A, "Skyy", "preview"))[2].startswith("The code is damaged (checksum"), "bad checksum refused")

    def enc(mod, text):
        raw = text.encode("utf-8")
        return "SKYY1.%s.%s.%08x" % (mod, base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode().rstrip("="), zlib.crc32(raw) & 0xffffffff)

    r = R(op("import", enc("SkyyOther", "_mod=SkyyOther\nbank.interestPercent=9\n"), A, "Skyy", "preview"))
    check(r[0] == "bad" and "This code is for SkyyOther" in r[2], "wrong mod refused %s" % (r,))
    r = R(op("import", enc("SkyyOldTest", "_mod=SkyyOldTest\nbank.interestPercent=9\n"), A, "Skyy", "apply"))
    check(r[0] == "ok" and get("bank.interestPercent") == "9", "legacy alias accepted %s" % (r,))
    r = R(op("import", enc("SkyyCfgTest", "_mod=SkyyCfgTest\nbazaar.spread=0.2\nbank.interestPercent=500\n"), A, "Skyy", "apply"))
    check(r[0] == "bad" and get("bazaar.spread") == "0.1" and get("bank.interestPercent") == "9", "one bad value -> nothing applied %s" % (r,))
    r = R(op("import", enc("SkyyCfgTest", "_mod=SkyyCfgTest\nfoo.bar=1\nbazaar.spread=0.2\n"), A, "Skyy", "apply"))
    check(r[0] == "ok" and get("bazaar.spread") == "0.2" and "Skipped (not known or read-only here): foo.bar" in r[2], "unknown key skipped and listed %s" % (r,))
    r = R(op("import", enc("SkyyCfgTest", "_mod=SkyyCfgTest\n_table=xp.block\nxp.block[Ore_Iron]=Mining|1\n"), A, "Skyy", "preview"))
    check(r[0] == "ok" and "Ore_Copper removed" in r[2] and "Ore_Gold removed" in r[2], "a table in a code replaces the whole table %s" % (r,))
    print("I. export / import done")

    # ---------------- J. (8.2 i) table ops + log format + rotation
    r = R(op("add", "xp.block", "Wood_Oak_Trunk", "Foraging|4", A, "Skyy", ""))
    check(r[0] == "ok", "table add %s" % (r,))
    r = R(op("tset", "xp.block", "Wood_Oak_Trunk", "Foraging|9", A, "Skyy", ""))
    check(r[0] == "ok" and r[1] == "Foraging|9", "table tset %s" % (r,))
    check(R(op("add", "xp.block", "Wood_Oak_Trunk", "Foraging|1", A, "Skyy", ""))[0] == "bad", "add of an existing entry refused")
    check(R(op("add", "xp.block", "Nope_Block", "Mining|1", A, "Skyy", ""))[2] == "Unknown item: Nope_Block.", "entry=item checked")
    check(R(op("tset", "xp.block", "Ore_Iron", "Mining", A, "Skyy", ""))[0] == "bad", "column count checked")
    check(R(op("tset", "xp.block", "Ore_Iron", "Min:ing|3", A, "Skyy", ""))[0] == "bad", "separator refused inside a column")
    k = op("keys", "xp.block", "oak")
    check(list(k[0]) == ["Wood_Oak_Trunk"] and list(k[2]) == ["Foraging|9"], "keys with a filter")
    r = R(op("remove", "xp.block", "Wood_Oak_Trunk", A, "Skyy", ""))
    check(r[0] == "ok", "table remove %s" % (r,))
    Pub.flush()
    L = logs()
    tl = [l for l in L if "\txp.block[Wood_Oak_Trunk]\t" in l]
    check(len(tl) == 3 and tl[2].split("\t")[5:8] == ["(none)", "Foraging|4", "ok"] and tl[1].split("\t")[5:7] == ["Foraging|4", "Foraging|9"]
          and tl[0].split("\t")[5:7] == ["Foraging|9", "(none)"], "table log lines in the 1.4.6 form: %s" % tl)
    f = tl[0].split("\t")
    r = R(op("add", "xp.block", f[4][len("xp.block["):-1], f[5], A, "Skyy", "yes", "undo"))
    Pub.flush()
    check(r[0] == "ok" and "block.Wood_Oak_Trunk=Foraging:9" in ftext(xpp).split("\r\n") and "\tundo\txp.block[Wood_Oak_Trunk]\t(none)\tForaging|9\tok" in logs()[0],
          "inverse op from the log line restores the entry exactly")
    check(all(len(l.split("\t")) == 8 and re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in logs()), "every log line has 8 tab fields and a time")
    lp = os.path.join(home, "config-changes.log")
    open(lp, "ab").write(("x" * 1023 + "\n").encode() * 1030)
    setv("bank.interestPercent", "33")
    Pub.flush()
    check(os.path.exists(lp + ".1") and os.path.getsize(lp) < 4096 and os.path.getsize(lp + ".1") > 1048576, "log rotated at 1 MB")
    check(len(logs()) == 200, "log op reads across the rotation")
    # a custom: table (the mod keeps the entries, the kit validates, confirms, logs and writes the lines customSet returns)
    check(list(op("keys", "coins.tags", "")[0]) == [], "custom table starts empty")
    r = R(op("add", "coins.tags", "gold", "Shiny|1", A, "Skyy", ""))
    check(r[0] == "confirm" and r[2].startswith("Add gold to Tags (Shiny / 1)?"), "custom table danger add asks %s" % (r,))
    check(R(op("add", "coins.tags", "gold", "Shiny|1", A, "Skyy", "yes"))[0] == "ok", "custom table add")
    r = R(op("tset", "coins.tags", "gold", "Shiny|2", A, "Skyy", "yes"))
    k = op("keys", "coins.tags", "")
    check(r[0] == "ok" and list(k[0]) == ["gold"] and list(k[2]) == ["Shiny|2"], "custom table tset + keys %s" % (r,))
    Pub.flush()
    check("tag.gold=Shiny:2" in ftext(cfgp).split("\n"), "custom table line written")
    check(R(op("remove", "coins.tags", "gold", A, "Skyy", "yes"))[0] == "ok", "custom table remove")
    Pub.flush()
    check("tag.gold" not in ftext(cfgp) and [l.split("\t")[5:7] for l in logs() if "\tcoins.tags[gold]\t" in l] ==
          [["Shiny|2", "(none)"], ["Shiny|1", "Shiny|2"], ["(none)", "Shiny|1"]], "custom table: line removed, 3 log lines in the table form")
    # restore of a file that holds a table (key family): the version before the undo lacks Wood_Oak_Trunk
    xv = [str(v) for v in op("versions") if str(v).split("\t")[1] == FILES[1]][0].split("\t")[0]
    r = R(op("restore", xv, A, "Skyy", "preview"))
    check(r[0] == "ok" and "Block XP: Wood_Oak_Trunk removed" in r[2], "table restore preview %s" % (r,))
    r = R(op("restore", xv, A, "Skyy", "apply"))
    settle()
    check(r[0] == "ok" and not any(l.startswith("block.Wood_Oak_Trunk=") for l in ftext(xpp).split("\r\n")), "table restore applied %s" % (r,))
    print("J. tables + log done")

    # ---------------- K. (8.2 j) the real effect
    r = setv("party.inviteSeconds", "90")
    Pub.flush()
    check(r[0] == "ok" and TestCfg.INVITE_MS == 90000 and get("party.inviteSeconds") == "90" and "inviteSeconds=90" in ftext(cfgp).split("\n"),
          "inviteSeconds 90 -> field 90000 ms, get 90, file 90")
    TestCfg.INVITE_MS = 1
    TestCfg.load()
    check(TestCfg.INVITE_MS == 90000, "the mod's own load reads 90000 again")
    r = setv("visit.notify", "false")
    Pub.flush()
    check(r[0] == "ok" and "defaults.visit.notify=0" in ftext(cfgp).split("\n") and TestCfg.NOTIFY == 0, "01 bool writes 0")
    TestCfg.NOTIFY = 1
    TestCfg.load()
    check(TestCfg.NOTIFY == 0 and get("visit.notify") == "false", "the mod's 'anything except 0 is on' parser reads it back as off")
    r = setv("xp.quiet", "on")
    Pub.flush()
    check(r[0] == "ok" and "quiet=1" in ftext(xpp).splitlines() and get("xp.quiet") == "true", "01 reload row: absent = its default OFF, set ON writes 1")
    print("K. real effect done")

    # ---------------- L. (8.2 h) 8 threads x 5,000 mixed ops
    System.setOut(JClass("java.io.PrintStream")(JClass("java.io.OutputStream").nullOutputStream()))
    runners = [Stress(s, 5000) for s in range(8)]
    threads = [Thread(x) for x in runners]
    t0 = time.time()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    System.setOut(old_out)
    settle()
    time.sleep(0.6)
    settle()
    done = sum(x.done for x in runners)
    errs = sum(x.errors for x in runners)
    check(errs == 0, "stress: %d errors (last: %s)" % (errs, [str(x.last) for x in runners if x.last is not None][:1]))
    pr, xr = fprops(cfgp), fprops(xpp)
    check(str(pr.getProperty("interestPercent")) == get("bank.interestPercent") and int(get("bank.interestPercent")) == TestCfg.PERCENT, "stress: file = memory (interest)")
    check(str(pr.getProperty("inviteSeconds")) == get("party.inviteSeconds") and int(get("party.inviteSeconds")) * 1000 == TestCfg.INVITE_MS, "stress: file = memory (invite)")
    check(str(xr.getProperty("multiplier")) == get("xp.multiplier") and abs(TestCfg.XPMULT - float(get("xp.multiplier"))) < 1e-9, "stress: file = memory = reloaded (multiplier)")
    check(str(xr.getProperty("block.Ore_Iron")).replace(":", "|") == str(op("keys", "xp.block", "Ore_Iron")[2][0]), "stress: file = memory (table)")
    sums = [str(v).split("\t")[4] for v in op("versions")]
    bad_sums = [x for x in sums if not re.match(r"^before (\S+ changed ([A-Za-z0-9._\[\]-]+|[23] settings)|(import|restore|undo) by \S+)$", x)]
    check(not bad_sums, "history summaries name the setting or count distinct settings: %s" % bad_sums[:3])
    print("L. stress: %d ops in %.1f s on 8 threads, %d errors" % (done, time.time() - t0, errs))

    # ---------------- M. the real permission / item paths (SkyyCfgPlain: PermissionsModule and Item are not running in a bare JVM)
    P2 = "com.skyy.cfgplain."
    ph = os.path.join(mods, "Skyy_SkyyCfgPlain")
    os.makedirs(ph)
    open(os.path.join(ph, "config.properties"), "w").write("# plain\nlimit=5\n")
    JClass(P2 + "CfgPub").start(Paths.get(mods), None)
    fn2 = bridge.get("config:fn:SkyyCfgPlain")

    def op2(*args):
        a = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            a[i] = x
        return fn2.apply(a)

    check(str(op2("set", "limit", "7", A, "Skyy", "", "menu")[0]) == "denied", "PermissionsModule unavailable -> denied (false on any error)")
    check(str(op2("set", "limit", "7", None, None, "", "command")[0]) == "denied", "null who via command denied (real PermissionsModule path)")
    check(str(op2("set", "limit", "7", None, None, "", "console")[0]) == "ok" and JClass(P2 + "PlainCfg").LIMIT == 7, "console via console works")
    check(str(op2("set", "kit", "Food_Bread", None, None, "", "console")[2]) == "Unknown item: Food_Bread.", "item check fails closed without the asset map")
    JClass(P2 + "CfgPub").flush()
    pp = os.path.join(ph, "config.properties")
    open(pp, "w").write("# plain\nlimit=99\n")
    os.utime(pp, (time.time(), time.time() + 20))
    check(str(op2("reload", None, None, "command")[0]) == "denied", "reload with null who via command denied")
    r = R(op2("reload", None, None, "console"))
    JClass(P2 + "CfgPub").flush()
    check(r[0] == "ok" and JClass(P2 + "PlainCfg").LIMIT == 50, "no reload routine: the kit clamps a hand edit (99 -> 50) %s" % (r,))
    l2 = [str(x) for x in op2("log", Integer.valueOf(5))]
    check(any(l.endswith("\tfile\tlimit\t7\t99\tok") for l in l2) and any(l.endswith("\tfile\tlimit\t99\t50\tclamped") for l in l2),
          "kit clamp logged as hand edit + clamp: %s" % l2[:2])
    print("M. plain sample done")

    # ---------------- O. a file deleted by hand: reload = back to defaults; the next write recreates it from the DEFAULTS text
    Pub.flush()
    os.remove(xpp)
    r = R(op("reload", A, "Skyy"))
    settle()
    check(r[0] == "ok" and get("xp.multiplier") == "1" and TestCfg.XPMULT == 1.0 and not os.path.exists(xpp), "deleted file reads as defaults %s" % (r,))
    setv("xp.multiplier", "3")
    settle()
    xt = ftext(xpp) if os.path.exists(xpp) else ""
    check(xt.startswith("# XP config") and "multiplier=3" in xt.splitlines() and "block.Ore_Iron=Mining:5" in xt.splitlines()
          and xt.count("\r\n") == xt.count("\n"), "recreated from DEFAULTS + the change, CRLF kept: %r" % xt[:80])
    L = logs()
    check(any("\tfile\txp.multiplier\t" in l and l.endswith("\t1\tok") for l in L), "the deletion is logged via=file (back to the default)")
    check(TestCfg.XPMULT == 3.0, "reload routine ran on the recreated file")
    print("O. deleted file done")

    # ---------------- P. restart rows bound reload: and restart tables never run the reload routine; confirm=never; check= on actions
    settle()
    s0 = [str(x) for x in op("status")]
    n0 = int(s0[1].split(" ")[0]) if s0[0] == "restart" else 0
    r0 = TestCfg.RELOADS
    r = setv("xp.startBonus", "5", confirm="")
    settle()
    check(r[0] == "restart" and "after a server restart" in r[2] and get("xp.startBonus") == "5" and "startBonus=5" in ftext(xpp).splitlines(),
          "restart reload row: saved, answers restart %s" % (r,))
    check(TestCfg.RELOADS == r0, "restart reload row: the reload routine did NOT run (%d -> %d)" % (r0, TestCfg.RELOADS))
    r = R(op("add", "xp.alias", "sp", "spawn", A, "Skyy", ""))
    settle()
    check(r[0] == "restart" and r[2] == "Command aliases: sp added (spawn) - saved, applies after a server restart."
          and "alias.sp=spawn" in ftext(xpp).splitlines(), "restart table add: danger + confirm=never asks nothing, answers restart %s" % (r,))
    check(TestCfg.RELOADS == r0, "restart table: the reload routine did NOT run")
    check(any(l.endswith("\txp.alias[sp]\t(none)\tspawn\trestart") for l in logs()), "restart table change logged status=restart")
    s = [str(x) for x in op("status")]
    check(s[0] == "restart" and s[1].startswith("%d change" % (n0 + 2)), "status counts the restart row and the restart table %s (was %s)" % (s, s0))
    t = ftext(xpp).replace("alias.sp=spawn", "alias.sp=home")
    open(xpp, "wb").write(t.encode("latin-1"))
    st_ = os.stat(xpp)
    os.utime(xpp, (st_.st_atime, st_.st_mtime + 30))
    R(op("reload", A, "Skyy"))
    settle()
    check(TestCfg.RELOADS == r0 and any("\tfile\txp.alias[sp]\tspawn\thome\tok" in l for l in logs()),
          "hand edit of a restart table: logged via=file, reload routine not run")
    r = R(op("action", "tools.purge", A, "Skyy", ""))
    check(r == ("confirm", None, "Purge every cached value?") and TestCust.PURGES == 0, "action check= ?question asks (no danger flag) %s" % (r,))
    r = R(op("action", "tools.purge", A, "Skyy", "yes"))
    check(r == ("ok", "", "Purged.") and TestCust.PURGES == 1, "action with yes runs %s" % (r,))
    TestCust.PURGEBLOCK = True
    r = R(op("action", "tools.purge", A, "Skyy", "yes"))
    check(r == ("bad", None, "A purge is already running.") and TestCust.PURGES == 1, "action check= refusal is bad and the action does not run %s" % (r,))
    TestCust.PURGEBLOCK = False
    check(R(op("action", "tools.purge", Bp, "B", "yes"))[0] == "denied" and TestCust.PURGES == 1, "action with check= still needs the node")
    print("P. restart reload rows, confirm=never, action check= done")

    # ---------------- N. status / versions / log shapes
    s = [str(x) for x in op("status")]
    check(s[0] in ("ok", "restart") and len(s) == 2, "status shape %s" % s)
    lg = op("log", Integer.valueOf(3))
    check(len(lg) == 3, "log max honoured")
    Pub.shutdown()
    print("N. shapes done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    os.makedirs(SCRATCH, exist_ok=True)
    jar = build()
    env = dict(os.environ)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", jar, "--dir", SCRATCH], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("skyycfg harness:", "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
