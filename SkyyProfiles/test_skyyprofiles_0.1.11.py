"""Harness for SkyyProfiles 0.1.11 (lag fixes: lock-free bridge, per-player lock stripes, touch() at most once a minute;
tools/profiles_0_1_11_patch.py). Build first: python tools/profiles_0_1_11_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.11.py

    python SkyyProfiles/test_skyyprofiles_0.1.11.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.10 -> 0.1.11: exactly the listed members differ (no class added)
  X  exec     0.1.10 and 0.1.11 side by side (own class loaders over the 0.7.0 server jar, own data folders):
              DIFF   600 random profile operations (create / switch / class / bonus / username / prompted / delete / undo / archive commit /
                     restore commit / reload) on both jars: the same answers and the same players files (timestamps normalised)
              STRIPE a thread HOLDING player 1's stripe: player 2 (another stripe) commits, loads from disk, reloads and reads its file at
                     once; player 1's own commit / readPlayerFile wait until the stripe is free. CONTROL 0.1.10: holding the ProfStore
                     class monitor blocks player 2 too. Stripe = (uuid.hashCode & 0x7fffffff) % 64, 64 distinct lock objects
              STRESS 8 threads x 400 operations on 24 players at once (0.1.11; each thread owns 3 players, stripes shared): no exception, every
                     players file = its cached copy, every player's epoch = the number of its epoch-moving operations; then 8 threads
                     on the SAME 6 players: no exception, every players file = its cached copy
              TOUCH  lastPlayed younger than 60 s -> no write (file bytes + mtime unchanged); older, missing or in the future -> written
                     with now; no active profile -> nothing; CONTROL 0.1.10 writes every time
              BRIDGE ProfCfg.bridge() = the System property map (same identity), cached in BRIDGE; with System.class's monitor held by
                     another thread it still answers at once (0.1.10: waits = CONTROL)
              SCAN   the deleted-profile index scan (ProfDel.scanIndex) and the name lookup (ProfStore.resolve) read through readPlayerFile
                     and find the same players as 0.1.10; a non-player file in the folder is read through readPath (no stripe)
  D  live     start twice on a scratch COPY of the live Skyy_SkyyProfiles with 0.1.10 and 0.1.11 (setup()'s data steps): no file changed
              by either start, the same keys published
  AA engine-access audit
Scratch: tools/dev/scratch/perfmenu/profiles (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, shutil, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.10.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfmenu", "profiles")))
PKG = "com.skyy.profiles."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyProfiles")
_STRIPED = ["loadSlow", "reload", "commit", "create", "setActive", "setClass", "setBonus", "noteLogin", "markPrompted", "markDeleted",
            "unDelete", "archiveCommit", "restoreCommit", "touch"]
EXPECT = {
    "ProfCfg": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m capMigrate"],        # capMigrate: the version text of its marker comment
    "ProfStore": ["+f LK", "+f TOUCH_MS", "+m mkLocks", "+m lockOf", "+m readPath0", "~m readPath", "+m readPathFor", "+m readPlayerFile",
                  "~m readFile", "~m resolve", "+m touchDue", "~<clinit>"] + ["+m %s0" % m for m in _STRIPED] + ["~m %s" % m for m in _STRIPED],
    "ProfDel": ["~m scanIndex", "~m archiveLocked"],                               # archiveLocked: archive.version = the version text
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],             # the kit's lock-free bridge (tools/skyycfg.py) + version text
    "CfgFn": ["~m opExport"],                                                     # the version text
    "SkyyProfilesPlugin": ["~m setup"],                                            # the ready line's version
}
ADDED = []


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)([JClass("java.io.File")(jar).toURI().toURL()])
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


class Jar(object):
    """one jar in its own loader with its own players folder"""

    def __init__(self, jar, home):
        from jpype import JClass
        self.L = loader_for(jar)
        self.c = lambda n: JClass(PKG + n, loader=self.L)
        self.Store, self.Cfg, self.Del = self.c("ProfStore"), self.c("ProfCfg"), self.c("ProfDel")
        P = JClass("java.nio.file.Paths")
        os.makedirs(os.path.join(home, "players"), exist_ok=True)
        self.home = home
        self.Store.DIR = P.get(os.path.join(home, "players"))
        self.Store.SWDIR = P.get(os.path.join(home, "switching"))
        self.Store.INVDIR = P.get(os.path.join(home, "inventories"))
        self.Store.LOGF = P.get(os.path.join(home, "switches.log"))
        self.Del.ARCDIR = P.get(os.path.join(home, "archive"))

    def file(self, u):
        return os.path.join(self.home, "players", str(u) + ".properties")


def norm(props):
    """a players file / Properties as a dict with the time values normalised"""
    d = {}
    for k in props.stringPropertyNames():
        k = str(k)
        v = str(props.getProperty(k))
        if k.endswith((".lastPlayed", ".created", ".deleted", ".until")) or k.startswith("gone.") and not k.endswith(".dir"):
            v = "T"
        d[k] = v
    return d


def read_file(path):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    if os.path.isfile(path):
        s_ = JClass("java.io.FileInputStream")(path)
        try:
            p.load(s_)
        finally:
            s_.close()
    return p


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID, Props = JClass("java.util.UUID"), JClass("java.util.Properties")
    old = Jar(OLD_JAR, os.path.join(scratch, "x_old"))
    new = Jar(jar, os.path.join(scratch, "x_new"))
    rnd = random.Random(1311)
    us = [UUID(0x5157000000000000 + i, 0x1000 + i) for i in range(10)]
    classes = ["Archer", "Warrior", "Mage", "Monk", "Priest"]

    # ------------------------------------------------------------------ DIFF
    n_ops, n_true = 0, 0
    for step in range(600):
        u = rnd.choice(us)
        op = rnd.choice(["create", "create", "switch", "class", "bonus", "login", "prompted", "del", "undel", "arc", "rest", "reload"])
        res = []
        for J in (old, new):
            S = J.Store
            p = S.load(u)
            ids = [str(i) for i in range(1, 9) if S.exists(p, str(i))]
            r = None
            rs = random.Random(step)
            if op == "create":
                nid = S.nextId(p)
                r = bool(S.create(u, nid if nid is not None else "1", "Fruit%d" % step, rs.choice(classes), rs.random() < 0.5))
            elif op == "switch" and ids:
                r = bool(S.setActive(u, S.activeOf(p), rs.choice(ids), rs.choice([None, "", "0.5"])))
            elif op == "class" and ids:
                r = bool(S.setClass(u, rs.choice(ids), rs.choice(classes)))
            elif op == "bonus":
                r = bool(S.setBonus(u, rs.randint(-1, 20)))
            elif op == "login":
                S.noteLogin(u, rs.choice(["Steve", "Alex", "Bea"]))
            elif op == "prompted":
                S.markPrompted(u)
            elif op == "del" and ids:
                r = bool(S.markDeleted(u, rs.choice(ids), 1000, 2000))
            elif op == "undel" and ids:
                r = bool(S.unDelete(u, rs.choice(ids)))
            elif op == "arc" and ids:
                r = bool(S.archiveCommit(u, rs.choice(ids), 3000, "x-3000"))
            elif op == "rest":
                rec = Props()
                rid = str(rs.randint(1, 8))
                rec.setProperty("p.%s.name" % rid, "Back")
                rec.setProperty("p.%s.class" % rid, "Mage")
                r = bool(S.restoreCommit(u, rid, rec, rs.choice([None, "Kiwi"])))
            elif op == "reload":
                r = bool(S.reload(u))
            res.append(r)
        n_ops += 1
        n_true += 1 if res[0] else 0
        K.eq(res[1], res[0], "DIFF step %d %s: the same answer" % (step, op))
        if step % 25 == 0 or step == 599:
            for u2 in us:
                fo, fn = read_file(old.file(u2)), read_file(new.file(u2))
                K.eq(norm(fn), norm(fo), "DIFF step %d: players file of %s" % (step, u2))
                K.eq(norm(new.Store.load(u2)), norm(old.Store.load(u2)), "DIFF step %d: cached copy of %s" % (step, u2))
    K.notes.append("DIFF: %d operations, %d accepted" % (n_ops, n_true))

    # ------------------------------------------------------------------ STRIPE
    S = new.Store
    K.eq(len(set(int(jpype.JClass("java.lang.System").identityHashCode(x)) for x in S.LK)), 64, "STRIPE: 64 distinct lock objects")
    K.eq(len(S.LK), 64, "STRIPE: 64 stripes")

    def stripe(u):
        return (int(u.hashCode()) & 0x7fffffff) % 64
    for u in us[:3]:
        K.check(S.lockOf(u) is S.LK[stripe(u)] or S.lockOf(u).equals(S.LK[stripe(u)]), "STRIPE: lockOf(%s) = LK[%d]" % (u, stripe(u)))
    u1 = UUID(0x7000000000000001, 1)
    u2 = None
    for i in range(2, 200):
        c = UUID(0x7000000000000000 + i * 7919, 12345)
        if stripe(c) != stripe(u1):
            u2 = c
            break
    S.create(u1, "1", "Apple", "Mage", True)
    S.create(u2, "1", "Pear", "Mage", True)

    def run_bg(fn):
        box = {}

        def t():
            try:
                box["r"] = fn()
            except Exception as e:
                box["e"] = str(e)
        th = threading.Thread(target=t, daemon=True)
        th.start()
        return th, box
    lk1 = S.lockOf(u1)
    with jpype.synchronized(lk1):
        for name, fn in (("commit", lambda: S.commit(u2, S.load(u2).clone())), ("reload", lambda: S.reload(u2)),
                         ("readPlayerFile", lambda: S.readPlayerFile(S.DIR.resolve(str(u2) + ".properties"))),
                         ("setClass", lambda: S.setClass(u2, "1", "Archer")), ("touch", lambda: S.touch(u2))):
            th, box = run_bg(fn)
            th.join(5.0)
            K.check(not th.is_alive() and "e" not in box, "STRIPE: player 2's %s runs while player 1's stripe is held (%s)" % (name, box))
        th1, box1 = run_bg(lambda: S.commit(u1, S.load(u1).clone()))
        th2, box2 = run_bg(lambda: S.readPlayerFile(S.DIR.resolve(str(u1) + ".properties")))
        th1.join(0.6)
        th2.join(0.1)
        K.check(th1.is_alive() and th2.is_alive(), "STRIPE: player 1's own commit + file read wait while its stripe is held")
    th1.join(5.0)
    th2.join(5.0)
    K.check(not th1.is_alive() and box1.get("r") is True and not th2.is_alive() and "e" not in box2,
            "STRIPE: both finish once the stripe is free (%s %s)" % (box1, box2))
    # CONTROL 0.1.10: the class monitor blocks every player
    O = old.Store
    O.create(u2, "1", "Pear", "Mage", True)
    with jpype.synchronized(O.class_):
        th, box = run_bg(lambda: O.commit(u2, O.load(u2).clone()))
        th.join(0.6)
        K.check(th.is_alive(), "STRIPE CONTROL: 0.1.10 - player 2 waits while the ProfStore class monitor is held")
    th.join(5.0)
    K.check(not th.is_alive(), "STRIPE CONTROL: 0.1.10 finishes after")

    # ------------------------------------------------------------------ STRESS
    ups = [UUID(0x6000000000000000 + i, 0x77 + i) for i in range(24)]
    epochs_expected = {}
    lock = threading.Lock()
    errors = []

    def worker(seed, mine, count_epochs):
        r = random.Random(seed)
        for _ in range(400):
            u = r.choice(mine)
            try:
                p = S.load(u)
                op = r.choice(["create", "switch", "class", "bonus", "login", "reload", "touch"])
                moved = False
                if op == "create":
                    nid = S.nextId(p)
                    if nid is not None:
                        moved = bool(S.create(u, nid, "S", "Mage", r.random() < 0.3))
                elif op == "switch":
                    ids = [str(i) for i in range(1, 9) if S.live(p, str(i))]
                    if ids:
                        moved = bool(S.setActive(u, S.activeOf(p), r.choice(ids), None))
                elif op == "class":
                    a = S.activeOf(p)
                    if a is not None:
                        moved = bool(S.setClass(u, a, r.choice(classes)))
                elif op == "bonus":
                    S.setBonus(u, r.randint(0, 5))
                elif op == "login":
                    S.noteLogin(u, r.choice(["A", "B"]))
                elif op == "reload":
                    S.reload(u)
                else:
                    S.touch(u)
                if moved and count_epochs:
                    with lock:
                        epochs_expected[str(u)] = epochs_expected.get(str(u), 0) + 1
            except Exception as e:
                errors.append(str(e)[:200])
    # each thread owns 3 players (exact epoch counts; the stripes are shared across threads), then 8 threads on the SAME 6 players
    ths = [threading.Thread(target=worker, args=(s_, ups[s_ * 3:s_ * 3 + 3], True), daemon=True) for s_ in range(8)]
    t0 = time.time()
    for t in ths:
        t.start()
    for t in ths:
        t.join(120)
    K.check(not any(t.is_alive() for t in ths), "STRESS: every thread finished")
    K.eq(errors, [], "STRESS: no exception")
    bad = []
    for u in ups:
        f = read_file(new.file(u))
        if dict((str(k), str(f.getProperty(k))) for k in f.stringPropertyNames()) != dict((str(k), str(S.load(u).getProperty(k))) for k in S.load(u).stringPropertyNames()):
            bad.append(str(u))
        if int(S.num(S.load(u), "epoch")) != epochs_expected.get(str(u), 0):
            bad.append("epoch " + str(u))
    K.eq(bad, [], "STRESS: every players file = its cached copy; every epoch = its epoch-moving operations")
    shared = [UUID(0x6100000000000000 + i * 104729, 0x99) for i in range(6)]
    ths = [threading.Thread(target=worker, args=(100 + s_, shared, False), daemon=True) for s_ in range(8)]
    for t in ths:
        t.start()
    for t in ths:
        t.join(120)
    K.check(not any(t.is_alive() for t in ths), "STRESS shared: every thread finished")
    K.eq(errors, [], "STRESS shared: no exception")
    bad = []
    for u in shared:
        f = read_file(new.file(u))
        if dict((str(k), str(f.getProperty(k))) for k in f.stringPropertyNames()) != dict((str(k), str(S.load(u).getProperty(k))) for k in S.load(u).stringPropertyNames()):
            bad.append(str(u))
    K.eq(bad, [], "STRESS shared: 8 threads on the same 6 players - every players file = its cached copy")
    K.notes.append("STRESS: 3200 operations on 24 players in %.1f s" % (time.time() - t0))

    # ------------------------------------------------------------------ TOUCH
    def touch_case(J, label, lp):
        u = UUID(0x4400000000000000 + abs(hash(label)) % 100000, 5)
        J.Store.create(u, "1", "Fig", "Mage", True)
        q = J.Store.load(u).clone()
        if lp is None:
            q.remove("p.1.lastPlayed")
        else:
            q.setProperty("p.1.lastPlayed", str(lp))
        J.Store.commit(u, q)
        f = J.file(u)
        b0, m0 = open(f, "rb").read(), os.stat(f).st_mtime_ns
        time.sleep(0.05)
        J.Store.touch(u)
        b1, m1 = open(f, "rb").read(), os.stat(f).st_mtime_ns
        now = int(JClass("java.lang.System").currentTimeMillis())
        lp1 = int(J.Store.num(J.Store.load(u), "p.1.lastPlayed"))
        return (b1 != b0 or m1 != m0), lp1, now
    nowm = int(JClass("java.lang.System").currentTimeMillis())
    for label, lp, want in (("fresh", nowm - 5000, False), ("59s", nowm - 59000, False), ("61s", nowm - 61000, True),
                            ("future", nowm + 3600000, True), ("missing", None, True)):
        w, lp1, now = touch_case(new, "n" + label, lp)
        K.eq(w, want, "TOUCH: lastPlayed %s -> written %s" % (label, want))
        if want:
            K.check(abs(now - lp1) < 5000, "TOUCH: %s written with now (%d vs %d)" % (label, lp1, now))
        else:
            K.eq(lp1, lp, "TOUCH: %s keeps its stamp" % label)
        wo, _l, _n = touch_case(old, "o" + label, lp)
        K.eq(wo, True, "TOUCH CONTROL: 0.1.10 writes for %s" % label)
    un = UUID(0x4500000000000000, 9)
    new.Store.touch(un)
    K.check(not os.path.isfile(new.file(un)), "TOUCH: a player without profiles - nothing written")
    K.check(S.touchDue(Props(), "1", 1000) and not S.touchDue(read_file(new.file(u1)), "1", int(S.num(S.load(u1), "p.1.lastPlayed")) + 10),
            "TOUCH: touchDue direct")

    # ------------------------------------------------------------------ BRIDGE
    Sys = JClass("java.lang.System")
    Sys.getProperties().remove("skyy.bridge")
    new.Cfg.BRIDGE = None
    m1 = new.Cfg.bridge()
    K.check(m1 is not None and Sys.getProperties().get("skyy.bridge").equals(m1) and Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1),
            "BRIDGE: bridge() creates the System property map (same identity)")
    K.check(Sys.identityHashCode(new.Cfg.BRIDGE) == Sys.identityHashCode(m1), "BRIDGE: cached in BRIDGE")
    K.check(Sys.identityHashCode(old.Cfg.bridge()) == Sys.identityHashCode(m1), "BRIDGE: 0.1.10 finds the same map")
    with jpype.synchronized(Sys.class_):
        th, box = run_bg(lambda: new.Cfg.bridge())
        th.join(5.0)
        K.check(not th.is_alive() and Sys.identityHashCode(box.get("r")) == Sys.identityHashCode(m1), "BRIDGE: answers while System.class's monitor is held")
        th2, box2 = run_bg(lambda: old.Cfg.bridge())
        th2.join(0.6)
        K.check(th2.is_alive(), "BRIDGE CONTROL: 0.1.10 waits for System.class's monitor")
    th2.join(5.0)
    K.check(not th2.is_alive(), "BRIDGE CONTROL: 0.1.10 answers after")

    # ------------------------------------------------------------------ SCAN
    for J in (old, new):
        uu = UUID(0x3300000000000000, 3)
        J.Store.create(uu, "1", "Lime", "Mage", True)
        J.Store.create(uu, "2", "Plum", "Mage", False)
        J.Store.markDeleted(uu, "2", 1000, 99999999999999)
        J.Store.noteLogin(uu, "ScanMe")
        with open(os.path.join(J.home, "players", "notes.properties"), "w") as f_:
            f_.write("username=ScanMe2\n")
    for J in (old, new):
        J.Del.INDEX.clear()
    no, nn = int(old.Del.scanIndex()), int(new.Del.scanIndex())
    K.eq(nn, no, "SCAN: the deleted-profile index finds the same players (%d)" % no)
    K.check(nn >= 1, "SCAN: at least the scan test player")
    K.eq(str(new.Store.resolve("ScanMe")), str(old.Store.resolve("ScanMe")), "SCAN: resolve by name = 0.1.10")
    K.eq(str(new.Store.resolve("ScanMe")), str(UUID(0x3300000000000000, 3)), "SCAN: resolve by name finds the player")
    pf = new.Store.readPlayerFile(new.Store.DIR.resolve("notes.properties"))
    K.eq(str(pf.getProperty("username")), "ScanMe2", "SCAN: a non-player file goes through readPath")
    with jpype.synchronized(new.Store.class_):
        th, box = run_bg(lambda: new.Store.readPlayerFile(new.Store.DIR.resolve("notes.properties")))
        th.join(0.5)
        K.check(th.is_alive(), "SCAN: ... under the ProfStore class monitor (0.1.10's readPath)")
    th.join(5.0)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths, Files, Attr = JClass("java.nio.file.Paths"), JClass("java.nio.file.Files"), JClass("java.nio.file.attribute.FileAttribute")
    d10 = os.path.join(os.path.dirname(home), "live10", "Skyy_SkyyProfiles")
    shutil.copytree(home, d10)
    pubs = {}
    for start in (1, 2):
        for tag, j, d in (("old", OLD_JAR, d10), ("new", jar, home)):
            b0 = HK.tree_hash(d)
            L = loader_for(j)
            c = lambda n: JClass(PKG + n, loader=L)
            Cfg, Store, Del, Pub, KeyFn = c("ProfCfg"), c("ProfStore"), c("ProfDel"), c("CfgPub"), c("KeyFn")
            Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
            Store.DIR, Store.SWDIR = Paths.get(os.path.join(d, "players")), Paths.get(os.path.join(d, "switching"))
            Store.INVDIR, Store.LOGF = Paths.get(os.path.join(d, "inventories")), Paths.get(os.path.join(d, "switches.log"))
            Del.ARCDIR = Paths.get(os.path.join(d, "archive"))
            up, capm, summ = Cfg.upgradeDefault(), Cfg.capMigrate(), str(Cfg.load())
            for dd in (Store.DIR, Store.SWDIR, Store.INVDIR):
                Files.createDirectories(dd, JArray(Attr)(0))
            waiting = int(Del.scanIndex())
            br = JClass("java.util.concurrent.ConcurrentHashMap")()
            JClass("java.lang.System").getProperties().put("skyy.bridge", br)
            try:
                Cfg.BRIDGE = None
            except Exception:
                pass
            Cfg.bridge().put("profile:fn:key", KeyFn())
            Pub.start(Paths.get(os.path.dirname(d)), None)
            Pub.flush()
            time.sleep(0.3)
            Pub.flush()
            keys = {}
            pdir = os.path.join(d, "players")
            for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
                if fn.endswith(".properties"):
                    u = JClass("java.util.UUID").fromString(fn[:-11])
                    keys[fn] = str(KeyFn().apply(u))
                    Store.publish(u)
            pubs[(start, tag)] = (sorted(str(k) for k in br.keySet() if not str(k).startswith("config:")), keys, waiting, up is None, capm is None, summ[:60])
            Pub.shutdown()
            a0 = HK.tree_hash(d)
            ch = sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))
            K.eq(ch, [], "D%d %s: no file changed by the start" % (start, tag))
        K.eq(pubs[(start, "new")], pubs[(start, "old")], "D%d: 0.1.11 publishes the same keys / storage keys as 0.1.10" % start)
    K.notes.append("D: %d player files, keys %s" % (len(pubs[(1, "new")][1]), list(pubs[(1, "new")][1].values())[:3]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyProfiles"))
