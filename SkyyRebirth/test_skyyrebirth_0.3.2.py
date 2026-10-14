"""SkyyRebirth 0.3.2 - harness for the econ39 round (tools/rebirth_0_3_2_patch.py): SkyyGear 0.3.5's rebirth:part:gear is the 4th participant;
the tool-node ids SkyyGear reads match the tree; the texts name the tools.
Build first: python tools/rebirth_0_3_2_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.2.py

    python SkyyRebirth/test_skyyrebirth_0.3.2.py --dir <empty folder inside tools/dev/scratch/> [--keep]

EVERY World of the older harnesses (test_skyyrebirth_0.2.py World, reused by 0.3 / 0.3.1) is upgraded here to FOUR REAL participants: the
round's jars SkyySkills 0.4.38 + SkyyCoins 0.1.8 + SkyyBank 0.1.11 in one class loader with THIS jar, plus the REAL SkyyGear 0.3.5 jar in its
own loader on <base>/Skyy_SkyyGear (GearRb = rebirth:part:gear; seed() also writes a lifelong/<pkey>.properties with an Iron pickaxe and one
Fortune point). A RESTART = new loaders = every static of all five jars gone. The old harnesses' checks gain gear checks: Checker.new = the
gear record rebirth/<pkey>.record.properties says rb.lastTx = the rebirth's txid, rb.n, hist.<n>, and the lifelong file is byte-identical
(SkyyGear changes tools on the world thread, never in the participant); Checker.old = no gear record; staged() includes SkyyGear's staged
files (rebirth/<pkey>.rb-<txid>.properties).
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.1 -> 0.3.2: exactly the planned members differ, no class added
  G   gear     EXECUTED: the tool-node ids - every id SkyyGear's GearLL.RBNODE x RBSFX asks for is one of the tree's node ids, and the REAL
               GearLL.rbNode / rbMult read the levels bought (node.Mining.tool + tool2 ...) through the REAL rebirth:fn:node for all five
               lifelong kinds; the Works line of the tool nodes; a full 4-part rebirth (BEGIN names skills,coins,bank,gear; PREPARED gear
               with SkyyGear's facts; COMMITTED gear; the gear backup + record; the done chat line names the tools); THE CRASH PROOF at
               every point 0-7 with 4 parts + RESTART + recovery (old / new, never half; twice more = no change); crashes INSIDE gear
               (GearRb.CRASH 1 / 2 in prepare = cancelled, nothing left; CRASH 3 after the record write = the restart finishes it, the
               commit answers done; FAIL_WRITE = waits, restart finishes); SkyyGear MISSING after the decision (skills / coins / bank
               commit, "waiting for SkyyGear 0.3.5+", the gear record absent) then back = done; missing at the click = refused +
               requirement line "NO  Needs SkyyGear 0.3.5+"; a gear prepare that fails (unreadable lifelong file) = cancelled, every staged
               file gone; a 0.3.1 journal (BEGIN with skills,coins,bank) recovered by 0.3.2 finishes with ITS three parts (gear never
               called); dryrun / status (4 parts) / backups (Skyy_SkyyGear listed); the armed notes; /rebirthadmin help
  N   new      test_skyyrebirth_0.3.1.py's new phase (parser + Farming arm) on this jar with the 4-part World
  X2  x02      test_skyyrebirth_0.2.py's EXEC phase (the R3 two-phase-commit proofs: H0-H7 crash points, crashes inside every participant,
               a jar missing, income / spends while busy, profile switch, two rebirths in a row, live page clicks, torn lines, stubs,
               admin) on this jar with FOUR participants, up to its 0.2 page section (the 0.2 page API is gone since 0.3 - X02_STOP; the
               0.3 page is the exec phase, the gear page note is G); checks whose expected values changed on purpose since 0.2 are
               listed in X02_DEV (each must still occur - a deviation that no longer happens is a fail)
  X   exec     test_skyyrebirth_0.3.py's exec phase (tree, markets, Continue) with four participants (deviations: X03_DEV)
  KK  kill     the real-kill proofs (40 back-to-back 4-part rebirths killed at random + the tree kill) through THIS script's children;
               killcheck: every profile ALL-old or ALL-new across FIVE mods (the gear record agrees with SkyyRebirth's lastTx)
  D   live     test_skyyrebirth_0.3.py's live phase + a scratch COPY of the live Skyy_SkyyGear/lifelong: two starts write nothing there,
               every live profile key is measured by rebirth:part:gear (ok, nothing written)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, importlib.util, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.2"
RB = "com.skyy.rebirth."
GPKG = "com.skyy.gear."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.1.jar")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ39", "rb")))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T31 = _load("t_rb031", os.path.join(HERE, "test_skyyrebirth_0.3.1.py"))
T3, T2 = T31.T3, T31.T2
T31.VERSION = T3.VERSION = T2.VERSION = VERSION
T31.JAR = T3.JAR = T2.JAR = JAR
props, sha, tree = T2.props, T2.sha, T2.tree
U0 = T2.U0
LIVE_DIR = T2.LIVE_DIR
LL_SEED = "pickaxe.uid=rbtest-pick-1\npickaxe.id=Tool_Pickaxe_Iron\npickaxe.up.fort=1\n"

# ====================================================================================================== the 4-part World (+ the real SkyyGear)
_World0, _seed0, _new0, _old0 = T2.World, T2.seed, T2.Checker.new, T2.Checker.old


class GWorld(_World0):
    def __init__(self, base, parts=("skills", "coins", "bank"), keymap=None, start=True):
        _World0.__init__(self, base, parts=parts, keymap=keymap, start=start)
        from jpype import JClass, JArray
        URL = JClass("java.net.URL")
        self.GL = JClass("java.net.URLClassLoader")(JArray(URL)([JClass("java.io.File")(GEAR_JAR).toURI().toURL()]),
                                                     JClass("java.lang.ClassLoader").getSystemClassLoader())
        g = lambda n: JClass(GPKG + n, loader=self.GL)
        self.GCfg, self.GRb, self.GLL, self.GLog = g("GearCfg"), g("GearRb"), g("GearLL"), g("GearLog")
        gh = os.path.join(base, "Skyy_SkyyGear")
        self.GCfg.DIR = self.path(gh)
        self.GCfg.FILE = self.path(os.path.join(gh, "config.properties"))
        self.GLog.FILE = self.path(os.path.join(base, "gear-harness.log"))     # outside Skyy_SkyyGear (tree checks of that folder)
        self.gear_on = tuple(parts) == ("skills", "coins", "bank") or "gear" in parts
        if self.gear_on:
            self.br.put("rebirth:part:gear", self.GRb())

    def files(self, k):
        f = _World0.files(self, k)
        f["gear"] = os.path.join(self.base, "Skyy_SkyyGear", "lifelong", k + ".properties")
        f["gearrec"] = os.path.join(self.base, "Skyy_SkyyGear", "rebirth", k + ".record.properties")
        return f

    def staged(self):
        out = _World0.staged(self)
        d = os.path.join(self.base, "Skyy_SkyyGear", "rebirth")
        if os.path.isdir(d):
            out += ["Skyy_SkyyGear/" + f for f in os.listdir(d) if ".rb-" in f]
        return out


def gseed(base, k, cls_total, extra_skills=None, purse=None, bank=None):
    _seed0(base, k, cls_total, extra_skills=extra_skills, purse=purse, bank=bank)
    d = os.path.join(base, "Skyy_SkyyGear", "lifelong")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, k + ".properties"), "w").write(LL_SEED)


def gnew(self, W, k, what, n=1, purse=0, bank=0, mining=0, bonus=None, hist=None, expl=None):
    tx = _new0(self, W, k, what, n=n, purse=purse, bank=bank, mining=mining, bonus=bonus, hist=hist, expl=expl)
    f = W.files(k)
    rec = props(f["gearrec"])
    self.K.check(rec is not None and rec.get("rb.lastTx") == tx and rec.get("rb.n") == str(n) and rec.get("hist.%d" % n) == tx,
                 "%s: NEW state - the SkyyGear record says rb.lastTx = the rebirth's txid, rb.n %d, hist.%d: %s" % (what, n, n, rec))
    self.K.check(not os.path.exists(f["gear"]) or open(f["gear"]).read() == LL_SEED, "%s: the lifelong file is untouched by the participant" % what)
    return tx


def gold(self, W, k, hashes, what):
    _old0(self, W, k, hashes, what)
    f = W.files(k)
    self.K.check(not os.path.exists(f["gearrec"]), "%s: OLD state - no SkyyGear rebirth record" % what)
    self.K.check(not os.path.exists(f["gear"]) or open(f["gear"]).read() == LL_SEED, "%s: OLD state - the lifelong file untouched" % what)


T2.World = GWorld
T2.seed = T3.seed = gseed
T2.Checker.new = gnew
T2.Checker.old = gold

EXPECT = {
    "RbJournal": ["~<clinit>"],                                    # PARTS + JARS: + gear / SkyyGear 0.3.5+
    "RbTx": ["~m backups", "~m finish"],                           # + Skyy_SkyyGear; the done line names the tools
    "RbPage": ["~m fill"],                                         # the armed notes
    "RbAdmin": ["~m help", "~m run"],                              # help + the rebirth / crashtest confirm name the tools
    "RbTree": ["~<clinit>"],                                       # the tool nodes' Works line
    "SkyyRebirthPlugin": ["~m setup"],                             # the ready line (version + gear)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],            # the kit's version text
    "RbStore": ["~m writeNow"],                                    # the file comment's version
}
ADDED = []

# checks of the older harnesses whose expected values changed ON PURPOSE (each must still be hit, see dev())
X02_DEV = {
    "X config:def:SkyyRebirth: 9 rows": "0.3 has more rows (the tree + stat rows) - checked by the 0.3 exec phase",
    "LIVE below max: DECIDED abort names the class level": "0.3 begins a live rebirth only after the market re-check (no Bazaar / AH on "
                                                           "this bridge = refused before BEGIN, nothing changed - the CK.old check above passed); 0.3's exec covers live starts",
    "LIVE below max: the player is told it was cancelled": "the same (refused before BEGIN)",
    "TWICE: level coins pay again after rebirth 2": "SkyySkills 0.4.38 (the round's jar) pays level coins x0.8 per rebirth, 0.4.36 paid x0.9 - "
                                                    "a SkyySkills number, not a SkyyRebirth path",
}
X02_STOP = "has no attribute 'goOn'"     # the 0.2 page API (goOn) is gone since 0.3 - its section 8+ is 0.3's exec phase / G here
X03_DEV = {}


def sub(fn, name):
    """an older phase in its own scratch sub-folder (the harnesses reuse folder names like full / halt3)"""
    def run(out, jar, scratch, home):
        d = os.path.join(scratch, name)
        os.makedirs(d, exist_ok=True)
        return fn(out, jar, d, home)
    return run


def dev(fn, devs, stop=None):
    """run an older harness phase; a FAILED check whose text contains a key of devs is an expected deviation (noted, not failed); every
    key must be hit at least once (else the list is stale = a fail). stop = an AttributeError text where the old phase ends on purpose
    (an API the newer version removed): the checks so far are saved with a note"""
    def run(out, jar, scratch, home):
        orig = HK.Child.check
        orig_init = HK.Child.__init__
        made = []

        def init(self, o_):
            orig_init(self, o_)
            made.append(self)
        HK.Child.__init__ = init
        hit = dict((d_, 0) for d_ in devs)

        def check(self, cond, what):
            if not cond:
                for d_ in devs:
                    if d_ in what:
                        hit[d_] += 1
                        self.notes.append("EXPECTED DEVIATION (%s): %s" % (devs[d_], what[:240]))
                        self.ok += 1
                        return True
            return orig(self, cond, what)
        HK.Child.check = check
        try:
            fn(out, jar, scratch, home)
        except AttributeError as e:
            if stop is None or stop not in str(e) or not made:
                raise
            made[-1].notes.append("STOPPED ON PURPOSE at %r (an API removed since; the newer phases cover it) after %d ok checks" % (str(e)[:120], made[-1].ok))
            made[-1].save()
        finally:
            HK.Child.check = orig
            HK.Child.__init__ = orig_init
        d = json.load(open(out))
        for d_, n_ in hit.items():
            if n_ == 0:
                d["fails"].append("deviation list stale: no failed check contains %r" % d_)
        json.dump(d, open(out, "w"), indent=1)
    return run


# ====================================================================================================== G: the gear participant, end to end
def run_gear(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Obj, Integer = JClass("java.lang.Object"), JClass("java.lang.Integer")
    k = U0
    W0 = GWorld(os.path.join(scratch, "g0"))
    CK = T2.Checker(K, W0)
    CK.K = K

    def fresh(name, **kw):
        base = os.path.join(scratch, name)
        gseed(base, k, CK.cls_total, **kw)
        W = GWorld(base)
        W.br.put("class:" + k, "Archer")
        f = W.files(k)
        return W, base, dict((m_, sha(f[m_])) for m_ in ("skills", "coins", "bank", "gear"))

    def restart(base, **kw):
        W = GWorld(base, **kw)
        W.br.put("class:" + k, "Archer")
        return W

    def journal_done(base, tx):
        return open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", k + "." + tx + ".journal"), encoding="utf8").read()

    # ---- the parts table
    K.check(list(W0.Jr.PARTS) == ["skills", "coins", "bank", "gear"] and list(W0.Jr.JARS)[3] == "SkyyGear 0.3.5+" and str(W0.Jr.jar("gear")) == "SkyyGear 0.3.5+",
            "G PARTS = skills, coins, bank, gear (JARS SkyyGear 0.3.5+): %s" % list(W0.Jr.PARTS))
    # ---- (2) THE TOOL NODE IDS: what SkyyGear asks = what the tree sells; the REAL GearLL.rbNode / rbMult through the REAL rebirth:fn:node
    Tr = JClass(RB + "RbTree", loader=W0.L)
    nid = [str(x) for x in Tr.NID]
    asks = [str(a) + str(b) for a in W0.GLL.RBNODE for b in W0.GLL.RBSFX]
    K.check(len(asks) == 10 and all(a in nid for a in asks), "G the 10 node ids SkyyGear 0.3.5 reads (GearLL.RBNODE x RBSFX) are all tree node ids: %s" % sorted(set(asks)))
    Wn, bn, _H = fresh("nodes")
    rbp = os.path.join(bn, "Skyy_SkyyRebirth", "players")
    os.makedirs(rbp, exist_ok=True)
    open(os.path.join(rbp, k + ".properties"), "w").write("n=1\nnode.Mining.tool=2\nnode.Mining.tool2=1\nnode.Foraging.tool=1\nnode.Farming.tool2=4\nnode.Fishing.tool=5\nnode.Fishing.tool2=1\n")
    Wn.Sto.CACHE.clear()
    Wn.Sto.get(k)
    t0 = time.time()
    while not bool(Wn.Sto.ready(k)) and time.time() - t0 < 5:
        time.sleep(0.05)
        Wn.Sto.get(k)
    u = Wn.uuid(k)
    lv = [int(Wn.GLL.rbNode(u, i)) for i in range(5)]
    K.check(lv == [3, 1, 4, 4, 6], "G the REAL SkyyGear GearLL.rbNode reads the levels bought through the REAL rebirth:fn:node: pickaxe 2+1, hatchet 1, hoe + sickle 4 (Farming), pole 5+1: %s" % lv)
    mult = float(Wn.GLL.rbMult(u, 0))
    K.check(abs(mult - (1.0 + 3 * int(Wn.GCfg.LL_RBPCT) / 100.0)) < 1e-9 and int(Wn.GCfg.LL_RBPCT) == 5, "G rbMult (pickaxe) = 1 + 3 levels x 5 %% = %s" % mult)
    K.check(int(Wn.GLL.rbNode(Wn.uuid("00000000-0000-4000-8000-0000000003ff"), 0)) == 0, "G a profile with no nodes = 0")
    live = dict((str(Tr.NID[i]), str(Tr.NLIVE[i])) for i in range(len(nid)))
    K.check(all(live[a + ".tool"].startswith("now (SkyyGear") and live[a + ".tool2"].startswith("now (SkyyGear") for a in ("Mining", "Foraging", "Farming"))
            and live["Fishing.tool"].startswith("after a later Fishing update"), "G the tool nodes' Works line: Mining / Foraging / Farming now, Fishing later: %s"
            % [live[a + ".tool"] for a in ("Mining", "Fishing")])

    # ---- a full rebirth with four parts
    W, base, H = fresh("full")
    u = W.uuid(k)
    m_ = str(W.br.get("rebirth:part:gear").apply(JArray(Obj)(["measure", k, "tx1760000000001-a1b2c3", Integer(1), ""])))
    K.check(m_.startswith("ok:kinds=1;points=") and "pickaxe:Tool_Pickaxe_Iron" in m_, "G SkyyGear measures the seeded profile: %s" % m_)
    r = str(W.Tx.adminStart(u, -1))
    tx = CK.new(W, k, "G full 4-part rebirth")
    dj = journal_done(base, tx)
    K.check(r.startswith("+Rebirth tx") and (" skills,coins,bank,gear force") in dj.split("\n")[0] and "\nPREPARED gear kinds=1;points=" in dj
            and "\nCOMMITTED gear\n" in dj and dj.index("COMMITTED bank") < dj.index("COMMITTED gear"),
            "G the journal: BEGIN names 4 parts, PREPARED gear with SkyyGear's facts, COMMITTED gear (after bank): %r" % dj[:200])
    K.check(os.path.isfile(os.path.join(base, "Skyy_SkyyGear", "rebirth-backup", k, tx, k + ".properties")), "G SkyyGear backed up lifelong/<pkey> (rebirth-backup/<pkey>/<txid>)")
    told = [str(t) for t in W.told]
    K.check(any("rebirth 1 done" in t and "your lifelong tools are Crude again (upgrade points gone) and your Mining armor is Copper again" in t for t in told), "G fix: the done line names the tools AND the Mining armor: %s" % told[-1:])
    W2 = restart(base)
    h_after = tree(base)
    K.check(int(W2.Tx.recoverAll(True)) == 0 and tree(base) == h_after, "G a restart after the finished rebirth changes nothing")
    bl = [str(x) for x in W2.Adm.run(u, "backups", 1000)]
    K.check(len(bl) == 4 and bl[3].startswith("=Skyy_SkyyGear/rebirth-backup/" + k + ": " + tx), "G /rebirthadmin backups lists the 4 mods (+ Skyy_SkyyGear): %s" % bl)
    st = [str(x) for x in W2.Tx.status(u)]
    K.check(any(x == "=Every part is loaded (4)." for x in st), "G status: every part loaded (4): %s" % st)

    # ---- THE CRASH PROOF with 4 parts: halt after every point, RESTART, recover
    for p in range(8):
        W, base, H = fresh("halt%d" % p)
        u = W.uuid(k)
        W.Tx.adminStart(u, p)
        K.check(W.Sto.BUSY.containsKey(k) and W.Tx.HALTED.containsKey(k), "GH%d: stopped after point %d with 4 parts" % (p, p))
        rec_mid = os.path.exists(W.files(k)["gearrec"])
        K.check(rec_mid == (p >= 5), "GH%d: the gear record exists only once every part committed (point 5+): %s" % (p, rec_mid))
        W2 = restart(base)
        K.check(W2.open == 1 and W2.Sto.BUSY.containsKey(k), "GH%d RESTART: busy at start" % p)
        W2.Tx.recoverAll(False)
        if p <= 2:
            CK.old(W2, k, H, "GH%d (before the decision)" % p)
        else:
            CK.new(W2, k, "GH%d (after the decision)" % p)
        snap = tree(base)
        W2.Tx.recoverAll(True)
        W3 = restart(base)
        W3.Tx.recoverAll(True)
        K.check(tree(base) == snap, "GH%d: recovered twice more + restarted = no file changes" % p)

    # ---- crashes INSIDE the gear participant
    for label, crash in (("prepare after the backup", 1), ("prepare after the staged file", 2)):
        W, base, H = fresh("gcrash%d" % crash)
        u = W.uuid(k)
        W.GRb.CRASH = crash
        r = str(W.Tx.adminStart(u, -1))
        W.GRb.CRASH = 0
        _op, dn = W.journals()
        K.check(any("gear could not get ready" in open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", d), encoding="utf8").read() for d in dn),
                "G CRASH %d (%s): the rebirth is cancelled (gear could not get ready)" % (crash, label))
        CK.old(W, k, H, "G CRASH %d (%s)" % (crash, label))
    W, base, H = fresh("gcrash3")
    u = W.uuid(k)
    W.GRb.CRASH = 3
    W.Tx.adminStart(u, -1)
    W.GRb.CRASH = 0
    K.check(W.Sto.BUSY.containsKey(k) and "gear could not finish" in str(W.Tx.WAIT.get(k)) and os.path.exists(W.files(k)["gearrec"]),
            "G CRASH 3 (after the gear record write): the rebirth waits, the record is on disk: %s" % W.Tx.WAIT.get(k))
    W2 = restart(base)
    W2.Tx.recoverAll(False)
    CK.new(W2, k, "G CRASH 3 + RESTART (the commit answers done)")
    K.check(int(W2.GRb.N[2]) == 1, "G CRASH 3: the repeated commit answered done (GearRb N[2] = %d)" % int(W2.GRb.N[2]))
    W, base, H = fresh("gfail")
    u = W.uuid(k)
    W.GRb.FAIL_WRITE = 1
    W.Tx.adminStart(u, -1)
    K.check(W.Sto.BUSY.containsKey(k) and "gear could not finish" in str(W.Tx.WAIT.get(k)) and not os.path.exists(W.files(k)["gearrec"]),
            "G FAIL_WRITE: the gear record write fails - the rebirth waits (skills / coins / bank committed): %s" % W.Tx.WAIT.get(k))
    W.Tx.recoverAll(False)
    CK.new(W, k, "G FAIL_WRITE + the 30 s retry")

    # ---- SkyyGear missing after the decision, then back; missing at the click
    W, base, H = fresh("gmissing")
    u = W.uuid(k)
    W.Tx.adminStart(u, 3)
    Wm = restart(base, parts=("skills", "coins", "bank"))
    Wm.br.remove("rebirth:part:gear")
    Wm.Tx.recoverAll(False)
    K.check(Wm.Sto.BUSY.containsKey(k) and "waiting for SkyyGear 0.3.5+" in str(Wm.Tx.WAIT.get(k)) and not os.path.exists(Wm.files(k)["gearrec"])
            and props(Wm.files(k)["bank"]).get("balance") == "0", "G GEAR MISSING after the decision: skills / coins / bank committed, 'waiting for SkyyGear 0.3.5+', no gear record: %s" % Wm.Tx.WAIT.get(k))
    K.check(not Wm.CS.take(u, 1), "G GEAR MISSING: spends stay refused while it waits")
    Wb = restart(base)
    Wb.Tx.recoverAll(False)
    CK.new(Wb, k, "G GEAR BACK")
    W, base, H = fresh("gmissing_click")
    Wc = restart(base)
    Wc.br.remove("rebirth:part:gear")
    r = str(Wc.Tx.adminStart(Wc.uuid(k), -1))
    Wc.Cfg.HUB_TEST = "hub"
    Wc.Cfg.ON = True
    line = str(Wc.Chk.reqs(Wc.uuid(k), "hub", 0)[0][0])
    Wc.Cfg.ON = False
    K.check(r.startswith("-Rebirth needs SkyyGear 0.3.5+") and line == "NO  Needs SkyyGear 0.3.5+", "G GEAR MISSING at the click: refused + requirement line: %s | %s" % (r, line))
    CK.old(Wc, k, H, "G GEAR MISSING at the click")

    # ---- a gear prepare that fails (an unreadable lifelong file) = cancelled, every staged file gone
    W, base, H = fresh("gprepfail")
    u = W.uuid(k)
    lf = W.files(k)["gear"]
    os.remove(lf)
    os.makedirs(lf)
    W.Tx.adminStart(u, -1)
    _op, dn = W.journals()
    K.check(not W.staged() and not W.Sto.BUSY.containsKey(k) and props(W.files(k)["rebirth"]) is None and sha(W.files(k)["skills"]) == H["skills"]
            and sha(W.files(k)["coins"]) == H["coins"] and sha(W.files(k)["bank"]) == H["bank"] and not os.path.exists(W.files(k)["gearrec"])
            and any("gear could not get ready" in open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", d), encoding="utf8").read() for d in dn),
            "G GEAR PREPARE FAILS (unreadable lifelong file): cancelled, the skills / coins / bank staged files deleted, nothing changed")

    # ---- a 0.3.1 journal (3 parts in its BEGIN line) recovered by 0.3.2: finishes with its own parts, gear never called
    W, base, H = fresh("old_journal")
    jf = os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal")
    os.makedirs(os.path.dirname(jf), exist_ok=True)
    t31 = "tx1760000000777-0a0b0c"
    open(jf, "w", encoding="utf8").write("BEGIN %s %s 1 %s skills,coins,bank force\n" % (t31, k, k))
    W2 = restart(base)
    W2.br.put("rebirth:part:gear", W2.Fn(lambda o: "err:the 0.3.1 journal must never call gear"))
    W2.Tx.recoverAll(False)
    _op, dn = W2.journals()
    K.check(not _op and any(d.startswith(k + "." + t31) for d in dn) and "ABORTED" in journal_done(base, t31) and not os.path.exists(W2.files(k)["gearrec"]),
            "G a 0.3.1 journal (BEGIN only, no decision) recovered by 0.3.2: aborted with its 3 parts, gear never asked")
    # the same with a DECIDED commit (the 0.3.1 run was past the decision): finishes with skills / coins / bank only
    W, base, H = fresh("old_journal2")
    u = W.uuid(k)
    W.Tx.adminStart(u, 3)
    jf2 = os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal")
    t_ = open(jf2, encoding="utf8").read()
    txh = t_.split()[1]
    t_ = t_.replace(" skills,coins,bank,gear force", " skills,coins,bank force")
    t_ = "\n".join(l_ for l_ in t_.split("\n") if not l_.startswith("PREPARED gear"))
    open(jf2, "w", encoding="utf8").write(t_)
    for f_ in os.listdir(os.path.join(base, "Skyy_SkyyGear", "rebirth")):
        os.remove(os.path.join(base, "Skyy_SkyyGear", "rebirth", f_))           # what 0.3.1 never made
    W2 = restart(base)
    calls = []
    W2.br.put("rebirth:part:gear", W2.Fn(lambda o: (calls.append(str(o[0])), "err:never")[1]))
    W2.Tx.recoverAll(False)
    rp = props(W2.files(k)["rebirth"])
    K.check(rp is not None and rp.get("lastTx") == txh and rp.get("n") == "1" and props(W2.files(k)["coins"]).get("balance") == "0"
            and not calls and not os.path.exists(W2.files(k)["gearrec"]) and not W2.Sto.BUSY.containsKey(k),
            "G a 0.3.1 journal past the decision finishes with skills / coins / bank, gear never called: %s %s" % (rp and rp.get("n"), calls))

    # ---- dry run, admin texts, the armed notes
    W, base, H = fresh("admin")
    u = W.uuid(k)
    t_ = tree(base)
    lines = [str(x) for x in W.Tx.dryRun(u)]
    K.check(tree(base) == t_ and any(x.startswith("=gear: kinds=1;points=") for x in lines), "G dryrun: gear measured, nothing written: %s" % [x for x in lines if "gear" in x])
    hl = " ".join(str(x) for x in W.Adm.run(u, "help", 1000))
    cf = str(W.Adm.run(u, "rebirth", 2000)[0])
    K.check("purse, bank, lifelong tools (back to Crude) and Mining armor (back to Copper)" in hl and "lifelong tools (back to Crude) and Mining armor (back to Copper)" in cf, "G fix: /rebirthadmin help + the rebirth confirm name the tools AND the Mining armor: %s" % cf[:160])
    W.Cfg.HUB_TEST = "hub"
    W.Cfg.ON = True
    W.br.put("bazaar:fn:wouldclose", W.Fn(lambda o: "ok:0:0:0:0"))
    W.br.put("ah:fn:wouldclose", W.Fn(lambda o: "ok:0:0:0:0"))
    pg = W.Page(u, "hub")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    pg.build(None, UCB(), UEB(), None)
    t1 = int(JClass("java.lang.System").currentTimeMillis())
    K.check(int(pg.goKind) == 1 and str(pg.click(t1, "hub", False)) == "=armed", "G the page offers Rebirth (every requirement met, 4 parts loaded) and arms")
    pg.build(None, UCB(), UEB(), None)
    K.eq(str(pg.note), "Resets skills, coins, tools, Mining armor! Press again in 10 s.", "G fix: the armed note names the tools AND the Mining armor")
    W.Cfg.ON = False
    gen = open(os.path.join(HERE, "build_skyyrebirth_%s.py" % VERSION), encoding="utf8").read()
    K.check('"Closes orders (fees kept), resets skills, coins, gear! Press again."' in gen and gen.count("NO  Needs SkyyGear 0.3.5+") == 1
            and "identified Mining armor back to Copper" in gen and "and Mining armor (back to Copper) - type it twice" in gen,
            "G static: the Continue armed note + the fit list have the new texts")
    K.save()


# ====================================================================================================== KK: the kills through THIS script
def run_kill(out, jar, scratch, _home):
    K = HK.Child(out)
    env = dict(os.environ)
    for rnd in range(4):
        d = os.path.join(scratch, "kill%d" % rnd)
        for i in range(40):
            kk = "00000000-0000-4000-8000-%012d" % (5000 + i)
            gseed(d, kk, 10, purse=1000 + i, bank=50000 + i)
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "killer", "--out", os.path.join(scratch, "kk.json"), "--dir", scratch,
                              "--jar", jar, "--kdir", d], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 120:
            time.sleep(0.02)
        time.sleep(random.Random(rnd).uniform(0.05, 1.2))
        p.kill()
        p.wait()
        K.check(not os.path.exists(os.path.join(d, "finished")), "KK%d: killed mid-run (rc %s)" % (rnd, p.returncode))
    for rnd in range(4):
        d = os.path.join(scratch, "tkill%d" % rnd)
        for i in range(20):
            kk = "00000000-0000-4000-8000-%012d" % (7000 + i) + ("-p2" if i % 2 else "")
            T3.write_rb(d, kk, dict([("n", 2)] + [("pts." + a_, 400) for a_ in T3.ARMS]))
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "treekiller", "--out", os.path.join(scratch, "tk.json"), "--dir", scratch,
                              "--jar", jar, "--kdir", d, "--seed", str(rnd)], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 120:
            time.sleep(0.02)
        time.sleep(random.Random(100 + rnd).uniform(0.5, 2.5))
        p.kill()
        p.wait()
        K.check(p.returncode != 0, "TK%d: the tree child killed mid-run (rc %s)" % (rnd, p.returncode))
    K.save()


def run_killcheck(out, jar, scratch, home):
    T3.run_killcheck(out, jar, scratch, home)
    K = HK.Child(out + ".gear")
    for rnd in range(4):
        d = os.path.join(scratch, "kill%d" % rnd)
        bad, news = [], 0
        for i in range(40):
            kk = "00000000-0000-4000-8000-%012d" % (5000 + i)
            rp = props(os.path.join(d, "Skyy_SkyyRebirth", "players", kk + ".properties"))
            rec = props(os.path.join(d, "Skyy_SkyyGear", "rebirth", kk + ".record.properties"))
            n = int(rp.get("n", "0")) if rp else 0
            if n == 1:
                news += 1
                if not (rec and rec.get("rb.lastTx") == rp.get("lastTx") and rec.get("rb.n") == "1"):
                    bad.append((i, "new without the matching gear record", rec))
            elif rec is not None:
                bad.append((i, "old with a gear record", rec))
            if open(os.path.join(d, "Skyy_SkyyGear", "lifelong", kk + ".properties")).read() != LL_SEED:
                bad.append((i, "lifelong file changed"))
        staged = [f for f in os.listdir(os.path.join(d, "Skyy_SkyyGear", "rebirth")) if ".rb-" in f] if os.path.isdir(os.path.join(d, "Skyy_SkyyGear", "rebirth")) else []
        K.check(not bad and not staged, "KK%d gear: %d new profiles each with the matching SkyyGear record, the old ones none, no gear staged file: %s %s" % (rnd, news, bad[:2], staged[:2]))
    K.save()
    a = json.load(open(out))
    b = json.load(open(out + ".gear"))
    a["ok"] += b["ok"]
    a["fails"] += b["fails"]
    a["notes"] += b["notes"]
    json.dump(a, open(out, "w"), indent=1)


# ====================================================================================================== D: live copies (+ Skyy_SkyyGear/lifelong)
def run_live(out, jar, scratch, home):
    mods = os.path.dirname(home)
    src = os.path.join(T2.MODS_LIVE, "Skyy_SkyyGear", "lifelong")
    dst = os.path.join(mods, "Skyy_SkyyGear", "lifelong")
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    g0 = tree(os.path.join(mods, "Skyy_SkyyGear")) if os.path.isdir(os.path.join(mods, "Skyy_SkyyGear")) else {}
    T3.run_live(out, jar, scratch, home)
    from jpype import JClass, JArray
    K = HK.Child(out + ".gear")
    W = GWorld(mods)
    g1 = tree(os.path.join(mods, "Skyy_SkyyGear")) if os.path.isdir(os.path.join(mods, "Skyy_SkyyGear")) else {}
    Obj = JClass("java.lang.Object")
    keys = sorted(f[:-11] for f in os.listdir(dst) if f.endswith(".properties")) if os.path.isdir(dst) else []
    res = [str(W.br.get("rebirth:part:gear").apply(JArray(Obj)(["measure", kk, "tx1760000000001-a1b2c3", JClass("java.lang.Integer")(1), ""]))) for kk in keys]
    g2 = tree(os.path.join(mods, "Skyy_SkyyGear")) if os.path.isdir(os.path.join(mods, "Skyy_SkyyGear")) else {}
    K.check(g0 == g1 == g2, "D the copied Skyy_SkyyGear/lifelong is byte-identical after the starts and the measures (%d files)" % len(g0))
    K.check(all(r_.startswith("ok:kinds=") for r_ in res), "D every live lifelong key (%d) measured by rebirth:part:gear: ok, nothing written: %s" % (len(keys), [r_ for r_ in res if not r_.startswith("ok:")][:3]))
    K.notes.append("D live gear measures: %s" % res[:4])
    K.save()
    a = json.load(open(out))
    b = json.load(open(out + ".gear"))
    a["ok"] += b["ok"]
    a["fails"] += b["fails"]
    a["notes"] += b["notes"]
    json.dump(a, open(out, "w"), indent=1)


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") == "killer":
        T2.run_killer(None, JAR, SCRATCH, None)
        sys.exit(0)
    if "--phase" in sys.argv and HK.arg("--phase") == "treekiller":
        T3.run_treekiller(None, JAR, SCRATCH, None)
        sys.exit(0)
    for j_ in (T2.SK_JAR, T2.CO_JAR, T2.BK_JAR, T2.PF_JAR, T3.AH_JAR, T3.BZ_JAR, OLD_JAR, GEAR_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("gear", sub(run_gear, "g")), ("new", sub(T31.run_new, "n")), ("x02", sub(dev(T2.run_exec, X02_DEV, X02_STOP), "x2")),
                   ("exec", sub(dev(T3.run_exec, X03_DEV), "x3")),
                   ("kill", run_kill), ("killcheck", run_killcheck), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
