"""Harness for SkyyIslands 0.5.21 (new island / shard / zone worlds turn on BetterMap by themselves; tools/islands_0_5_21_patch.py).
Build first: python tools/islands_0_5_21_patch.py && python SkyyIslands/build_skyyislands_0.5.21.py

    python SkyyIslands/test_skyyislands_0.5.21.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py, -Xverify:all):
  A / C / AA  verify, compare 0.5.20 -> 0.5.21 (exactly the planned members; IsleMap + IslandWorldAdd new; only the manifest changes), audit
  CFG   bettermap.autoTrack: a fresh file lists it (on), a 0.5.20 file without it = on and is not rewritten, a hand edit "false" read, the
        Server Setup row (Technical, bool, live)
  MAP   the name matcher (island / -pN / -rN / shard / zone worlds yes; hub-like, vanilla, other mods' worlds no); no BetterMap (no
        CommandManager, a null loader, a loader without BetterMap) = no-op and nothing thrown; THE REAL BetterMap 1.3.9 classes (a scratch
        copy of the jar in its own class loader, like the server's plugin loader): ModConfig on a scratch config -> isTrackedWorld read by
        reflection (0 / 1), the world added the way TrackWorldCommand does it (addAllowedWorld) -> already tracked = no-op; a scratch COPY
        of the test world's BetterMap config.json: the tracked worlds = no-op, an untracked zone world = track; once per run; the setting
        off; the command chain read from BetterMap's own bytecode (bettermap -> config -> track [world], permission
        bettermap.command.config, the console branch uses the world argument and ModConfig.addAllowedWorld); the real ConsoleSender
        holds that permission; our bytecode: send = CommandManager.handleCommand(ConsoleSender.INSTANCE, "bettermap config track " + wn),
        setup registers IslandWorldAdd for AddWorldEvent, accept -> IsleMap.onAdd(world name), everything inside try/catch
  LIVE  a scratch COPY of the live Skyy_SkyyIslands: config load = on (no new line), the file not rewritten
Not testable without the game (UNVERIFIED): the console command really parsed + run inside the live server, BetterMap's async command
finishing before the first player arrives, the map showing in a brand-new island world.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK

VERSION = "0.5.21"
OLD = "0.5.20"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "isl521", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
BM_JAR = os.path.join(B.USERDATA, "Mods", "BetterMap-1.3.9.jar")                                   # read-only: copied into scratch
BM_CFG = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "BetterMap", "config.json")       # read-only: copied into scratch
ADDED = ["IsleMap", "IslandWorldAdd"]
EXPECT = {
    "IslandCfg": ["+f BM_TRACK", "~<clinit>", "~m load"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
    "SkyyIslandsPlugin": ["~m setup"],
}


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare; its non-class check: only the manifest may change"""
    HK._kit_compare(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na = set(n_ for n_ in za.namelist() if not n_.endswith(".class"))
    nb = set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if na != nb or changed != ["manifest.json"]:
        d["fails"].append("C: non-class entries: added %s removed %s changed %s" % (sorted(nb - na), sorted(na - nb), changed))
    d["ok"] += 1
    json.dump(d, open(out, "w"), indent=1)


HK._kit_compare = HK.run_compare
HK.run_compare = run_compare


def boot(jar, scratch, sub):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    home = os.path.join(scratch, sub, "Skyy_SkyyIslands")
    shutil.rmtree(os.path.join(scratch, sub), ignore_errors=True)
    os.makedirs(home, exist_ok=True)
    P = lambda n: JClass(PKG + n)
    P("IslandStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    P("IslandCfg").FILE = JClass("java.nio.file.Paths").get(os.path.join(home, "config.properties"))
    P("IslandCfg").load("")
    return P, home


# ================================================================================================ CFG
def run_cfg(out, jar, scratch, _home):
    K = HK.Child(out)
    P, home = boot(jar, scratch, "cfg")
    Cfg = P("IslandCfg")
    cf = os.path.join(home, "config.properties")
    txt = open(cf, encoding="utf-8").read()
    lines = txt.splitlines()
    K.check("bettermap.autoTrack=true" in lines, "CFG a fresh config.properties lists bettermap.autoTrack=true")
    K.check(bool(Cfg.BM_TRACK), "CFG default on")
    old = "\n".join(l for l in lines if not l.startswith("bettermap.autoTrack") and "0.5.21" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.BM_TRACK = False
    Cfg.load("")
    K.check(bool(Cfg.BM_TRACK), "CFG a 0.5.20 file without the line = on")
    K.eq(open(cf, encoding="utf-8").read(), old, "CFG the 0.5.20 file is not rewritten (no migration)")
    open(cf, "w", encoding="utf-8").write(old + "bettermap.autoTrack=FALSE\n")
    Cfg.load("")
    K.check(not bool(Cfg.BM_TRACK), "CFG hand edit false read")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    r = SK.kit_rows(P("CfgRows")).get("bettermap.autoTrack")
    K.check(r is not None and tuple(r[1:5]) == ("BetterMap maps new worlds", "tech", "bool", "true") and "live" in r[9] and len(r[10]) <= 100
            and r[10].startswith("New island"), "ROW bettermap.autoTrack (Technical, bool, on, live, help <= 100): %s" % (r and r[1:11]))
    K.save()


# ================================================================================================ MAP
def run_map(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    P, home = boot(jar, scratch, "map")
    Cfg, Map, St = P("IslandCfg"), P("IsleMap"), P("IslandStore")
    # --- the name matcher
    yes = ["skyy-island-b942734e-90b8-4e4b-986c-cd725d975b9e", "skyy-island-d8ddde89-98b2-4739-983e-a39773d582b6-p2",
           "skyy-island-d8ddde89-98b2-4739-983e-a39773d582b6-p3-r1", "skyy-shard-00000000-0000-4000-8000-000000000001", "skywynn_zones",
           "skywynn_zones2", "skywynn_zones5"]
    no = ["default", "world", "skyy-islands", "skyy_island-x", "Skyy-Island-x", "skywynn", "skywynn_z", "skywynn_hub", "instance-x", "", None]
    for wn in yes:
        K.check(bool(Map.kind(JString(wn))), "MAP kind: %s is ours" % wn)
    for wn in no:
        K.check(not bool(Map.kind(None if wn is None else JString(wn))), "MAP kind: %r is not ours" % wn)
    # --- no BetterMap: no CommandManager in a bare JVM, a null loader, a loader without BetterMap's classes
    K.check(Map.bmCommand() is None, "MAP no CommandManager / no /bettermap command -> bmCommand null")
    K.eq(int(Map.onAdd(JString("skyy-island-nobm"))), 1, "MAP no BetterMap -> onAdd = 1 (no-op), nothing thrown")
    K.check(Map.SENT.isEmpty() and int(Map.TRACKED.get()) == 0, "MAP ... nothing recorded as sent")
    K.check(not bool(Map.send(JString("skyy-island-nobm"))), "MAP send without a server -> false, nothing thrown")
    K.eq(int(Map.decide(JString("skyy-island-x"), None)), 1, "MAP decide with no BetterMap loader -> 1")
    for bad in (None, JString(""), JString("default")):
        K.eq(int(Map.onAdd(bad)), 0, "MAP onAdd(%r) -> 0, nothing thrown" % bad)
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    K.eq(int(Map.tracked(sysl, JString("skyy-island-x"))), -1, "MAP a loader without BetterMap -> tracked -1 (cannot tell)")
    K.eq(int(Map.tracked(None, JString("skyy-island-x"))), -1, "MAP tracked(null loader) -> -1, nothing thrown")
    K.eq(int(Map.decide(JString("skyy-island-x"), sysl)), 3, "MAP cannot tell -> the idempotent command runs anyway (3)")
    # --- the REAL BetterMap 1.3.9 classes in their own loader (a scratch copy of the jar)
    if not os.path.isfile(BM_JAR):
        K.check(False, "MAP BetterMap jar not found: %s" % BM_JAR)
        K.save()
        return
    bmd = os.path.join(scratch, "map", "bm")
    os.makedirs(bmd, exist_ok=True)
    bj = os.path.join(bmd, "BetterMap-1.3.9.jar")
    shutil.copyfile(BM_JAR, bj)
    URL = JClass("java.net.URL")
    urls = JArray(URL)([JClass("java.io.File")(bj).toURI().toURL()])
    cl = JClass("java.net.URLClassLoader")(urls, sysl)
    MC = JClass("java.lang.Class").forName("dev.ninesliced.configs.ModConfig", True, cl)
    inst = MC.getMethod("getInstance").invoke(None)
    save1 = os.path.join(bmd, "save1")
    os.makedirs(save1, exist_ok=True)
    MC.getMethod("initialize", JClass("java.nio.file.Path")).invoke(inst, JClass("java.nio.file.Paths").get(save1))
    cfgf = os.path.join(save1, "mods", "BetterMap", "config.json")
    K.check(os.path.isfile(cfgf), "MAP real ModConfig.initialize wrote its config.json in scratch")
    W = "skyy-island-00000000-0000-4000-8000-0000000d0521"
    K.eq(int(Map.tracked(cl, JString(W))), 0, "MAP real ModConfig: a new island world is not tracked (reflection read)")
    K.eq(int(Map.decide(JString(W), cl)), 3, "MAP real ModConfig: not tracked -> track it (3)")
    added = MC.getMethod("addAllowedWorld", JClass("java.lang.String")).invoke(inst, JString(W))   # what TrackWorldCommand runs
    K.check(bool(added) and W in json.load(open(cfgf, encoding="utf-8")).get("allowedWorlds", []), "MAP real addAllowedWorld (the command's step) saves it")
    K.eq(int(Map.tracked(cl, JString(W))), 1, "MAP real ModConfig: now tracked (1)")
    K.eq(int(Map.decide(JString(W), cl)), 2, "MAP already tracked -> no-op (2)")
    # a scratch COPY of the test world's BetterMap config
    if os.path.isfile(BM_CFG):
        save2 = os.path.join(bmd, "save2")
        os.makedirs(os.path.join(save2, "mods", "BetterMap"), exist_ok=True)
        shutil.copyfile(BM_CFG, os.path.join(save2, "mods", "BetterMap", "config.json"))
        live = json.load(open(BM_CFG, encoding="utf-8")).get("allowedWorlds", [])
        MC.getMethod("initialize", JClass("java.nio.file.Path")).invoke(inst, JClass("java.nio.file.Paths").get(save2))
        ours = [w for w in live if Map.kind(JString(w))]
        for w in ours:
            K.eq(int(Map.decide(JString(w), cl)), 2, "MAP live copy: %s already tracked -> no-op" % w[:40])
        for w in ("skywynn_zones2", "skywynn_zones3", "skyy-shard-00000000-0000-4000-8000-0000000e0521"):
            if w not in live:
                K.eq(int(Map.decide(JString(w), cl)), 3, "MAP live copy: %s not tracked -> track it" % w)
        K.notes.append("live BetterMap config: %d tracked worlds, %d of them ours" % (len(live), len(ours)))
    else:
        K.notes.append("no live BetterMap config.json to copy (skipped)")
    # once per run + the setting off
    Map.SENT.put(JString("skywynn_zones4"), JClass("java.lang.Boolean").TRUE)
    K.eq(int(Map.decide(JString("skywynn_zones4"), cl)), 4, "MAP already sent this run -> 4 (no second command)")
    Cfg.BM_TRACK = False
    K.eq(int(Map.decide(JString("skywynn_zones3"), cl)), 0, "MAP setting off -> 0")
    K.eq(int(Map.onAdd(JString("skywynn_zones3"))), 0, "MAP setting off -> onAdd 0")
    Cfg.BM_TRACK = True
    # --- the command chain, read from BetterMap's own bytecode (javassist over the scratch copy)
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(bj)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def ins(cn, mn):
        cc = pool.get(cn)
        out_ = []
        for mi in cc.getClassFile().getMethods():
            if str(mi.getName()) == mn and mi.getCodeAttribute() is not None:
                it = mi.getCodeAttribute().iterator()
                while it.hasNext():
                    out_.append(str(IP.instructionString(it, it.next(), mi.getConstPool())))
        return "\n".join(out_)
    bmc = ins("dev.ninesliced.commands.bettermap.BetterMapCommand", "<init>")
    cfc = ins("dev.ninesliced.commands.bettermap.config.ConfigCommand", "<init>")
    trc = ins("dev.ninesliced.commands.bettermap.config.TrackWorldCommand", "<init>")
    tre = ins("dev.ninesliced.commands.bettermap.config.TrackWorldCommand", "execute")
    K.check('"bettermap"' in bmc and "ConfigCommand.<init>" in bmc, "CMD BetterMapCommand = /bettermap with the config sub-command")
    K.check('"config"' in cfc and "TrackWorldCommand.<init>" in cfc and '"bettermap.command.config"' in cfc, "CMD ConfigCommand = config (bettermap.command.config) with track")
    K.check('"track"' in trc and '"world"' in trc and "withOptionalArg" in trc and '"bettermap.command.config"' in trc,
            "CMD TrackWorldCommand = track [world] (optional argument, bettermap.command.config)")
    lam = ins("dev.ninesliced.commands.bettermap.config.TrackWorldCommand", "lambda$execute$0")
    K.check("isPlayer" in tre and "ModConfig.addAllowedWorld" in tre and "World.execute" in tre and "refreshTrackers" in lam and "broadcastMapSettings" in lam,
            "CMD track: the given world -> ModConfig.addAllowedWorld (+ world.execute(broadcastMapSettings / refreshTrackers))")
    Con = JClass("com.hypixel.hytale.server.core.console.ConsoleSender")
    try:
        hp = bool(Con.INSTANCE.hasPermission(JString("bettermap.command.config")))
    except Exception as e:
        hp = "error %s" % e
    K.check(hp is True, "CMD the real ConsoleSender holds bettermap.command.config: %s" % hp)
    K.eq(str(Map.CMD) + "x", "bettermap config track x", "CMD the command line")
    sd = ins(PKG + "IsleMap", "send")
    K.check("ConsoleSender.INSTANCE" in sd and "CommandManager.handleCommand" in sd, "CMD send = CommandManager.handleCommand(ConsoleSender.INSTANCE, CMD + wn)")
    tk = ins(PKG + "IsleMap", "tracked")
    K.check('"getInstance"' in tk and '"isTrackedWorld"' in tk and "addAllowedWorld" not in tk and "setAllowedWorlds" not in tk,
            "CMD the reflection only READS (getInstance + isTrackedWorld; never addAllowedWorld / setAllowedWorlds)")
    K.check("addAllowedWorld" not in ins(PKG + "IsleMap", "onAdd") and "config.json" not in "".join(ins(PKG + "IsleMap", m) for m in
            ("onAdd", "decide", "send", "tracked", "bmCommand")), "CMD no BetterMap file is touched by our code")
    su = ins(PKG + "SkyyIslandsPlugin", "setup")
    K.check("AddWorldEvent" in su and "IslandWorldAdd" in su, "HOOK setup registers IslandWorldAdd for AddWorldEvent")
    ac = ins(PKG + "IslandWorldAdd", "accept")
    K.check("IsleMap.onAdd" in ac and "getWorld" in ac and "World.getName" in ac, "HOOK accept -> IsleMap.onAdd(world name)")
    for cn, mn in (("IslandWorldAdd", "accept"), ("IsleMap", "onAdd"), ("IsleMap", "send"), ("IsleMap", "tracked"), ("IsleMap", "bmCommand")):
        mi = [m for m in pool.get(PKG + cn).getClassFile().getMethods() if str(m.getName()) == mn][0]
        et = mi.getCodeAttribute().getExceptionTable()
        K.check(et.size() >= 1 and any(et.catchType(i) == 0 or "Throwable" in str(mi.getConstPool().getClassInfo(et.catchType(i))) for i in range(et.size())),
                "SAFE %s.%s catches Throwable (nothing escapes into the world load)" % (cn, mn))
    # no exception escapes: the listener with junk
    L = P("IslandWorldAdd")()
    for junk in (None, JString("not an event"), JClass("java.lang.Object")()):
        try:
            L.accept(junk)
            ok = True
        except Exception as e:
            ok = "threw %s" % e
        K.check(ok is True, "SAFE IslandWorldAdd.accept(%r) returns quietly: %s" % (junk, ok))
    K.save()


# ================================================================================================ LIVE
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg = P("IslandCfg")
    P("IslandStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    Cfg.FILE = JClass("java.nio.file.Paths").get(os.path.join(home, "config.properties"))
    Cfg.load("")
    K.check(bool(Cfg.BM_TRACK) and bool(Cfg.POND_ON) and str(Cfg.DEATH_KEEP) == "skyy-shard-", "LIVE the live config (no new line) = auto-track on, 0.5.20 values kept")
    K.check(HK.tree_hash(home) == h0, "LIVE no file of the copy changed (load writes nothing)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("cfg", run_cfg), ("map", run_map), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
