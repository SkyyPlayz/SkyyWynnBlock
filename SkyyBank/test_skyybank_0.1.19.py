"""Harness for SkyyBank 0.1.19 (round bankroute: /bank and the Storage > Bank tab open SkyyMenu's Bank view while the old menu is off;
tools/bank_0_1_19_patch.py). Build first: python tools/bank_0_1_19_patch.py && python SkyyBank/build_skyybank_0.1.19.py

    python SkyyBank/test_skyybank_0.1.19.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the pinned SkyyCore jar on its class path (SKYY_HARNESS_CP). OLD jar = the LIVE 0.1.18 (the SET pin).
  A      every class loads + initialises with -Xverify:all
  C      class compare 0.1.18 -> 0.1.19 (exactly: BankActFn + openNew / ROUTED, BankCmd.openPage, BankHubOpen.apply, SkyyBankPlugin.setup)
  S      static: the patch re-runs to identical bytes; no class / command / system added; both doors ask SkyyMenu before the old page; the
         page id unchanged; the ready line names menu:fn:bankview
  X18    the WHOLE 0.1.18 exec phase (bank:fn:view / bank:fn:act: every line, every answer, the races, register / unregister) on the 0.1.19 jar
  ROUTE  BankActFn.openNew: no key / a non-Function = false (no call); bankview alone '+' = true; menu:fn:oldmenu TRUE / null / throwing = false
         (bankview never called); FALSE + '+' = true; '-' / null / a non-String / a throw = false; a null UUID = false.
         BankHubOpen.apply (the Storage > Bank tab) and BankCmd.openPage (/bank) EXECUTED: the route opens the new view and stops (the old
         Vault tab / page never reached); every refusal / missing key / old menu on = the 0.1.18 path (vault:fn:openBank stand-in reached)
  LIVE   the 0.1.18 live phase (start twice on a scratch COPY of the live Skyy_SkyyBank) with 0.1.18 as the reference: nothing written,
         every balance the same
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.19"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyBank-0.1.18.jar"))
GEN = os.path.join(HERE, "build_skyybank_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyybank_0.1.18.py")
PATCH = os.path.join(ROOT, "tools", "bank_0_1_19_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bankroute", "bank")))


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T18 = tmod("test_skyybank_0.1.18.py", "tb0118_for19")
T18.OLD_JAR = OLD_JAR           # the live phase compares with the SET pin 0.1.18
T18.T9.OLD_JAR = OLD_JAR
T9 = T18.T9
LIVE_DIR = T18.LIVE_DIR
EXPECT = {
    "BankActFn": ["+f ROUTED", "+m openNew", "~<clinit>"],   # ROUTED = 0 in the class initialiser
    "BankCmd": ["~m openPage"],
    "BankHubOpen": ["~m apply"],
    "SkyyBankPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyyBank 0.1.19 - build script') and g.count('VERSION = "0.1.19"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "pool.makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    op = g[g.index("public static void openPage({REF} ref, {ST} store, {PR} pr) {{"):]
    op = op[:op.index('}}""", cmd))')]
    K.check(op.index("BankActFn.openNew(pr.getUuid())") < op.index("BankPanelFn.openMerged(pr.getUuid())") < op.index("new {PKG}.BankPage(pr)"),
            "S /bank: SkyyMenu's Bank view first, then the 0.1.18 path (merged Vault tab, the page)")
    ho = g[g.index("hopn.addMethod(CtNewMethod.make(jv(r\"\"\"\npublic Object apply(Object o) {"):]
    ho = ho[:ho.index('}"""), hopn))')]
    K.check(ho.index("BankActFn.openNew((java.util.UUID) o)") < ho.index("BankPanelFn.openMerged((java.util.UUID) o)") < ho.index("new @PKG@.BankPage(pr)"),
            "S the Storage > Bank tab: SkyyMenu's Bank view first, then the 0.1.18 path")
    nw = g[g.index("public static boolean openNew(java.util.UUID u) {"):]
    nw = nw[:nw.index('}""")')]
    K.check('if (!Boolean.FALSE.equals(on)) return false;' in nw and 'if (r instanceof String && ((String) r).startsWith("+"))' in nw
            and nw.index('"menu:fn:oldmenu"') < nw.index("((java.util.function.Function) f).apply(u)"),
            "S openNew: the old menu read first (only FALSE goes on), only a '+' answer counts")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', g)
    data = zipfile.ZipFile(jar).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and m.group(1) == "250c80711aad" and ("page " + m.group(1)).encode() in data, "S the page id = 0.1.17's checked page (BankPage unchanged)")
    K.check(b"menu:fn:bankview" in data and b"bank:fn:view / bank:fn:act" in data, "S the ready line names menu:fn:bankview (and still bank:fn:view / act)")
    K.save()


