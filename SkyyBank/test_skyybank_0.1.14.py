"""Harness for SkyyBank 0.1.14 (the SkyyCore pilot; tools/bank_0_1_14_patch.py). Build first: python SkyyCore/build_skyycore_1.0.0.py,
python tools/bank_0_1_14_patch.py && python SkyyBank/build_skyybank_0.1.14.py

    python SkyyBank/test_skyybank_0.1.14.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the SkyyCore jar on its class path (SKYY_HARNESS_CP; tools/harness_kit.py) - the module's classes in their own
loader see Core's, like the engine's dependency bridge. The OLD jar everywhere is the LIVE 0.1.13 (the SET pin) - "same behaviour" is
checked against what runs today.
  A      every class loads + initialises with -Xverify:all (Core on the class path)
  C      class compare 0.1.13 -> 0.1.14: removed = the 7 private kit classes + HubBar, added = CfgData, changed = exactly the members that
         now call SkyyCore (listed in EXPECT); non-class entries: manifest.json + the 59 kit files (gone from the jar)
  KITBYTES  no kit art / asset in the jar; manifest = stable name SkyyBank, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0;
         SkyyCore's jar carries the 59 kit files the page names
  HUB    tools/hub_tab_harness.py on SkyyCore's HubBar (owner SkyyBank): REG / PAGE (the Sky Window hub page) / CLICK / DROP
         (removeAll("SkyyBank") removes only SkyyBank's array) + VIS (bank:fn:unlocked) + Refresh + the page id = BANK_PAGE_CHECKED
  D      two opens of the page on a scratch COPY of the live Skyy_SkyyBank (nothing written)
  SND    test_skyybank_0.1.12.py's sound phase on 0.1.14 (the Server Setup rows + the check= hook read from SkyyBank's kit copy in SkyyCore)
  RB, N  test_skyybank_0.1.11.py's rebirth participant phase / test_skyybank_0.1.10.py's profile-name phase (old = 0.1.13; their
         0.1.9 / 0.1.10 CONTROL checks prove bugs an old jar had, so those become notes)
  X      test_skyybank_0.1.9.py's exec phase, 0.1.13 vs 0.1.14 side by side: 800 random deposit / withdraw / switch / sweep steps = the
         same answers, account files, purses and bank:<uuid>; the lock, snapshot, crash, coins, bridge and publish checks
  LIVE2  test_skyybank_0.1.9.py's live phase: START TWICE on a scratch COPY of the live data with 0.1.13 and 0.1.14 (BankMig, BankMig2,
         BankConfig.load, every account read, a due payout): the same files changed, the same balances, the second start writes nothing
  MIG    the one-time updates THROUGH SkyyCore's kit handle (prepare / histSnapshot / histList / histBak / histDir / logEnqueue /
         logFlush / files / CfgText): five starting folders (a 0.1.6 file with intervalMinutes=60, the 0.1.7 default file with
         catchUpPeriods=24 in CRLF, a hand-edited catchUpPeriods=30, no config.properties, config-history blocked by a FILE) run
         BankMig + BankMig2 on 0.1.13 and on 0.1.14: every written file (config.properties, state.properties, config-history copies +
         index, config-changes.log, markers) is the same (time stamps masked), a second run changes nothing
  KIT    Server Setup parity: 0.1.13's own kit and 0.1.14's kit copy in SkyyCore, each started on a COPY of the live Skyy_SkyyBank:
         the same config:def header (but the version), the same answers to get (every row) / status / keys / versions / log / export, the
         same set results (console) and the same file bytes / history / change-log lines afterwards; /bankconfig's cmdSet the same
  PAGE   page parity: the REAL BankPage (opened through each jar's hub bar) built for a player with an account and one without, and the
         Refresh click: 0.1.13 and 0.1.14 send the SAME UI commands and event bindings (digits masked: the payout countdown)
  AA     engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import perfworld_kit as PW
import soundpass_kit as SK

VERSION = "0.1.14"
PKG = "com.skyy.bank."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyBank-0.1.13.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "core10", "bank")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyBank")
SND = "SFX_Coffer_Goblin_Reward"
DAY = 86400000
KITN = ("CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub")
# every child JVM sees SkyyCore (tools/harness_kit.py jvm)
os.environ["SKYY_HARNESS_CP"] = CORE_JAR


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T9 = tmod("test_skyybank_0.1.9.py", "tb019")
T10 = tmod("test_skyybank_0.1.10.py", "tb0110")
T11 = tmod("test_skyybank_0.1.11.py", "tb0111")
# the carried phases compare against the LIVE 0.1.13 (their own old jars are not built any more)
T9.OLD_JAR = T10.OLD_JAR = T11.OLD_JAR = OLD_JAR
# the 0.1.9 exec phase's COINS check runs the REAL SkyyCoins ledger: the live SET pin (its 0.1.6 jar is not built any more)
T9.COINS_JAR = os.path.join(ROOT, "SkyyCoins", "SkyyCoins-%s.jar" % dict(__import__("deploy_set").SET)["SkyyCoins"])


# =====================================================================================================================  helpers
STAMP_RE = re.compile(r"\d{8}-\d{6}-\d{3}")
TIME_RE = re.compile(r"\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d")
MS_RE = re.compile(r"\b1\d{12}\b")             # epoch milliseconds (the clock, notice times)
HEX_RE = re.compile(r"@[0-9a-f]{4,}\b")


def norm(s):
    return MS_RE.sub("MS", TIME_RE.sub("T", STAMP_RE.sub("S", str(s))))


def tree(d):
    """{relative path (stamps masked): text (time stamps masked)} of every file under d"""
    out = {}
    for base, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(base, f)
            rel = STAMP_RE.sub("S", os.path.relpath(p, d).replace(os.sep, "/"))
            out[rel] = norm(open(p, "rb").read().decode("latin-1"))
    return out


def kit_handle(J):
    """the module's handle on its kit copy inside SkyyCore (J = the module's class lookup)"""
    return J("CfgData").kit()


def kit_class(J, name, core):
    """the module's kit class: its own (old jar) or its copy inside SkyyCore (new jar)"""
    from jpype import JClass
    if not core:
        return J(name)
    return JClass("com.skyy.core.cfg." + name, loader=kit_handle(J).loader())


