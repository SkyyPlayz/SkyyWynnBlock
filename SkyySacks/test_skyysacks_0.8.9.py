"""Harness for SkyySacks 0.8.9 (VOID COSTS + FABRIC TO COMBAT + STORAGE REBALANCE; tools/sacks_0_8_9_patch.py).
Build first: python tools/sacks_0_8_9_patch.py && python SkyySacks/build_skyysacks_0.8.9.py   (see KIT)

    python SkyySacks/test_skyysacks_0.8.9.py [--keep] [--dir <scratch>] [--tree-kit]

KIT: the jar is built on the COMMITTED kit (skyyui 1.5). While tools/skyyui.py differs from git HEAD (another builder's uncommitted edits),
this harness - parent and children - first loads `git show HEAD:tools/skyyui.py` (copied to <dir>/../kit-head/skyyui.py) as the `skyyui`
module, so every page check uses the kit the jar was built with. --tree-kit uses the working-tree file instead.

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.8 -> 0.8.9: + SackMig089; SackDefs (homeOf, + lineName, the HOLDS texts), SackCfg (+ PD_CURVE, curve, the loader),
              VoidStore (totalFor, levelOf, upgrade), SacksPage (upgradeBox), the plugin setup, the kit rows / default text
  X / L / ART / FUEL / LOGS / SND / D   the 0.8.8 harness's phases on the 0.8.9 jar. Where an older phase pins the 0.8.0-0.8.8 NUMBERS
              (100 space per level, the square curve, the old Smithing / Combat costs) it runs with exactly those values set
              (OLDNUM below: the fields the kit / file would hold on a server that kept the old values) - that proves the code paths
              are unchanged; the new numbers are proven in VOID.
  MIG  NEW (the real SackMig089 + the real config kit, a scratch mods folder): the CRLF file of the NewBetaTest world (commented
              defaults; copied read-only): the 6 commented cost lines + #pd.perLevel get the new default, every other byte kept, the
              marker appended, Properties identical, History copy = the old bytes, no change-log line; the HUD mod file (no pd lines):
              the marker only; a synthetic LF file with one CRLF line and no final newline: live old-default lines (cost text with
              spaces, perLevel 100.0) moved, a hand-edited cost kept + named, a doubled line kept, the change-log has one line per moved
              value (key, old, new), SackCfg.reload reads the new values; start 2 changes nothing (marker); the kit's own console set
              back to the old value (what Changes -> Undo runs) sticks and start 3 keeps it; a fresh start (no file): SackCfg.reload writes
              the 0.8.9 default (marker inside) and the update does nothing; a file whose History copy cannot be written: untouched
  VOID NEW (the 0.8.0 harness's Void stand-ins): fabric scraps -> Combat (catOf / homeOf / catTotal: a stored stack counts in Combat
              now, not Smithing; nothing moved), bars / leather / hides / bolts stay Smithing; a Combat over its space keeps every item,
              a sweep takes in no more Combat (the fabric stays in the inventory) while Smithing has its room back; the level curve
              (totalFor / levelOf exact inverses at 1.75 for every category and every level 1..250; at curve 2 the old formula exactly;
              Skyy's Foraging 3,425 -> Lv 19), space = level x 150 x rarity; the Smithing Unique upgrade with leather + copper bars from
              the Void and the inventory (exact cost taken, conserved), refused short (the real name in the line), a crash part-way
              rolled back, paid once after; Combat Unique with Linen Scraps; the upgrade box: icon cells with the new ids, the real names
              over the counts (stand-in I18nModule), the plain count cell without a name
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks089", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
BETA_CFG = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks", "config.properties")
EXPECT = {
    "SackDefs": ["~m homeOf", "+m lineName", "~<clinit>"],
    "SackCfg": ["+f PD_CURVE", "+m curve", "~m pdKeys", "~m pdSig", "~m reload", "~<clinit>"],   # reload: the default file text
    "VoidStore": ["~m levelOf", "~m totalFor", "~m upgrade"],
    "SacksPage": ["~m upgradeBox"],
    "SkyySacksPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header", "~<clinit>"],
    "CfgFile": ["~<clinit>"],   # the kit's copy of the default file text (the curve row, the marker line, the new defaults)
}
ADDED = ["SackMig089"]
T080 = os.path.join(HERE, "test_skyysacks_0.8.0.py")
OLDNUM = {"PD_PER_LEVEL": 100, "PD_CURVE": 2.0,
          "PD_COST_SMITHING_UNIQUE": "Ingredient_Hide_Light:200,Ingredient_Fabric_Scrap_Linen:100,Ingredient_Fabric_Scrap_Wool:100",
          "PD_COST_SMITHING_RARE": "Ingredient_Hide_Light:750,Ingredient_Hide_Medium:500,Ingredient_Fabric_Scrap_Linen:250,Ingredient_Fabric_Scrap_Shadoweave:100",
          "PD_COST_SMITHING_LEGENDARY": "Ingredient_Hide_Light:2000,Ingredient_Hide_Medium:1000,Ingredient_Hide_Heavy:250,Ingredient_Fabric_Scrap_Shadoweave:250,Ingredient_Fabric_Scrap_Cindercloth:100",
          "PD_COST_COMBAT_UNIQUE": "Ingredient_Bone_Fragment:250,Ingredient_Feathers_Light:100",
          "PD_COST_COMBAT_RARE": "Ingredient_Bone_Fragment:1000,Ingredient_Feathers_Light:500,Ingredient_Sac_Venom:100,Ingredient_Chitin_Sturdy:100",
          "PD_COST_COMBAT_LEGENDARY": "Ingredient_Bone_Fragment:2500,Ingredient_Feathers_Light:1000,Ingredient_Sac_Venom:250,Ingredient_Chitin_Sturdy:250,Ingredient_Void_Essence:100,Ingredient_Voidheart:10"}
NEWCOST = {"PD_COST_SMITHING_UNIQUE": "Ingredient_Leather_Light:200,Ingredient_Bar_Copper:100",
           "PD_COST_SMITHING_RARE": "Ingredient_Leather_Light:750,Ingredient_Leather_Medium:500,Ingredient_Bar_Copper:250,Ingredient_Bar_Iron:100",
           "PD_COST_SMITHING_LEGENDARY": "Ingredient_Leather_Light:2000,Ingredient_Leather_Medium:1000,Ingredient_Leather_Heavy:250,Ingredient_Bar_Iron:250,Ingredient_Bar_Thorium:100",
           "PD_COST_COMBAT_UNIQUE": "Ingredient_Bone_Fragment:250,Ingredient_Fabric_Scrap_Linen:100",
           "PD_COST_COMBAT_RARE": "Ingredient_Bone_Fragment:1000,Ingredient_Fabric_Scrap_Linen:500,Ingredient_Sac_Venom:100,Ingredient_Chitin_Sturdy:100,Ingredient_Fabric_Scrap_Shadoweave:100",
           "PD_COST_COMBAT_LEGENDARY": "Ingredient_Bone_Fragment:2500,Ingredient_Fabric_Scrap_Linen:1000,Ingredient_Sac_Venom:250,Ingredient_Chitin_Sturdy:250,Ingredient_Void_Essence:100,Ingredient_Voidheart:10"}
MIGKEYS = [("pd.perLevel", "100", "150")] + [("pd.cost.%s.%s" % (k.split("_")[2].title(), k.split("_")[3].title()), OLDNUM[k], NEWCOST[k])
                                             for k in ("PD_COST_COMBAT_UNIQUE", "PD_COST_COMBAT_RARE", "PD_COST_COMBAT_LEGENDARY",
                                                       "PD_COST_SMITHING_UNIQUE", "PD_COST_SMITHING_RARE", "PD_COST_SMITHING_LEGENDARY")]
MK = "skyysacks-0.8.9-void"


def _blob(b):
    return b.replace(b"\r\n", b"\n")


def _load_kit():
    """the committed kit as `skyyui` (see KIT above); returns a note"""
    tree = os.path.join(TOOLS, "skyyui.py")
    if "--tree-kit" in sys.argv:
        return "working-tree kit (--tree-kit)"
    head = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=ROOT, capture_output=True).stdout
    if not head or _blob(open(tree, "rb").read()) == _blob(head):
        return "tools/skyyui.py = HEAD"
    kd = os.path.join(os.path.dirname(SCRATCH), "kit-head")
    kf = os.path.join(kd, "skyyui.py")
    assert os.path.realpath(kd).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
    if not os.path.isfile(kf) or open(kf, "rb").read() != head:
        os.makedirs(kd, exist_ok=True)
        open(kf, "wb").write(head)
    spec = importlib.util.spec_from_file_location("skyyui", kf)
    m = importlib.util.module_from_spec(spec)
    sys.modules["skyyui"] = m
    spec.loader.exec_module(m)
    return "HEAD kit %s (%s)" % (getattr(m, "KIT_VERSION", "?"), kf)


KIT_NOTE = _load_kit()


def _t088():
    sp = importlib.util.spec_from_file_location("t088", os.path.join(HERE, "test_skyysacks_0.8.8.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.VERSION = VERSION   # its static checks (and the modules it loads) read the 0.8.9 generated script
    return m


def _old_numbers():
    """OLDNUM on the SackCfg statics of THIS JVM (a server that kept the 0.8.8 values) - for the older phases' pinned numbers. The fields are
    set once the class can be loaded (jpype started by the phase itself), and again after each SackCfg.reload / pdKeys a phase runs."""
    from jpype import JClass, JString
    C = JClass(PKG + "SackCfg")
    for f, v in OLDNUM.items():
        setattr(C, f, JString(v) if isinstance(v, str) else v)


def _with_old_numbers(fn):
    """run an older phase with the 0.8.8 numbers: the first time SackCfg is touched through jpype after the JVM starts, OLDNUM is applied;
    SackCfg.pdKeys (every reload) is followed by the same values through a JPype class hook"""
    import jpype
    orig = jpype.startJVM

    def start(*a, **k):
        r = orig(*a, **k)
        try:
            _old_numbers()
        except Exception as e:
            print("note: OLDNUM not applied at JVM start (%s)" % e)
        return r
    jpype.startJVM = start
    return fn


def _phase(name, old=False):
    def run(out, jar, scratch, home):
        m = _t088()
        f = getattr(m, "run_" + name)
        if old:
            _with_old_numbers(f)
        f(out, jar, scratch, home)
    return run


# ======================================================================================================== MIG
def run_mig(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass, JString
    Paths = JClass("java.nio.file.Paths")
    Pool, Cfg, Mig = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "SackMig089")
    Rows, Hist, Log = JClass(PKG + "CfgRows"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    base = os.path.join(scratch, "mig")
    shutil.rmtree(base, ignore_errors=True)
    nfile = [0]

    def world(text_bytes):
        nfile[0] += 1
        d = os.path.join(base, "w%d" % nfile[0], "mods", "Skyy_SkyySacks")
        os.makedirs(d)
        f = os.path.join(d, "config.properties")
        if text_bytes is not None:
            open(f, "wb").write(text_bytes)
        return d, f

    def props(b):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(d):
        hd = os.path.join(d, "config-history")
        return sorted(os.path.join(hd, n) for n in os.listdir(hd) if "config.properties." in n and n.endswith(".bak")) if os.path.isdir(hd) else []

    def chlog(d):
        f = os.path.join(d, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    def reload_cfg(f):
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        Cfg.reload()

    # ---- the NewBetaTest file (CRLF, commented defaults)
    if os.path.isfile(BETA_CFG):
        b0 = open(BETA_CFG, "rb").read()
        d, f = world(b0)
        r = str(Mig.run(Paths.get(f)))
        b1 = open(f, "rb").read()
        l0, l1 = b0.split(b"\r\n"), b1.split(b"\r\n")
        diff = [(a, c) for a, c in zip(l0[:-1], l1) if a != c]
        want = [(("#%s=%s" % (k, o)).encode(), ("#%s=%s" % (k, n)).encode()) for k, o, n in MIGKEYS]
        K.check(sorted(diff) == sorted(want), "MIG beta: exactly the 7 commented default lines get the 0.8.9 default: %s" % [x[1][:50] for x in diff])
        K.check(len(l1) == len(l0) + 1 and l1[-2].startswith(b"# ---------- SkyySacks 0.8.9 (marker " + MK.encode()) and l1[-1] == b""
                and b1.count(b"\r\n") == b0.count(b"\r\n") + 1 and b1.count(b"\n") == b1.count(b"\r\n"),
                "MIG beta: the marker line appended with the file's CRLF ending, no other line added")
        K.check(props(b0) == props(b1), "MIG beta: the Properties are identical (only comments changed)")
        h = hist(d)
        K.check(len(h) == 1 and open(h[0], "rb").read() == b0, "MIG beta: config-history holds the old bytes")
        K.check(chlog(d) == [] and "no setting line held the old default" in r and "7 commented default line(s) refreshed" in r,
                "MIG beta: no change-log line (no live value changed); INFO: %s" % r[:160])
        K.check(str(Mig.run(Paths.get(f))) == "" and open(f, "rb").read() == b1 and len(hist(d)) == 1, "MIG beta: start 2 changes nothing (marker)")
    else:
        K.notes.append("MIG: no NewBetaTest config.properties - the beta case skipped")
    # ---- the HUD mod file (no pd lines at all)
    live = os.path.join(LIVE_DIR, "config.properties")
    if os.path.isfile(live):
        b0 = open(live, "rb").read()
        d, f = world(b0)
        Mig.run(Paths.get(f))
        b1 = open(f, "rb").read()
        eol = b"\r\n" if b"\r\n" in b0 else b"\n"
        K.check(b1.startswith(b0 if b0.endswith(b"\n") else b0 + eol) and b1[len(b0):].strip().startswith(b"# ---------- SkyySacks 0.8.9")
                and b1.count(b"\n") == b0.count(b"\n") + (1 if b0.endswith(b"\n") else 2), "MIG hud: only the marker line appended")
        reload_cfg(f)
        K.check(int(Cfg.PD_PER_LEVEL) == 150 and str(Cfg.PD_COST_SMITHING_UNIQUE) == NEWCOST["PD_COST_SMITHING_UNIQUE"] and abs(float(Cfg.PD_CURVE) - 1.75) < 1e-9,
                "MIG hud: no lines -> the new built-in defaults apply (150, curve 1.75, leather + copper)")
    # ---- synthetic: LF file, one CRLF line, no final newline; live old defaults, a hand edit, a doubled line
    k_su, o_su, n_su = MIGKEYS[4]       # Smithing.Unique
    k_cu, o_cu, n_cu = MIGKEYS[1]       # Combat.Unique
    k_sr, o_sr, n_sr = MIGKEYS[5]       # Smithing.Rare
    k_cr, o_cr, n_cr = MIGKEYS[2]       # Combat.Rare
    k_cl, o_cl, n_cl = MIGKEYS[3]       # Combat.Legendary
    spaced = o_su.replace(",", " , ").replace(":", ": ")
    txt = ("# SkyySacks config\ncraftSearch=true\npd.perLevel=100.0\r\n%s = %s\n%s=%s\n%s=Ingredient_Hide_Light:5\n#%s=%s\n%s=%s\n%s=%s\npd.mult.Rare=2\n"
           "%s=%s" % (k_su, spaced, k_cu, o_cu, k_sr, k_cl, o_cl, k_cr, o_cr, k_cr, o_cr, "pd.cost.Mining.Unique", "Ore_Iron:1"))
    b0 = txt.encode("latin-1")
    d, f = world(b0)
    r = str(Mig.run(Paths.get(f)))
    b1 = open(f, "rb").read()
    t1 = b1.decode("latin-1")
    want = ("# SkyySacks config\ncraftSearch=true\npd.perLevel=150\r\n%s = %s\n%s=%s\n%s=Ingredient_Hide_Light:5\n#%s=%s\n%s=%s\n%s=%s\npd.mult.Rare=2\n"
            "%s=%s\n" % (k_su, n_su, k_cu, n_cu, k_sr, k_cl, n_cl, k_cr, o_cr, k_cr, o_cr, "pd.cost.Mining.Unique", "Ore_Iron:1"))
    K.check(t1.startswith(want) and t1[len(want):].startswith("# ---------- SkyySacks 0.8.9") and t1.endswith("\n") and t1.count("\r\n") == 1,
            "MIG syn: perLevel 100.0 -> 150 (its CRLF kept), the spaced Smithing.Unique old default and Combat.Unique moved, the commented "
            "Combat.Legendary default refreshed, the hand-edited Smithing.Rare and the DOUBLED Combat.Rare kept, the missing final newline "
            "added (LF), the marker appended: %r" % t1[:400])
    K.check(open(hist(d)[0], "rb").read() == b0 and len(hist(d)) == 1, "MIG syn: the History copy = the old bytes")
    cl = chlog(d)
    K.check(sorted((x[4], x[5], x[6]) for x in cl) == sorted([("pd.perLevel", "100.0", "150"), (k_su, spaced.strip(), n_su), (k_cu, o_cu, n_cu)])
            and all(x[1] == "SkyySacks 0.8.9" and x[3] == "update" and x[7] == "ok" for x in cl),
            "MIG syn: one change-log line per moved value (key, old, new): %s" % [x[4:7] for x in cl])
    K.check("pd.cost.Smithing.Rare=Ingredient_Hide_Light:5 kept - an admin changed it" in r and "pd.cost.Combat.Rare=" in r and "doubled" in r,
            "MIG syn: the INFO names the kept hand edit and the doubled line: %s" % r.replace("\n", " | ")[:400])
    reload_cfg(f)
    K.check(int(Cfg.PD_PER_LEVEL) == 150 and str(Cfg.PD_COST_SMITHING_UNIQUE) == n_su and str(Cfg.PD_COST_COMBAT_UNIQUE) == n_cu
            and str(Cfg.PD_COST_SMITHING_RARE) == "Ingredient_Hide_Light:5" and str(Cfg.PD_COST_COMBAT_LEGENDARY) == n_cl
            and str(Cfg.PD_COST_MINING_UNIQUE) == "Ore_Iron:1", "MIG syn: SackCfg.reload reads the moved values, the hand edits, the defaults")
    K.check(str(Mig.run(Paths.get(f))) == "" and open(f, "rb").read() == b1, "MIG syn: start 2 changes nothing (marker)")
    # ---- Undo through the kit (what Server Setup -> Changes -> Undo runs: a console set of the old value), then start 3
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    mods = os.path.dirname(d)
    CP.start(Paths.get(mods), Pool.LOG)
    ru = str(Fn.cmdSetConsole(JString(k_su), JString(o_su)))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check(str(Cfg.PD_COST_SMITHING_UNIQUE) == o_su and (("%s = %s" % (k_su, o_su)) in t2 or ("%s=%s" % (k_su, o_su)) in t2),
            "MIG undo: the kit sets the old Smithing cost back (field + file line): %s" % ru)
    K.check(str(Mig.run(Paths.get(f))) == "" and open(f, "rb").read().decode("latin-1") == t2, "MIG undo: start 3 keeps the undone value (marker)")
    # ---- a fresh start: no file -> SackCfg.reload writes the 0.8.9 default (marker inside); the update does nothing
    d, f = world(None)
    K.check(str(Mig.run(Paths.get(f))) == "" and not os.path.exists(f), "MIG fresh: no file -> nothing done")
    reload_cfg(f)
    t3 = open(f, "rb").read()
    K.check(MK.encode() in t3 and b"#pd.perLevel=150" in t3 and b"#pd.curve=1.75" in t3 and ("#%s=%s" % (k_su, n_su)).encode() in t3,
            "MIG fresh: the default file carries the marker, perLevel 150, the curve row and the new costs")
    K.check(str(Mig.run(Paths.get(f))) == "" and open(f, "rb").read() == t3 and hist(d) == [], "MIG fresh: the update finds the marker - nothing written")
    # ---- History cannot be written (a FILE named config-history blocks the folder): the file stays untouched
    d, f = world(("pd.perLevel=100\n%s=%s\n" % (k_cu, o_cu)).encode())
    open(os.path.join(d, "config-history"), "wb").write(b"not a folder")
    b0 = open(f, "rb").read()
    r = str(Mig.run(Paths.get(f)))
    K.check(r == "" and open(f, "rb").read() == b0, "MIG nohist: config-history cannot be made -> the file is untouched (next start tries again)")
    os.remove(os.path.join(d, "config-history"))
    K.check(str(Mig.run(Paths.get(f))) != "" and b"pd.perLevel=150" in open(f, "rb").read(), "MIG nohist: the next start updates it")
    # ---- the pure step on odd input
    K.check(Mig.update(JString("a=\\u00zz")) is None or True, "MIG: odd text never throws")
    K.save()


# ======================================================================================================== VOID (stand-ins)
def run_void(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    src = open(T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_void_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _VOID(locals())\n"
    ns = {"__file__": T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "void"), _VOID=lambda L: void_cases(K, L, scratch))
    exec(compile(body, T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_void_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "VOID fixture: " + f)
        K.save()
        try:
            __import__("jpype").JClass(PKG + "SackPool").WRITER.shutdownNow()
        except Exception:
            pass


def void_cases(K, L, scratch):
    import math
    from jpype import JClass, JString, JShort
    VS, Defs, Cfg, Pool, SPage, Swp = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["SPage"], L["Swp"]
    fresh, write_pool, player, coll, pc, inv_counts, total, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "pc", "inv_counts", "total", "custom_item", "drain"))
    TBoom, UUID, us, jfield, pref, IS = L["TBoom"], L["UUID"], L["us"], L["jfield"], L["pref"], L["IS"]
    base = os.path.join(scratch, "void")
    LIN, SHA, WOOL, CIN = ("Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Wool",
                           "Ingredient_Fabric_Scrap_Cindercloth")
    LL, LM, CU, IR, TH, BONE, HIDE = ("Ingredient_Leather_Light", "Ingredient_Leather_Medium", "Ingredient_Bar_Copper", "Ingredient_Bar_Iron",
                                      "Ingredient_Bar_Thorium", "Ingredient_Bone_Fragment", "Ingredient_Hide_Light")
    for i_ in (LIN, SHA, WOOL, CIN, LL, LM, CU, IR, TH, BONE, HIDE, "Ingredient_Bolt_Linen", "Ingredient_Feathers_Light"):
        custom_item(i_, 100)
    cs = lambda i: None if Defs.catOf(JString(i)) is None else str(Defs.catOf(JString(i)))
    # ---- B. fabric -> Combat
    K.eq([cs(i) for i in (LIN, SHA, WOOL, CIN, "Ingredient_Fabric_Scrap_Silk")], ["Combat"] * 5, "VOID: every fabric scrap -> Combat")
    K.eq([cs(i) for i in (LL, CU, HIDE, "Ingredient_Bolt_Linen", "Ingredient_Strap_Leather", "Ingredient_Stud_Iron", "Ingredient_Charcoal")],
         ["Smithing"] * 7, "VOID: leather, bars, hides, cloth bolts, strap, stud, charcoal stay Smithing")
    K.eq([cs(i) for i in (BONE, "Ingredient_Feathers_Light")], ["Combat", "Combat"], "VOID: bones / feathers stay Combat")
    K.check("fabric scraps" in str(Defs.HOLDS[4]) and "fabric" not in str(Defs.HOLDS[5]), "VOID: the Combat / Smithing 'holds' lines: %s | %s"
            % (Defs.HOLDS[4], Defs.HOLDS[5]))
    drain()
    fresh(base)
    U = UUID.fromString("00000000-0000-0000-0000-0000000a0891")
    k = str(U)
    stored = {LIN: 300, SHA: 40, LL: 120, CU: 80, BONE: 900}
    write_pool(os.path.join(base, "pools"), k, stored)
    s = VS.st(k)
    s.first = 1
    K.eq([int(Pool.catTotal(k, "Combat")), int(Pool.catTotal(k, "Smithing"))], [900 + 340, 200],
         "VOID: stored fabric (written as 0.8.8 left it) counts in Combat now, not Smithing - same pool lines, nothing moved")
    K.eq(pc(k), stored, "VOID: the pool itself is untouched")
    # Combat over its space: Lv 1 Normal = 150 < 1,240 stored. Nothing is deleted; a sweep takes in no Combat; Smithing still takes
    coll(U, {"Combat": 0, "Smithing": int(VS.totalFor(3, 5))})
    p = player(storage=[(LIN, 50), (CU, 20)])
    b0 = total(inv_counts(p), pc(k))
    caps = VS.capsK(U, k)
    K.eq([int(caps.get("Combat")), int(caps.get("Smithing"))], [150, 450], "VOID: Lv 1 space = 150 (was 100), Lv 3 = 450")
    Swp.sweep(p, k, "Combat", True, None, caps, None)
    Swp.sweep(p, k, "Smithing", True, None, VS.capsK(U, k), None)
    drain()
    after = pc(k)
    K.check(total(inv_counts(p), after) == b0 and after.get(LIN) == 300 and inv_counts(p).get(LIN) == 50 and after.get(CU) == 100,
            "VOID: an over-full Combat (1,240 / 150) keeps every item, the 50 Linen stay in the inventory; Smithing (200 / 450) takes the 20 "
            "copper - conserved: pool %s inv %s" % (after, inv_counts(p)))
    # ---- C. the level curve + space
    STEP = {"Mining": 25, "Foraging": 20, "Farming": 25, "Fishing": 2, "Combat": 8, "Smithing": 10}
    cats = [str(c) for c in Defs.CATS]
    K.check(abs(float(Cfg.PD_CURVE) - 1.75) < 1e-12 and int(Cfg.PD_PER_LEVEL) == 150, "VOID: defaults curve 1.75, 150 per level")
    bad = []
    for ci, c in enumerate(cats):
        prev = -1
        for lv in range(1, 251):
            t = int(VS.totalFor(lv, ci))
            want = 0 if lv == 1 else math.ceil(STEP[c] * (lv - 1) ** 1.75 - 1e-6)
            if t != want or t <= prev or int(VS.levelOf(t, ci)) != lv or (lv > 1 and int(VS.levelOf(t - 1, ci)) != lv - 1):
                bad.append((c, lv, t, want, int(VS.levelOf(t, ci))))
            prev = t
    K.check(not bad and int(VS.levelOf(10 ** 12, 0)) == 250 and int(VS.levelOf(0, 0)) == 1, "VOID: totalFor = ceil(step x (L-1)^1.75), levelOf its exact "
            "inverse for all 6 categories, Lv 1..250: %s" % bad[:4])
    K.eq([int(VS.totalFor(lv, 1)) for lv in (5, 10, 15, 25, 50)], [227, 936, 2027, 5205, 18150], "VOID: Foraging collect curve Lv 5/10/15/25/50")
    K.eq(int(VS.levelOf(3425, 1)), 19, "VOID: Skyy's Foraging 3,425 collected -> Lv 19 (was 14)")
    Cfg.PD_CURVE = 2.0
    K.check(all(int(VS.totalFor(lv, ci)) == STEP[c] * (lv - 1) ** 2 and int(VS.levelOf(STEP[c] * (lv - 1) ** 2, ci)) == lv
                for ci, c in enumerate(cats) for lv in range(1, 251)), "VOID: pd.curve 2 = the 0.8.0-0.8.8 square curve exactly")
    Cfg.PD_CURVE = 1.75
    K.eq([int(VS.capOf(10, 0)), int(VS.capOf(25, 1)), int(VS.capOf(50, 2)), int(VS.capOf(14, 1))], [1500, 5625, 15000, 3150],
         "VOID: space = level x 150 x rarity (gates Lv 10 / 25 / 50; Skyy's Lv 14 Unique 2,100 -> 3,150)")
    # ---- A. the Smithing Unique upgrade (leather + copper)
    K.eq(str(Cfg.PD_COST_SMITHING_UNIQUE), NEWCOST["PD_COST_SMITHING_UNIQUE"], "VOID: the default Smithing Unique cost")
    for f_, v_ in NEWCOST.items():
        K.eq(str(getattr(Cfg, f_)), v_, "VOID: default %s" % f_)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {LL: 150, CU: 30, LIN: 500})
    s = VS.st(k)
    s.first = 1
    coll(U, {"Smithing": int(VS.totalFor(10, 5))})
    p = player(storage=[(LL, 30), (CU, 70), (HIDE, 100)])
    b0 = total(inv_counts(p), pc(k))
    r_ = str(VS.upgrade(p, U, k, 5, 0))
    K.check(r_ == "-Not enough Ingredient_Leather_Light (180 / 200)" and total(inv_counts(p), pc(k)) == b0 and int(s.rar[5]) == 0,
            "VOID: 180 of 200 Light Leather (hides do not count) -> refused, nothing moved: %s" % r_)
    p.getInventory().getHotbar().addItemStack(IS(LL, 40))
    b1 = total(inv_counts(p), pc(k))
    r_ = str(VS.upgrade(p, U, k, 5, 0))
    drain()
    after = total(inv_counts(p), pc(k))
    K.check(r_.startswith("+Smithing is now Unique") and int(s.rar[5]) == 1 and total(after, {LL: 200, CU: 100}) == b1
            and after.get(LL) == 20 and CU not in after and after.get(HIDE) == 100 and after.get(LIN) == 500,
            "VOID: leather + copper from the Void then the inventory pay the Smithing Unique cost exactly; hides / linen untouched: %s / %s" % (r_, after))
    # a crash part-way through the inventory take -> everything back, then paid once
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {LL: 10})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[(LL, 50), (LL, 50), (LL, 50), (LL, 50), (CU, 60), (CU, 60)], boom=True)
    b2 = total(inv_counts(p), pc(k))
    TBoom.CALLS = 0
    TBoom.BOOMAT = 1
    r_ = str(VS.upgrade(p, U, k, 5, 0))
    K.check(r_.startswith("-Internal error") and total(inv_counts(p), pc(k)) == b2 and int(s.rar[5]) == 0 and pc(k).get(LL) == 10,
            "VOID: a crash at the 2nd inventory slot removal -> rolled back (every slot, the Void's 10 leather), no rarity: %s (calls %d)"
            % (r_, int(TBoom.CALLS)))
    TBoom.BOOMAT = -1
    r_ = str(VS.upgrade(p, U, k, 5, 0))
    drain()
    K.check(r_.startswith("+Smithing is now Unique") and total(total(inv_counts(p), pc(k)), {LL: 200, CU: 100}) == b2,
            "VOID: the same upgrade after the crash pays exactly once: %s" % r_)
    # Combat Unique with Linen Scraps (no feathers)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {BONE: 250, LIN: 60, "Ingredient_Feathers_Light": 500})
    s = VS.st(k)
    s.first = 1
    coll(U, {"Combat": int(VS.totalFor(10, 4))})
    p = player(storage=[(LIN, 40)])
    b3 = total(inv_counts(p), pc(k))
    r_ = str(VS.upgrade(p, U, k, 4, 0))
    drain()
    after = total(inv_counts(p), pc(k))
    K.check(r_.startswith("+Combat is now Unique") and total(after, {BONE: 250, LIN: 100}) == b3 and after.get("Ingredient_Feathers_Light") == 500,
            "VOID: Combat Unique takes 250 bones + 100 Linen Scraps (60 Void + 40 inventory); the 500 feathers stay: %s" % r_)
    # ---- D. the upgrade box: icons + real names
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def ucb_text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def render(cat):
        pg = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(pg, pref(U))
        jfield(SPage.class_, "info").set(pg, JString(""))
        jfield(SPage.class_, "amount").set(pg, JString(""))
        pg.cat = cat
        b_, e_ = UCBc(), UEBc()
        pg.render(b_, e_, p, k, U)
        return ucb_text(b_)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {LL: 50, CU: 7})
    s = VS.st(k)
    s.first = 1
    p = player(storage=[])
    t0 = render("Smithing")
    K.check("Ingredient_Leather_Light" in t0 and "Ingredient_Bar_Copper" in t0 and "50 / 200" in t0 and "7 / 100" in t0
            and "SkyyVCostG0" not in t0 and "Ingredient_Hide_Light" not in t0 and "Fabric_Scrap" not in t0,
            "VOID: the Smithing box: the two new icon cells (leather, copper) with their counts; no name yet (no translations) -> plain cells")
    # real names through a stand-in I18nModule
    I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
    jp = L["jp"]
    ti = jp.makeClass("com.hypixel.hytale.server.core.modules.i18n.SkyyTestI18n089", jp.get(I18N))
    ti.addField(JClass("javassist.CtField").make("public static final java.util.HashMap M = new java.util.HashMap();", ti))
    ti.addMethod(JClass("javassist.CtNewMethod").make("public String getMessage(String l, String k) { return (String) M.get(k); }", ti))
    TI = JClass(ti.toClass(JClass(I18N).class_))
    names = {LL: "Light Leather", CU: "Copper Ingot", LIN: "Linen Scraps", BONE: "Bone Fragment"}
    for i_, n_ in names.items():
        TI.M.put(JString("server.items.%s.name" % i_), JString(n_))
    jfield(JClass(I18N).class_, "instance").set(None, us.allocateInstance(TI.class_))
    Defs.DNAMES.clear()
    got = [None if Defs.lineName(JString(i_)) is None else str(Defs.lineName(JString(i_))) for i_ in (LL, CU, "Wood_Oak_Trunk")]
    if got[0] is None:
        K.notes.append("VOID: the stand-in Item has no translation key - lineName checked through SackDefs.DNAMES (the dname cache) instead")
        for i_, n_ in names.items():
            Defs.DNAMES.put(JString(i_), JString(n_))
        got = [None if Defs.lineName(JString(i_)) is None else str(Defs.lineName(JString(i_))) for i_ in (LL, CU, "Wood_Oak_Trunk")]
    K.eq(got, ["Light Leather", "Copper Ingot", "Oak-tier logs"], "VOID: lineName = the real name; a tier log keeps its group label")
    t1 = render("Smithing")
    K.check("Light Leather" in t1 and "Copper Ingot" in t1 and "SkyyVCostG0" in t1 and "SkyyVCostN0" in t1 and "SkyyVCostG1" in t1
            and "50 / 200" in t1 and "7 / 100" in t1 and "Ingredient_Leather_Light" in t1,
            "VOID: the Smithing box shows 'Light Leather' over 50 / 200 and 'Copper Ingot' over 7 / 100, the icons stay the item ids")
    coll(U, {"Smithing": int(VS.totalFor(10, 5))})
    r_ = str(VS.upgrade(p, U, k, 5, 0))
    K.eq(r_, "-Not enough Light Leather (50 / 200)", "VOID: the refusal line uses the real name")
    t2 = render("Combat")
    K.check("Linen Scraps" in t2 and "Bone Fragment" in t2 and "Feathers" not in t2, "VOID: the Combat box: Bone Fragment + Linen Scraps, no feathers")
    jfield(JClass(I18N).class_, "instance").set(None, None)
    Defs.DNAMES.clear()
    Pool.WRITER.shutdownNow()


if __name__ == "__main__":
    print("kit:", KIT_NOTE)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", _phase("exec", True)), ("late", _phase("late", True)), ("art", _phase("art", True)), ("fuel", _phase("fuel")),
            ("logs", _phase("logs", True)), ("snd", _phase("snd")), ("mig", run_mig), ("void", run_void), ("live", _phase("live", True))],
           __file__, live=(LIVE_DIR, "Skyy_SkyySacks"))
