"""Harness for SkyyIslands 0.5.9 (SOUND PASS ROUND 1: the portal sound after /island and /hub; tools/islands_0_5_9_patch.py). Build first:
python tools/islands_0_5_9_patch.py && python SkyyIslands/build_skyyislands_0.5.9.py

    python SkyyIslands/test_skyyislands_0.5.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.5.8 -> 0.5.9: + IslandSnd; IslandCfg (3 fields, load), IslandCmd.go, HubCmd.execute, IslandReady.accept, the kit + version
              texts only
  SND         EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py: every Assets.zip sound id in the engine's SoundEvent
              store, a stand-in player on a REAL GamePacketHandler, a stand-in Universe):
              - THE ARRIVAL: the REAL IslandReady.accept on a REAL PlayerReadyEvent (its Ref on a stand-in Store that answers the player)
                after IslandSnd.arm = ONE PlaySoundEvent2D SFX_Portal_Neutral_Teleport_Local (UI) to that player; a second ready = nothing
                (one-shot); a ready with nothing armed (a login, another mod's teleport) = nothing; an arm older than 30 s = nothing;
                the switches (master / the sound / an empty id) = silent but the arm is used up
              - IslandSnd itself (idx / err / check / pick / gate / playTo; a missing id = one WARN)
              - Server Setup: the 3 rows (Sounds category, live, the default id), the kit's own check= hook; config.properties: a fresh
                file lists the 3 lines, a 0.5.8 file without them = the defaults, typed values read
              - static: /island's go() arms right BEFORE each teleport (loaded and loading world), /hub arms only when sendToHub sent
                the player, IslandReady.accept calls arrived before the login routing; only IslandSnd calls SoundUtil
  X, D        every 0.5.8 phase carried forward on the 0.5.9 jar (test_skyyislands_0.5.8.py's run_exec and run_live = START TWICE on a
              scratch COPY of the live Skyy_SkyyIslands, nothing written)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK

_spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_8", os.path.join(HERE, "test_skyyislands_0.5.8.py"))
T58 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T58)

VERSION = "0.5.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound1", "islands")))
PKG = "com.skyy.islands."
PORTAL = "SFX_Portal_Neutral_Teleport_Local"
EXPECT = {
    "IslandCfg": ["+f SND_ON", "+f SND_PORTAL", "+f SND_PORTAL_ID", "~<clinit>", "~m load"],
    "IslandCmd": ["~m go"],
    "HubCmd": ["~m execute"],
    "IslandReady": ["~m accept"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyIslandsPlugin": ["~m setup"],
}
ADDED = ["IslandSnd"]


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    st = SK.Stage()
    P = lambda n: JClass(PKG + n)
    Cfg, Snd, Rows, Fn, Ready, Store = P("IslandCfg"), P("IslandSnd"), P("CfgRows"), P("CfgFn"), P("IslandReady"), P("IslandStore")
    Paths, UUID, Long = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long")
    u = UUID.fromString("00000000-0000-0000-0000-0000000000a2")
    pa = st.player("Alice", str(u))
    st.universe()
    # ---------------- config.properties + rows
    home = os.path.join(scratch, "snd", "Skyy_SkyyIslands")
    os.makedirs(home, exist_ok=True)
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    K.check("sounds.enabled=true" in txt and "sound.portal=true" in txt and ("sound.portal.id=%s" % PORTAL) in txt, "CFG a fresh config.properties lists the 3 sound lines")
    K.check(bool(Cfg.SND_ON) and bool(Cfg.SND_PORTAL) and str(Cfg.SND_PORTAL_ID) == PORTAL and PORTAL in st.ids, "CFG defaults (the id is in Assets.zip)")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("sound")) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.SND_PORTAL_ID = "x"
    Cfg.load("")
    K.check(bool(Cfg.SND_ON) and bool(Cfg.SND_PORTAL) and str(Cfg.SND_PORTAL_ID) == PORTAL, "CFG a 0.5.8 file without the lines = the defaults")
    open(cf, "w", encoding="utf-8").write(old + "sounds.enabled=false\nsound.portal=false\nsound.portal.id=\n")
    Cfg.load("")
    K.check(not bool(Cfg.SND_ON) and not bool(Cfg.SND_PORTAL) and str(Cfg.SND_PORTAL_ID) == "", "CFG off / off / an empty id read")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "sounds.enabled", [("sound.portal", "sound.portal.id", PORTAL)])
    K.check(all(rows[k][2] == "sounds" for k in ("sounds.enabled", "sound.portal", "sound.portal.id")), "ROW the Sounds category")
    K.check("no sound event" in (SK.kit_check(Fn, Rows, "sound.portal.id", SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, "sound.portal.id", "a.b") is not None
            and SK.kit_check(Fn, Rows, "sound.portal.id", "") is None and SK.kit_check(Fn, Rows, "sound.portal.id", "SFX_Portal_Void") is None,
            "CHECK the kit's check= hook")
    # ---------------- IslandSnd itself
    K.check(int(Snd.idx(PORTAL)) == st.ids[PORTAL] and int(Snd.idx(SK.BAD_ID)) == -2147483648, "IslandSnd.idx")
    K.check(Snd.pick(True, True, PORTAL) == PORTAL and Snd.pick(True, False, PORTAL) is None and Snd.pick(False, True, PORTAL) is None and Snd.pick(True, True, "") is None, "IslandSnd.pick")
    st.clear()
    K.check(bool(Snd.playTo(pa, PORTAL, "t")) and not bool(Snd.playTo(pa, PORTAL, "t")) and st.sounds() == [("Alice", PORTAL, "UI", "2d")], "IslandSnd.playTo once; the gate")
    K.check(not bool(Snd.playTo(pa, SK.BAD_ID, "z")) and not bool(Snd.playTo(None, PORTAL, "z")) and len(st.sounds()) == 1, "IslandSnd: a missing id / no player = nothing")
    # ---------------- THE ARRIVAL through the REAL IslandReady.accept on a REAL PlayerReadyEvent
    U = st.us
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    CM, CC, CF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    StoreC = JClass("com.hypixel.hytale.component.Store")
    fs = cp.makeClass("com.hypixel.hytale.component.SkyySndFakeStore", cp.get("com.hypixel.hytale.component.Store"))
    fs.addField(CF.make("public static Object COMP;", fs))
    fs.addConstructor(CC.make("public SkyySndFakeStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, null, (com.hypixel.hytale.component.IResourceStorage) null); }", fs))
    fs.addMethod(CM.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) COMP; }", fs))
    fs.addMethod(CM.make("public Object getExternalData() { return null; }", fs))
    FSC = fs.toClass(StoreC.class_)
    store = U.allocateInstance(FSC)
    FSC.getField("COMP").set(None, pa)
    RefC = JClass("com.hypixel.hytale.component.Ref")
    ref = U.allocateInstance(RefC.class_)
    st.fld(RefC.class_, "store").set(ref, store)
    PRE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
    rdy = Ready()
    Store.SEEN.put(u, JClass("java.lang.Boolean").TRUE)      # not the first ready of the session (no login routing in a bare JVM)

    def ready():
        rdy.accept(PRE(ref, None, 1))
    Snd.LAST.clear()
    st.clear()
    ready()
    K.check(st.sounds() == [], "SITE a ready with nothing armed (a login, another mod's teleport) = silent")
    Snd.arm(u)
    ready()
    K.eq(st.sounds(), [("Alice", PORTAL, "UI", "2d")], "SITE /island or /hub armed -> the next PlayerReadyEvent (IslandReady.accept) plays the portal sound")
    Snd.LAST.clear()
    st.clear()
    ready()
    K.check(st.sounds() == [] and Snd.PEND.isEmpty(), "SITE one-shot: the next ready is silent")
    Snd.arm(u)
    Snd.PEND.put(u, Long(int(JClass("java.lang.System").currentTimeMillis()) - 1))
    ready()
    K.check(st.sounds() == [] and Snd.PEND.isEmpty(), "SITE an arm older than 30 s = silent (and used up)")
    for what, f, v in (("master off", "SND_ON", False), ("portal off", "SND_PORTAL", False), ("empty id", "SND_PORTAL_ID", "")):
        o = getattr(Cfg, f)
        setattr(Cfg, f, v)
        Snd.LAST.clear()
        st.clear()
        Snd.arm(u)
        ready()
        K.check(st.sounds() == [] and Snd.PEND.isEmpty(), "SITE %s: silent, the arm used up" % what)
        setattr(Cfg, f, o)
    K.check(not bool(Snd.arrived(None)), "SITE arrived(null) = false, no throw")
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["IslandSnd.playTo"], "STATIC only IslandSnd.playTo calls SoundUtil")
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    go = code("IslandCmd", "go")
    a1, t1 = go.find("IslandSnd.arm"), go.find("teleportPlayerToInstance")
    a2, t2 = go.find("IslandSnd.arm", a1 + 1), go.find("teleportPlayerToLoadingInstance")
    K.check(0 <= a1 < t1 < a2 < t2 and go.count("IslandSnd.arm") == 2, "STATIC /island go(): arm right before each of the two teleports")
    hx = code("HubCmd", "execute")
    K.check(0 <= hx.find("HubCmd.sendToHub") < hx.find("IslandSnd.arm") and hx.count("IslandSnd.arm") == 1, "STATIC /hub arms after sendToHub (only when it sent)")
    ac = code("IslandReady", "accept")
    K.check(0 <= ac.find("IslandSnd.arrived") < ac.find("RouteTask.schedule"), "STATIC IslandReady.accept calls arrived before the login routing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("exec", T58.run_exec), ("live", T58.run_live)], script=__file__, live=(T58.LIVE_DIR, "Skyy_SkyyIslands"))
