"""Harness for SkyyCollections 0.2.35 (round eggs D5b-4: the Crystal collection's last tier finds SkyyPets' secret Crystal dragon egg;
tools/collections_0_2_35_patch.py). Build first:
    python tools/collections_0_2_35_patch.py && python SkyyCollections/build_skyycollections_0.2.35.py
      (SkyyGear/SkyyGear-0.3.29.jar gone? set SKYY_GEAR_0329_JAR to a copy extracted from backups/archive/old-jars-20261022.tar.xz)
    python SkyyCollections/test_skyycollections_0.2.35.py [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; +1 class, no command / system; jar: only CollSecret.class added,
                the only non-class change is the manifest
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.34 -> 0.2.35 (EXPECT below)
  X    EXECUTED on a scratch registry (CollReg.loadAll): the rows' defaults (on, Crystal, last tier) + collections.properties lines read
       back (off / another collection / tier 3 / a bad tier = 0); CollSecret.check: below the tier nothing; no SkyyPets = nothing asked
       (counted) and retried only after 10 minutes; HAS_EGG = asked, no marker, asked again later; OK = the marker _secret.crystal saved,
       never asked again; GIVEN also sets it; a SkyyProfiles hold = nothing; another collection never; the door gets {UUID, "crystal",
       "SkyyCollections:Crystal <tier>"}; CollRewards.settle EXECUTES the call (a maxed Crystal profile = one door call, the marker on disk);
       fixer: HAS_DRAGON = final (marker 2); an unclaimed egg keeps owedAny true -> mark() keeps OWED -> settleAll re-asks (10 min throttle)
  LIVE every setup migration + CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest), twice: no file changes
       (no migration), the rows read their defaults
  AA   audit    the engine-access audit
NOT COVERED (UNVERIFIED in game): a live settle on the world thread after a real Crystal credit, SkyyPets' delivery of the egg.
Exit code 1 on any failure.
"""
import os, sys, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.2.35", "0.2.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_35_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "eggs", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],          # the kit: 3 new rows + the version
          "CollReg": ["~m parseReg"], "RegData": ["+f secColl", "+f secOn", "+f secTier", "~c "],
          "CollRewards": ["~m owedAny", "~m settle"], "SkyyCollectionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollSecret"]
U1S = "00000000-0000-4000-8000-0000000023c1"
U2S = "00000000-0000-4000-8000-0000000023c2"
U3S = "00000000-0000-4000-8000-0000000023c3"


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old, cmp0 = sys.argv, HK.run_compare
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
        HK.run_compare = cmp0
    return m


T31 = None


def t31():
    global T31
    if T31 is None:
        T31 = tmod(os.path.join(HERE, "test_skyycollections_0.2.31.py"), "tco0231")
    return T31


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.35"') == 1 and '[SkyyCollections] 0.2.35 ready (' in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count(' = K("') - o.count(' = K("'), 1, "S one new class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/collections/CollSecret.class"], []), "S only CollSecret.class added")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"], "S the only non-class change is the manifest")
    K.save()