def pyval(o, vers=()):
    """a Java answer (Object[] / String / Long / null, nested) as plain Python; time stamps and the given version strings masked"""
    if o is None:
        return None
    try:
        if o.getClass().isArray():
            return [pyval(x, vers) for x in o]
    except Exception:
        pass
    s = str(o)
    if s.startswith("SKYY1.") and s.count(".") >= 3:      # an export code: SKYY1.<mod>.<base64url zlib>.<crc> - compare its text
        import base64, zlib
        body = s.split(".")[2]
        try:
            s = "SKYY1 " + zlib.decompress(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))).decode("utf-8")
        except Exception:
            pass
    s = norm(s)
    for v in sorted(vers, key=len, reverse=True):
        s = s.replace(v, "VER")
    return s


def kit_parity(K, mod, pkg, old_jar, new_jar, vers, scratch, live_dir, sets, cmd_sets, prep_fn=None):
    """KIT: the old jar's own kit vs the new jar's kit copy in SkyyCore, each started on a COPY of the live folder (one JVM, two
    loaders over the server + SkyyCore). sets = [(key, value)] through config:fn as the console (the menu path); cmd_sets = [(key,
    value)] through cmdSetConsole + cmdGet (the /<mod>config path). vers = the two versions (masked in every answer)."""
    from jpype import JClass, JArray, JObject
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    Paths = JClass("java.nio.file.Paths")
    res = {}
    for tag, jar in (("old", old_jar), ("new", new_jar)):
        br = Sys.getProperties().get("skyy.bridge")
        if br is not None:
            br.clear()
        L = T9.loader_for(jar)
        J = lambda n, L=L: JClass(pkg + n, loader=L)
        mods = os.path.join(scratch, "kit_" + tag, "mods")
        home = os.path.join(mods, os.path.basename(live_dir))
        shutil.copytree(live_dir, home, ignore=shutil.ignore_patterns("accounts", "rebirth*", "players", "parties"))
        if prep_fn:
            prep_fn(J, home)
        core = tag == "new"
        if core:
            kit_handle(J).start(Paths.get(mods), None)
        else:
            J("CfgPub").start(Paths.get(mods), None)
        br = Sys.getProperties().get("skyy.bridge")
        fn = br.get("config:fn:" + mod)
        hdr = br.get("config:def:" + mod)
        K.check(fn is not None and hdr is not None, "KIT %s: config:fn / config:def:%s published" % (tag, mod))

        def op(*a):
            arr = JArray(JObject)(len(a))
            for i, x in enumerate(a):
                arr[i] = x
            return pyval(fn.apply(arr), vers)
        r = {"header": pyval(hdr, vers)}
        keys = [str(row[0]) for row in hdr[7]]
        r["get"] = [(k, op("get", k)) for k in keys]
        r["status"] = op("status")
        r["versions"] = op("versions")
        r["export"] = op("export", "all")
        r["log0"] = op("log", JClass("java.lang.Integer").valueOf(50))
        r["sets"] = [(k, v, op("set", k, v, None, "console", "yes", "console")) for k, v in sets]
        Rows = kit_class(J, "CfgRows", core)
        K.check(int(Sys.identityHashCode(Rows.bridge())) == int(Sys.identityHashCode(br)), "KIT %s: the kit uses skyy.bridge" % tag)
        fnc = kit_class(J, "CfgFn", core)
        r["cmd"] = []
        for k, v in cmd_sets:
            a = kit_handle(J).cmdSetConsole(k, v) if core else fnc.cmdSetConsole(k, v)
            g = kit_handle(J).cmdGet(k) if core else fnc.cmdGet(k)
            r["cmd"].append((k, v, pyval(a, vers), pyval(g, vers)))
        if core:
            kit_handle(J).flush()
        else:
            J("CfgPub").flush()
        r["get2"] = [(k, op("get", k)) for k in keys]
        r["log1"] = op("log", JClass("java.lang.Integer").valueOf(50))
        r["versions1"] = op("versions")
        r["files"] = tree(home)
        res[tag] = r
    for part in ("header", "get", "status", "versions", "export", "log0", "sets", "cmd", "get2", "log1", "versions1", "files"):
        a, b = res["old"][part], res["new"][part]
        if part == "files":
            K.eq(sorted(b), sorted(a), "KIT: the same files after the changes (%d)" % len(a))
            bad = [k for k in a if k in b and a[k] != b[k]]
            K.eq(bad, [], "KIT: every file's bytes the same (config.properties, history copies + index, change log; stamps masked)")
        else:
            K.check(a == b, "KIT %s: the old jar's own kit = the kit copy in SkyyCore%s" % (part, "" if a == b else ": %r / %r" % (str(a)[:400], str(b)[:400])))
    K.notes.append("KIT: %d rows, sets %s" % (len(res["new"]["get"]), [x[2] for x in res["new"]["sets"]][:6]))
    return res


