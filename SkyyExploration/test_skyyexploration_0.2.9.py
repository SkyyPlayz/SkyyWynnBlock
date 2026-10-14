"""Harness for SkyyExploration 0.2.9 (SOUND PASS ROUND 1: the claim sting + the landing / reveal sounds as Server Setup rows;
tools/exploration_0_2_9_patch.py). Build first: python tools/exploration_0_2_9_patch.py && python SkyyExploration/build_skyyexploration_0.2.9.py

    python SkyyExploration/test_skyyexploration_0.2.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.2.8 -> 0.2.9 (the 0.2.8 harness's compare; non-class entries: manifest.json only): ExpCfg (9 fields, sndPick, apply, check),
              LgRv (play2d, sound), LgCore (placeNow, claimOk), the kit + version texts only
  SND         EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py: every Assets.zip sound id in the engine's SoundEvent store,
              a stand-in player on a REAL GamePacketHandler):
              - THE CLAIM: the REAL LgCore.claimOk on a Lost Loot site (the 0.2.8 LgApi stand-in world) = the chat line AND ONE
                PlaySoundEvent2D SFX_Chest_Wooden_Open_Player (UI) to the claimer; the switches (master / the row / an empty id) = silent
              - THE LANDING: the REAL LgCore.placeNow of a supply drop = LgEng.snd with the row's id (default SFX_Wood_Land = 0.2.8's);
                another id typed = that id; off / empty = no thump (the puff stays)
              - THE REVEAL: LgRv.sound rank 1 / 2 = the Rare / Legendary rows (defaults = 0.2.8's ids), rank 0 = nothing; the switches
              - LgRv.play2d: a missing id = nothing + one WARN, null player / id = nothing
              - Server Setup: the 9 rows (Sounds category, live, the defaults), the kit's own check= hook (ExpCfg.check -> soundErr);
                config: an old file (no lines) = the defaults, typed values read; every default id is in Assets.zip
              - static: only LgRv / LgEng call SoundUtil (as in 0.2.8); claimOk -> LgRv.play2d; placeNow -> sndPick
  X, D        every 0.2.8 phase carried forward on the 0.2.9 jar (test_skyyexploration_0.2.8.py's run_exec and run_live = START TWICE on a
              scratch COPY of the live Skyy_SkyyExploration)
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

_spec = importlib.util.spec_from_file_location("test_skyyexploration_0_2_8", os.path.join(HERE, "test_skyyexploration_0.2.8.py"))
T28 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T28)
T28.NONCLASS = ["manifest.json"]              # 0.2.8 -> 0.2.9: the asset pack files are the same bytes

VERSION = "0.2.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound1", "explore")))
PKG = T28.PKG
SOUNDS = [("claim", "CLAIM", "SFX_Chest_Wooden_Open_Player"), ("landing", "LAND", "SFX_Wood_Land"),
          ("revealRare", "RARE", "SFX_Coffer_Goblin_Reward"), ("revealLegend", "LEGEND", "SFX_Memories_Unlock_Local")]
EXPECT = {
    "ExpCfg": ["+f SND_ON"] + sum([["+f SND_%s" % f, "+f SND_%s_ID" % f] for _k, f, _d in SOUNDS], []) + ["+m sndPick", "~<clinit>", "~m apply", "~m check", "~m live", "~m load"],
    "LgRv": ["+m play2d", "~m sound"],
    "LgCore": ["~m placeNow", "~m claimOk"],
    "SkyyExplorationPlugin": ["~m setup"],
    "ExpLgMig": ["~m logLine", "~m migrate"],   # its WHO constant (inlined) names the version
    "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = []


def run_snd(out, jar, scratch, _home):
    from jpype import JClass, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    st = SK.Stage()
    P = lambda n: JClass(PKG + n)
    Cfg, Core, Site, Eng, Rv, Reg, CR_, Rows, Fn, EIO = (P("ExpCfg"), P("LgCore"), P("LgSite"), P("LgEng"), P("LgRv"), P("LgReg"), P("ChestReg"),
                                                         P("CfgRows"), P("CfgFn"), P("ExpIO"))
    Props, UUID, AL = JClass("java.util.Properties"), JClass("java.util.UUID"), JClass("java.util.ArrayList")
    u = UUID.fromString("00000000-0000-0000-0000-0000000000a3")
    pa = st.player("Alice", str(u))
    st.universe()
    # ---------------- config
    Cfg.apply(Props())
    K.check(bool(Cfg.SND_ON) and all(bool(getattr(Cfg, "SND_" + f)) and str(getattr(Cfg, "SND_%s_ID" % f)) == d for _k, f, d in SOUNDS)
            and all(d in st.ids for _k, _f, d in SOUNDS), "CFG an old file without the lines = the defaults (= 0.2.8's ids where 0.2.8 played one; all in Assets.zip)")
    pp = Props()
    for k, v in (("sounds.enabled", "false"), ("sound.claim", "false"), ("sound.landing.id", "SFX_Coins_Land"), ("sound.revealRare.id", "")):
        pp.setProperty(k, v)
    Cfg.apply(pp)
    K.check(not bool(Cfg.SND_ON) and not bool(Cfg.SND_CLAIM) and str(Cfg.SND_LAND_ID) == "SFX_Coins_Land" and str(Cfg.SND_RARE_ID) == "", "CFG typed values read (off / another id / empty)")
    Cfg.apply(Props())
    K.check(Cfg.sndPick(True, " SFX_Wood_Land ") == "SFX_Wood_Land" and Cfg.sndPick(False, "x") is None and Cfg.sndPick(True, "") is None and Cfg.sndPick(True, None) is None,
            "CFG sndPick")
    Cfg.SND_ON = False
    K.check(Cfg.sndPick(True, "x") is None, "CFG sndPick: master off")
    Cfg.SND_ON = True
    defs = open(os.path.join(os.path.dirname(jar), "build_skyyexploration_0.2.9.py"), encoding="utf8").read()
    K.check("sounds.enabled=true" in defs and all(("sound.%s.id=%s" % (k, d)) in defs for k, _f, d in SOUNDS), "CFG the default file text lists the sound lines")
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "sounds.enabled", [("sound.%s" % k, "sound.%s.id" % k, d) for k, _f, d in SOUNDS])
    K.check(all(rows[k][2] == "sounds" for k in rows if k.startswith("sound")), "ROW the Sounds category")
    for k, _f, _d in SOUNDS:
        key = "sound.%s.id" % k
        K.check("no sound event" in (SK.kit_check(Fn, Rows, key, SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, key, "") is None
                and SK.kit_check(Fn, Rows, key, "SFX_Coins_Land") is None, "CHECK %s: the kit's check= hook (soundErr)" % key)
    # ---------------- LgRv.play2d + the reveal
    st.clear()
    K.check(bool(Rv.play2d(pa, "SFX_Coins_Land")) and st.sounds() == [("Alice", "SFX_Coins_Land", "UI", "2d")], "play2d = ONE PlaySoundEvent2D (UI) to that player")
    K.check(not bool(Rv.play2d(pa, SK.BAD_ID)) and not bool(Rv.play2d(None, "SFX_Coins_Land")) and not bool(Rv.play2d(pa, None)) and len(st.sounds()) == 1,
            "play2d: a missing id / no player / no id = nothing")
    st.clear()
    Rv.sound(pa, 1)
    Rv.sound(pa, 2)
    Rv.sound(pa, 0)
    K.eq(st.sounds(), [("Alice", "SFX_Coffer_Goblin_Reward", "UI", "2d"), ("Alice", "SFX_Memories_Unlock_Local", "UI", "2d")], "SITE reveal: rank 1 / 2 = the rows' ids, rank 0 = nothing")
    Cfg.SND_RARE_ID = "SFX_Coins_Hit"
    Cfg.SND_LEGEND = False
    st.clear()
    Rv.sound(pa, 1)
    Rv.sound(pa, 2)
    K.eq(st.sounds(), [("Alice", "SFX_Coins_Hit", "UI", "2d")], "SITE reveal: a typed id is played; Legendary off = silent")
    Cfg.apply(Props())
    # ---------------- THE CLAIM through the REAL claimOk (the 0.2.8 LgApi stand-in world)
    state = {"placed": {}, "log": [], "ground": "Soil_Grass", "given": []}
    Eng.API = T28.sim(state)

    def claim():
        s1 = Site.parse("1\t65\t1\t1\t23\t0\t10\t0\t10\t7\t")
        a = Core.act(1, None, "w1", s1, JLong(0))
        a.u, a.at, a.pr = u, JLong(int(JClass("java.lang.System").currentTimeMillis())), pa
        Core.claimOk(a, None, None, None)
    st.clear()
    claim()
    K.check(st.sounds() == [("Alice", "SFX_Chest_Wooden_Open_Player", "UI", "2d")], "SITE claimOk = the claim sting to the claimer: %s (chat %s)" % (st.sounds(), st.chats()[-1:]))
    for what, f, v in (("master off", "SND_ON", False), ("claim off", "SND_CLAIM", False), ("empty id", "SND_CLAIM_ID", "")):
        setattr(Cfg, f, v)
        st.clear()
        claim()
        K.check(st.sounds() == [], "SITE claimOk %s = silent" % what)
        Cfg.apply(Props())
    # ---------------- THE LANDING through the REAL placeNow
    wf = CR_.wf("w1")

    def land(x):
        d5 = Site.parse("%d\t65\t1\t5\t23\t0\t10\t0\t10\t7\t" % x)
        sites = AL()
        sites.add(d5)
        Reg.W.put(wf, sites)
        a5 = Core.act(0, None, "w1", d5, JLong(0))
        n0 = len(state["log"])
        ok = bool(Core.placeNow(a5))
        return ok, [e for e in state["log"][n0:] if e[0] in ("snd", "poof")]
    ok, ev = land(100)
    K.check(ok and ("snd", "SFX_Wood_Land") in ev and any(e[0] == "poof" for e in ev), "SITE placeNow (supply drop) = the puff + the row's thump (SFX_Wood_Land, 0.2.8's): %s" % ev)
    Cfg.SND_LAND_ID = "SFX_Coins_Land"
    ok, ev = land(110)
    K.check(ok and ("snd", "SFX_Coins_Land") in ev, "SITE placeNow: a typed landing id is used")
    for what, f, v in (("master off", "SND_ON", False), ("landing off", "SND_LAND", False), ("empty id", "SND_LAND_ID", "")):
        Cfg.apply(Props())
        setattr(Cfg, f, v)
        ok, ev = land(120 + len(what))
        K.check(ok and not [e for e in ev if e[0] == "snd"] and any(e[0] == "poof" for e in ev), "SITE placeNow %s = the puff, no thump" % what)
    Cfg.apply(Props())
    Eng.API = None
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    users = sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs))
    K.check(set(users) <= {"LgRv.play2d", "LgEng.sound", "LgEng.poof", "LgEng.snd", "ExpSpot.sound"} and "LgRv.play2d" in users and "LgRv.sound" not in users,
            "STATIC SoundUtil callers = 0.2.8's + LgRv.play2d (LgRv.sound now goes through it): %s" % users)
    K.check(PKG + "LgRv.play2d" in g.get("LgCore.claimOk", set()) and PKG + "ExpCfg.sndPick" in g.get("LgCore.placeNow", set())
            and PKG + "LgRv.play2d" in g.get("LgRv.sound", set()), "STATIC claimOk -> play2d; placeNow -> sndPick; sound -> play2d")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("exec", T28.run_exec), ("live", T28.run_live)], script=__file__, live=(T28.LIVE_DIR, "Skyy_SkyyExploration"))
