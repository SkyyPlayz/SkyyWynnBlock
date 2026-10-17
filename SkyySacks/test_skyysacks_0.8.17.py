"""Harness for SkyySacks 0.8.17 (round sacks0817: the Void's weighed fish for SkyyFishing 0.1.10's Fishing Bench - sacks:fn:fishList /
fishTake / fishPut + the plain take keeps entries in sync; tools/sacks_0_8_17_patch.py). Build first:
    python tools/sacks_0_8_17_patch.py && python SkyySacks/build_skyysacks_0.8.17.py
    (and SkyyFishing 0.1.10: python tools/fishing_0_1_10_patch.py && python SkyyFishing/build_skyyfishing_0.1.10.py)

    python SkyySacks/test_skyysacks_0.8.17.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.16 -> 0.8.17: exactly the planned members; non-class entries: manifest.json only
  KEYS EXECUTED on the REAL SackBridge / SackPool / SackFn (a scratch pool folder, a stand-in player through SackBridge.PLAYERS):
       LIST   entries oldest first + "" per plain fish; not a fish / bad args; PAUSED (profile:busy, no player on this thread, a profile
              switch's settle window) = null
       TAKE   exactly once (a second take of the same entry = 0), the pool FILE already holds the change when it answers 1, bad entry
              (";") refused, a plain fish by "", two fish with the same entry = two takes then 0
       PUT    only an owed entry (never one that was not taken, never twice, not after commit, not after 60 s), written before 1
       COMMIT finalises (the entry leaves the ledger); WRITE FAIL: take -> 0 + memory unchanged; put -> 0 + still owed (commit works)
       PROFILE a profile switch between take and put: the put goes back into the pool the take left (LASTKEY), the new one untouched
       SYNC   (the 0.8.10 gap) plain sacks:fn:take of fish takes the oldest entries with the count; put gives exactly those back (the list
              as before); commit drops them; entries never above the count; other items' take / put / commit unchanged
       TOKENS (fishvoid critic round) the op token stored in the same pool write as the take, an idempotent retake refused, fishTaken
              TRUE / FALSE / null (paused, no player, bad token, op time at / before the 24 h prune cut), put clears it (also a 3-arg put
              and a plain sacks:fn:put of a tokened take), write fail of take / put, a crash between the write and the answer
              (memory cleared -> TRUE from the file, retake 0), the 24 h prune + cut; fishList null (not a fish) vs [] (readable, none)
  REAL THE REAL SkyyFishing 0.1.10 Fishing Bench (its FishPage + FishBench, SkyyFishing harness setup) on the REAL SkyySacks keys: the Void
       rows, sell once, fillet once, a refused payment = fishPut back, Sell all, a stale row, CRASH at every step (before / inside the
       Sacks take = after its write before its answer / after the take / before pay / before + after the coin flush) and of a fillet:
       restart (Sacks + Fishing memory lost, pool + op files as on disk) + FishBench.recover = the fish in the Void and nothing paid, or
       gone and paid exactly once (the named residual window after the coin flush = SkyyFishing's documented one)
  TG   the 0.8.16 harness's TG phase on this jar (seeds / saplings switches, popup, feed) - unchanged behaviour
  FISH10 the 0.8.10 harness's FISH phase on this jar (with SkyyFishing 0.1.8): deposit / sweep / take-out of weighed fish unchanged
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the real world-thread call from the bench page in game, the plugin setup's puts (checked as
text in the build script + the jar's SkyySacksPlugin class), timing of the synchronous pool write on the world thread. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_16", os.path.join(HERE, "test_skyysacks_0.8.16.py"))
T16 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T16)
HK.run_compare = _orig_compare
T0810 = T16.T0810

VERSION = "0.8.17"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.16.jar")
FISH_JAR = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks0817", "h")))
PKG = "com.skyy.sacks."
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
    "SackPool": ["+f TOK_MS", "+m tokOk", "+m tokRaw", "+m tokHas", "+m tokCut", "+m tokSet", "+m fishPickTok", "+m fishAtTok", "+m fishAt", "+m fishFront", "+m fishView", "+m fishPick", "+m fishDebit", "+m saveOk0", "+m saveOk"],
    "SackBridge": ["+f FTOK", "+m ftokClear", "+m ftokPush", "+m ftokFind", "+m ftokDrop", "+m ftokPopOld", "+m ftokTidy", "+m fishTaken", "+f FOWE", "+m oweE", "+m unoweE", "+m fishUnowe", "+m fishList", "+m fishTake", "+m fishPut", "+m fishCall",
                   "~<clinit>", "~m take", "~m put", "~m commit"],
    "SackFn": ["~m apply"],
    "SkyySacksPlugin": ["~m setup"],
}
ADDED = []
U1S = "00000000-0000-4000-8000-0000000110f9"
KEYS = (("sacks:fn:take", 1), ("sacks:fn:put", 2), ("sacks:fn:all", 3), ("sacks:fn:commit", 4),
        ("sacks:fn:fishList", 14), ("sacks:fn:fishTake", 15), ("sacks:fn:fishPut", 16), ("sacks:fn:fishTaken", 17))


def fishing_module(scratch):
    """the SkyyFishing 0.1.10 harness as a library (its setup / page helpers); its import adds --dir / --jar to sys.argv - kept apart"""
    keep = list(sys.argv)
    sys.argv = [sys.argv[0], "--jar", FISH_JAR, "--dir", os.path.join(scratch, "fishlib")]
    try:
        sp = importlib.util.spec_from_file_location("test_skyyfishing_0_1_10", os.path.join(ROOT, "SkyyFishing", "test_skyyfishing_0.1.10.py"))
        TF = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(TF)
    finally:
        sys.argv = keep
    return TF


def sacks_env(K, scratch, tag):
    """both jars in one JVM (the SkyyFishing harness setup + SKYY_HARNESS_CP = this SkyySacks jar), the Sacks side on a scratch folder"""
    import jpype
    from jpype import JClass, JImplements, JOverride
    TF = fishing_module(scratch)
    os.environ["SKYY_HARNESS_CP"] = JAR
    P, mods = TF.setup(K, FISH_JAR, scratch, tag)
    J = lambda n: JClass(PKG + n)
    Pool, Br, Fn, CLog, Mir = J("SackPool"), J("SackBridge"), J("SackFn"), J("CraftLog"), J("BagMirror")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "sacks-" + tag)
    os.makedirs(base, exist_ok=True)
    Pool.DIR = Paths.get(os.path.join(base, "pools"))
    CLog.FILE = Paths.get(os.path.join(base, "crafts.log"))
    Pool.WRITER = JClass("java.util.concurrent.Executors").newSingleThreadScheduledExecutor()
    br = P("FishBridge").bridge()
    K.check(JClass("java.lang.System").identityHashCode(Pool.bridge()) == JClass("java.lang.System").identityHashCode(br),
            "ENV: SkyySacks and SkyyFishing share the one skyy.bridge map")
    for name, mode in KEYS:
        br.put(name, Fn(mode))
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    pl = uf.get(None).allocateInstance(PLA.class_)
    W = {"player": pl}

    @JImplements("java.util.function.Function")
    class Players(object):
        @JOverride
        def apply(self, o):
            return W["player"]
    Br.PLAYERS = Players()
    return TF, P, mods, J, Pool, Br, Fn, br, W, base


def clear_sacks(J):
    Pool, Br, Mir = J("SackPool"), J("SackBridge"), J("BagMirror")
    for m in (Pool.POOLS, Pool.DIRTY, Pool.PMETA, Pool.PENDING, Pool.LASTSAVE, Pool.SWEPTQ, Pool.BADPOOL, Pool.SEENEPOCH, Pool.SEENKEY,
              Pool.CHANGEDAT, Pool.UNKNOWN, Mir.MIRRORS, Br.OWED, Br.FOWE, Br.FTOK, Br.LASTKEY):
        m.clear()


def disk(base, key):
    """the pool FILE as it is on disk now: {item: count}, {fish id: [entries]}"""
    f = os.path.join(base, "pools", key + ".properties")
    if not os.path.isfile(f):
        return {}, {}
    from jpype import JClass
    p = JClass("java.util.Properties")()
    ins = JClass("java.io.FileInputStream")(f)
    try:
        p.load(ins)
    finally:
        ins.close()
    cnt, ent = {}, {}
    for k_ in p.stringPropertyNames():
        k_ = str(k_)
        v = str(p.getProperty(k_))
        if k_.startswith("~fish:"):
            ent[k_[6:]] = [x for x in v.split(";") if x]
        elif not k_.startswith("~"):
            cnt[k_] = int(v)
    return cnt, ent


# ------------------------------------------------------------------------------------------------ KEYS: the contract on the real classes
def run_keys(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JString, JObject
    K = HK.Child(out)
    TF, P, mods, J, Pool, Br, Fn, br, W, base = sacks_env(K, scratch, "keys")
    UUID, Long, Bool, ObjA = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Boolean"), JArray(JClass("java.lang.Object"))
    u = UUID.fromString(U1S)
    k = str(u)
    FISH = [str(x) for x in P("FishDefs").FISH]
    f0, f1 = FISH[0], FISH[1]
    ROCK = "Rock_Stone_Cobble"

    def call(name, *a):
        return br.get(name).apply(ObjA(list(a)))

    def lst(id_):
        r = call("sacks:fn:fishList", u, id_)
        return None if r is None else [str(x) for x in r]

    def take(id_, e, tok=None):
        return int(call("sacks:fn:fishTake", u, id_, e, *([tok] if tok is not None else [])))

    def put(id_, e, tok=None):
        return int(call("sacks:fn:fishPut", u, id_, e, *([tok] if tok is not None else [])))

    def taken(tok, since=None):
        r = call("sacks:fn:fishTaken", u, tok, *([Long(since)] if since is not None else []))
        return None if r is None else bool(r.booleanValue())

    def commit(id_, n):
        return int(call("sacks:fn:commit", u, id_, Long(n)))

    def mem(id_):
        return int(Pool.get(k, id_)), [str(x) for x in Pool.fishList(k, id_)]

    def owed():
        o = {}
        for e_ in Br.OWED.entrySet():
            o[str(e_.getKey())] = int(e_.getValue()[0])
        return o

    def fowe():
        return dict((str(e_.getKey()), [str(x) for x in e_.getValue()]) for e_ in Br.FOWE.entrySet())

    def reset(entries, plain=0, id_=f0):
        clear_sacks(J)
        shutil.rmtree(os.path.join(base, "pools"), ignore_errors=True)
        for e_ in entries:
            Pool.fishIn(k, id_, JString(e_), Long(1).longValue())
        if plain:
            Pool.fishIn(k, id_, JString(""), Long(plain).longValue())
        Pool.save(k)
    E1, E2, E3 = "1200,300,Skyy", "2500,410,Skyy", "3300,520,Bob"
    # ================= LIST
    reset([E1, E2], plain=1)
    K.eq(lst(f0), [E1, E2, ""], "LIST: entries oldest first, then '' per plain fish")
    K.eq(lst(f1), [], "LIST: a fish id with none stored = []")
    K.check(lst(ROCK) is None, "LIST: not a SkyyFishing whole fish = null (not a readable fish list)")
    K.check(br.get("sacks:fn:fishList").apply(JString("x")) is None and br.get("sacks:fn:fishList").apply(ObjA([u])) is None,
            "LIST: bad arguments = null (never throws)")
    br.put("profile:busy:" + k, Bool.TRUE)
    K.check(lst(f0) is None, "LIST PAUSED: profile:busy = null")
    K.eq(take(f0, E1), 0, "TAKE PAUSED: profile:busy = 0")
    br.remove("profile:busy:" + k)
    W["player"], keep_p = None, W["player"]
    K.check(lst(f0) is None and take(f0, E1) == 0, "PAUSED: no player on this world thread = null / 0")
    W["player"] = keep_p
    K.eq(mem(f0), (3, [E1, E2]), "PAUSED: nothing moved")
    # ================= TAKE exactly once, written before the answer
    r = take(f0, E2)
    dc, de = disk(base, k)
    K.eq(r, 1, "TAKE: answers 1")
    K.check(dc.get(f0) == 2 and de.get(f0) == [E1], "TAKE: the pool FILE already holds count 2 + entries [E1] when it answers (%s %s)" % (dc, de))
    K.eq(mem(f0), (2, [E1]), "TAKE: memory count 2, entries [E1]")
    K.eq(take(f0, E2), 0, "TAKE TWICE (double click / second bench): the same entry again = 0")
    K.eq(take(f0, "9,9,X"), 0, "TAKE: an entry the Void does not hold = 0")
    K.eq(take(f0, E1 + ";" + E1), 0, "TAKE: an entry with the separator ';' = 0")
    K.eq(take(ROCK, ""), 0, "TAKE: not a fish = 0")
    K.eq(owed(), {k + "|" + f0: 1}, "TAKE: one fish owed on the refund ledger")
    K.eq(fowe(), {k + "|" + f0: [E2]}, "TAKE: the ledger holds its entry")
    # ================= PUT
    K.eq(put(f0, E3), 0, "PUT: an entry that was never taken = 0 (a put never creates a fish or changes a weight)")
    K.eq(put(f1, E2), 0, "PUT: another fish id = 0")
    r = put(f0, E2)
    dc, de = disk(base, k)
    K.check(r == 1 and dc.get(f0) == 3 and sorted(de.get(f0, [])) == sorted([E1, E2]), "PUT: 1, the FILE has the fish back (%s %s)" % (dc, de))
    K.eq(mem(f0), (3, [E2, E1]), "PUT: back at the oldest end (count 3)")
    K.eq(put(f0, E2), 0, "PUT TWICE: 0 (no longer owed)")
    K.check(owed() == {} and fowe() == {}, "PUT: the ledger is empty")
    # ================= COMMIT
    K.eq(take(f0, E1), 1, "COMMIT: take E1")
    K.eq(commit(f0, 1), 1, "COMMIT: 1 cleared")
    K.eq(put(f0, E1), 0, "COMMIT: a committed fish can not be put back")
    K.eq(mem(f0), (2, [E2]), "COMMIT: count 2, entries [E2] (the plain fish + E2)")
    K.check(owed() == {} and fowe() == {}, "COMMIT: the ledger is empty")
    # plain fish by ""
    K.eq(take(f0, ""), 1, "PLAIN: '' takes the plain fish")
    K.eq(take(f0, ""), 0, "PLAIN: no plain fish left = 0 (the weighed one is not taken by '')")
    K.eq(put(f0, ""), 1, "PLAIN: put back")
    K.eq(mem(f0), (2, [E2]), "PLAIN: count 2, entries [E2]")
    # two fish with the same entry
    reset([E1, E1])
    K.check([take(f0, E1), take(f0, E1), take(f0, E1)] == [1, 1, 0] and mem(f0) == (0, []), "SAME ENTRY: two fish = two takes, then 0")
    K.check([put(f0, E1), put(f0, E1), put(f0, E1)] == [1, 1, 0] and mem(f0) == (2, [E1, E1]), "SAME ENTRY: two puts, then 0")
    # ================= EXPIRY (60 s)
    reset([E1, E2])
    take(f0, E2)
    o = Br.OWED.get(k + "|" + f0)
    o[1] = o[1] - 61000
    K.eq(put(f0, E2), 0, "EXPIRY: 61 s after the take a put is refused")
    K.check(owed() == {} and fowe() == {}, "EXPIRY: the stale ledger is dropped")
    K.eq(mem(f0), (1, [E1]), "EXPIRY: the fish stays out (the caller owns it)")
    # ================= WRITE FAIL
    reset([E1, E2])
    good = Pool.DIR
    blocker = os.path.join(base, "blocker")
    open(blocker, "w").write("x")
    Pool.DIR = JClass("java.nio.file.Paths").get(os.path.join(blocker, "pools"))
    r = take(f0, E2)
    K.check(r == 0 and mem(f0) == (2, [E1, E2]) and owed() == {} and fowe() == {},
            "WRITE FAIL TAKE: 0 and memory unchanged (fish + entry in place, nothing owed) %s %s %s" % (r, mem(f0), owed()))
    Pool.DIR = good
    K.eq(take(f0, E2), 1, "WRITE FAIL: take again with a writable folder")
    Pool.DIR = JClass("java.nio.file.Paths").get(os.path.join(blocker, "pools"))
    r = put(f0, E2)
    K.check(r == 0 and mem(f0) == (1, [E1]) and owed() == {k + "|" + f0: 1} and fowe() == {k + "|" + f0: [E2]},
            "WRITE FAIL PUT: 0, the fish stays out and stays owed (the caller gives it another way) %s %s" % (mem(f0), owed()))
    Pool.DIR = good
    K.eq(commit(f0, 1), 1, "WRITE FAIL PUT: the caller's commit after giving it another way clears it")
    Pool.save(k)
    dc, de = disk(base, k)
    K.check(dc.get(f0) == 1 and de.get(f0) == [E1], "WRITE FAIL: the file = memory after the next save (%s %s)" % (dc, de))
    # ================= PROFILE switch between take and put
    reset([E1, E2])
    PK = {"k": k}

    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, o):
            return PK["k"]
    br.put("profile:fn:key", PKey())
    br.put("profile:epoch:" + k, Long(1))
    Pool.CHANGEDAT.clear()
    K.eq(lst(f0), [E1, E2], "PROFILE: profile 1 lists its fish")
    K.eq(take(f0, E2), 1, "PROFILE: take E2 from profile 1")
    k2 = k + ".2"
    PK["k"] = k2
    br.put("profile:epoch:" + k, Long(2))
    K.check(lst(f0) is None and take(f0, E1) == 0, "PROFILE: the switch's settle window = paused (null / 0)")
    K.eq(put(f0, E2), 1, "PROFILE: the put still answers 1 ...")
    K.check(mem(f0) == (2, [E2, E1]) and int(Pool.get(k2, f0)) == 0, "PROFILE: ... into profile 1's pool (LASTKEY), profile 2 untouched")
    Pool.CHANGEDAT.clear()
    K.eq(lst(f0), [], "PROFILE: after the window profile 2 lists its own (empty) Void")
    br.remove("profile:fn:key")
    br.remove("profile:epoch:" + k)
    Pool.SEENKEY.clear(); Pool.SEENEPOCH.clear(); Pool.CHANGEDAT.clear()
    # ================= SYNC: the plain take (0.8.10 gap)
    A_, B_, C_ = "1000,200,A", "2000,300,B", "3000,400,C"
    reset([A_, B_, C_], plain=1)
    K.eq(lst(f0), [A_, B_, C_, ""], "SYNC: 3 weighed + 1 plain")
    t = int(call("sacks:fn:take", u, f0, Long(2)))
    K.check(t == 2 and mem(f0) == (2, [C_]), "SYNC TAKE 2: count 2, the two OLDEST entries went with them (%s)" % (mem(f0),))
    K.eq(fowe(), {k + "|" + f0: [A_, B_]}, "SYNC: the ledger holds them")
    K.eq(int(call("sacks:fn:put", u, f0, Long(1))), 1, "SYNC PUT 1")
    K.eq(mem(f0), (3, [B_, C_]), "SYNC PUT 1: the newest-taken entry (B) is back at the oldest end")
    K.eq(int(call("sacks:fn:put", u, f0, Long(5))), 1, "SYNC PUT: only what is owed (1 of 5)")
    K.eq(mem(f0), (4, [A_, B_, C_]), "SYNC: after both puts the Void is exactly as before the take")
    t = int(call("sacks:fn:take", u, f0, Long(9)))
    K.check(t == 4 and mem(f0) == (0, []) and fowe() == {k + "|" + f0: [A_, B_, C_, ""]}, "SYNC TAKE ALL: 4 out, entries + one plain on the ledger")
    K.eq(commit(f0, 4), 4, "SYNC COMMIT 4")
    K.check(fowe() == {} and owed() == {} and int(call("sacks:fn:put", u, f0, Long(1))) == 0, "SYNC: after commit nothing can come back")
    reset([A_, B_, C_])
    call("sacks:fn:take", u, f0, Long(2))
    commit(f0, 1)
    K.eq(fowe(), {k + "|" + f0: [B_]}, "SYNC COMMIT 1: the oldest owed (A) is finalised")
    call("sacks:fn:put", u, f0, Long(1))
    K.eq(mem(f0), (2, [B_, C_]), "SYNC: put returns B (still owed)")
    # invariant over a random walk
    import random
    rnd = random.Random(817)
    reset(["%d,%d,R" % (1000 + i, 100 + i) for i in range(6)], plain=2)
    bad = []
    for step in range(300):
        op = rnd.choice(["take", "put", "commit", "ftake", "fput"])
        if op == "take":
            call("sacks:fn:take", u, f0, Long(rnd.randint(1, 3)))
        elif op == "put":
            call("sacks:fn:put", u, f0, Long(rnd.randint(1, 3)))
        elif op == "commit":
            commit(f0, rnd.randint(1, 2))
        elif op == "ftake":
            l_ = lst(f0)
            if l_:
                take(f0, rnd.choice(l_))
        else:
            l_ = fowe().get(k + "|" + f0, [])
            if l_:
                put(f0, rnd.choice(l_))
        c_, es = mem(f0)
        ow = owed().get(k + "|" + f0, 0)
        fl = fowe().get(k + "|" + f0, [])
        if len(es) > c_ or ow != len(fl):
            bad.append((step, op, c_, len(es), ow, len(fl)))
    K.check(not bad, "SYNC WALK: 300 random take / put / commit / fishTake / fishPut - entries never above the count, ledger count = ledger entries %s" % bad[:3])
    # conservation: every fish is in the Void, on the ledger, or committed
    # ================= TOKENS (fishvoid critic round)
    def disk_tok():
        f = os.path.join(base, "pools", k + ".properties")
        p_ = JClass("java.util.Properties")()
        ins = JClass("java.io.FileInputStream")(f)
        try:
            p_.load(ins)
        finally:
            ins.close()
        v = p_.getProperty("~fishtok")
        c = p_.getProperty("~fishcut")
        return ([] if v is None else [str(x).rsplit("@", 1)[0] for x in str(v).split(" ") if x]), (None if c is None else str(c))
    reset([E1, E2, E3])
    K.check(taken("bench.op-1") is False, "TOKEN: an unknown token with no prune ever = FALSE (definitely not taken)")
    K.eq(take(f0, E2, "bench.op-1"), 1, "TOKEN TAKE: 1")
    K.check(disk_tok()[0] == ["bench.op-1"] and disk(base, k)[1].get(f0) == [E1, E3], "TOKEN TAKE: the token is in the SAME pool file write as the take %s" % (disk_tok(),))
    K.check(taken("bench.op-1") is True, "TOKEN: fishTaken TRUE after the take")
    K.eq(take(f0, E1, "bench.op-1"), 0, "TOKEN IDEMPOTENT: a take with a stored token = 0 (even for another entry)")
    K.eq(mem(f0), (2, [E1, E3]), "TOKEN IDEMPOTENT: nothing more moved")
    K.eq(take(f0, E1, "bad token"), 0, "TOKEN: a token with white space = 0")
    K.eq(take(f0, E1, "a@b"), 0, "TOKEN: a token with '@' = 0")
    K.check(taken("bad token") is None and taken("") is None, "TOKEN: fishTaken of a bad token = null")
    br.put("profile:busy:" + k, Bool.TRUE)
    K.check(taken("bench.op-1") is None, "TOKEN PAUSED: profile:busy = null")
    br.remove("profile:busy:" + k)
    W["player"] = None
    K.check(taken("bench.op-1") is None, "TOKEN: no player on this thread = null")
    W["player"] = keep_p
    K.eq(put(f0, E2, "other.op"), 0, "TOKEN PUT: a token this entry's take did not carry = 0")
    r = put(f0, E2, "bench.op-1")
    K.check(r == 1 and disk_tok()[0] == [] and taken("bench.op-1") is False and mem(f0) == (3, [E2, E1, E3]),
            "TOKEN PUT: fish back + token cleared in the same write -> fishTaken FALSE %s" % (disk_tok(),))
    K.eq(take(f0, E2, "bench.op-1"), 1, "TOKEN: after its put the same op id may take again (the token was cleared)")
    K.eq(commit(f0, 1), 1, "TOKEN COMMIT")
    K.check(taken("bench.op-1") is True and disk_tok()[0] == ["bench.op-1"], "TOKEN COMMIT: the take stands - the token stays on disk")
    K.eq(put(f0, E2, "bench.op-1"), 0, "TOKEN COMMIT: no put after commit")
    K.eq(take(f0, E1, "bench.op-2"), 1, "TOKEN: take E1 with op-2")
    K.check(put(f0, E1) == 1 and taken("bench.op-2") is False, "TOKEN: a 3-argument put clears that take's token too")
    K.eq(take(f0, E1, "bench.op-3"), 1, "TOKEN: take E1 with op-3")
    K.eq(int(call("sacks:fn:put", u, f0, Long(1))), 1, "TOKEN: plain put returns it")
    Pool.save(k)
    K.check(taken("bench.op-3") is False and "bench.op-3" not in disk_tok()[0] and E1 in mem(f0)[1], "TOKEN: plain put cleared the token (memory + file)")
    blocker2 = os.path.join(base, "blocker2")
    open(blocker2, "w").write("x")
    goodd = Pool.DIR
    Pool.DIR = JClass("java.nio.file.Paths").get(os.path.join(blocker2, "pools"))
    K.check(take(f0, E3, "bench.op-4") == 0 and taken("bench.op-4") is False and E3 in mem(f0)[1], "TOKEN WRITE FAIL TAKE: 0, no token, fish in place")
    Pool.DIR = goodd
    K.eq(take(f0, E3, "bench.op-4"), 1, "TOKEN: the same op id takes once the folder is writable")
    Pool.DIR = JClass("java.nio.file.Paths").get(os.path.join(blocker2, "pools"))
    K.check(put(f0, E3, "bench.op-4") == 0 and taken("bench.op-4") is True and E3 not in mem(f0)[1], "TOKEN WRITE FAIL PUT: 0, token kept, fish still out")
    Pool.DIR = goodd
    K.eq(commit(f0, 1), 1, "TOKEN WRITE FAIL PUT: the caller's commit")
    reset([E1, E2])
    K.eq(take(f0, E2, "bench.op-5"), 1, "CRASH: take with op-5 (written)")
    clear_sacks(J)
    K.check(taken("bench.op-5") is True, "CRASH AFTER WRITE (before the answer): fishTaken TRUE from the file")
    K.eq(take(f0, E2, "bench.op-5"), 0, "CRASH AFTER WRITE: the replayed take is refused (idempotent)")
    K.eq(mem(f0), (1, [E1]), "CRASH AFTER WRITE: exactly one fish left")
    K.check(taken("bench.op-6") is False, "CRASH BEFORE WRITE: a take that never ran = FALSE")
    import time as _t
    now_ms = int(_t.time() * 1000)
    old_t = now_ms - 25 * 3600 * 1000
    mt = Pool.PMETA.get(k)
    mt.put("~fishtok", "old.op@%d bench.op-5@%d" % (old_t, now_ms - 1000))
    K.eq(take(f0, E1, "bench.op-7"), 1, "PRUNE: a new take prunes tokens older than 24 h")
    d_t, d_c = disk_tok()
    K.check(d_t == ["bench.op-5", "bench.op-7"] and d_c == "t%d" % old_t, "PRUNE: old.op gone, the cut = its take time (%s %s)" % (d_t, d_c))
    K.check(taken("old.op") is None, "PRUNE: an unknown token after a prune, no op time = null (can't tell)")
    K.check(taken("old.op", old_t - 5) is None and taken("old.op", old_t) is None, "PRUNE: op time at / before the cut = null")
    K.check(taken("new.op", old_t + 5) is False, "PRUNE: op time after the cut and no token = FALSE")
    K.check(taken("bench.op-7", old_t - 5) is True, "PRUNE: a stored token = TRUE whatever the op time")
    K.check(call("sacks:fn:fishTaken", u, "x.op", "notanumber") is None, "TOKEN: a non-number op time = null")
    # ================= other items unchanged
    clear_sacks(J)
    Pool.add(k, ROCK, Long(10).longValue())
    K.check([int(call("sacks:fn:take", u, ROCK, Long(3))), int(call("sacks:fn:put", u, ROCK, Long(5))), int(call("sacks:fn:take", u, ROCK, Long(4))),
             commit(ROCK, 4), int(call("sacks:fn:put", u, ROCK, Long(1)))] == [3, 3, 4, 4, 0] and int(Pool.get(k, ROCK)) == 6 and fowe() == {},
            "OTHER ITEMS: take / put / commit as before (no entry ledger)")
    bs = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check(all(('sbr0.put("%s", new {PKG}.SackFn(%d));' % (n_, m_)) in bs for n_, m_ in KEYS),
            "SETUP: the plugin publishes every key used here with these modes")
    with zipfile.ZipFile(jar) as z:
        pc = z.read("com/skyy/sacks/SkyySacksPlugin.class")
    K.check(all(n_.encode() in pc for n_, m_ in KEYS), "SETUP: the jar's SkyySacksPlugin holds the three new key names")
    try:
        Pool.WRITER.shutdownNow()
    except Exception:
        pass
    P("FishStore").stopIO()
    K.save()


# ------------------------------------------------------------------------------------------------ REAL: the real bench on the real keys
def run_real(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    TF, P, mods, J, Pool, Br, Fn, br, W0, base = sacks_env(K, scratch, "real")
    T19, H = TF.T19, TF.H
    Defs, Cfg, Rig, Bench, Brg, Eng, Store = (P("FishDefs"), P("FishCfg"), P("FishRig"), P("FishBench"), P("FishBridge"), P("FishEng"), P("FishStore"))
    IS, SIC, SH, UUID, Long = (JClass("com.hypixel.hytale.server.core.inventory.ItemStack"),
                               JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("java.lang.Short"),
                               JClass("java.util.UUID"), JClass("java.lang.Long"))
    u = UUID.fromString(U1S)
    key = str(u)
    bench_dir = os.path.join(mods, "Skyy_SkyyFishing", "bench")
    pools = os.path.join(base, "pools")
    S = {"coins": [], "persisted": [], "failpay": False, "hook": None, "snaps": {}, "takes": 0}

    def snap(point):
        if S["hook"] != point:
            return
        ops_ = {}
        if os.path.isdir(bench_dir):
            for n_ in sorted(os.listdir(bench_dir)):
                ops_[n_] = open(os.path.join(bench_dir, n_), "rb").read()
        pf = {}
        if os.path.isdir(pools):
            for n_ in os.listdir(pools):
                if n_.endswith(".properties"):
                    pf[n_] = open(os.path.join(pools, n_), "rb").read()
        S["snaps"][point] = {"pools": pf, "persisted": list(S["persisted"]), "ops": ops_, "inv": TF.snap_inv(W["inv"])}
    real_take = br.get("sacks:fn:fishTake")

    @JImplements("java.util.function.Function")
    class TakeSpy(object):          # the REAL fishTake; the disk is copied before it runs and after it wrote (before its answer arrives)
        @JOverride
        def apply(self, o):
            snap("take-before")
            r = real_take.apply(o)
            if int(r) == 1:
                S["takes"] += 1
            snap("take-inside")
            return r

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            snap("add-before")
            if S["failpay"]:
                return None
            S["coins"].append(int(o[1]))
            return Long(sum(S["coins"]))

    @JImplements("java.util.function.Function")
    class Flush(object):
        @JOverride
        def apply(self, o):
            snap("flush-before")
            S["persisted"] = list(S["coins"])
            snap("flush-after")
            return JClass("java.lang.Integer")(1)
    br.put("sacks:fn:fishTake", TakeSpy())
    br.put("coins:fn:add", Coins())
    br.put("coins:fn:flush", Flush())
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = T19._api(W)
    inv = W["inv"]
    rar = [int(x) for x in Defs.SP_RAR]
    FISH = [str(x) for x in Defs.FISH]
    common = [i for i in range(len(rar)) if rar[i] == 0]
    rare = [i for i in range(len(rar)) if rar[i] >= int(Cfg.FIL_CONFIRM_R)]
    FIL = [str(x) for x in Defs.FILLET]
    ent = lambda g, mm: "%d,%d,Skyy" % (g, mm)
    c0, c1, r0 = FISH[common[0]], FISH[common[1 % len(common)]], FISH[rare[0]]

    def void(id_):
        return [str(x) for x in Pool.fishList(key, id_)]

    def fill(d, plain=None):
        clear_sacks(J)
        shutil.rmtree(pools, ignore_errors=True)
        for id_, l in d.items():
            for e in l:
                Pool.fishIn(key, id_, JString(e), 1)
        for id_, n in (plain or {}).items():
            Pool.fishIn(key, id_, JString(""), n)
        Pool.save(key)
    fill({c0: [ent(2000, 450), ent(3100, 520)], c1: [ent(2600, 500)], r0: [ent(8000, 1100)]}, plain={c0: 1})
    K.check(bool(Brg.voidOn()), "REAL: the three real keys present = SkyyFishing's voidOn")
    pg = T19.fake_page_class()(T19.player_ref(u))

    def click(a, i=None, tok=True):
        d = {"a": a}
        if i is not None:
            d["i"] = str(i)
        if tok:
            d["t"] = str(pg.tok)
        pg.handleDataEvent(None, None, json.dumps(d))
        return str(pg.info)

    def ops():
        return sorted(os.listdir(bench_dir)) if os.path.isdir(bench_dir) else []

    def fil_count():
        return sum(int(st[2]) for st in TF.snap_inv(inv) if st[1] in FIL)
    pg.rebuild()
    click("tab", 2, tok=False)
    vi = [str(x) for x in pg.vIds]
    ve = [str(x) for x in pg.vEnts]
    K.eq(sorted(zip(vi, ve)), sorted([(c0, ent(2000, 450)), (c0, ent(3100, 520)), (c1, ent(2600, 500)), (r0, ent(8000, 1100))]),
         "REAL LIST: the bench lists every weighed Void fish through the real sacks:fn:fishList (the plain one is not a row)")
    # ---- sell one
    j = vi.index(c0)
    e0 = ve[j]
    r = click("sell", j)
    K.check(r.startswith("+Sold the") and "from the Void" in r, "REAL SELL: %s" % r)
    K.eq(len(S["coins"]), 1, "REAL SELL: exactly one payment")
    K.check(e0 not in void(c0) and len(void(c0)) == 1 and int(Pool.get(key, c0)) == 2, "REAL SELL: that entry + one fish left the real pool (%s, %d)" % (void(c0), int(Pool.get(key, c0))))
    dc, de = disk(base, key)
    K.check(dc.get(c0) == 2 and e0 not in de.get(c0, []), "REAL SELL: the pool FILE agrees")
    K.check(Br.OWED.isEmpty() and Br.FOWE.isEmpty(), "REAL SELL: committed (the refund ledger is empty)")
    K.eq(ops(), [], "REAL SELL: no op file left")
    # ---- stale row (another bench took it meanwhile)
    pg.rebuild()
    vi = [str(x) for x in pg.vIds]; ve = [str(x) for x in pg.vEnts]
    jj = vi.index(c1)
    K.eq(int(real_take.apply(JArray(JClass("java.lang.Object"))([u, c1, ve[jj]]))), 1, "STALE: a second bench takes that fish first")
    br.get("sacks:fn:commit").apply(JArray(JClass("java.lang.Object"))([u, c1, Long(1)]))
    nc = len(S["coins"])
    r = click("sell", jj)
    K.check(r.startswith("-That fish left the Void") and len(S["coins"]) == nc, "STALE: the bench sells nothing: %s" % r)
    K.eq(ops(), [], "STALE: no op file left")
    # ---- fillet one
    fill({c1: [ent(2600, 500)]})
    pg.rebuild()
    vi = [str(x) for x in pg.vIds]
    nf = int(Bench.filletsG(2600))
    f0_ = fil_count()
    r = click("fil", vi.index(c1))
    K.check(r.startswith("+Filleted") and fil_count() - f0_ == nf and void(c1) == [] and int(Pool.get(key, c1)) == 0,
            "REAL FILLET: %d Raw Fish, the fish left the real Void: %s" % (nf, r))
    K.check(Br.OWED.isEmpty() and ops() == [], "REAL FILLET: committed, no op file")
    # ---- refused payment = the real fishPut
    fill({c0: [ent(2000, 450)]})
    pg.rebuild()
    S["failpay"] = True
    r = click("sell", 0)
    S["failpay"] = False
    K.check(r.startswith("-The sale did not go through") and "in the Void" in r, "REAL PAYFAIL: %s" % r)
    dc, de = disk(base, key)
    K.check(void(c0) == [ent(2000, 450)] and int(Pool.get(key, c0)) == 1 and dc.get(c0) == 1 and de.get(c0) == [ent(2000, 450)],
            "REAL PAYFAIL: the same fish is back in the real Void (memory + file)")
    K.check(Br.OWED.isEmpty() and Br.FOWE.isEmpty() and ops() == [], "REAL PAYFAIL: nothing owed, no op file")
    # ---- double click on the same row: the second click sees the new list
    fill({c0: [ent(2000, 450), ent(2100, 460)]})
    pg.rebuild()
    nc = len(S["coins"])
    r1 = click("sell", 0)
    r2 = click("sell", 0)
    K.check(r1.startswith("+Sold") and len(void(c0)) + (len(S["coins"]) - nc) == 2 and int(Pool.get(key, c0)) == len(void(c0)),
            "DOUBLE CLICK: every fish sold once, count = entries (%s / %s, %d paid)" % (r1, r2, len(S["coins"]) - nc))
    # ---- Sell all (two clicks): the Normal fish of the Void, the Rare stays
    fill({c0: [ent(2000, 450)], c1: [ent(2600, 500)], r0: [ent(8000, 1100)]})
    pg.rebuild()
    nc = len(S["coins"])
    click("sellall")
    r = click("sellall")
    K.check(r.startswith("+Sold 2 Normal fish (2 from the Void)") and len(S["coins"]) - nc == 2, "REAL SELLALL: %s" % r)
    K.check(void(c0) == [] and void(c1) == [] and void(r0) == [ent(8000, 1100)] and int(Pool.get(key, r0)) == 1, "REAL SELLALL: the Rare fish stays")
    K.check(Br.OWED.isEmpty() and ops() == [], "REAL SELLALL: all committed, no op file")
    # ---- CRASH at each step; restart = Sacks + Fishing memory lost, the pool + op files as they were on disk at that moment
    def restart_from(sn):
        clear_sacks(J)
        shutil.rmtree(pools, ignore_errors=True)
        os.makedirs(pools)
        for n_, b_ in sn["pools"].items():
            open(os.path.join(pools, n_), "wb").write(b_)
        S["coins"] = list(sn["persisted"])
        S["persisted"] = list(sn["persisted"])
        shutil.rmtree(bench_dir, ignore_errors=True)
        os.makedirs(bench_dir, exist_ok=True)
        for n_, b_ in sn["ops"].items():
            open(os.path.join(bench_dir, n_), "wb").write(b_)
        inv.clear()
        for s_, id_, q, md in sn["inv"]:
            st = IS(id_, q) if md is None else IS(id_, q, JClass("org.bson.BsonDocument").parse(md))
            inv.setItemStackForSlot(jpype.JShort(s_), st)
    for op_, point, expect in (("sell", "take-before", "kept"), ("sell", "take-inside", "paid"), ("sell", "add-before", "paid"),
                               ("sell", "flush-before", "paid"), ("sell", "flush-after", "window"),
                               ("fil", "take-before", "kept"), ("fil", "take-inside", "paid")):
        inv.clear()
        e = ent(2222, 444)
        fill({c0: [e]})
        S["coins"], S["persisted"], S["snaps"] = [], [], {}
        S["hook"] = point
        pg.rebuild()
        price = int(Bench.priceG(common[0], 2222, jpype.JLong(int(JClass("java.lang.System").currentTimeMillis()))))
        nfil = int(Bench.filletsG(2222))
        r = click("sell" if op_ == "sell" else "fil", 0)
        S["hook"] = None
        sn = S["snaps"].get(point)
        what = "CRASH %s at %s" % (op_, point)
        if not K.check(sn is not None and r.startswith("+"), "%s: the step was reached (%s)" % (what, r)):
            continue
        if point == "take-inside":
            dpool = sn["pools"].get(key + ".properties", b"").decode("latin-1")
            K.check(e not in dpool, "%s: the real Sacks wrote the pool file before answering (the entry is gone on disk)" % what)
        restart_from(sn)
        n_done = int(Bench.recover(inv, u, key))
        in_void = void(c0).count(e)
        paid = sum(S["coins"])
        fil = fil_count()
        cnt = int(Pool.get(key, c0))
        if op_ == "sell":
            got = "kept" if in_void == 1 and paid == 0 else ("paid" if in_void == 0 and paid == price else "dupe" if in_void == 0 and paid == 2 * price else "BAD")
        else:
            got = "kept" if in_void == 1 and fil == 0 else ("paid" if in_void == 0 and fil == nfil else "BAD")
        K.eq(cnt, in_void, "%s: after the restart the real pool's count = its entries (%d)" % (what, cnt))
        if expect == "window":
            K.notes.append("%s: RESIDUAL WINDOW (SkyyFishing's documented one, after the coin flush) - %s" % (what, got))
            K.check(got == "dupe", "%s: exactly the named residual window (got %s)" % (what, got))
        else:
            K.eq(got, expect, "%s: after restart + replay the fish is %s exactly once (void %d, paid %d, fillets %d)" % (what, expect, in_void, paid, fil))
        K.eq(ops(), [], "%s: the replay settled the op file (%d)" % (what, n_done))
        K.eq(int(Bench.recover(inv, u, key)), 0, "%s: a second replay does nothing" % what)
    K.notes.append("REAL: bench sold %d, filleted %d, replayed %d through the real SkyySacks keys" % (int(Bench.VOID_SOLD), int(Bench.VOID_FILLETED), int(Bench.REPLAYED)))
    try:
        Pool.WRITER.shutdownNow()
    except Exception:
        pass
    Store.stopIO()
    K.save()


def run_fish10(out, jar, scratch, home):
    T0810.run_fish(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("keys", run_keys), ("real", run_real), ("tg", T16.run_tg), ("fish10", run_fish10), ("live", T0810.run_live10)],
           __file__, live=(T16.T15.BETA, "Skyy_SkyySacks"))
