"""Harness for SkyySacks 0.8.38 (round inv4 - tools/sacks_0_8_38_patch.py: the pocket tabs + Tannery bridges for SkyyMenu 0.3.53's inventory).
Build first:
    python tools/sacks_0_8_38_patch.py && python SkyySacks/build_skyysacks_0.8.38.py

    python SkyySacks/test_skyysacks_0.8.38.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.37 -> 0.8.38 (SackBridge.pocketList / pocketAct, SackFn.apply and the version lines only)
  P38     EXECUTED on the 0.8.0 Void stand-ins (the REAL SackPool / VoidStore / SacksPage / SackBridge / SackFn):
          LIST    sacks:fn:pocketList: the ok line (category, level, rarity, used, space, sell open), only that pocket's items, the Void
                  page's order (most first), the unpack flag (Enchanted only), the Bazaar price, zero counts left out; an unknown pocket /
                  a paused Void = off; no player on this thread / bad arguments = null
          ACT     sacks:fn:pocket: Withdraw (a number, empty = one stack, all; a full storage = refused, nothing lost), Deposit (empty =
                  all you carry, a number; none carried = refused), Sell through a fake bazaar:fn:sell (paid once, the debit on disk
                  first; a dot refused; no Bazaar = refused, nothing sold), Unpack (Enchanted -> base to the inventory; a plain item
                  refused); a double click = two separate takes (each counted); unknown op / no item = refused; FIX PASS: the list's
                  profile token = the settled key, an action with another profile's token refused (nothing moved), with the right one
                  done; the pocket modes answer null (not Long 0) on a failure. ITEM SAFETY: after every
                  step the Void + the inventory hold exactly what they held before (+ what was sold, counted once)
          TAN     sacks:fn:openTannery is the CraftHubOpen("Tannery") gate: a player who is not online -> FALSE
  F37 / S36 / BC36 / ALL35   the 0.8.37, 0.8.36 and 0.8.35 cases on THIS jar (regression)
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_37", os.path.join(HERE, "test_skyysacks_0.8.37.py"))
T37 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T37)
sys.argv = _argv
HK.run_compare = _RC
T36, T35, T089, T30, BETA = T37.T36, T37.T35, T37.T089, T37.T30, T37.BETA

VERSION = "0.8.38"
OLD_VERSION = "0.8.37"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv4", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "SackBridge": ["+m pocketAct", "+m pocketList", "+m tok"], "SackFn": ["~m apply"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LEAD, IRON_E, IRON_B = T36.LEAD, T36.IRON_E, T36.IRON_B
ORE = "Ore_Copper"


def cases38(K, L, scratch):
    from jpype import JClass, JString, JArray, JImplements, JOverride
    VS, Defs, Pool = L["VS"], L["Defs"], L["Pool"]
    fresh, write_pool, player, inv_counts, custom_item, drain, coll = (L[n] for n in ("fresh", "write_pool", "player", "inv_counts", "custom_item", "drain", "coll"))
    UUID, bridge, TPlayers, Bridge = L["UUID"], L["bridge"], L["TPlayers"], L["Bridge"]
    Fn = JClass(PKG + "SackFn")
    Obj = JClass("java.lang.Object")
    Long_ = JClass("java.lang.Long")
    cats = [str(c) for c in Defs.CATS]
    base = os.path.join(scratch, "p38")
    pools = os.path.join(base, "pools")
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0838")
    k = str(U)
    for i_ in (LEAD, IRON_E, IRON_B, ORE):
        custom_item(i_, 100)

    def mk(vals):
        drain()
        fresh(base)
        write_pool(pools, k, vals)
        VS.st(k).first = 1
        coll(U, dict((c_, 0) for c_ in cats))

    def rd(i):
        return int(Pool.get(JString(k), JString(i)))

    def call(mode, *a):
        return Fn(mode).apply(JArray(Obj)([JString(x) if isinstance(x, str) else x for x in a]))

    def plist(cat):
        s = call(20, U, cat)
        return None if s is None else str(s).split("\n")

    def act(op, iid, amt, p):
        TPlayers.P = p
        r = call(21, U, op, iid, amt)
        drain()
        return None if r is None else str(r)

    def held(p, iid):
        return int(inv_counts(p).get(iid) or 0)

    @JImplements("java.util.function.Function")
    class FakeBz(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            a = list(o)
            self.calls.append((str(a[0]), str(a[1]), int(a[2])))
            return Long_(int(a[2]) * 7)
    fz = FakeBz()

    mk({IRON_B: 300, IRON_E: 2, LEAD: 5, ORE: 40})
    # ---- LIST
    Bridge.PLAYERS = None
    K.check(call(20, U, "Smithing") is None and call(21, U, "wd", IRON_B, "1") is None, "P38 no player on this world thread -> null (nothing read, nothing moved)")
    Bridge.PLAYERS = TPlayers()
    TPlayers.P = player(storage=[])
    try:
        ls = plist("Smithing")
        head = ls[0].split("|")
        rows = [x.split("|") for x in ls[1:]]
        ids = [r_[0] for r_ in rows]
        used_sm = int(VS.usedAll(JString(k))[cats.index("Smithing")])
        K.check(head[0] == "ok" and head[1] == "Smithing" and int(head[2]) >= 0 and head[3] in [str(x) for x in Defs.RNAME] and int(head[4]) == used_sm and int(head[5]) > 0
                and head[6] in ("0", "1") and len(head) == 8 and head[7] == k, "P38 LIST the ok line: category, level, rarity, used (%d), space, sell open, the profile token (%s)" % (used_sm, head))
        K.check(set(ids) == {IRON_B, IRON_E, LEAD} and ids[0] == IRON_B and dict((r_[0], int(r_[1])) for r_ in rows) == {IRON_B: 300, IRON_E: 2, LEAD: 5},
                "P38 LIST only Smithing's items, most first, the exact counts (%s)" % rows)
        K.check(dict((r_[0], r_[2]) for r_ in rows) == {IRON_B: "0", IRON_E: "1", LEAD: "1"}, "P38 LIST the unpack flag = Enchanted items only (%s)" % rows)
        bridge.put(JString("bazaar:sell:" + LEAD), Long_(7))
        rows2 = [x.split("|") for x in plist("Smithing")[1:]]
        K.check(dict((r_[0], r_[3]) for r_ in rows2).get(LEAD) == "7" and dict((r_[0], r_[3]) for r_ in rows2).get(IRON_B) == "-1", "P38 LIST the Bazaar price for one (-1 none)")
        mn = plist("Mining")
        K.check(mn[0].startswith("ok|Mining|") and [x.split("|")[0] for x in mn[1:]] == [ORE], "P38 LIST Mining shows only its ore (%s)" % mn)
        K.check(plist("Nope")[0] == "off|No such pocket" and call(20, U) is None and call(20, "x", "Smithing") is None, "P38 LIST unknown pocket = off; bad arguments = null")
        mk({IRON_B: 300, IRON_E: 2, LEAD: 0, ORE: 40})
        K.check(LEAD not in [x.split("|")[0] for x in plist("Smithing")[1:]], "P38 LIST a zero count is left out")
        # ---- ACT: withdraw
        mk({IRON_B: 300, IRON_E: 2, LEAD: 5, ORE: 40})
        pW = player(storage=[])
        tot = lambda p, i: rd(i) + held(p, i)
        r = act("wd", IRON_B, "64", pW)
        K.check(r.startswith("+Took 64") and rd(IRON_B) == 236 and held(pW, IRON_B) == 64 and tot(pW, IRON_B) == 300, "P38 WITHDRAW 64: +Took 64, the Void 236, the bag 64 (%s)" % r)
        r = act("wd", IRON_B, "", pW)
        K.check(r.startswith("+Took 100") and tot(pW, IRON_B) == 300, "P38 WITHDRAW empty amount = one stack (100) (%s)" % r)
        r1, r2 = act("wd", IRON_B, "10", pW), act("wd", IRON_B, "10", pW)
        K.check(r1.startswith("+Took 10") and r2.startswith("+Took 10") and tot(pW, IRON_B) == 300 and rd(IRON_B) == 116, "P38 WITHDRAW a double click = two takes, each counted (%s / %s)" % (r1, r2))
        r = act("wd", IRON_B, "abc", pW)
        K.check(r.startswith("-Type a number") and rd(IRON_B) == 116, "P38 WITHDRAW a bad amount refused, nothing moved (%s)" % r)
        pF = player(storage=[(ORE, 100)], cap=1)
        r = act("wd", IRON_B, "50", pF)
        K.check(tot(pF, IRON_B) == 116 and held(pF, ORE) == 100 and (r.startswith("-Your storage is full") or r.startswith("+Took")), "P38 WITHDRAW a full storage: %s - nothing lost (Void + bag = 116)" % r)
        # ---- deposit
        r = act("dep", IRON_B, "", pW)
        K.check(r.startswith("+Put 184") and held(pW, IRON_B) == 0, "P38 DEPOSIT empty = all you carry (%s; Void %d)" % (r, rd(IRON_B)))
        K.check(rd(IRON_B) + held(pW, IRON_B) + held(pF, IRON_B) == 300, "P38 every Iron bar counted once (Void + both test bags = 300)")
        # ---- FIX PASS: the profile token (the Void page's own "your profile changed" check)
        for op_ in ("wd", "sell", "dep", "unpack"):
            TPlayers.P = pW
            v0_ = (rd(IRON_B), held(pW, IRON_B), rd(IRON_E), len(fz.calls))
            r = call(21, U, op_, IRON_E if op_ == "unpack" else IRON_B, "5", "someone-else#2")
            drain()
            K.check(r is not None and str(r).startswith("-Your profile changed") and (rd(IRON_B), held(pW, IRON_B), rd(IRON_E), len(fz.calls)) == v0_,
                    "P38 FIX %s with another profile's token: refused, nothing moved (%s)" % (op_, r))
        TPlayers.P = pW
        r = call(21, U, "wd", IRON_B, "5", k)
        drain()
        K.check(str(r).startswith("+Took 5") and rd(IRON_B) + held(pW, IRON_B) + held(pF, IRON_B) == 300, "P38 FIX Withdraw with the list's own token: done, every bar counted once (%s)" % r)
        r = call(21, U, "dep", IRON_B, "", k)
        drain()
        K.check(str(r).startswith("+Put 5") and held(pW, IRON_B) == 0, "P38 FIX Deposit with the right token puts them back (%s)" % r)
        r = act("dep", IRON_B, "", player(storage=[]))
        K.check(r.startswith("-You carry none"), "P38 DEPOSIT none carried = refused (%s)" % r)
        pD = player(storage=[(LEAD, 9)])
        r = act("dep", LEAD, "4", pD)
        K.check(r.startswith("+Put 4") and held(pD, LEAD) == 5 and rd(LEAD) == 9, "P38 DEPOSIT a number (%s)" % r)
        # ---- sell
        bridge.remove("bazaar:fn:sell")
        r = act("sell", LEAD, "3", pD)
        K.check(r.startswith("-The Bazaar cannot buy") and rd(LEAD) == 9, "P38 SELL without the Bazaar: refused, nothing sold (%s)" % r)
        bridge.put(JString("bazaar:fn:sell"), fz)
        r = act("sell", LEAD, "3", pD)
        K.check(r.startswith("+Sold 3") and rd(LEAD) == 6 and fz.calls == [(k, LEAD, 3)], "P38 SELL 3: paid once, the Void -3 (%s / %s)" % (r, fz.calls))
        r = act("sell", LEAD, "1.5", pD)
        K.check(r.startswith("-Type a number or all") and rd(LEAD) == 6 and len(fz.calls) == 1, "P38 SELL a dot refused (a sale cannot be undone) (%s)" % r)
        # ---- unpack
        pU = player(storage=[])
        r = act("unpack", IRON_E, "1", pU)
        K.check(r.startswith("+Unpacked 100") and held(pU, IRON_B) == 100 and rd(IRON_E) == 1, "P38 UNPACK one Enchanted Iron -> 100 bars in the bag (%s)" % r)
        r = act("unpack", IRON_B, "1", pU)
        K.check(r.startswith("-Pick an Enchanted item") and held(pU, IRON_B) == 100, "P38 UNPACK a plain item refused (%s)" % r)
        # ---- refusals
        K.check(act("dance", LEAD, "1", pU).startswith("-Unknown pocket action") and act("wd", "", "1", pU).startswith("-Pick an item"), "P38 unknown op / no item = refused")
        K.check(call(21, U, "wd") is None and call(21, U, "wd", IRON_B, Long_(1)) is not None, "P38 too few arguments = null; a non-text amount = the default amount")
        Bridge.PLAYERS = None
        # ---- TAN
        Th = JClass(PKG + "CraftHubOpen")
        K.check(not bool(Th(JString("Tannery")).apply(U)) and not bool(Th(JString("Tannery")).apply(JString("x"))), "P38 TAN sacks:fn:openTannery: a player who is not online / not a UUID -> FALSE")
    finally:
        Bridge.PLAYERS = None
        bridge.remove("bazaar:fn:sell")
        bridge.remove("bazaar:sell:" + LEAD)


def run_p38(out, jar, scratch, home):
    T089.void_cases = cases38
    T089.run_void(out, jar, scratch, home)


def run_static(out, jar, scratch, home):
    import subprocess, zipfile
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_38_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g = open(gen, encoding="utf8").read()
    for key in ("sacks:fn:pocketList", "sacks:fn:pocket", "sacks:fn:openTannery"):
        K.check(g.count('sbr0.put("%s"' % key) == 1, "S setup publishes %s once" % key)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.check("this.mode == 18 || this.mode == 20 || this.mode == 21) ? null" in g, "S FIX the pocket modes 20 / 21 answer null (not Long 0) when they fail")
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S no jar entry added or removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("p38", run_p38), ("f37", T37.run_f37), ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
