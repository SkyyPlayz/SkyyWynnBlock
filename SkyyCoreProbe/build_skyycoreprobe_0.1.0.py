"""SkyyCoreProbe 0.1.0 + SkyyDepProbe 0.1.0 - build script (javassist via jpype). PHASE 0 of research/Architecture-Spec.md (2.3 probes
C1-C4): can one Skyy jar (a future SkyyCore library) export classes + assets that another Skyy jar declares as a manifest dependency?
A THROWAWAY dev / test pair: NOT in tools/deploy_set.py SET, pinned for ONE Skyy test session, then removed.

Run:   python SkyyCoreProbe/build_skyycoreprobe_0.1.0.py   -> SkyyCoreProbe/SkyyCoreProbe-0.1.0.jar + SkyyDepProbe/SkyyDepProbe-0.1.0.jar
       (no --deploy on purpose)
Check: python SkyyCoreProbe/test_skyycoreprobe_0.1.0.py    (bare JVM with -Xverify:all, a bridge class-loader stand-in, engine parse
       of both manifests + both semver range syntaxes, page / texture / command checks)

FOR SKYY'S TEST (the MAIN session does this, game CLOSED, after python tools/backup_deploy.py - the probes are not in the SET, so
deploy_set.py never copies them):
  1. copy SkyyCoreProbe/SkyyCoreProbe-0.1.0.jar -> %APPDATA%/Hytale/UserData/Mods/SkyyCoreProbe.jar
     copy SkyyDepProbe/SkyyDepProbe-0.1.0.jar   -> %APPDATA%/Hytale/UserData/Mods/SkyyDepProbe.jar
  2. switch both on in the test world: python -c "import sys; sys.path.insert(0,'tools'); import skyybuild as B, deploy_set as D;
     B.enable_in_world(D.WORLD, 'Skyy:SkyyCoreProbe'); B.enable_in_world(D.WORLD, 'Skyy:SkyyDepProbe')"
     (STABLE keys: no version in the key - spec question 1 default, used here for the probes only; no disable_prefix needed)
  3. after the test: delete both jars from Mods (Recycle Bin) and set both keys Enabled false (or leave them off).

STABLE-NAME MANIFESTS (spec 7 question 1, default "drop the version from the display name" - probes only): Name "SkyyCoreProbe" /
"SkyyDepProbe", the version only in the Version field, so the plugin identifier and the world config key are "Skyy:SkyyCoreProbe" /
"Skyy:SkyyDepProbe" and the dependency can name Core.

THE TWO JARS
  SkyyCoreProbe-0.1.0.jar (plugin + asset pack, package com.skyy.coreprobe): exports CoreApi (static hello / add / bump / version) and
      CoreBox (a class with a constructor + an instance method); ships Common/UI/Custom/SkyyKit/Probe@2x.png - a texture drawn HERE
      by code (gold frame, "CORE" / "OK" on dark blue; no vanilla art); markup path "SkyyKit/Probe.png". Its setup() publishes
      skyy.bridge "coreprobe:core" (version), "coreprobe:boxclass" (its own CoreBox Class object) and appends "core" to
      "coreprobe:order", then prints "[SkyyCoreProbe] 0.1.0 ready".
  SkyyDepProbe-0.1.0.jar (plugin, no assets, package com.skyy.depprobe): manifest "Dependencies": {"Skyy:SkyyCoreProbe": ">=0.1.0 <1.0.0"}.
      ONE class (DepCalls) references Core's classes directly; everything else reaches it only through a try / catch(Throwable)
      call, because on Hytale 0.7.2 a plugin whose setup() throws (or that fails to load) SHUTS THE SERVER DOWN (MOD_ERROR) unless
      --ignore-broken-mods - a C1 failure must stay a log line, never a dead world.
      setup(): C1 (CoreApi.hello / add / bump, new CoreBox(..).describe(), "same Class object as Core published?"), C2 (manifest
      Name, identifier = world config key + its Enabled value from the server config, the engine's base permission, Dependencies),
      C3 server side (does our class loader see Core's texture resource through the bridge?), C4 (setup order seen on the bridge) ->
      every result as a "[SkyyDepProbe] C<n> ..." log line; registers /coreprobe; prints "[SkyyDepProbe] 0.1.0 ready".
      /coreprobe (admin: requirePermission skyydepprobe.admin + no permission groups, like the other probes): re-runs C1 live and
      prints C1-C4 to chat AND the log, then opens the C3 page (inline, vanilla kit look) whose picture is Core's texture.

ENGINE FACTS RE-READ FROM HytaleServer.jar 0.7.2 (cached copy via tools/serverjar.py; Implementation-Version 0.7.2) - the spec's 2.2
table was read from 0.6.8:
  * PluginManifest CODEC keys: Group, Name, Version, Description, Authors, Website, Main, ServerVersion, Dependencies,
    OptionalDependencies, LoadBefore, DisabledByDefault, IncludesAssetPack, SubPlugins. Dependencies = ObjectMapCodec: a JSON object
    "<Group>:<Name>" (PluginIdentifier.fromString, "String does not match <group>:<name>") -> SemverRange string.
  * SemverRange syntax (SemverRangeCodec schema text): *, >=0.5.0, 0.5.x, ^0.5.0, >=0.5.0 <0.6.0, 1.0.0 || ^2.0.0, a - b, ~x. A bare
    version is refused unless its patch is 0 ("Bare version '' is not a valid range. Use '=' for an exact match, or '^' / '~'").
  * PluginManager.setup(): every pending plugin goes through validatePluginDeps; a missing dependency throws
    MissingPluginDependencyException "Failed to load '%s' because the dependency '%s' could not be found!" (wrong version: "...because
    version of dependency '%s'(%s) does not satisfy '%s'!"), logged SEVERE, and the plugin is DROPPED from the pending set - it is not a
    "failed" plugin, so the server keeps booting. (ModLoadOrderException MISSING_DEPENDENCY in Mod.calculateLoadOrder is only hit when a
    dependency vanishes between the two steps.) A plugin disabled in the config is skipped before that ("Skipping mod %s (Disabled by
    server config)"), so "Core disabled" = "Core missing" for its dependents.
  * NEW in 0.7: a plugin that fails to LOAD (no main class, ...), or whose setup() / start() fails, shuts the server down
    (ShutdownReason MOD_ERROR, "client.disconnection.shutdownReason.pluginError.detail") unless --ignore-broken-mods; a Mods config entry
    with a "RequiredVersion" whose plugin is missing shuts it down too ("Failed to start server! Missing Mods:").
  * PluginClassLoader.loadClass0: server classes, then the plugin's own jar, then PluginBridgeClassLoader.loadClass0(name, pcl, manifest):
    the plugins named in Dependencies, then OptionalDependencies, then EVERY other loaded plugin (tryGetClass -> loadLocalClass). So a
    plugin can link against another plugin's classes at run time even without declaring it (only load order is then not guaranteed).
    PluginManager.DISABLE_DYNAMIC_DEPENDENCIES is AssetStore.DISABLE_DYNAMIC_DEPENDENCIES (asset store, cleared around setup0) - it has
    nothing to do with class loading. getResource / getResources walk the same bridge (bridgeResources).
  * PluginBase.createBasePermission = (Group + "." + Name).toLowerCase(ROOT).replace(' ', '_'); AbstractCommand.generatePermission =
    base + ".command." + <name>. Today "Skyy" + "0.3.26 SkyyMenu" -> skyy.0.3.26_skyymenu.command.menu (version inside); with a stable
    Name -> skyy.skyydepprobe.command.<name>.
  * PluginIdentifier.toString = Group + ":" + Name = the key of the server / world config "Mods" map (ModConfig: Enabled, RequiredVersion).
"""
import sys, os, json, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI
import skyyart as SA
import serverjar

