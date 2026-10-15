"""Harness for SkyyBazaar 0.1.12 (SOUND PASS ROUND 2: buy done / sell done + the per-player sound switch; tools/bazaar_0_1_12_patch.py).
Build first: python tools/bazaar_0_1_12_patch.py && python SkyyBazaar/build_skyybazaar_0.1.12.py

    python SkyyBazaar/test_skyybazaar_0.1.12.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.11 -> 0.1.12: + BzSnd; Trader.buy0 / sell0 (the sting), the plugin setup, the kit's rows / version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, the kit's check=
     hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE CALL SITES' call BzSnd.play(u, 0 | 1)
     with the stub buyer / seller (buy sting, sell sting, muted = silent, a Sell inventory burst = ONE sting); static: buy0 / sell0 play it
     on their ONE success return only (after the "bought" / "sold" result is built, never on a refusal), setup loads the file before the
     kit, only BzSnd.playTo calls SoundUtil; KIT end to end (cmdSetConsole edits, file lines)
  D  live     0.1.11's start-twice phase on a scratch COPY of the live Skyy_SkyyBazaar (now 0.1.11 vs 0.1.12: same products / pricing /
              quotes, the second start changes nothing), then the 0.1.12 setup data steps + BzSnd.load + the kit TWICE: the first
              adds only sounds.properties, the second nothing
  AA engine-access audit
NOT driven here: a whole trade through Trader.buy0 / sell0 (needs a Player inventory + the coins bridge; 0.1.11's harnesses prove the
trade itself, unchanged) - the new line in it is the one BzSnd.play call executed above, its place proven statically.
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

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBazaar-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "bazaar")))
PKG = "com.skyy.bazaar."
SOUNDS = [dict(key="buy", field="BUY", label="Buy done", id="SFX_Coins_Land", help="A bazaar buy went through (items bought)."),
          dict(key="sell", field="SELL", label="Sell done", id="SFX_Coins_Land", help="A bazaar sale paid (one product or Sell inventory).")]
EXPECT = {
    "Trader": ["~m buy0", "~m sell0"],
    "SkyyBazaarPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>", "~m init"],
    "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["BzSnd"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T11 = tmod("test_skyybazaar_0.1.11.py", "tb0111")
T11.OLD_JAR = OLD_JAR   # its live phase compares with ITS old jar (0.1.10): now the live 0.1.11
LIVE_DIR = T11.LIVE_DIR


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    st = SK.Stage()
    ua, ub = "00000000-0000-0000-0000-0000000000a1", "00000000-0000-0000-0000-0000000000b2"
    pa = st.player("Alice", ua)
    pb = st.player("Bob", ub)
    st.universe()
    L = T11.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Snd, Rows, Fn, CP = J("BzSnd"), J("CfgRows"), J("CfgFn"), J("CfgPub")
    home = os.path.join(scratch, "snd", "mods", "Skyy_SkyyBazaar")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyBazaar", SOUNDS, home)
    UUID = JClass("java.util.UUID")
    A, Bb = UUID.fromString(ua), UUID.fromString(ub)
    b = G.bridge(st.J)
    # ---- THE CALL SITES' call: BzSnd.play(u, 0) at buy0's success, BzSnd.play(u, 1) at sell0's
    Snd.LAST.clear()
    st.clear()
    K.check(bool(Snd.play(A, 0)) and st.sounds() == [("Alice", "SFX_Coins_Land", "UI", "2d")], "SITE buy done: the buyer only")
    K.check(bool(Snd.play(Bb, 1)) and st.sounds()[1:] == [("Bob", "SFX_Coins_Land", "UI", "2d")], "SITE sell done: the seller only")
    Snd.LAST.clear()
    st.clear()
    n = sum(1 for _ in range(12) if bool(Snd.play(Bb, 1)))
    K.check(n == 1 and len(st.sounds()) == 1, "SITE Sell inventory (12 products sold in one click, sell0 each) = ONE sting")
    Snd.LAST.clear()
    st.clear()
    b.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    K.check(not bool(Snd.play(A, 0)) and not bool(Snd.play(A, 1)) and st.sounds() == [], "SITE the buyer muted every sound in /settings: silent")
    b.remove("settings:sounds:" + ua)
    Snd.S_SELL = False
    K.check(not bool(Snd.play(Bb, 1)) and bool(Snd.play(A, 0)), "SITE the Sell row off: sells silent, buys still play")
    Snd.S_SELL = True
    # ---- static: the ONE success return of buy0 / sell0
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["BzSnd.playTo"], "STATIC only BzSnd.playTo calls SoundUtil")
    K.check(PKG + "BzSnd.play" in g.get("Trader.buy0", set()) and PKG + "BzSnd.play" in g.get("Trader.sell0", set())
            and PKG + "BzSnd.load" in g.get("SkyyBazaarPlugin.setup", set()), "STATIC buy0 / sell0 play the stings; setup loads sounds.properties")
    K.check(not any(PKG + "BzSnd.play" in g.get("Trader." + m, set()) for m in ("buy", "sell", "buyN", "sellN", "buyN0", "sellN0", "sellInventory")),
            "STATIC the wrappers do not play again (one sting per trade)")
    gen = open(os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION), encoding="utf8").read()
    b0 = gen[gen.index("public static {TR} buy0("):]
    b0 = b0[:b0.index('}}""", trd))')]
    s0 = gen[gen.index("public static {TR} sell0("):]
    s0 = s0[:s0.index('}}""", trd))')]
    K.check(b0.count("BzSnd.play") == 1 and b0.index("new {TR}(true, real, charged, m);") < b0.index("{PKG}.BzSnd.play(u, 0);") < b0.index("return r1;")
            and b0.count("new {TR}(true") == 1, "STATIC buy0: the sting only on its one success return (after the bought result)")
    K.check(s0.count("BzSnd.play") == 1 and s0.index("{TR} ok = new {TR}(true, removed, pay,") < s0.index("{PKG}.BzSnd.play(u, 1);") < s0.index("return ok;")
            and s0.count("new {TR}(true") == 1, "STATIC sell0: the sting only on its one success return (after the paid result)")
    K.check(gen.index("@PKG@.BzSnd.load(dir);") < gen.index("@PKG@.CfgPub.start("), "STATIC sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyBazaar", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    import json
    tmp = os.path.join(scratch, "live11.json")
    T11.run_live(tmp, jar, scratch, home)
    from jpype import JClass
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        bz = T11.Bz(jar, home)
        J = lambda n: JClass(PKG + n, loader=bz.L)
        Snd, CP = J("BzSnd"), J("CfgPub")
        t = str(Snd.load(Paths.get(home)))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBazaar"))
        K.check(t == "sounds on (2 of 2)" and int(Snd.WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        CP.shutdown()
        bz.M.flush()
        snaps.append(HK.tree_hash(home))
    # trades.log / market.properties are the market's own (flushed by the data steps both times); compare the rest
    keep = lambda h: dict((k, v) for k, v in h.items() if k not in ("trades.log", "market.properties"))
    G.live_twice(K, keep(h0), keep(snaps[0]), keep(snaps[1]))
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyBazaar", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyBazaar", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyBazaar"))
