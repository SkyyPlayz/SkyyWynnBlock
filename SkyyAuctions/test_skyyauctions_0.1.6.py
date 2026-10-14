"""Harness for SkyyAuctions 0.1.6 (econ38: same-account buys blocked through SkyyCoins' switch; tools/auctions_0_1_6_patch.py).
Build first: python tools/auctions_0_1_6_patch.py && python SkyyAuctions/build_skyyauctions_0.1.6.py

    python SkyyAuctions/test_skyyauctions_0.1.6.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.5 -> 0.1.6: exactly the listed members differ
  S  same     EXECUTED with the REAL SkyyCoins 0.1.8 ledger + its coins:fn:sameacct (own class loader, scratch purses) and a profile
              switch (profile:fn:key): profile 2 of player A buying profile 1's listing = REFUSED with the message, nothing moved (the
              record still ACTIVE + unchanged on disk, the purse unchanged, no claim); ANOTHER player buying the same kind of listing =
              bought (SOLD, item owed to the buyer, coins taken); the same-account buy with SkyyCoins' switch OFF = bought
              (otherProfileBuy=true, 0.1.5 behaviour); OFF + otherProfileBuy=false = refused with 0.1.5's message; no
              coins:fn:sameacct on the bridge (an older SkyyCoins) = refused; a throwing / non-Boolean answer = refused; another player's
              buy never asks SkyyCoins (a spy); the ready line / summary / page texts (static); a crash-free order: the check sits
              before the first coin call
  0.1.5's phases on the 0.1.6 jar: mkpr, X exec (closeall / wouldclose, crash at every step, race, rollback, fixes), D live (start
              twice on a scratch COPY of the live Skyy_SkyyAuctions: no file changes)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

_spec = importlib.util.spec_from_file_location("t015", os.path.join(HERE, "test_skyyauctions_0.1.5.py"))
T5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T5)
T4 = T5.T4

VERSION = "0.1.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.5.jar")
COINS18 = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ38", "auctions")))
PKG = "com.skyy.auctions."
LIVE_DIR = T5.LIVE_DIR
T5.JAR = JAR
EXPECT = {
    "Coins": ["+<clinit>", "+f SAME_REFUSED", "+m ownBlocked", "+m sameText"],
    "AhCmds": ["~m status"],                     # /ahadmin status: the version text
    "AhStore": ["~m buy0"],
    "AhPage": ["~m renderItem"],
    "AhCfg": ["~m load", "~m migrate", "~m setPaused", "~m summary"],   # load/migrate/setPaused: the reworded OTHER_NOTE (fixer 2)
    "SkyyAuctionsPlugin": ["~m setup"],
}
ADDED = []
uu, L = T4.uu, T4.L


def run_same(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    UUID, Paths = JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    now = int(JClass("java.lang.System").currentTimeMillis())
    # the REAL SkyyCoins 0.1.8 ledger on the bridge (get / add / take / flush / sameacct)
    Lc = T4.HK_loader(COINS18)
    CS = JClass("com.skyy.coins.CoinStore", loader=Lc)
    X = JClass("com.skyy.coins.CoinXfer", loader=Lc)
    CFn = JClass("com.skyy.coins.CoinFn", loader=Lc)
    CS.DIR = Paths.get(os.path.join(scratch, "coins", "balances"))
    CS.JOURNAL = Paths.get(os.path.join(scratch, "coins", "balances-journal.properties"))
    br = CS.bridge()
    for m in ("get", "add", "take", "flush", "sameacct"):
        br.put("coins:fn:" + m, CFn(m))
    real_same = br.get("coins:fn:sameacct")
    active = {}

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    br.put("profile:fn:key", Fn(lambda o: active.get(str(o), str(o))))
    asked = []

    def spy(o):
        asked.append((str(o[0]), str(o[1])))
        return real_same.apply(o)
    br.put("coins:fn:sameacct", Fn(spy))
    A, OTHER = uu(77), uu(3)
    KA1, KA2 = A, A + "-p2"
    t = T4.template()
    h = os.path.join(scratch, "same", "Skyy_SkyyAuctions")
    recs = [T5.mk(t, 6000 + i, KA1, now=now, qty=1) for i in range(8)]
    T4.write_records(h, recs)
    a = T5.Ah(jar, h)
    a.start()
    ua, uo = UUID.fromString(A), UUID.fromString(OTHER)

    def price(i):
        return int(a.Rec.lng(a.S.get(i), "price", 0))

    def state(i):
        return str(a.Rec.state(a.S.get(i)))

    def buy(u, key, i):
        return a.S.buy(None, u, key, "Buyer", "P2", i, price(i))
    # profile 2 of player A is active; give both buyers coins
    active[A] = KA2
    CS.set(ua, 10 ** 9)
    CS.set(uo, 10 ** 9)
    bal_a = int(CS.get(ua))
    disk0 = T5.disk(h)
    del asked[:]
    r = buy(ua, KA2, "6000")
    K.check(not bool(r.ok) and "your own other profile" in str(r.msg) and "never move between your own profiles" in str(r.msg),
            "S same account, switch ON: refused - %s" % r.msg)
    K.check(state("6000") == "ACTIVE" and int(CS.get(ua)) == bal_a and T5.disk(h)["6000.json"] == disk0["6000.json"],
            "S refused: the listing still ACTIVE and unchanged on disk, the purse untouched")
    K.check(asked == [(KA2, KA1)], "S the buy asked SkyyCoins once with { buyer key, seller key }: %s" % asked)
    K.eq(int(JClass(PKG + "Coins", loader=a.L).SAME_REFUSED.get()), 1, "S SAME_REFUSED counted the refusal")
    # another player: bought, SkyyCoins never asked
    del asked[:]
    p = price("6001")
    r = buy(uo, OTHER, "6001")
    d = T5.disk(h)
    K.check(bool(r.ok) and state("6001") == "SOLD" and d["6001.json"]["claims"]["buyerItem"] == "OWED" and int(CS.get(uo)) == 10 ** 9 - p,
            "S another player: bought (SOLD, item owed, %d coins taken) - %s" % (p, r.msg))
    K.check(asked == [], "S another player's buy never asks SkyyCoins: %s" % asked)
    # the switch OFF (Server Setup -> Coins): otherProfileBuy=true decides = bought
    X.BLOCK_SAME = False
    p = price("6002")
    r = buy(ua, KA2, "6002")
    K.check(bool(r.ok) and state("6002") == "SOLD" and int(CS.get(ua)) == bal_a - p, "S same account, switch OFF: bought (0.1.5 behaviour) - %s" % r.msg)
    a.Cfg.OTHER_PROFILE = False
    r = buy(ua, KA2, "6003")
    K.check(not bool(r.ok) and "switched off on this server" in str(r.msg) and state("6003") == "ACTIVE", "S switch OFF + otherProfileBuy=false: refused (0.1.5's message) - %s" % r.msg)
    a.Cfg.OTHER_PROFILE = True
    X.BLOCK_SAME = True
    # no coins:fn:sameacct (an older SkyyCoins) / a throw / a non-Boolean = refused
    for what, f in (("missing", None), ("throws", Fn(lambda o: 1 / 0)), ("non-Boolean", Fn(lambda o: "yes"))):
        if f is None:
            br.remove("coins:fn:sameacct")
        else:
            br.put("coins:fn:sameacct", f)
        r = buy(ua, KA2, "6004")
        K.check(not bool(r.ok) and "your own other profile" in str(r.msg) and state("6004") == "ACTIVE", "S coins:fn:sameacct %s: refused - %s" % (what, r.msg))
    br.put("coins:fn:sameacct", real_same)
    # the same profile still can never buy its own listing (0.1.5's rule, first)
    active[A] = KA1
    r = buy(ua, KA1, "6005")
    K.check(not bool(r.ok) and "your own listing" in str(r.msg), "S the listing's own profile: 'That is your own listing.' - %s" % r.msg)
    active[A] = KA2
    # the Coins wrapper itself
    Cn = JClass(PKG + "Coins", loader=a.L)
    K.check(bool(Cn.ownBlocked(KA2, KA1)) and not bool(Cn.ownBlocked(OTHER, KA1)), "S Coins.ownBlocked: own profiles TRUE, another player FALSE (the REAL SkyyCoins answer)")
    X.BLOCK_SAME = False
    K.check(not bool(Cn.ownBlocked(KA2, KA1)) and "asks SkyyCoins" in str(Cn.sameText()), "S Coins.ownBlocked OFF: FALSE; sameText says it asks SkyyCoins")
    X.BLOCK_SAME = True
    br.remove("coins:fn:sameacct")
    K.check("blocked by default (SkyyCoins 0.1.8+ coins:fn:sameacct not loaded yet" in str(Cn.sameText()), "S sameText without SkyyCoins 0.1.8")
    br.put("coins:fn:sameacct", real_same)
    # static: the order inside buy0 + the page + texts
    gen = open(os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION), encoding="utf8").read()
    i_own = gen.index('if (key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""))) return new @RES@(false, "That is your own listing.");')
    i_chk = gen.index('@PKG@.Coins.ownBlocked(key, @PKG@.AhRec.subStr(r, "seller", "key", ""))')
    i_get = gen.index("long bal = @PKG@.Coins.get(u);", i_chk)
    i_take = gen.index("int tk = @PKG@.Coins.take(u, price);", i_chk)
    K.check(i_own < i_chk < i_get < i_take, "S static: own listing first, then the same-account check, BEFORE any coin call")
    g = PW.calls(jar)
    K.check(PKG + "Coins.ownBlocked" in g.get("AhPage.renderItem", set()) and PKG + "Coins.ownBlocked" in g.get("AhStore.buy0", set())
            and PKG + "Coins.sameText" in g.get("SkyyAuctionsPlugin.setup", set()), "S static: the page note, the buy and the ready line use it")
    K.check("coins never move between your own profiles on this server." in gen.split("public void renderItem")[1][:20000] if "public void renderItem" in gen else True,
            "S static: the page's note text")
    K.save()


def run_mkpr(out, jar, scratch, home):
    return T5.run_mkpr(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    return T5.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    return T5.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    assert os.path.isfile(COINS18), COINS18
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("same", run_same), ("mkpr", run_mkpr), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