def page_dump(out, S, jar, scratch, label, core, scenario):
    """PAGE: one jar's page through its hub bar in the engine stand-ins; the UI commands + bindings (digits masked) -> out json"""
    from jpype import JClass
    K = HK.Child(out)
    W = H.boot(scratch, jar, label)
    E = W.E
    J = lambda n: JClass(S.pkg + n)
    HB = JClass("com.skyy.core.ui.HubBar") if core else J("HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "page_" + label)
    os.makedirs(home, exist_ok=True)
    S.prep(E, J, home)
    dumps = scenario(K, W, E, J, HB, home)
    mask = lambda s: re.sub(r"\d+", "#", HEX_RE.sub("@H", re.sub(r'"t": "[0-9a-f]+"', '"t": "T"', str(s))))   # "t" = the page's own token
    json.dump([[d[0], [[mask(x) for x in c] for c in d[1]], [[mask(x) for x in e] for e in d[2]]] for d in dumps],
              open(os.path.join(scratch, "page-%s.json" % label), "w"), indent=0)
    K.notes.append("PAGE %s: %d dumps" % (label, len(dumps)))
    K.save()


def page_compare(out, scratch, a, b):
    K = HK.Child(out)
    da = json.load(open(os.path.join(scratch, "page-%s.json" % a)))
    db = json.load(open(os.path.join(scratch, "page-%s.json" % b)))
    K.eq([d[0] for d in db], [d[0] for d in da], "PAGE: the same scenario steps")
    for x, y in zip(da, db):
        K.check(x[1] == y[1], "PAGE %s: the same %d UI commands (old) / %d (new)%s" % (x[0], len(x[1]), len(y[1]),
                "" if x[1] == y[1] else ": first difference %s" % next((((i, p, q) for i, (p, q) in enumerate(zip(x[1], y[1])) if p != q)), "length")))
        K.check(x[2] == y[2], "PAGE %s: the same %d event bindings" % (x[0], len(x[2])))
    K.save()


# =====================================================================================================================  Bank-specific
EXPECT = {      # the class compare 0.1.13 -> 0.1.14: exactly the members that now call SkyyCore (everything else byte-identical)
    "BankConfig": ["~m load", "~m saveState"],                                   # CfgRows.atomicWrite -> CfgText.atomicWrite
    "BankConfigCmd": ["~m apply"],                                               # CfgFn.cmdSet -> CfgData.kit().cmdSet
    "BankHubOpen": ["~m register"], "BankHubVis": ["~m apply"],                  # HubBar.put / get -> SkyyCore's HubBar
    "BankMig": ["~m fileIdx", "~m mgKit", "~m mgLog", "~m mgSaved", "~m mgUpdate", "~m run"],   # the kit handle + CfgText
    "BankMig2": ["~m mgLog", "~m mgUpdate", "~m run"],
    "BankPage": ["~m build", "~m colorOf", "~m hubClick", "~m textOf"],          # HubBar.build / handle, UiKit.colorOf / textOf
    "BankStore": ["~m pkey"],                                                    # Core.pkey (bridge() / bridge0 unchanged)
    "SkyyBankPlugin": ["~m setup", "~m shutdown"],                               # register, kit start / shutdown, HubBar.removeAll(owner)
}


def prep(E, J, home):
    from jpype import JClass
    J("BankStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyBank")
    J("BankStore").DIR = E.Paths.get(os.path.join(home, "accounts"))
    J("BankConfig").FILE = E.Paths.get(os.path.join(home, "config.properties"))
    J("BankConfig").STATE = E.Paths.get(os.path.join(home, "state.properties"))
    J("BankWatch").STOP = False
    J("BankWatch").EXEC = E.U.allocateInstance(E.RecEx.class_)


def vis_cases(K, E, J, vis, u):
    from jpype import JClass, JImplements, JOverride
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    @JImplements("java.util.function.Function")
    class Unl:
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            if self.ans == "throw":
                raise RuntimeError("boom")
            return self.ans
    HB = JClass("com.skyy.core.ui.HubBar")
    for ans, want, what in ((TRUE, TRUE, "TRUE"), (FALSE, FALSE, "FALSE"), ("throw", FALSE, "throws")):
        E.br.put("bank:fn:unlocked", Unl(ans))
        K.check(vis.apply(u) == want, "VIS: bank:fn:unlocked answers %s -> the tab %s" % (what, "shown" if want == TRUE else "hidden"))
    E.br.put("bank:fn:unlocked", Unl(FALSE))
    K.check(len(list(HB.tabs("storage", u))) == 0, "VIS: a locked bank -> HubBar.tabs(storage) has no Bank tab")
    K.eq(str(HB.open(None, u, "storage", "bank")), "hidden", "VIS: a locked bank -> HubBar.open answers hidden (no page, no command)")
    E.br.remove("bank:fn:unlocked")
    K.check(vis.apply(u) == TRUE, "VIS: the key gone again -> shown")


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "BankPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the bank page")


