"""SkyyHud 0.3.22 harness - PLAYERS ROUTE THEIR OWN MESSAGES + the Abilities message type (tools/hud_0_3_22_patch.py). Built on
tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the
scratch folder). The new checks run the REAL SkyyHud classes together with the REAL SkyyMenu 0.3.20 settings registry (SetReg / SetStore /
the settings:fn:* bridge Functions) - only the player is a stand-in.

    python SkyyHud/test_skyyhud_0.3.22.py [--jar SkyyHud-0.3.22.jar] [--old SkyyHud-0.3.21.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.21 -> 0.3.22: exactly the listed classes / members differ; non-class entries: the manifest
  X20 / X19 / Q / ST   EVERY check of the 0.3.21 harness (its x20, x19, quest and live phases) on THIS jar; the 0.3.20 E6 check that
       expected 20 switches with the node skyyhud.messages is eased (re-checked exactly in M2)
  M    messages M1 the "ability" kind: FeedCfg.KINDS / route / config line / Server Setup row (default Chat; a 0.3.21 file without the
                line = chat); M2 22 switches registered with SkyyMenu WITHOUT a node; M3 a NON-OP player sees all 22 rows on the settings
                tab (a node-gated control key stays hidden from them); M4 that player CHANGES their own routes through settings:fn:set
                (Chat / Feed / Off for ability and pickup; saved in their SkyyMenu settings file) and msgroute:fn:get answers them; a
                player who never chose = the server default; M5 the non-op CANNOT change the server defaults (Server Setup kit set =
                denied, nothing changes); the console can, and the players' registered default follows
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the /settings page itself (SkyyMenu draws it; 8 rows per page, the rows land on the General
tab because SkyyMenu 0.3.20 has no Messages tab).
Scratch: tools/dev/scratch/hudroute/hud (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, PREV = "0.3.22", "0.3.21"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
MENU_JAR = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hudroute", "hud")))
PKG = "com.skyy.hud."
MPKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
KINDS = ["pickup", "drop", "skillxp", "levelup", "coins", "collection", "rankup", "quest", "heal", "petxp", "ability"]
EXPECT = {}
ADDED = []


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t21():
    return load_module(os.path.join(HERE, "test_skyyhud_0.3.21.py"), "hud0321h")


def ease(out, rules, label):
    d = json.load(open(out))
    keep, eased = [], []
    for f in d["fails"]:
        if any(fr in f and cond(f) for fr, cond in rules):
            eased.append(f[:100])
        else:
            keep.append(f)
    d["fails"] = keep
    d["ok"] += len(eased)
    d.setdefault("notes", []).append("%s: %d check(s) eased for 0.3.22 (re-checked exactly in M): %s" % (label, len(eased), eased))
    json.dump(d, open(out, "w"), indent=1)


def run_x20(out, jar, scratch, home):
    t21().run_x20(out, jar, scratch, home)
    ease(out, [("E6: 20 switches registered", lambda f: True)], "X20")


REBUILD18 = r'''
import os, sys
src, d = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf8").read()
for a, b in (("OUT = B.class_out(HERE)", "OUT = B.class_out(%r)" % d), ('jar = os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)', "jar = os.path.join(%r, 'SkyyHud-0.3.18.jar')" % d)):
    assert t.count(a) == 1, a
    t = t.replace(a, b)
sys.argv = [src]
exec(compile(t, src, "exec"), {"__file__": src, "__name__": "__main__"})
'''


def old18(scratch):
    """the 0.3.19 exec checks compare with SkyyHud-0.3.18.jar, which the tidy-up removed: rebuild it from its own build script INTO the
    scratch folder (classes + jar there; SkyyHud/ untouched) in a separate process (one JVM per process)"""
    j = os.path.join(HERE, "SkyyHud-0.3.18.jar")
    if os.path.isfile(j):
        return j
    d = os.path.join(scratch, "old18")
    j = os.path.join(d, "SkyyHud-0.3.18.jar")
    if not os.path.isfile(j):
        import subprocess
        os.makedirs(d, exist_ok=True)
        subprocess.run([sys.executable, "-c", REBUILD18, os.path.join(HERE, "build_skyyhud_0.3.18.py"), d], check=True, stdout=subprocess.DEVNULL)
    return j


def run_x19(out, jar, scratch, home):
    sys.argv += ["--old", old18(scratch)]     # read by the 0.3.19 harness module (its OLD_JAR) when it is loaded below
    t21().run_x19(out, jar, scratch, home)


def run_quest(out, jar, scratch, home):
    t21().run_quest(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    t21().run_live(out, jar, scratch, home)


def run_msg(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, MENU_JAR, B.JAVASSIST], verify=True)
    UUID, System, CHM, Paths, Boolean = (JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"),
                                         JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"))
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                f.set(obj, val)
                return
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    def arr(*xs):
        return JArray(JObject)(list(xs))
    H = lambda n: JClass(PKG + n)
    M = lambda n: JClass(MPKG + n)
    LS, HM, Cfg, Plugin, Feed, FCfg = H("LayoutStore"), H("HudMain"), H("HudCfg"), H("SkyyHudPlugin"), H("Feed"), H("FeedCfg")
    SetReg, SetStore = M("SetReg"), M("SetStore")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "m")
    for d in ("cfg", "layouts", "settings", "old"):
        os.makedirs(os.path.join(work, d), exist_ok=True)
    LS.DIR = Paths.get(os.path.join(work, "layouts"))
    LS.CACHE.clear()
    # ================================================================================== M1 the ability kind
    Cfg.FILE = Paths.get(os.path.join(work, "old", "config.properties"))
    open(os.path.join(work, "old", "config.properties"), "w", encoding="latin-1").write("# a 0.3.21 file\ndefaultLayout=\nmsg.petxp=chat\n")
    FCfg.R_ABILITY = "feed"
    Cfg.load()
    K.eq((str(FCfg.R_ABILITY), str(FCfg.R_PETXP)), ("chat", "chat"), "M1 a 0.3.21 config.properties (no msg.ability line) = ability Chat; other lines as saved")
    Cfg.FILE = Paths.get(os.path.join(work, "cfg", "config.properties"))
    Cfg.load()
    ct = open(os.path.join(work, "cfg", "config.properties"), encoding="latin-1").read()
    K.check("msg.ability=chat" in ct and "msg.petxp=feed" in ct, "M1 a NEW config.properties carries msg.ability=chat")
    K.eq([str(x) for x in FCfg.KINDS], KINDS, "M1 the kinds (ability APPENDED)")
    K.eq((str(FCfg.route("ability")), FCfg.route("system")), ("chat", None), "M1 FeedCfg.route: ability = Chat by default, system = always chat (null)")
    K.eq(str(FCfg.SLABEL[10]), "Ability casts and results", "M1 the Server Setup label")
    Rows = H("CfgRows")
    ri = int(Rows.index("hud.msg.ability"))
    K.check(ri >= 0 and str(Rows.DEFS[ri]) == "chat", "M1 the Server Setup row hud.msg.ability exists, default chat (index %d)" % ri)
    nmsg = len([k for k in Rows.KEYS if str(k).startswith("hud.msg.")]) if hasattr(Rows, "KEYS") else None
    K.check(nmsg in (None, 11), "M1 Server Setup -> Messages has 11 rows (%s)" % nmsg)
    # ================================================================================== M2 registration with the REAL SkyyMenu registry
    SetStore.DIR = Paths.get(os.path.join(work, "settings"))
    bridge.put("settings:fn:register", M("SetRegFn")())
    bridge.put("settings:fn:get", M("SetGetFn")())
    bridge.put("settings:fn:set", M("SetSetFn")())
    K.check(FCfg.NODE is None, "M2 FeedCfg.NODE = null (no permission node)")
    FCfg.registerAll()
    keys = ["msg." + k for k in KINDS] + ["msg." + k + ".feed" for k in KINDS]
    defs = dict((k, SetReg.DEFS.get(k)) for k in keys)
    K.check(all(v is not None for v in defs.values()), "M2 all 22 switches registered with SkyyMenu: missing %s" % [k for k, v in defs.items() if v is None])
    K.check(all(v is not None and v[6] is None for v in defs.values()), "M2 no switch carries a permission node: %s"
            % [(k, str(v[6])) for k, v in defs.items() if v is not None and v[6] is not None])
    K.check(defs["msg.ability"] is not None and bool(defs["msg.ability"][4]) and not bool(defs["msg.ability.feed"][4]),
            "M2 the ability switches' defaults follow the server default Chat (shown, feed off)")
    # ================================================================================== M3 a non-op player sees their rows
    u = UUID(0x322, 1)
    u2 = UUID(0x322, 2)
    cat = int(SetReg.catIndex("messages"))
    vis = [str(x) for x in SetReg.visible(cat, u)]
    K.check(all(k in vis for k in keys), "M3 a NON-OP player sees all 22 message rows on the settings tab %d: missing %s" % (cat, [k for k in keys if k not in vis]))
    bridge.get("settings:fn:register").apply(arr("SkyyHudTest", "msg.zzzgated", "Gated", "messages", Boolean.TRUE, "control", "skyyhud.messages"))
    vis2 = [str(x) for x in SetReg.visible(cat, u)]
    K.check("msg.zzzgated" not in vis2 and bool(SetReg.may(u, "msg.ability")) and not bool(SetReg.may(u, "msg.zzzgated")),
            "M3 control: a row registered with the old node skyyhud.messages stays hidden from the same player (they are not an op)")
    # ================================================================================== M4 the non-op changes their own routes
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    Feed.PLUGIN = plugin
    Feed.publish()
    froute, fset = bridge.get("msgroute:fn:get"), bridge.get("settings:fn:set")
    for n_, uu in ((1, u), (2, u2)):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uu)
        setf(pr, PRef, "username", "Mia%d" % n_)
        LS.get(uu)
        plugin.huds.put(uu, HM(pr))

    def route(uu, k):
        return str(froute.apply(arr(uu, k)))

    def put(k, v):
        return bool(fset.apply(arr(u, k, Boolean(v))))
    r0 = (route(u, "ability"), route(u, "pickup"))
    sets = [put("msg.ability", True), put("msg.ability.feed", True)]
    r1 = route(u, "ability")
    sets += [put("msg.ability", False)]
    r2 = route(u, "ability")
    sets += [put("msg.ability", True), put("msg.ability.feed", False), put("msg.pickup.feed", False)]
    r3 = (route(u, "ability"), route(u, "pickup"))
    sets += [put("msg.pickup", False)]
    r4 = route(u, "pickup")
    K.check(all(sets), "M4 every settings:fn:set of the non-op player is accepted: %s" % sets)
    K.eq((r0, r1, r2, r3, r4), (("chat", "feed"), "feed", "off", ("chat", "chat"), "off"),
         "M4 msgroute answers the player's own choices (ability Chat -> Feed -> Off -> Chat; pickup Feed -> Chat -> Off)")
    K.eq((route(u2, "ability"), route(u2, "pickup")), ("chat", "feed"), "M4 a player who never chose = the server defaults")
    SetStore.saveNow(str(u))
    sf = [f for f in os.listdir(os.path.join(work, "settings")) if str(u) in f]
    st = open(os.path.join(work, "settings", sf[0]), encoding="latin-1").read() if sf else ""
    K.check("msg.ability=true" in st and "msg.ability.feed=false" in st and "msg.pickup=false" in st,
            "M4 the choices are saved where they always were (the player's SkyyMenu settings file %s)" % sf)
    # ================================================================================== M5 server defaults stay admin-only
    kmods = os.path.join(work, "k", "mods")
    os.makedirs(os.path.join(kmods, "Skyy_SkyyHud"))
    kf = os.path.join(kmods, "Skyy_SkyyHud", "config.properties")
    open(kf, "w", encoding="latin-1").write(ct)
    Cfg.FILE = Paths.get(kf)
    Cfg.load()
    Pub, Fn = H("CfgPub"), H("CfgFn")
    Pub.start(Paths.get(kmods), None)
    rd = Fn.set("hud.msg.ability", "feed", u, "Mia1", "yes", "menu")
    K.check(rd is not None and str(rd[0]) == "denied" and str(FCfg.R_ABILITY) == "chat" and route(u2, "ability") == "chat",
            "M5 a non-op player cannot change the server default (Server Setup set = %s; ability default stays chat)" % (None if rd is None else str(rd[0])))
    rc = Fn.set("hud.msg.ability", "feed", None, "Console", "yes", "console")
    Pub.flush()
    K.check(rc is not None and str(rc[0]) == "ok" and str(FCfg.R_ABILITY) == "feed" and bool(SetReg.DEFS.get("msg.ability.feed")[4])
            and route(u2, "ability") == "feed" and route(u, "ability") == "chat" and "msg.ability=feed" in open(kf, encoding="latin-1").read(),
            "M5 the console (admin) can: the server default -> Feed, the registered default follows (a player who never chose = feed), the "
            "player's own Chat choice still wins, the file line written")
    K.save()


EXPECT.update({
    # the ability kind (FeedCfg.R_ABILITY, route, loadFrom, the KINDS / label arrays) + NODE null
    "FeedCfg": ["+f R_ABILITY", "~<clinit>", "~m loadFrom", "~m register", "~m route"],
    # the Server Setup row hud.msg.ability + the config template line (CfgFile, HudCfg) + the version string (the kit's header / export, the ready line)
    "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"], "HudCfg": ["~m writeDefaults"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
})

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("x20", run_x20), ("x19", run_x19), ("quest", run_quest), ("msg", run_msg), ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
