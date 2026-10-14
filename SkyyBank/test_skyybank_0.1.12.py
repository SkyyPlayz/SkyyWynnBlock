"""Harness for SkyyBank 0.1.12 (SOUND PASS ROUND 1: the interest payout sting; tools/bank_0_1_12_patch.py).
Build first: python tools/bank_0_1_12_patch.py && python SkyyBank/build_skyybank_0.1.12.py

    python SkyyBank/test_skyybank_0.1.12.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.11 -> 0.1.12: + BankSnd; BankConfig (3 fields, load), BankTick.sweep, the kit + version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py: every Assets.zip sound id in the engine's SoundEvent store, stand-in
     players on REAL GamePacketHandlers, a stand-in Universe): THE REAL BankTick.sweep pays a due day -> Alice (an account) gets the
     "You earned" chat line AND ONE PlaySoundEvent2D SFX_Coffer_Goblin_Reward (UI); Bob (no account) gets neither; the sound row off /
     the master off / an empty id = the chat line only; BankSnd itself (idx / err / check / pick / gate / a missing id = one WARN);
     Server Setup: the 3 rows (Sounds category, live, the default id), the kit's own check= hook; config.properties: a fresh file lists the
     3 lines, a 0.1.11 file without them = the defaults, typed values read; static: only BankSnd calls SoundUtil, sweep -> BankSnd.playTo
  RB, N, X, D every 0.1.11 phase carried forward on the 0.1.12 jar (test_skyybank_0.1.11.py's run_rb, run_name, run_exec, run_live = start
     twice on a scratch COPY of the live Skyy_SkyyBank); X and D now compare 0.1.12 with the LIVE 0.1.11 jar (their old 0.1.8 is not built)
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


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9 = tmod("test_skyybank_0.1.9.py", "tb019")
T10 = tmod("test_skyybank_0.1.10.py", "tb0110")
T11 = tmod("test_skyybank_0.1.11.py", "tb0111")

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound1", "bank")))
PKG = "com.skyy.bank."
SND = "SFX_Coffer_Goblin_Reward"
DAY = 86400000
# the 0.1.9 exec / live phases compare against T9.OLD_JAR (0.1.8, no longer built here): they now compare 0.1.12 with the LIVE 0.1.11
T9.OLD_JAR = OLD_JAR
EXPECT = {
    "BankConfig": ["+f SND_ON", "+f SND_INTEREST", "+f SND_INTEREST_ID", "~<clinit>", "~m load"],
    "BankTick": ["~m sweep"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyBankPlugin": ["~m setup"],
}
ADDED = ["BankSnd"]


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    W = T9.World()
    st = SK.Stage()
    ua, ub = W.u(1), W.u(2)
    pa = st.player("Alice", str(ua))
    pb = st.player("Bob", str(ub))
    st.universe()
    home = os.path.join(scratch, "snd", "Skyy_SkyyBank")
    bk = T9.Bank(jar, home)
    S, C, T = bk.S, bk.C, bk.T
    Snd = JClass(PKG + "BankSnd", loader=bk.L)
    Rows, Fn = JClass(PKG + "CfgRows", loader=bk.L), JClass(PKG + "CfgFn", loader=bk.L)
    Long = JClass("java.lang.Long")
    # ---------------- config.properties
    C.load()
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    K.check("sounds.enabled=true" in txt and "sound.interest=true" in txt and ("sound.interest.id=%s" % SND) in txt, "CFG a fresh config.properties lists the 3 sound lines")
    K.check(bool(C.SND_ON) and bool(C.SND_INTEREST) and str(C.SND_INTEREST_ID) == SND and SND in st.ids, "CFG defaults (the id is in Assets.zip)")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("sound")) + "\n"
    open(os.path.join(home, "config.properties"), "w", encoding="latin-1").write(old + "sound.interest.id=SFX_Coins_Land\n")
    C.SND_INTEREST_ID = "x"
    C.load()
    K.check(bool(C.SND_ON) and bool(C.SND_INTEREST) and str(C.SND_INTEREST_ID) == "SFX_Coins_Land", "CFG a 0.1.11 file without the lines = the defaults; a typed id is read")
    open(os.path.join(home, "config.properties"), "w", encoding="latin-1").write(old + "sounds.enabled=false\nsound.interest=false\nsound.interest.id=\n")
    C.load()
    K.check(not bool(C.SND_ON) and not bool(C.SND_INTEREST) and str(C.SND_INTEREST_ID) == "", "CFG off / off / empty read")
    open(os.path.join(home, "config.properties"), "w", encoding="latin-1").write(txt)
    C.load()
    # ---------------- rows + the kit's check hook
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "sounds.enabled", [("sound.interest", "sound.interest.id", SND)])
    K.check(all(rows[k][2] == "sounds" for k in ("sounds.enabled", "sound.interest", "sound.interest.id")), "ROW the Sounds category")
    K.check("no sound event" in (SK.kit_check(Fn, Rows, "sound.interest.id", SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, "sound.interest.id", "a b") is not None
            and SK.kit_check(Fn, Rows, "sound.interest.id", "") is None and SK.kit_check(Fn, Rows, "sound.interest.id", "SFX_Coins_Land") is None,
            "CHECK the kit's check= hook refuses a missing id / a space, takes empty and a real id")
    # ---------------- BankSnd itself
    st.clear()
    K.check(int(Snd.idx(SND)) == st.ids[SND] and int(Snd.idx(SK.BAD_ID)) == -2147483648, "BankSnd.idx")
    K.check(Snd.pick(True, True, SND) == SND and Snd.pick(False, True, SND) is None and Snd.pick(True, False, SND) is None and Snd.pick(True, True, " ") is None,
            "BankSnd.pick")
    K.check(bool(Snd.playTo(pa, SND, "t")) and not bool(Snd.playTo(pa, SND, "t")) and st.sounds() == [("Alice", SND, "UI", "2d")], "BankSnd.playTo once, the gate holds a repeat")
    K.check(not bool(Snd.playTo(pa, SK.BAD_ID, "u")) and not bool(Snd.playTo(None, SND, "u")) and len(st.sounds()) == 1, "BankSnd: a missing id / no player = nothing")
    Snd.LAST.clear()
    # ---------------- THE CALL SITE: the real sweep pays a due day
    T9.write_acc(home, W.key(ua), 1000000)
    bk.point(home)
    C.load()
    now = int(JClass("java.lang.System").currentTimeMillis())
    st.clear()
    C.LAST = now - DAY - 5000
    T.sweep()
    ch = [t for w, t in st.chats("Alice")]
    K.check(any("You earned" in t for t in ch), "SITE the sweep paid Alice and sent the chat line: %s" % ch)
    K.eq(st.sounds(), [("Alice", SND, "UI", "2d")], "SITE ... AND the payout sting, to Alice only (Bob has no account)")
    K.check(not st.chats("Bob"), "SITE Bob got nothing")
    for what, setup in (("the sound row off", lambda: setattr(C, "SND_INTEREST", False)), ("the master off", lambda: setattr(C, "SND_ON", False)),
                        ("an empty id", lambda: setattr(C, "SND_INTEREST_ID", ""))):
        C.load()
        setup()
        Snd.LAST.clear()
        st.clear()
        C.LAST = int(JClass("java.lang.System").currentTimeMillis()) - DAY - 5000
        T.sweep()
        K.check(any("You earned" in t for w, t in st.chats("Alice")) and st.sounds() == [], "SITE %s: the chat line only, no sound" % what)
    C.load()
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["BankSnd.playTo"], "STATIC only BankSnd.playTo calls SoundUtil")
    K.check(PKG + "BankSnd.playTo" in g.get("BankTick.sweep", set()), "STATIC the sweep plays the sting")
    K.save()


def run_exec11(out, jar, scratch, home):
    """test_skyybank_0.1.9.py's exec phase against the LIVE 0.1.11: its CONTROL checks prove 0.1.8's own bugs (no flush, the System.class
    bridge lock, the class monitor) - against a fixed old jar they have nothing to catch, so exactly those (text names 0.1.8) become notes"""
    import json
    T9.run_exec(out, jar, scratch, home)
    d = json.load(open(out))
    gone = [f for f in d["fails"] if "0.1.8" in f]
    d["fails"] = [f for f in d["fails"] if "0.1.8" not in f]
    d["notes"] = d.get("notes", []) + ["X: 0.1.8-only control (old jar = live 0.1.11, which has the fix): %s" % f for f in gone]
    json.dump(d, open(out, "w"), indent=1)


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("rb", T11.run_rb), ("name", T10.run_name), ("exec", run_exec11), ("live", T9.run_live)], script=__file__,
           live=(T9.LIVE_DIR, "Skyy_SkyyBank"))
