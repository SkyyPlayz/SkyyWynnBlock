"""Harness for SkyyCoins 0.1.9 (SOUND PASS ROUND 2: the large-payment sting + the per-player sound switch; tools/coins_0_1_9_patch.py).
Build first: python tools/coins_0_1_9_patch.py && python SkyyCoins/build_skyycoins_0.1.9.py

    python SkyyCoins/test_skyycoins_0.1.9.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.8 -> 0.1.9: + CoinSnd; PayCmd.execute, the plugin setup, the kit's rows / version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage: every Assets.zip sound id in the engine's SoundEvent
     store, stand-in players on REAL GamePacketHandlers, a stand-in Universe): tools/soundpass_gen.unit = the file (fresh / old / typed /
     off), the rows + the kit's check= hook, id / master / row / empty, the 0.5 s gate, the per-player switch settings:sounds:<uuid>
     (FALSE silent + counted, TRUE / junk / absent play), a missing id = one WARN, offline = nothing, ok(); THE CALL SITE's call
     CoinSnd.paidTo(receiver, amount) with the stub receiver: 9,999 silent, 10,000 plays (receiver only, UI 2D), muted receiver silent,
     sound.payment.min 0 = every /pay, a typed min in the file, a junk min = default + WARN; static: /pay calls it right after the
     receiver's chat line (after transfer), only CoinSnd.playTo calls SoundUtil; KIT end to end (cmdSetConsole edits, file lines)
  D  live    0.1.6's start-twice phase on a scratch COPY of the live Skyy_SkyyCoins (balances read, nothing written), then the 0.1.9 setup
     order (CoinXfer.load, CoinSnd.load, CfgPub.start) TWICE on the same copy: the first adds only sounds.properties, the second nothing
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
import soundpass_gen as G

VERSION = "0.1.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCoins-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "coins")))
PKG = "com.skyy.coins."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCoins")
SOUNDS = [dict(key="payment", field="PAYMENT", label="Large payment", id="SFX_Coins_Land",
               help="Someone /pay-ed you at least the Large payment amount.")]
EXPECT = {
    "PayCmd": ["~m execute"],
    "SkyyCoinsPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>", "~m init"],                              # the kit: the second file
    "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],   # the kit: the second file's default lines + the rows
    "CfgFn": ["~m opExport"],
}
ADDED = ["CoinSnd"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T18 = tmod("test_skyycoins_0.1.8.py", "tc018")
T16 = T18.T16
T16.OLD_JAR = OLD_JAR   # 0.1.6's live phase compares with its OLD_JAR (0.1.5, no longer built here): now the LIVE 0.1.8


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    st = SK.Stage()
    ua, ub = T16.uu(1), T16.uu(2)
    pa = st.player("Alice", ua)
    pb = st.player("Bob", ub)
    st.universe()
    L = T16.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Snd, Rows, Fn, CP = J("CoinSnd"), J("CfgRows"), J("CfgFn"), J("CfgPub")
    home = os.path.join(scratch, "snd", "mods", "Skyy_SkyyCoins")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyCoins", SOUNDS, home)
    # ---- the extra row + the file line
    rows = SK.kit_rows(Rows)
    r = rows.get("sound.payment.min")
    K.check(r is not None and r[2] == "sounds" and r[3] == "int" and r[4] == "10000" and r[5] == "0" and "live" in r[9] and r[8] == "coins",
            "ROW sound.payment.min = a live int (coins), default 10000, min 0: %s" % r)
    txt = open(os.path.join(home, "sounds.properties"), encoding="latin-1").read()
    K.check("sound.payment.min" in txt and int(Snd.PAY_MIN) == 10000, "FILE the default file explains sound.payment.min; default 10000")
    # ---- THE CALL SITE's call: CoinSnd.paidTo(target, amount) - receiver only
    Snd.LAST.clear()
    st.clear()
    K.check(not bool(Snd.paidTo(pb, 9999)) and st.sounds() == [], "SITE 9,999 coins: silent")
    K.check(bool(Snd.paidTo(pb, 10000)) and st.sounds() == [("Bob", "SFX_Coins_Land", "UI", "2d")], "SITE 10,000 coins: the sting, to the RECEIVER only")
    Snd.LAST.clear()
    st.clear()
    b = G.bridge(st.J)
    b.put("settings:sounds:" + ub, JClass("java.lang.Boolean").FALSE)
    K.check(not bool(Snd.paidTo(pb, 50000)) and st.sounds() == [], "SITE the receiver muted every sound in /settings: silent")
    b.remove("settings:sounds:" + ub)
    K.check(not bool(Snd.paidTo(None, 50000)) and not bool(Snd.paidTo(pb, 0)) and not bool(Snd.paidTo(pb, -5)), "SITE no receiver / 0 / negative: nothing")
    Snd.PAY_MIN = 0
    Snd.LAST.clear()
    st.clear()
    K.check(bool(Snd.paidTo(pb, 1)) and len(st.sounds()) == 1, "SITE sound.payment.min 0 = every /pay plays")
    Paths = JClass("java.nio.file.Paths")
    fp = os.path.join(home, "sounds.properties")
    open(fp, "w", encoding="latin-1").write("sound.payment.min=2,500\n")
    Snd.load(Paths.get(home))
    K.eq(int(Snd.PAY_MIN), 2500, "FILE a typed min (2,500) is read")
    w0 = int(Snd.WARNS.get())
    open(fp, "w", encoding="latin-1").write("sound.payment.min=lots\n")
    Snd.PAY_MIN = 10000
    Snd.load(Paths.get(home))
    K.check(int(Snd.PAY_MIN) == 10000 and int(Snd.WARNS.get()) == w0 + 1, "FILE a junk min keeps the value + one WARN")
    os.remove(fp)
    Snd.load(Paths.get(home))
    # ---- static: where /pay plays it
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["CoinSnd.playTo"], "STATIC only CoinSnd.playTo calls SoundUtil")
    K.check(PKG + "CoinSnd.paidTo" in g.get("PayCmd.execute", set()) and PKG + "CoinSnd.load" in g.get("SkyyCoinsPlugin.setup", set()),
            "STATIC /pay plays the sting; setup loads sounds.properties")
    gen = open(os.path.join(HERE, "build_skyycoins_%s.py" % VERSION), encoding="utf8").read()
    i_tr = gen.index("if (!{PKG}.CoinStore.transfer(pr.getUuid(), target.getUuid(), amount))")
    i_msg = gen.index('target.sendMessage({MSG}.raw(pr.getUsername() + " paid you "', i_tr)
    i_snd = gen.index("{PKG}.CoinSnd.paidTo(target, amount);", i_msg)
    i_load = gen.index("{PKG}.CoinSnd.load(")
    i_kit = gen.index("{PKG}.CfgPub.start(")
    K.check(i_tr < i_msg < i_snd and i_load < i_kit, "STATIC the sting only after a done transfer and the chat line; sounds.properties read before the kit starts")
    # ---- the kit end to end
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyCoins", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    import json
    tmp = os.path.join(scratch, "live16.json")
    T16.run_live(tmp, jar, scratch, home)
    from jpype import JClass, JArray
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    bal0 = HK.tree_hash(os.path.join(home, "balances"))
    snaps = []
    for start in (1, 2):
        L = T16.loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        CS, X, CP, Snd = J("CoinStore"), J("CoinXfer"), J("CfgPub"), J("CoinSnd")
        CS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCoins")
        CS.DIR = P(os.path.join(home, "balances"))
        CS.JOURNAL = P(os.path.join(home, "balances-journal.properties"))
        CS.recover()
        J("CoinConfig").FILE = P(os.path.join(home, "config.properties"))
        J("CoinConfig").load()
        X.FILE = P(os.path.join(home, "transfers.properties"))
        X.load()
        t = str(Snd.load(P(home)))
        CP.start(P(mods), CS.LOG)
        K.check(t == "sounds on (1 of 1)" and int(Snd.PAY_MIN) == 10000 and int(Snd.WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
    G.live_twice(K, h0, snaps[0], snaps[1], also=("transfers.properties",))   # 0.1.8's own file when the live copy never ran 0.1.8
    K.check(HK.tree_hash(os.path.join(home, "balances")) == bal0, "DS: no balance file changed")
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyCoins", SOUNDS, [
        "sound.payment.min = the smallest /pay (coins) that plays the Large payment sound to the receiver; 0 = every /pay."]), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCoins", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCoins"))
