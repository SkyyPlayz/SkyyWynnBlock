"""Harness for SkyyAuctions 0.1.5 (rebirth R4: ah:fn:closeall / ah:fn:wouldclose; tools/auctions_0_1_5_patch.py).
Build first: python tools/auctions_0_1_5_patch.py && python SkyyAuctions/build_skyyauctions_0.1.5.py

    python SkyyAuctions/test_skyyauctions_0.1.5.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.4 -> 0.1.5: exactly the listed members differ (+ AhRebirthFn, AhAdminCloseAllCmd, AhAdminCloseAllOkCmd)
  X  exec     EVERY NEW CODE PATH on a folder of 300 generated listings + hand-made ones for three profile keys:
              wouldclose (closable / blocking / claims / coins, one line per open listing, oldest first, tabs in names cleaned),
              closeall through the AhRebirthFn objects (= the bridge objects): ACTIVE -> CANCELLED, ended-not-expired -> EXPIRED,
              in-grace -> CANCELLED, item owed to the seller with the full quantity, rev + 1, nothing else on disk changes, the
              other-profile / buyer-side / claim / closed / read-only (v2, AUCTION) records untouched; read-only ones BLOCK
              (err:blocked:<n>:<b>); bad keys (null, "", "  ", a number) -> err:bad-key; IDEMPOTENT (second call ok:0 / blocked:0);
              CRASH AT EVERY STEP (AhStore.CRASH_AT: before each write and after each write before its log line), restart from
              disk in a fresh class loader: every listing is either still ACTIVE exactly as before or closed with its item owed -
              never both, never neither; the next call closes the rest; claims count = before + closed;
              a crash INSIDE a write (a left-over .tmp) = the old listing; a FAILED write (err:write-failed:<n>:<f>) changes
              nothing in memory or on disk, the next call finishes; the AhRebirthFn.after path (auction:count, auction:claims);
              RACE: closeall on one thread while another buys the same 40 listings (real SkyyCoins 0.1.6 ledger): every listing
              ends SOLD (buyer item owed, buyer paid its price) XOR closed (seller item owed) - coins taken = the sold prices;
              ROLLBACK: 0.1.4 loads the closed folder: same open records, same claims for every key, the closed ones claimable.
  D  live     start twice on a scratch COPY of the live Skyy_SkyyAuctions: no file changes; wouldclose for every seller key in it;
              closeall on the copy closes exactly what wouldclose listed
  AA engine-access audit
              /ahadmin closeall [confirm] (AhCmds.closeAll) with a test-only PlayerRef subclass (phase mkpr, javassist, scratch only)
              that records the chat lines: no bridge keys -> says so; preview = 4 + 2 blocking, no file change; confirm closes.
  FIX     (critic round 2026-10-14) unclaimed sale coins BLOCK (wouldclose flag-2 lines, closeall err:blocked counts them, a
          claim clears it); rebirth:busy:<uuid> = TRUE refuses list / buy / cancel / claim, FALSE / absent allows them, closeall
          itself still runs; the cancelRefundsFee comment says the Continue button keeps the fee.
  FIX 2   (critic round 2, 2026-10-14) unclaimed sale coins are checked BEFORE closeall writes anything: err:blocked:0:<b> and
          no file changes; after the claim closeall closes the rest. Crash / rollback runs claim the coins first; the race accepts
          only "closeall first (all closed, ok)" or "a sale first (nothing closed, err:blocked:0:<sales so far>)".
NOT executed here: SkyyAuctionsPlugin.setup's / shutdown's bridge put / remove lines (the smoke test boots setup).
Scratch: tools/dev/scratch/market4fix2/auctions (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, random, shutil, copy, threading, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("t014", os.path.join(HERE, "test_skyyauctions_0.1.4.py"))
T4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T4)       # reuse 0.1.4's record generator, loader + coins helpers (definitions only)

VERSION = "0.1.5"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "market4fix2", "auctions")))
PKG = "com.skyy.auctions."
LIVE_DIR = T4.LIVE_DIR
EXPECT = {
    "AhStore": ["+f CRASH_AT", "+m openFor", "+m openOf", "+m crashPoint", "+m closeAll0", "+m cleanName", "+m wouldClose0",
                "+m closeAll", "+m wouldClose", "~<clinit>",      # <clinit>: CRASH_AT = -1
                "+m coinRows", "~m refuse"],                     # fix round: unclaimed sale coins block; rebirth:busy refuses
    "AhUtil": ["+m rebirthBusy"],
    "AhCfg": ["~m load", "~m setPaused"],                # fix round: the default config text (cancelRefundsFee comment line)
    "AhCmds": ["+m closeAll", "~m status"],
    "AhAdminCmd": ["~c "],           # the constructor: + addSubCommand(AhAdminCloseAllCmd)
    "SkyyAuctionsPlugin": ["~m setup", "~m shutdown"],
}
ADDED = ["AhRebirthFn", "AhAdminCloseAllCmd", "AhAdminCloseAllOkCmd"]
uu, L = T4.uu, T4.L
K1, K2, K3 = uu(77), uu(78), uu(79)
FINISHED = ("SOLD", "EXPIRED", "CANCELLED", "REMOVED")


def mk(t, rid, key, state="ACTIVE", now=0, qty=1, ends=3600000, grace=-100000, v=1, typ="BIN", closed=False, claims=None, buyer=None, name=None):
    r = copy.deepcopy(t)
    r["id"] = str(rid)
    r["v"] = {"$numberInt": str(v)}
    r["type"] = typ
    r["state"] = state
    r["closed"] = closed
    r["rev"] = L(3)
    u = key[:36]
    r["seller"] = {"uuid": u, "key": key, "name": "Seller%s" % u[:8], "profile": "P"}
    r["buyer"] = buyer
    r["sale"] = {"gross": L(500), "tax": L(0), "net": L(500)} if state == "SOLD" else None
    c = {"sellerCoins": "NONE", "sellerItem": "NONE", "buyerItem": "NONE", "sellerItemQty": L(qty), "buyerItemQty": L(qty)}
    c.update(claims or {})
    r["claims"] = c
    r.setdefault("item", {})
    r["item"]["qty"] = L(qty)
    r["price"] = L(100 + rid)
    r["endsAt"] = L(now + ends)
    r["graceUntil"] = L(now + grace)
    r["createdAt"] = L(now - 200000)
    r["fee"] = {"listing": L(5), "duration": L(20), "refunded": False}
    r["noticed"] = {"seller": False}
    r["removed"] = None
    r["regrants"] = []
    r["closedAt"] = L(now - 1000 if closed else 0)
    r["name"] = name or ("Item %d" % rid)
    r["search"] = "item %d" % rid
    r["category"] = "WEAPONS"
    return r


def build_folder(home, now):
    t = T4.template()
    recs = T4.gen_records(300, now, 515)
    hand = [
        mk(t, 1001, K1, now=now, qty=3, name="Sharp\tCopper\nSword"),
        mk(t, 1002, K1, now=now, qty=1, grace=20000),                      # in grace
        mk(t, 1003, K1, now=now, qty=7, ends=-5000),                       # ended, the tick has not expired it yet
        mk(t, 1004, K1, now=now, qty=2),
        mk(t, 1005, K1, "SOLD", now=now, claims={"sellerCoins": "OWED"}, buyer={"uuid": uu(3), "key": uu(3), "name": "B3", "profile": "P", "at": L(now)}),
        mk(t, 1006, K1, "EXPIRED", now=now, qty=4, claims={"sellerItem": "OWED"}),
        mk(t, 1007, K1, now=now, v=2),                                     # newer schema: read-only -> blocks
        mk(t, 1008, K1, now=now, typ="AUCTION"),                           # an auction type (bids) -> blocks
        mk(t, 1009, K1, "CANCELLED", now=now, closed=True),                # closed -> archived at load
        mk(t, 1010, K1 + "-p2", now=now),                                  # another profile of the same account
        mk(t, 1011, uu(4), now=now),                                       # someone else's listing ...
        mk(t, 2001, K2, now=now, qty=5),
        mk(t, 2002, K2, now=now, qty=1),
        mk(t, 2003, K2, now=now, qty=9, ends=-1),
    ]
    T4.write_records(home, recs + hand)
    open(os.path.join(home, "state.properties"), "w").write("nextId=3000\n")
    return recs + hand


class Ah(T4.Ah):
    def __init__(self, jar, home):
        T4.Ah.__init__(self, jar, home)
        from jpype import JClass
        self.Fn = JClass(PKG + "AhRebirthFn", loader=self.L) if jar != OLD_JAR else None
        self.Idx = JClass(PKG + "AhIdx", loader=self.L)

    def close(self, key):
        return str(self.Fn(0).apply(key))

    def would(self, key):
        return str(self.Fn(1).apply(key))


def disk(home):
    return T4.listings(home)


def head(w):
    return w.split("\n")[0]


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys, UUID = JClass("java.lang.System"), JClass("java.util.UUID")
    now = int(Sys.currentTimeMillis())
    base = os.path.join(scratch, "base", "Skyy_SkyyAuctions")
    build_folder(base, now)
    CS = T4.coins_on_bridge(scratch)
    CLOSABLE = ["1001", "1002", "1003", "1004"]
    QTY = {"1001": 3, "1002": 1, "1003": 7, "1004": 2}

    def fresh(tag):
        h = os.path.join(scratch, tag, "Skyy_SkyyAuctions")
        shutil.rmtree(os.path.dirname(h), ignore_errors=True)
        shutil.copytree(base, h)
        return h

    # ---- wouldclose
    h = fresh("w")
    a = Ah(jar, h)
    a.start()
    d_start = disk(h)
    w = a.would(K1)
    hd = head(w).split(":")
    owed0 = [int(x) for x in a.S.owedFor(K1)]
    K.eq(hd[:3], ["ok", "4", "3"], "X wouldclose(K1): 4 closable, 3 blocking = 2 read-only + 1 unclaimed sale (%s)" % head(w))
    K.eq([int(hd[3]), int(hd[4])], owed0[:2], "X wouldclose(K1): claims + coins = owedFor (%s)" % owed0)
    rows = [l.split("\t") for l in w.split("\n")[1:]]
    K.eq([r[0] for r in rows], CLOSABLE + ["1007", "1008", "1005"], "X wouldclose(K1): one line per open listing, oldest id first, then the unclaimed sale")
    K.eq([r[1] for r in rows], ["1", "1", "1", "1", "0", "0", "2"], "X wouldclose(K1): closable 1 / blocking 0 / unclaimed sale coins 2")
    K.eq(rows[6][2:5], ["1", "500", "0"], "FIX wouldclose: the unclaimed-sale line carries qty, the coins owed and 0")
    K.eq([r[2] for r in rows[:4]], ["3", "1", "7", "2"], "X wouldclose(K1): quantities")
    K.eq(rows[0][5], "Sharp Copper Sword", "X wouldclose: tab / line break in a name -> space")
    K.check(all(len(r) == 6 for r in rows), "X wouldclose: 6 tab-separated fields per line")
    K.eq(head(a.would(K2)).split(":")[:3], ["ok", "3", "0"], "X wouldclose(K2)")
    K.eq(a.would(uu(999)), "ok:0:0:0:0", "X wouldclose of a key with nothing")
    for bad in (None, "", "   ", JInt(5)):
        K.eq(str(a.Fn(1).apply(bad)), "err:bad-key", "X wouldclose(%r) = err:bad-key" % (bad,))
        K.eq(str(a.Fn(0).apply(bad)), "err:bad-key", "X closeall(%r) = err:bad-key" % (bad,))
    K.check(disk(h) == d_start, "X wouldclose + bad keys changed no file")

    # ---- FIX 2: an unclaimed sale blocks BEFORE anything closes (no listing, no fee lost for a rebirth that cannot go on)
    d_pre = disk(h)
    K.eq(a.close(K1), "err:blocked:0:3", "FIX2 closeall(K1) with an unclaimed sale: closes nothing, 2 read-only + 1 sale block")
    K.check(disk(h) == d_pre, "FIX2 the blocked closeall changed no file")
    K.eq(head(a.would(K1)).split(":")[:3], ["ok", "4", "3"], "FIX2 wouldclose unchanged after the blocked call")
    K.eq(a.close(K1), "err:blocked:0:3", "FIX2 again: same answer")
    lgp = os.path.join(h, "auctions.log")
    lg0 = open(lgp, encoding="utf8").read() if os.path.exists(lgp) else ""
    K.eq(lg0.count(" CLOSEALL "), 0, "FIX2 no CLOSEALL log line for the blocked call")
    # claiming the sale coins clears that blocking line (the coins land in the purse = counted in the rebirth balance)
    CS.set(UUID.fromString(K1), 0)
    rcl = a.S.claimCoins(UUID.fromString(K1), K1, "1005")
    K.check(bool(rcl.ok) and int(CS.get(UUID.fromString(K1))) == 500, "FIX claim the sale coins -> 500 in the purse (%s)" % rcl.msg)
    K.eq(head(a.would(K1)).split(":")[:3], ["ok", "4", "2"], "FIX wouldclose after the claim: 4 closable, only the 2 read-only block")
    K.check(all(l.split("\t")[1] != "2" for l in a.would(K1).split("\n")[1:]), "FIX no unclaimed-sale (kind 2) line left")

    # ---- closeall, no crash
    before = disk(h)
    claims_before = int(a.S.owedFor(K1)[0])
    r = a.close(K1)
    K.eq(r, "err:blocked:4:2", "X closeall(K1) closes 4, 2 read-only block")
    after = disk(h)
    for i in CLOSABLE:
        d = after[i + ".json"]
        st = "EXPIRED" if i == "1003" else "CANCELLED"
        K.check(d["state"] == st and d["claims"]["sellerItem"] == "OWED" and int(d["claims"]["sellerItemQty"]["$numberLong"]) == QTY[i]
                and int(d["rev"]["$numberLong"]) == 4 and "closeAll" in d and d["closed"] is False,
                "X closeall: #%s -> %s, item x%d owed to the seller, rev+1 (%s %s)" % (i, st, QTY[i], d["state"], d["claims"]))
    others = sorted(k for k in before if k[:-5] not in CLOSABLE)
    K.eq([k for k in others if before[k] != after.get(k)], [], "X closeall: no other listing file changed (%d)" % len(others))
    K.eq(sorted(after), sorted(before), "X closeall: no listing file appeared or vanished")
    K.eq(int(a.S.owedFor(K1)[0]), claims_before + 4, "X closeall: 4 more claims for K1")
    K.eq(int(a.Idx.owed(K1)), claims_before + 4, "X closeall: the claims index follows")
    T4.check_index(K, a, "X after closeall", int(Sys.currentTimeMillis()))
    K.eq(a.close(K1), "err:blocked:0:2", "X closeall again: nothing more (idempotent), still blocked by the 2 read-only")
    K.check(disk(h) == after, "X closeall again changed no file")
    K.eq(head(a.would(K1)).split(":")[:3], ["ok", "0", "2"], "X wouldclose after: 0 closable, 2 blocking")
    lg = open(os.path.join(h, "auctions.log"), encoding="utf8").read()
    K.eq(lg.count(" CLOSEALL "), 4, "X auctions.log: one CLOSEALL line per closed listing")
    K.check("fee-kept=25" in lg, "X auctions.log: the fee is kept and logged")
    rbuy = a.S.buy(None, UUID.fromString(uu(3)), uu(3), "B", "P", "1001", 1101)
    K.check(not bool(rbuy.ok), "X a cancelled listing can no longer be bought (%s)" % rbuy.msg)
    rc = a.S.cancel(None, UUID.fromString(K1), K1, "1002")
    K.check(not bool(rc.ok), "X a closed listing cannot be cancelled twice (%s)" % rc.msg)
    r2 = a.close(K2)
    K.eq(r2, "ok:3", "X closeall(K2): ok:3")
    K.eq(a.close(K2), "ok:0", "X closeall(K2) again: ok:0")
    K.eq(disk(h)["2003.json"]["state"], "EXPIRED", "X closeall(K2): the ended one is EXPIRED")
    K.eq(disk(h)["1010.json"]["state"], "ACTIVE", "X the other profile's listing is untouched")
    K.eq(disk(h)["1011.json"]["state"], "ACTIVE", "X someone else's listing is untouched")
    # after(): auction:count + auction:claims:<uuid> republished
    br = Sys.getProperties().get("skyy.bridge")
    br.remove("auction:claims:" + K2)
    br.put("auction:count", JClass("java.lang.Long")(-1))
    lst = JClass("java.util.ArrayList")()
    lst.add(K2)
    a.Fn.after(lst, "ok:3")
    K.eq(int(br.get("auction:claims:" + K2)), int(a.S.owedFor(K2)[0]), "X after(): auction:claims:<uuid> republished")
    K.eq(int(br.get("auction:count")), int(a.S.active(int(Sys.currentTimeMillis())).size()), "X after(): auction:count republished")
    a.Fn.after(lst, "err:blocked:2:1")
    a.Fn.after(lst, "err:write-failed:x:1")
    K.check(True, "X after(): the err forms parse without throwing")

    # ---- crash at every step, then restart from disk (a fresh class loader = a fresh server)
    steps = 2 * len(CLOSABLE)
    for step in range(steps):
        h = fresh("c%d" % step)
        a = Ah(jar, h)
        a.start()
        rcl = a.S.claimCoins(UUID.fromString(K1), K1, "1005")     # FIX 2: unclaimed sale coins would stop closeall before step 0
        K.check(bool(rcl.ok), "C%d: sale coins claimed first (%s)" % (step, rcl.msg))
        before = disk(h)
        claims0 = int(a.S.owedFor(K1)[0])
        a.S.CRASH_AT = step
        threw = False
        try:
            a.S.closeAll(K1, JClass("java.util.ArrayList")())     # the IllegalStateException = the server dying at this step
        except Exception:
            threw = True
        K.check(threw, "C%d: the crash hook fired" % step)
        a2 = Ah(jar, h)          # restart: a fresh class loader reads the folder like a new server
        a2.start()
        d = disk(h)
        want_closed = (step + 1) // 2
        closed = [i for i in CLOSABLE if d[i + ".json"]["state"] != "ACTIVE"]
        K.eq(closed, CLOSABLE[:want_closed], "C%d: after the crash exactly the first %d listings are closed on disk" % (step, want_closed))
        bad = []
        for i in CLOSABLE:
            x, o = d[i + ".json"], before[i + ".json"]
            if x["state"] == "ACTIVE":
                if x != o:
                    bad.append((i, "changed while still ACTIVE"))
            elif not (x["claims"]["sellerItem"] == "OWED" and int(x["claims"]["sellerItemQty"]["$numberLong"]) == QTY[i]):
                bad.append((i, "closed without the item owed"))
        K.eq(bad, [], "C%d: every listing is either still listed (unchanged) or closed with its item owed - never both, never neither" % step)
        K.eq([k for k in before if k[:-5] not in CLOSABLE and before[k] != d.get(k)], [], "C%d: nothing else changed" % step)
        K.eq(int(a2.S.owedFor(K1)[0]), claims0 + want_closed, "C%d: claims after restart = before + closed" % step)
        r = a2.close(K1)
        K.eq(r, "err:blocked:%d:2" % (4 - want_closed), "C%d: the next call closes the rest" % step)
        K.eq(a2.close(K1), "err:blocked:0:2", "C%d: and the one after closes nothing" % step)
        K.eq(int(a2.S.owedFor(K1)[0]), claims0 + 4, "C%d: in the end every listing's item is owed exactly once" % step)
        T4.check_index(K, a2, "C%d end" % step, int(Sys.currentTimeMillis()))
    K.notes.append("C: crash tested at %d steps (before / after each of 4 writes)" % steps)
    # the Function never throws: a crash inside closeAll0 comes back as err:exception
    h = fresh("cfn")
    a = Ah(jar, h)
    a.start()
    a.S.claimCoins(UUID.fromString(K1), K1, "1005")
    a.S.CRASH_AT = 0
    K.eq(a.close(K1), "err:exception", "C: an exception inside closeall is caught -> err:exception (never thrown to the caller)")
    a.S.CRASH_AT = -1

    # ---- crash INSIDE a write: a left-over tmp file is the unfinished write -> the old listing stays
    h = fresh("tmp")
    nxt = copy.deepcopy(disk(h)["2001.json"])
    nxt["state"] = "CANCELLED"
    open(os.path.join(h, "listings", "2001.json.tmp"), "w").write(json.dumps(nxt))
    a = Ah(jar, h)
    a.start()
    K.check(not os.path.exists(os.path.join(h, "listings", "2001.json.tmp")) and disk(h)["2001.json"]["state"] == "ACTIVE",
            "T: a crash inside the write (tmp left) -> the listing is still ACTIVE after restart")
    K.eq(a.close(K2), "ok:3", "T: then closeall closes it")

    # ---- a FAILED write: memory and disk unchanged, the next call finishes
    h = fresh("wf")
    a = Ah(jar, h)
    a.start()
    blocker = os.path.join(h, "listings", "2002.json.tmp")
    os.makedirs(blocker)
    d0 = disk(h)
    r = a.close(K2)
    K.eq(r, "err:write-failed:2:1", "W: a write that fails -> err:write-failed:<closed>:<failed>")
    K.eq(disk(h)["2002.json"], d0["2002.json"], "W: the failed listing's file is unchanged")
    K.eq(str(a.Rec.state(a.S.get("2002"))), "ACTIVE", "W: ... and memory still has it ACTIVE")
    K.eq(head(a.would(K2)).split(":")[:2], ["ok", "1"], "W: wouldclose still lists it")
    os.rmdir(blocker)
    K.eq(a.close(K2), "ok:1", "W: the next call closes it")
    K.eq(a.close(K2), "ok:0", "W: and then ok:0")

    # ---- RACE: closeall vs buys of the same listings (one lock: each listing sold XOR closed)
    h = os.path.join(scratch, "race", "Skyy_SkyyAuctions")
    t = T4.template()
    rr = [mk(t, 5000 + i, K3, now=now, qty=1 + i % 3) for i in range(40)]
    T4.write_records(h, rr)
    a = Ah(jar, h)
    a.start()
    buyer = UUID.fromString(uu(3))
    CS.set(buyer, 10 ** 7)
    ids = [r_["id"] for r_ in rr]
    res = {}

    started = threading.Event()

    def closer():
        started.wait(30)
        res["c"] = a.close(K3)

    def buyer_t():
        for n_, i in enumerate(reversed(ids)):
            if n_ == 5:
                started.set()
            a.S.buy(None, buyer, uu(3), "B3", "P", i, int(a.Rec.lng(a.S.get(i), "price", 0)) if a.S.get(i) is not None else 0)

    th = [threading.Thread(target=closer), threading.Thread(target=buyer_t)]
    for x in th:
        x.start()
    for x in th:
        x.join()
    d = disk(h)
    sold = [i for i in ids if d[i + ".json"]["state"] == "SOLD"]
    canc = [i for i in ids if d[i + ".json"]["state"] in ("CANCELLED", "EXPIRED")]
    K.eq(len(sold) + len(canc), 40, "R: every listing ended SOLD or closed (%d sold, %d closed, closeall %s)" % (len(sold), len(canc), res.get("c")))
    K.check(all(d[i + ".json"]["claims"]["buyerItem"] == "OWED" and d[i + ".json"]["claims"]["sellerItem"] == "NONE" for i in sold),
            "R: a sold listing owes its item to the buyer only")
    K.check(all(d[i + ".json"]["claims"]["sellerItem"] == "OWED" and d[i + ".json"]["claims"]["buyerItem"] == "NONE" for i in canc),
            "R: a closed listing owes its item to the seller only")
    # FIX 2: closeall is all-or-nothing against a sale: either it ran before any buy (all 40 closed, ok:40) or after >= 1 sale
    # (closes nothing, err:blocked:0:<sales so far>, every later buy succeeds) - never a half-closed profile
    rc_ = str(res.get("c"))
    nsold_at = int(rc_.split(":")[3]) if rc_.startswith("err:blocked:0:") else -1
    K.check((rc_ == "ok:40" and len(canc) == 40 and not sold)
            or (1 <= nsold_at <= 40 and len(canc) == 0 and len(sold) == 40),
            "R: closeall is all-or-nothing against the buys (%s, %d sold, %d closed)" % (rc_, len(sold), len(canc)))
    paid = sum(100 + int(i) for i in sold)
    K.eq(10 ** 7 - int(CS.get(buyer)), paid, "R: the buyer paid exactly the sold prices")
    K.notes.append("R: race %d sold / %d closed" % (len(sold), len(canc)))

    # ---- /ahadmin closeall [confirm] = AhCmds.closeAll(pr, confirm) through the bridge objects (setup's two puts, done here by hand)
    h = fresh("cmd")
    a = Ah(jar, h)
    a.start()
    Cmds = JClass(PKG + "AhCmds", loader=a.L)
    FP, pr = fake_pr(scratch, K1)
    br.remove("ah:fn:closeall")
    br.remove("ah:fn:wouldclose")
    Cmds.closeAll(pr, False)
    K.check(any("not on the bridge" in str(x) for x in FP.LINES), "M: /ahadmin closeall without the bridge keys says so")
    FP.LINES.clear()
    br.put("ah:fn:closeall", a.Fn(0))
    br.put("ah:fn:wouldclose", a.Fn(1))
    d0 = disk(h)
    Cmds.closeAll(pr, False)
    txt = [str(x) for x in FP.LINES]
    K.check(any("wouldclose on profile " + K1 + " -> ok:4:3:" in x for x in txt) and sum("would be cancelled" in x for x in txt) == 4
            and sum("BLOCKS" in x for x in txt) == 3 and any("closeall confirm" in x for x in txt), "M: /ahadmin closeall previews 4 + 3 blocking (%s)" % txt[:3])
    K.check(any("#1005" in x and "500 coins unclaimed" in x and "claim them" in x for x in txt), "FIX M: the unclaimed sale shows as a blocking coins line")
    K.check(disk(h) == d0, "M: the preview changed no file")
    FP.LINES.clear()
    Cmds.closeAll(pr, True)
    txt = [str(x) for x in FP.LINES]
    K.check(any("closeall on profile " + K1 + " -> err:blocked:0:3" in x for x in txt) and any("now open: ok:4:3:" in x for x in txt),
            "FIX2 M: /ahadmin closeall confirm with an unclaimed sale closes nothing (%s)" % txt)
    K.check(disk(h) == d0, "FIX2 M: ... no file changed")
    a.S.claimCoins(UUID.fromString(K1), K1, "1005")
    FP.LINES.clear()
    Cmds.closeAll(pr, True)
    txt = [str(x) for x in FP.LINES]
    K.check(any("closeall on profile " + K1 + " -> err:blocked:4:2" in x for x in txt) and any("now open: ok:0:2:" in x for x in txt),
            "M: after the claim /ahadmin closeall confirm closes them and shows what is left (%s)" % txt)
    K.eq(sum(1 for i in CLOSABLE if disk(h)[i + ".json"]["state"] != "ACTIVE"), 4, "M: ... on disk")
    br.remove("ah:fn:closeall")
    br.remove("ah:fn:wouldclose")

    # ---- FIX: rebirth:busy:<uuid> = TRUE refuses every AH action of that player (spec 5.4); closeall still runs
    h = fresh("busy")
    a = Ah(jar, h)
    a.start()
    Bool = JClass("java.lang.Boolean")
    u2 = UUID.fromString(K2)
    br.put("rebirth:busy:" + K2, Bool.FALSE)
    K.check(not bool(a.U.rebirthBusy(u2)), "FIX busy FALSE -> not busy")
    br.put("rebirth:busy:" + K2, Bool.TRUE)
    K.check(bool(a.U.rebirthBusy(u2)) and not bool(a.U.rebirthBusy(UUID.fromString(K1))) and not bool(a.U.rebirthBusy(None)), "FIX busy TRUE for K2 only")
    d0 = disk(h)
    for what, res_ in (("cancel", a.S.cancel(None, u2, K2, "2001")), ("buy", a.S.buy(None, u2, K2, "S2", "P", "1011", 1111)),
                       ("claimCoins", a.S.claimCoins(u2, K2, "1005"))):
        K.check(not bool(res_.ok) and "rebirth is running" in str(res_.msg), "FIX busy: %s refused (%s)" % (what, res_.msg))
    K.eq(str(a.S.refuse(u2, None, True)), "A rebirth is running on your profile - the Auction House waits until it is done.", "FIX busy: refuse() for a new listing")
    K.check(disk(h) == d0, "FIX busy: the refused actions changed no file")
    K.eq(a.close(K2), "ok:3", "FIX busy: closeall itself still runs while busy (it never asks)")
    br.put("rebirth:busy:" + K2, Bool.FALSE)
    rc = a.S.cancel(None, u2, K2, "2001")
    K.check(not bool(rc.ok) and "rebirth" not in str(rc.msg), "FIX busy FALSE again: the normal rules answer (%s)" % rc.msg)
    K.check(a.S.refuse(u2, None, False) is None, "FIX busy FALSE: refuse() allows")
    br.remove("rebirth:busy:" + K2)
    K.check(a.S.refuse(u2, None, False) is None, "FIX busy absent: refuse() allows")
    cfgtxt = open(os.path.join(h, "config.properties"), encoding="utf8").read()
    K.check("always keeps the fee, even with cancelRefundsFee=true" in cfgtxt, "FIX the cancelRefundsFee comment names the Continue exception")

    # ---- ROLLBACK: 0.1.4 reads the closed folder
    h = fresh("rb")
    a = Ah(jar, h)
    a.start()
    a.S.claimCoins(UUID.fromString(K1), K1, "1005")
    K.eq(a.close(K1), "err:blocked:4:2", "B: closeall(K1) after the claim")
    a.close(K2)
    o = Ah(OLD_JAR, h)
    n_old = o.start()
    a2 = Ah(jar, h)
    n_new = a2.start()
    K.eq(n_old, n_new, "B: 0.1.4 loads the same open records (%d)" % n_new)
    for k in [K1, K2, K1 + "-p2", uu(3), uu(4)]:
        K.eq([int(x) for x in o.S.owedFor(k)], [int(x) for x in a2.S.owedFor(k)], "B: 0.1.4 sees the same claims for %s" % k[:8])
    K.check(not bool(o.Rec.readOnly(o.S.get("1001"))) and str(o.Rec.claimField(o.S.get("1001"), "seller")) == "sellerItem",
            "B: 0.1.4 can claim a closed listing's item (not read-only)")
    K.save()


def run_mkpr(out, jar, scratch, _home):
    """a test-only PlayerRef subclass (javassist, written into the scratch folder): getUuid = the given uuid, sendMessage records the text"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST, B.SERVER_JAR], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    pr = cp.makeClass(HK.FAKE_PKG + ".FakePR", cp.get("com.hypixel.hytale.server.core.universe.PlayerRef"))
    pr.addField(JClass("javassist.CtField").make("public static java.util.ArrayList LINES = new java.util.ArrayList();", pr))
    pr.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public FakePR(java.util.UUID u) { super(null, u, \"AdminTest\", \"en_us\", null, null); }", pr))
    pr.addMethod(JClass("javassist.CtNewMethod").make(
        "public void sendMessage(com.hypixel.hytale.server.core.Message m) { LINES.add(m.getRawText()); }", pr))
    pr.writeFile(os.path.join(scratch, "fakepr"))
    K.save()


