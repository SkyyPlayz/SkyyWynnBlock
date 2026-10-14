"""SkyyTrees 0.3.6 - bare-JVM harness for LIFELONG TOOL PERKS (tools/trees_0_3_6_patch.py). Child JVMs run the game's own JRE with the
cached HytaleServer.jar copy (tools/serverjar.py) on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the
scratch folder. The live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyTrees/test_skyytrees_0.3.6.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyTrees-0.3.6.jar] [--prev SkyyTrees-0.3.5.jar] [--gear SkyyGear/SkyyGear-0.3.1.jar] [--live <Skyy_SkyyTrees folder>]

SECTIONS
  A   every class of both jars loads, verifies (-Xverify:all) and initialises (own class loader each)
  CC  CLASS COMPARE 0.3.5 -> 0.3.6 (javassist text of every method): no class added / removed; new fields only TreeAbil.LL* (+ the config
      kit's CfgRows.BRIDGE - tools/skyycfg.py changed since 0.3.5, not this patch); structural changes only in the methods this patch
      names (TreeAbil new methods + <clinit>, TreeGather.run, the TreeTick tick, TreeSaver.retainOnline, the plugin setup / shutdown) and
      the kit's Cfg* classes; the engine 0.7.1 owner moves (ChunkStore -> ChunkGrid) are constant-only
  JT  jar: manifest = 0.3.5's but the version; every asset = 0.3.5's except the vanilla-derived chop chain (Assets.zip of the 2026-10-13
      game update: vanilla Hatchet_Chop names Trigger_Explosion_State_Generic) - listed, not failed
  PK  EXECUTED (new jar; config = a scratch copy of the live trees.properties): the perk read / stack / cap / other tool / retired /
      wrong kind / switches / cache (hit, expiry, profile drop) / bridge throws / SkyyGear absent; llTotal; gear:perk:readers merge +
      removal; heldMd with no hand; TreeGather.run on an ore and a trunk with the stand-in player (the new lines run, nothing breaks);
      and the REAL SkyyGear 0.3.1 GearLLFn (gear:fn:lifelong / gear:fn:perk, its registry in memory) feeding the real SkyyTrees reader,
      plus SkyyGear's own GearLL.perkOn turning on for vein / fell once SkyyTrees published its readers
  ZN  the 0.3.5 harness's Monk "Zen" text child on both jars: identical texts
  ST  START TWICE on a scratch COPY of Skyy's live Skyy_SkyyTrees (the 0.3.4 harness's start routine): 0.3.6 = 0.3.5, start 2 nothing
  Z   the engine-access audit (MethodHandles lookups, the 0.3.1 harness's run_audit) on the 0.3.6 jar: 0 refused
  CF  (--cf, ~5 min) CARRY-FORWARD: the 0.3.4 harness (+ its H33 = the 0.3.3 harness, 467,000+ checks) on the 0.3.6 jar next to the control
      run on the 0.3.5 jar. A test-only sitecustomize in the scratch folder points those older harnesses at the installed Assets.zip (they
      look next to SERVER_JAR, now a cached copy - tools/serverjar.py). Only these may fail beyond the control: its class-shape checks (F),
      the H33 jar-shape line, and the chop-chain checks J / E3 that follow the 2026-10-13 Assets.zip (vanilla Hatchet_Chop changed)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.6", "0.3.5"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "perksfix", "trees036")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
GEAR_JAR = os.path.abspath(arg("--gear", os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.1.jar")))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
MODS_LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods")
LIVE = os.path.abspath(arg("--live", os.path.join(MODS_LIVE, "Skyy_SkyyTrees")))
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def sk():
    return _mod(SKILLS_HARNESS, "ts0427")


def t35():
    return _mod(os.path.join(HERE, "test_skyytrees_0.3.5.py"), "tt035")


def t34():
    return _mod(os.path.join(HERE, "test_skyytrees_0.3.4.py"), "tt034")


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child: PK (the new jar)
def run_pk(jar, gear, home, out):
    from jpype import JClass, JArray, JString, JImplements, JOverride
    H = t34().t33().H
    H.SCRATCH = SCRATCH
    H._jvm_start([], [])
    U, setf, _ByTree, me, pr = H._stand_ins()
    S = sk()
    R = {"checks": [], "notes": []}

    def ck(cond, what):
        R["checks"].append([bool(cond), what])

    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()

    def loader(j):
        urls = JArray(URL)(1)
        urls[0] = File(j).toURI().toURL()
        return URLCL(urls, sysl)
    try:
        ld = loader(jar)
        R["classes"], R["load_fails"] = S.load_all(jar, ld)
        C = lambda n: JClass(PKG + n, loader=ld)
        Cfg, Sto, Abil, Fx, Calc, Defs, Gat = (C("TreeCfg"), C("TreeStore"), C("TreeAbil"), C("TreeFx"), C("TreeCalc"), C("TreeDefs"),
                                               C("TreeGather"))
        Paths = JClass("java.nio.file.Paths")
        b = Paths.get(home)
        Cfg.FILE = b.resolve("trees.properties")
        Sto.DIR = b.resolve("players")
        R["load"] = str(Cfg.load())
        ids = [str(x) for x in Defs.ID]
        iV, iF = ids.index("MVein"), ids.index("FFeller")
        Int, Long, Obj = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Object")
        BD, BI, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonString")
        br = Sto.bridge()
        for k in ("gear:fn:lifelong", "gear:fn:perk", "gear:perk:readers"):
            br.remove(k)

        def md(lu=None, ll=1, lrt=None, gear_doc=True):
            m = BD()
            if not gear_doc:
                m.put("SkyyRolls", BD())
                return m
            g = BD()
            if ll is not None:
                g.put("ll", BI(ll))
            if lu is not None:
                g.put("lu", BS(lu))
            if lrt is not None:
                g.put("lrt", BI(lrt))
            g.put("lvl", BI(20))
            m.put("SkyyGear", g)
            return m

        d = Sto.data(me)
        base, per = float(Cfg.BASE[iV]), float(Cfg.PER[iV])
        logs = [int(x) for x in Cfg.FELLER_LOGS]
        fall = int(Cfg.FELLER_ALL)
        R["notes"].append("config: Vein Burst base %s per %s max %d; feller.logs %s (cap %d); Tree Feller max %d"
                          % (base, per, int(Cfg.MAX[iV]), logs, fall, int(Cfg.MAX[iF])))

        def vein_val(lv):
            return 0.0 if lv <= 0 else base + per * lv

        def fell_val(lv):
            return 0.0 if lv <= 0 else float(min(logs[min(lv, len(logs)) - 1], fall))

        def setlv(i, lv):
            d.lv[i] = lv

        def val(i, k, m):
            cur = float(Fx.value(i, Calc.eff(d, i)))
            return float(Abil.llValue(me, i, k, cur, m)), cur

        # ---- llUid
        ck(str(Abil.llUid(md("P1"))) == "P1", "PK llUid: a lifelong document's uid")
        ck(Abil.llUid(md("P1", lrt=1)) is None, "PK llUid: a RETIRED lifelong tool (lrt=1) = none")
        ck(Abil.llUid(md("P1", ll=0)) is None and Abil.llUid(md("P1", ll=None)) is None, "PK llUid: ll 0 / missing = none")
        ck(Abil.llUid(md(None)) is None and Abil.llUid(md("")) is None, "PK llUid: no / empty uid = none")
        ck(Abil.llUid(md(gear_doc=False)) is None and Abil.llUid(None) is None, "PK llUid: no SkyyGear document / no metadata = none")
        bad = BD()
        bad.put("SkyyGear", BS("x"))
        ck(Abil.llUid(bad) is None, "PK llUid: SkyyGear key that is no document = none")

        # ---- llTotal (cap 8, a tree level above 8 kept)
        tt = [(e, p, int(Abil.llTotal(e, p))) for e, p in ((0, 0), (3, 0), (0, 3), (3, 3), (5, 3), (6, 3), (6, 2), (10, 2), (9, 0), (2, -1))]
        ck([x[2] for x in tt] == [0, 3, 3, 6, 8, 8, 8, 10, 9, 2], "PK llTotal: tree + tool capped at 8: %s" % tt)

        # ---- SkyyGear absent: the tree alone, whatever the tool says
        setlv(iV, 3)
        setlv(iF, 2)
        Abil.LLC.clear()
        n0 = [int(x) for x in Abil.LLN]
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur == vein_val(3), "PK SkyyGear absent: Vein Burst = the tree alone (%s / %s)" % (v, cur))
        v, cur = val(iF, 1, md("H1"))
        ck(v == cur == fell_val(2), "PK SkyyGear absent: Tree Feller = the tree alone (%s / %s)" % (v, cur))
        ck(int(Abil.LLN[0]) == n0[0] + 2 and int(Abil.LLN[2]) == n0[2], "PK SkyyGear absent: asked once per kind, nothing boosted")

        # ---- the fake SkyyGear (the 0.3.1 GearLLFn contract) with call counters
        calls = {"lifelong": 0, "perk": 0}
        table = {"uid": {"pickaxe": "P1", "hatchet": "H1"}, "perk": {"pickaxe|vein": 3, "hatchet|fell": 3}, "throw": False}

        @JImplements("java.util.function.Function")
        class LifeFn(object):
            @JOverride
            def apply(self, o):
                calls["lifelong"] += 1
                if table["throw"]:
                    raise RuntimeError("boom")
                u = table["uid"].get(str(o[1]))
                return JString(u) if u else None

        @JImplements("java.util.function.Function")
        class PerkFn(object):
            @JOverride
            def apply(self, o):
                calls["perk"] += 1
                return Int.valueOf(int(table["perk"].get("%s|%s" % (o[1], o[2]), 0)))
        br.put("gear:fn:lifelong", LifeFn())
        br.put("gear:fn:perk", PerkFn())
        Abil.LLC.clear()

        # stack
        v, cur = val(iV, 0, md("P1"))
        ck(v == vein_val(3) + 3 and cur == vein_val(3), "PK stack: Vein Burst tree 3 + pickaxe Vein Mine 3 = the tree's number + 3 ore (%s, tree alone %s)" % (v, cur))
        v, cur = val(iF, 1, md("H1"))
        ck(v == fell_val(5) and cur == fell_val(2), "PK stack: Tree Feller tree 2 + hatchet 3 = level 5 = %s logs (tree alone %s)" % (v, cur))
        ck(calls == {"lifelong": 2, "perk": 2}, "PK read: one lifelong + one perk ask per kind: %s" % calls)
        # cache hits: no new asks
        for _ in range(20):
            val(iV, 0, md("P1"))
            val(iF, 1, md("H1"))
        ck(calls == {"lifelong": 2, "perk": 2} and int(Abil.LLN[1]) >= 40, "PK cache: 40 more breaks inside 5 s ask SkyyGear nothing (%s, hits %d)" % (calls, int(Abil.LLN[1])))
        # cap
        setlv(iV, 5)
        setlv(iF, 6)
        v, _c = val(iV, 0, md("P1"))
        ck(v == vein_val(5) + 3, "PK cap: Vein Burst tree 5 + 3 = level 8 = the tree's number + 3 ore (%s)" % v)
        v, cur = val(iF, 1, md("H1"))
        ck(v == fell_val(8) and cur == fell_val(6), "PK cap: Tree Feller tree 6 + 3 = 9 -> 8 = %s logs (tree alone %s; feller.logs %s)" % (v, cur, logs))
        # tree level 0: the tool alone
        setlv(iV, 0)
        setlv(iF, 0)
        v, cur = val(iV, 0, md("P1"))
        ck(v == 3.0 and cur == 0.0, "PK tool alone: no tree level + Vein Mine 3 = 3 extra ore (the lock) (%s)" % v)
        v, cur = val(iF, 1, md("H1"))
        ck(v == fell_val(3) and cur == 0.0, "PK tool alone: no tree level + Tree Feller 3 = level 3 = %s logs" % v)
        # FIX 1 (critic HIGH; docs/answered/gear.md LOCKED 2026-10-10 "lvl 1 breaks 1 extra block. lvl 2 breaks 2 and so on. capped at 8"):
        # each Vein Mine level adds exactly ONE ore; the total level never passes 8
        lock = []
        mx0 = int(Cfg.MAX[iV])
        Cfg.MAX[iV] = 8   # an admin max of 8 so tree levels 7 / 8 reach the cap
        for tl in (0, 2, 5, 7, 8):
            setlv(iV, tl)
            for pkl in (1, 2, 3):
                Abil.LLC.clear()
                table["perk"]["pickaxe|vein"] = pkl
                v, cur = val(iV, 0, md("P1"))
                lock.append((tl, pkl, v - cur))
        table["perk"]["pickaxe|vein"] = 3
        Cfg.MAX[iV] = mx0
        Abil.LLC.clear()
        want = [(tl, pkl, float(max(0, min(pkl, 8 - tl)))) for tl in (0, 2, 5, 7, 8) for pkl in (1, 2, 3)]
        ck(lock == want, "FIX1 Vein Mine lock: tool level N = N extra ore on top of the tree, total level capped at 8: %s" % lock)
        setlv(iV, 0)
        Abil.LLC.clear()
        v1 = []
        for pkl in (1, 2, 3):
            Abil.LLC.clear()
            table["perk"]["pickaxe|vein"] = pkl
            v1.append(val(iV, 0, md("P1"))[0])
        table["perk"]["pickaxe|vein"] = 3
        Abil.LLC.clear()
        ck(v1 == [1.0, 2.0, 3.0], "FIX1 Vein Mine with no Vein Burst in the tree: level 1 / 2 / 3 = 1 / 2 / 3 extra ore (%s)" % v1)
        # FIX 3 (critic MEDIUM, kept as a question for Skyy): with the locked default feller.logs 1,2,4,5,6,10 a tree Tree Feller 6
        # gets nothing from the hatchet (levels 7 / 8 reuse the last number) - recorded so the behaviour is known, not hidden
        if logs == [1, 2, 4, 5, 6, 10]:
            setlv(iF, 6)
            Abil.LLC.clear()
            v, cur = val(iF, 1, md("H1"))
            setlv(iF, 4)
            Abil.LLC.clear()
            v4, cur4 = val(iF, 1, md("H1"))
            ck(v == cur == 10.0 and cur4 == 5.0 and v4 == 10.0,
               "FIX3 default feller.logs: tree 6 + hatchet 3 = 10 logs (no gain); tree 4 + 3 = 10 (tree alone 5) (%s/%s, %s/%s)" % (v, cur, v4, cur4))
            R["notes"].append("FIX3: default feller.logs ends at level 6 - the hatchet's Tree Feller adds nothing above tree level 5 (question for Skyy)")
        else:
            R["notes"].append("FIX3: live feller.logs is not the default (%s) - the default-table check skipped" % logs)
        setlv(iV, 3)
        setlv(iF, 2)
        Abil.LLC.clear()
        # not the lifelong tool / wrong kind / retired / plain
        cases = [("another player's / old lifelong pickaxe", iV, 0, md("ZZ")), ("the hatchet uid on an ore", iV, 0, md("H1")),
                 ("the pickaxe uid on a log", iF, 1, md("P1")), ("a retired lifelong pickaxe", iV, 0, md("P1", lrt=1)),
                 ("a plain SkyyGear tool (ll 0)", iV, 0, md("P1", ll=0)), ("a SkyyRolls-only tool", iV, 0, md(gear_doc=False)),
                 ("no metadata (vanilla tool / bare hand)", iV, 0, None)]
        for what, i, k, m in cases:
            v, cur = val(i, k, m)
            ck(v == cur, "PK ignored: %s = the tree alone (%s / %s)" % (what, v, cur))
        # switches
        Cfg.EN[iV] = False
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur == 0.0, "PK switch: Vein Burst switched off by the admin stays off with the tool (%s)" % v)
        Cfg.EN[iV] = True
        d.off[iF] = True
        v, cur = val(iF, 1, md("H1"))
        ck(v == cur == 0.0, "PK switch: Tree Feller the player switched off stays off with the tool (%s)" % v)
        d.off[iF] = False
        # perk change: cached for up to 5 s, then read again; profile drop
        pa = calls["perk"]
        table["perk"]["pickaxe|vein"] = 1
        v, _c = val(iV, 0, md("P1"))
        ck(v == vein_val(3) + 3, "PK cache: a perk change is not seen inside the 5 s window (%s)" % v)
        row = Abil.LLC.get(me)
        e = row[0]
        e[2] = Long.valueOf(0)
        v, _c = val(iV, 0, md("P1"))
        ck(v == vein_val(3) + 1 and calls["perk"] == pa + 1, "PK cache: an expired entry is read again (Vein Mine 1: tree + 1 ore = %s; perk asks %d)" % (v, calls["perk"]))
        # an entry that claims to live longer than the TTL (clock moved back) is read again too
        row = Abil.LLC.get(me)
        row[0][2] = Long.valueOf(JClass("java.lang.System").currentTimeMillis() + 3600000)
        val(iV, 0, md("P1"))
        ck(calls["perk"] == pa + 2, "PK cache: an entry further than 5 s ahead (clock moved back) is read again")
        Abil.LLC.remove(me)
        table["uid"]["pickaxe"] = "P2"
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur, "PK profile switch: after the cache drop the old profile's pickaxe P1 no longer counts")
        v, _c = val(iV, 0, md("P2"))
        ck(v == vein_val(3) + 1, "PK profile switch: the new profile's pickaxe P2 counts (%s)" % v)
        table["uid"]["pickaxe"] = "P1"
        # perk numbers out of range
        Abil.LLC.clear()
        table["perk"]["pickaxe|vein"] = 12
        v, _c = val(iV, 0, md("P1"))
        ck(v == vein_val(3) + 5, "PK clamp: a perk answer of 12 -> total level 8 = tree 3 + 5 ore (%s)" % v)
        Abil.LLC.clear()
        table["perk"]["pickaxe|vein"] = -4
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur, "PK clamp: a negative perk answer = 0")
        table["perk"]["pickaxe|vein"] = 3
        # no lifelong pickaxe registered: perk never asked
        Abil.LLC.clear()
        table["uid"]["pickaxe"] = None
        p0 = calls["perk"]
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur and calls["perk"] == p0, "PK no lifelong pickaxe in SkyyGear: the tree alone, perk not asked")
        table["uid"]["pickaxe"] = "P1"
        # the bridge throws
        Abil.LLC.clear()
        table["throw"] = True
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur, "PK a throwing SkyyGear bridge = the tree alone, no exception")
        table["throw"] = False
        # only one of the two functions
        Abil.LLC.clear()
        br.remove("gear:fn:perk")
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur, "PK only gear:fn:lifelong present (old SkyyGear) = the tree alone")
        br.put("gear:fn:perk", PerkFn())
        # a value no larger than the tree's own (admin max above 8) is never lowered
        Abil.LLC.clear()
        mx = int(Cfg.MAX[iV])
        Cfg.MAX[iV] = 10
        setlv(iV, 10)
        v, cur = val(iV, 0, md("P1"))
        ck(v == cur == vein_val(10), "PK admin max 10: a tree level 10 is kept (never cut to 8) (%s)" % v)
        Cfg.MAX[iV] = mx
        setlv(iV, 3)

        # ---- heldMd + TreeGather.run with the stand-in player (no hand -> the tree alone; the new lines run)
        ck(Abil.heldMd(None) is None and Abil.heldMd(pr) is None, "PK heldMd: no player / no entity reference = none")
        BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")

        def block(i_):
            bt = U.allocateInstance(BTY.class_)
            c_ = BTY.class_
            while c_ is not None:
                try:
                    f_ = c_.getDeclaredField("id")
                    f_.setAccessible(True)
                    f_.set(bt, JString(i_))
                    break
                except Exception:
                    c_ = c_.getSuperclass()
            return bt
        ore, log = block("Ore_Iron_Stone"), block("Wood_Oak_Trunk")
        ck(str(Defs.bid(ore)) == "Ore_Iron_Stone" and str(Defs.bid(log)) == "Wood_Oak_Trunk", "PK stand-in blocks carry their ids")
        Abil.LLC.clear()
        n1 = [int(x) for x in Abil.LLN]
        err = None
        try:
            Gat.run(pr, 0, ore, "default", False, 10, 40, 10)
            Gat.run(pr, 1, log, "default", False, 12, 41, 12)
            Gat.run(pr, 0, ore, "default", True, 10, 40, 10)
        except Exception as ex:
            err = str(ex)[:400]
        ck(err is None and not bool(Gat.FAILED_ONCE), "PK TreeGather.run on an ore and a trunk (stand-in player, no hand): no error %s" % err)
        ck([int(x) for x in Abil.LLN] == n1, "PK TreeGather.run with nothing in hand asks SkyyGear nothing (%s -> %s)" % (n1, [int(x) for x in Abil.LLN]))

        # ---- gear:perk:readers
        rw = lambda c, a: str(Abil.readersWith(c, a))
        ck(rw(None, True) == "vein,fell" and rw("", True) == "vein,fell" and rw("x", True) == "x,vein,fell"
           and rw("vein,fell", True) == "vein,fell" and rw(" x , vein ,fell,y", False) == "x,y" and rw("vein,fell", False) == ""
           and rw("fell,smelt", True) == "smelt,vein,fell", "PK readersWith: merge without duplicates, removal keeps other words")
        br.remove("gear:perk:readers")
        Abil.readers(True)
        r1 = br.get("gear:perk:readers")
        br.put("gear:perk:readers", JString("smelt"))
        Abil.readers(True)
        r2 = br.get("gear:perk:readers")
        Abil.readers(False)
        r3 = br.get("gear:perk:readers")
        br.put("gear:perk:readers", JString("vein,fell"))
        Abil.readers(False)
        r4 = br.containsKey("gear:perk:readers")
        br.put("gear:perk:readers", Int.valueOf(5))
        Abil.readers(True)
        r5 = br.get("gear:perk:readers")
        br.remove("gear:perk:readers")
        ck(str(r1) == "vein,fell" and str(r2) == "smelt,vein,fell" and str(r3) == "smelt" and not r4 and str(r5) == "5",
           "PK readers: publish / merge / remove / a non-text value left alone: %s %s %s %s %s" % (r1, r2, r3, r4, r5))

        # ---- the REAL SkyyGear 0.3.1 read side
        if os.path.isfile(gear):
            gl = loader(gear)
            G = lambda n: JClass("com.skyy.gear." + n, loader=gl)
            try:
                GLL, GCfg, GFn = G("GearLL"), G("GearCfg"), G("GearLLFn")
            except Exception:
                pk_ = [n for n in zipfile.ZipFile(gear).namelist() if n.endswith("/GearLL.class")]
                pre = pk_[0][:-len("GearLL.class")].replace("/", ".") if pk_ else "com.skyy.gear."
                G = lambda n: JClass(pre + n, loader=gl)
                GLL, GCfg, GFn = G("GearLL"), G("GearCfg"), G("GearLLFn")
            GCfg.LL_ON = True
            P = JClass("java.util.Properties")()
            P.setProperty("pickaxe.uid", "GP")
            P.setProperty("pickaxe.up.vein", "2")
            P.setProperty("hatchet.uid", "GH")
            P.setProperty("hatchet.up.fell", "3")
            P.setProperty("pickaxe.up.spd", "4")
            GLL.REG.put(str(me.toString()), P)
            br.put("gear:fn:lifelong", GFn(0))
            br.put("gear:fn:perk", GFn(1))
            Abil.LLC.clear()
            setlv(iV, 3)
            setlv(iF, 6)
            v, cur = val(iV, 0, md("GP"))
            ck(v == vein_val(3) + 2 and cur == vein_val(3), "PK REAL SkyyGear: lifelong pickaxe GP with Vein Mine 2 + tree 3 = tree + 2 ore (%s)" % v)
            v, cur = val(iF, 1, md("GH"))
            ck(v == fell_val(8), "PK REAL SkyyGear: lifelong hatchet GH Tree Feller 3 + tree 6 -> 8 = %s logs" % v)
            v, cur = val(iV, 0, md("GH"))
            ck(v == cur, "PK REAL SkyyGear: the hatchet on an ore = the tree alone")
            v, cur = val(iV, 0, md("XX"))
            ck(v == cur, "PK REAL SkyyGear: a tool that is not the registered lifelong one = the tree alone")
            Abil.LLC.clear()
            GCfg.LL_ON = False
            v, cur = val(iV, 0, md("GP"))
            ck(v == cur, "PK REAL SkyyGear: Lifelong tools switched off (part.lifelong) = the tree alone")
            GCfg.LL_ON = True
            br.remove("gear:perk:readers")
            before = [bool(GLL.perkOn(3)), bool(GLL.perkOn(4))]
            Abil.readers(True)
            after = [bool(GLL.perkOn(3)), bool(GLL.perkOn(4)), bool(GLL.perkOn(0))]
            ck(before == [False, False] and after == [True, True, True],
               "PK REAL SkyyGear: GearLL.perkOn(Vein Mine / Tree Feller) false before, true after SkyyTrees published its readers: %s -> %s" % (before, after))
            Abil.readers(False)
            ck([bool(GLL.perkOn(3)), bool(GLL.perkOn(4))] == [False, False], "PK REAL SkyyGear: perkOn false again after the shutdown removal")
        else:
            ck(False, "PK REAL SkyyGear: no jar at %s" % gear)
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-3000:]
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


def run_load(jar, out):
    S = sk()
    S.jvm_start()
    R = {}
    R["classes"], R["load_fails"] = S.load_all(jar, S.loader(jar))
    json.dump(R, open(out, "w"))
    os._exit(0)


# ============================================================================================ parent
SHIM = r'''import zipfile, os
_REAL = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
_Orig = zipfile.ZipFile.__init__
def _init(self, file, *a, **k):
    if isinstance(file, str):
        n = file.replace(chr(92), "/").lower()
        if n.endswith("/../assets.zip") and "serverjar" in n:
            file = _REAL
    return _Orig(self, file, *a, **k)
zipfile.ZipFile.__init__ = _init
'''


def carry_forward(env):
    shim = os.path.join(SCRATCH, "cf-shim")
    os.makedirs(shim, exist_ok=True)
    open(os.path.join(shim, "sitecustomize.py"), "w").write(SHIM)
    e2 = dict(env)
    e2["PYTHONPATH"] = shim
    res = {}
    for tag, j in (("new", JAR), ("ctl", PREV_JAR)):
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyytrees_0.3.4.py"), "--jar", j, "--dir", os.path.join(SCRATCH, "cf-" + tag)],
                           env=e2, capture_output=True, encoding="utf8", errors="replace")
        t = p.stdout or ""
        res[tag] = (set(l[5:].strip() for l in t.splitlines() if l.startswith("FAIL ")), t)
    extra = sorted(res["new"][0] - res["ctl"][0])
    hn = re.search(r"H33: the 0\.3\.3 harness on the 0\.3\.4 jar: (\d+) passed", res["new"][1])
    hc = re.search(r"H33: the 0\.3\.3 harness on the 0\.3\.4 jar: (\d+) passed", res["ctl"][1])

    def expected(f):
        return (f.startswith("F: ") or f.startswith("H33: the 0.3.3 harness on the 0.3.4 jar:")
                or f == "J: every 0.3.4 file re-inlined = 0.3.3's file text exactly: ['Skyy_Tree_Chop']"
                or re.match(r"E3: (Hatchet_Attack|SkyyHarness_Skyy_Tree_\w+): the name-free fingerprint", f) is not None)
    bad = [f for f in extra if not expected(f)]
    check(hn and hc and int(hn.group(1)) > 400000 and int(hc.group(1)) - int(hn.group(1)) <= 1,
          "CF: H33 behaviour checks on 0.3.6 = the control's (0.3.6 %s, 0.3.5 %s passed; the 1 = its byte-identical template classes line)"
          % (hn.group(1) if hn else "?", hc.group(1) if hc else "?"))
    check(not bad, "CF: beyond the 0.3.5 control only class-shape / chop-chain (Assets.zip update) checks fail: unexpected %s" % [b[:240] for b in bad])
    for f in extra:
        print("CF expected: " + f[:260])


def main():
    if "--pk" in sys.argv:
        return run_pk(arg("--pk"), arg("--gear"), arg("--home"), arg("--out"))
    if "--load" in sys.argv:
        return run_load(arg("--load"), arg("--out"))
    if "--zn" in sys.argv:
        return t35().run_zn(arg("--zn"), arg("--home"), arg("--out"))
    if "--cc" in sys.argv:
        return sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--audit" in sys.argv:
        H = t34().t33().H
        H.SCRATCH = SCRATCH
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
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

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        # ---- A
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            r = child(["--load", j], os.path.join(SCRATCH, "load-%s.json" % tag)) or {}
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30,
                  "A (%s): %s classes load, verify (-Xverify:all), initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        # ---- CC
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText"}
            fnew = dict((c, v["fields_new"]) for c, v in cls_.items() if (v["fields_new"] or v["fields_gone"]) and c not in KIT)
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not cc["added"] and not cc["gone"] and not gone and all(v["same_shape"] for v in cls_.values()),
                  "CC: no class added / removed, no field removed, same supers / interfaces: %s %s %s" % (cc["added"], cc["gone"], gone))
            want_f = sorted(["LLC:Ljava/util/concurrent/ConcurrentHashMap;", "LLCAP:I", "LLKIND:[Ljava/lang/String;", "LLN:[J",
                             "LLPERK:[Ljava/lang/String;", "LLTTL:J"])
            check(fnew == {"TreeAbil": want_f}, "CC: new fields only TreeAbil.LL* (kit classes aside): %s" % fnew)
            struct = dict((c, sorted(v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            newm = sorted(m.split("(")[0] for m in struct.get("TreeAbil", []) if m.endswith("(new)"))
            check(newm == sorted(["llUid", "llEntry", "llPerk", "llTotal", "llValue", "heldMd", "readersWith", "readers"]),
                  "CC: TreeAbil's new methods = the perk reader: %s" % newm)
            other = dict((c, [m.split("(")[0] for m in ms if not m.endswith("(new)")]) for c, ms in struct.items())
            check(other.get("TreeAbil") == ["<clinit>"] and other.get("TreeGather") == ["run"] and other.get("TreeSaver") == ["retainOnline"]
                  and sorted(other.get("SkyyTreesPlugin", [])) == ["setup", "shutdown"] and list(other.get("TreeTick", [])) and len(other["TreeTick"]) == 1
                  and set(other) - {"TreeDefs"} == {"TreeAbil", "TreeGather", "TreeSaver", "SkyyTreesPlugin", "TreeTick"}
                  and other.get("TreeDefs", ["<clinit>"]) == ["<clinit>"],
                  "CC: structural changes only where the patch says (TreeAbil <clinit>, TreeGather.run, TreeTick tick, TreeSaver.retainOnline, plugin setup / shutdown): %s" % other)
            if "TreeDefs" in other:
                # the build reads the wood families from Assets.zip: the 2026-10-13 game update added Sadwillow trees
                import skyybuild as SB
                azp = os.path.join(SB.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
                with zipfile.ZipFile(azp) as az:
                    sad = [n for n in az.namelist() if n.startswith("Server/Item/Items/") and "/Wood_Sadwillow_Trunk" in n]
                zt = lambda j: zipfile.ZipFile(j).read("com/skyy/trees/TreeDefs.class")
                check(sad and b"Sadwillow" in zt(JAR) and b"Sadwillow" not in zt(PREV_JAR),
                      "CC: TreeDefs.<clinit> differs only by the Assets.zip-derived wood list (the game update's Sadwillow trunk %s)" % sad[:1])
            kitc = dict((c, v["structural"] + v["fields_new"]) for c, v in cls_.items() if c in KIT and (v["structural"] or v["fields_new"]))
            print("CC. 0.3.5 -> 0.3.6 structural: %s; constant-only: %s" % (other, sorted(c for c, v in cls_.items() if v["const_only"])))
            print("CC. NOTE the config kit (tools/skyycfg.py, rebuilt from today's kit) changed: %s" % kitc)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        chop = lambda n: n.startswith("Server/Item/Interactions/SkyyTrees/Skyy_Tree_Chop_N")
        diff = sorted(n for n in (nn | np_) if n != "manifest.json" and (n not in nn or n not in np_ or zj.read(n) != zp.read(n)))
        check(all(chop(n) for n in diff), "JT: assets = 0.3.5's except the vanilla-derived chop chain (game update): %s" % [n for n in diff if not chop(n)])
        print("JT. NOTE vanilla-derived chop files that follow the 2026-10-13 Assets.zip: %s" % diff)
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mp, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.5's but the version")
        # ---- PK
        h = os.path.join(SCRATCH, "pk-home")
        shutil.copytree(LIVE, h)
        pk = child(["--pk", JAR, "--gear", GEAR_JAR, "--home", h], os.path.join(SCRATCH, "pk.json"))
        check(pk is not None and "error" not in pk, "PK ran: %s" % (pk or {}).get("error", "")[-2500:])
        if pk:
            for n in pk.get("notes", []):
                print("PK. " + n)
            for ok, what in pk.get("checks", []):
                check(ok, what)
            print("PK. %d executed checks" % len(pk.get("checks", [])))
            check(len(pk.get("checks", [])) >= 45, "PK: every scenario ran (%d checks)" % len(pk.get("checks", [])))
        # ---- ZN (0.3.5's Monk text child, both jars)
        zr = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            hz = os.path.join(SCRATCH, "zn-" + tag)
            shutil.copytree(LIVE, hz)
            zr[tag] = child(["--zn", j, "--home", hz], os.path.join(SCRATCH, "zn-%s.json" % tag)) or {}
            check("error" not in zr[tag] and zr[tag].get("texts"), "ZN (%s) ran: %s" % (tag, zr[tag].get("error", "")[-1500:]))
        check(zr["new"].get("texts") == zr["prev"].get("texts") and zr["new"].get("cskill") == zr["prev"].get("cskill")
              and zr["new"].get("ckey") == zr["prev"].get("ckey") and (zr["new"].get("cskill") or [""])[-1] == "Zen",
              "ZN: the 0.3.5 checks - Monk = Zen, CSKILL_KEY and every class's tree texts identical to 0.3.5's")
        # ---- ST
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T = t34()
            nz = lambda r: T.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.6 = 0.3.5's (same summary, migrations, changed files): %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.5), start 2 nothing" % sn[0]["changed"])
        # ---- Z
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000 and au.get("classes", 0) >= 30,
                  "Z: engine-access audit of the 0.3.6 jar: %s references in %s classes, 0 refused: %s" % (au.get("refs"), au.get("classes"), str(au.get("refused"))[:600]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control (skyytest.BadAccess) is refused: %s" % str(au.get("control"))[:300])
            print("Z. %s references, %d refused, control refused %d; caller-sensitive %s" % (au.get("refs"), len(au.get("refused") or []),
                                                                                         len(au.get("control") or []), au.get("caller_sensitive")))
        if "--cf" in sys.argv:
            carry_forward(env)
        check(snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
