"""Harness for SkyyAuctions 0.1.7 (SOUND PASS ROUND 2: bought / sold / claimed + the per-player sound switch + the config kit for the
Sounds rows; tools/auctions_0_1_7_patch.py).
Build first: python tools/auctions_0_1_7_patch.py && python SkyyAuctions/build_skyyauctions_0.1.7.py

    python SkyyAuctions/test_skyyauctions_0.1.7.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.6 -> 0.1.7: + AhSnd + the 7 config kit classes; AhStore.buy / claimCoins / claimItem / claimAll (the stings) + the silent claimCoinsQ / claimItemQ, the plugin
              setup / shutdown (sounds.properties, the kit) only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage: stand-in players on REAL GamePacketHandlers):
     tools/soundpass_gen.unit (file, rows, the kit's check= hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id,
     offline, ok()); THE CALL SITES, REAL: the 0.1.6 same-account harness setup (the REAL SkyyCoins 0.1.8 ledger on the bridge, scratch
     listings) - AhStore.buy by Bob of Sam's listing: Bob hears "bought", Sam (online) hears "sold", nobody else; a refused buy (price
     moved / gone / own listing) = silent; Bob MUTED in /settings: Sam still hears "sold", Bob nothing; Sam OFFLINE: nothing for Sam;
     claimCoins by Sam = "claimed"; a second claim of the same coins (refused) = silent; claimItem with no player (refused) = silent;
     the Sold row off = no "sold"; static: the stings sit AFTER the lock, only AhSnd.playTo calls SoundUtil; KIT end to end
  D  live     0.1.5's start-twice phase on a scratch COPY of the live Skyy_SkyyAuctions (no file changed), then the 0.1.7 data steps +
              AhSnd.load + the kit TWICE: the first adds only sounds.properties (+ kit files), the second nothing
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK
import soundpass_gen as G

_spec = importlib.util.spec_from_file_location("t016", os.path.join(HERE, "test_skyyauctions_0.1.6.py"))
T6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T6)
T5, T4 = T6.T5, T6.T4

VERSION = "0.1.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.6.jar")
COINS18 = T6.COINS18
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "auctions")))
PKG = "com.skyy.auctions."
LIVE_DIR = T6.LIVE_DIR
T5.JAR = JAR
SOUNDS = [dict(key="bought", field="BOUGHT", label="Bought", id="SFX_Coins_Hit", help="Your Buy It Now buy went through."),
          dict(key="sold", field="SOLD", label="Sold", id="SFX_Coins_Land", help="Someone bought your listing (you hear it if online)."),
          dict(key="claim", field="CLAIM", label="Claimed", id="SFX_Chest_Wooden_Open_Player", help="A claim paid coins or gave an item (Claim all = one sound).")]
EXPECT = {
    "AhStore": ["~m buy", "~m claimAll", "~m claimCoins", "+m claimCoinsQ", "~m claimItem", "+m claimItemQ"],   # fixer: Claim all = ONE sound
    "AhCmds": ["~m status"],                     # /ahadmin status: the version text
    "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["AhSnd", "CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub"]
uu = T4.uu


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    st = SK.Stage()
    SAM, BOB, ZED = uu(77), uu(3), uu(5)
    ps = st.player("Sam", SAM)
    pb = st.player("Bob", BOB)
    pz = st.player("Zed", ZED)
    st.universe()
    UUID, Paths = JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    now = int(JClass("java.lang.System").currentTimeMillis())
    # ---------------- the REAL SkyyCoins 0.1.8 ledger on the bridge
    Lc = T4.HK_loader(COINS18)
    CS = JClass("com.skyy.coins.CoinStore", loader=Lc)
    CFn = JClass("com.skyy.coins.CoinFn", loader=Lc)
    CS.DIR = Paths.get(os.path.join(scratch, "coins", "balances"))
    CS.JOURNAL = Paths.get(os.path.join(scratch, "coins", "balances-journal.properties"))
    br = CS.bridge()
    for m in ("get", "add", "take", "flush", "sameacct"):
        br.put("coins:fn:" + m, CFn(m))
    t = T4.template()
    h = os.path.join(scratch, "snd", "mods", "Skyy_SkyyAuctions")
    T4.write_records(h, [T5.mk(t, 7000 + i, SAM, now=now, qty=1) for i in range(8)])
    a = T5.Ah(jar, h)
    a.start()
    Snd = JClass(PKG + "AhSnd", loader=a.L)
    Rows, Fn, CP = JClass(PKG + "CfgRows", loader=a.L), JClass(PKG + "CfgFn", loader=a.L), JClass(PKG + "CfgPub", loader=a.L)
    # ---------------- the generic paths (own scratch folder for the file part)
    G.unit(K, st, Snd, Rows, Fn, pb, BOB, "SkyyAuctions", SOUNDS, os.path.join(scratch, "unit", "Skyy_SkyyAuctions"))
    ub, us_, uz = UUID.fromString(BOB), UUID.fromString(SAM), UUID.fromString(ZED)
    CS.set(ub, 10 ** 9)
    CS.set(uz, 10 ** 9)

    def price(i):
        return int(a.Rec.lng(a.S.get(i), "price", 0))

    def state(i):
        return str(a.Rec.state(a.S.get(i)))

    def buy(u, key, i, shown=None):
        return a.S.buy(None, u, key, "Buyer", "P1", i, price(i) if shown is None else shown)

    def fresh():
        Snd.LAST.clear()
        st.clear()
    # ---------------- THE CALL SITES, REAL
    fresh()
    r = buy(ub, BOB, "7000")
    K.check(bool(r.ok) and state("7000") == "SOLD", "SITE Bob buys Sam's listing #7000: %s" % r.msg)
    K.eq(sorted(st.sounds()), sorted([("Bob", "SFX_Coins_Hit", "UI", "2d"), ("Sam", "SFX_Coins_Land", "UI", "2d")]),
         "SITE bought -> Bob, sold -> Sam (online), nobody else, each ONE 2D UI packet")
    fresh()
    r = buy(ub, BOB, "7001", 1)
    K.check(not bool(r.ok) and state("7001") == "ACTIVE" and st.sounds() == [], "SITE a refused buy (the price moved) is silent: %s" % r.msg)
    r = buy(ub, BOB, "7000")
    K.check(not bool(r.ok) and st.sounds() == [], "SITE a refused buy (already sold) is silent: %s" % r.msg)
    r = buy(us_, SAM, "7002")
    K.check(not bool(r.ok) and st.sounds() == [], "SITE a refused buy (own listing) is silent: %s" % r.msg)
    # Bob muted: Sam still hears sold
    fresh()
    br.put("settings:sounds:" + BOB, JClass("java.lang.Boolean").FALSE)
    r = buy(ub, BOB, "7003")
    K.check(bool(r.ok) and st.sounds() == [("Sam", "SFX_Coins_Land", "UI", "2d")], "SITE Bob MUTED in /settings: Bob silent, Sam still hears sold: %s" % st.sounds())
    br.remove("settings:sounds:" + BOB)
    # Sam offline: no sold sting (Universe has no Sam)
    fresh()
    uni = st.uni
    byu = st.fld(JClass("com.hypixel.hytale.server.core.universe.Universe").class_, "playersByUuid").get(uni)
    byu.remove(us_)
    r = buy(uz, ZED, "7004")
    K.check(bool(r.ok) and st.sounds() == [("Zed", "SFX_Coins_Hit", "UI", "2d")], "SITE Sam OFFLINE: only Zed's bought: %s" % st.sounds())
    byu.put(us_, ps)
    # the Sold row off
    fresh()
    Snd.S_SOLD = False
    r = buy(ub, BOB, "7005")
    K.check(bool(r.ok) and st.sounds() == [("Bob", "SFX_Coins_Hit", "UI", "2d")], "SITE the Sold row off: only bought")
    Snd.S_SOLD = True
    # claims: Sam claims the coins of #7000 = claimed; again = refused, silent
    fresh()
    bal = int(CS.get(us_))
    r = a.S.claimCoins(us_, SAM, "7000")
    K.check(bool(r.ok) and int(CS.get(us_)) > bal and st.sounds() == [("Sam", "SFX_Chest_Wooden_Open_Player", "UI", "2d")],
            "SITE Sam claims the coins of #7000: paid + ONE claimed sting: %s" % r.msg)
    fresh()
    r = a.S.claimCoins(us_, SAM, "7000")
    K.check(not bool(r.ok) and st.sounds() == [], "SITE the same claim again (nothing owed) is silent: %s" % r.msg)
    r = a.S.claimItem(None, ub, BOB, "7000", False)
    K.check(not bool(r.ok) and st.sounds() == [], "SITE claimItem without a player (refused) is silent: %s" % r.msg)
    # Claim all: several coin claims in one click = ONE sting (the 0.5 s gate)
    fresh()
    r = a.S.claimAll(None, us_, SAM)
    K.check(int(r.coins) > 0 and st.sounds() == [("Sam", "SFX_Chest_Wooden_Open_Player", "UI", "2d")],
            "SITE Claim all (%s coins over several listings) = ONE claimed sting: %s" % (r.coins, st.sounds()))
    fresh()
    r = a.S.claimAll(None, us_, SAM)
    K.check(int(r.coins) == 0 and int(r.items) == 0 and st.sounds() == [], "SITE Claim all again (nothing owed) is silent: %s" % r.msg)
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["AhSnd.playTo"], "STATIC only AhSnd.playTo calls SoundUtil")
    K.check(all(PKG + "AhSnd.play" in g.get("AhStore." + m, set()) for m in ("buy", "claimCoins", "claimItem", "claimAll"))
            and not any(PKG + "AhSnd.play" in g.get("AhStore." + m, set()) for m in ("buy0", "claimCoins0", "claimItem0", "claimCoinsQ", "claimItemQ")),
            "STATIC the three wrappers + Claim all play; the locked bodies and the silent Q steps do not")
    gen = open(os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION), encoding="utf8").read()
    ca = g.get("AhStore.claimAll", set())
    K.check(PKG + "AhStore.claimCoinsQ" in ca and PKG + "AhStore.claimItemQ" in ca
            and PKG + "AhStore.claimCoins" not in ca and PKG + "AhStore.claimItem" not in ca,
            "STATIC FIX Claim all walks the rows through the SILENT claimCoinsQ / claimItemQ only (one sound however long the loop runs): %s" % sorted(c for c in ca if "AhStore." in c))
    w2 = gen[gen.index("public static @RES@ claimAll(@PLA@ p,"):]
    w2 = w2[:w2.index('}""")')]
    K.check(w2.count("@PKG@.AhSnd.play(") == 1 and w2.index("claimItemQ(") < w2.index("@PKG@.AhSnd.play(u, 2);") and "synchronized" not in w2,
            "STATIC FIX claimAll plays exactly once, after both loops, outside any lock")
    w = gen[gen.index("public static @RES@ buy(@PLA@ p,"):]
    w = w[:w.index('}""")')]
    K.check(w.index("synchronized (@PKG@.AhStore.class) { r = buy0(") < w.index("@PKG@.AhSnd.play(u, 0);"), "STATIC buy: the stings AFTER the lock")
    K.check(gen.index("@PKG@.AhSnd.load(dir);") < gen.index("@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());")
            and "@PKG@.CfgPub.shutdown();" in gen, "STATIC setup loads sounds.properties before the kit; shutdown flushes the kit")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyAuctions", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    tmp = os.path.join(scratch, "live15.json")
    T5.run_live(tmp, jar, scratch, home)
    from jpype import JClass
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        a = T5.Ah(jar, home)
        a.start()
        Snd, CP = JClass(PKG + "AhSnd", loader=a.L), JClass(PKG + "CfgPub", loader=a.L)
        t = str(Snd.load(Paths.get(home)))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAuctions"))
        K.check(t == "sounds on (3 of 3)" and int(Snd.WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
    G.live_twice(K, h0, snaps[0], snaps[1])
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyAuctions", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
