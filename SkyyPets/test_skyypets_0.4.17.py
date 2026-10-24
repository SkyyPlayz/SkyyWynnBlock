"""Harness for SkyyPets 0.4.17 (Beastmastery hatching: Warm Nest + Burrow Nursery; Pet Fang x1.5 + the one-time PetsMigW15; tools/pets_0_4_17_patch.py
+ tools/trees_v3_effects.py r062_apply). Build first:
    python tools/pets_0_4_17_patch.py && python SkyyPets/build_skyypets_0.4.17.py
    python SkyyPets/test_skyypets_0.4.17.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes, 0.4.16's patch still regenerates 0.4.16 byte for byte; one class added (PetsMigW15), no
                 system / command; line endings kept; the jar: no non-class entry added / removed / changed except manifest.json
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.16 -> 0.4.17, engine-access audit
  HX    EXECUTED (stub tree:fn:level = SkyyTrees' answer): Warm Nest 0-4 ranks = 0 / 5 / 10 / 15 / 20 % off every Hatchery wait (a rank over the
                 max clamps, the 1 s cache, the Server Setup per-rank / ceiling rows live, the 90 % clamp), no SkyyTrees = the full wait; Burrow
                 Nursery + Gentle Hand = 5 extra slots (7), the 10-extra clamp; the REAL paths with the player: place ("it hatches in 1m 36s"),
                 slotSub / headText, ready + the "ready to hatch" chat line (tickRec), Hatch refused while still hatching and allowed once the
                 cut wait passed, a respec (ranks gone) makes the same egg wait again; dragon eggs too
  W15   EXECUTED PetsMigW15 on scratch trees.properties: the four Pet Fang lines on the old defaults (CRLF, odd spacing) -> the new ones,
                 every other byte kept, History copy byte-equal, 4 Changes lines, marker; a hand-edited line kept (+ note); a file already new;
                 no file; a second start = nothing; PetsCfg.loadV3 then reads 2.6 / 1.5; a fresh trees.properties holds the new rows
  rl/pt/sl/mig/dr/t/r/m/f/dg/vw/st/el410   0.4.16's phases EXECUTED on this jar
  live  start twice on a scratch COPY of the live Skyy_SkyyPets folder: the five one-time updates (W15 moves the live Pet Fang lines still on
                 the old defaults), every pet file reads, start 2 writes nothing
NOT COVERED (UNVERIFIED in game): the header text's fit on the Hatchery tab; SkyyTrees' real tree:fn:level (the SkyyTrees 0.6.2 harness runs
the Trees side; the bridge shape is the 0.4.5 contract).
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "bm1", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s416 = importlib.util.spec_from_file_location("test_skyypets_0_4_16", os.path.join(HERE, "test_skyypets_0.4.16.py"))
T416 = importlib.util.module_from_spec(_s416)
_s416.loader.exec_module(T416)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T415, T414, T413, T412, T411, T410, T44, T41 = T416.T415, T416.T414, T416.T413, T416.T412, T416.T411, T416.T410, T416.T44, T416.T41

VERSION = "0.4.17"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.16.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.16.py")
PATCH = os.path.join(TOOLS, "pets_0_4_17_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T416, T415, T414, T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T416, T415, T414, T413, T412, T411):
    _m.JAR = JAR
T414.GEN = GEN
T415.GEN = GEN
T416.GEN = GEN
EXPECT = {   # checked 2026-10-24 against the harness's class compare 0.4.16 -> 0.4.17 (every member is a change of tools/pets_0_4_17_patch.py)
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit's row tables (+ the 4 new rows)
    "PetsCfg": ["+f V3P30", "+f V3P31", "+f V3X30", "+f V3X31", "~<clinit>", "~m applyAll", "~m loadV3", "~m seed", "~m v3most", "~m v3per"],   # applyAll / seed: the VERSION in the default text
    "PetV3": ["+f CUT_CAP", "+f HCC", "+m hatchCut", "~<clinit>", "~m reads"],                       # reads: the reader list (+ the two keys)
    "PetHatchery": ["+m left", "+m ready", "+m slotSub", "+m waitMs", "~m eggCell", "~m headText", "~m hatchLocked", "~m placeLocked", "~m tickRec"],
    "PetsPage": ["~m build", "~m slotClick"],
    "PetsMigP5": ["~m mgLog", "~m run"], "PetsMigS2": ["~m run"],                                     # VERSION strings
    "SkyyPetsPlugin": ["~m setup"],
}
ADDED = ["PetsMigW15"]
if "--expect-dump" in sys.argv:
    EXPECT = {}
WN, BN, GH = "Skill.Beastmastery.b3.r2c", "Skill.Beastmastery.b2.r4c", "Skill.Beastmastery.b3.r1b"
FANG = [("tree.Combat.b3.r3a.xp.per", "2", "2.6"), ("tree.Combat.b3.r3a.xp.max", "15", "19.5"), ("tree.Combat.b3.r3a.dmg.per", "1", "1.5"), ("tree.Combat.b3.r3a.dmg.max", "7.5", "11.25")]


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.17 - build script') and g.count('VERSION = "0.4.17"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls(") + 1,
            "S one class added (PetsMigW15), no system or command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_16_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(n for n in set(z.namelist()) - set(oz.namelist()) if not n.endswith(".class")), [], "S no new non-class entry")
    K.eq(sorted(set(oz.namelist()) - set(z.namelist())), [], "S no entry removed")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["manifest.json"], "S the changed non-class entries = manifest.json")
    K.check(sorted(n for n in set(z.namelist()) - set(oz.namelist())) == ["com/skyy/pets/PetsMigW15.class"], "S the one new class file")
    # fixer (critic 3): the Warm Nest Server Setup rows say what they cut ("Hatch time cut", not a bare "Hatch")
    allcls = b"".join(z.read(n) for n in z.namelist() if n.endswith(".class"))
    K.check(b"Warm Nest Hatch time cut a rank" in allcls and b"Warm Nest Hatch time cut most" in allcls and b"Warm Nest Hatch a rank" not in allcls,
            "S FIX3 the Warm Nest rows are labelled 'Hatch time cut'")
    K.save()


def _stub(W):
    from jpype import JClass, JProxy
    ranks = {}
    W["BR"].put("tree:fn:level", JProxy("java.util.function.Function", dict={"apply": lambda a: JClass("java.lang.Integer").valueOf(int(ranks.get(str(a[1]), 0)))}))
    return ranks


# ======================================================================================================== HX: hatching, EXECUTED
def run_hx(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "hx")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    P_ = lambda n: JClass(PKG + n)
    Hy, V3, Cfg, Defs, Eng, Store = P_("PetHatchery"), P_("PetV3"), P_("PetsCfg"), P_("PetEggDefs"), P_("PetsEng"), P_("PetStore")
    keys = [str(x) for x in V3.KEYS]
    effs = [str(x) for x in V3.EFF]
    K.check(keys[-2:] == [WN, BN] and effs[-2:] == ["hatchspd", "hatch"], "HX PetV3: the two rows are the last two (%s)" % keys[-2:])
    rd = str(V3.READS)
    K.check(WN in rd and BN in rd and GH in rd, "HX tree:reads:SkyyPets lists Warm Nest + Burrow Nursery (+ Gentle Hand)")
    iw = keys.index(WN)
    ranks = _stub(W)
    told = []
    names = W["names"]
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(names)), "byName": lambda n: None,
                                            "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: told.append(str(t))})

    def setr(d):
        ranks.clear()
        ranks.update(d)
        V3.HSC.clear()
        V3.HCC.clear()
    u, k, r = T44._mk(W, 9701)
    E = "Skyy_PetEgg_Combat_Common"
    base = int(Hy.waitMs(E))
    K.eq(base, 120000, "HX a Common egg waits 120 s (pets.hatch.wait.common)")
    setr({})
    K.check(float(V3.hatchCut(u)) == 0.0 and int(Hy.waitMs(E, u)) == base and "hatch time" not in str(Hy.headText(r, u)), "HX no rank = the full wait, no header note")
    for rk in range(1, 6):
        setr({WN: rk})
        want = min(rk, 4) * 0.05
        K.check(abs(float(V3.hatchCut(u)) - want) < 1e-9 and int(Hy.waitMs(E, u)) == int(round(base * (1 - want))),
                "HX Warm Nest %d = -%d %% (%d ms)%s" % (rk, round(want * 100), int(Hy.waitMs(E, u)), " (over the max: clamped to 4)" if rk > 4 else ""))
    setr({WN: 4})
    K.check("hatch time -20%" in str(Hy.headText(r, u)), "HX the header says the cut: %s" % Hy.headText(r, u))
    ranks[WN] = 1
    K.check(abs(float(V3.hatchCut(u)) - 0.2) < 1e-9, "HX the cut is cached for 1 s")
    V3.HCC.clear()
    K.check(abs(float(V3.hatchCut(u)) - 0.05) < 1e-9, "HX after the cache: rank 1 = 5 %")
    # the Server Setup rows (per rank / ceiling) are live; the 90 % clamp
    P0, X0 = float(getattr(Cfg, "V3P%d" % iw)), float(getattr(Cfg, "V3X%d" % iw))
    K.check((P0, X0) == (5.0, 20.0), "HX Server Setup defaults: 5 %% a rank, at most 20 %% (%s, %s)" % (P0, X0))
    setattr(Cfg, "V3P%d" % iw, 50.0)
    setr({WN: 4})
    K.check(abs(float(V3.hatchCut(u)) - 0.2) < 1e-9, "HX per rank 50 %: the ceiling row (20 %) holds")
    setattr(Cfg, "V3X%d" % iw, 1000.0)
    V3.HCC.clear()
    K.check(abs(float(V3.hatchCut(u)) - 0.9) < 1e-9 and int(Hy.waitMs(E, u)) == 12000, "HX ceiling 1000 %: the code's 90 % clamp (never an instant hatch)")
    setattr(Cfg, "V3P%d" % iw, P0)
    setattr(Cfg, "V3X%d" % iw, X0)
    # no SkyyTrees (no tree:fn:level) = the full wait
    W["BR"].remove("tree:fn:level")
    V3.HCC.clear()
    K.check(float(V3.hatchCut(u)) == 0.0 and int(Hy.waitMs(E, u)) == base, "HX no SkyyTrees: the full wait (today's behaviour)")
    ranks = _stub(W)
    # Burrow Nursery + Gentle Hand slots
    hs = int(Cfg.HATCH_SLOTS)
    setr({BN: 2})
    K.check(int(Hy.extra(u)) == 2 and int(Hy.slots(u)) == hs + 2, "HX Burrow Nursery 2 = +2 Hatchery slots (%d)" % int(Hy.slots(u)))
    setr({BN: 2, GH: 3})
    K.check(int(Hy.extra(u)) == 5 and int(Hy.slots(u)) == hs + 5 and "(5 from Beastmastery)" in str(Hy.headText(r, u)), "HX + Gentle Hand 3 = 5 extra (%s)" % Hy.headText(r, u))
    setr({BN: 9, GH: 3})
    K.check(int(Hy.extra(u)) == 5, "HX a rank over Burrow Nursery's max clamps to 2")
    W["BR"].put("pets:hatch:slots:" + str(u), JClass("java.lang.Integer").valueOf(8))
    K.check(int(Hy.extra(u)) == 10 and int(Hy.slots(u)) == hs + 10, "HX the bridge key 8 + 5 stops at 10 extra")
    W["BR"].remove("pets:hatch:slots:" + str(u))
    # the REAL paths with the player: place
    setr({WN: 4})
    inv = T41.Inv({E: 2})
    p1 = T44._place(W, u, inv, E)
    K.check(p1[0].startswith("+") and "it hatches in 1m 36s" in p1[0], "HX place with Warm Nest 4: %s" % p1[0])
    # a slot line placed 100 s ago: ready only with the cut (96 s), slotSub / tickRec / hatch follow it
    now = int(Hy.now())
    n = hs + 1
    r.set("hatchery.%d" % n, "%s|%d|hx1|inv" % (E, now - 100000))
    ln = Hy.line(r, n)
    K.check(not bool(Hy.ready(ln, now)) and bool(Hy.ready(ln, now, u)) and str(Hy.slotSub(ln, now, u)).startswith("READY"), "HX 100 s in: ready with the cut, not without (%s)" % Hy.slotSub(ln, now, u))
    setr({})
    K.check(not bool(Hy.ready(ln, now, u)) and "20s left" in str(Hy.slotSub(ln, now, u)), "HX a respec (no rank): the same egg waits again (%s)" % Hy.slotSub(ln, now, u))
    told.clear()
    Hy.NOTIFIED.clear()
    Hy.tickRec(u, r, T41.proxy_inv(T41.Inv({})), Hy.now())
    K.check(not [t for t in told if "ready to hatch" in t], "HX tickRec without the cut: no ready line yet")
    h0 = [str(x) if x is not None else None for x in Hy.hatch(u, n, "hx1", "harness")]
    K.check(h0[0].startswith("-Still hatching") and "20s left" in h0[0], "HX Hatch refused while still hatching: %s" % h0[0])
    setr({WN: 4})
    Hy.tickRec(u, r, T41.proxy_inv(T41.Inv({})), Hy.now())
    K.check(len([t for t in told if "ready to hatch" in t]) == 1, "HX tickRec with the cut: ONE 'ready to hatch' line (%s)" % told[-1:])
    Hy.CLICK.clear()
    h1 = [str(x) if x is not None else None for x in Hy.hatch(u, n, "hx1", "harness")]
    K.check(h1[0].startswith("+") and r.get("hatchery.%d" % n) is None, "HX Hatch goes through once the cut wait passed: %s" % h1[0])
    # dragon eggs wait in a Hatchery slot too
    dg = [str(x) for x in Defs.IDS if bool(Defs.isDragon(str(x)))]
    if dg:
        dbase = int(Hy.waitMs(dg[0]))
        K.check(int(Hy.waitMs(dg[0], u)) == int(round(dbase * 0.8)), "HX a dragon egg: %d -> %d ms" % (dbase, int(Hy.waitMs(dg[0], u))))
    sev = [str(l) for l in W["PetsLog"].LINES if "SEVERE" in str(l)]
    K.check(not sev, "HX no SEVERE: %s" % sev[:3])
    K.save()


# ======================================================================================================== W15: the one-time update, EXECUTED
# (" -> " counts: one per moved line + the message's "Server Setup -> Changes")
def run_w15(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Mig, Cfg, Log = P_("PetsMigW15"), P_("PetsCfg"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    fresh = str(Cfg.V3_TEXT)
    K.check(all(("%s=%s\n" % (k, n)) in fresh for k, o, n in FANG) and "tree.Beastmastery.b3.r2c.hatchspd.per=5\n" in fresh and "tree.Beastmastery.b2.r4c.hatch.max=2\n" in fresh,
            "W15 a fresh trees.properties holds the new Pet Fang numbers + the two hatching rows")
    old_text = fresh
    for k, o, n in FANG:
        old_text = old_text.replace("%s=%s\n" % (k, n), "%s=%s\n" % (k, o))
    old_text = old_text.replace("tree.Combat.b3.r3a.dmg.per=1\n", "tree.Combat.b3.r3a.dmg.per = 1\n")     # odd spacing kept
    cases = {"crlf": old_text.replace("\n", "\r\n"), "lf": old_text, "hand": old_text.replace("tree.Combat.b3.r3a.xp.per=2\n", "tree.Combat.b3.r3a.xp.per=3\n"), "new": fresh}
    for tag, txt in cases.items():
        mods = os.path.join(scratch, "w15-" + tag)
        home = os.path.join(mods, "Skyy_SkyyPets")
        os.makedirs(home, exist_ok=True)
        f = os.path.join(home, "trees.properties")
        open(f, "wb").write(txt.encode("latin-1"))
        Log.LINES.clear()
        s = str(Mig.run(Paths.get(home)))
        after = open(f, "rb").read().decode("latin-1")
        marker = os.path.isfile(os.path.join(home, "migrations", "pets-w15.done"))
        if tag in ("crlf", "lf"):
            want = txt
            for k, o, n in FANG:
                want = want.replace("%s=%s" % (k, o), "%s=%s" % (k, n)).replace("%s = %s" % (k, o), "%s = %s" % (k, n))
            K.check(after == want and marker and s.count(" -> ") == 4 + 1, "W15 %s: the four Pet Fang lines moved, every other byte kept (spacing, line endings): %s" % (tag, s[:160]))
            hd = os.path.join(home, "config-history")
            hist = [os.path.join(dp, x) for dp, _d, fs in os.walk(hd) for x in fs]
            K.check(any(open(h, "rb").read() == txt.encode("latin-1") for h in hist), "W15 %s: the old file is in config-history byte for byte" % tag)
            ch = open(os.path.join(home, "config-changes.log"), encoding="utf-8").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else ""
            K.check(len([l for l in ch.splitlines() if "SkyyPets 0.4.17\t-\tupdate\ttree.Combat.b3.r3a." in l]) == 4, "W15 %s: 4 Changes lines (Undo in Server Setup): %s" % (tag, ch[-200:]))
            Cfg.loadV3(Paths.get(home))
            ix = [str(x) for x in P_("PetV3").KEYS].index("Skill.Combat.b3.r3a")
            K.check(abs(float(Cfg.v3per(ix)) - 0.026) < 1e-9 and abs(float(Cfg.v3per(ix + 1)) - 1.5) < 1e-9 and abs(float(Cfg.v3most(ix + 1)) - 11.25) < 1e-9,
                    "W15 %s: PetsCfg reads Pet Fang 2.6 %% XP / 1.5 %% damage (ceiling 11.25)" % tag)
        elif tag == "hand":
            K.check("tree.Combat.b3.r3a.xp.per=3\n" in after and "tree.Combat.b3.r3a.xp.max=19.5\n" in after and all(("%s %s -> %s" % f3) in s for f3 in FANG[1:]) and FANG[0][0] + " 2 -> " not in s and "kept hand-edited tree.Combat.b3.r3a.xp.per=3" in s,
                    "W15 a hand-edited line is kept (+ one INFO line), the other three move: %s" % s[-200:])
        else:
            K.check(after == txt and marker and "nothing to change" in s, "W15 a file already on the new numbers: untouched (%s)" % s[:120])
        s2 = str(Mig.run(Paths.get(home)))
        K.check(s2 == "" and open(f, "rb").read().decode("latin-1") == after, "W15 %s: a second start does nothing" % tag)
    mods = os.path.join(scratch, "w15-none")
    home = os.path.join(mods, "Skyy_SkyyPets")
    os.makedirs(home, exist_ok=True)
    s = str(Mig.run(Paths.get(home)))
    K.check("no trees.properties" in s and os.path.isfile(os.path.join(home, "migrations", "pets-w15.done")) and not os.path.isfile(os.path.join(home, "trees.properties")),
            "W15 no trees.properties: marker only (%s)" % s)
    K.save()


def run_mig(out, jar, scratch, home):
    f = T414._swap(T415.run_mig, T415, [(r"SkyyPets 0.4.15\t-\tupdate", r"SkyyPets 0.4.17\t-\tupdate")])     # the Changes line names this jar
    f(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)
    tp = os.path.join(home, "trees.properties")
    before = open(tp, encoding="latin-1").read() if os.path.isfile(tp) else ""
    on_old = [k for k, o, n in FANG if re.search(r"(?m)^\s*%s\s*[=:]\s*%s\s*$" % (re.escape(k), re.escape(o)), before)]

    def start():
        out_ = [str(P_(m).run(Paths.get(home))) for m in ("PetsCfgMig", "PetsCfgMig2", "PetsMigP5", "PetsMigS2", "PetsMigW15")]
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return out_, [int(x) for x in Store.scanAll()]
    s1, sc1 = start()
    t1 = T41.tree(home)
    changed = sorted(x for x in set(t0) | set(t1) if t0.get(x) != t1.get(x) and not x.startswith(("config-history", "migrations", "config.properties", "config-changes", "trees.properties")))
    K.eq(changed, [], "LIVE start 1 touches only config files")
    print("   live: Pet Fang lines on the old defaults %s; PetsMigW15: %s" % (on_old, s1[4][:240] or "(already done)"))
    after = open(tp, encoding="latin-1").read() if os.path.isfile(tp) else ""
    K.check(all(re.search(r"(?m)^\s*%s\s*[=:]\s*%s\s*$" % (re.escape(k), re.escape(dict((a, c) for a, b, c in FANG)[k])), after) for k in on_old), "LIVE the live Pet Fang lines on the old defaults moved (%d)" % len(on_old))
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    s2, sc2 = start()
    K.check(all(x == "" for x in s2) and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("hx", run_hx), ("w15", run_w15), ("rl", T416.run_rl), ("pt", T416.run_pt), ("sl", T415.run_sl), ("mig", run_mig),
                   ("dr", T415.run_dr), ("t", T415.run_t), ("r", T414.run_r), ("m", T412.run_m), ("f", T414.run_f), ("dg", T414.run_dg), ("vw", T411.run_vw),
                   ("st", T414.run_st), ("el410", T414.run_el), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