def run_exec18(out, jar, scratch, home):
    T18.run_exec(out, jar, scratch, home)


def run_route(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T9.World()
    Bool = JClass("java.lang.Boolean")
    home = os.path.join(scratch, "route")
    N = T9.Bank(jar, home)
    N.S.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    N.C.load()
    J = lambda n: JClass(PKG + n, loader=N.L)
    A, HO, CMD = J("BankActFn"), J("BankHubOpen"), J("BankCmd")
    M = {"bv": [], "om": [], "vault": [], "ans": "+The Bank opened in the SkyWynn screen.", "old": Bool.FALSE, "bvthrow": False, "omthrow": False}

    @JImplements("java.util.function.Function")
    class BV:
        @JOverride
        def apply(self, x):
            M["bv"].append(str(x))
            if M["bvthrow"]:
                raise RuntimeError("bankview boom")
            return M["ans"]

    @JImplements("java.util.function.Function")
    class OM:
        @JOverride
        def apply(self, x):
            M["om"].append(str(x))
            if M["omthrow"]:
                raise RuntimeError("oldmenu boom")
            return M["old"]

    @JImplements("java.util.function.Function")
    class Vault:
        @JOverride
        def apply(self, x):
            M["vault"].append(str(x))
            return Bool.TRUE

    def reset():
        for k_ in ("bv", "om", "vault"):
            M[k_] = []

    def setkeys(bv=True, om=True):
        for k_, v_, on_ in (("menu:fn:bankview", BV(), bv), ("menu:fn:oldmenu", OM(), om)):
            if on_:
                W.BR.put(k_, v_)
            else:
                W.BR.remove(k_)
    u = W.u(1)
    us = str(u)
    r0 = int(A.ROUTED)
    # ---------------- openNew
    setkeys(False, False)
    reset()
    K.check(not bool(A.openNew(u)) and not M["bv"] and not M["om"], "ROUTE no SkyyMenu 0.3.79 keys = false (the old way), nothing called")
    W.BR.put("menu:fn:bankview", "not a Function")
    K.check(not bool(A.openNew(u)), "ROUTE a non-Function under menu:fn:bankview = false")
    setkeys(True, False)
    reset()
    K.check(bool(A.openNew(u)) and M["bv"] == [us] and int(A.ROUTED) == r0 + 1, "ROUTE bankview alone (no oldmenu key) answering '+' = true, called once with the UUID")
    setkeys(True, True)
    for old_, what_ in ((Bool.TRUE, "TRUE"), (None, "null"), ("false", "a String 'false'")):
        M["old"] = old_
        reset()
        K.check(not bool(A.openNew(u)) and M["om"] == [us] and not M["bv"], "ROUTE menu:fn:oldmenu %s = false, bankview never called (the old menu stays whole)" % what_)
    M["old"] = Bool.FALSE
    M["omthrow"] = True
    reset()
    K.check(not bool(A.openNew(u)) and not M["bv"], "ROUTE menu:fn:oldmenu throwing = false (logged), bankview never called")
    M["omthrow"] = False
    reset()
    r1 = int(A.ROUTED)
    K.check(bool(A.openNew(u)) and M["om"] == [us] and M["bv"] == [us] and int(A.ROUTED) == r1 + 1, "ROUTE old menu OFF + '+' = true (oldmenu read, then bankview)")
    for ans_, what_ in (("-The old SkyWynn menu is on (Server Setup) - the bank page opens.", "'-' refused"), (None, "null"), ("", "''"),
                        (Bool.TRUE, "a non-String TRUE"), ("=a note", "'='")):
        M["ans"] = ans_
        reset()
        K.check(not bool(A.openNew(u)) and M["bv"] == [us], "ROUTE bankview answering %s = false (the old page opens)" % what_)
    M["ans"] = "+The Bank opened in the SkyWynn screen."
    M["bvthrow"] = True
    reset()
    K.check(not bool(A.openNew(u)) and M["bv"] == [us], "ROUTE bankview throwing = false (logged), no throw out")
    M["bvthrow"] = False
    reset()
    K.check(not bool(A.openNew(None)) and not M["bv"] and not M["om"], "ROUTE a null UUID = false, nothing called")
    # ---------------- BankHubOpen.apply (the Storage > Bank tab) - the old path is observed at its first step: vault:fn:openBank (0.1.15 MERGE)
    W.BR.put("vault:fn:openBank", Vault())
    hub = HO()
    reset()
    K.check(bool(hub.apply(u)) and M["bv"] == [us] and not M["vault"], "HUB old menu OFF: the Bank tab = SkyyMenu's Bank view (TRUE), the old Vault tab / page never reached")
    M["old"] = Bool.TRUE
    reset()
    K.check(bool(hub.apply(u)) and not M["bv"] and M["vault"] == [us], "HUB old menu ON: the Bank tab = the 0.1.18 path (the merged Vault tab), bankview never called")
    M["old"] = Bool.FALSE
    M["ans"] = "-That player is not online."
    reset()
    K.check(bool(hub.apply(u)) and M["bv"] == [us] and M["vault"] == [us], "HUB bankview '-' = the 0.1.18 path")
    M["ans"] = None
    reset()
    K.check(bool(hub.apply(u)) and M["vault"] == [us], "HUB bankview null = the 0.1.18 path")
    M["ans"] = "+The Bank opened in the SkyWynn screen."
    setkeys(False, False)
    reset()
    K.check(bool(hub.apply(u)) and M["vault"] == [us], "HUB no SkyyMenu keys = the 0.1.18 path")
    W.BR.remove("vault:fn:openBank")
    reset()
    K.check(not bool(hub.apply(u)) and not M["bv"], "HUB no keys, no Vault, no Universe player = FALSE (the bar runs /bank) - 0.1.18 exactly")
    setkeys(True, True)
    reset()
    K.check(not bool(hub.apply("not a uuid")) and not M["bv"], "HUB a non-UUID = FALSE, nothing called")
    # ---------------- BankCmd.openPage (/bank with no arguments) on a stand-in PlayerRef (uuid only)
    Ucls = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    Ucls.setAccessible(True)
    U = Ucls.get(None)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PRc.class_)
    fu = [f_ for f_ in PRc.class_.getDeclaredFields() if str(f_.getType().getName()) == "java.util.UUID" and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers())]
    K.check(len(fu) >= 1, "CMD the PlayerRef stand-in has a UUID field")
    fu[0].setAccessible(True)
    fu[0].set(pr, u)
    K.eq(str(pr.getUuid()), us, "CMD the stand-in PlayerRef answers getUuid")
    W.BR.put("vault:fn:openBank", Vault())
    reset()
    CMD.openPage(None, None, pr)
    K.check(M["bv"] == [us] and not M["vault"], "CMD /bank, old menu OFF = SkyyMenu's Bank view, nothing else (the old page path never reached)")
    M["old"] = Bool.TRUE
    reset()
    CMD.openPage(None, None, pr)
    K.check(not M["bv"] and M["vault"] == [us], "CMD /bank, old menu ON = the 0.1.18 path (the merged Vault tab)")
    M["old"] = Bool.FALSE
    M["bvthrow"] = True
    reset()
    CMD.openPage(None, None, pr)
    K.check(M["bv"] == [us] and M["vault"] == [us], "CMD /bank, bankview throwing = the 0.1.18 path (never a dead end)")
    M["bvthrow"] = False
    setkeys(False, False)
    reset()
    CMD.openPage(None, None, pr)
    K.check(not M["bv"] and M["vault"] == [us], "CMD /bank without SkyyMenu 0.3.79 = the 0.1.18 path")
    W.BR.remove("vault:fn:openBank")
    K.notes.append("ROUTE ran: BankActFn.ROUTED = %d" % int(A.ROUTED))
    K.save()


def run_live(out, jar, scratch, home):
    T18.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyBank", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec18", run_exec18), ("route", run_route), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyBank"))
