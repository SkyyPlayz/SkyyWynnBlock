"""Harness for SkyyPets 0.4.4 (the second egg could not go in - Skyy: "i was able to hatch one of these, but i cant hatch the second one i
made"; tools/pets_0_4_4_patch.py). Build first: python tools/pets_0_4_4_patch.py; python SkyyPets/build_skyypets_0.4.4.py

    python SkyyPets/test_skyypets_0.4.4.py [--dir <folder inside tools/dev/scratch/>]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.3 -> 0.4.4 (exactly the planned members),
              engine audit
  STATIC      the root cause in the engine bytecode (Store.copyEntity -> Component.clone -> Entity.clone -> EntityModule.getCodec, Player
              registered as a plain component, no clone override) + 0.4.3's force0 calls copyEntity, 0.4.4's the shallow holder
  REPRO       EXECUTED on the 0.4.3 jar (0.4.1's fake inventory): a forced save that failed (NOFORCE) -> the next move of that egg stays
              "=Saving your last egg move" 10 minutes later, after the player file was saved, and after a profile switch and back
  FIX         EXECUTED on the 0.4.4 jar: the same three cases go through; two eggs in a row (the forced save works); the 60 s bound;
              a take-out (credit) too; a Void line keeps its own rule; NO DUPE: each egg removed exactly once per slot, two hatches,
              a stop between the moves gives the egg back exactly once, a stop inside a place (every step) restores it
  OLD043      0.4.3's NEW phase + the 0.4.2 / 0.4.1 HATCH + PAGES phases EXECUTED on this jar (only their listed expected differences)
  LIVE        0.4.1's LIVE phase (start twice on a scratch COPY of the live Skyy_SkyyPets folder, nothing written) + LIVE2: Skyy's own
              stuck p3 record (2 open debts) on a copy: the join after the deploy settles both, nothing taken, the Combat egg goes in
Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_s43 = importlib.util.spec_from_file_location("test_skyypets_0_4_3", os.path.join(HERE, "test_skyypets_0.4.3.py"))
T43 = importlib.util.module_from_spec(_s43)
_s43.loader.exec_module(T43)
T41 = T43.T41
HK.run_compare = _cmp0

VERSION = "0.4.4"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets44", "test")))

EXPECT = {
    "PetEgg": sorted(["+f NOFORCE_MS", "+f SETTLE_MS", "+f FILEMS", "+f PDIR", "+f FILESETTLED", "+f CAPPED60", "+m playersDir", "+m fileMs",
                      "+m savedAfter", "+m why", "+f NOSAVE", "~<clinit>", "~m debts"]),
    "PetEggSave": sorted(["+f FAILS", "+f FAILED", "+m shallow", "+m noteWorld", "~<clinit>", "~m force0"]),
    "PetHatchery": sorted(["+f KICKS", "+f SWITCHED", "+m kick", "+m switchLocked", "+m switchSync", "+m switched", "~<clinit>", "~m place",
                           "~m takeOut", "~m credits"]),
    "PetTick": ["~m switched"],
    "SkyyPetsPlugin": ["~m setup"],
    # only the version text "0.4.3" -> "0.4.4" (the config.properties header + the Server Setup header; checked by hand 2026-10-18)
    "PetsCfg": ["~m applyAll", "~m seed"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = []


# ======================================================================================================== the shared world of REPRO / FIX
def _world(out, jar, scratch, tag):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    W = dict(K=K, JClass=JClass, JProxy=JProxy)
    for n in ("PetsCfg", "PetStore", "PetsLog", "PetEgg", "PetsEng", "PetHatchery", "PetTick", "PetOps"):
        W[n] = P_(n)
    Cfg, Store, Log, Eng = W["PetsCfg"], W["PetStore"], W["PetsLog"], W["PetsEng"]
    Paths, UUID, Long = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, tag + "-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    home = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    names = {}
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(names)), "byName": lambda n: None,
                                            "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: None})
    BR = Log.bridge()
    V = T41.Void()
    for k_, f_ in (("count", V.count), ("take", V.take), ("put", V.put), ("commit", V.commit)):
        BR.put("sacks:fn:" + k_, JProxy("java.util.function.Function", dict={"apply": (lambda f: (lambda a: Long(f(list(a)))))(f_)}))
    keys = {}          # uuid -> the active profile key (profile:fn:key)
    BR.put("profile:fn:key", JProxy("java.util.function.Function", dict={"apply": lambda u: keys.get(str(u))}))
    W.update(mods=mods, home=home, names=names, BR=BR, V=V, keys=keys, UUID=UUID, Long=Long, Bool=JClass("java.lang.Boolean"),
             now=lambda: int(JClass("java.lang.System").currentTimeMillis()))
    fileT = {}         # uuid -> the player file's mtime (the FILEMS seam; 0.4.4 only)
    W["fileT"] = fileT
    Egg = W["PetEgg"]
    W["fixed"] = hasattr(Egg, "FILEMS")
    if W["fixed"]:
        Egg.FILEMS = JProxy("java.util.function.Function", dict={"apply": lambda u: Long(fileT.get(str(u), -1))})
    return W


def _mk(W, n, key=None):
    Store = W["PetStore"]
    u = W["UUID"].fromString("00000000-0000-0000-0000-%012d" % n)
    W["names"][str(u)] = "P%d" % n
    if key:
        W["keys"][str(u)] = key
    k = str(Store.pkey(u))
    Store.KEYOF.put(u, k)
    r = Store.get(k)
    r.set("starter", "1")
    return u, k, r


def _place(W, u, inv, egg):
    W["PetHatchery"].CLICK.clear()
    W["PetEgg"].HATCHING.clear()
    return [None if x is None else str(x) for x in W["PetHatchery"].place(u, T41.proxy_inv(inv), egg, "harness")]


def _takeout(W, u, inv, n, hid=None):
    W["PetHatchery"].CLICK.clear()
    return [None if x is None else str(x) for x in W["PetHatchery"].takeOut(u, T41.proxy_inv(inv), n, hid, "harness")]


def _tick(W, u, r, inv, plus=0):
    """one second of the world thread for the active record: debts + credits (PetEgg.tickPlayer / PetHatchery.tickRec minus the engine)"""
    t = W["now"]() + plus
    W["PetEgg"].debts(u, r, T41.proxy_inv(inv), t)
    W["PetHatchery"].credits(u, r, T41.proxy_inv(inv), t)


def _debt_ms(r, hid):
    v = r.get("eggdebt." + hid)
    return int(str(v).split("|")[2]) if v is not None else 0


def _ledger(W):
    return T41.ledger(W["mods"])


# ---- the three cases of Skyy's bug; returns {case: True when the second move went through}
def _cases(W):
    K, Egg, Hy, Tick, Store = W["K"], W["PetEgg"], W["PetHatchery"], W["PetTick"], W["PetStore"]
    E = "Skyy_PetEgg_Combat_Common"
    got = {}
    # CASE 1 (the log of 2026-10-18): the forced save NPE'd -> force() put the hid in NOFORCE; the game saved the player 10 s later
    u, k, r = _mk(W, 4401)
    inv = T41.Inv({E: 2})
    p1 = _place(W, u, inv, E)
    K.check(p1[0].startswith("+") and inv.count(E) == 1, "CASE1 the first Common Combat Egg goes in (2 -> 1): %s" % p1[0])
    Egg.NOFORCE.put(p1[1], W["Bool"].TRUE)                     # = PetEggSave.force after the NPE (0.4.1 critic fix 4)
    inv.psave()
    W["fileT"][str(u)] = _debt_ms(r, p1[1]) + 10000             # the game's own 10 s player save wrote the file
    _tick(W, u, r, inv, 11000)
    p2 = _place(W, u, inv, E)
    _tick(W, u, r, inv, 600000)                                  # 10 minutes later
    p3 = _place(W, u, inv, E) if not p2[0].startswith("+") else p2
    got["case1"] = p2[0].startswith("+")
    got["case1_10min"] = p3[0].startswith("+")
    W["case1"] = (p2[0], p3[0], inv.count(E), int(Hy.used(r)))
    # CASE 2: the forced save failed AND the player file is unknown (another storage) -> 0.4.4: at most 60 s
    u2, k2, r2 = _mk(W, 4402)
    inv2 = T41.Inv({E: 2})
    q1 = _place(W, u2, inv2, E)
    Egg.NOFORCE.put(q1[1], W["Bool"].TRUE)
    _tick(W, u2, r2, inv2, 31000)
    q31 = _place(W, u2, inv2, E)
    _tick(W, u2, r2, inv2, 61000)
    q61 = _place(W, u2, inv2, E)
    got["case2_31s"] = q31[0].startswith("+")
    got["case2_61s"] = q61[0].startswith("+")
    W["case2"] = (q31[0], q61[0])
    # CASE 3 (16:45 in the log): a profile switch p3 -> p2 -> p3 with the move still open
    u3, k3, r3 = _mk(W, 4403, key="00000000-0000-0000-0000-000000004403-p3")
    inv3 = T41.Inv({E: 2})
    s1 = _place(W, u3, inv3, E)
    Egg.NOFORCE.put(s1[1], W["Bool"].TRUE)
    W["keys"][str(u3)] = "00000000-0000-0000-0000-000000004403-p2"
    Store.KEYOF.put(u3, W["keys"][str(u3)])
    Tick.switched(u3, k3)                                        # PetTick.second saw the key change
    W["keys"][str(u3)] = k3
    Store.KEYOF.put(u3, k3)
    Tick.switched(u3, "00000000-0000-0000-0000-000000004403-p2")
    r3 = Store.get(k3)
    _tick(W, u3, r3, inv3, 1000)
    s2 = _place(W, u3, inv3, E)
    got["case3"] = s2[0].startswith("+")
    W["case3"] = (s2[0], r3.get("eggdebt." + s1[1]), inv3.count(E))
    return got


def run_repro(out, _jar, scratch, _home):
    W = _world(out, OLD_JAR, scratch, "repro")
    K = W["K"]
    K.check(not W["fixed"], "REPRO runs on the 0.4.3 jar (no PetEgg.FILEMS)")
    g = _cases(W)
    K.check(not g["case1"] and not g["case1_10min"] and W["case1"][0].startswith("=Saving your last egg move")
            and W["case1"][1].startswith("=Saving your last egg move") and W["case1"][3] == 1,
            "REPRO 0.4.3 Skyy's bug: after the failed forced save the second Common Combat Egg stays '=Saving your last egg move' - after the game "
            "saved the player and 10 minutes later, 1 of 2 slots used: %s" % (W["case1"],))
    K.check(not g["case2_31s"] and not g["case2_61s"], "REPRO 0.4.3 no player file either: still blocked after 61 s: %s" % (W["case2"],))
    K.check(not g["case3"] and W["case3"][1] is not None, "REPRO 0.4.3 a profile switch away and back: still blocked, the old debt still open: %s" % (W["case3"],))
    K.save()


def run_fix(out, jar, scratch, _home):
    W = _world(out, jar, scratch, "fix")
    K, Egg, Hy, Store, Ops, Tick = W["K"], W["PetEgg"], W["PetHatchery"], W["PetStore"], W["PetOps"], W["PetTick"]
    Long, Bool, now = W["Long"], W["Bool"], W["now"]
    K.check(W["fixed"] and int(Egg.NOFORCE_MS) == 60000 and int(Egg.SETTLE_MS) == 5000, "FIX runs on the 0.4.4 jar: NOFORCE_MS 60 s, SETTLE_MS 5 s")
    g = _cases(W)
    K.check(g["case1"] and W["case1"][2] == 0 and W["case1"][3] == 2,
            "FIX CASE1 the failed forced save: once the game saved the player file the second Common Combat Egg goes in (1 -> 0, 2 / 2 slots): %s" % (W["case1"],))
    K.check(not g["case2_31s"] and g["case2_61s"], "FIX CASE2 no forced save and no player file: still waiting at 31 s, in at 61 s (the bound): %s" % (W["case2"],))
    K.check(g["case3"] and W["case3"][1] is None, "FIX CASE3 a profile switch settles the old profile's debt under its own key: after switching back the egg goes in: %s" % (W["case3"],))
    L = _ledger(W)
    K.check(any("hatch-debt-clear" in l and "the player file was saved after the move" in l for l in L)
            and any("hatch-debt-clear" in l and "60 s passed without a forced save" in l for l in L)
            and any("hatch-debt-clear" in l and "profile switch" in l for l in L), "FIX each clear says why (player file / 60 s / profile switch)")
    E = "Skyy_PetEgg_Mining_Common"
    # ---------------------------------------------------------------- the player file written TOO SOON after the move does not settle it
    u, k, r = _mk(W, 4411)
    inv = T41.Inv({E: 2})
    a1 = _place(W, u, inv, E)
    Egg.NOFORCE.put(a1[1], Bool.TRUE)
    W["fileT"][str(u)] = _debt_ms(r, a1[1]) + 1000            # a write that may have been queued before the move
    _tick(W, u, r, inv, 2000)
    K.check(r.get("eggdebt." + a1[1]) is not None, "FIX a player file written 1 s after the move (< 5 s) does not settle the debt")
    # ---------------------------------------------------------------- TWO EGGS IN A ROW, the forced save works (DONE)
    a2 = _place(W, u, inv, E)
    K.check(a2[0].startswith("=Saving your last egg move") and str(Egg.FORCE.get(a1[1])) == k and int(Hy.KICKS.get()) >= 1,
            "FIX a blocked second move asks for a forced save of the open line at once (FORCE, next tick): %s" % a2[0])
    Egg.NOFORCE.remove(a1[1])
    Egg.DONE.put(a1[1], Long(now()))                          # PetSaveDone: the forced save finished
    _tick(W, u, r, inv)
    a3 = _place(W, u, inv, E)
    K.check(a3[0].startswith("+") and inv.count(E) == 0 and int(Hy.used(r)) == 2, "FIX two eggs in a row: the forced save finished -> the second goes in at once: %s" % a3[0])
    # ---------------------------------------------------------------- a TAKE-OUT (credit) with a failed forced save
    u4, k4, r4 = _mk(W, 4412)
    E4 = "Skyy_PetEgg_Farming_Common"
    inv4 = T41.Inv({E4: 2})
    b1 = _place(W, u4, inv4, E4)
    Egg.DONE.put(b1[1], Long(now()))
    _tick(W, u4, r4, inv4)
    b2 = _place(W, u4, inv4, E4)
    Egg.DONE.put(b2[1], Long(now()))
    _tick(W, u4, r4, inv4)
    t1 = _takeout(W, u4, inv4, 1, b1[1])
    Egg.NOFORCE.put(t1[1], Bool.TRUE)
    t2 = _takeout(W, u4, inv4, 2, b2[1])
    v = r4.get("eggcredit." + t1[1])
    W["fileT"][str(u4)] = int(str(v).split("|")[2]) + 9000
    _tick(W, u4, r4, inv4, 9500)
    t3 = _takeout(W, u4, inv4, 2, b2[1])
    K.check(t1[0].startswith("+") and t2[0].startswith("=Saving your last egg move") and r4.get("eggcredit." + t1[1]) is None and t3[0].startswith("+")
            and inv4.count(E4) == 2 and int(Hy.used(r4)) == 0, "FIX take-outs: a failed forced save blocks only until the player file is saved: %s | %s" % (t2[0], t3[0]))
    # ---------------------------------------------------------------- a VOID line keeps its own rule (a player save does not settle it)
    u5, k5, r5 = _mk(W, 4413)
    E5 = "Skyy_PetEgg_Foraging_Common"
    W["V"].live = {E5: 2}
    W["V"].save()
    inv5 = T41.Inv({})
    c1 = _place(W, u5, inv5, E5)
    W["fileT"][str(u5)] = _debt_ms(r5, c1[1]) + 9000
    _tick(W, u5, r5, inv5, 9500)
    held = r5.get("eggdebt." + c1[1]) is not None
    _tick(W, u5, r5, inv5, 31000)
    K.check(c1[2] == "void" and held and r5.get("eggdebt." + c1[1]) is None, "FIX a Void egg's debt is not settled by the player file (the Void saves itself), 30 s as before")
    # ---------------------------------------------------------------- NO DUPE: each egg removed exactly once per slot; two hatches
    u6, k6, r6 = _mk(W, 4414)
    E6 = "Skyy_PetEgg_Exploration_Common"
    inv6 = T41.Inv({E6: 2})
    inv6.psave()
    d1 = _place(W, u6, inv6, E6)
    Egg.DONE.put(d1[1], Long(now()))
    inv6.psave()                                                 # that forced save
    _tick(W, u6, r6, inv6)
    d2 = _place(W, u6, inv6, E6)                                 # NOT saved yet - the server stops now
    K.check(d1[0].startswith("+") and d2[0].startswith("+") and inv6.count(E6) == 0 and int(Hy.used(r6)) == 2, "DUPE two places: 2 -> 0, 2 slots")
    pl = [l for l in _ledger(W) if "egg-place-done" in l and (d1[1] in l or d2[1] in l)]
    K.check(len(pl) == 2, "DUPE one egg-place-done per slot (%d)" % len(pl))

    def restart(inv):
        Egg.SESSION.clear(); Egg.DONE.clear(); Egg.FORCE.clear(); Egg.RISE.clear(); Egg.NOFORCE.clear(); Egg.HATCHING.clear(); Egg.CLICK.clear()
        Hy.CLICK.clear(); Hy.NOTIFIED.clear()
        Egg.FAULT = 0
        Store.REC.clear()
        Store.INDEX.clear()
        Store.scanAll()
        Egg.recover()
        Hy.recover()
        if inv is not None:
            inv.restart()

    def join(u_, k_, inv_):
        Store.KEYOF.put(u_, k_)
        r_ = Store.get(k_)
        _tick(W, u_, r_, inv_)
        Hy.checks(u_, r_, T41.proxy_inv(inv_))
        return r_

    def total(k_, inv_, egg):
        f = T41.props(os.path.join(W["home"], "pets", k_ + ".properties"))
        slots = sum(1 for kk, vv in f.items() if kk.startswith("hatchery.") and vv.startswith(egg + "|"))
        pets = sum(1 for kk, vv in f.items() if kk.endswith(".src") and vv.startswith("egg:%s:" % egg))
        return inv_.count(egg) + slots + pets
    restart(inv6)                                                # the player file holds 1 egg (after the first move)
    K.check(inv6.count(E6) == 1, "DUPE the stop: the second egg came back in the inventory (1)")
    r6 = join(u6, k6, inv6)
    K.check(inv6.count(E6) == 0 and total(k6, inv6, E6) == 2 and any("hatch-reconcile %s" % d2[1] in l for l in _ledger(W)),
            "DUPE the join after the stop takes the returned egg back exactly once: 0 in the inventory + 2 slots = the 2 there were")
    Egg.DONE.put(d2[1], Long(now()))
    inv6.psave()
    _tick(W, u6, r6, inv6)
    Hy.CLOCK_OFF = 3 * 3600 * 1000
    h1 = [str(x) for x in Hy.hatch(u6, 1, None, "harness")]
    Hy.CLICK.clear(); Egg.HATCHING.clear()
    h2 = [str(x) for x in Hy.hatch(u6, 2, None, "harness")]
    Hy.CLOCK_OFF = 0
    K.check(h1[0].startswith("+You hatched") and h2[0].startswith("+You hatched") and inv6.count(E6) == 0 and total(k6, inv6, E6) == 2
            and int(Hy.used(r6)) == 0, "DUPE both hatch: 2 pets, 0 eggs, nothing taken twice: %s | %s" % (h1[0][:50], h2[0][:50]))
    K.check(not list(r6.keysWith("eggdebt.")) and not list(r6.keysWith("eggcredit.")), "DUPE no debt / credit left")
    # a stop INSIDE a place (after every step 11-14): the egg is back, nothing open (0.4.1's CRASH phase does every move kind - OLD043)
    bad = []
    for st_ in (11, 12, 13, 14):
        u7, k7, r7 = _mk(W, 4420 + st_)
        inv7 = T41.Inv({E6: 1})
        inv7.psave()
        e0 = total(k7, inv7, E6)
        Egg.FAULT = st_
        try:
            _place(W, u7, inv7, E6)
        except Exception:
            pass
        Egg.FAULT = 0
        restart(inv7)
        r7 = join(u7, k7, inv7)
        if total(k7, inv7, E6) != e0:
            bad.append((st_, total(k7, inv7, E6), e0))
    K.check(not bad, "DUPE a stop after each place step 11-14: the egg is in the inventory or in a slot, never both, never gone: %s" % bad)
    # ---------------------------------------------------------------- review F1: ORPHAN lines (from before a restart) survive a switch right after the join
    def switch_away_and_back(u_, ka, kb):
        W["keys"][str(u_)] = kb
        Store.KEYOF.put(u_, kb)
        Tick.switched(u_, ka)                                    # within ~1 s of the join: no debts / credits tick ran yet
        held_ = T41.props(os.path.join(W["home"], "pets", ka + ".properties"))
        W["keys"][str(u_)] = ka
        Store.KEYOF.put(u_, ka)
        Tick.switched(u_, kb)
        return held_
    ka, kb = "00000000-0000-0000-0000-000000004430-p3", "00000000-0000-0000-0000-000000004430-p2"
    u8, k8, r8 = _mk(W, 4430, key=ka)
    E8 = "Skyy_PetEgg_Combat_Common"
    inv8 = T41.Inv({E8: 2})
    inv8.psave()
    o1 = _place(W, u8, inv8, E8)                                # the pet file holds slot + debt; the player file never got the move
    restart(inv8)                                                # crash: the egg is back in the inventory (2)
    Store.KEYOF.put(u8, ka)
    Store.get(ka)
    held = switch_away_and_back(u8, ka, kb)
    r8 = join(u8, ka, inv8)
    K.check(o1[0].startswith("+") and ("eggdebt." + o1[1]) in held and inv8.count(E8) == 1 and total(ka, inv8, E8) == 2,
            "F1 DUPE timeline: crash before the player save, a profile switch right after the join keeps the orphan debt; back on that profile the "
            "count reconcile takes the returned egg once (1 + 1 slot = 2, no dupe)")
    ka2, kb2 = "00000000-0000-0000-0000-000000004431-p3", "00000000-0000-0000-0000-000000004431-p2"
    u9, k9, r9 = _mk(W, 4431, key=ka2)
    inv9 = T41.Inv({E8: 1})
    o2 = _place(W, u9, inv9, E8)
    Egg.DONE.put(o2[1], Long(now()))
    _tick(W, u9, r9, inv9)
    inv9.psave()                                                 # the player file: 0 eggs (the egg is in the slot)
    o3 = _takeout(W, u9, inv9, 1, o2[1])                        # the egg back in the inventory + a credit; the player file never got it
    restart(inv9)                                                # crash: inventory 0, slot empty in the pet file
    Store.KEYOF.put(u9, ka2)
    Store.get(ka2)
    held2 = switch_away_and_back(u9, ka2, kb2)
    r9 = join(u9, ka2, inv9)
    K.check(o3[0].startswith("+") and ("eggcredit." + o3[1]) in held2 and inv9.count(E8) == 1 and total(ka2, inv9, E8) == 1,
            "F1 LOSS timeline: crash before the player save of a take-out, a switch right after the join keeps the orphan credit; back on that "
            "profile the egg is given again (1, not lost)")
    # ---------------------------------------------------------------- review F2: no blind 60 s clear where nothing saves the player
    Pes = W["JClass"](PKG + "PetEggSave")
    u10, k10, r10 = _mk(W, 4432)
    E10 = "Skyy_PetEgg_Mining_Common"
    inv10 = T41.Inv({E10: 2})
    n1 = _place(W, u10, inv10, E10)
    K.check(not bool(Pes.force(None, None, None, n1[1])) and Egg.NOFORCE.containsKey(n1[1]) and Egg.NOSAVE.containsKey(n1[1]),
            "F2 a forced save that could not see a saving world (unknown store) = NOFORCE + NOSAVE")
    _tick(W, u10, r10, inv10, 61000)
    _tick(W, u10, r10, inv10, 600000)
    n2 = _place(W, u10, inv10, E10)
    K.check(r10.get("eggdebt." + n1[1]) is not None and n2[0].startswith("=Saving"), "F2 NOSAVE: no clear at 61 s nor 10 min (nothing writes the player file there)")
    W["fileT"][str(u10)] = _debt_ms(r10, n1[1]) + 7000
    _tick(W, u10, r10, inv10, 8000)
    n3 = _place(W, u10, inv10, E10)
    K.check(r10.get("eggdebt." + n1[1]) is None and n3[0].startswith("+") and not Egg.NOSAVE.containsKey(n1[1]),
            "F2 ... once the player file IS written after the move it settles (the file rule), NOSAVE dropped: %s" % n3[0])
    # ---------------------------------------------------------------- PetEggSave: the failure counter
    K.check(int(Pes.FAILS.get()) == 0 and not bool(Pes.BROKEN), "FIX PetEggSave: no failure yet, not switched off")
    K.save()


# ======================================================================================================== STATIC: the root cause (bytecode)
def run_static(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(*cp):
        p_ = CPc(False)
        p_.appendSystemPath()
        for c in cp:
            p_.appendClassPath(c)
        return p_

    def code(p_, cn, mn):
        out_ = []
        for m_ in p_.get(cn).getDeclaredMethods():
            if str(m_.getName()) != mn:
                continue
            ca_ = m_.getMethodInfo().getCodeAttribute()
            if ca_ is None:
                continue
            it_, cpl_ = ca_.iterator(), m_.getMethodInfo().getConstPool()
            while it_.hasNext():
                out_.append(str(IP.instructionString(it_, it_.next(), cpl_)))
        return "\n".join(out_)
    pe = pool_of(B.SERVER_JAR)
    K.check("clone" not in [str(m.getName()) for m in pe.get("com.hypixel.hytale.server.core.entity.entities.Player").getDeclaredMethods()],
            "STATIC the engine's Player does not override clone() (Entity.clone is used)")
    ec = code(pe, "com.hypixel.hytale.server.core.entity.Entity", "clone")
    K.check("EntityModule.getCodec" in ec and "DirectDecodeCodec.encode" in ec, "STATIC Entity.clone() = EntityModule.getCodec(getClass()).encode(...) - the NPE of the log")
    gc = code(pe, "com.hypixel.hytale.server.core.modules.entity.EntityModule", "getCodec")
    K.check("codecMap" in gc, "STATIC EntityModule.getCodec reads codecMap (filled only by registerEntity)")
    su = code(pe, "com.hypixel.hytale.server.core.modules.entity.EntityModule", "setup").splitlines()
    ix = [i for i, l in enumerate(su) if "entities.Player.CODEC" in l]
    K.check(len(ix) == 1 and "ComponentRegistryProxy.registerComponent" in su[ix[0] + 1],
            "STATIC EntityModule.setup registers Player with registerComponent(Player.class, \"Player\", Player.CODEC) - never registerEntity, so codecMap has no Player")
    ac = code(pe, "com.hypixel.hytale.component.ArchetypeChunk", "copyEntity")
    K.check("Component.clone" in ac, "STATIC Store.copyEntity -> ArchetypeChunk.copyEntity clones every component (the Player too)")
    sh = code(pe, "com.hypixel.hytale.server.core.modules.entity.player.PlayerSavingSystems", "createShallowHolder")
    K.check("ArchetypeChunk.getComponent" in sh and "ComponentRegistry.newHolder" in sh and "clone" not in sh,
            "STATIC the engine's own player save uses a shallow holder (getComponent + newHolder, no clone)")
    po, pn = pool_of(B.SERVER_JAR, OLD_JAR), pool_of(B.SERVER_JAR, jar)
    fo, fn = code(po, PKG + "PetEggSave", "force0"), code(pn, PKG + "PetEggSave", "force0")
    K.check("Store.copyEntity" in fo and "PetEggSave.BROKEN" in fo, "STATIC 0.4.3 force0 = Store.copyEntity (always the NPE) + BROKEN on the first throw")
    sw = code(pn, PKG + "PetEggSave", "shallow")
    K.check("copyEntity" not in fn and "PetEggSave.shallow" in fn and "Store.getArchetype" in sw and "ComponentRegistry.newHolder" in sw and "clone" not in sw
            and "Store.getComponent" in sw, "STATIC 0.4.4 force0 = the shallow holder (Store.getArchetype + getComponent + EntityStore.REGISTRY.newHolder, nothing cloned)")
    K.check("PetEggSave.FAILS" in fn, "STATIC 0.4.4 force0 counts failures in a row (BROKEN only after 5)")
    sd = code(pn, PKG + "PetTick", "switched")
    K.check(sd.find("PetHatchery.switched") >= 0 and sd.find("PetHatchery.switched") < sd.find("PetStore.release"),
            "STATIC PetTick.switched settles the old profile (PetHatchery.switched) BEFORE it releases its record")
    K.save()


# ======================================================================================================== OLD043 + LIVE
def run_new043(out, jar, scratch, home):
    T43.run_new(out, jar, scratch, home)


def run_old043(out, jar, scratch, home):
    T43.run_old(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    T41.run_live(out, jar, scratch, home)


SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"


def run_live2(out, jar, scratch, home):
    """Skyy's own record on a scratch COPY: the join after the deploy (a server restart) with today's inventory"""
    from jpype import JClass, JProxy
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Egg, Hy, Eng = P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetEgg"), P_("PetHatchery"), P_("PetsEng")
    Paths, UUID, Long = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long")
    Log.LINES = JClass("java.util.ArrayList")()
    Cfg.load(Paths.get(os.path.dirname(home)))
    Store.ROOT = Paths.get(home)
    Store.DIR = Store.ROOT.resolve("pets")
    Store.scanAll()
    Egg.recover()
    Hy.recover()
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, [SKYY]), "byName": lambda n: None, "nameOf": lambda u: "Skyy",
                                            "tell": lambda u, t, c: None})
    key = SKYY + "-p3"
    Log.bridge().put("profile:fn:key", JProxy("java.util.function.Function", dict={"apply": lambda u: key}))
    u = UUID.fromString(SKYY)
    f0 = T41.props(os.path.join(home, "pets", key + ".properties"))
    debts = dict((k_, v_) for k_, v_ in f0.items() if k_.startswith("eggdebt."))
    if not debts:
        K.notes.append("LIVE2: Skyy's p3 record holds no open debt any more (already settled) - only the place is checked")
    E = "Skyy_PetEgg_Combat_Common"
    # today's inventory (the screenshot): 1 Common Combat Egg, no Common Exploration Egg; the player file was saved long after the moves
    inv = T41.Inv({E: 1})
    Egg.FILEMS = JProxy("java.util.function.Function", dict={"apply": lambda x: Long(int(JClass("java.lang.System").currentTimeMillis()))})
    Store.KEYOF.put(u, key)
    r = Store.get(key)
    t = int(JClass("java.lang.System").currentTimeMillis())
    Egg.debts(u, r, T41.proxy_inv(inv), t)
    Hy.credits(u, r, T41.proxy_inv(inv), t)
    K.check(not list(r.keysWith("eggdebt.")) and inv.count(E) == 1, "LIVE2 the join after the deploy settles Skyy's %d open debts by the counts, NOTHING taken (still 1 Combat egg): %s"
            % (len(debts), sorted(debts.values())))
    Hy.CLICK.clear()
    p = [str(x) for x in Hy.place(u, T41.proxy_inv(inv), E, "harness")]
    K.check(p[0].startswith("+") and inv.count(E) == 0, "LIVE2 ... and the second Common Combat Egg goes into the Hatchery: %s" % p[0])
    K.save()


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") in ("old_hatch", "old_pages"):
        T43_main = os.path.join(HERE, "test_skyypets_0.4.3.py")
        raise SystemExit(subprocess.call([sys.executable, T43_main] + sys.argv[1:]))
    phases = [("static", run_static), ("repro", run_repro), ("fix", run_fix), ("new043", run_new043), ("old043", run_old043),
              ("live", run_live), ("live2", run_live2)]
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