def extra_hub(K, W, J):
    src = open(os.path.join(HERE, "build_skyybank_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'BANK_PAGE_CHECKED = "([0-9a-f]{12})"', src)
    data = zipfile.ZipFile(JAR).read("com/skyy/bank/SkyyBankPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data,
            "PAGE: the built page id = BANK_PAGE_CHECKED %s (the ready line; the 0.1.7 page-check rule)" % (m and m.group(1)))
    K.check(b"SkyyCore " in data, "PAGE: the ready line names the SkyyCore version")


def run_snd(out, jar, scratch, _home):
    """test_skyybank_0.1.12.py's SND phase on 0.1.14; the Server Setup rows + the check= hook come from SkyyBank's kit copy in SkyyCore"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    W = T9.World()
    st = SK.Stage()
    ua, ub = W.u(1), W.u(2)
    pa = st.player("Alice", str(ua))
    pb = st.player("Bob", str(ub))
    st.universe()
    home = os.path.join(scratch, "snd", "Skyy_SkyyBank")
    bk = T9.Bank(jar, home)
    S, C, T = bk.S, bk.C, bk.T
    Snd = JClass(PKG + "BankSnd", loader=bk.L)
    J = lambda n: JClass(PKG + n, loader=bk.L)
    Rows, Fn = kit_class(J, "CfgRows", True), kit_class(J, "CfgFn", True)
    K.check(str(Rows.class_.getClassLoader().getClass().getName()) == "com.skyy.core.KitLoader", "SND: the rows come from SkyyBank's kit copy in SkyyCore")
    C.load()
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    K.check("sounds.enabled=true" in txt and "sound.interest=true" in txt and ("sound.interest.id=%s" % SND) in txt, "CFG a fresh config.properties lists the 3 sound lines")
    K.check(bool(C.SND_ON) and bool(C.SND_INTEREST) and str(C.SND_INTEREST_ID) == SND and SND in st.ids, "CFG defaults (the id is in Assets.zip)")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("sound")) + "\n"
    open(os.path.join(home, "config.properties"), "w", encoding="latin-1").write(old + "sound.interest.id=SFX_Coins_Land\n")
    C.SND_INTEREST_ID = "x"
    C.load()
    K.check(bool(C.SND_ON) and bool(C.SND_INTEREST) and str(C.SND_INTEREST_ID) == "SFX_Coins_Land", "CFG a 0.1.11 file without the lines = the defaults; a typed id is read")
    open(os.path.join(home, "config.properties"), "w", encoding="latin-1").write(txt)
    C.load()
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "sounds.enabled", [("sound.interest", "sound.interest.id", SND)])
    K.check(all(rows[k][2] == "sounds" for k in ("sounds.enabled", "sound.interest", "sound.interest.id")), "ROW the Sounds category")
    K.check("no sound event" in (SK.kit_check(Fn, Rows, "sound.interest.id", SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, "sound.interest.id", "a b") is not None
            and SK.kit_check(Fn, Rows, "sound.interest.id", "") is None and SK.kit_check(Fn, Rows, "sound.interest.id", "SFX_Coins_Land") is None,
            "CHECK the kit's check= hook (BankSnd.check, reached from the kit copy through SkyyBank's loader) refuses a missing id / a space")
    st.clear()
    K.check(bool(Snd.playTo(pa, SND, "t")) and st.sounds() == [("Alice", SND, "UI", "2d")], "BankSnd.playTo")
    Snd.LAST.clear()
    T9.write_acc(home, W.key(ua), 1000000)
    bk.point(home)
    C.load()
    now = int(JClass("java.lang.System").currentTimeMillis())
    st.clear()
    C.LAST = now - DAY - 5000
    T.sweep()
    K.check(any("You earned" in t for w, t in st.chats("Alice")), "SITE the sweep paid Alice and sent the chat line")
    K.eq(st.sounds(), [("Alice", SND, "UI", "2d")], "SITE ... AND the payout sting, to Alice only")
    g = PW.calls(jar)
    K.check(PKG + "BankSnd.playTo" in g.get("BankTick.sweep", set()), "STATIC the sweep plays the sting")
    K.save()


def controls_to_notes(fn, mark):
    """an old phase whose CONTROL checks prove an OLD jar's bug: against the live 0.1.13 (which has the fix) they become notes"""
    def phase(out, jar, scratch, home):
        fn(out, jar, scratch, home)
        d = json.load(open(out))
        gone = [f for f in d["fails"] if mark in f]
        d["fails"] = [f for f in d["fails"] if mark not in f]
        d["notes"] = d.get("notes", []) + ["control for %s (old jar = the live 0.1.13, which has the fix): %s" % (mark, f) for f in gone]
        json.dump(d, open(out, "w"), indent=1)
    return phase


CFG16 = "#SkyyBank config\r\ninterestPercent=2\r\nintervalMinutes=60\r\nlastInterestMillis=%d\r\nmaxPrincipal=10000000\r\n"


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    W = T9.World()
    Paths = JClass("java.nio.file.Paths")
    now = int(JClass("java.lang.System").currentTimeMillis())
    # the 0.1.7 default file text = the jar's own default (BankConfig.DEFAULT_TEXT) with catchUpPeriods=24, CRLF
    cases = [("m16", lambda h: open(os.path.join(h, "config.properties"), "w", newline="").write(CFG16 % (now - 3600000))),
             ("m24", None), ("m30", None), ("none", lambda h: None), ("blocked", None)]
    res = {}
    for tag, jar_ in (("old", OLD_JAR), ("new", jar)):
        for case, mk in cases:
            home = os.path.join(scratch, "mig", tag, case, "Skyy_SkyyBank")
            os.makedirs(home)
            bk = T9.Bank(jar_, home)
            if case in ("m24", "m30", "blocked"):
                dt = str(bk.C.DEFAULT_TEXT).replace("catchUpPeriods=1", "catchUpPeriods=%s" % ("30" if case == "m30" else "24"))
                assert "catchUpPeriods=" in dt
                open(os.path.join(home, "config.properties"), "w", newline="").write(dt.replace("\n", "\r\n"))
                os.makedirs(os.path.join(home, "migrations"), exist_ok=True)
                open(os.path.join(home, "migrations", "bank-daily-1.done"), "w").write("x\n")      # 0.1.7's update already ran
                open(os.path.join(home, "state.properties"), "w").write("lastInterestMillis=%d\n" % (now - 3600000))
                if case == "blocked":
                    open(os.path.join(home, "config-history"), "w").write("a FILE where the history folder goes\n")
            elif mk:
                mk(home)
            M1 = JClass(PKG + "BankMig", loader=bk.L)
            M2 = JClass(PKG + "BankMig2", loader=bk.L)
            r1 = norm(M1.run(Paths.get(home)))
            r2 = norm(M2.run(Paths.get(home)))
            t1 = tree(home)
            M1.run(Paths.get(home))
            M2.run(Paths.get(home))
            t2 = tree(home)
            res[(tag, case)] = (r1, r2, t1, t2)
    for case, _mk in cases:
        o, n = res[("old", case)], res[("new", case)]
        K.eq(n[0:2], o[0:2], "MIG %s: BankMig / BankMig2 report the same" % case)
        K.eq(sorted(n[2]), sorted(o[2]), "MIG %s: the same files written (%s)" % (case, sorted(o[2])))
        K.eq([k for k in o[2] if o[2].get(k) != n[2].get(k)], [], "MIG %s: every file the same (stamps masked)" % case)
        K.eq(n[3], n[2], "MIG %s: a second run changes nothing (0.1.14)" % case)
    K.check(any("history" in k for k in res[("new", "m24")][2]) and "catchUpPeriods=1" in res[("new", "m24")][2].get("config.properties", ""),
            "MIG m24: 24 -> 1 with the History copy written through SkyyCore's kit handle")
    K.check("catchUpPeriods 24 -> 1" in res[("new", "m24")][2].get("config-changes.log", "").replace("\t", " ").replace("catchUpPeriods 24 1", "catchUpPeriods 24 -> 1")
            or "\tcatchUpPeriods\t24\t1\tok" in res[("new", "m24")][2].get("config-changes.log", ""), "MIG m24: the change-log line (Undo in Server Setup)")
    K.check("intervalSeconds=86400" in res[("new", "m16")][2].get("config.properties", ""), "MIG m16: a 0.1.6 file -> daily interest (0.1.7's update)")
    K.check("catchUpPeriods=30" in res[("new", "m30")][2].get("config.properties", ""), "MIG m30: a hand-edited value is kept")
    K.check(not any(k.startswith("migrations/bank-backpay") for k in res[("new", "blocked")][2]), "MIG blocked: no marker while history cannot be written")
    K.save()


def run_kit(out, jar, scratch, _home):
    K = HK.Child(out)

    def prep_fn(J, home):
        b = T9.Bank.__new__(T9.Bank)
        b.L = J("BankStore").class_.getClassLoader()
        b.S, b.C, b.T = J("BankStore"), J("BankConfig"), J("BankTick")
        b.point(home)
        b.C.load()
    kit_parity(K, "SkyyBank", PKG, OLD_JAR, jar, ("0.1.13", VERSION), scratch, LIVE_DIR,
               sets=[("interestPercent", "3"), ("catchUpPeriods", "2"), ("sound.interest", "false"), ("nope.key", "1"),
                     ("interestPercent", "999"), ("scope", "account")],
               cmd_sets=[("maxPrincipal", "20000000"), ("interestPercent", "2")], prep_fn=prep_fn)
    K.save()


def bank_scenario(K, W, E, J, HB, home):
    from jpype import JClass
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    T9.write_acc(home, str(W.P.pr.getUuid()), 123456)
    J("BankConfig").load()
    J("BankHubOpen").register()
    dumps = []
    for nm, X in (("account", W.P), ("no account", W.O)):
        r = str(HB.open(X.pr, X.pr.getUuid(), "storage", "bank"))
        E.pump(X)
        pg = X.pm.getCustomPage()
        K.check(r == "bridge" and pg is not None, "PAGE %s opened through the hub bar (%s)" % (nm, r))
        b, ev = UCB(), UEB()
        pg.build(X.ref, b, ev, X.st)
        dumps.append((nm, H.cmds_of(b), H.events_of(ev)))
        n0 = len(E.sent(X))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"refresh","@BAmount":""}'))
        E.pump(X)
        dumps.append((nm + " refresh", [[k] for k in E.kinds(X, n0)], [[E.strs_of(X, n0)]]))
        n1 = len(E.sent(X))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"hub:bank"}'))
        E.pump(X)
        dumps.append((nm + " own tab", [[k] for k in E.kinds(X, n1)], [[E.strs_of(X, n1)]]))
    return dumps


