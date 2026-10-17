"""Harness for SkyyAuctions 0.1.11 (round small16: AH REBIRTH AUTO-CLAIM; tools/auctions_0_1_11_patch.py). Build first:
python tools/auctions_0_1_11_patch.py && python SkyyAuctions/build_skyyauctions_0.1.11.py

    python SkyyAuctions/test_skyyauctions_0.1.11.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.10 -> 0.1.11: exactly the listed members differ (+ AhAutoClaim)
  HUB  the 0.1.10 harness's HUB phase on THIS jar: every Auction House view through SUI.assert_menu_page (kit 1.7 pages unchanged) + the
       LIST / BUY / CLAIM smoke through the page clicks
  MK   SkyyBazaar/test_skyybazaar_0.1.18.py run_mk with this jar (both Market jars together)
  RB   EXECUTED over the engine stand-ins (tools/hub_tab_harness.py: a Universe with two players, real inventories, a recording world
       task queue) + a fake SkyyCoins purse; records written to a scratch listings folder and loaded by the real AhStore.load:
       WOULD  wouldclose with auto-claim ON: unclaimed sale coins = closable kind 3 lines (SkyyRebirth 0.3.5 then offers Continue and
              shows no "Claim AH sale coins first"); OFF / no SkyyCoins / the player on another profile = the 0.1.10 kind 2 blocking lines
       CLAIM  ah:fn:closeall pays every sale claim into the purse exactly once (CLAIMED on disk, REBIRTH-CLAIM log lines, the chat line),
              then closes the listings; the re-check reads ok:0:0 (SkyyRebirth's marketClear); a second call pays nothing
       CRASH  a crash before / after each of two coin claims, then a restart from disk: the paid ones are never paid again, the rest are
              paid by the next call, nothing was closed by the crashed call; total = the owed coins exactly
       REFUSE coins:fn:add refuses -> err:blocked:0:<n>, no listing closed, the claims back to OWED, the purse unchanged
       ITEMS  the item claims are queued for after the rebirth: rebirth:busy keeps them waiting, then the AH tick hands AhAutoClaim to the
              player's world; on the world thread the items land in the real inventory (CLAIMED, once); a full inventory keeps the claim
              (nothing lost) and says so; the 10-minute queue times out cleanly
       CFG    rebirth.properties (written with the default ON, read by AhCfg.loadRebirth), the Server Setup row in CfgRows
  D    live     two opens on a scratch COPY of the live Skyy_SkyyAuctions (NewBetaTest; read-only source): nothing written
  AA   engine-access audit
Not testable here (UNVERIFIED): SkyyRebirth's real Continue in game (its page lines read kind 3 as "nothing to claim first"), the real
world thread timing after a rebirth. Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_sp = importlib.util.spec_from_file_location("ah0110test", os.path.join(HERE, "test_skyyauctions_0.1.10.py"))
T10 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T10)
TB, H = T10.TB, T10.H

VERSION = "0.1.11"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.10.jar")
BZ_JAR = T10.BZ_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "small16", "ah")))
EXPECT = {"AhCfg": ["+f RB_TEXT", "+f REBIRTH_CLAIM", "+m loadRebirth", "~<clinit>"],
          "AhCmds": ["~m closeAll", "~m status"],                           # closeAll: the kind 3 preview line; status: the version text
          "AhRebirthFn": ["+m paid", "~m apply"],
          "AhStore": ["+f AUTO", "+f AUTO_MS", "+f AUTO_WAIT", "+f CRASH_COIN", "+m autoCoins", "+m autoTick", "+m claimItemsOnly", "+m closeAll1", "+m closeAllRb",
                      "+m crashCoin", "+m itemClaims", "+m itemOwner", "+m sellerUuid", "~<clinit>", "~m closeAll0", "~m wouldClose0"],
          "AhTick": ["~m run"],
          "CfgFile": ["~<clinit>", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],   # the kit: + rebirth.properties
          "SkyyAuctionsPlugin": ["~m setup"]}
ADDED = ["AhAutoClaim"]


def L(n):
    return {"$numberLong": str(int(n))}


def run_rb(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = H.boot(scratch, jar, "rb")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = J("HubBar")
    E.br = HB.map()
    br = E.br
    TB.fake_items(E, ["Ore_Iron", "Ore_Copper", "Ingredient_Bar_Iron"])
    purse = {}
    TB.fake_coins(br, purse)
    Sto, Cfg, Fn = J("AhStore"), J("AhCfg"), J("AhRebirthFn")
    Sys = JClass("java.lang.System")
    TRUE = JClass("java.lang.Boolean").TRUE
    P, O = W.P, W.O
    u, uo = P.pr.getUuid(), O.pr.getUuid()
    k = str(u)
    now = int(Sys.currentTimeMillis())
    K.check(bool(J("Coins").ready()), "X: the fake SkyyCoins bridge is seen")
    # TEST ONLY: the stand-in Inventory has no ECS inventory components, so getCombinedStorageHotbarBackpack() (the vanilla add the claim
    # uses) is null - a subclass answers it with the real storage + hotbar containers (what the engine combines in game)
    from jpype import JClass as JC
    jp = JC("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    CICN, ICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer", "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    ct = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyAhTestInv", jp.get(INVN))
    ct.addMethod(JC("javassist.CtNewMethod").make("public %s getCombinedStorageHotbarBackpack() { return new %s(new %s[] { getStorage(), getHotbar() }); }"
                                                  % (CICN, CICN, ICN), ct))
    TI = JC(ct.toClass(JC(INVN).class_))

    def jf_(cls, name):
        c_ = cls
        while c_ is not None:
            try:
                f_ = c_.getDeclaredField(name)
                f_.setAccessible(True)
                return f_
            except Exception:
                c_ = c_.getSuperclass()
        raise KeyError(name)
    ti = TI()
    for fld in ("storage", "hotbar", "backpack", "utility", "tools", "armor"):
        jf_(JC(INVN).class_, fld).set(ti, jf_(JC(INVN).class_, fld).get(P.inv))
    jf_(P.pl.getClass(), "inventory").set(P.pl, ti)
    P.inv = ti

    def rec(i, item, qty, state="ACTIVE", coins=0, sitem=False, ends=3600000):
        d = json.loads(TB.rec_json(i, item, qty, 100 + i, ends, now, "Item %d" % i, seller="Plain", state=state, seller_uuid=k, seller_key=k))
        if state == "SOLD":
            d["sale"] = {"gross": L(coins), "tax": L(0), "net": L(coins)}
            d["claims"]["sellerCoins"] = "OWED"
            d["buyer"] = {"uuid": str(uo), "key": str(uo), "name": "Op", "profile": "P", "at": L(now)}
        if sitem:
            d["state"] = "EXPIRED"
            d["claims"]["sellerItem"] = "OWED"
        return d

    def home_with(tag, recs):
        h = os.path.join(scratch, "rb_" + tag, "Skyy_SkyyAuctions")
        ld = os.path.join(h, "listings")
        os.makedirs(ld, exist_ok=True)
        for d in recs:
            json.dump(d, open(os.path.join(ld, d["id"] + ".json"), "w", encoding="utf8"), indent=1)
        open(os.path.join(h, "state.properties"), "w").write("nextId=9000\n")
        T10.prep(E, J, h)
        return h

    def disk(h, i):
        for dp, _dn, fs in os.walk(h):          # listings/ or archive/<month>/ (a finished record is archived)
            if "%s.json" % i in fs:
                return json.load(open(os.path.join(dp, "%s.json" % i), encoding="utf8"))
        raise KeyError("no record file #%s" % i)

    def would():
        w = str(Fn(1).apply(k))
        return w.split("\n")[0].split(":"), [l.split("\t") for l in w.split("\n")[1:]]

    def close():
        return str(Fn(0).apply(k))

    def logtxt(h):
        p_ = os.path.join(h, "auctions.log")
        return open(p_, encoding="utf8").read() if os.path.exists(p_) else ""

    # ============================================================== WOULD + CLAIM (+ ITEMS)
    h = home_with("main", [rec(101, "Ore_Iron", 3), rec(102, "Ore_Iron", 1, "SOLD", 500), rec(103, "Ore_Iron", 2, "SOLD", 250),
                           rec(104, "Ore_Copper", 4, sitem=True)])
    Cfg.REBIRTH_CLAIM = True
    hd, rows = would()
    K.eq(hd[:3], ["ok", "3", "0"], "WOULD: auto-claim ON - 1 listing + 2 unclaimed sales closable, nothing blocking (%s)" % ":".join(hd))
    K.eq(sorted((r[0], r[1]) for r in rows), [("101", "1"), ("102", "3"), ("103", "3")], "WOULD: the sales are kind 3 lines (sale coins Continue claims)")
    K.eq([r[3] for r in rows if r[1] == "3"], ["500", "250"], "WOULD: a kind 3 line carries the coins owed")
    # SkyyRebirth 0.3.5's market(): kind 2 lines block, header 0 = to close -> Continue
    kind2 = sum(1 for r in rows if r[1] == "2")
    K.check(kind2 == 0 and int(hd[1]) > 0 and int(hd[2]) == 0, "WOULD: SkyyRebirth 0.3.5 reads this as 'NO  3 to close - Continue' (no kind 2 line)")
    Cfg.REBIRTH_CLAIM = False
    hd2, rows2 = would()
    K.check(hd2[:3] == ["ok", "1", "2"] and sorted(r[1] for r in rows2) == ["1", "2", "2"], "WOULD: switch OFF = the 0.1.10 rule (2 blocking kind 2 sales)")
    Cfg.REBIRTH_CLAIM = True

    @JImplements("java.util.function.Function")
    class OtherKey:
        @JOverride
        def apply(self, o):
            return "someone-else-profile"
    br.put("profile:fn:key", OtherKey())
    hd3, rows3 = would()
    br.remove("profile:fn:key")
    K.check(sorted(r[1] for r in rows3 if r[0] in ("102", "103")) == ["2", "2"], "WOULD: the player on another profile = the sales block (kind 2)")
    cget = br.remove("coins:fn:get")
    hd4, rows4 = would()
    br.put("coins:fn:get", cget)
    K.check(sorted(r[1] for r in rows4 if r[0] in ("102", "103")) == ["2", "2"], "WOULD: no SkyyCoins = the sales block (kind 2)")
    purse[k] = 1000
    n_sent = len(E.sent(P))
    r = close()
    K.eq(r, "ok:1", "CLAIM: closeall = ok:1 (the listing) after paying the 2 sales")
    K.eq(purse[k], 1750, "CLAIM: the purse got exactly 500 + 250")
    K.check(disk(h, 102)["claims"]["sellerCoins"] == "CLAIMED" and disk(h, 103)["claims"]["sellerCoins"] == "CLAIMED", "CLAIM: both sales CLAIMED on disk")
    K.check(disk(h, 101)["state"] in ("CANCELLED", "EXPIRED") and disk(h, 101)["claims"]["sellerItem"] == "OWED", "CLAIM: the listing closed, its item owed")
    lg = logtxt(h)
    K.check(lg.count(" REBIRTH-CLAIM ") == 2 and lg.count(" CLOSEALL ") == 1, "CLAIM: auctions.log - 2 REBIRTH-CLAIM + 1 CLOSEALL")
    msgs = E.strs_of(P, n_sent)
    K.check("went into your purse first" in msgs and "750" in msgs, "CLAIM: the player is told the 750 coins went into the purse first")
    hd5, rows5 = would()
    K.check(hd5[:3] == ["ok", "0", "0"], "CLAIM: the re-check = ok:0:0 (SkyyRebirth's marketClear passes) - %s" % ":".join(hd5))
    K.eq(close(), "ok:0", "CLAIM: a second closeall closes nothing")
    K.eq(purse[k], 1750, "CLAIM: ... and pays nothing again (exactly once)")
    # ITEMS: the queue, rebirth:busy, the world thread
    K.check(Sto.AUTO.get(k) is not None and str(Sto.AUTO.get(k)[0]) == k, "ITEMS: the item claims are queued for this player + profile")
    K.eq(int(Sto.autoTick(now + 14000)), 0, "ITEMS: never handed over within 15 s of closeall (the rebirth's gear reset runs first)")
    K.check(Sto.AUTO.get(k) is not None, "ITEMS: ... the entry waits")
    br.put("rebirth:busy:" + k, TRUE)
    K.eq(int(Sto.autoTick(now + 16000)), 0, "ITEMS: while the rebirth runs (rebirth:busy) nothing is handed over")
    K.check(Sto.AUTO.get(k) is not None, "ITEMS: ... the entry waits")
    br.remove("rebirth:busy:" + k)
    K.eq(int(Sto.autoTick(now + 16000)), 1, "ITEMS: rebirth over (+15 s) -> handed to the player's world")
    K.check(Sto.AUTO.get(k) is None and "AhAutoClaim" in E.queued(E.W1), "ITEMS: AhAutoClaim queued on the world (World.execute), the entry gone")
    c0, i0 = int(E.count(P, "Ore_Copper")), int(E.count(P, "Ore_Iron"))
    n_sent = len(E.sent(P))
    E.run_world(E.W1)
    K.eq([int(E.count(P, "Ore_Copper")) - c0, int(E.count(P, "Ore_Iron")) - i0], [4, 3], "ITEMS: on the world thread the 4 Copper Ore (expired) + 3 Iron Ore (closed listing) land in the inventory")
    K.check(disk(h, 104)["claims"]["sellerItem"] == "CLAIMED" and disk(h, 101)["claims"]["sellerItem"] == "CLAIMED", "ITEMS: both item claims CLAIMED on disk")
    K.check("After your rebirth" in E.strs_of(P, n_sent), "ITEMS: the player is told")
    rr = Sto.claimItemsOnly(P.pl, u, k)
    K.check(int(rr.items) == 0 and int(E.count(P, "Ore_Copper")) - c0 == 4, "ITEMS: claiming again gives nothing (exactly once)")

    # ============================================================== CRASH between the coin claims (+ restart from disk)
    for step in range(4):
        h = home_with("crash%d" % step, [rec(201, "Ore_Iron", 1, "SOLD", 100), rec(202, "Ore_Iron", 1, "SOLD", 200), rec(203, "Ore_Iron", 5)])
        purse[k] = 0
        Sto.CRASH_COIN = step
        r = close()
        Sto.CRASH_COIN = -1
        paid_first = step >= 1
        paid_second = step >= 3
        want = (100 if paid_first else 0) + (200 if paid_second else 0)
        K.check(r == "err:exception" and purse[k] == want, "CRASH%d: the crash hook fired (%s), paid so far %d (want %d)" % (step, r, purse[k], want))
        K.check(disk(h, 203)["state"] == "ACTIVE", "CRASH%d: the crashed call closed no listing" % step)
        K.eq([disk(h, 201)["claims"]["sellerCoins"], disk(h, 202)["claims"]["sellerCoins"]],
             ["CLAIMED" if paid_first else "OWED", "CLAIMED" if paid_second else "OWED"], "CRASH%d: on disk the paid claims are CLAIMED, the rest OWED" % step)
        T10.prep(E, J, h)          # restart: memory from disk
        r2 = close()
        K.check(r2 == "ok:1" and purse[k] == 300, "CRASH%d: after the restart the next call pays only the rest - total 300 exactly (%s, %d)" % (step, r2, purse[k]))
        K.check(close() == "ok:0" and purse[k] == 300, "CRASH%d: and the one after pays nothing" % step)
        Sto.AUTO.clear()

    # ============================================================== REFUSE (coins:fn:add refuses)
    h = home_with("refuse", [rec(301, "Ore_Iron", 1, "SOLD", 100), rec(302, "Ore_Iron", 5)])
    purse[k] = 0
    cadd = br.get("coins:fn:add")

    @JImplements("java.util.function.Function")
    class Refuse:
        @JOverride
        def apply(self, o):
            return None
    br.put("coins:fn:add", Refuse())
    r = close()
    br.put("coins:fn:add", cadd)
    K.check(r == "err:blocked:0:1" and purse[k] == 0 and disk(h, 302)["state"] == "ACTIVE" and disk(h, 301)["claims"]["sellerCoins"] == "OWED",
            "REFUSE: a refused pay = err:blocked:0:1, the listing stays, the claim back to OWED, the purse unchanged (%s)" % r)
    K.check(" REBIRTH-CLAIM-FAILED " in logtxt(h), "REFUSE: logged REBIRTH-CLAIM-FAILED")
    K.check(close() == "ok:1" and purse[k] == 100, "REFUSE: with SkyyCoins answering again the next call pays + closes")
    Sto.AUTO.clear()

    # ============================================================== ITEMS: full inventory + the queue timeout
    h = home_with("full", [rec(401, "Ore_Copper", 4, sitem=True), rec(402, "Ore_Iron", 1)])
    K.eq(close(), "ok:1", "FULL: closeall ok:1")
    from jpype import JShort, JArray
    for ic in (P.inv.getStorage(), P.inv.getHotbar()):
        for i in range(int(ic.getCapacity())):
            ic.setItemStackForSlot(JShort(i), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Ingredient_Bar_Iron", 1))
    K.eq(int(Sto.autoTick(int(Sys.currentTimeMillis()) + 16000)), 1, "FULL: handed to the world (after 15 s)")
    n_sent = len(E.sent(P))
    E.run_world(E.W1)
    K.check(disk(h, 401)["claims"]["sellerItem"] == "OWED" and disk(h, 402)["claims"]["sellerItem"] == "OWED", "FULL: a full inventory keeps both claims (nothing lost)")
    K.check("inventory is full" in E.strs_of(P, n_sent), "FULL: the player is told the items wait in /ah > Manage")
    Sto.AUTO.put(k, JArray(JClass("java.lang.Object"))([k, JClass("java.lang.Long")(now)]))
    K.eq(int(Sto.autoTick(now + 1 + int(Sto.AUTO_MS))), 0, "TIMEOUT: an entry older than 10 minutes is dropped")
    K.check(Sto.AUTO.get(k) is None and " REBIRTH-ITEMS-WAIT " in logtxt(h), "TIMEOUT: ... and logged (the items stay in /ah > Manage)")

    # ============================================================== CFG
    d_ = JClass("java.nio.file.Paths").get(h)
    rp = os.path.join(h, "rebirth.properties")
    if os.path.exists(rp):
        os.remove(rp)
    msg = str(Cfg.loadRebirth(d_))
    K.check(os.path.exists(rp) and "rebirthAutoClaim=true" in open(rp, encoding="latin-1").read() and bool(Cfg.REBIRTH_CLAIM) and "ON" in msg,
            "CFG: rebirth.properties written with the default ON and read (%s)" % msg)
    open(rp, "w", encoding="latin-1").write("rebirthAutoClaim=false\n")
    Cfg.loadRebirth(d_)
    K.check(not bool(Cfg.REBIRTH_CLAIM), "CFG: a hand edit to false is read at the next start")
    Cfg.REBIRTH_CLAIM = True
    import zipfile
    with zipfile.ZipFile(jar) as z:
        rows_ = z.read("com/skyy/auctions/CfgRows.class")
    K.check(b"rebirthAutoClaim" in rows_ and b"Skyy_SkyyAuctions/rebirth.properties" in rows_, "CFG: the Server Setup row (Auctions -> Rebirth) is in CfgRows")
    K.save()


if __name__ == "__main__":
    ph = [("hub", T10.run_hub), ("rb", run_rb)]
    if os.path.isfile(BZ_JAR):
        ph.append(("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)))
    ph.append(("live", lambda out, jar, scratch, home: H.run_live(T10.S, out, jar, scratch, home)))
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=ph, script=__file__, live=(T10.LIVE, "Skyy_SkyyAuctions"))