if "--deploy" in sys.argv:
    raise SystemExit("SkyyCoreProbe: --deploy is not supported - the main session copies the probes for Skyy's test (see the header)")

VERSION = "0.1.0"
RANGE = ">=0.1.0 <1.0.0"            # the Dependencies range (the test script also parses "^0.1.0" with the engine)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyCoreProbe")
HERE_D = os.path.join(ROOT, "SkyyDepProbe")
os.makedirs(HERE_D, exist_ok=True)
CORE_ID, DEP_ID = "Skyy:SkyyCoreProbe", "Skyy:SkyyDepProbe"
NODE = "skyydepprobe.admin"
CMD = "coreprobe"
TEX_JAR = "Common/UI/Custom/SkyyKit/Probe@2x.png"     # inline texture root is Common/UI/Custom/ ; the client loads the @2x file
TEX_MARKUP = "SkyyKit/Probe.png"
TEX_UI_W, TEX_UI_H = 256, 128                         # UI units; the PNG is 2x (512 x 256 px)

# ================= the texture (drawn here, deterministic; no vanilla pixels) =================
GLYPH = {   # 5 x 7 pixel letters
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
}


def hexc(s, a=255):
    return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16), a)


def draw_texture():
    w, h = TEX_UI_W * 2, TEX_UI_H * 2
    img = SA.Img(w, h)
    navy_top, navy_bot = hexc("#14284a"), hexc("#0a1428")         # ui-data (texture pixels)
    gold, gold_dark, gold_light = hexc("#e0b040"), hexc("#7a5a14"), hexc("#ffe08a")   # ui-data (texture pixels)
    white, green = hexc("#f4f8ff"), hexc("#46d46a")                # ui-data (texture pixels)
    for y in range(h):
        t = y / float(h - 1)
        row = tuple(int(round(navy_top[i] * (1 - t) + navy_bot[i] * t)) for i in range(3)) + (255,)
        for x in range(w):
            img.put(x, y, row)
    for y in range(h):                                             # 12 px frame: dark rim, gold body, light inner line
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            if d < 2:
                img.put(x, y, gold_dark)
            elif d < 10:
                img.put(x, y, gold)
            elif d < 12:
                img.put(x, y, gold_light)

    def text(s, top, scale, col):
        gw = 5 * scale + scale                                     # glyph + one column gap
        x0 = (w - (len(s) * gw - scale)) // 2
        for i, ch in enumerate(s):
            for gy, line in enumerate(GLYPH[ch]):
                for gx, bit in enumerate(line):
                    if bit == "1":
                        for yy in range(scale):
                            for xx in range(scale):
                                img.put(x0 + i * gw + gx * scale + xx, top + gy * scale + yy, col)
    text("CORE", 40, 12, white)                                    # 84 px high
    text("OK", 148, 9, green)                                      # 63 px high
    return SA.png_encode(img)


