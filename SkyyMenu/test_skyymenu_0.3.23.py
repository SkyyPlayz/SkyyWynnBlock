"""Harness for SkyyMenu 0.3.23 (the Admin page; tools/menu_0_3_23_patch.py).
Build first: python tools/menu_0_3_23_patch.py && python SkyyMenu/build_skyymenu_0.3.23.py

    python SkyyMenu/test_skyymenu_0.3.23.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.22 -> 0.3.23: exactly OpsPage added; AdminPage drawList / clickView (+ openOps), AdminModCmd execute + its description,
              MenuData.<clinit> (the Mods text line /modconfig admin + the version), the version texts differ
  O  ops      THE ADMIN PAGE, executed (-Xverify:all, every SET jar + the engine on the class path):
              - every OPS row against the REAL command objects of the SET jars (constructed, setOwner'd + completeRegistration'd the
                engine's way): the root exists, its requirePermission node = the row's node, every literal word is a sub-command or an
                option the command takes
              - DISPATCH STRINGS EXACT: every button clicked on a real OpsPage (player picked, Text box filled, a danger button twice)
                records exactly the expected line, and that line goes through the ENGINE's own parser (Tokenizer, ParserContext,
                AbstractCommand.acceptCall) to the command's execute (the player-only answer); the same line + one extra word is
                refused (control); /shardadmin give <player> is refused by the engine (why it is left out)
              - PERMISSION HIDING: OpsPage.visible(i) = the engine's own parse-time permission verdict for that line, for a sender with
                no node, each single node of the table, every node, "*" (PermissionsModule's own set matching); no node = nothing drawn;
                the page node gate (skyymenu.modconfig) hides everything and refuses clicks
              - CONFIRM: a danger button arms on the first click (no dispatch, "Press again" look), a second click within 400 ms is one
                double-click, the second click within 10 s runs it once, after 10 s it re-arms (and says the 10 s ran out), another
                player / Text in between re-arms; non-danger buttons run at once, and a repeat of the same line within 400 ms (a
                duplicated event) runs nothing (Airdrop here)
              - SUB-COMMAND DEPTH: O_DEPTH of every row = the sub-commands the real SET tree has for its literal words (the rest are
                arguments); an older mod without a sub-command, or with an argument count no usage variant takes, HIDES the button
              - the page itself (engine UICommandBuilder / UIEventBuilder): tabs, 24 buttons per page + paging, help texts, the picker,
                the Text box value kept, Diagnostics info lines (versions vs the SET), missing input answers, the click payloads
              - Server Setup's Admin button + /modconfig admin (bytecode + the engine parser)
  S, T, N, D  every 0.3.22 check carried forward: test_skyymenu_0.3.22.py's run_shards and the run_tabs / run_name / run_live it
              carries, run on the 0.3.23 jar
  AA engine-access audit
Scratch: tools/dev/scratch/admin23/menu (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, ast, zipfile, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyymenu_0_3_22", os.path.join(HERE, "test_skyymenu_0.3.22.py"))
T22 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T22)
T21, T20, T19 = T22.T21, T22.T20, T22.T19

VERSION = "0.3.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "admin23", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T19.LIVE_DIR
EXPECT = {
    "MenuData": ["~<clinit>"],                       # the Mods text line + the version
    "CfgRows": ["~m header"],                        # the version text
    "CfgFn": ["~m opExport"],                        # the version text
    "SkyyMenuPlugin": ["~m setup"],                  # the ready line's version
    "AdminPage": ["~m drawList", "~m clickView", "+m openOps"],
    "AdminModCmd": ["~m execute", "~c "],            # /modconfig admin + the description
}
ADDED = ["OpsPage"]

ENGINE_ROOTS = ["com.hypixel.hytale.server.core.command.commands.debug.server.ServerCommand",
                "com.hypixel.hytale.server.core.command.commands.debug.VersionCommand",
                "com.hypixel.hytale.server.core.command.commands.server.WhoCommand",
                "com.hypixel.hytale.server.core.plugin.commands.PluginCommand"]


def set_pins():
    t = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
    for n in ast.parse(t).body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "SET" for x in n.targets):
            return ast.literal_eval(n.value)
    raise SystemExit("no SET")


def run_ops(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    pins = set_pins()
    jars = {}
    for m, v in pins:
        j = os.path.join(ROOT, m, "%s-%s.jar" % (m, v))
        if os.path.isfile(j) and m != "SkyyMenu":
            jars[m] = j
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar] + sorted(jars.values()), verify=True)
    Cls = JClass("java.lang.Class")
    Mod = JClass("java.lang.reflect.Modifier")
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HS = JClass("java.util.HashSet")
    Tok = JClass("com.hypixel.hytale.server.core.command.system.Tokenizer")
    PCx = JClass("com.hypixel.hytale.server.core.command.system.ParserContext")
    PRs = JClass("com.hypixel.hytale.server.core.command.system.ParseResult")
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    OP = JClass(PKG + "OpsPage")
    LINES = [str(x) for x in OP.O_LINE]
    NODES = [str(x) for x in OP.O_NODE]
    MODS = [str(x) for x in OP.O_MOD]
    CONF = [bool(x) for x in OP.O_CONF]
    TABS = [int(x) for x in OP.O_TAB]
    LABELS = [str(x) for x in OP.O_LABEL]
    DEPTH = [int(x) for x in OP.O_DEPTH]
    N = len(LINES)
    K.check(N >= 80 and len(set(LABELS)) == N, "O: %d buttons, labels unique" % N)

    # ---------------- model senders: the engine's own set matching (PermissionsModule.hasPermission(Set, PermissionQuery))
    MSGS = []

    def sender(nodes, name="Tester"):
        ns = HS()
        for n_ in nodes:
            ns.add(n_)

        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Snd(object):
            @JOverride
            def getUsername(self):
                return name

            @JOverride
            def getUuid(self):
                return JClass("java.util.UUID")(1, 2)

            @JOverride
            def sendMessage(self, m):
                MSGS.append(str(m.getMessageId() or m.getRawText()))

            @JOverride
            def hasPermission(self, q, *rest):
                if isinstance(q, str) or str(q.getClass().getName()) == "java.lang.String":
                    r = PM.hasPermission(ns, str(q))
                else:
                    r = PM.hasPermission(ns, q)
                return bool(r) if r is not None else False
        return Snd()

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    owner = Owner()
    CMGR = JClass("com.hypixel.hytale.server.core.command.system.CommandManager")
    eng_owner = U.allocateInstance(CMGR.class_)

    # ---------------- the real command objects: every AbstractCommand of a SET jar with a no-argument constructor
    cand = {}

    def construct(cn, ld):
        k = Cls.forName(cn, True, ld)
        if not AC.class_.isAssignableFrom(k) or Mod.isAbstract(k.getModifiers()):
            return None
        try:
            c = k.getDeclaredConstructor()
        except Exception:
            return None
        c.setAccessible(True)
        return c.newInstance()
    ld = JClass("java.lang.ClassLoader").getSystemClassLoader()
    for m, j in sorted(list(jars.items()) + [("SkyyMenu", jar)]):
        for nm in zipfile.ZipFile(j).namelist():
            if not nm.endswith(".class") or "$" in nm:
                continue
            try:
                o = construct(nm[:-6].replace("/", "."), ld)
            except Exception:
                o = None
            if o is not None and o.getName() is not None:
                cand.setdefault((m, str(o.getName())), []).append(o)
                for a in o.getAliases():
                    cand.setdefault((m, str(a)), []).append(o)
    for cn in ENGINE_ROOTS:
        o = construct(cn, ld)
        cand.setdefault(("Hytale", str(o.getName())), []).append(o)

    def size(c):
        return c.getSubCommands().size() + c.getVariantCommands().size()
    roots = {}
    for i in range(N):
        root = LINES[i].split(" ")[0]
        key = (MODS[i], root)
        if key in roots:
            continue
        cs = cand.get(key, [])
        K.check(len(cs) > 0, "O root: %s has a command /%s" % key)
        if not cs:
            continue
        best = sorted(cs, key=size)[-1]
        try:
            best.setOwner(owner if best.getPermission() is not None else eng_owner)
        except Exception as e:
            K.check(False, "O root: /%s setOwner: %s" % (root, e))
        try:
            best.completeRegistration()
        except Exception as e:
            K.notes.append("completeRegistration /%s: %s" % (root, str(e)[:80]))
        roots[key] = best
    # the row's node = the requirePermission of the root or of the sub-command the line names (an admin sub under a player command)
    for i in range(N):
        if MODS[i] == "Hytale" or (MODS[i], LINES[i].split(" ")[0]) not in roots:
            continue
        c = roots[(MODS[i], LINES[i].split(" ")[0])]
        path = [c]
        for w in LINES[i].split(" ")[1:]:
            if w.startswith("{"):
                break
            s2 = c.getSubCommand(w)
            if s2 is None:
                break
            c = s2
            path.append(c)
        K.eq(DEPTH[i], len(path) - 1, "O depth: /%s - O_DEPTH = the sub-commands the real tree has for its literal words" % LINES[i])
        n_ = len(LINES[i].split(" ")) - len(path)
        _xf = AC.class_.getDeclaredField("allowsExtraArguments"); _xf.setAccessible(True); ext = bool(_xf.get(c)) and c.getRequiredArguments().size() < n_ and c.getVariantByArgCount(n_) is None
        K.eq(bool(OP.O_EXTRA[i]), ext, "O extra: /%s - O_EXTRA = the command reads extra words (allowsExtraArguments, no variant for %d)" % (LINES[i], n_))
        declared = [str(x.getPermission()) for x in path if x.getPermission() is not None and not str(x.getPermission()).startswith(str(path[0].getPermission()) + ".")] if path[0].getPermission() is not None else                    [str(x.getPermission()) for x in path[1:] if x.getPermission() is not None]
        K.check(NODES[i] in declared, "O node: /%s - the row's node %s is the command's own requirePermission (%s)" % (LINES[i], NODES[i], declared))

    # ---------------- an OpsPage with the test seams (real command objects, a model sender, online names, the clock)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    pr = U.allocateInstance(PR.class_)
    jf(PR.class_, "uuid").set(pr, JClass("java.util.UUID").fromString("00000000-0000-4000-8000-000000000323"))
    try:
        jf(PR.class_, "username").set(pr, "Skyy")
    except KeyError:
        K.notes.append("PlayerRef has no username field")
    HM = JClass("java.util.HashMap")
    AL = JClass("java.util.ArrayList")
    Long = JClass("java.lang.Long")
    Bool = JClass("java.lang.Boolean")

    def page(nodes=("*",), online=("Alpha", "Skyy", "zed"), ok=True, tab=0):
        p = OP(pr, tab)
        t = HM()
        for (m, r), c in roots.items():
            t.put("cmd:" + r, c)
        t.put("sender", sender(list(nodes)))
        t.put("online", JArray(JString)(list(online)))
        t.put("page", Bool.TRUE if ok else Bool.FALSE)
        t.put("ran", AL())
        t.put("now", Long(1000000))
        p.test = t
        return p

    def ran(p):
        return [str(x) for x in p.test.get("ran")]

    def at(p, ms):
        p.test.put("now", Long(ms))

    def click(p, data):
        p.handleDataEvent(None, None, data)

    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def build(p):
        b, ev = UCB(), UEB()
        p.build(None, b, ev, None)
        res = []
        for c in list(b.getCommands()):
            g = lambda n: (lambda v: "" if v is None else str(v))(jf(c.getClass(), n).get(c))
            dat = g("data")
            if dat.startswith("{"):
                try:
                    dat = str(json.loads(dat).get("0", dat))
                except Exception:
                    pass
            res.append((g("selector"), g("text"), dat))
        return res, ev

    def btn_ids(cmds):
        return [int(m.group(1)) for s_, t, d in cmds for m in [re.search(r"TextButton #SkyyOpsA(\d+) \{", t)] if m]

    def sets(cmds, sel):
        return [d for s_, t, d in cmds if s_ == sel]

    # ---------------- dispatch strings exact: every button, clicked, records exactly the expected line
    PLAYER, TEXT = "Alpha", "Oak_Log.2"
    expect_line = {}
    for i in range(N):
        exp = LINES[i].replace("{p}", PLAYER).replace("{t}", TEXT)
        expect_line[i] = exp
        p = page()
        p.pick = PLAYER
        p.arg = TEXT
        at(p, 1000000)
        click(p, '{"a":"op%d","@OpsArg":"%s"}' % (i, TEXT))
        if CONF[i]:
            K.eq(ran(p), [], "O confirm: %s - the first click only arms" % LABELS[i])
            K.check(str(p.info).startswith("=Press ") and int(p.armed) == i, "O confirm: %s armed (%s)" % (LABELS[i], p.info))
            at(p, 1000000 + 3000)
            click(p, '{"a":"op%d","@OpsArg":"%s"}' % (i, TEXT))
        K.eq(ran(p), [exp], "O dispatch: %s -> /%s" % (LABELS[i], exp))
        K.check(str(p.info).startswith("+Ran /" + exp), "O dispatch: %s answers %s" % (LABELS[i], p.info))

    # ---------------- the engine's own parser accepts every line (reaches the player command's execute) and refuses line + extra word
    allp = sender(["*"])

    def parse(root, line, snd=None):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        if res.failed():
            return False, ["tokenizer"]
        ctx = PCx.of(toks, line, res)
        try:
            root.acceptCall(snd or allp, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:300])
        if res.failed():
            res.sendMessages(snd or allp)
            return False, list(MSGS)
        return True, list(MSGS)
    for i in range(N):
        root = roots.get((MODS[i], LINES[i].split(" ")[0]))
        if root is None:
            continue
        ok, msgs = parse(root, expect_line[i])
        K.check(ok, "O engine parser: /%s parses (%s)" % (expect_line[i], msgs[:2]))
        if MODS[i] != "Hytale":
            live_arg = any(x.startswith("EXC") and "universe" in x.lower() for x in msgs)
            if live_arg:
                K.notes.append("/%s: the player argument is resolved against the live Universe while parsing (no server here) - parsed up to it" % expect_line[i])
            K.check("server.commands.errors.playerOrArg" in msgs or live_arg, "O engine parser: /%s reaches the player command (%s)" % (expect_line[i], msgs[:2]))
        allows_extra = False
        try:
            allows_extra = bool(jf(AC.class_, "allowsExtraArguments").get(p.leaf(i))) or bool(jf(AC.class_, "allowsExtraArguments").get(root))
        except Exception:
            pass
        if not allows_extra:
            ok2, msgs2 = parse(root, expect_line[i] + " x1 x2 x3 x4 x5 x6")
            K.check(not ok2, "O engine parser CONTROL: /%s + 6 extra words is refused (%s)" % (expect_line[i], msgs2[:1]))
    sh = cand.get(("SkyyShards", "shardadmin"), [])
    if sh:
        r_ = sorted(sh, key=size)[-1]
        r_.setOwner(owner)
        ok, msgs = parse(r_, "shardadmin give Alpha")
        K.check(not ok and any("wrongNumber" in x for x in msgs), "O left out: /shardadmin give <player> is refused by the engine parser (%s)" % msgs[:1])
        ok, msgs = parse(r_, 'shardadmin "give Alpha"')
        K.notes.append("quoted /shardadmin \"give Alpha\" parses=%s - the GREEDY_STRING value keeps the quotes (ArgTypes.GREEDY_STRING.parse)" % ok)
    mc = JClass(PKG + "AdminCmd")()
    mc.setOwner(owner)
    ok, msgs = parse(mc, "modconfig admin")
    K.check(ok and "server.commands.errors.playerOrArg" in msgs, "O /modconfig admin parses to the usage variant (%s)" % msgs[:1])

    # ---------------- permission hiding = the engine's own parse-time verdict, per node set
    all_nodes = sorted(set(n for n in NODES if n))

    def engine_ok(i, snd):
        root = roots.get((MODS[i], LINES[i].split(" ")[0]))
        ok, msgs = parse(root, expect_line[i], snd)
        return ok
    sets_ = [[], ["skyymenu.modconfig"]] + [[n] for n in all_nodes] + [all_nodes, ["*"]]
    for nodes in sets_:
        p = page(nodes)
        snd = p.test.get("sender")
        vis = [bool(p.visible(i)) for i in range(N)]
        eng = [engine_ok(i, snd) for i in range(N)]
        dif = [LINES[i] for i in range(N) if vis[i] != eng[i]]
        K.check(not dif, "O hiding: nodes %s - visible == the engine's permission verdict (differs: %s)" % (nodes[:3], dif[:4]))
        if nodes == []:
            K.check(not any(vis), "O hiding: no node = no button")
        if len(nodes) == 1 and nodes[0] in all_nodes:
            K.check(all(not vis[i] for i in range(N) if NODES[i] != nodes[0]), "O hiding: %s shows only its own mod's rows" % nodes[0])
            own = [i for i in range(N) if NODES[i] == nodes[0]]
            K.check(any(vis[i] for i in own), "O hiding: %s shows at least one of its rows (%d of %d)" % (nodes[0], sum(vis[i] for i in own), len(own)))
            hid = [LINES[i] for i in own if not vis[i]]
            if hid:
                K.notes.append("%s alone does not reach (engine-generated sub nodes): %s" % (nodes[0], hid))
        if nodes == ["*"]:
            K.check(all(vis), "O hiding: * (an op) sees every button: missing %s" % [LINES[i] for i in range(N) if not vis[i]])
    p = page(["skyyauctions.admin"])
    _ah = sorted(LABELS[i] for i in range(N) if NODES[i] == "skyyauctions.admin")
    K.eq(sorted(LABELS[i] for i in range(N) if p.visible(i)), _ah,
         "O hiding: skyyauctions.admin alone = exactly the %d Auction House buttons" % len(_ah))
    K.eq(len(_ah), 10, "O hiding: 10 Auction House buttons (AH status added in the fix round)")
    # missing mod: no command object -> hidden
    p = page(["*"])
    p.test.remove("cmd:ahadmin")
    K.check(not any(p.visible(i) for i in range(N) if LINES[i].startswith("ahadmin")), "O hiding: SkyyAuctions not on the server = no AH button")
    click(p, '{"a":"op%d"}' % LINES.index("ahadmin pause"))
    K.check(ran(p) == [] and str(p.info).startswith("-You cannot run"), "O hiding: a stale click on a hidden button runs nothing (%s)" % p.info)
    # FIX (critic: older / partial mods): a command object WITHOUT one sub-command (an older SkyyAuctions with no closeall, a SkyyQuests
    # with no npc) hides exactly the rows that need it - never falls back to the parent; the other rows of that command stay
    SubF = jf(AC.class_, "subCommands")

    def without(key, sub):
        m_, r_ = key
        fresh = construct(roots[key].getClass().getName(), ld)
        fresh.setOwner(owner)
        try:
            fresh.completeRegistration()
        except Exception:
            pass
        mp = SubF.get(fresh)
        K.check(mp.remove(sub) is not None, "O older mod: /%s really had the sub-command %s" % (r_, sub))
        K.check(fresh.getSubCommand(sub) is None, "O older mod: /%s %s removed" % (r_, sub))
        return fresh
    for key, sub in ((("SkyyAuctions", "ahadmin"), "closeall"), (("SkyyQuests", "questadmin"), "npc"), (("SkyyWorldGen", "zone"), "info")):
        p = page(["*"])
        p.test.put("cmd:" + key[1], without(key, sub))
        need = [i for i in range(N) if MODS[i] == key[0] and LINES[i].split(" ")[0] == key[1] and DEPTH[i] >= 1 and LINES[i].split(" ")[1] == sub]
        rest = [i for i in range(N) if MODS[i] == key[0] and LINES[i].split(" ")[0] == key[1] and i not in need]
        K.check(len(need) >= 1 and not any(p.visible(i) for i in need), "O older mod: /%s without %s hides %s" % (key[1], sub, [LABELS[i] for i in need]))
        K.check(len(rest) >= 1 and all(p.visible(i) for i in rest), "O older mod: /%s without %s keeps %s" % (key[1], sub, [LABELS[i] for i in rest]))
        p.pick = PLAYER
        click(p, '{"a":"op%d"}' % need[0])
        click(p, '{"a":"op%d"}' % need[-1])
        K.eq(ran(p), [], "O older mod: clicking a hidden %s row runs nothing (%s)" % (sub, p.info))
    # an argument count no usage variant takes hides the row too (the old fallback drew it): /zone with a 2-word Text-free line
    p = page(["*"])
    zi = LINES.index("zone {t}")
    K.check(p.visible(zi) and p.leaf(zi) is not None, "O leaf: /zone <id> resolves to its usage variant")
    K.check(p.leaf(LINES.index("ahadmin")) is not None and p.visible(LINES.index("ahadmin")), "O leaf: bare /ahadmin (AH status) resolves to the root")

    # ---------------- the page node gate
    p = page(["*"], ok=False)
    cmds, _ev = build(p)
    K.eq(btn_ids(cmds), [], "O gate: without skyymenu.modconfig no button is drawn")
    K.check(not any(s_ == "#SkyyOpsTabs" for s_, t, d in cmds) and not any("SkyyOpsArg" in t for s_, t, d in cmds), "O gate: no tabs, no Text box")
    K.check(any("skyymenu.modconfig" in d for s_, t, d in cmds if s_ == "#SkyyOpsSub.Text"), "O gate: the page says which permission it needs")
    click(p, '{"a":"op0"}')
    K.check(ran(p) == [] and "skyymenu.modconfig" in str(p.info), "O gate: a click runs nothing (%s)" % p.info)
    click(p, '{"a":"close"}')
    K.eq(str(p.test.get("went")), "close", "O gate: Close still works")

    # ---------------- confirm timing
    d = LINES.index("classadmin reset {p}")
    p = page(["*"])
    p.pick = "Alpha"
    at(p, 5000)
    click(p, '{"a":"op%d"}' % d)
    K.check(ran(p) == [] and p.armedNow(d), "O confirm: first click arms")
    p.tab = TABS[d]
    p.pg = [i for i in range(N) if TABS[i] == TABS[d]].index(d) // 24
    cmds, _ev = build(p)
    arm = [t for s_, t, dd in cmds if ("TextButton #SkyyOpsA%d " % d) in t]
    K.check(arm and "PRESS AGAIN" in arm[0].upper() and "Destructive" in arm[0], "O confirm: the armed button reads Press again (Destructive): %s" % [a[:160] for a in arm])
    at(p, 5200)
    click(p, '{"a":"op%d"}' % d)
    K.check(ran(p) == [] and p.armedNow(d), "O confirm: a second click within 400 ms is one double-click (still armed, nothing run)")
    at(p, 5000 + 10000)
    click(p, '{"a":"op%d"}' % d)
    K.eq(ran(p), ["classadmin reset Alpha"], "O confirm: the second click at 10.0 s runs it once")
    K.check(not p.armedNow(d), "O confirm: disarmed after running")
    at(p, 30000)
    click(p, '{"a":"op%d"}' % d)
    at(p, 30000 + 10001)
    click(p, '{"a":"op%d"}' % d)
    K.eq(ran(p), ["classadmin reset Alpha"], "O confirm: after 10 s the click arms again instead of running")
    at(p, 30000 + 12000)
    click(p, '{"a":"pnext"}')
    K.eq(str(p.pick), "Skyy", "O picker: > picks the next online player")
    click(p, '{"a":"op%d"}' % d)
    K.eq(ran(p), ["classadmin reset Alpha"], "O confirm: another player picked in between = arm again (nothing run)")
    at(p, 30000 + 13000)
    click(p, '{"a":"op%d"}' % d)
    K.eq(ran(p), ["classadmin reset Alpha", "classadmin reset Skyy"], "O confirm: then the second click runs it for the new player")
    t_ = LINES.index("ahadmin remove {t}")
    p = page(["*"])
    at(p, 1000)
    click(p, '{"a":"op%d","@OpsArg":"L1"}' % t_)
    at(p, 2000)
    click(p, '{"a":"op%d","@OpsArg":"L2"}' % t_)
    K.eq(ran(p), [], "O confirm: other Text between the clicks = arm again")
    at(p, 3000)
    click(p, '{"a":"op%d","@OpsArg":"L2"}' % t_)
    K.eq(ran(p), ["ahadmin remove L2"], "O confirm: then it runs with the Text shown")
    s_ = LINES.index("ahadmin pause")
    p = page(["*"])
    click(p, '{"a":"op%d"}' % s_)
    K.eq(ran(p), ["ahadmin pause"], "O: a non-danger button runs on the first click")
    K.check(not any(CONF[i] for i in range(N) if LINES[i] in ("ahadmin pause", "ahadmin list", "rebirthadmin status", "ahadmin")), "O: info buttons never confirm")
    # FIX (critic: Airdrop here): a duplicated Activating event / double-click within 400 ms on ANY button runs it once
    a_ = LINES.index("exploreadmin airdrop")
    p = page(["*"])
    at(p, 50000)
    click(p, '{"a":"op%d"}' % a_)
    at(p, 50000 + 150)
    click(p, '{"a":"op%d"}' % a_)
    K.eq(ran(p), ["exploreadmin airdrop"], "O double: Airdrop here clicked twice within 400 ms spawns one airdrop")
    at(p, 50000 + 399)
    click(p, '{"a":"op%d"}' % a_)
    K.eq(ran(p), ["exploreadmin airdrop"], "O double: ... still one at 399 ms")
    at(p, 50000 + 400)
    click(p, '{"a":"op%d"}' % a_)
    K.eq(ran(p), ["exploreadmin airdrop", "exploreadmin airdrop"], "O double: a click 400 ms later is a real second click")
    p = page(["*"])
    at(p, 60000)
    click(p, '{"a":"op%d"}' % LINES.index("ahadmin pause"))
    at(p, 60000 + 100)
    click(p, '{"a":"op%d"}' % LINES.index("ahadmin resume"))
    K.eq(ran(p), ["ahadmin pause", "ahadmin resume"], "O double: a DIFFERENT button right after is not swallowed")
    # a confirmed danger run followed by a duplicated event does not re-arm
    p = page(["*"])
    hb = LINES.index("sethub")
    at(p, 70000)
    click(p, '{"a":"op%d"}' % hb)
    at(p, 71000)
    click(p, '{"a":"op%d"}' % hb)
    at(p, 71100)
    click(p, '{"a":"op%d"}' % hb)
    K.check(ran(p) == ["sethub"] and not p.armedNow(hb), "O double: a duplicated event after a confirmed run neither runs nor re-arms (%s)" % p.info)
    # FIX (critic: stale Press again): the click after the 10 s window says the window ran out
    p = page(["*"])
    at(p, 80000)
    click(p, '{"a":"op%d"}' % hb)
    at(p, 80000 + 10001)
    click(p, '{"a":"op%d"}' % hb)
    K.check(ran(p) == [] and str(p.info).startswith("=The 10 s ran out") and p.armedNow(hb), "O confirm: after 10 s it says the window ran out and re-arms (%s)" % p.info)
    at(p, 80000 + 12000)
    click(p, '{"a":"op%d"}' % hb)
    K.eq(ran(p), ["sethub"], "O confirm: ... then the next click within 10 s runs it")
    # FIX (critic: guild names have spaces): Guild info asks for the tag or id (2-4 letters / digits) the Text box can hold
    gi = LINES.index("guildadmin info {t}")
    K.eq(str(OP.O_HINT[gi]), "guild tag or id", "O input: Guild info asks for the guild tag or id")
    p = page(["*"])
    p.arg = "SKY"
    p.run(gi)
    K.eq(ran(p), ["guildadmin info SKY"], "O input: Guild info with a tag runs")
    # FIX (critic: closeall labels): the closeall buttons say they act on the admin's own listings
    K.check(LABELS[LINES.index("ahadmin closeall")] == "My AH close preview" and LABELS[LINES.index("ahadmin closeall confirm")] == "Close my AH listings",
            "O labels: closeall buttons name the admin's own listings")
    K.check(not CONF[LINES.index("ahadmin")] and TABS[LINES.index("ahadmin")] == 1, "O: AH status (bare /ahadmin) on Economy, no confirm")
    K.check(all(CONF[LINES.index(x)] for x in ("sethub", "classadmin reset {p}", "questadmin repay {p}", "ahadmin remove {t}", "bazaaradmin reset {t}",
                                                "merchantadmin remove {t}", "rebirthadmin recover", "ahadmin closeall confirm")), "O: the danger buttons confirm")

    # ---------------- missing input
    p = page(["*"], online=())
    p.pick = None
    click(p, '{"a":"op%d"}' % LINES.index("classadmin info {p}"))
    K.check(ran(p) == [] and str(p.info).startswith("-Pick an online player"), "O input: no player online -> %s" % p.info)
    p = page(["*"])
    p.pick = "Gone"
    click(p, '{"a":"op%d"}' % LINES.index("classadmin info {p}"))
    K.check(ran(p) == [] and str(p.info).startswith("-Pick"), "O input: a picked player who left is not used")
    p = page(["*"])
    click(p, '{"a":"op%d","@OpsArg":""}' % LINES.index("bazaaradmin info {t}"))
    K.check(ran(p) == [] and "item id" in str(p.info), "O input: empty Text box -> %s" % p.info)
    for bad in ("two words", "x;y", "a" * 65, 'q\\"x'):
        p = page(["*"])
        p.arg = bad
        p.run(LINES.index("bazaaradmin info {t}"))
        K.check(ran(p) == [] and str(p.info).startswith("-"), "O input: Text %r refused" % bad)
    p = page(["*"], online=("Bad Name",))
    p.pick = "Bad Name"
    p.run(LINES.index("classadmin info {p}"))
    K.check(ran(p) == [], "O input: a player name that is not one word is never typed into a command")
    p = page(["*"])
    p.test.put("fail", Bool.TRUE)
    p.run(LINES.index("ahadmin list"))
    K.check(str(p.info).startswith("-/ahadmin list could not be run"), "O: a failed dispatch says so")

    # ---------------- the page itself
    p = page(["*"])
    br.put("auction:count", JClass("java.lang.Long")(12))
    br.put("bazaar:products", "a,b,c")
    for tb in range(4):
        p.tab = tb
        p.pg = 0
        cmds, ev = build(p)
        want = [i for i in range(N) if TABS[i] == tb]
        got = btn_ids(cmds)
        K.eq(got, want[:24], "O page: tab %d page 1 draws the first %d of its %d buttons in table order" % (tb, min(24, len(want)), len(want)))
        tabs_ = [t for s_, t, d in cmds if s_ == "#SkyyOpsTabs"]
        K.eq(len(tabs_), 4, "O page: 4 tabs")
        K.check(("#SkyyOpsTab%d " % tb) in [t for t in tabs_ if "Primary" in t][0], "O page: tab %d drawn selected" % tb)
        helps = [d for s_, t, d in cmds if re.match(r"#SkyyOpsH\d+\.Text", s_)]
        K.eq(len(helps), len(got), "O page: one help text per button")
        K.check(any("TextField #SkyyOpsArg " in t for s_, t, d in cmds), "O page: the Text box is drawn")
        if len(want) > 24:
            p.pg = 1
            c2, _e = build(p)
            K.eq(btn_ids(c2), want[24:48], "O page: tab %d page 2 = the rest" % tb)
            K.check("Page 2 of %d" % ((len(want) + 23) // 24) in sets(c2, "#SkyyOpsPage.Text"), "O page: page label %s" % sets(c2, "#SkyyOpsPage.Text"))
            p.pg = 9
            c9, _e = build(p)
            K.eq(int(p.pg), (len(want) + 23) // 24 - 1, "O page: a page past the end clamps to the last")
    p.tab = 1
    p.pg = 0
    cmds, _ev = build(p)
    _hs = [d for s_, t, d in cmds if s_.startswith("#SkyyOpsH")]
    K.check("/ahadmin list - 12 open" in _hs and "/ahadmin" in _hs, "O status: AH listings shows auction:count, AH status is plain (%s)" % _hs[:3])
    K.check(any("/bazaaradmin info <item id> - 3 items" == x for x in [d for s_, t, d in cmds if s_.startswith("#SkyyOpsH")]), "O status: Bazaar item info shows bazaar:products")
    K.check(any(x == "Alpha  (1 of 3)" for x in sets(cmds, "#SkyyOpsPName.Text")) or any(x.startswith("Skyy  (2 of 3)") for x in sets(cmds, "#SkyyOpsPName.Text")),
            "O picker: name + position shown (%s)" % sets(cmds, "#SkyyOpsPName.Text"))
    p.arg = "Oak_Log"
    cmds, _ev = build(p)
    K.eq(sets(cmds, "#SkyyOpsArg.Value"), ["Oak_Log"], "O page: the Text box keeps its value through a redraw")
    # Diagnostics
    p.tab = 3
    for m, v in pins:
        p.test.put("ver:" + m, v if m != "SkyyMenu" else VERSION)
    p.test.remove("ver:SkyyUiProbeB")
    p.test.put("ver:SkyyHud", "9.9")
    cmds, _ev = build(p)
    info = [d for s_, t, d in cmds if re.match(r"#SkyyOpsI\d+\.Text", s_)]
    K.check(info and info[0].startswith("Skyy mods running: %d of the %d" % (len(pins) - 1, len(pins))), "O diag: %s" % info[:1])
    K.check(any("Not running: SkyyUiProbeB" in x for x in info), "O diag: a missing mod is named")
    K.check(any("SkyyHud 9.9 (set " in x for x in info), "O diag: another version is named")
    K.check(any(x == "Players online: 3" for x in info) and any(x == "Auction House: 12 open" for x in info), "O diag: players + AH count: %s" % info)
    K.check(all(len(x) <= int(OP.LINE_MAX) + 1 for x in info), "O diag: info lines cut at %d characters" % int(OP.LINE_MAX))
    for m, _v in pins:
        p.test.remove("ver:" + m)
    cmds, _ev = build(p)
    info = [d for s_, t, d in cmds if re.match(r"#SkyyOpsI\d+\.Text", s_)]
    K.check(len(info) >= 3 and info[1].startswith("Not running:") and info[2].startswith("    "), "O diag: a long Not running list wraps (%s)" % info[:3])
    K.check(3 * int(OP.ROW_H) + len(info) * int(OP.LINE_H) <= int(OP.WELL_H), "O diag: the info lines fit the well")
    # an admin with one node sees only their tab's buttons and an empty-tab note elsewhere
    p = page(["skyyauctions.admin"])
    p.tab = 0
    cmds, _ev = build(p)
    K.eq(btn_ids(cmds), [], "O page: a tab with no button for the viewer draws none")
    K.check(any(d.startswith("No button on this tab") for s_, t, d in cmds if s_.startswith("#SkyyOpsI")), "O page: ... and says why")
    # clicks: tabs, paging, picker, clear, footer seams
    p = page(["*"])
    click(p, '{"a":"ot2","@OpsArg":"Abc"}')
    K.check(int(p.tab) == 2 and str(p.arg) == "Abc", "O click: a tab click switches and keeps the Text box")
    click(p, '{"a":"gnext"}')
    click(p, '{"a":"gnext"}')
    cmds, _ev = build(p)
    K.eq(int(p.pg), 1, "O click: Next > twice on a 2-page tab stays on page 2")
    click(p, '{"a":"gprev"}')
    click(p, '{"a":"gprev"}')
    K.eq(int(p.pg), 0, "O click: < Prev stops at page 1")
    p.pick = "Alpha"
    click(p, '{"a":"pprev"}')
    K.eq(str(p.pick), "zed", "O picker: < wraps around")
    click(p, '{"a":"clr","@OpsArg":"Abc"}')
    K.eq(str(p.arg), "", "O click: Clear empties the Text box")
    for a_, w_ in (("menu", "menu"), ("setup", "setup"), ("close", "close")):
        p = page(["*"])
        click(p, '{"a":"%s"}' % a_)
        K.eq(str(p.test.get("went")), w_, "O click: %s" % a_)
    p = page(["*"])
    click(p, '{"a":"op99999"}')
    click(p, '{"a":"opx"}')
    click(p, 'garbage')
    K.eq(ran(p), [], "O click: unknown / broken payloads run nothing")
    p = page(["*"])
    cmds, ev = build(p)
    nb = -1
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is not None and JClass("java.util.Collection").class_.isInstance(v_):
            nb = int(v_.size())
    K.check(nb >= 24 + 4 + 3 + 5, "O page: every button is bound (%d bindings)" % nb)
    # the default pick = the viewer
    p0 = OP(pr, 0)
    K.eq(str(p0.pick), "Skyy", "O picker: starts on the viewer")
    K.eq(int(p0.tab), 0, "O: opens on Server")

    # ---------------- Server Setup's Admin button + /modconfig admin (bytecode)
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    PS = JClass("java.io.PrintStream")
    BOS = JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        out_ = []
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out_.append(str(bos.toString()))
        return "\n".join(out_)
    dl = code("AdminPage", "drawList")
    K.check('"SkyyAdmOps"' in dl and '"aops"' in dl and '"Admin"' in dl and "spc" in dl, "O setup: drawList draws the Admin button and binds aops")
    K.check(dl.count("ldc") > 0 and "140" not in re.findall(r"bipush (\d+)", dl) + re.findall(r"sipush (\d+)", dl), "O setup: the 140 px spacer is gone")
    cv = code("AdminPage", "clickView")
    K.check('"aops"' in cv and "openOps" in cv, "O setup: clickView opens the Admin page on aops")
    oo = code("AdminPage", "openOps")
    K.check("OpsPage.<init>" in oo and "openCustomPage" in oo, "O setup: openOps opens a new OpsPage (no close first)")
    ex = code("AdminModCmd", "execute")
    K.check('"admin"' in ex and "OpsPage.openFor" in ex and "equalsIgnoreCase" in ex, "O /modconfig admin opens the Admin page")
    of = code("OpsPage", "openFor")
    K.check("openCustomPage" in of and "OpsPage.<init>" in of, "O openFor opens the page on the command's thread")
    hd = code("OpsPage", "dispatch")
    K.check("CommandManager.handleCommand" in hd, "O dispatch goes through CommandManager.handleCommand")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("ops", run_ops), ("shards", T22.run_shards), ("tabs", T21.run_tabs), ("name", T20.run_name), ("live", T19.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