def fake_pr(scratch, uuid):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(os.path.join(scratch, "fakepr")).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
    F = JClass(HK.FAKE_PKG + ".FakePR", loader=ld)
    return F, F(JClass("java.util.UUID").fromString(uuid))


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    mk_ = os.path.join(os.path.dirname(LIVE_DIR), "Skyy_Market")
    if os.path.isdir(mk_) and not os.path.isdir(os.path.join(os.path.dirname(home), "Skyy_Market")):
        shutil.copytree(mk_, os.path.join(os.path.dirname(home), "Skyy_Market"))
    h0 = HK.tree_hash(home)
    a = None
    for start in (1, 2):
        a = Ah(jar, home)
        n = a.start()
        K.eq(HK.tree_hash(home), h0, "D%d: no file changed" % start)
        K.notes.append("D%d: %d open records" % (start, n))
    keys = set()
    it = a.S.LIVE.values().iterator()
    while it.hasNext():
        keys.add(str(a.Rec.subStr(it.next(), "seller", "key", "")))
    tot = 0
    for k in sorted(keys):
        w = a.would(k)
        hd = head(w).split(":")
        K.check(hd[0] == "ok", "D: wouldclose(%s) = %s" % (k[:8], head(w)))
        r = a.close(k)
        sales = sum(1 for l in w.split("\n")[1:] if l.split("\t")[1:2] == ["2"])
        want = ("ok:%s" % hd[1]) if hd[2] == "0" else ("err:blocked:0:%s" % hd[2]) if sales else ("err:blocked:%s:%s" % (hd[1], hd[2]))
        K.eq(r, want, "D: closeall(%s) closes what wouldclose listed (nothing while %d sale(s) unclaimed)" % (k[:8], sales))
        tot += 0 if sales else int(hd[1])
    K.notes.append("D: %d seller keys with open records, %d listings closed on the COPY" % (len(keys), tot))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("mkpr", run_mkpr), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