TEX_PNG = draw_texture()
assert SA.png_size(TEX_PNG) == (TEX_UI_W * 2, TEX_UI_H * 2)
assert draw_texture() == TEX_PNG, "the texture generator is deterministic"
ASSETS = serverjar.assets_zip()
with zipfile.ZipFile(ASSETS) as _az:
    assert TEX_JAR not in set(_az.namelist()), "the probe texture path exists in Assets.zip"
print("texture %s: %d x %d px, %d bytes" % (TEX_JAR, TEX_UI_W * 2, TEX_UI_H * 2, len(TEX_PNG)))

# ================= the C3 page (inline only, the shared vanilla kit) =================
SUI.verify(assets_zip=ASSETS)
P = "Cpr"
PAGE_W = 760
ONE = "C3: the picture below ships ONLY inside SkyyCoreProbe's jar."
HINT = ("A gold frame with CORE and OK on dark blue = C3 passed. An empty box, or the client log line 'could not find texture' "
        "naming SkyyKit/Probe.png = C3 failed.")
C1_ID, C2_ID, CLOSE_ID = P + "C1", P + "C2", P + "Close"
LINE_PX = 21


def text_h(text, w, size=16):
    return SUI.text_lines(text, w - 4, size) * LINE_PX + 4


C1_SAMPLE = "C1 cross-jar class: PASS - CoreApi + CoreBox from SkyyCoreProbe work, one class copy."
C2_SAMPLE = "C2 stable names: PASS - key Skyy:SkyyDepProbe Enabled=true, base permission skyy.skyydepprobe"


