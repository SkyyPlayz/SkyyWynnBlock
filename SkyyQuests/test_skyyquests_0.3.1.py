"""SkyyQuests 0.3.1 harness (SOUND PASS ROUND 1: task / quest done, reward paid, NPC talk; tools/quests_0_3_1_patch.py) on top of the 0.3
harness (test_skyyquests_0.3.py: every 0.3 phase runs again on the 0.3.1 jar). tools/harness_kit.py phases, fresh child JVMs (-Xverify:all).

    python SkyyQuests/test_skyyquests_0.3.1.py [--jar SkyyQuests-0.3.1.jar] [--dir <scratch>] [--keep]

  A / C / AA  verify, class compare 0.3 -> 0.3.1 (+ QSnd; QCfg / QEng / QPay / QTalk / the kit + version texts only), engine-access audit
  SND         EXECUTED, every new code path through the ENGINE's own send path: the stand-in SoundEvent store holds every id of the cached
              Assets.zip (tools/soundpass_kit.py), stand-in players on REAL GamePacketHandlers capture the packets SoundUtil writes:
              - QSnd: idx / err / check / pick / gate / playTo / play (by UUID through Universe.getPlayer), a missing id = nothing + one
                WARN, the 0.5 s gate per player per sound (another sound / player not held back), a player who left = nothing
              - THE CALL SITES through the real engine paths: 10 trunk breaks (QEng.count -> after -> doneSound) = ONE task-done
                PlaySoundEvent2D (UI) for that player only; its coins claim paid at once (QPay.tell) = the reward sound; a finished
                quest LINE (doneSound with no next task) = the quest-done sting INSTEAD of the task one; F on Marlow (QTalk.pageFor) =
                the talk sound; every switch (master, each sound, an empty id) = silent
              - Server Setup: the 9 rows (category Sounds, live, defaults = the build's ids), the kit's own check= hook refuses a bad id
                / bad characters and takes "" and a real id; config.properties: a 0.3 file (no sound lines) = the defaults, typed lines
                read (off, another id, an empty id); every default id is in Assets.zip
              - static: only QSnd calls SoundUtil; after -> doneSound; tell / pageFor -> QSnd
  D E L P K S N B F ST   the 0.3 phases on the 0.3.1 jar (start twice on a scratch COPY of the live data in ST)
Scratch: tools/dev/scratch/sound1/quests (deleted unless --keep). Exit 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "sound1", "quests")]
_spec = importlib.util.spec_from_file_location("test_skyyquests_0_3", os.path.join(HERE, "test_skyyquests_0.3.py"))
T03 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T03)
HK.run_compare = T03._orig_compare            # 0.3's compare wrap expects the 0.2 -> 0.3 lang file; 0.3 -> 0.3.1 = the plain kit compare

VERSION = "0.3.1"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyQuests-0.3.jar")
SCRATCH = T03.SCRATCH
FAKE_DIR = T03.FAKE_DIR
PKG = T03.PKG
SOUNDS = [("task", "TASK", "SFX_Dungeon_Checkpoint_Activate"), ("quest", "QUEST", "SFX_Event_Chapter_1_Complete_Sting"),
          ("reward", "REWARD", "SFX_Coins_Land"), ("talk", "TALK", "SFX_Drag_Items_Paper")]
EXPECT = {
    "QCfg": ["+f SND_ON"] + sum([["+f SND_%s" % f, "+f SND_%s_ID" % f] for _k, f, _d in SOUNDS], []) + ["~<clinit>", "~m load"],
    "QEng": ["+m doneSound", "~m after"],
    "QPay": ["~m tell"],
    "QTalk": ["~m pageFor"],
    "CfgFile": ["~<clinit>"],                     # the kit holds the default file text (9 new lines)
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyQuestsPlugin": ["~m setup"],
}
ADDED = ["QSnd"]


def run_snd(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    PyFn = T03.fn_class()
    Boolean, Long = JClass("java.lang.Boolean"), JClass("java.lang.Long")
    st = SK.Stage()
    X = T03.scene3(K, scratch, "snd")
    Eng, Cfg, Defs, Talk, Log, Sto = X.Eng, X.Cfg, X.Defs, X.Talk, X.Log, X.Sto
    Snd = X.E.P("QSnd")
    Sto.STOPPED = True
    br.put("profile:fn:key", PyFn(lambda a: str(a)))
    br.put("coins:fn:add", PyFn(lambda a: Long(1)))
    br.put("skill:fn:addxp", PyFn(lambda a: Boolean.TRUE))
    br.put("feed:fn:push", PyFn(lambda a: Boolean.TRUE))
    u, p, s = X.player(1)
    pa = st.player("Alice", str(u))
    pb = st.player("Bob", "00000000-0000-5151-0000-0000000000b0")
    st.universe()
    ID = st.ids
    # ---------------- defaults + config.properties
    K.check(bool(Cfg.SND_ON) and all(bool(getattr(Cfg, "SND_" + f)) and str(getattr(Cfg, "SND_%s_ID" % f)) == d for _k, f, d in SOUNDS),
            "CFG defaults: master on, every sound on with its build id")
    K.check(all(d in ID for _k, _f, d in SOUNDS), "CFG every default id is a sound event of Assets.zip")
    cfgp = os.path.join(X.base, "config.properties")
    txt = open(cfgp, encoding="latin-1").read()
    K.check("sounds.enabled=true" in txt and all(("sound.%s=true" % k) in txt and ("sound.%s.id=%s" % (k, d)) in txt for k, _f, d in SOUNDS),
            "CFG a fresh config.properties lists the 9 sound lines")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("sound"))
    open(cfgp, "w", encoding="latin-1").write(old + "\nsound.task.id=SFX_Coins_Hit\n")
    Cfg.SND_TASK_ID = "x"
    Cfg.load()
    K.check(bool(Cfg.SND_ON) and bool(Cfg.SND_QUEST) and str(Cfg.SND_QUEST_ID) == SOUNDS[1][2] and str(Cfg.SND_TASK_ID) == "SFX_Coins_Hit",
            "CFG a 0.3 file without the sound lines = the defaults; a typed id is read")
    open(cfgp, "w", encoding="latin-1").write(old + "\nsounds.enabled=false\nsound.talk=false\nsound.reward.id=\n")
    Cfg.load()
    K.check(not bool(Cfg.SND_ON) and not bool(Cfg.SND_TALK) and str(Cfg.SND_REWARD_ID) == "" and bool(Cfg.SND_TASK), "CFG off / off / an empty id are read")
    open(cfgp, "w", encoding="latin-1").write(txt)
    Cfg.load()
    K.check(bool(Cfg.SND_ON) and str(Cfg.SND_REWARD_ID) == SOUNDS[2][2], "CFG back to the defaults")
    # ---------------- Server Setup rows + the kit's check= hook
    Rows, Fn = X.E.P("CfgRows"), X.E.P("CfgFn")
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "quests.sounds", [("quests.sound.%s" % k, "quests.sound.%s.id" % k, d) for k, _f, d in SOUNDS])
    K.check(all(rows[k][2] == "sounds" for k in rows if k.startswith("quests.sound")) and "sounds" in [str(x) for x in Rows.CAT_IDS],
            "ROW every sound row sits in the new Sounds category")
    for k, _f, d in SOUNDS:
        key = "quests.sound.%s.id" % k
        K.check(SK.kit_check(Fn, Rows, key, SK.BAD_ID) is not None and "no sound event" in SK.kit_check(Fn, Rows, key, SK.BAD_ID),
                "CHECK %s refuses a missing id" % key)
        K.check(SK.kit_check(Fn, Rows, key, "SFX Coins") is not None, "CHECK %s refuses a space" % key)
        K.check(SK.kit_check(Fn, Rows, key, "") is None and SK.kit_check(Fn, Rows, key, "SFX_Coins_Hit") is None and SK.kit_check(Fn, Rows, key, d) is None,
                "CHECK %s takes empty, another real id and its default" % key)
    # ---------------- QSnd itself
    K.eq(int(Snd.idx("SFX_Coins_Land")), ID["SFX_Coins_Land"], "QSnd.idx = the game's index")
    K.check(int(Snd.idx(SK.BAD_ID)) == -2147483648 and int(Snd.idx("")) == -2147483648 and int(Snd.idx(None)) == -2147483648, "QSnd.idx missing / empty / null")
    K.check(Snd.pick(True, True, " SFX_Coins_Land ") == "SFX_Coins_Land" and Snd.pick(False, True, "a") is None and Snd.pick(True, False, "a") is None
            and Snd.pick(True, True, "  ") is None and Snd.pick(True, True, None) is None, "QSnd.pick: master / sound / empty")
    st.clear()
    K.check(bool(Snd.playTo(pa, "SFX_Coins_Land", "t1")), "QSnd.playTo true")
    K.eq(st.sounds(), [("Alice", "SFX_Coins_Land", "UI", "2d")], "QSnd.playTo = ONE PlaySoundEvent2D (UI) to that player only")
    K.check(not bool(Snd.playTo(pa, "SFX_Coins_Land", "t1")) and len(st.sounds()) == 1, "QSnd gate: the same sound again within 0.5 s = nothing")
    K.check(bool(Snd.playTo(pa, "SFX_Coins_Hit", "t2")) and bool(Snd.playTo(pb, "SFX_Coins_Land", "t1")), "QSnd gate: another sound / another player plays")
    Snd.LAST.put(str(pa.getUuid()) + "|t1", Long(int(JClass("java.lang.System").currentTimeMillis()) - 600))
    K.check(bool(Snd.playTo(pa, "SFX_Coins_Land", "t1")), "QSnd gate: 0.6 s later it plays again")
    st.clear()
    n0 = len(Log.LINES)
    K.check(not bool(Snd.playTo(pa, SK.BAD_ID, "t3")) and not bool(Snd.playTo(pa, SK.BAD_ID, "t3")) and st.sounds() == [], "QSnd: a missing id plays nothing")
    w = [str(x) for x in list(Log.LINES)[n0:] if SK.BAD_ID in str(x)]
    K.eq(len(w), 1, "QSnd: ... and WARNs once: %s" % w)
    K.check(bool(Snd.play(u, "SFX_Coins_Break", "t4")) and st.sounds() == [("Alice", "SFX_Coins_Break", "UI", "2d")], "QSnd.play by UUID (Universe.getPlayer)")
    K.check(not bool(Snd.play(JClass("java.util.UUID")(9, 9), "SFX_Coins_Break", "t4")) and not bool(Snd.playTo(None, "SFX_Coins_Break", "t5"))
            and not bool(Snd.play(u, None, "t6")), "QSnd: a player not online / null player / null id = nothing, no throw")
    # ---------------- THE CALL SITES
    Snd.LAST.clear()
    st.clear()
    for i in range(10):
        Eng.count(u, T03.TB["break"], "Wood_Oak_Trunk", 1, "skyy-island-a1", False)
    K.check(X.done(s, "chop_logs"), "SITE chop_logs done (10 trunk breaks through QEng.count)")
    snd = st.sounds()
    K.check(("Alice", "SFX_Dungeon_Checkpoint_Activate", "UI", "2d") in snd and ("Alice", "SFX_Coins_Land", "UI", "2d") in snd and not st.sounds("Bob"),
            "SITE the task-done sound + the reward-paid sound (its coins claim paid at once) to that player only: %s" % snd)
    K.eq(len([x for x in snd if x[1] == "SFX_Dungeon_Checkpoint_Activate"]), 1, "SITE one task sound for one task")
    K.check("SFX_Event_Chapter_1_Complete_Sting" not in [x[1] for x in snd], "SITE a task that leaves the line open is not the quest sting")
    # the quest-done sting: every task of the tutorial line done, the last one reported
    Snd.LAST.clear()
    st.clear()
    L = X.L
    OUT = JClass("java.util.ArrayList")()
    OUT.add(JArray(JObject)([L, L.tasks[0], ""]))
    K.check(s.nextTask(L) is not None and bool(Eng.doneSound(p, s, OUT)) and [x[1] for x in st.sounds()] == ["SFX_Dungeon_Checkpoint_Activate"],
            "SITE doneSound with tasks left = the task sound")
    for t in L.tasks:
        s.done.put(Eng.tk(L, t), Long(1))
    Snd.LAST.clear()
    st.clear()
    K.check(s.nextTask(L) is None and bool(Eng.doneSound(p, s, OUT)) and [x[1] for x in st.sounds()] == ["SFX_Event_Chapter_1_Complete_Sting"],
            "SITE the last task of a LINE = the quest-done sting INSTEAD of the task one: %s" % st.sounds())
    Cfg.SND_QUEST = False
    Snd.LAST.clear()
    st.clear()
    Eng.doneSound(p, s, OUT)
    K.eq([x[1] for x in st.sounds()], ["SFX_Dungeon_Checkpoint_Activate"], "SITE quest sound off = the task sound still marks the done task")
    Cfg.SND_QUEST = True
    Cfg.SND_ON = False
    Snd.LAST.clear()
    st.clear()
    K.check(not bool(Eng.doneSound(p, s, OUT)) and st.sounds() == [], "SITE master off = silent")
    Cfg.SND_ON = True
    Cfg.SND_TASK_ID = ""
    Cfg.SND_QUEST = False
    K.check(not bool(Eng.doneSound(p, s, OUT)) and st.sounds() == [], "SITE an empty id = silent")
    Cfg.SND_TASK_ID, Cfg.SND_QUEST = SOUNDS[0][2], True
    for t in L.tasks:
        s.done.remove(Eng.tk(L, t))
    # the reward sound through QPay.tell (a claim text) + off
    Snd.LAST.clear()
    st.clear()
    X.Pay.tell(s, "coins|40|%s:x:1" % u, None)
    K.eq(st.sounds(), [("Alice", "SFX_Coins_Land", "UI", "2d")], "SITE QPay.tell = the reward sound")
    Cfg.SND_REWARD = False
    Snd.LAST.clear()
    st.clear()
    X.Pay.tell(s, "coins|40|%s:x:1" % u, None)
    K.check(st.sounds() == [], "SITE reward sound off = silent")
    Cfg.SND_REWARD = True
    # the talk sound: F on Marlow (QTalk.pageFor, the real dialogue logic)
    Snd.LAST.clear()
    st.clear()
    pg = Talk.pageFor(pa, "marlow")
    K.check(pg is not None and st.sounds() == [("Alice", "SFX_Drag_Items_Paper", "UI", "2d")], "SITE F on Marlow: the page + the talk sound: %s" % st.sounds())
    Cfg.SND_TALK = False
    Snd.LAST.clear()
    st.clear()
    K.check(Talk.pageFor(pa, "marlow") is not None and st.sounds() == [], "SITE talk sound off = page only")
    Cfg.SND_TALK = True
    K.check(Talk.pageFor(pa, "nobody") is None and st.sounds() == [], "SITE an unknown NPC: no page, no sound")
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    users = sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs))
    K.eq(users, ["QSnd.playTo"], "STATIC only QSnd.playTo calls SoundUtil")
    K.check(PKG + "QEng.doneSound" in g.get("QEng.after", set()) and PKG + "QSnd.play" in g.get("QPay.tell", set())
            and PKG + "QSnd.playTo" in g.get("QTalk.pageFor", set()) and PKG + "QSnd.play" in g.get("QEng.doneSound", set()),
            "STATIC after -> doneSound -> QSnd.play; tell -> QSnd.play; pageFor -> QSnd.playTo")
    K.save()


if __name__ == "__main__":
    if "--mkfake" in sys.argv:
        T03.mkfake(HK.arg("--mkfake"), JAR)
        sys.exit(0)
    if "--phase" not in sys.argv:
        shutil.rmtree(FAKE_DIR, ignore_errors=True)
        os.makedirs(FAKE_DIR, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(FAKE_DIR, "tmp")
        os.makedirs(env["TEMP"], exist_ok=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkfake", FAKE_DIR, "--jar", JAR, "--dir", SCRATCH], env=env)
        if r.returncode != 0:
            sys.exit("the stand-in classes were not compiled")
    try:
        HK.run("SkyyQuests", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
               [("snd", run_snd), ("defs", T03.run_defs), ("engine", T03.run_engine), ("life", T03.run_life), ("pay", T03.run_pay),
                ("crash", T03.run_crash), ("static", T03.run_static), ("npc", T03.run_npc), ("board", T03.run_board), ("fish", T03.run_fish),
                ("live", T03.run_live)],
               os.path.abspath(__file__), live=(T03.LIVE_DIR, "Skyy_SkyyIslands"))
    finally:
        if "--phase" not in sys.argv and "--keep" not in sys.argv:
            shutil.rmtree(FAKE_DIR, ignore_errors=True)
