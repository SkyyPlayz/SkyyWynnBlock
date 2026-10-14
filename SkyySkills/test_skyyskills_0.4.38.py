"""SkyySkills 0.4.38 - harness for the econ38 round (tools/skills_0_4_38_patch.py): rebirth.coinFactor 0.9 -> 0.8 + the one-time RbCoinMig,
Fishing / Ranching / Orchard on the /skills page (12 rows, 960 x 973), arm.ranching + arm.orchard in the rebirth facts.
Build first: python tools/skills_0_4_38_patch.py && python SkyySkills/build_skyyskills_0.4.38.py

    python SkyySkills/test_skyyskills_0.4.38.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.37 -> 0.4.38: exactly the planned members differ; RbCoinMig added
  G   g38      EXECUTED:
               COIN FACTOR - SkillCfg defaults (RB_COIN 0.8; a fresh xp.properties has rebirth.coinFactor=0.8 + the marker; a missing /
               bad number = 0.8, clamps 0 - 1); SkillStore.rbCoins x0.8 per rebirth (100 -> 80 -> 64); the Server Setup row default 0.8
               (config:def:SkyySkills through the REAL kit); RbCoinMig.plan on: 0.4.37's default file (0.9 -> 0.8 + the marker under
               the line, nothing else), the same in CRLF (endings kept), a file WITHOUT the key (the line + marker appended), an admin's
               0.5 (kept + marker + note), a continued entry (kept), a file ending in a backslash, the marker present (nothing), the
               0.4.38 default (nothing); sameAfter refuses any other change; run() on a file: History copy of the old bytes FIRST, one
               change-log line rebirth.coinFactor 0.9 -> 0.8 (Undo-able), the file then loads 0.8, run() again = nothing; a missing file
               = nothing
               /skills PAGE - SkillDefs.ROW_SLOTS = 12 rows (Fishing, Ranching, Orchard after Farming); the REAL SkillsPage.build with the
               engine's UICommandBuilder / UIEventBuilder: root 960 x 973 (<= the kit's 980 ceiling = fits 1080), the 12 rows
               #SkyySkRow0..11 drawn with their names + levels, a STATS binding skstat16 / skstat17 / skstat18 for the new rows, TREE
               buttons only where SkyyTrees has a tree; the Top 10 view still builds
               REBIRTH FACTS - SkillRb.facts: arm.ranching / arm.orchard = run XP / XP to the cap / level / cap of those slots (the
               arm.farming format), every 0.4.37 fact unchanged
  0.4.37's phases on the 0.4.38 jar: F fakes, G37 (perfect dodge, gathering phase 2), R3 rebirth participant, RS restart, RB, R route,
               X exec, D live (start twice on a scratch copy; every live player file loads)
  DM  livemig  START TWICE on a scratch COPY of the live Skyy_SkyySkills with every one-time update in setup() order, 0.4.37 vs 0.4.38:
               0.4.38's first start changes only xp.properties (rebirth.coinFactor=0.8 + the marker appended - the live file has no
               line - every other byte kept), its History copy and the change log; the second start changes nothing; player files
               untouched; the live file then reads RB_COIN 0.8
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.38"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.37.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "econ38", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))
# 0.4.32's exec phase compares PollMig with a 0.4.31 jar (the local tidy removed SkyySkills-0.4.31.jar): pass a copy with SKYY_JAR031
# (e.g. one built in a cross-check scratch, copied into this round's scratch) - without it that phase cannot run its PollMig checks

EXPECT = {
    "SkillCfg": ["~<clinit>", "~m load"],                    # RB_COIN 0.8 (field initialiser) + the load default + the header version
    "SkillDefs": ["~<clinit>"],                              # ROW_SLOTS: 12 rows
    "SkillRb": ["+f XARMS", "~<clinit>", "~m facts"],        # arm.ranching / arm.orchard
    "SkillsPage": ["~m build"],                              # 12 rows, 973 high
    "SkyySkillsPlugin": ["~m setup"],                        # RbCoinMig.run + the ready line
    # version texts only (inlined strings): the pack name, the kit's rows (the coinFactor default 0.8) + its default file text
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["RbCoinMig"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T37 = tmod("test_skyyskills_0.4.37.py", "t0437")
T32 = T37.T32
loader_for, path = T32.loader_for, T32.path
MARK = ("# SkyySkills 0.4.38 rebirth level coins x0.8: level-up coins after a rebirth pay x rebirth.coinFactor per rebirth "
        "(the old default was 0.9).")


def run_g38(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Defs, Mig, Rb = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("RbCoinMig"), J("SkillRb")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Lo = loader_for(OLD_JAR, isolated=True)
    old_def = str(JClass(PKG + "SkillCfg", loader=Lo).DEFAULTS)
    new_def = str(Cfg.DEFAULTS)
    # ================================================================ COIN FACTOR
    K.check(float(Cfg.RB_COIN) == 0.8, "G coin: SkillCfg.RB_COIN defaults to 0.8")
    K.check("\nrebirth.coinFactor=0.9\n" in "\n" + old_def and "\nrebirth.coinFactor=0.8\n" + MARK + "\n" in "\n" + new_def and "rebirth.coinFactor=0.9" not in new_def
            and str(Mig.MARK) == MARK, "G coin: the fresh file says 0.8 with the marker under it (0.4.37's said 0.9)")
    K.check(old_def.replace("(0.9 = 90 % after 1, 81 % after 2)", "(0.8 = 80 % after 1, 64 % after 2)").replace("rebirth.coinFactor=0.9\n", "rebirth.coinFactor=0.8\n" + MARK + "\n")
            .replace("SkyySkills 0.4.37 - XP rules", "SkyySkills 0.4.38 - XP rules") == new_def, "G coin: the fresh file differs from 0.4.37's ONLY by the factor, its comment, the marker and the header version")
    d = os.path.join(scratch, "g", "fresh")
    os.makedirs(d)
    Cfg.FILE = path(os.path.join(d, "xp.properties"))
    Cfg.load()
    K.check(open(os.path.join(d, "xp.properties"), encoding="latin-1").read() == new_def and float(Cfg.RB_COIN) == 0.8, "G coin: load() with no file writes the 0.4.38 default, reads 0.8")
    for txt, want, what in (("multiplier=1.0\n", 0.8, "missing"), ("rebirth.coinFactor=x\n", 0.8, "bad"), ("rebirth.coinFactor=0.5\n", 0.5, "0.5"),
                            ("rebirth.coinFactor=7\n", 1.0, "7 -> 1"), ("rebirth.coinFactor=-2\n", 0.0, "-2 -> 0")):
        open(os.path.join(d, "xp.properties"), "w").write(txt)
        Cfg.load()
        K.check(abs(float(Cfg.RB_COIN) - want) < 1e-9, "G coin: rebirth.coinFactor %s -> %s (got %s)" % (what, want, float(Cfg.RB_COIN)))
    Cfg.RB_COIN = 0.8
    K.check([int(Sto.rbCoins(100, n)) for n in (0, 1, 2, 3)] == [100, 80, 64, 51], "G coin: level coins x0.8 per rebirth: 100 / 80 / 64 / 51 (rounded)")
    gen = open(os.path.join(HERE, "build_skyyskills_%s.py" % VERSION), encoding="utf8").read()
    K.check('("rebirth.coinFactor", "Level coins after each rebirth", "general", "dec", "0.8", "0", "1"' in gen, "G coin: the Server Setup row default is 0.8 (build script)")
    # ---- RbCoinMig.plan
    r = Mig.plan(old_def)
    body = str(r[0]) if r is not None else ""
    K.check(r is not None and bool(r[2]) and not bool(r[4]) and list(r[1]) == ["rebirth.coinFactor", "0.9", "0.8"] and str(r[3]) == ""
            and body == old_def.replace("rebirth.coinFactor=0.9\n", "rebirth.coinFactor=0.8\n" + MARK + "\n"), "G plan(0.4.37 default): 0.9 -> 0.8 + the marker under the line, nothing else")
    crlf = old_def.replace("\n", "\r\n")
    r = Mig.plan(crlf)
    K.check(r is not None and str(r[0]) == crlf.replace("rebirth.coinFactor=0.9\r\n", "rebirth.coinFactor=0.8\r\n" + MARK + "\r\n"), "G plan(CRLF): line endings kept")
    nokey = old_def.replace("rebirth.coinFactor=0.9\n", "")
    r = Mig.plan(nokey)
    K.check(r is not None and bool(r[2]) and bool(r[4]) and list(r[1]) == ["rebirth.coinFactor", "0.9", "0.8"] and str(r[0]) == nokey + "rebirth.coinFactor=0.8\n" + MARK + "\n",
            "G plan(no rebirth.coinFactor line - pre-0.4.36 file): the line + the marker appended at the end")
    r = Mig.plan("a=1\r\nb=2")
    K.check(r is not None and str(r[0]) == "a=1\r\nb=2\r\nrebirth.coinFactor=0.8\r\n" + MARK + "\r\n", "G plan(no key, CRLF, no final newline): appended in the file's ending")
    r = Mig.plan("a=1\nb=x\\")
    K.check(r is not None and str(r[0]) == "a=1\nb=x\\\n\nrebirth.coinFactor=0.8\n" + MARK + "\n", "G plan(a dangling continuation): an empty line first so nothing joins it")
    r = Mig.plan(old_def.replace("rebirth.coinFactor=0.9", "rebirth.coinFactor = 0.5"))
    K.check(r is not None and not bool(r[2]) and list(r[1]) == [] and "kept" in str(r[3]) and "rebirth.coinFactor = 0.5\n" + MARK + "\n" in str(r[0]),
            "G plan(an admin's 0.5): kept + the marker + a note")
    r = Mig.plan(old_def.replace("rebirth.coinFactor=0.9", "rebirth.coinFactor=0.\\\n9"))
    K.check(r is not None and not bool(r[2]) and "rebirth.coinFactor=0.\\\n9\n" + MARK in str(r[0]), "G plan(a continued entry): kept")
    K.check(Mig.plan(body) is None and Mig.plan(new_def) is None and Mig.plan(None) is None, "G plan: the marker present / the 0.4.38 default / null -> nothing")
    b1 = old_def.encode("latin-1")
    K.check(bool(Mig.sameAfter(b1, body.encode("latin-1"), True, False)) and not bool(Mig.sameAfter(b1, (body + "x=1\n").encode("latin-1"), True, False))
            and not bool(Mig.sameAfter(b1, body.replace("multiplier=1.0", "multiplier=2").encode("latin-1"), True, False))
            and not bool(Mig.sameAfter(b1, body.encode("latin-1"), False, False)), "G sameAfter: only rebirth.coinFactor 0.9 -> 0.8 passes")
    # ---- run() on a file
    mf = os.path.join(scratch, "g", "mig", "xp.properties")
    os.makedirs(os.path.dirname(mf))
    open(mf, "wb").write(nokey.encode("latin-1"))
    Cfg.FILE = path(mf)
    msg = str(Mig.run())
    after = open(mf, "rb").read().decode("latin-1")
    hist = os.path.join(os.path.dirname(mf), "config-history")
    logf = os.path.join(os.path.dirname(mf), "config-changes.log")
    K.check("0.9 -> 0.8" in msg and "line added" in msg and after == nokey + "rebirth.coinFactor=0.8\n" + MARK + "\n", "G run(): the line added: %s" % msg[:200])
    K.check(os.path.isdir(hist) and any(open(os.path.join(hr, f_), "rb").read() == nokey.encode("latin-1") for hr, _d, fs_ in os.walk(hist) for f_ in fs_),
            "G run(): the old file kept in config-history first")
    K.check(os.path.isfile(logf) and "rebirth.coinFactor\t0.9\t0.8\tok" in open(logf, encoding="latin-1").read() and "SkyySkills 0.4.38" in open(logf, encoding="latin-1").read(),
            "G run(): one Undo-able change-log line rebirth.coinFactor 0.9 -> 0.8")
    K.check(str(Mig.run()) == "" and open(mf, "rb").read().decode("latin-1") == after, "G run() again: nothing")
    Cfg.load()
    K.check(float(Cfg.RB_COIN) == 0.8, "G run(): the updated file reads 0.8")
    Cfg.FILE = path(os.path.join(scratch, "g", "nofile", "xp.properties"))
    K.check(str(Mig.run()) == "" and not os.path.exists(os.path.join(scratch, "g", "nofile")), "G run(): no file = nothing written")
    # ================================================================ /skills PAGE
    rows = [int(x) for x in Defs.ROW_SLOTS]
    K.check(rows == [0, 1, 2, 16, 17, 18, 10, 11, 12, 4, 13, 3] and [str(Defs.LABELS[x]) for x in rows[3:6]] == ["Fishing", "Ranching", "Orchard"],
            "G page: ROW_SLOTS = 12 rows, Fishing / Ranching / Orchard after Farming: %s" % rows)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    me = UUID(0x5117, 8)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    N = int(Defs.N)
    dd = [0] * (2 * N)
    dd[int(Defs.FISHING)] = 5000
    dd[int(Defs.RANCHING)] = 1200
    dd[int(Defs.ORCHARD)] = 300
    Sto.DATA.put(me.toString(), JArray(JLong)(dd))

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v
    br = Sto.bridge()

    def build(view=-1, trees=False):
        if trees:
            br.put("tree:fn:level", Const(JClass("java.lang.Integer")(0)))
            br.put("tree:names", "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration")
        else:
            br.remove("tree:fn:level")
            br.remove("tree:names")
        pg = J("SkillsPage")(pr)
        pg.view = view
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        cmds = [(str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)) for c in b.getCommands()]
        evs = [None if e.data is None else str(e.data) for e in ev.getEvents()]
        return err, cmds, evs
    for trees in (False, True):
        err, cmds, evs = build(trees=trees)
        markup = "\n".join(c[2] or "" for c in cmds) + "\n".join(c[3] or "" for c in cmds)
        texts = "\n".join(c[3] or "" for c in cmds if c[3]) + "\n" + "\n".join(str(c) for c in cmds)
        K.check(err is None, "G page (trees %s): SkillsPage.build ran: %s" % (trees, err))
        K.check("Height: 973" in markup and "Width: 960" in markup and "Height: 786" not in markup, "G page (trees %s): the window is 960 x 973 (fits 1080)" % trees)
        K.check(all("SkyySkRow%d" % i in markup for i in range(12)) and "SkyySkRow12" not in markup, "G page (trees %s): 12 rows #SkyySkRow0..11" % trees)
        K.check(all(any(("skstat%d" % s) in (e or "") for e in evs) for s in (16, 17, 18)), "G page (trees %s): STATS bindings skstat16 / 17 / 18" % trees)
        K.check(all(("%s  " % nm) in texts for nm in ("Fishing", "Ranching", "Orchard")), "G page (trees %s): the new rows' names + levels drawn" % trees)
        trees_b = [e for e in evs if e and "sktree" in e]
        K.check((not trees and not trees_b) or (trees and not any(("sktree%d" % s) in e for e in trees_b for s in (16, 17, 18)) and any("sktree2" in e for e in trees_b)),
                "G page (trees %s): TREE buttons only where SkyyTrees has a tree (none for the 3 new rows)" % trees)
    err, cmds, evs = build(view=int(Defs.FISHING))
    K.check(err is None and any("skback" in (e or "") for e in evs), "G page: the Top 10 view (Fishing) still builds: %s" % err)
    Sto.DATA.remove(me.toString())
    # ================================================================ REBIRTH FACTS
    k = "00000000-0000-4000-8000-0000000003b7"
    u = UUID.fromString(k)
    d2 = [0] * (2 * N)
    d2[int(Defs.FARMING)], d2[int(Defs.RANCHING)], d2[int(Defs.ORCHARD)] = 7000, 2500, 900
    f = Rb.facts(k, u, JArray(JLong)(d2))
    cap = lambda s: int(J("SkillCap").cap(k, s))
    fmt = lambda s, t: "%d/%d/%d/%d" % (t, int(Defs.cumAt(s, cap(s))), int(Defs.levelCap(s, t, cap(s))), cap(s))
    K.check(str(f.getProperty("arm.ranching")) == fmt(int(Defs.RANCHING), 2500) and str(f.getProperty("arm.orchard")) == fmt(int(Defs.ORCHARD), 900)
            and str(f.getProperty("arm.farming")) == fmt(int(Defs.FARMING), 7000), "G facts: arm.ranching / arm.orchard in the arm.farming format: %s / %s"
            % (f.getProperty("arm.ranching"), f.getProperty("arm.orchard")))
    OCfg = JClass(PKG + "SkillCfg", loader=Lo)   # 0.4.37's tables from its own default file (the new jar's are loaded above)
    OCfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger", loader=Lo).get("SkyySkills")
    os.makedirs(os.path.join(scratch, "g", "old37"))
    OCfg.FILE = path(os.path.join(scratch, "g", "old37", "xp.properties"))
    OCfg.load()
    Cfg.FILE = path(os.path.join(scratch, "g", "fresh", "xp.properties"))
    open(os.path.join(scratch, "g", "fresh", "xp.properties"), "w").write(new_def)
    Cfg.load()
    f = Rb.facts(k, u, JArray(JLong)(d2))
    Ro = JClass(PKG + "SkillRb", loader=Lo)
    fo = Ro.facts(k, u, JArray(JLong)(d2))
    old_keys = sorted(str(x) for x in fo.stringPropertyNames())
    new_keys = sorted(str(x) for x in f.stringPropertyNames())
    K.check(sorted(set(new_keys) - set(old_keys)) == ["arm.orchard", "arm.ranching"] and all(str(fo.getProperty(x)) == str(f.getProperty(x)) for x in old_keys),
            "G facts: exactly two new keys, every 0.4.37 fact unchanged: %s" % [(x, str(fo.getProperty(x)), str(f.getProperty(x))) for x in sorted(set(old_keys) | set(new_keys)) if str(fo.getProperty(x)) != str(f.getProperty(x))][:6])
    K.save()


# ====================================================================================================== DM: start twice on live data
def run_livemig(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    migs_old = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig", "PollMig"]
    res = {}
    lc_root = os.path.dirname(home)

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    for tag, jr, migs in (("old", OLD_JAR, migs_old), ("new", jar, migs_old + ["RbCoinMig"])):
        lc = os.path.join(lc_root, "copy-" + tag)
        shutil.copytree(home, lc)
        L = loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Hist, CLog, Rows = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

        def start():
            Cfg.FILE = path(os.path.join(lc, "xp.properties"))
            Sto.DATA.clear()
            Sto.DIRTY.clear()
            Sto.DIR = path(os.path.join(lc, "players"))
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r = {}
            for nm in migs:
                r[nm] = str(J(nm).run())
            r["load"] = str(Cfg.load())
            J("ClassCurve").start(path(lc))
            J("OwnCurve").start(path(lc))
            return r
        s0 = snap(lc)
        r1 = start()
        s1 = snap(lc)
        r2 = start()
        s2 = snap(lc)
        res[tag] = {"r1": r1, "r2": r2, "s0": s0, "s1": s1, "s2": s2, "coin": float(Cfg.RB_COIN)}
    o, n = res["old"], res["new"]
    ch_o = sorted(k for k in set(o["s0"]) | set(o["s1"]) if o["s0"].get(k) != o["s1"].get(k))
    ch_n = sorted(k for k in set(n["s0"]) | set(n["s1"]) if n["s0"].get(k) != n["s1"].get(k))
    extra = sorted(set(ch_n) - set(ch_o))
    K.notes.append("DM: 0.4.37 start 1 changed %s; 0.4.38 changed %s; RbCoinMig: %s" % (ch_o, ch_n, n["r1"].get("RbCoinMig", "")[:300]))
    K.check(set(extra) <= {"xp.properties", "config-changes.log"} | set(k for k in extra if k.startswith("config-history/")),
            "DM: 0.4.38 start 1 changes what 0.4.37 changes + only xp.properties / its History copy / the change log: %s" % extra)
    xp0 = n["s0"].get("xp.properties", b"").decode("latin-1")
    xp1 = n["s1"].get("xp.properties", b"").decode("latin-1")
    nl = "\r\n" if "\r\n" in xp0 else "\n"
    if "\nrebirth.coinFactor" not in "\n" + xp0:
        pre = "" if xp0.endswith("\n") else nl
        K.check(xp1 == xp0 + pre + "rebirth.coinFactor=0.8" + nl + MARK + nl, "DM: the live xp.properties (no rebirth.coinFactor line): the line + the marker appended, every other byte kept")
    elif "\nrebirth.coinFactor=0.9" + nl in "\n" + xp0:
        K.check(xp1 == xp0.replace("rebirth.coinFactor=0.9" + nl, "rebirth.coinFactor=0.8" + nl + MARK + nl, 1), "DM: the live xp.properties: 0.9 -> 0.8 + the marker, every other byte kept")
    else:
        K.notes.append("DM: the live xp.properties holds an admin's rebirth.coinFactor (kept)")
    if xp0 != xp1:
        K.check(any(k.startswith("config-history/") and v == n["s0"]["xp.properties"] for k, v in n["s1"].items() if k not in n["s0"]),
                "DM: the live xp.properties before the update is in config-history")
    K.check(all(n["s1"].get(k) == n["s2"].get(k) for k in set(n["s1"]) | set(n["s2"])) and n["r2"].get("RbCoinMig") == "", "DM: 0.4.38 start 2 changes nothing")
    K.check(all(n["s0"].get(k) == n["s1"].get(k) for k in n["s0"] if k.startswith("players/")), "DM: player files untouched")
    K.check(n["coin"] == 0.8, "DM: the live copy reads rebirth.coinFactor 0.8 after the update (0.4.37 read %s)" % o["coin"])
    K.save()


# ---- 0.4.37's phases on this jar
def run_fake15(out, jar, scratch, home):
    return T37.run_fake15(out, jar, scratch, home)


def run_fake25(out, jar, scratch, home):
    return T37.run_fake25(out, jar, scratch, home)


def run_g37(out, jar, scratch, home):
    return T37.run_g37(out, jar, scratch, home)


# 0.4.36's R3 checks that pin the OLD default 0.9 (the fresh file line, its replace-based clamp cases, the 0.9^n coins) and the fact count
# (+ arm.ranching / arm.orchard) are expected to change in 0.4.38 - G checks the same paths with 0.8 and the two new facts
EXPECTED_R3_38 = ("R3 rebirth.coinFactor: default 0.9", "R3 rebirth.coinFactor=0.5 -> 0.5", "R3 rebirth.coinFactor=7 -> 1.0",
                  "R3 rebirth.coinFactor=-2 -> 0.0", "R3 rebirth.coinFactor=abc -> 0.9", "R3 rbCoins: 0.9^n rounded")


def run_r3(out, jar, scratch, home):
    tmp = os.path.join(scratch, "r3-37.json")
    T37.run_r3(tmp, jar, scratch, home)
    d = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.notes = d["ok"], d["notes"]
    for f in d["fails"]:
        if any(f.startswith(e) for e in EXPECTED_R3_38):
            K.ok += 1
            K.notes.append("R3 expected in 0.4.38 (the default is 0.8 now - checked in G): " + f[:90])
        else:
            K.fails.append(f)
    K.save()


def run_restart(out, jar, scratch, home):
    return T37.run_restart(out, jar, scratch, home)


def run_r1(out, jar, scratch, home):
    return T37.run_r1(out, jar, scratch, home)


def run_route(out, jar, scratch, home):
    return T37.run_route(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    return T37.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    """0.4.37's live phase (D), then the one-time update start-twice proof (DM) on a fresh copy in the same child"""
    tmp = os.path.join(scratch, "live37.json")
    T37.run_live(tmp, jar, scratch, home)
    prev = json.load(open(tmp))
    tmp2 = os.path.join(scratch, "livemig.json")
    lm = os.path.join(scratch, "lm", "Skyy_SkyySkills")
    shutil.copytree(LIVE_DIR, lm)
    run_livemig_nojvm(tmp2, jar, scratch, lm)
    b = json.load(open(tmp2))
    json.dump({"ok": prev["ok"] + b["ok"], "fails": list(prev["fails"]) + list(b["fails"]), "notes": list(prev["notes"]) + list(b["notes"])}, open(out, "w"), indent=1)


def run_livemig_nojvm(out, jar, scratch, home):
    import jpype
    orig = HK.jvm
    HK.jvm = lambda *a, **k: None   # the JVM of the live phase is already up (same class path)
    try:
        run_livemig(out, jar, scratch, home)
    finally:
        HK.jvm = orig


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("g38", run_g38), ("fake15", run_fake15), ("fake25", run_fake25), ("g37", run_g37), ("r3", run_r3), ("restart", run_restart),
                   ("r1", run_r1), ("route", run_route), ("exec", run_exec), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
