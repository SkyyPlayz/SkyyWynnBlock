"""SkyyRebirth 0.2 - harness for REBIRTH R3 (the journaled two-phase commit with SkyySkills 0.4.36, SkyyCoins 0.1.7, SkyyBank 0.1.11;
SkyyProfiles 0.1.13 refuses a switch while it runs) - tools/rebirth_0_2_patch.py.
Build first: python tools/rebirth_0_2_patch.py && python SkyyRebirth/build_skyyrebirth_0.2.py  (+ the four other jars of the round)

    python SkyyRebirth/test_skyyrebirth_0.2.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Every phase is a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch). A "RESTART" below = a NEW class
loader holding the four REAL jars (SkyyRebirth 0.2, SkyySkills 0.4.36, SkyyCoins 0.1.7, SkyyBank 0.1.11) on the files exactly as the
crash left them: every static (memory) is gone, the shared bridge is wiped, each mod's start-up data steps run again, then recovery.
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1 -> 0.2: exactly the planned members differ; RbJ, RbJournal, RbTell, RbTx, RbRun, RbAdmin, RbAdminArgsCmd, RbAdminCmd added
  X   exec     EVERY NEW CODE PATH with the real parts: a full rebirth (every file of every mod = the new state: skills reset but
               Exploration, paid markers 0, purse 0, bank 0 + rb.bonus = the spec 3.3 formula + rb.hist.1, our n / points (the spec 3.5
               curve recomputed here) / title / lastTx, the journal in done/, no staged file left, backups in every mod, BUSY gone, the
               player told); THE CRASH PROOF at EVERY point 0-7 (crashtest halt) + RESTART + recovery: 0-2 = the old state (the live files
               byte-identical), 3-7 = the full new state, never half; recovered TWICE more + restarted again = nothing changes (no
               double bank bonus, no coins lost / made); a crash INSIDE each participant's write (SkyySkills FAIL_SAVE, SkyyCoins
               FAIL_FLUSH and its flush stopped at steps 1-3, SkyyBank FAIL_WRITE) + RESTART = the full new state; a PARTICIPANT JAR
               MISSING after the decision (the others commit, "waiting for SkyyBank", busy stays, the bank untouched, spends refused) then
               back = done, bonus once; missing at the click = refused; INCOME during the busy window (coins:fn:add, a bank credit, an
               interest payout, skill XP) kept, SPENDS refused (coins take, bank deposit = 6, the REAL SkyyProfiles 0.1.13 switch check);
               a PROFILE SWITCH mid-rebirth (profile:fn:key flips) = the clicked profile reset, the other byte-identical; TWO rebirths
               in a row (n 2, points add up, the bonus capped / summed, hist.2) + the level coins x0.9^2 after it; a live (player) rebirth
               with the class below max = aborted by the decision; a prepare that fails (an unreadable purse) = aborted, every staged file
               deleted; a TORN journal line (crash mid-append) = never written; rebirth:fn:decision commit / abort / unknown; the dry run
               writes nothing; /rebirthadmin run(): help / status / dryrun / backups / rebirth + crashtest (confirm twice) / recover;
               the page: requirement line 1 (off / a part missing / busy / a profile switch running / ok), the Rebirth button only
               behind the switch + every requirement (goOn, its binding), the 10 s arm, a player rebirth from two clicks; RbRun 0-3
               (the 30 s tick on the real SkyyRebirth-IO thread skips a crashtest stop, recover takes it); startup() with an unreadable
               journal (busy, waits); RbMath.bonusPpm / maxPpm / pct; the config (9 rows, bank.* clamps)
  KK  kill     a REAL KILL: a child JVM runs 40 back-to-back rebirths on 40 profiles; the parent kills the process at a random moment (4
               rounds); a fresh JVM restarts + recovers: every profile is ALL-old or ALL-new across the four mods (skills, purse, bank,
               rebirth count agree), no journal open, no staged file
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyySkills + Skyy_SkyyCoins + Skyy_SkyyBank: only Skyy_SkyyRebirth/ is
               written (config), the copied folders stay byte-identical, no journal; every live profile-1 key MEASURED by every part:
               nothing written
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, hashlib, math, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.2"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.1.jar")
SK_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.36.jar")
CO_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-0.1.7.jar")
BK_JAR = os.path.join(ROOT, "SkyyBank", "SkyyBank-0.1.11.jar")
PF_JAR = os.path.join(ROOT, "SkyyProfiles", "SkyyProfiles-0.1.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth3", "rb")))
MODS_LIVE = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")
LIVE_DIR = os.path.join(MODS_LIVE, "Skyy_SkyySkills")
DAY = 86400000

EXPECT = {
    "RbCfg": ["+f BANK_BASE", "+f BANK_MAX", "+f BANK_PER", "~<clinit>", "~m loadCfg", "~m writeDefaults"],   # the bank rows + the default text
    "RbCheck": ["~m reqs", "~m tip"],               # requirement line 1 (parts / busy / profile switch); the tooltip's last line
    "RbFn": ["~m apply"],                           # rebirth:fn:decision from the journals
    "RbMath": ["+m bonusPpm", "+m maxPpm", "+m pct"],
    "RbPage": ["+f armedAt", "+f goOn", "+f last", "+f note", "+m click", "~m build", "~m fill", "~m handleDataEvent"],
    "RbStore": ["~m writeNow", "+f PEND", "~<clinit>"],          # the file comment's version + fsync (fix round 2); PEND = decided new n (fix round 2)
    "SkyyRebirthPlugin": ["+f recov", "~m setup", "~m shutdown"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],   # the kit: 3 rows + the version text
}
ADDED = ["RbJ", "RbJournal", "RbTell", "RbTx", "RbRun", "RbAdmin", "RbAdminArgsCmd", "RbAdminCmd"]

U0 = "00000000-0000-4000-8000-0000000003a1"
SEED = {"purse": 5000000, "bank": 20000000, "Mining": 200000, "Foraging": 50000, "Farming": 1000, "Exploration": 12345, "Acrobatics": 500}


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def props(p):
    if not os.path.isfile(p):
        return None
    out = {}
    for ln in open(p, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        a, b = ln.split("=", 1)
        out[a.strip()] = b.strip()
    return out


def tree(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), sha(os.path.join(r, f))) for r, _ds, fs in os.walk(d) for f in fs)


def pts(run, to_cap, b):
    if run <= 0 or to_cap <= 0:
        return 0
    r = run / float(to_cap)
    if r < 0.25:
        return 0
    return int(math.floor(b * math.sqrt(min(r, 16.0))))


def bonus_ppm(bal, base=0.25, per=1.0):
    if bal <= 0:
        return 0
    x = base * math.log10(1.0 + bal / 100000.0)
    x = min(x, per)
    return int(math.floor(x * 10000.0 + 0.5)) if x > 0 else 0


def ppm_text(ppm):
    return "%d.%04d" % (ppm // 10000, ppm % 10000)


# ====================================================================================================== the world: 4 real jars, one restart
class World(object):
    def __init__(self, base, parts=("skills", "coins", "bank"), keymap=None, start=True):
        from jpype import JClass, JArray, JImplements, JOverride
        self.base = base
        URL = JClass("java.net.URL")
        jars = [JAR, SK_JAR, CO_JAR, BK_JAR]
        self.L = JClass("java.net.URLClassLoader")(JArray(URL)([JClass("java.io.File")(j).toURI().toURL() for j in jars]),
                                                    JClass("java.lang.ClassLoader").getSystemClassLoader())
        c = lambda n: JClass(n, loader=self.L)
        Sys = JClass("java.lang.System")
        br = Sys.getProperties().get("skyy.bridge")
        if br is None:
            br = JClass("java.util.concurrent.ConcurrentHashMap")()
            Sys.getProperties().put("skyy.bridge", br)
        br.clear()
        self.br = br
        self.keymap = keymap if keymap is not None else {}
        W = self

        @JImplements("java.util.function.Function")
        class Fn(object):
            def __init__(self, f):
                self.f = f

            @JOverride
            def apply(self, o):
                return self.f(o)
        self.Fn = Fn
        P = JClass("java.nio.file.Paths")
        path = lambda p_: P.get(p_, JArray(JClass("java.lang.String"))([]))
        self.path = path
        LOG = JClass("com.hypixel.hytale.logger.HytaleLogger")
        # SkyyRebirth
        R = lambda n: c(RB + n)
        self.Cfg, self.Sto, self.Jr, self.Tx, self.Fnc, self.Mth, self.Chk, self.Adm, self.Page, self.Run, self.Pub = (
            R("RbCfg"), R("RbStore"), R("RbJournal"), R("RbTx"), R("RbFn"), R("RbMath"), R("RbCheck"), R("RbAdmin"), R("RbPage"), R("RbRun"), R("RbPub"))
        self.Cfg.LOG = LOG.get("SkyyRebirth")
        rbh = os.path.join(base, "Skyy_SkyyRebirth")
        self.Cfg.DIR = path(rbh)
        self.Cfg.FILE = path(os.path.join(rbh, "config.properties"))
        self.Cfg.loadCfg(True)
        self.Sto.DIR = path(os.path.join(rbh, "players"))
        self.Jr.DIR = path(os.path.join(rbh, "journal"))
        for i, nm in enumerate(("count", "cap", "node", "dustmult", "busy", "decision")):
            br.put("rebirth:fn:" + nm, self.Fnc(i))
        self.told = JClass("java.util.ArrayList")()
        self.Tx.TEST_TOLD = self.told
        # SkyySkills
        S = lambda n: c("com.skyy.skills." + n)
        self.SCfg, self.SSto, self.SDefs, self.SRb, self.SRun = S("SkillCfg"), S("SkillStore"), S("SkillDefs"), S("SkillRb"), S("SkillRunFn")
        self.SCfg.LOG = LOG.get("SkyySkills")
        skh = os.path.join(base, "Skyy_SkyySkills")
        os.makedirs(os.path.join(skh, "players"), exist_ok=True)
        self.SCfg.FILE = path(os.path.join(skh, "xp.properties"))
        self.SCfg.load()
        self.SSto.DIR = path(os.path.join(skh, "players"))
        br.put("skill:fn:run", self.SRun())
        if "skills" in parts:
            br.put("rebirth:part:skills", self.SRb())
        # SkyyCoins
        Co = lambda n: c("com.skyy.coins." + n)
        self.CS, self.CRb, self.CFn = Co("CoinStore"), Co("CoinRb"), Co("CoinFn")
        coh = os.path.join(base, "Skyy_SkyyCoins")
        os.makedirs(os.path.join(coh, "balances"), exist_ok=True)
        self.CS.DIR = path(os.path.join(coh, "balances"))
        self.CS.JOURNAL = path(os.path.join(coh, "balances-journal.properties"))
        self.CS.recover()
        for m_ in ("get", "add", "take", "flush"):
            br.put("coins:fn:" + m_, self.CFn(m_))
        if "coins" in parts:
            br.put("rebirth:part:coins", self.CRb())
        # SkyyBank
        Bk = lambda n: c("com.skyy.bank." + n)
        self.BS, self.BC, self.BRb = Bk("BankStore"), Bk("BankConfig"), Bk("BankRb")
        bkh = os.path.join(base, "Skyy_SkyyBank")
        os.makedirs(os.path.join(bkh, "accounts"), exist_ok=True)
        self.BS.DIR = path(os.path.join(bkh, "accounts"))
        self.BC.FILE = path(os.path.join(bkh, "config.properties"))
        self.BC.STATE = path(os.path.join(bkh, "state.properties"))
        self.BC.load()
        if "bank" in parts:
            br.put("rebirth:part:bank", self.BRb())
        br.put("profile:fn:key", Fn(lambda o: W.keymap.get(str(o), str(o))))
        self.open = int(self.Tx.startup()) if start else 0

    def uuid(self, s):
        from jpype import JClass
        return JClass("java.util.UUID").fromString(s)

    def files(self, k):
        b = self.base
        return {"skills": os.path.join(b, "Skyy_SkyySkills", "players", k + ".properties"),
                "coins": os.path.join(b, "Skyy_SkyyCoins", "balances", k + ".properties"),
                "bank": os.path.join(b, "Skyy_SkyyBank", "accounts", k + ".properties"),
                "rebirth": os.path.join(b, "Skyy_SkyyRebirth", "players", k + ".properties")}

    def staged(self):
        out = []
        for m_ in ("Skyy_SkyySkills", "Skyy_SkyyCoins", "Skyy_SkyyBank"):
            d = os.path.join(self.base, m_, "rebirth")
            if os.path.isdir(d):
                out += [m_ + "/" + f for f in os.listdir(d)]
        return out

    def journals(self):
        d = os.path.join(self.base, "Skyy_SkyyRebirth", "journal")
        op = [f for f in os.listdir(d) if f.endswith(".journal")] if os.path.isdir(d) else []
        dn = sorted(os.listdir(os.path.join(d, "done"))) if os.path.isdir(os.path.join(d, "done")) else []
        return op, dn


def seed(base, k, cls_total, extra_skills=None, purse=None, bank=None):
    sk = dict(SEED)
    sk.pop("purse")
    sk.pop("bank")
    sk["Combat.Archer"] = cls_total
    if extra_skills:
        sk.update(extra_skills)
    d = os.path.join(base, "Skyy_SkyySkills", "players")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, k + ".properties"), "w", encoding="latin-1").write("name=Tester\n" + "".join("%s=%d\n" % (a, b) for a, b in sorted(sk.items())))
    d = os.path.join(base, "Skyy_SkyyCoins", "balances")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, k + ".properties"), "w").write("#SkyyCoins\nbalance=%d\n" % (SEED["purse"] if purse is None else purse))
    d = os.path.join(base, "Skyy_SkyyBank", "accounts")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, k + ".properties"), "w").write("#SkyyBank\nbalance=%d\n" % (SEED["bank"] if bank is None else bank))


class Checker(object):
    """the expected new / old state of profile k (computed from the REAL SkillDefs of the jar)"""

    def __init__(self, K, W0):
        self.K = K
        D = W0.SDefs
        self.arch = int(D.indexOf("archery"))
        self.amax = int(D.maxOf(self.arch))
        self.cls_total = int(D.cumAt(self.arch, self.amax)) + 1000
        self.names = [str(x) for x in D.NAMES]
        self.N = int(D.N)
        self.EXP = int(D.EXPLORATION)
        self.tocap = {}
        for arm, nm in (("class", None), ("foraging", "Foraging"), ("mining", "Mining"), ("smithing", "Smithing"), ("alchemy", "Alchemy"),
                        ("farming", "Farming"), ("fishing", None), ("cooking", "Cooking")):
            s = self.arch if arm == "class" else (int(D.indexOf(nm)) if nm else -1)
            self.tocap[arm] = (s, int(D.cumAt(s, int(D.maxOf(s)))) if s >= 0 else 0)
        B_ = {"class": 12}
        self.points = {}
        arms = ["Class", "Foraging", "Mining", "Smithing", "Alchemy", "Farming", "Fishing", "Cooking"]
        runs = {"class": self.cls_total, "foraging": SEED["Foraging"], "mining": SEED["Mining"], "farming": SEED["Farming"]}
        for nm in arms:
            a = nm.lower()
            s, tc = self.tocap[a]
            self.points[nm] = pts(runs.get(a, 0), tc, B_.get(a, 8)) if s >= 0 else 0

    def old(self, W, k, hashes, what):
        K = self.K
        f = W.files(k)
        K.check(all(sha(f[m_]) == hashes[m_] for m_ in ("skills", "coins", "bank")), "%s: OLD state - skills / purse / bank files byte-identical" % what)
        rp = props(f["rebirth"])
        K.check(rp is None or int(rp.get("n", "0")) == 0, "%s: OLD state - still 0 rebirths" % what)
        K.check(not W.staged(), "%s: OLD state - no staged file left: %s" % (what, W.staged()))
        op, _dn = W.journals()
        K.check(not op and not W.Sto.BUSY.containsKey(k), "%s: no journal open, not busy" % what)

    def new(self, W, k, what, n=1, purse=0, bank=0, mining=0, bonus=None, hist=None, expl=None):
        K = self.K
        f = W.files(k)
        sp, cp, bp, rp = props(f["skills"]), props(f["coins"]), props(f["bank"]), props(f["rebirth"])
        tx = rp.get("lastTx") if rp else None
        K.check(rp is not None and int(rp.get("n", "0")) == n and tx and rp.get("title") == "Void-Touched " + ["I", "II", "III"][n - 1],
                "%s: NEW state - rebirth n %d, title, lastTx: %s" % (what, n, rp))
        reset = dict((self.names[s], 0) for s in range(self.N) if s != self.EXP)
        reset["Mining"] = mining
        bad = [(a, sp.get(a)) for a, v in reset.items() if int(sp.get(a, "0")) != v]
        badp = [a for a in reset if int(sp.get(a + ".paid", "0")) > 0 and not (a == "Mining" and mining > 0)]
        K.check(not bad and not badp and int(sp.get("Exploration")) == (SEED["Exploration"] if expl is None else expl) and sp.get("rb.lastTx") == tx,
                "%s: NEW state - every skill but Exploration reset (Mining %d), paid markers 0, Exploration kept, rb.lastTx: %s %s" % (what, mining, bad[:3], badp[:3]))
        K.check(cp == {"balance": str(purse), "rb.lastTx": tx}, "%s: NEW state - purse %d with rb.lastTx: %s" % (what, purse, cp))
        bonus = bonus_ppm(SEED["purse"] + SEED["bank"]) if bonus is None else bonus
        hist = {"rb.hist.1": str(SEED["purse"] + SEED["bank"])} if hist is None else hist
        K.check(bp.get("balance") == str(bank) and bp.get("rb.bonus") == ppm_text(bonus) and bp.get("rb.lastTx") == tx
                and all(bp.get(a) == v for a, v in hist.items()), "%s: NEW state - bank %d, rb.bonus %s, %s: %s" % (what, bank, ppm_text(bonus), hist, bp))
        if n == 1:
            want = dict(("pts." + a, str(p)) for a, p in self.points.items() if p > 0)
            got = dict((a, b) for a, b in rp.items() if a.startswith("pts."))
            K.check(got == want, "%s: NEW state - points = the spec 3.5 curve recomputed here: %s" % (what, got))
        K.check(not W.staged(), "%s: NEW state - no staged file left: %s" % (what, W.staged()))
        op, dn = W.journals()
        K.check(not op and any(d.startswith(k + "." + tx) for d in dn) and not W.Sto.BUSY.containsKey(k), "%s: the journal is in done/, not busy" % what)
        done = open(os.path.join(W.base, "Skyy_SkyyRebirth", "journal", "done", k + "." + tx + ".journal"), encoding="utf8").read()
        K.check(done.rstrip().endswith("DONE") and "DECIDED commit" in done, "%s: the done journal ends DONE" % what)
        return tx


# ====================================================================================================== X: every new path, the crash proofs
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Obj, Str, Integer, Long, Bool = (JClass("java.lang.Object"), JClass("java.lang.String"), JClass("java.lang.Integer"), JClass("java.lang.Long"),
                                     JClass("java.lang.Boolean"))
    OA = lambda *xs: JArray(Obj)(list(xs))
    k = U0
    W0 = World(os.path.join(scratch, "w0"))
    CK = Checker(K, W0)

    def fresh(name, **kw):
        base = os.path.join(scratch, name)
        seed(base, k, CK.cls_total, **kw)
        W = World(base)
        W.br.put("class:" + k, "Archer")
        f = W.files(k)
        return W, base, dict((m_, sha(f[m_])) for m_ in ("skills", "coins", "bank"))

    def restart(base, **kw):
        W = World(base, **kw)
        W.br.put("class:" + k, "Archer")
        return W

    # ---- RbMath + config
    M = W0.Mth
    K.check([int(M.bonusPpm(x)) for x in (0, 1000000, 10000000, 100000000, 1000000000, 10 ** 15)] == [0, 2603, 5011, 7501, 10000, 10000],
            "X bonusPpm: 0 / 1M 0.26 / 10M 0.50 / 100M 0.75 / 1B 1.00 (spec 3.3) / capped at 1: %s" % [int(M.bonusPpm(x)) for x in (0, 1000000, 10000000, 100000000, 1000000000)])
    K.check(int(M.maxPpm()) == 30000 and str(M.pct(5011)) == "0.50" and str(M.pct(0)) == "0.00", "X maxPpm 3 %, pct")
    cfgf = os.path.join(scratch, "w0", "Skyy_SkyyRebirth", "config.properties")
    txt = open(cfgf, encoding="utf8").read()
    K.check("bank.bonusBase=0.25" in txt and "bank.bonusPer=1" in txt and "bank.bonusMax=3" in txt and "rebirth.on=false" in txt, "X the default config has the bank rows, rebirth off")
    open(cfgf, "w", encoding="utf8").write(txt.replace("bank.bonusBase=0.25", "bank.bonusBase=9").replace("bank.bonusMax=3", "bank.bonusMax=x"))
    W0.Cfg.loadCfg(False)
    K.check(float(W0.Cfg.BANK_BASE) == 5.0 and float(W0.Cfg.BANK_MAX) == 3.0 and float(W0.Cfg.BANK_PER) == 1.0, "X bank.* rows clamp / a bad number = default")
    open(cfgf, "w", encoding="utf8").write(txt)
    W0.Cfg.loadCfg(False)
    CP = JClass(RB + "CfgPub", loader=W0.L)
    CP.start(W0.path(os.path.join(scratch, "w0")), W0.Cfg.LOG)
    hdr = W0.br.get("config:def:SkyyRebirth")
    K.check(hdr is not None and len(hdr[7]) == 9 and str(hdr[3]) == VERSION, "X config:def:SkyyRebirth: 9 rows, version %s" % VERSION)
    CP.shutdown()

    # ---- 1. a full rebirth (admin, IO not running = inline)
    W, base, H = fresh("full")
    u = W.uuid(k)
    r = str(W.Tx.adminStart(u, -1))
    K.check(r.startswith("+Rebirth tx") and "started on " + k in r, "X1 adminStart: %s" % r)
    tx = CK.new(W, k, "X1 full rebirth")
    K.check(any("rebirth 1 done" in str(t) for t in W.told), "X1 the player is told: %s" % [str(t) for t in W.told][-1:])
    for m_ in ("Skyy_SkyySkills", "Skyy_SkyyCoins", "Skyy_SkyyBank"):
        K.check(os.path.isdir(os.path.join(base, m_, "rebirth-backup", k, tx)), "X1 %s backed up the profile (rebirth-backup/<pkey>/<txid>)" % m_)
    K.check(int(W.br.get("rebirth:fn:count").apply(k)) == 1 and str(W.br.get("rebirth:fn:decision").apply(tx)) == "commit"
            and str(W.br.get("rebirth:fn:decision").apply("tx1700000000000-000000")) == "unknown" and str(W.br.get("rebirth:fn:decision").apply("../x")) == "unknown",
            "X1 rebirth:fn:count = 1, decision commit / unknown")
    K.check(int(W.br.get("rebirth:fn:cap").apply(OA(k, "Mining", Integer(100)))) == 110, "X1 caps +10 after the rebirth")
    h_after = dict((m_, sha(W.files(k)[m_])) for m_ in ("skills", "coins", "bank", "rebirth"))
    W2 = restart(base)
    K.check(int(W2.Tx.recoverAll(True)) == 0 and dict((m_, sha(W2.files(k)[m_])) for m_ in h_after) == h_after, "X1 a restart after a finished rebirth changes nothing")

    # ---- 2. THE CRASH PROOF: halt after every point, RESTART, recover
    for p in range(8):
        W, base, H = fresh("halt%d" % p)
        u = W.uuid(k)
        r = str(W.Tx.adminStart(u, p))
        K.check(W.Sto.BUSY.containsKey(k) and W.Tx.HALTED.containsKey(k), "H%d: stopped after point %d, the profile busy (%s)" % (p, p, r[:60]))
        K.check(not W.CS.take(u, 1) and int(W.BS.deposit(u, 1)) == 6, "H%d: while busy coins take + bank deposit are refused" % p)
        cnt = int(W.br.get("rebirth:fn:count").apply(k))
        K.check(cnt == (1 if p >= 3 else 0), "FIX2 H%d: rebirth:fn:count = %d while open (the new n from the decision on: level coins never at the old factor)" % (p, cnt))
        W.Tx.recoverAll(False)
        K.check(W.Tx.HALTED.containsKey(k), "H%d: the 30 s retry (recoverAll(false)) leaves a crashtest stop alone" % p)
        W2 = restart(base)
        K.check(W2.open == 1 and W2.Sto.BUSY.containsKey(k), "H%d RESTART: the open journal makes the profile busy at start" % p)
        cnt2 = int(W2.br.get("rebirth:fn:count").apply(k))
        K.check(cnt2 == (1 if p >= 3 else 0), "FIX2 H%d RESTART: rebirth:fn:count = %d before recovery (startup knows a decided commit)" % (p, cnt2))
        W2.Tx.recoverAll(False)
        if p <= 2:
            CK.old(W2, k, H, "H%d (before the decision)" % p)
            _op, dn = W2.journals()
            K.check(any(open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", d), encoding="utf8").read().rstrip().endswith("ABORTED") for d in dn),
                    "H%d: the journal ends ABORTED" % p)
        else:
            CK.new(W2, k, "H%d (after the decision)" % p)
        K.check(not W2.Sto.PEND.containsKey(k) and int(W2.br.get("rebirth:fn:count").apply(k)) == (1 if p >= 3 else 0), "FIX2 H%d: after recovery PEND is clear, the count is the file's" % p)
        snap = tree(base)
        W2.Tx.recoverAll(True)
        W3 = restart(base)
        W3.Tx.recoverAll(True)
        W3.Tx.recoverAll(True)
        K.check(tree(base) == snap, "H%d: recovered twice more + restarted again = no file changes (no double reset / bonus)" % p)

    # ---- 3. a crash INSIDE each participant's write
    for label, setup in (("skills FAIL_SAVE", lambda W: setattr(W.SRb, "FAIL_SAVE", 1)), ("coins FAIL_FLUSH", lambda W: setattr(W.CRb, "FAIL_FLUSH", 1)),
                         ("coins flush stop 1", lambda W: (setattr(W.CS, "STEPS", 0), setattr(W.CS, "STOP_AT", 1))),
                         ("coins flush stop 2", lambda W: (setattr(W.CS, "STEPS", 0), setattr(W.CS, "STOP_AT", 2))),
                         ("coins flush stop 3", lambda W: (setattr(W.CS, "STEPS", 0), setattr(W.CS, "STOP_AT", 3))),
                         ("bank FAIL_WRITE", lambda W: setattr(W.BRb, "FAIL_WRITE", 1))):
        W, base, H = fresh("in_" + label.replace(" ", "_"))
        u = W.uuid(k)
        W.CS.get(u)
        setup(W)
        W.Tx.adminStart(u, -1)
        K.check(W.Sto.BUSY.containsKey(k) and W.Tx.WAIT.containsKey(k), "IN %s: the rebirth waits (%s)" % (label, str(W.Tx.WAIT.get(k))[:90]))
        W2 = restart(base)
        W2.Tx.recoverAll(False)
        CK.new(W2, k, "IN %s + RESTART" % label)

    # ---- 4. a participant jar missing after the decision, then back
    W, base, H = fresh("missing")
    u = W.uuid(k)
    W.Tx.adminStart(u, 3)
    Wm = restart(base, parts=("skills", "coins"))
    Wm.Tx.recoverAll(False)
    K.check(Wm.Sto.BUSY.containsKey(k) and "waiting for SkyyBank 0.1.11+" in str(Wm.Tx.WAIT.get(k)) and sha(Wm.files(k)["bank"]) == H["bank"]
            and props(Wm.files(k)["coins"]).get("balance") == "0" and props(Wm.files(k)["skills"]).get("Mining") == "0",
            "JAR MISSING: skills + coins committed, 'waiting for SkyyBank', busy stays, the bank untouched: %s" % Wm.Tx.WAIT.get(k))
    K.check(not Wm.CS.take(u, 1), "JAR MISSING: spends stay refused while the rebirth waits")
    # fix round: the 30 s retry of a waiting rebirth logs its reason ONCE (again only when it changes)
    JSys = JClass("java.lang.System")
    bos = JClass("java.io.ByteArrayOutputStream")()
    o_out, o_log = JSys.out, Wm.Cfg.LOG
    Wm.Cfg.LOG = None
    JSys.setOut(JClass("java.io.PrintStream")(bos, True))
    try:
        for _i in range(3):
            Wm.Tx.recoverAll(False)
        Wm.Tx.waitOn(k, "a different reason")
        Wm.Tx.waitOn(k, "a different reason")
    finally:
        JSys.setOut(o_out)
        Wm.Cfg.LOG = o_log
    logged = str(bos.toString())
    K.check(logged.count("is waiting") == 1 and "a different reason" in logged,
            "FIX WAIT LOG: 3 more 30 s retries log nothing new, a changed reason logs once: %r" % logged[:300])
    Wm.Tx.WLOG.remove(k)
    Wm.Tx.recoverAll(False)   # the real reason back (waiting for SkyyBank) for the checks below
    st = [str(x) for x in Wm.Tx.status(u)]
    K.check(any("OPEN" in x and "waiting for SkyyBank" in x for x in st) and any("Not loaded: SkyyBank" in x for x in st), "JAR MISSING: /rebirthadmin status says so: %s" % st)
    Wb = restart(base)
    Wb.Tx.recoverAll(False)
    CK.new(Wb, k, "JAR BACK")
    s1 = tree(base)
    Wb.Tx.recoverAll(True)
    K.check(tree(base) == s1, "JAR BACK: recovered again = no double bonus")
    W, base, H = fresh("missing_click")
    Wc = restart(base, parts=("skills", "coins"))
    r = str(Wc.Tx.adminStart(Wc.uuid(k), -1))
    K.check(r.startswith("-Rebirth needs SkyyBank 0.1.11+"), "JAR MISSING at the click: refused (%s)" % r)
    CK.old(Wc, k, H, "JAR MISSING at the click")

    # ---- 5. income during the busy window kept; spends refused (+ the REAL SkyyProfiles 0.1.13 switch check)
    W, base, H = fresh("income")
    u = W.uuid(k)
    W.Tx.adminStart(u, 3)
    W.CS.add(u, 777)
    K.check(bool(W.BS.creditK(k, 1234)), "INCOME: a bank credit lands")
    W.SSto.addK(k, u, "T", int(W.SDefs.MINING), 500)
    now = int(JClass("java.lang.System").currentTimeMillis())
    GS = lambda *gs: JArray(Obj)([JArray(Str)(list(g)) for g in gs])
    pay = int(W.BS.payAll(GS([k]), now - 2 * DAY, now - DAY, DAY, 1)[0][0])
    K.check(pay > 0, "INCOME: an interest payout between prepare and commit (+%d)" % pay)
    K.check(not W.CS.take(u, 1) and not W.CS.transfer(u, W.uuid("00000000-0000-4000-8000-0000000003ff"), 1) and int(W.BS.deposit(u, 1)) == 6
            and int(W.BS.withdraw(u, 1)) == 6, "BUSY: coins take / pay, bank deposit / withdraw refused")
    PL = JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(PF_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getSystemClassLoader())
    PSw = JClass("com.skyy.profiles.ProfSwitch", loader=PL)
    K.check(str(PSw.rebirthBlock(u)).startswith("A rebirth is finishing"), "BUSY: the REAL SkyyProfiles 0.1.13 refuses the switch (with the real rebirth:fn:busy)")
    W.Tx.recoverAll(True)
    CK.new(W, k, "INCOME", purse=777, bank=1234 + pay, mining=500)
    K.check(PSw.rebirthBlock(u) is None, "BUSY over: SkyyProfiles lets the switch through")

    # ---- 6. a profile switch mid-rebirth
    W, base, H = fresh("switch")
    k2 = k + "-p2"
    seed(base, k2, 7, purse=11, bank=22)
    h2 = dict((m_, sha(W.files(k2)[m_])) for m_ in ("skills", "coins", "bank"))
    u = W.uuid(k)
    W.Tx.adminStart(u, 3)
    W.keymap[k] = k2
    K.check(not bool(W.br.get("rebirth:fn:busy").apply(u)), "SWITCH: the new active profile is not busy")
    W.Tx.recoverAll(True)
    CK.new(W, k, "SWITCH: the clicked profile")
    K.check(dict((m_, sha(W.files(k2)[m_])) for m_ in h2) == h2 and props(W.files(k2)["rebirth"]) is None, "SWITCH: the other profile is byte-identical")
    W.keymap.clear()

    # ---- 7. two rebirths in a row + the level coins after it
    W, base, H = fresh("twice")
    u = W.uuid(k)
    W.Tx.adminStart(u, -1)
    tx1 = CK.new(W, k, "TWICE #1")
    W.CS.add(u, 300000)
    r = str(W.Tx.adminStart(u, -1))
    rp = props(W.files(k)["rebirth"])
    b1 = bonus_ppm(SEED["purse"] + SEED["bank"])
    b2 = bonus_ppm(300000)
    CK.new(W, k, "TWICE #2", n=2, bonus=min(b1 + b2, 30000), hist={"rb.hist.1": str(SEED["purse"] + SEED["bank"]), "rb.hist.2": "300000"})
    K.check(rp.get("hist.1") and rp.get("hist.2") and rp.get("pts.Class") == str(CK.points["Class"]) and rp.get("lastTx") != tx1,
            "TWICE: points kept (rebirth 2 adds 0: no run XP), hist.1 + hist.2")
    cm = [int(x) for x in W.SDefs.cumOf(int(W.SDefs.FORAGING))]
    W.SSto.addK(k, u, "T", int(W.SDefs.FORAGING), cm[3])
    before = int(W.CS.get(u))
    W.SSto.payOwedK(k, u, int(W.SDefs.FORAGING))
    per = int(W.SCfg.COINS_PER_LEVEL)
    K.eq(int(W.CS.get(u)) - before, sum(int(math.floor(per * L * 0.81 + 0.5)) for L in (1, 2, 3)), "TWICE: level coins pay again after rebirth 2 at x0.9^2 (Skyy 'a little less each rebirth')")

    # ---- 8. a player (live) rebirth: the decision aborts a class below max; two clicks on the page start a real one
    W, base, H = fresh("live_low", extra_skills={"Combat.Archer": 5})
    u = W.uuid(k)
    r = str(W.Tx.begin(k, u, "live", -1))
    W.Tx.drive(k, True)
    CK.old(W, k, H, "LIVE below max: aborted by the decision")
    _op, dn = W.journals()
    K.check(any("the class is level" in open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", d), encoding="utf8").read() for d in dn),
            "LIVE below max: DECIDED abort names the class level")
    K.check(any("cancelled" in str(t) for t in W.told), "LIVE below max: the player is told it was cancelled")
    W, base, H = fresh("live_ok")
    u = W.uuid(k)
    W.Cfg.HUB_TEST = "hub"
    pg = W.Page(u, "hub")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    W.Cfg.ON = False
    pg.build(None, UCB(), UEB(), None)
    pg.handleDataEvent(None, None, '{"a":"rbgo"}')
    K.check(not pg.goOn and str(pg.last).startswith("-Rebirth is switched off"), "PAGE off: no button (goOn false), a click is refused")
    ev = UEB()
    W.Cfg.ON = True
    pg.build(None, UCB(), ev, None)
    K.check(pg.goOn and len(ev.getEvents()) == 2, "PAGE on + every requirement met: the Rebirth button + its binding (2 bindings)")
    t0 = int(JClass("java.lang.System").currentTimeMillis())
    K.eq(str(pg.click(t0, "hub")), "=armed", "PAGE first press: armed")
    pg.build(None, UCB(), UEB(), None)
    K.eq(str(pg.note), "Resets skills, purse and bank to 0! Press again within 10 s.", "PAGE armed: the note warns what is lost + asks to press again (fix round 2)")
    K.eq(str(pg.click(t0 + 300, "hub")), "=armed", "FIX2 PAGE a second press 0.3 s later (a double-click) is NOT a confirm")
    K.check(int(pg.armedAt) == t0 and not W.Sto.BUSY.containsKey(k) and not W.journals()[0], "FIX2 PAGE the double-click keeps the first arm time, nothing started")
    K.eq(str(pg.click(t0 + 11000, "hub")), "=armed", "PAGE a press after 10 s arms again (no start)")
    pg.armedAt = int(JClass("java.lang.System").currentTimeMillis()) - 2000
    pg.handleDataEvent(None, None, '{"a":"rbgo"}')
    K.check(str(pg.last).startswith("+The void is imprinting your soul"), "PAGE second press within 10 s: started (%s)" % pg.last)
    CK.new(W, k, "PAGE player rebirth")
    # fix round: with SkyyRebirth-IO running the click only hands RbRun mode 4 to IO (no file step on the world thread)
    Wio, base_io, H_io = fresh("live_io")
    uio = Wio.uuid(k)
    Wio.Cfg.HUB_TEST = "hub"
    Wio.Cfg.ON = True
    Wio.Sto.start()
    try:
        pgi = Wio.Page(uio, "hub")
        pgi.build(None, UCB(), UEB(), None)
        t1 = int(JClass("java.lang.System").currentTimeMillis())
        pgi.click(t1, "hub")
        r_io = str(pgi.click(t1 + 1000, "hub"))
        ok_io = PW.wait_until(lambda: not Wio.Sto.BUSY.containsKey(k) and not Wio.journals()[0] and len(Wio.journals()[1]) > 0, 10)
    finally:
        Wio.Sto.stop()
    K.check(r_io.startswith("+The void is imprinting your soul") and ok_io, "FIX PAGE with IO running: handed to SkyyRebirth-IO, the rebirth finishes (%s)" % r_io)
    CK.new(Wio, k, "FIX PAGE via SkyyRebirth-IO")
    Wio.Cfg.ON = False
    gp = PW.calls(jar)
    K.check(RB + "RbTx.begin" not in gp.get("RbTx.playerStart", set()) and RB + "RbRun.<init>" in gp.get("RbTx.playerStart", set())
            and RB + "RbTx.startNow" in gp.get("RbRun.run", set()), "FIX static: playerStart never calls begin itself (RbRun mode 4 on IO; startNow inline only without IO)")
    # mode 4 refused on IO (the max reached after the page's checks): told in chat
    Wr, base_r, H_r = fresh("live_io_refused")
    ur = Wr.uuid(k)
    rbf = os.path.join(base_r, "Skyy_SkyyRebirth", "players")
    os.makedirs(rbf, exist_ok=True)
    open(os.path.join(rbf, k + ".properties"), "w").write("n=10\n")
    Wr.Sto.CACHE.clear()
    Wr.Run(k, 4, ur).run()
    K.check(any("Max rebirths reached" in str(t) for t in Wr.told) and not Wr.Sto.BUSY.containsKey(k), "FIX RbRun mode 4 refused: the player is told, nothing busy")
    pg.build(None, UCB(), UEB(), None)
    K.check(not pg.goOn or int(pg.n) == 1, "PAGE after it: n 1")
    W.Cfg.ON = False

    # ---- 9. a prepare that fails = aborted, every staged file deleted
    W, base, H = fresh("prep_fail")
    u = W.uuid(k)
    cf = W.files(k)["coins"]
    os.remove(cf)
    os.makedirs(cf)
    r = str(W.Tx.adminStart(u, -1))
    _op, dn = W.journals()
    K.check(not W.staged() and not W.Sto.BUSY.containsKey(k) and props(W.files(k)["rebirth"]) is None and sha(W.files(k)["skills"]) == H["skills"]
            and any("coins could not get ready" in open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", d), encoding="utf8").read() for d in dn),
            "PREPARE FAILS (an unreadable purse): aborted, the skills staged file deleted, nothing changed")

    # ---- 10. a torn journal line (a crash mid-append) = never written
    W, base, H = fresh("torn")
    u = W.uuid(k)
    W.Tx.adminStart(u, 4)
    jf = os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal")
    open(jf, "ab").write(b"COMMITTED coi")
    W2 = restart(base)
    W2.Tx.recoverAll(False)
    CK.new(W2, k, "TORN line")

    # ---- 11. startup with an unreadable journal: busy, waits for an admin
    W, base, H = fresh("badjournal")
    os.makedirs(os.path.join(base, "Skyy_SkyyRebirth", "journal"))
    open(os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal"), "w").write("garbage\n")
    W2 = restart(base)
    W2.Tx.recoverAll(True)
    K.check(W2.Sto.BUSY.containsKey(k) and "cannot be read" in str(W2.Tx.WAIT.get(k)) and str(W2.Tx.adminStart(W2.uuid(k), -1)).startswith("-A rebirth is already running"),
            "BAD JOURNAL: the profile stays busy, waits for an admin, no new rebirth")
    CK_old_h = dict(H)
    K.check(all(sha(W2.files(k)[m_]) == CK_old_h[m_] for m_ in ("skills", "coins", "bank")), "BAD JOURNAL: nothing changed")

    # ---- 11b. fix round: a journal with NO complete line (BEGIN never finished: a kill / disk full between creating the file and the
    # line) = nothing started: startup() and recovery remove it and free the profile; a run being born (FRESH) is left alone
    for label, data in (("empty", b""), ("torn BEGIN", ("BEGIN tx1760000000000-abcdef " + k + " 1").encode())):
        W, base, H = fresh("stub_" + label.replace(" ", "_"))
        jd = os.path.join(base, "Skyy_SkyyRebirth", "journal")
        os.makedirs(jd, exist_ok=True)
        jf = os.path.join(jd, k + ".journal")
        open(jf, "wb").write(data)
        W2 = restart(base)
        K.check(not os.path.exists(jf) and not W2.Sto.BUSY.containsKey(k) and int(W2.open) == 0, "FIX STUB %s at startup: removed, not busy" % label)
        CK.old(W2, k, H, "FIX STUB %s at startup" % label)
        open(jf, "wb").write(data)
        W2.Sto.BUSY.put(k, "?")
        W2.Tx.recoverAll(False)
        K.check(not os.path.exists(jf) and not W2.Sto.BUSY.containsKey(k) and not W2.Tx.WAIT.containsKey(k),
                "FIX STUB %s found by the recovery tick: removed, the profile free (no admin needed)" % label)
        r = str(W2.Tx.adminStart(W2.uuid(k), -1))
        K.check(r.startswith("+"), "FIX STUB %s: a new rebirth starts (%s)" % (label, r[:80]))
        CK.new(W2, k, "FIX STUB %s, then a rebirth" % label)
        W2.Tx.FRESH.put(k, "tx1760000000001-abcdef")
        open(jf, "wb").write(data)
        K.check(not W2.Tx.dropStub(k) and os.path.exists(jf), "FIX STUB %s while a run is being born (FRESH): left alone" % label)
        W2.Tx.FRESH.remove(k)
        os.remove(jf)
    gb = PW.calls(jar)
    K.check("java.nio.file.Files.deleteIfExists" in gb.get("RbTx.begin0", set()) and RB + "RbTx.dropStub" in gb.get("RbTx.startup", set())
            and RB + "RbTx.dropStub" in gb.get("RbTx.drive", set()), "FIX static: begin deletes the stub when BEGIN fails; startup + drive drop stubs")

    # ---- 11c. FIX ROUND 2
    # a torn DECIDED commit fragment, then the recovery's abort: the fragment is cut first - never glued into "DECIDED commit ...DECIDED abort"
    W, base, H = fresh("torn_decided")
    u = W.uuid(k)
    W.Tx.adminStart(u, 2)
    jf = os.path.join(base, "Skyy_SkyyRebirth", "journal", k + ".journal")
    txd = open(jf, encoding="utf8").read().split()[1]
    open(jf, "ab").write(b"DECIDED commit pts.cl")
    W2 = restart(base)
    W2.Tx.recoverAll(False)
    CK.old(W2, k, H, "FIX2 TORN DECIDED + abort")
    dj = open(os.path.join(base, "Skyy_SkyyRebirth", "journal", "done", k + "." + txd + ".journal"), encoding="utf8").read()
    K.check("pts.cl" not in dj and "DECIDED commit" not in dj and "\nDECIDED abort " in dj and dj.endswith("ABORTED\n")
            and str(W2.br.get("rebirth:fn:decision").apply(txd)) == "abort", "FIX2 TORN DECIDED: the fragment cut, the journal says abort (decision abort): %r" % dj[-160:])
    # cutTorn on its own: no newline at all -> empty; a clean file untouched
    tf = os.path.join(base, "cut.txt")
    open(tf, "wb").write(b"A\nB\nfrag")
    W2.Jr.cutTorn(JClass("java.io.File")(tf))
    a1 = open(tf, "rb").read()
    W2.Jr.cutTorn(JClass("java.io.File")(tf))
    open(tf + "2", "wb").write(b"frag")
    W2.Jr.cutTorn(JClass("java.io.File")(tf + "2"))
    K.check(a1 == b"A\nB\n" and open(tf, "rb").read() == b"A\nB\n" and open(tf + "2", "rb").read() == b"", "FIX2 cutTorn: tail cut / clean untouched / no newline = empty")
    # level coins inside the commit window (skills committed, our n not written yet) pay at the NEW factor (x0.9 after rebirth 1)
    W, base, H = fresh("gap_coins")
    u = W.uuid(k)
    W.Tx.adminStart(u, 4)
    rp0 = props(W.files(k)["rebirth"])
    K.check((rp0 is None or rp0.get("n", "0") == "0") and W.Sto.PEND.containsKey(k), "FIX2 GAP: our file still says 0 rebirths, PEND holds the decided n")
    cm = [int(x) for x in W.SDefs.cumOf(int(W.SDefs.FORAGING))]
    W.SSto.addK(k, u, "T", int(W.SDefs.FORAGING), cm[3])
    before = int(W.CS.get(u))
    W.SSto.payOwedK(k, u, int(W.SDefs.FORAGING))
    per = int(W.SCfg.COINS_PER_LEVEL)
    K.eq(int(W.CS.get(u)) - before, sum(int(math.floor(per * L * 0.9 + 0.5)) for L in (1, 2, 3)), "FIX2 GAP: level coins in the commit window pay x0.9 (rebirth 1), not x1")
    # a throw inside a run (RbRun 0) -> off FRESH, on the 30 s retry (WAIT), not stuck
    W, base, H = fresh("run_throw")
    W.Tx.FRESH.put(k, "tx1760000000002-abcdef")
    W.Sto.BUSY.put(k, "tx1760000000002-abcdef")
    jd = W.Jr.DIR
    W.Jr.DIR = None
    W.Run(k, 0).run()
    W.Jr.DIR = jd
    K.check(not W.Tx.FRESH.containsKey(k) and "internal error" in str(W.Tx.WAIT.get(k)), "FIX2 RbRun 0 throws: off FRESH, waiting (the 30 s retry takes it): %s" % W.Tx.WAIT.get(k))
    W.Sto.BUSY.remove(k)
    W.Tx.WAIT.remove(k)
    g2 = PW.calls(jar)
    K.check("java.io.FileDescriptor.sync" in g2.get("RbStore.writeNow", set()), "FIX2 static: our profile file is fsync'd before the rename (RbStore.writeNow)")
    K.check(RB + "RbTx.begin0" in g2.get("RbTx.begin", set()) and RB + "RbJournal.cutTorn" in g2.get("RbJournal.append", set()),
            "FIX2 static: begin claims BUSY then calls begin0 (the profile:busy check); append cuts a torn tail first")

    # ---- 12. dry run, admin commands, RbRun, the requirement line
    W, base, H = fresh("admin")
    u = W.uuid(k)
    t_ = tree(base)
    lines = [str(x) for x in W.Tx.dryRun(u)]
    K.check(tree(base) == t_ and lines[0].startswith("+Dry run for " + k) and any(x.startswith("=skills: x.") or x.startswith("=skills: arm.") for x in lines)
            and any(x == "=coins: purse=5000000" for x in lines) and any(x.startswith("=bank: bank=20000000") for x in lines)
            and lines[-1].startswith("+Would commit: pts.Class=%d" % CK.points["Class"]), "ADMIN dryrun: every part measured, the decision shown, NOTHING written: %s" % lines[-1][:120])
    A = W.Adm
    now = 1000000
    K.check(str(A.run(u, "", now)[0]).startswith("=/rebirthadmin status") and str(A.run(u, "help", now)[0]).startswith("=/rebirthadmin"), "ADMIN help")
    K.check(any("rebirths 0 of 10" in str(x) for x in A.run(u, "status", now)), "ADMIN status")
    K.check(str(A.run(u, "crashtest 9", now)[0]).startswith("-Usage") and str(A.run(u, "crashtest x", now)[0]).startswith("-Usage")
            and str(A.run(u, "fly", now)[0]).startswith("-Unknown"), "ADMIN bad arguments")
    K.check(str(A.run(u, "rebirth", now)[0]).startswith("=This rebirth") and str(A.run(u, "crashtest 3", now + 1)[0]).startswith("=This crash test")
            and not W.Sto.BUSY.containsKey(k), "ADMIN rebirth / crashtest ask first (a different command resets the question), nothing started")
    K.check(str(A.run(u, "crashtest 3", now + 20000)[0]).startswith("=This crash test"), "ADMIN the same command after 10 s asks again")
    r = str(A.run(u, "crashtest  3", now + 25000)[0])
    K.check(r.startswith("+Rebirth tx") and "stops after point 3" in r and W.Tx.HALTED.containsKey(k), "ADMIN crashtest 3 confirmed: started, stopped after point 3")
    K.check(any("OPEN" in str(x) and "stopped after point 3" in str(x) for x in A.run(u, "status", now)), "ADMIN status shows the stopped rebirth")
    # RbRun: mode 3 on the real IO thread skips the crashtest stop; mode 2 (recover) takes it
    W.Sto.start()
    W.Run(None, 3).run()
    time.sleep(0.5)
    K.check(W.Tx.HALTED.containsKey(k) and W.Sto.BUSY.containsKey(k), "RUN mode 3 (the 30 s tick) on SkyyRebirth-IO: the crashtest stop is left alone")
    r = str(A.run(u, "recover", now)[0])
    ok = PW.wait_until(lambda: not W.Sto.BUSY.containsKey(k), 10)
    K.check(r.startswith("+Recovery started") and ok, "ADMIN recover (IO running): the rebirth finishes")
    W.Sto.stop()
    CK.new(W, k, "ADMIN crashtest + recover")
    bl = [str(x) for x in A.run(u, "backups", now)]
    K.check(len(bl) == 3 and all(" tx" in x or ": tx" in x for x in bl), "ADMIN backups: the 3 mods list the backup txids: %s" % bl)
    r = str(A.run(u, "recover", now)[0])
    K.check(r.startswith("+Recovered 0"), "ADMIN recover (IO not running): inline, nothing open")
    W.Run(k, 0).run()
    W.Run(None, 1).run()
    W.Run(None, 2).run()
    K.check(not W.Sto.BUSY.containsKey(k), "RUN modes 0-2 with nothing open: no change")
    # the requirement line 1
    W, base, H = fresh("reqs")
    u = W.uuid(k)
    W.Cfg.HUB_TEST = "hub"

    def row0():
        return str(W.Chk.reqs(u, "hub", 0)[0][0])
    W.Cfg.ON = False
    a0 = row0()
    W.Cfg.ON = True
    a1 = row0()
    W.br.remove("rebirth:part:coins")
    a2 = row0()
    W.br.put("rebirth:part:coins", W.CRb())
    W.Sto.BUSY.put(k, "tx")
    a3 = row0()
    W.Sto.BUSY.remove(k)
    W.br.put("profile:busy:" + k, Bool.TRUE)
    a4 = row0()
    K.check([a0, a1, a2, a3, a4] == ["NO  Rebirth is switched off", "OK  Rebirth is switched on", "NO  Needs SkyyCoins 0.1.7+", "NO  A rebirth is finishing",
                                      "NO  A profile switch is running"], "REQ line 1: off / ok / a part missing / busy / a profile switch: %s" % [a0, a1, a2, a3, a4])
    r = str(W.Tx.adminStart(u, -1))
    K.check(r.startswith("-A profile switch is running") and not W.Sto.BUSY.containsKey(k) and not W.journals()[0], "BEGIN refused while a profile switch runs (fix round 2: the early BUSY claim released, no journal)")
    W.br.remove("profile:busy:" + k)
    tip = str(W.Chk.tip(0, W.Chk.reqs(u, "hub", 0), W.Chk.gains(u, 0)))
    K.check("press Rebirth on the left" in tip, "the Nexus tooltip names the button when everything is met")
    W.Cfg.ON = False
    rbf = os.path.join(base, "Skyy_SkyyRebirth", "players")
    os.makedirs(rbf, exist_ok=True)
    os.makedirs(os.path.join(rbf, k + ".properties"))
    W.Sto.BAD.clear()
    K.check(str(W.Tx.adminStart(u, -1)).startswith("-The rebirth file of this profile cannot be read"), "BEGIN refused: an unreadable SkyyRebirth file")
    os.rmdir(os.path.join(rbf, k + ".properties"))
    open(os.path.join(rbf, k + ".properties"), "w").write("n=10\n")
    W.Sto.CACHE.clear()
    K.check(str(W.Tx.adminStart(u, -1)).startswith("-Max rebirths reached (10 of 10)"), "BEGIN refused at the max")
    # the real chat path in a bare JVM: no Universe -> tell() returns quietly; RbTell with no player does nothing
    W.Tx.TEST_TOLD = None
    try:
        W.Tx.tell(k, "x", "#ffffff")
        W.Tx.tell("-", "x", "#ffffff")
        JClass(RB + "RbTell", loader=W.L)(None, "x", "#ffffff").run()
        K.check(True, "tell / RbTell without a server: no exception")
    except Exception as e:
        K.check(False, "tell / RbTell without a server: %s" % e)
    g = PW.calls(jar)
    K.check(RB + "RbTell.<init>" in g.get("RbTx.tell", set()) or any("RbTell" in x for x in g.get("RbTx.tell", set())), "static: tell hands the line to the world thread (RbTell)")
    K.check(any("sendMessage" in x for x in g.get("RbAdmin.send", set())) and any("sendMessage" in x for x in g.get("RbTell.run", set())),
            "static: RbAdmin.send / RbTell.run send chat lines (UNVERIFIED by execution: needs a live player)")
    su, sd = g.get("SkyyRebirthPlugin.setup", set()), g.get("SkyyRebirthPlugin.shutdown", set())
    K.check(RB + "RbTx.startup" in su and any("scheduleAtFixedRate" in x for x in su) and any("registerCommand" in x for x in su), "static: setup scans the journals, schedules the 30 s recovery, registers /rebirthadmin")
    K.check(any("cancel" in x for x in sd), "static: shutdown cancels the tickers")
    K.check(RB + "RbAdmin.run" in g.get("RbAdminArgsCmd.execute", set()) and RB + "RbTx.status" in g.get("RbAdminCmd.execute", set()), "static: the admin commands call RbAdmin / RbTx")
    try:
        ac = JClass(RB + "RbAdminCmd", loader=W.L)()
        K.check(str(ac.getName()) == "rebirthadmin", "/rebirthadmin constructs (admin: skyyrebirth.admin)")
    except Exception as e:
        K.check(False, "/rebirthadmin constructor: %s" % e)
    K.save()


# ====================================================================================================== KK: a real kill
def run_killer(out, jar, scratch, _home):
    """child: 40 back-to-back admin rebirths, killed by the parent at a random moment"""
    HK.jvm([B.SERVER_JAR], verify=False)
    d = HK.arg("--kdir")
    W = World(d)
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(d, "Skyy_SkyyCoins", "balances")) if f.endswith(".properties"))
    open(os.path.join(d, "ready"), "w").write("1")
    for kk in keys:
        W.Tx.adminStart(W.uuid(kk), -1)
    open(os.path.join(d, "finished"), "w").write("1")
    time.sleep(60)


def run_kill(out, jar, scratch, _home):
    K = HK.Child(out)
    env = dict(os.environ)
    for rnd in range(4):
        d = os.path.join(scratch, "kill%d" % rnd)
        for i in range(40):
            kk = "00000000-0000-4000-8000-%012d" % (5000 + i)
            seed(d, kk, 10, purse=1000 + i, bank=50000 + i)
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--phase", "killer", "--out", os.path.join(scratch, "kk.json"), "--dir", scratch,
                              "--jar", jar, "--kdir", d], env=env)
        t0 = time.time()
        while not os.path.exists(os.path.join(d, "ready")) and time.time() - t0 < 120:
            time.sleep(0.02)
        time.sleep(random.Random(rnd).uniform(0.05, 1.2))
        p.kill()
        p.wait()
        K.check(not os.path.exists(os.path.join(d, "finished")), "KK%d: killed mid-run (rc %s)" % (rnd, p.returncode))
    K.save()


def run_killcheck(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    for rnd in range(4):
        d = os.path.join(scratch, "kill%d" % rnd)
        W = World(d)
        n_open = W.open
        W.Tx.recoverAll(True)
        news, olds, bad = 0, 0, []
        for i in range(40):
            kk = "00000000-0000-4000-8000-%012d" % (5000 + i)
            f = W.files(kk)
            sp, cp, bp, rp = props(f["skills"]), props(f["coins"]), props(f["bank"]), props(f["rebirth"])
            n = int(rp.get("n", "0")) if rp else 0
            is_new = (n == 1, cp.get("balance") == "0", bp.get("balance") == "0", sp.get("Mining") == "0", "rb.lastTx" in cp, "rb.bonus" in bp)
            is_old = (n == 0, cp.get("balance") == str(1000 + i), bp.get("balance") == str(50000 + i), sp.get("Mining") == str(SEED["Mining"]),
                      "rb.lastTx" not in cp, "rb.bonus" not in bp)
            if all(is_new) and cp.get("rb.lastTx") == bp.get("rb.lastTx") == sp.get("rb.lastTx") == rp.get("lastTx"):
                news += 1
            elif all(is_old):
                olds += 1
            else:
                bad.append((i, is_new, is_old))
        op, _dn = W.journals()
        K.check(not bad and not op and not W.staged() and W.Sto.BUSY.isEmpty(),
                "KK%d after the kill (%d journal(s) open at start) + recovery: %d profiles all-new, %d all-old, %d half: %s; open %s, staged %s, busy %s, wait %s"
                % (rnd, n_open, news, olds, len(bad), bad[:2], op, W.staged(), W.Sto.BUSY.size(), str(W.Tx.WAIT)))
        K.notes.append("KK%d: %d open journal(s) at restart, %d done, %d not started" % (rnd, n_open, news, olds))
    K.save()


# ====================================================================================================== D: start twice on a live copy
def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    mods = os.path.dirname(home)
    for m_ in ("Skyy_SkyyCoins", "Skyy_SkyyBank"):
        if os.path.isdir(os.path.join(MODS_LIVE, m_)):
            shutil.copytree(os.path.join(MODS_LIVE, m_), os.path.join(mods, m_))
    before = dict((m_, tree(os.path.join(mods, m_))) for m_ in ("Skyy_SkyySkills", "Skyy_SkyyCoins", "Skyy_SkyyBank"))
    W1 = World(mods)
    s1 = tree(mods)
    W2 = World(mods)
    s2 = tree(mods)
    after = dict((m_, tree(os.path.join(mods, m_))) for m_ in before)
    added = sorted(set(s1) - set(tree_flat(before)))
    K.check(W1.open == 0 and W2.open == 0, "D no journal on the live copy")
    K.check(all(a_.startswith("Skyy_SkyyRebirth/") for a_ in added) and "Skyy_SkyyRebirth/config.properties" in added, "D start 1 writes only into Skyy_SkyyRebirth/: %s" % added)
    K.check(after == before, "D the copied Skyy_SkyySkills / Coins / Bank are byte-identical after two starts")
    K.check(s1 == s2, "D start 2 changes nothing")
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(mods, "Skyy_SkyySkills", "players")) if f.endswith(".properties") and len(f) == 47)
    from jpype import JClass, JArray
    Obj = JClass("java.lang.Object")
    n, oks = 0, 0
    for kk in keys:
        for nm in ("skills", "coins", "bank"):
            r = str(W2.br.get("rebirth:part:" + nm).apply(JArray(Obj)(["measure", kk, "tx1760000000001-a1b2c3"])))
            n += 1
            oks += 1 if r.startswith("ok:") else 0
    K.check(n > 0 and oks == n and tree(mods) == s2, "D every live profile-1 key (%d) measured by every part: all ok, nothing written" % len(keys))
    K.save()


def tree_flat(per_mod):
    out = {}
    for m_, t in per_mod.items():
        for a, b in t.items():
            out[m_ + "/" + a] = b
    return out


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") == "killer":
        run_killer(None, JAR, SCRATCH, None)
        sys.exit(0)
    for j_ in (SK_JAR, CO_JAR, BK_JAR, PF_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("kill", run_kill), ("killcheck", run_killcheck), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyySkills"))