def page(page_h=None):
    sh = SUI.page_shell(P, PAGE_W, page_h or SUI.MAX_PAGE_H, "Core probe", kind="decorated")
    ap, body, w = sh.appends, sh.body, sh.inner_w
    ap.text(body, P + "One", ONE, "strong", h=26, w=w)
    ap.append((body, SUI.spacer(h=8)))
    ap.append((body, "Group #%s { Anchor: (Height: %d); LayoutMode: Left; }" % (P + "PicRow", TEX_UI_H)))
    ap.append((P + "PicRow", SUI.spacer(w=(w - TEX_UI_W) // 2)))
    ap.append((P + "PicRow", 'Group #%s { Anchor: (Width: %d, Height: %d); Background: "%s"; }' % (P + "Pic", TEX_UI_W, TEX_UI_H,
                                                                                                  TEX_MARKUP)))
    ap.append((body, SUI.spacer(h=8)))
    ap.text(body, P + "Hint", HINT, "default", h=text_h(HINT, w), w=w, wrap=True)
    ap.append((body, SUI.spacer(h=6)))
    ap.append((body, SUI.label(C1_ID, "", "default", h=text_h(C1_SAMPLE, w), w=w, wrap=True)))
    ap.append((body, SUI.label(C2_ID, "", "default", h=text_h(C2_SAMPLE, w) + LINE_PX, w=w, wrap=True)))
    ap.append((body, "Group #%s { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 8); }" % (P + "Nav", SUI.BTN_H + 8)))
    ap.append((P + "Nav", SUI.spacer(w=(w - 170) // 2)))
    ap.append((P + "Nav", SUI.button(CLOSE_ID, "Close", "secondary", w=170)))
    return sh, ap, SUI.used_height(ap, body)


_sh, _ap, _used = page()
PAGE_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + _used + 4
SH, AP, _u2 = page(PAGE_H)
assert _u2 == _used
_chk = SUI.Appends(AP)
_chk.sets = list(AP.sets) + list(SH.sets)
SUI.check_page(_chk, P)
SUI.assert_page_size(SH.w, SH.h)
_toks = SUI.assert_proven(_chk, allow=(), what="core probe page")
assert all(g is None for g in _toks.values()), _toks
PAGE_JAVA = SH.appends.java("b", sets=list(SH.sets))
assert TEX_MARKUP in PAGE_JAVA, "the page names Core's texture"
print("page: %d x %d px, %d appends, %d b.set lines" % (SH.w, SH.h, len(AP), len(AP.sets) + len(SH.sets)))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT_C = B.class_out(HERE)
OUT_D = B.class_out(HERE_D)
PKG_C, PKG_D = "com.skyy.coreprobe", "com.skyy.depprobe"
T = {
    "PKC": PKG_C, "PKD": PKG_D, "VERSION": VERSION, "NODE": NODE, "CMD": CMD, "TEXJAR": TEX_JAR, "COREID": CORE_ID,
    "DEPID": DEP_ID, "RANGE": RANGE, "C1ID": C1_ID, "C2ID": C2_ID, "CLOSEID": CLOSE_ID,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PB": "com.hypixel.hytale.server.core.plugin.PluginBase",
    "MAN": "com.hypixel.hytale.common.plugin.PluginManifest",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "MCF": "com.hypixel.hytale.server.core.config.ModConfig",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
}
for c, m in ((T["PB"], "getLogger"), (T["PB"], "getCommandRegistry"), (T["PB"], "getIdentifier"), (T["PB"], "getManifest"),
             (T["PB"], "getBasePermission"), (T["MAN"], "getName"), (T["MAN"], "getVersion"), (T["MAN"], "getDependencies"),
             (T["HSV"], "get"), (T["HSV"], "getConfig"), ("com.hypixel.hytale.server.core.HytaleServerConfig", "getModConfig"),
             (T["MCF"], "getEnabled"), (T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["PR"], "sendMessage"),
             (T["PR"], "getUsername"), (T["MSG"], "raw"), (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"), (T["PAGE"], "build"),
             (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["LIFE"], "CanDismiss"), (T["UCB"], "appendInline"),
             (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["BT"], "Activating"),
             ("com.hypixel.hytale.component.Store", "getComponent")):
    B.probe(pool, c, m)
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(pkg, name, sup=None):
    return pool.makeClass(pkg + "." + name, pool.get(sup)) if sup else pool.makeClass(pkg + "." + name)


def jl(s):
    return json.dumps(s)


BRIDGE = r"""
public static java.util.Map bridge() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) {
    System.getProperties().putIfAbsent("skyy.bridge", new java.util.concurrent.ConcurrentHashMap());
    o = System.getProperties().get("skyy.bridge");
  }
  return (o instanceof java.util.Map) ? (java.util.Map) o : null;
}"""
ORDER = r"""
public static void order(String who) {
  java.util.Map m = bridge();
  if (m == null) return;
  Object o = m.get("coreprobe:order");
  m.put("coreprobe:order", o == null ? who : String.valueOf(o) + "," + who);
}"""

# ---------------- SkyyCoreProbe: the exported API (CoreApi static methods + the CoreBox class) ----------------
api = mk(PKG_C, "CoreApi")
F(api, "public static volatile int calls;")
M(api, 'public static String version() { return "@VERSION@"; }')
M(api, 'public static String hello(String who) { return "SkyyCoreProbe " + version() + " says hello to " + who; }')
M(api, "public static int add(int a, int b) { return a + b; }")
M(api, "public static int bump() { calls = calls + 1; return calls; }")
box = mk(PKG_C, "CoreBox")
F(box, "public String tag;")
C(box, "public CoreBox(String tag) { this.tag = tag; }")
M(box, r"""
public String describe() {
  ClassLoader cl = getClass().getClassLoader();
  return "CoreBox(" + this.tag + ") from " + (cl == null ? "boot" : (cl.getName() != null ? cl.getName() : String.valueOf(cl)));
}""")
cpl = mk(PKG_C, "SkyyCoreProbePlugin", T["JP"])
C(cpl, "public SkyyCoreProbePlugin(@JPI@ init) { super(init); }")
M(cpl, BRIDGE)
M(cpl, ORDER)
M(cpl, r"""
public void setup() {
  String pub = "published";
  try {
    java.util.Map m = bridge();
    if (m == null) pub = "NOT published (skyy.bridge is not a Map)";
    else {
      m.put("coreprobe:core", "SkyyCoreProbe @VERSION@");
      m.put("coreprobe:boxclass", new @PKC@.CoreBox("published").getClass());
    }
    order("core");
  } catch (Throwable t) { pub = "NOT published: " + t; }
  String res = "?";
  try {
    java.net.URL u = getClass().getClassLoader().getResource("@TEXJAR@");
    res = u == null ? "MISSING from the jar" : "in the jar";
  } catch (Throwable t) { res = "unreadable: " + t; }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCoreProbe] @VERSION@ ready - library probe for SkyyDepProbe (C1: exports CoreApi + CoreBox, bridge keys " + pub + "; C3: texture SkyyKit/Probe.png " + res + ")");
}""")
M(cpl, "protected void shutdown() { super.shutdown(); }")
CORE_CLASSES = [api, box, cpl]
for c in CORE_CLASSES:
    c.writeFile(OUT_C)

# ---------------- SkyyDepProbe ----------------
log = mk(PKG_D, "DepLog")
F(log, "public static @LOG@ LOG;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyDepProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyDepProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String msg) {
  info(msg);
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyDepProbe] " + msg)); } catch (Throwable t) { }
}""")

# DepProbe: state + every probe that does NOT touch Core's classes (so a missing Core can never break plugin load / setup)
dp = mk(PKG_D, "DepProbe")
F(dp, 'public static volatile String C1SETUP = "not run";')
F(dp, 'public static volatile String C1SHORT = "not run";')
F(dp, 'public static volatile String C2 = "not run";')
F(dp, 'public static volatile String C3S = "not run";')
F(dp, 'public static volatile String ORDERSEEN = "";')
M(dp, BRIDGE)
M(dp, ORDER)
M(dp, r"""
public static Object bridgeGet(String k) {
  java.util.Map m = bridge();
  return m == null ? null : m.get(k);
}""")
dc = mk(PKG_D, "DepCalls")     # created now (DepProbe.runC1 names it); its body is compiled after DepProbe's helpers
# C1 short / long: DepCalls.c1() returns "PASS|FAIL<TAB>short<TAB>long"
M(dc, r"""
public static String c1() {
  String hello = @PKC@.CoreApi.hello("SkyyDepProbe");
  int sum = @PKC@.CoreApi.add(2, 3);
  int n = @PKC@.CoreApi.bump();
  @PKC@.CoreBox bx = new @PKC@.CoreBox("made-by-dep");
  String desc = bx.describe();
  Class mine = bx.getClass();
  Object pub = @PKD@.DepProbe.bridgeGet("coreprobe:boxclass");
  boolean one = pub != null && pub == mine;
  ClassLoader cl = mine.getClassLoader();
  ClassLoader own = @PKD@.DepCalls.class.getClassLoader();
  String cln = cl == null ? "boot" : (cl.getName() != null ? cl.getName() : String.valueOf(cl));
  String ownn = own == null ? "boot" : (own.getName() != null ? own.getName() : String.valueOf(own));
  boolean ok = hello.equals("SkyyCoreProbe @VERSION@ says hello to SkyyDepProbe") && sum == 5 && n > 0 && one && cl != own;
  String same = pub == null ? "Core published no CoreBox class (is SkyyCoreProbe's setup done?)" : (one ? "the same Class object Core published (one copy)" : "a DIFFERENT Class object than Core's (two copies)");
  String shortTxt = ok ? ("CoreApi + CoreBox from SkyyCoreProbe work in SkyyDepProbe; one class copy, loaded by " + cln) : ("hello='" + hello + "' add=" + sum + " box=" + same);
  String longTxt = "CoreApi.hello -> '" + hello + "', CoreApi.add(2,3) = " + sum + ", CoreApi.bump() = " + n + " (shared static), new CoreBox -> " + desc + "; " + same + "; CoreBox class loader " + cln + ", SkyyDepProbe's class loader " + ownn;
  return (ok ? "PASS" : "FAIL") + "\t" + shortTxt + "\t" + longTxt;
}""")
M(dp, r"""
public static String[] runC1() {
  String r = null;
  try { r = @PKD@.DepCalls.c1(); }
  catch (Throwable t) {
    String s = "FAIL\tSkyyCoreProbe's classes could not be used: " + t + "\t" + t;
    Throwable c = t.getCause();
    if (c != null) s = s + " <- " + c;
    r = s;
  }
  String[] p = r.split("\t", 3);
  if (p.length < 3) return new String[] { "FAIL", r, r };
  return p;
}""")
M(dp, r"""
public static String configOf(String key) {
  try {
    java.util.Map m = @HSV@.get().getConfig().getModConfig();
    if (m == null) return "no Mods map";
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (String.valueOf(e.getKey()).equals(key)) {
        Object v = e.getValue();
        if (v instanceof @MCF@) return String.valueOf(((@MCF@) v).getEnabled());
        return "entry " + v;
      }
    }
    return "no entry";
  } catch (Throwable t) { return "unreadable: " + t; }
}""")
M(dp, r"""
public static String c2(@PB@ p) {
  try {
    @MAN@ man = p.getManifest();
    String name = man.getName();
    String ver = String.valueOf(man.getVersion());
    String id = String.valueOf(p.getIdentifier());
    String base = p.getBasePermission();
    String en = configOf(id);
    String enCore = configOf("@COREID@");
    boolean ok = name.equals("SkyyDepProbe") && id.equals("@DEPID@") && base.equals("skyy.skyydepprobe") && en.equals("true") && enCore.equals("true");
    return (ok ? "PASS" : "CHECK") + " - manifest Name '" + name + "' (version " + ver + " only in Version), identifier = world config key '" + id + "' Enabled=" + en + " (Core '@COREID@' Enabled=" + enCore + "), engine base permission '" + base + "' so auto command nodes are '" + base + ".command.<name>' (no version; /@CMD@ itself uses @NODE@), Dependencies " + String.valueOf(man.getDependencies());
  } catch (Throwable t) { return "FAIL - " + t; }
}""")
M(dp, r"""
public static String c3server() {
  try {
    ClassLoader own = @PKD@.DepProbe.class.getClassLoader();
    java.net.URL u = own.getResource("@TEXJAR@");
    if (u == null) return "SkyyDepProbe's class loader does NOT see @TEXJAR@ (resources are not bridged) - the client test decides C3";
    String s = String.valueOf(u);
    return (s.indexOf("SkyyCoreProbe") >= 0 ? "Core's texture resource is visible from SkyyDepProbe through the plugin bridge: " : "texture resource found: ") + s;
  } catch (Throwable t) { return "resource check failed: " + t; }
}""")
M(dp, r"""
public static String c4() {
  String o = String.valueOf(bridgeGet("coreprobe:order"));
  return (o.indexOf("core") >= 0 && o.indexOf("core") < o.indexOf("dep") ? "Core is loaded and was set up BEFORE SkyyDepProbe" : "setup order NOT core-first") + " (bridge order '" + o + "'). Disabled-Core test: switch SkyyCoreProbe OFF in this world's Mods list and start the world - it must still load, /@CMD@ is then unknown, and the server log says: Failed to load '@DEPID@' because the dependency '@COREID@' could not be found!";
}""")
M(dp, r"""
public static void runSetup(@PB@ p) {
  order("dep");
  String[] c1 = runC1();
  C1SETUP = c1[0];
  C1SHORT = c1[0] + " - " + c1[1];
  C2 = c2(p);
  C3S = c3server();
  ORDERSEEN = String.valueOf(bridgeGet("coreprobe:order"));
  @PKD@.DepLog.info("C1 cross-jar class (setup): " + c1[0] + " - " + c1[2]);
  @PKD@.DepLog.info("C2 stable names: " + C2);
  @PKD@.DepLog.info("C3 Core asset pack, server side: " + C3S);
  @PKD@.DepLog.info("C4 dependency: " + c4());
}""")

# ---- the C3 page
pg = mk(PKG_D, "CoreProbePage", T["PAGE"])
F(pg, 'public String c1 = "";')
F(pg, 'public String c2 = "";')
C(pg, r"""
public CoreProbePage(@PR@ pr, String c1, String c2) {
  super(pr, @LIFE@.CanDismiss);
  this.c1 = c1;
  this.c2 = c2;
}""")
assert "@" not in PAGE_JAVA          # inline markup never holds @ (check_markup), so the token pass leaves it alone
M(pg, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n" + PAGE_JAVA + r"""
  b.set("#@C1ID@.Text", this.c1 == null ? "" : this.c1);
  b.set("#@C2ID@.Text", this.c2 == null ? "" : this.c2);
  ev.addEventBinding(@BT@.Activating, "#@CLOSEID@", @EVD@.of("a", "close"));
}""")
M(pg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data != null && data.indexOf("close") >= 0) {
      @PKD@.DepLog.info("C3 page closed by " + this.playerRef.getUsername());
      close();
    }
  } catch (Throwable t) { @PKD@.DepLog.warn("page click failed: " + t); }
}""")
M(pg, r"""
public static boolean open(@REF@ ref, @ST@ store, @PR@ pr, String c1, String c2) {
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKD@.DepLog.tell(pr, "C3: the page could not be opened (no player component)."); return false; }
  try {
    p.getPageManager().openCustomPage(ref, store, new @PKD@.CoreProbePage(pr, c1, c2));
  } catch (Throwable t) {
    @PKD@.DepLog.warn("C3: the page could not be opened: " + t);
    @PKD@.DepLog.tell(pr, "C3: the page could not be opened - see the server log.");
    return false;
  }
  @PKD@.DepLog.info("C3 page opened for " + pr.getUsername() + " (its picture is SkyyCoreProbe's SkyyKit/Probe.png)");
  return true;
}""")

# ---- /coreprobe (admin)
cmd = mk(PKG_D, "CoreProbeCmd", T["APC"])
C(cmd, r"""
public CoreProbeCmd() {
  super("@CMD@", "(admin) SkyyDepProbe: prints the SkyyCore probe results C1-C4 and opens the C3 page (throwaway dev pack)");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String[] c1 = @PKD@.DepProbe.runC1();
    String c1line = "C1 cross-jar class: " + c1[0] + " - " + c1[1] + " (at server start: " + @PKD@.DepProbe.C1SETUP + ")";
    String c2line = "C2 stable names: " + @PKD@.DepProbe.C2;
    @PKD@.DepLog.info("C1 live detail: " + c1[2]);
    @PKD@.DepLog.tell(pr, c1line);
    @PKD@.DepLog.tell(pr, c2line);
    @PKD@.DepLog.tell(pr, "C3 Core asset pack: opening the probe page - its picture comes only from SkyyCoreProbe's jar. Server side: " + @PKD@.DepProbe.C3S);
    @PKD@.DepLog.tell(pr, "C4 dependency: " + @PKD@.DepProbe.c4());
    @PKD@.CoreProbePage.open(ref, store, pr, c1line, c2line);
  } catch (Throwable t) {
    @PKD@.DepLog.warn("/@CMD@ failed: " + t);
    @PKD@.DepLog.tell(pr, "/@CMD@ failed - see the server log.");
  }
}""")

dpl = mk(PKG_D, "SkyyDepProbePlugin", T["JP"])
C(dpl, "public SkyyDepProbePlugin(@JPI@ init) { super(init); }")
M(dpl, r"""
public void setup() {
  @PKD@.DepLog.LOG = getLogger();
  try { @PKD@.DepProbe.runSetup(this); } catch (Throwable t) { @PKD@.DepLog.warn("probe setup problem: " + t); }
  try { getCommandRegistry().registerCommand(new @PKD@.CoreProbeCmd()); } catch (Throwable t) { @PKD@.DepLog.warn("/@CMD@ not registered: " + t); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyDepProbe] @VERSION@ ready - /@CMD@ (admin): SkyyCore probes C1-C4 to chat + log (manifest dependency @COREID@ @RANGE@; throwaway dev pack)");
}""")
M(dpl, "protected void shutdown() { super.shutdown(); }")
DEP_CLASSES = [log, dp, dc, pg, cmd, dpl]
for c in DEP_CLASSES:
    c.writeFile(OUT_D)
print("classes written: Core %d, Dep %d" % (len(CORE_CLASSES), len(DEP_CLASSES)))

# ================= manifests + jars =================
man_c = B.manifest("SkyyCoreProbe", VERSION, "SkyWynn THROWAWAY dev pack: the SkyyCore library probe (phase 0, C1-C4). Exports a class + a texture for SkyyDepProbe. Remove after the test session.", PKG_C + ".SkyyCoreProbePlugin")
man_d = B.manifest("SkyyDepProbe", VERSION, "SkyWynn THROWAWAY dev pack: depends on SkyyCoreProbe and uses its class + texture (/coreprobe, admin only). Remove after the test session.", PKG_D + ".SkyyDepProbePlugin")
for m_, nm in ((man_c, "SkyyCoreProbe"), (man_d, "SkyyDepProbe")):
    m_["Name"] = nm                     # STABLE name (spec question 1 default) - the version lives only in "Version"
man_d["IncludesAssetPack"] = False      # no assets of its own: the page's picture must come from Core
man_d["Dependencies"] = {CORE_ID: RANGE}
assert "%s:%s" % (man_c["Group"], man_c["Name"]) == CORE_ID and "%s:%s" % (man_d["Group"], man_d["Name"]) == DEP_ID
jar_c = os.path.join(HERE, "SkyyCoreProbe-%s.jar" % VERSION)
jar_d = os.path.join(HERE_D, "SkyyDepProbe-%s.jar" % VERSION)
B.assemble(jar_c, man_c, OUT_C, {TEX_JAR: TEX_PNG})
B.assemble(jar_d, man_d, OUT_D, {})
