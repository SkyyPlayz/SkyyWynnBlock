"""SkyyRebirth 0.4.2 - harness (tools/rebirth_0_4_2_patch.py, Balance P8a: the dust.first row hidden, the Nexus hover's worth-per-VP line,
0.3.6's rebirth.max migration re-checked on the live copy).
Build first: python tools/rebirth_0_4_2_patch.py && python SkyyRebirth/build_skyyrebirth_0.4.2.py

    python SkyyRebirth/test_skyyrebirth_0.4.2.py [--dir <empty folder inside tools/dev/scratch/>]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.1 -> 0.4.2: exactly the planned members differ (EXPECT)
  V / P / F41  the WHOLE 0.4.0 + 0.4.1 harness (run_vp / run_page / run_f41) against the 0.4.2 jar
  F42 P8a      EXECUTED: Server Setup has no dust.first row (the other rows unchanged) while loadCfg still reads dust.first and
               rebirth:fn:dustmult answers it; RbTree.worthTxt for Void Insight / Class Echo / Mining Echo / a Hand node / a tool node /
               Head Start / a full node; the REAL page build: the node hovers carry the worth line (XP nodes only); rebirth.max 0 -> a
               profile with 25 rebirths still meets the rebirths requirement (no limit)
  L42 live     a scratch COPY of the live NewBetaTest Skyy_SkyyRebirth started TWICE in setup()'s order (migOn, migMax, loadCfg, CfgPub):
               start 1 = rebirth.max 10 -> 0 (the 0.3.6 migration P8a relies on: value text only, marker under it, one change-log row
               10 -> 0, the old file in config-history, every other byte kept), Max = no limit; start 2 writes nothing
  AA  engine-access audit
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


VERSION = "0.4.2"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.4.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp8afix2", "rb")))
T41 = _load("t_rb041", os.path.join(HERE, "test_skyyrebirth_0.4.1.py"))
T40 = T41.T40
T41.VERSION, T41.JAR = VERSION, JAR
T40.VERSION, T40.JAR = VERSION, JAR
T40.T34.VERSION, T40.T34.JAR = VERSION, JAR
R = T40.R
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyRebirthPlugin": ["~m setup"],   # the version text; the row list (dust.first gone)
    "RbMig": ["~m migrate"], "RbStore": ["~m writeNow"],   # only the @VERSION@ text in the vp-migration.log line / the file comment
    "RbTree": ["~<clinit>", "+f NWORTH", "+f NMIX", "+m worthTxt", "~m keepTxt"],   # fix round 2: the limit on the keep line
    "RbCheck": ["~m gains"],   # fix round: no Dust on the page
    "RbPage": ["~m fillTree"],
}


def run_f42(out, jar, scratch, _home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    Bag, Part, Const = T40.fakes()
    Cfg, St, Tr = R("RbCfg"), R("RbStore"), R("RbTree")
    home, pl, U, k = T40.world(scratch, "f42")
    # ---------------------------------------------------------------- 1. the dust.first row hidden, the key still read
    rows = [str(r[0]) for r in R("CfgRows").header()[7]]
    K.check("dust.first" not in rows and "rebirth.max" in rows and "caps.levels" in rows and "nexus.respecCharms" in rows and len(rows) == 23,
            "F42 Server Setup: no dust.first row, the other 23 rows stay: %s" % rows)
    rmax = [list(r) for r in R("CfgRows").header()[7] if str(r[0]) == "rebirth.max"][0]
    K.check(str(rmax[4]) == "0" and "0 = no limit" in str(rmax[10]), "F42 the Max rebirths row: default 0, help '0 = no limit': %s" % str(rmax[10]))
    cfgf = os.path.join(home, "config.properties")
    open(cfgf, "w").write("dust.first=3\n")
    Cfg.loadCfg(False)
    fd = R("RbFn")(3)
    open(os.path.join(pl, k + ".properties"), "w").write("n=1\nv=4\nvp=0\n")
    St.CACHE.clear()
    K.check(float(Cfg.DUST_FIRST) == 3.0 and abs(float(fd.apply(T40_oa((U, "Mining")))) - 3.0) < 1e-9,
            "F42 the hidden key is still read (dust.first=3 -> DUST_FIRST 3, rebirth:fn:dustmult x3 at rebirth 1)")
    os.remove(cfgf)
    Cfg.loadCfg(False)
    # ---------------------------------------------------------------- 2. worthTxt
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("node.Mining.echo", "1")
    pp.setProperty("node.Hand.farming", "2")
    pp.setProperty("node.Class.echo", "5")
    pp.setProperty("vp", "500")
    I = lambda nid: int(Tr.idx(nid))

    def w(nid):
        c = int(Tr.cost(pp, I(nid)))
        r = Tr.worthTxt(pp, I(nid), c)
        return None if r is None else str(r)
    K.eq(w("Void.insight"), "Worth +0.5 % all XP a VP (keeping: +0.25 % all XP a VP)", "F42 Void Insight rank 1: 6 % / 12 VP")
    K.eq(w("Mining.echo"), "Worth +1.83 % Mining XP a VP (= ~+0.33 % all XP at a usual play mix; keeping: +0.25 %)",
         "F42 FIX1 Mining Echo rank 2: 11 % / 6 VP, x Mining share 0.18 = 0.33 all XP (spec 2.2 Mining Echo rank 2 = 0.33)")
    K.eq(w("Hand.cooking"), "Worth +0.8 % Cooking XP a VP (= ~+0.03 % all XP at a usual play mix; keeping: +0.25 %)",
         "F42 FIX1 Hand Cooking (its own rank 1, the shared 3rd cost 10 VP): 8 % / 10 VP x 0.04")
    K.eq(w("Foraging.echo"), "Worth +2 % Foraging XP a VP (= ~+0.3 % all XP at a usual play mix; keeping: +0.25 %)",
         "F42 FIX1 Foraging Echo rank 1: 8 % / 4 VP x 0.15 = 0.30 (spec 2.2 Foraging Echo rank 1 = 0.30)")
    import re as _re
    _hf = _re.match(r"Worth \+([0-9.]+) % Farming XP a VP \(= ~\+([0-9.]+) % all XP at a usual play mix; keeping: \+0\.25 %\)$", w("Hand.farming") or "")
    K.check(_hf is not None and abs(float(_hf.group(1)) * 0.10 - float(_hf.group(2))) <= 0.006,
            "F42 FIX1 Hand Farming: its raw value x the Farming share 0.10: %r" % w("Hand.farming"))
    K.eq(w("Combat.echo"), "Worth +2 % Combat XP (kills) a VP", "F42 FIX1 Combat Echo rank 1: 8 % / 4 VP, no play share = raw value, no keep comparison")
    K.eq(w("Beast.echo"), "Worth +2 % Beastmastery (pet) XP a VP", "F42 FIX1 Beastmastery Echo: share 0 = raw value only")
    K.check(all(int(float(Tr.NMIX[I(n_)]) * 100 + 0.5) == v_ for n_, v_ in (("Class.echo", 45), ("Mining.echo", 18), ("Foraging.echo", 15),
            ("Hand.farming", 10), ("Hand.cooking", 4), ("Hand.alchemy", 4), ("Hand.fishing", 2), ("Hand.smithing", 0), ("Combat.echo", 0)))
            and float(Tr.NMIX[I("Void.insight")]) < 0, "F42 FIX1 NMIX = balance_model SHARE (class 0.45, Mining 0.18, Foraging 0.15, Farming 0.10 ...)")
    K.check(w("Class.echo") is None and w("Mining.tool") is None and w("Void.head") is None,
            "F42 no line: a full node (Class Echo 5 / 5), a tool node, Head Start (not XP)")
    Cfg.KEEP = 0.5
    K.check(w("Void.insight").endswith("(keeping: +0.5 % all XP a VP)"), "F42 the keep value follows nexus.keep")
    Cfg.KEEP = 0.25
    # ---------------------------------------------------------------- 3. the REAL page: the hovers
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    f = os.path.join(pl, k + ".properties")
    open(f, "w").write("n=2\nv=4\nvp=76\nvpSpent=36\nnode.Void.insight=2\nnode.Hand.farming=1\nnode.Mining.tool=1\n")
    St.CACHE.clear()
    Cfg.BRIDGE.put("acc:defs", T40.DEFS)
    Cfg.BRIDGE.put("acc:fn:bag", Bag(["Skyy_Talisman_Lantern_Common"]))
    Cfg.PERM_TEST = Const(JClass("java.lang.Boolean").TRUE)
    pg = R("RbPage")(U, "hub")
    b_, e_ = UCB(), UEB()
    pg.build(None, b_, e_, None)
    sets = dict((s_, T40.unq(d_)) for ty, s_, t_, d_ in T40.cmds_of(b_) if ty == "Set")
    tip = lambda nid: sets.get("#SkyyRbN%dB.TooltipText" % I(nid), "")
    t0 = tip("Void.insight")
    K.check("Keeping those 32 VP instead: +8 % all XP\nWorth +0.31 % all XP a VP (keeping: +0.25 % all XP a VP)" in t0,
            "F42 the page: Void Insight's hover (rank 3 = 10 %% for 32 VP) shows the worth line under the keep line: %r" % t0)
    K.check("Worth +" in tip("Mining.echo") and "Worth +" not in tip("Mining.tool") and "Worth +" not in tip("Void.head"),
            "F42 the page: XP nodes have the line, tool / Head Start nodes do not")
    K.check(sum(1 for i in range(21) if "Worth +" in sets.get("#SkyyRbN%dB.TooltipText" % i, "")) == 12, "F42 the page: 12 XP nodes, 12 worth lines")
    K.check("~+" in tip("Mining.echo") and "keeping: +0.25 %)" in tip("Mining.echo"), "F42 FIX1 the page: Mining Echo's hover shows the all-XP value: %r" % tip("Mining.echo"))
    # ---------------------------------------------------------------- FIX2: the page offers no Dust
    gn = R("RbCheck").gains(U, 0)
    K.check(gn is not None and "Dust" not in str(gn[2]) and "Dust" not in str(gn[4]) and "Void-Touched I" in str(gn[2]),
            "F42 FIX2 the first rebirth's 'What you would get' lines name no Dust: %r / %r" % (str(gn[2]), str(gn[4])))
    # ---------------------------------------------------------------- FIX2b: the keep line names the +500 % limit past it
    K.eq(str(Tr.keepTxt(800)), "Holding 800 VP: +200 % XP", "F42 FIX2b keep line under the limit: unchanged")
    K.eq(str(Tr.keepTxt(2000)), "Holding 2000 VP: +500 % XP", "F42 FIX2b keep line exactly at the limit: no note")
    K.eq(str(Tr.keepTxt(2200)), "Holding 2200 VP: +550 % XP (limit +500 % XP)", "F42 FIX2b keep line past the limit names it (spec 3.4)")
    # ---------------------------------------------------------------- 4. no limit: 25 rebirths still allowed by the count
    t25 = [str(x) for x in list(R("RbCheck").reqs(U, "hub", 25)[0])]
    K.check(int(Cfg.MAX) == 0 and int(Cfg.lim()) == 2147483647 and "OK  Rebirths done 25 (no limit)" in t25,
            "F42 rebirth.max 0 = no limit: a profile with 25 rebirths meets the rebirths requirement: %s" % t25[:3])
    K.save()


def T40_oa(a):
    from jpype import JArray, JObject, JClass
    arr = JArray(JClass("java.lang.Object"))(len(a))
    for i, x in enumerate(a):
        arr[i] = x if not isinstance(x, str) else JClass("java.lang.String")(x)
    return arr


def run_live42(out, jar, scratch, home):
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass
    K = HK.Child(out)
    T34 = T40.T34
    mods = os.path.dirname(home)
    cfgf = os.path.join(home, "config.properties")
    raw0 = open(cfgf, "rb").read()
    t0 = T34.tree(home)
    Cfg, path = T34.kit_home(home)
    calls = T34.setup_calls(jar)
    idx = lambda n: calls.index(n) if n in calls else -1
    K.check(0 <= idx("RbCfg.migOn") < idx("RbCfg.migMax") < idx("RbCfg.loadCfg") < idx("CfgPub.start"), "L42 setup(): migOn, migMax, loadCfg, CfgPub.start")
    had10 = b"\nrebirth.max=10" in raw0
    r0, r1 = str(Cfg.migOn(path(cfgf))), str(Cfg.migMax(path(cfgf)))
    c1 = str(Cfg.loadCfg(True))
    raw1 = open(cfgf, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw0 else b"\n"
    K.notes.append("L42 live start 1: migMax: %s" % r1[:160])
    if had10:
        K.check((b"\nrebirth.max=0" + nl) in raw1 and b"skyyrebirth-0.3.6-max" in raw1,
                "L42 start 1: the live rebirth.max=10 -> 0 + the 0.3.6 marker")
        K.check(raw1.replace(b"rebirth.max=0", b"rebirth.max=10", 1).replace(
            [ln for ln in raw1.split(nl) if b"skyyrebirth-0.3.6-max" in ln][0] + nl, b"", 1) == raw0, "L42 start 1: every other byte kept")
        log = open(os.path.join(home, "config-changes.log"), encoding="utf-8").read()
        K.check(log.count("\trebirth.max\t10\t0\t") == 1, "L42 one change-log row rebirth.max 10 -> 0 (Undo)")
        hist = [os.path.join(r_, f_) for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs]
        K.check(any(open(h, "rb").read() == raw0 for h in hist), "L42 config-history holds the old file (verified copy)")
    else:
        K.notes.append("L42 the live file no longer holds rebirth.max=10 (already migrated or edited) - only start twice checked")
    K.check(int(Cfg.MAX) == 0, "L42 start 1: Max rebirths = no limit: %s" % c1[:120])
    t1 = T34.tree(home)
    St = R("RbStore")
    St.DIR = JClass("java.nio.file.Paths").get(os.path.join(home, "players"))
    r2 = str(Cfg.migMax(path(cfgf)))
    Cfg.loadCfg(True)
    JClass(RB + "CfgPub").start(JClass("java.nio.file.Paths").get(mods), None)
    JClass(RB + "CfgPub").flush()
    K.check(r2 == "" and T34.tree(home) == t1, "L42 start 2 + the config kit write nothing")
    K.save()


if __name__ == "__main__":
    assert os.path.isfile(B.JAVASSIST), B.JAVASSIST
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("vp", T40.run_vp), ("page", T40.run_page), ("f41", T41.run_f41), ("f42", run_f42), ("live42", run_live42)],
           script=__file__, live=(T40.LIVE_RB, "Skyy_SkyyRebirth"))
