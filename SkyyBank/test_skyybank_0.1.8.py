"""SkyyBank 0.1.8 - bare-JVM harness for THE HYTALE 0.7.0 PORT + BACK-PAY = ONE PAYOUT (tools/bank_0_1_8_patch.py). Child JVM: the game's
own JRE, the 0.7.0 HytaleServer.jar, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The live
Skyy_SkyyBank folder is only READ (copied into scratch) and checked afterwards.

    python SkyyBank/test_skyybank_0.1.8.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyBank-0.1.8.jar] [--prev SkyyBank-0.1.7.jar]

SECTIONS
  CC  CLASS COMPARE 0.1.7 -> 0.1.8: + exactly BankMig2; structural changes only BankPage.watchTick (the two renamed engine calls),
      BankConfig.load / describe / <clinit> (the default 1), SkyyBankPlugin.setup (BankMig2.run after BankMig.run); the kit classes
      only their default text / row (constants); everything else identical
  JT  jar entries: 0.1.7's classes + BankMig2, the manifest = 0.1.7's but the version
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7.0 engine
  P   THE PAGE CHECK through the 0.7.0 engine's OWN PageManager: the real /bank page opened (openCustomPage -> build), acknowledged via
      handleLegacyCustomPageEvent; watchTick healthy (the test click arrives, nothing sent), STUCK (clearLegacyCustomPageAcknowledgements
      resets the counter, the answer redraw is sent, the next click works), after a world change (forgotten with the 0.7.0 Dismiss, no
      packet); CONTROL: 0.1.7's watchTick throws NoSuchMethodError on 0.7.0
  M   BankMig2 (the one-time back-pay update) on scratch folders:
        M1 a COPY of the live Skyy_SkyyBank (no catchUpPeriods line): nothing rewritten, no History copy, no change-log line, the marker
        M2 catchUpPeriods=24 (CRLF, the 0.1.7 default file): only that value -> 1, CRLF kept, every other byte the same, the History copy
           = the old bytes first (index.log names the update), ONE change-log line "catchUpPeriods 24 -> 1 ok" (who SkyWynn update 0.1.8,
           the 0.1.7 line format = Undo), the marker; a second run changes no byte
        M3 hand-edited catchUpPeriods=30: kept, an INFO note, the marker, nothing else written
        M4 "catchUpPeriods = 24  " (spaces, LF): only the 24 -> 1 (spaces, separator, LF kept)
        M5 two entries (5 then 24 - the last wins): only the last line changes; (24 then 5): nothing (the live value is 5)
        M6 a continued entry (catchUpPeriods=2\\ + 4): a hand edit, kept
        M7 no config.properties: the marker only
        M8 config-history blocked (a FILE where the folder goes): nothing rewritten, no marker, a WARNING; unblocked -> the next start
           finishes it
        M9 BankMig (0.1.7's update) + BankMig2 on a 0.1.6-style file: daily + no catchUpPeriods line written (the default 1 applies)
  L   the loader: no line -> CATCH_UP 1; 24 kept by a hand edit after the update -> 24; describe() says "back-pay up to 1 payout"
  S   the sweep with the new default: 3.5 days off -> ONE payout (2% of 100,000 = 2,000) and the clock moves to the last whole day
      (the older days are dropped; nothing paid later); CONTROL 0.1.7 (default 24) on the same files pays 3 compounding days
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyBank (BankMig, BankMig2, BankConfig.load like setup()): the second start
      writes nothing
  AA  python tools/ci/crosscheck.py --jar <0.1.8> --baseline: no FAIL for SkyyBank on 0.7.0, the command tree identical to 0.1.7
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.8", "0.1.7"
PKG = "com.skyy.bank."
DAY = 86400000
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pages07", "bank")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyBank-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyBank")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")     # the shared JVM helpers (read only)
FAILS, OKS = [], [0]
CFG17 = ("# SkyyBank settings (0.1.7). Change them in game: SkyWynn Menu -> Server Setup -> Bank (every change is logged and can be undone),\r\n"
         "# or edit this file while the server is off.\r\ninterestPercent=2\r\nbracket1Coins=1000000\r\nbracket2Percent=1\r\nbracket2Coins=5000000\r\n"
         "bracket3Percent=0.5\r\nmaxPrincipal=10000000\r\nintervalSeconds=86400\r\ncatchUpPeriods=24\r\nscope=account\r\n").encode("ascii")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def sk():
    spec = importlib.util.spec_from_file_location("ts0427", SKILLS_HARNESS)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


def write_acc(home, key, bal, extra=""):
    d = os.path.join(home, "accounts")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, key + ".properties"), "w", encoding="ascii", newline="").write("#SkyyBank\r\nbalance=%s\r\n%s" % (bal, extra))


def acc(home, key):
    for ln in open(os.path.join(home, "accounts", key + ".properties"), encoding="latin-1"):
        if ln.strip().startswith("balance="):
            return int(ln.strip().split("=", 1)[1])
    return None


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString
    import skyybuild as B
    S = sk()
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    try:
        Cls = JClass("java.lang.Class")
        fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        fu.setAccessible(True)
        U = fu.get(None)

        def jf(c, name):
            while c is not None:
                try:
                    f = c.getDeclaredField(name)
                    f.setAccessible(True)
                    return f
                except Exception:
                    c = c.getSuperclass()
            raise KeyError(name)
        HP = JClass("javassist.ClassPool")(False)
        HP.appendSystemPath()
        HP.appendClassPath(B.SERVER_JAR)
        CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

        def hclass(name, sup, ctor, fields=(), meths=()):
            c = HP.makeClass(name, HP.get(sup)) if sup else HP.makeClass(name)
            for s_ in fields:
                c.addField(CtField.make(s_, c))
            if ctor:
                c.addConstructor(CtNewConstructor.make(ctor, c))
            for s_ in meths:
                c.addMethod(CtNewMethod.make(s_, c))
            c.writeFile(hcls)
        PH = "com.hypixel.hytale."
        hclass("skyybank07.Net", PH + "server.core.io.PacketHandler",
               "public Net() { super((" + PH + "protocol.io.ChannelConnection) null, (" + PH + "server.core.io.ProtocolVersion) null); }",
               ["public java.util.ArrayList sent;"],
               ["public void rec(Object p) { if (this.sent == null) this.sent = new java.util.ArrayList(); this.sent.add(p); }",
                "public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { rec(p); return true; }",
                "public void write(" + PH + "protocol.ToClientPacket p) { rec(p); }",
                "public void write(" + PH + "protocol.ToClientPacket[] ps) { for (int i = 0; i < ps.length; i++) rec(ps[i]); }",
                "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { for (int i = 0; i < ps.length; i++) rec(ps[i]); rec(p); }",
                "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { rec(p); }",
                "public void accept(" + PH + "protocol.ToServerPacket p) { }",
                "public String getIdentifier() { return \"skyybank07\"; }"])
        hclass(PH + "component.SkyyBank07Store", PH + "component.Store",
               "public SkyyBank07Store() { super((" + PH + "component.ComponentRegistry) null, 0, (Object) null, (" + PH + "component.IResourceStorage) null); }",
               ["public java.util.IdentityHashMap comps;"],
               ["public " + PH + "component.Component getComponent(" + PH + "component.Ref r, " + PH + "component.ComponentType t) {\n"
                "  if (this.comps == null) return null;\n  java.util.Map m = (java.util.Map) this.comps.get(r);\n"
                "  return m == null ? null : (" + PH + "component.Component) m.get(t);\n}"])
        hclass("skyybank07.World", PH + "server.core.universe.world.World",
               "public World() { super((String) null, (java.nio.file.Path) null, (" + PH + "server.core.universe.world.WorldConfig) null); }", [],
               ["public void execute(java.lang.Runnable r) { }"])
        UUID, Paths, ArrayList, IdMap = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"), JClass("java.util.IdentityHashMap")
        System = JClass("java.lang.System")
        PMc = JClass(PH + "server.core.entity.entities.player.pages.PageManager")
        WMc = JClass(PH + "server.core.entity.entities.player.windows.WindowManager")
        UniC = JClass(PH + "server.core.universe.Universe")
        EMc = JClass(PH + "server.core.modules.entity.EntityModule")
        ESc = JClass(PH + "server.core.universe.world.storage.EntityStore")
        STc, CTc, REFc = JClass(PH + "component.Store"), JClass(PH + "component.ComponentType"), JClass(PH + "component.Ref")
        PLAc, PR = JClass(PH + "server.core.entity.entities.Player"), JClass(PH + "server.core.universe.PlayerRef")
        CPE = JClass(PH + "protocol.packets.interface_.CustomPageEvent")
        CPT = JClass(PH + "protocol.packets.interface_.CustomPageEventType")
        nxt = [800]

        def ctype():
            c = CTc()
            nxt[0] += 1
            jf(CTc.class_, "index").setInt(c, nxt[0])
            jf(CTc.class_, "hashCode").setInt(c, nxt[0])
            return c
        CT_PR, CT_PLA = ctype(), ctype()
        uni = U.allocateInstance(UniC.class_)
        jf(UniC.class_, "playerRefComponentType").set(uni, CT_PR)
        WORLDS = JClass("java.util.concurrent.ConcurrentHashMap")()
        jf(UniC.class_, "worldsByUuid").set(uni, WORLDS)
        jf(UniC.class_, "players").set(uni, ArrayList())
        jf(UniC.class_, "instance").set(None, uni)
        em = U.allocateInstance(EMc.class_)
        jf(EMc.class_, "playerComponentType").set(em, CT_PLA)
        jf(EMc.class_, "instance").set(None, em)
        W1, W2 = U.allocateInstance(JClass("skyybank07.World").class_), U.allocateInstance(JClass("skyybank07.World").class_)
        W1U = UUID.randomUUID()
        WORLDS.put(W1U, W1)
        BR = JClass("java.util.concurrent.ConcurrentHashMap")()
        System.getProperties().put("skyy.bridge", BR)
        HLB, HL = JClass(PH + "logger.backend.HytaleLoggerBackend"), JClass(PH + "logger.HytaleLogger")
        RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
        HLB.subscribe(RECS)

        def logs():
            out_ = []
            for i in range(int(RECS.size())):
                r = RECS.get(i)
                try:
                    out_.append("%s %s" % (r.getLevel(), r.getMessage()))
                except Exception:
                    out_.append(str(r))
            return out_

        def jc(k, name):
            return JClass(PKG + name, loader=L[k])
        for k in ("new", "prev"):
            jc(k, "BankStore").LOG = HL.get("SkyyBankHarness" + k)
            jc(k, "BankWatch").STOP = True
        E = {}

        def home_of(tag):
            h = os.path.join(SCRATCH, "m", tag, "mods", "Skyy_SkyyBank")
            if os.path.isdir(h):
                shutil.rmtree(h)
            os.makedirs(os.path.join(h, "accounts"))
            return h

        def point(k, home):
            BS, BC = jc(k, "BankStore"), jc(k, "BankConfig")
            BS.DIR = Paths.get(os.path.join(home, "accounts"))
            BC.FILE = Paths.get(os.path.join(home, "config.properties"))
            BC.STATE = Paths.get(os.path.join(home, "state.properties"))
            for mp in (BS.BAL, BS.LOADED, BS.PAID, BS.GAIN, BS.EPOCH):
                mp.clear()
            CR, CH, CL = jc(k, "CfgRows"), jc(k, "CfgHist"), jc(k, "CfgLog")
            CR.HOME = None
            CH.DIR = None
            CL.FILE = None
        # ================================================================================ P: the page check
        home = home_of("page")
        write_acc(home, SKYY, 123456)
        point("new", home)
        point("prev", home)

        class Pl:
            pass

        def player():
            P = Pl()
            P.pr = U.allocateInstance(PR.class_)
            jf(PR.class_, "uuid").set(P.pr, UUID.fromString(SKYY))
            jf(PR.class_, "username").set(P.pr, "SkyyHarness")
            P.net = U.allocateInstance(JClass("skyybank07.Net").class_)
            jf(PR.class_, "packetHandler").set(P.pr, P.net)
            jf(PR.class_, "worldUuid").set(P.pr, W1U)
            P.pl = U.allocateInstance(PLAc.class_)
            P.wm = WMc()
            P.wm.init(P.pr)
            P.pm = PMc()
            P.pm.init(P.pr, P.wm)
            jf(PLAc.class_, "windowManager").set(P.pl, P.wm)
            jf(PLAc.class_, "pageManager").set(P.pl, P.pm)
            st = U.allocateInstance(JClass(PH + "component.SkyyBank07Store").class_)
            ref = U.allocateInstance(REFc.class_)
            jf(REFc.class_, "store").set(ref, st)
            jf(REFc.class_, "index").setInt(ref, 7)
            comps = IdMap()
            comps.put(CT_PR, P.pr)
            comps.put(CT_PLA, P.pl)
            allc = IdMap()
            allc.put(ref, comps)
            st.comps = allc
            es = U.allocateInstance(ESc.class_)
            jf(ESc.class_, "world").set(es, W1)
            jf(STc.class_, "externalData").set(st, es)
            P.ref, P.st = ref, st
            jf(PR.class_, "entity").set(P.pr, P.ref)
            P.seen = 0
            return P

        def sent(P):
            return [] if P.net.sent is None else [P.net.sent.get(i) for i in range(int(P.net.sent.size()))]

        def kinds(P, frm=0):
            return [str(p.getClass().getSimpleName()) for p in sent(P)[frm:]]

        def acks(P):
            return int(jf(PMc.class_, "customPageRequiredAcknowledgments").get(P.pm).get())

        def pump(P):
            for p in sent(P)[P.seen:]:
                if str(p.getClass().getSimpleName()) in ("CustomPage", "SetPage"):
                    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, CPE(CPT.Acknowledge, None))
            P.seen = len(sent(P))

        def page(k):
            P = player()
            pg = jc(k, "BankPage")(P.pr)
            P.pm.openCustomPage(P.ref, P.st, pg)
            pump(P)
            pg.world = W1
            return pg, P
        jc("new", "BankConfig").LAST = int(System.currentTimeMillis())
        pg, P = page("new")
        E["p1"] = [P.pm.getCustomPage() == pg, acks(P), kinds(P)]
        n0 = len(sent(P))
        pg.lastSend = 0
        E["p2"] = [bool(pg.watchTick(W1)), bool(pg.probeSeen), int(pg.heals), len(sent(P)) - n0]
        jf(PMc.class_, "customPageRequiredAcknowledgments").get(P.pm).set(1)
        n1 = len(sent(P))
        pg.lastSend = 0
        r3 = bool(pg.watchTick(W1))
        k3, a3, inf3 = kinds(P, n1), acks(P), str(pg.info)
        pump(P)
        pg.lastSend = 0
        E["p3"] = [r3, int(pg.heals), k3, a3, inf3, acks(P), bool(pg.watchTick(W1)), bool(pg.probeSeen)]
        pg5, P5 = page("new")
        n5 = len(sent(P5))
        E["p5"] = [bool(pg5.watchTick(W2)), P5.pm.getCustomPage() is None, len(sent(P5)) - n5, bool(pg5.dismissed)]
        pgo, Po = page("prev")
        pgo.lastSend = 0
        try:
            pgo.watchTick(W1)
            E["p6"] = "no error"
        except Exception as e_:
            E["p6"] = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        # ================================================================================ M: BankMig2
        BM, BM2 = jc("new", "BankMig"), jc("new", "BankMig2")

        def mig(home):
            point("new", home)
            RECS.clear()
            r1 = str(BM.run(Paths.get(home)))
            r2 = str(BM2.run(Paths.get(home)))
            return r1, r2, logs()

        def cfgb(home):
            p = os.path.join(home, "config.properties")
            return open(p, "rb").read() if os.path.exists(p) else None

        def hist(home):
            d = os.path.join(home, "config-history")
            if not os.path.isdir(d):
                return []
            return sorted((f, open(os.path.join(d, f), "rb").read()) for f in os.listdir(d) if f.endswith(".bak"))

        def chlog(home):
            p = os.path.join(home, "config-changes.log")
            return open(p, encoding="utf8").read().splitlines() if os.path.exists(p) else []
        MK = "migrations/bank-backpay-1.done"
        # M1 live copy
        h1 = os.path.join(SCRATCH, "m", "live", "mods", "Skyy_SkyyBank")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, h1)
        else:
            os.makedirs(os.path.join(h1, "accounts"))
        b1 = snap(h1)
        r = mig(h1)
        a1 = snap(h1)
        E["m1"] = {"had_line": b"catchUpPeriods" in (b1.get("config.properties") or b""), "changed": sorted(k for k in set(b1) | set(a1) if b1.get(k) != a1.get(k)),
                   "r": r[1], "live": os.path.isdir(LIVE)}
        # M2 the 0.1.7 default file
        h2 = home_of("def17")
        open(os.path.join(h2, "config.properties"), "wb").write(CFG17)
        open(os.path.join(h2, "state.properties"), "wb").write(b"lastInterestMillis=%d\r\n" % (int(System.currentTimeMillis()) - 1000))
        os.makedirs(os.path.join(h2, "migrations"))
        open(os.path.join(h2, "migrations", "bank-daily-1.done"), "wb").write(b"x\n")
        r = mig(h2)
        s2a = snap(h2)
        r_again = mig(h2)
        E["m2"] = {"cfg": cfgb(h2).decode("ascii"), "want": CFG17.replace(b"catchUpPeriods=24\r\n", b"catchUpPeriods=1\r\n").decode("ascii"),
                   "hist": [(f, b.decode("ascii")) for f, b in hist(h2)], "old": CFG17.decode("ascii"),
                   "index": open(os.path.join(h2, "config-history", "index.log"), encoding="utf8").read() if os.path.exists(os.path.join(h2, "config-history", "index.log")) else "",
                   "log": chlog(h2), "marker": os.path.exists(os.path.join(h2, MK)), "r": r[1],
                   "logs": [x for x in r[2] if "SkyyBank" in x or "back-pay" in x], "again": [r_again[1], snap(h2) == s2a]}
        # M3 hand-edited 30
        h3 = home_of("hand30")
        c3 = CFG17.replace(b"catchUpPeriods=24", b"catchUpPeriods=30")
        open(os.path.join(h3, "config.properties"), "wb").write(c3)
        r = mig(h3)
        E["m3"] = [cfgb(h3) == c3, hist(h3), chlog(h3), os.path.exists(os.path.join(h3, MK)), r[1]]
        # M4 spaces + LF
        h4 = home_of("spaces")
        c4 = b"# hand made\ninterestPercent=2\ncatchUpPeriods = 24  \nscope=account\n"
        open(os.path.join(h4, "config.properties"), "wb").write(c4)
        mig(h4)
        E["m4"] = [cfgb(h4).decode("ascii"), chlog(h4)[-1:] if chlog(h4) else []]
        # M5 two entries
        h5 = home_of("two")
        c5 = b"catchUpPeriods=5\r\ninterestPercent=2\r\ncatchUpPeriods=24\r\n"
        open(os.path.join(h5, "config.properties"), "wb").write(c5)
        mig(h5)
        h5b = home_of("twob")
        c5b = b"catchUpPeriods=24\r\ninterestPercent=2\r\ncatchUpPeriods=5\r\n"
        open(os.path.join(h5b, "config.properties"), "wb").write(c5b)
        mig(h5b)
        E["m5"] = [cfgb(h5).decode("ascii"), cfgb(h5b) == c5b, len(chlog(h5)), len(chlog(h5b))]
        # M6 continued entry
        h6 = home_of("cont")
        c6 = b"interestPercent=2\r\ncatchUpPeriods=2\\\r\n    4\r\n"
        open(os.path.join(h6, "config.properties"), "wb").write(c6)
        r = mig(h6)
        E["m6"] = [cfgb(h6) == c6, chlog(h6), os.path.exists(os.path.join(h6, MK))]
        # M7 no config
        h7 = home_of("nocfg")
        r = mig(h7)
        E["m7"] = [cfgb(h7), os.path.exists(os.path.join(h7, MK)), r[1]]
        # M8 blocked history
        h8 = home_of("blocked")
        open(os.path.join(h8, "config.properties"), "wb").write(CFG17)
        os.makedirs(os.path.join(h8, "migrations"))
        open(os.path.join(h8, "migrations", "bank-daily-1.done"), "wb").write(b"x\n")
        open(os.path.join(h8, "state.properties"), "wb").write(b"lastInterestMillis=%d\r\n" % (int(System.currentTimeMillis()) - 1000))
        open(os.path.join(h8, "config-history"), "wb").write(b"not a folder")
        r = mig(h8)
        blocked = [cfgb(h8) == CFG17, os.path.exists(os.path.join(h8, MK)), [x for x in r[2] if "NOT updated" in x][:1]]
        os.remove(os.path.join(h8, "config-history"))
        r = mig(h8)
        E["m8"] = blocked + [cfgb(h8) == CFG17.replace(b"catchUpPeriods=24", b"catchUpPeriods=1"), os.path.exists(os.path.join(h8, MK))]
        # M9 a 0.1.6-style file: both updates
        h9 = home_of("from016")
        c9 = b"#SkyyBank config\r\ninterestPercent=2\r\nintervalMinutes=60\r\nlastInterestMillis=%d\r\nmaxPrincipal=10000000\r\n" % (int(System.currentTimeMillis()) - 3600000)
        open(os.path.join(h9, "config.properties"), "wb").write(c9)
        r = mig(h9)
        E["m9"] = [cfgb(h9).decode("ascii"), os.path.exists(os.path.join(h9, "migrations", "bank-daily-1.done")), os.path.exists(os.path.join(h9, MK)),
                   [x.split("\t")[3:7] for x in chlog(h9)]]
        # ================================================================================ L: the loader
        BC = jc("new", "BankConfig")
        point("new", h9)
        BC.load()
        l1 = [int(BC.CATCH_UP), str(BC.describe())]
        point("new", h3)
        BC.load()
        l2 = int(BC.CATCH_UP)
        point("new", h2)
        BC.load()
        E["l"] = l1 + [l2, int(BC.CATCH_UP)]
        # ================================================================================ S: the sweep with the default
        res = {}
        for k in ("new", "prev"):
            hs = home_of("sweep-" + k)
            write_acc(hs, "00000000-0000-0000-0000-00000000a001", 100000)
            point(k, hs)
            BCk, BTk = jc(k, "BankConfig"), jc(k, "BankTick")
            BCk.load()
            now = int(System.currentTimeMillis())
            last = now - int(3.5 * DAY)
            BCk.LAST = last
            BR.clear()
            BTk.sweep()
            res[k] = [int(BCk.CATCH_UP), acc(hs, "00000000-0000-0000-0000-00000000a001"), int(BCk.LAST) - last]
            BTk.sweep()
            res[k].append(acc(hs, "00000000-0000-0000-0000-00000000a001"))
        E["s"] = res
        # ================================================================================ ST: start twice on a COPY of the live data
        hst = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyBank")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, hst)
        else:
            os.makedirs(os.path.join(hst, "accounts"))
        starts = []
        for n_ in range(2):
            b_ = snap(hst)
            point("new", hst)
            BM.run(Paths.get(hst))
            BM2.run(Paths.get(hst))
            BC.load()
            a_ = snap(hst)
            starts.append(sorted(k for k in set(b_) | set(a_) if b_.get(k) != a_.get(k)))
        E["st"] = [starts, int(BC.CATCH_UP)]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    p1 = E["p1"]
    check(p1[0] and p1[1] == 0 and "CustomPage" in p1[2], "P1: the /bank page opened through the 0.7.0 PageManager, acknowledged: %s" % p1)
    check(E["p2"] == [True, True, 0, 0], "P2: watchTick healthy - the test click arrives through handleLegacyCustomPageEvent, nothing sent: %s" % E["p2"])
    p3 = E["p3"]
    check(p3[0] and p3[1] == 1 and p3[2] == ["CustomPage"] and p3[3] == 1 and "holding back" in p3[4] and p3[5] == 0 and p3[6] and p3[7],
          "P3: STUCK - clearLegacyCustomPageAcknowledgements reset, the answer redraw sent, the next test click works: %s" % p3)
    check(E["p5"] == [False, True, 0, True], "P5: after a world change the page is forgotten with the 0.7.0 Dismiss (onDismiss), no packet: %s" % E["p5"])
    check(E["p6"] == "java.lang.NoSuchMethodError", "P6: CONTROL - 0.1.7's watchTick throws on 0.7.0: %s" % E["p6"])
    m1 = E["m1"]
    check(not m1["had_line"] and m1["changed"] == ["migrations/bank-backpay-1.done"] and "nothing to change" in m1["r"],
          "M1: the live copy has no catchUpPeriods line -> nothing rewritten, only the marker (the default 1 applies): %s" % m1)
    m2 = E["m2"]
    check(m2["cfg"] == m2["want"], "M2: only catchUpPeriods=24 -> 1, CRLF and every other byte kept")
    check(len(m2["hist"]) == 1 and m2["hist"][0][1] == m2["old"] and "before the 0.1.8 back-pay update" in m2["index"],
          "M2: ONE History copy = the old bytes, index.log names the update: %s" % [f for f, _b in m2["hist"]])
    check(len(m2["log"]) == 1 and m2["log"][0].split("\t")[1:] == ["SkyWynn update 0.1.8", "-", "update", "catchUpPeriods", "24", "1", "ok"],
          "M2: ONE change-log line in the 0.1.7 Undo format: %s" % m2["log"])
    check(m2["marker"] and "catchUpPeriods 24 -> 1" in m2["r"] and m2["again"] == ["", True], "M2: the marker, the INFO line; a second run changes "
          "no byte: %s" % [m2["r"][:90], m2["again"]])
    m3 = E["m3"]
    check(m3[0] and not m3[1] and not m3[2] and m3[3] and "kept hand-edited catchUpPeriods=30" in m3[4], "M3: hand-edited 30 kept + noted, nothing else "
          "written but the marker: %s" % m3[4][:160])
    check(E["m4"][0] == "# hand made\ninterestPercent=2\ncatchUpPeriods = 1  \nscope=account\n" and len(E["m4"][1]) == 1,
          "M4: spaces + LF kept, only 24 -> 1: %r" % E["m4"][0])
    check(E["m5"] == ["catchUpPeriods=5\r\ninterestPercent=2\r\ncatchUpPeriods=1\r\n", True, 1, 0],
          "M5: two entries - only the live (last) one changes; 24 then 5 = nothing: %s" % E["m5"])
    check(E["m6"][0] and not E["m6"][1] and E["m6"][2], "M6: a continued entry = a hand edit, kept: %s" % E["m6"])
    check(E["m7"][0] is None and E["m7"][1] and "no config.properties" in E["m7"][2], "M7: no config.properties - the marker only: %s" % E["m7"])
    check(E["m8"][:2] == [True, False] and E["m8"][2] and E["m8"][3:] == [True, True],
          "M8: config-history blocked -> nothing rewritten, no marker, a WARNING; the next start finishes it: %s" % E["m8"])
    m9 = E["m9"]
    check("intervalSeconds=86400" in m9[0] and "catchUpPeriods" not in m9[0] and m9[1] and m9[2] and m9[3] == [["update", "intervalSeconds", "3600", "86400"]],
          "M9: a 0.1.6 file: 0.1.7's update runs, BankMig2 writes no line (the default 1 applies): %s" % m9)
    check(E["l"][0] == 1 and "back-pay up to 1 payout" in E["l"][1] and "payouts" not in E["l"][1].split("back-pay up to 1")[1] and E["l"][2] == 30 and E["l"][3] == 1,
          "L: the loader - no line -> 1, describe 'back-pay up to 1 payout', a hand-edited 30 -> 30, the updated file -> 1: %s" % E["l"])
    s = E["s"]
    check(s["new"] == [1, 102000, 3 * DAY, 102000], "S: 3.5 days off -> ONE payout (100,000 + 2%% = 102,000), the clock moves 3 whole days (older "
          "days dropped), a second sweep pays nothing: %s" % s["new"])
    check(s["prev"][0] == 24 and s["prev"][1] == 106120 and s["prev"][2] == 3 * DAY, "S: CONTROL 0.1.7 (default 24) pays 3 compounding days "
          "(106,120): %s" % s["prev"])
    st = E["st"]
    check(st[0][1] == [] and all(k_ in ("migrations/bank-backpay-1.done",) for k_ in st[0][0]) and st[1] == 1,
          "ST: two starts on a COPY of the live Skyy_SkyyBank - the first writes only the marker, the second nothing, back-pay limit 1: %s" % st)


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)
    try:
        # ---- CC
        rules = []
        kid = [re.search(rb"skyyui \d+\.\d+ [0-9a-f]{12}", zipfile.ZipFile(j_).read("com/skyy/bank/SkyyBankPlugin.class")) for j_ in (JAR, PREV_JAR)]
        if kid[0] and kid[1]:
            rules.append([re.escape(kid[0].group(0).decode()), kid[1].group(0).decode()])
        out_cc = os.path.join(SCRATCH, "cc.json")
        with open(out_cc + ".log", "wb") as lf:
            subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import importlib.util as u; "
                            "s = u.spec_from_file_location('ts', %r); m = u.module_from_spec(s); sys.argv = ['x', '--dir', %r]; "
                            "s.loader.exec_module(m); m.SCRATCH = %r; m.run_cc(%r, %r, %r, %r)" % (
                                TOOLS, SKILLS_HARNESS, SCRATCH, SCRATCH, JAR, PREV_JAR, out_cc,
                                json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules}))],
                           env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        cc = json.load(open(out_cc)) if os.path.isfile(out_cc) else None
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(cc["added"] == ["BankMig2"] and cc["gone"] == [], "CC: + exactly BankMig2, none gone: %s %s" % (cc["added"], cc["gone"]))
            check(not [c for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]] and all(v["same_shape"] for v in cls_.values()),
                  "CC: no field added / removed, same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else "") for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.1.7 -> 0.1.8 structural %s; constants only %s" % (struct, const))
            allowed = {"BankPage": {"watchTick"}, "BankConfig": {"<clinit>", "load", "describe"}, "SkyyBankPlugin": {"setup"}}
            check(struct.get("BankPage") == ["watchTick"] and struct.get("SkyyBankPlugin") == ["setup"]
                  and set(struct.get("BankConfig", [])) <= allowed["BankConfig"] and "describe" in struct.get("BankConfig", [])
                  and set(struct) <= set(allowed) | set(c for c in struct if c.startswith("Cfg")),
                  "CC: structural changes = BankPage.watchTick, BankConfig (<clinit> / load / describe: the default 1), SkyyBankPlugin.setup "
                  "(+ the kit's default text): %s" % struct)
            kit_struct = dict((c, m) for c, m in struct.items() if c.startswith("Cfg"))
            check(all(set(m) <= {"<clinit>"} for m in kit_struct.values()), "CC: the config kit classes change only their constant tables: %s" % kit_struct)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(cn - cp_ == {"com/skyy/bank/BankMig2.class"} and not (cp_ - cn), "JT: class files = 0.1.7's + BankMig2: %s %s" % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")), "JT: the same non-class entries")
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.1.7's but the version")
        # ---- A + P + M + L + S + ST
        out_e = os.path.join(SCRATCH, "e.json")
        with open(out_e + ".log", "wb") as lf:
            subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT)
        r = json.load(open(out_e)) if os.path.isfile(out_e) else None
        if r is None:
            print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise on 0.7.0 %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check_e(r["E"])
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyBank " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.1.8: no FAIL for SkyyBank on 0.7.0: %s" % mine[:3])
        check("baseline SkyyBank %s -> %s: command / permission tree identical" % (PREV_VERSION, VERSION) in aa, "AA: the command / permission tree = 0.1.7's")
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyBank folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyBank %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