def fn_proxy(f):
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, o):
            return f(o)
    return Fn()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    base = os.path.join(scratch, "xbase", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"), exist_ok=True)
    Reg = t31().boot(base)
    Reg.loadAll()
    R = Reg.D
    Sec, Sto, Rew, UUID, Long = JClass(PKG + "CollSecret"), JClass(PKG + "CollStore"), JClass(PKG + "CollRewards"), JClass("java.util.UUID"), JClass("java.lang.Long")
    ids = [str(x) for x in R.id]
    K.check("Crystal" in ids, "X the registry has the Crystal collection")
    c = ids.index("Crystal")
    its = [str(x) for x in R.items[c]] if R.items[c] is not None else []
    K.check(its and all(i.startswith("Ingredient_Crystal_") for i in its), "X Crystal = the crystal shards (%d ids: %s)" % (len(its), its[:8]))
    mx = int(Reg.maxTier(R, c))
    K.check(bool(R.secOn) and str(R.secColl) == "Crystal" and int(R.secTier) == 0 and int(Sec.tierOf(R, c)) == mx and mx >= 5,
            "X defaults: on, Crystal, tier 0 = the last (%d)" % mx)
    K.check(bool(Sec.isColl(R, c)) and not bool(Sec.isColl(R, ids.index("Wheat"))), "X only the Crystal collection")
    CALLS = []
    ANS = {"a": "HAS_EGG"}

    def door(o):
        CALLS.append((str(o[0]), str(o[1]), str(o[2])))
        return ANS["a"]
    u1 = UUID.fromString(U1S)
    k1 = U1S
    d1 = Sto.dataK(k1)
    K.check(d1 is not None, "X a fresh profile's counts load")
    t0 = 10 ** 12
    K.check(Sec.check(d1, R, c, u1, k1, mx - 1, t0) is None and int(Sec.NODOOR) == 0, "X below the last tier: nothing asked")
    K.check(Sec.check(d1, R, c, u1, k1, mx, t0) is None and int(Sec.NODOOR) == 1, "X no SkyyPets: nothing (counted once)")
    K.check(Sec.check(d1, R, c, u1, k1, mx, t0 + 1000) is None and int(Sec.NODOOR) == 1, "X ... and not asked again within 10 minutes")
    br.put("pets:fn:giveSecretEgg", fn_proxy(door))
    t1 = t0 + 600001
    a1 = Sec.check(d1, R, c, u1, k1, mx, t1)
    roman = str(JClass(PKG + "CollUtil").roman(mx))
    K.eq((str(a1), CALLS, int(Sto.meta(d1, "_secret.crystal"))), ("HAS_EGG", [(U1S, "crystal", "SkyyCollections:Crystal " + roman)], 0),
         "X after 10 min with SkyyPets: the door gets {UUID, crystal, source}; HAS_EGG = no marker")
    K.check(Sec.check(d1, R, c, u1, k1, mx, t1 + 5000) is None and len(CALLS) == 1, "X HAS_EGG: not asked again within 10 minutes")
    ANS["a"] = "OK"
    a2 = Sec.check(d1, R, c, u1, k1, mx, t1 + 600001)
    K.eq((str(a2), int(Sto.meta(d1, "_secret.crystal")), int(Sec.FOUND)), ("OK", 1, 1), "X OK = the marker _secret.crystal set, found counted")
    K.check(Sec.check(d1, R, c, u1, k1, mx, t1 + 9 * 10 ** 9) is None and len(CALLS) == 2, "X claimed once: never asked again")
    # GIVEN also closes it; a SkyyProfiles hold; switched off; another collection id; a set tier
    u2, k2 = UUID.fromString(U2S), U2S
    d2 = Sto.dataK(k2)
    br.put("profile:busy:" + U2S, "x")
    K.check(Sec.check(d2, R, c, u2, k2, mx, t0) is None and len(CALLS) == 2, "X SkyyProfiles holds the inventory: nothing asked")
    br.remove("profile:busy:" + U2S)
    ANS["a"] = "GIVEN"
    K.eq((str(Sec.check(d2, R, c, u2, k2, mx, t0 + 1)), int(Sto.meta(d2, "_secret.crystal"))), ("GIVEN", 1), "X GIVEN (another source gave it) = the marker set too")
    u3, k3 = UUID.fromString(U3S), U3S
    d3 = Sto.dataK(k3)
    R.secOn = False
    K.check(Sec.check(d3, R, c, u3, k3, mx, t0) is None, "X secret.crystal off: nothing")
    R.secOn = True
    R.secColl = "Wheat"
    K.check(Sec.check(d3, R, c, u3, k3, mx, t0) is None and bool(Sec.isColl(R, ids.index("Wheat"))), "X secret.crystal.collection = Wheat: the Crystal tier no longer counts")
    R.secColl = "Crystal"
    R.secTier = 3
    n0 = len(CALLS)
    ANS["a"] = "HAS_DRAGON"
    K.check(Sec.check(d3, R, c, u3, k3, 2, t0) is None and str(Sec.check(d3, R, c, u3, k3, 3, t0)) == "HAS_DRAGON" and len(CALLS) == n0 + 1
            and CALLS[-1][2] == "SkyyCollections:Crystal III" and int(Sto.meta(d3, "_secret.crystal")) == 2, "X secret.crystal.tier 3: tier III asks; HAS_DRAGON = final (marker 2)")
    K.check(Sec.check(d3, R, c, u3, k3, 3, t0 + 9 * 10 ** 9) is None and len(CALLS) == n0 + 1 and not bool(Sec.owed(d3, R)),
            "X fixer: HAS_DRAGON is never asked again and not owed")
    R.secTier = 0
    # the call site: CollRewards.settle on a maxed Crystal profile (no SkyyCoins / SkyySkills: their tiers stay owed; the door still runs)
    u4s = "00000000-0000-4000-8000-0000000023c4"
    u4 = UUID.fromString(u4s)
    d4 = Sto.dataK(u4s)
    for i in its:
        d4.items.put(i, Long(10 ** 9))
    K.eq(int(Sto.countTier(d4, R, c)), mx, "X the maxed profile is at the last Crystal tier")
    ANS["a"] = "OK"
    n1 = len(CALLS)
    Rew.settle(d4, R, c, u4, u4s)
    K.eq(([x[:2] for x in CALLS[n1:]], int(Sto.meta(d4, "_secret.crystal"))), ([(u4s, "crystal")], 1), "X CollRewards.settle EXECUTES the door once + sets the marker")
    Rew.settle(d4, R, c, u4, u4s)
    K.eq(len(CALLS), n1 + 1, "X a second settle: not asked again")
    Sto.save(u4s)
    cf = os.path.join(base, "counts", u4s + ".properties")
    K.check(os.path.isfile(cf) and "_secret.crystal=1" in open(cf, encoding="latin-1").read(), "X the marker is in the counts file")
    Sto.DATA.remove(u4s)
    K.eq(int(Sto.meta(Sto.dataK(u4s), "_secret.crystal")), 1, "X ... and reads back after a reload")
    # fixer (critic 1): an unclaimed egg keeps the profile OWED (owedAny -> mark -> retryOwed -> settleAll asks again)
    u5s = "00000000-0000-4000-8000-0000000023c5"
    u5 = UUID.fromString(u5s)
    d5 = Sto.dataK(u5s)
    for i in its:
        d5.items.put(i, Long(10 ** 9))
    K.check(bool(Sec.owed(d5, R)) and not bool(Sec.owed(d4, R)) and not bool(Sec.owed(d1, R)), "X fixer: owed() = maxed with no marker only")
    for pre in ("_paid.", "_paidxp.", "_paiditem.", "_cub020.", "_cu020.", "_cub021.", "_cu021.", "_paidrank."):
        Sto.setMeta(d5, u5s, pre + "Crystal", Long(mx + 100))
    oa = bool(Rew.owedAny(d5, R))
    R.secOn = False
    ob = bool(Rew.owedAny(d5, R))
    R.secOn = True
    K.eq((oa, ob), (True, False), "X fixer: owedAny is true only because of the unclaimed egg (paid markers all set)")
    Rew.OWED.remove(u5s)
    Rew.mark(u5s, d5, R)
    K.check(bool(Rew.OWED.contains(u5s)), "X fixer: mark() keeps the profile in OWED (the 30 s retryOwed re-runs settleAll)")
    ANS["a"] = "BUSY"
    n2 = len(CALLS)
    Sec.LAST.remove(u5s)
    Rew.settleAll(None, u5, u5s)
    K.check(len(CALLS) == n2 + 1 and bool(Rew.OWED.contains(u5s)), "X fixer: settleAll asks; BUSY = still OWED")
    Rew.settleAll(None, u5, u5s)
    K.eq(len(CALLS), n2 + 1, "X fixer: a 30 s retry within 10 minutes asks nothing (throttle)")
    Sec.LAST.put(u5s, Long(0))
    ANS["a"] = "OK"
    Rew.settleAll(None, u5, u5s)
    K.check(len(CALLS) == n2 + 2 and int(Sto.meta(d5, "_secret.crystal")) == 1 and not bool(Rew.OWED.contains(u5s)),
            "X fixer: after 10 minutes the retry asks again; OK = marker set, OWED cleared")
    # collections.properties lines (the kit's reload@ rows)
    pf = os.path.join(base, "collections.properties")
    K.check(os.path.isfile(pf), "X loadAll seeded collections.properties")
    raw = open(pf, "rb").read()
    for lines, want in ((b"secret.crystal=false\nsecret.crystal.collection=Gemstone\nsecret.crystal.tier=3\n", (False, "Gemstone", 3)),
                        (b"secret.crystal.tier=x\n", (True, "Crystal", 0)), (b"secret.crystal.tier=99\n", (True, "Crystal", 0))):
        open(pf, "wb").write(raw + (b"\r\n" if b"\r\n" in raw else b"\n") + lines)
        Reg.loadAll()
        R2 = Reg.D
        K.eq((bool(R2.secOn), str(R2.secColl), int(R2.secTier)), want, "X collections.properties %r -> %s" % (lines, want))
    open(pf, "wb").write(raw)
    Reg.loadAll()
    t = str(Sec.text())
    K.check("secret Crystal egg: Crystal last tier" in t and "found" in t, "X text(): %s" % t)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Reg = t31().boot(home)
    P = JClass("java.nio.file.Paths").get(home)
    s0 = t31().snapd(home)
    MIGS = ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig", "CollP7Mig")
    for cn in MIGS:
        JClass(PKG + cn).run(P)
    Reg.loadAll()
    s1 = t31().snapd(home)
    K.check(s0 == s1, "LIVE start 1 changes no file (no migration): %s" % sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))[:6])
    for cn in MIGS:
        JClass(PKG + cn).run(P)
    Reg.loadAll()
    s2 = t31().snapd(home)
    K.check(s1 == s2, "LIVE start 2 changes no file")
    R = Reg.D
    K.check(R is not None and bool(R.secOn) and str(R.secColl) == "Crystal" and int(R.secTier) == 0 and "Crystal" in [str(x) for x in R.id],
            "LIVE the live collections.properties (no secret lines) = the defaults; the Crystal collection exists")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