S = H.Spec(name="SkyyBank", version=VERSION, pkg=PKG, hub="storage", tab="bank", mod="SkyyBank", open_cls="BankHubOpen", vis_cls="BankHubVis",
           page_cls="BankPage", prefix="SkyyBankF", idp="SkyyB", plugin_cls="SkyyBankPlugin", register_call="BankHubOpen.register",
           register=lambda J: J("BankHubOpen").register(), prep=prep, vis_cases=vis_cases, clicks=[('{"a":"refresh","@BAmount":""}', chk_refresh)],
           extra_hub=extra_hub, jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           hub_class="com.skyy.core.ui.HubBar", hub_owner="SkyyBank", kit_in_jar=False,
           added=["CfgData"], removed=list(KITN) + ["HubBar"],
           expect=EXPECT,
           extra_phases=[("snd", run_snd), ("rb", controls_to_notes(T11.run_rb, "0.1.10")), ("name", controls_to_notes(T10.run_name, "CONTROL 0.1.9")),
                         ("exec", controls_to_notes(T9.run_exec, "0.1.8")), ("live2", T9.run_live), ("mig", run_mig), ("kit", run_kit),
                         ("pageold", lambda out, jar, scratch, home: page_dump(out, S, OLD_JAR, scratch, "old", False, bank_scenario)),
                         ("pagenew", lambda out, jar, scratch, home: page_dump(out, S, jar, scratch, "new", True, bank_scenario)),
                         ("pagecmp", lambda out, jar, scratch, home: page_compare(out, scratch, "old", "new"))])

if __name__ == "__main__":
    H.run(S)
