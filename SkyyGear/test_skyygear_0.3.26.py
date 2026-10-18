"""Harness for SkyyGear 0.3.26 (tools/gear_0_3_26_patch.py header = Quirk's multitool / Harvester models, checked + the five Armory Untiered sets)
= the 0.3.25 harness (and through it the whole older chain) run on the 0.3.26 jar + S326 (the jar compare 0.3.25 -> 0.3.26, replacing S325) + H326
(inside the h319 child, after H319 .. H325, on the same booted engine), plus a --static phase (no jar):
    python tools/gear_0_3_26_patch.py && python SkyyGear/build_skyygear_0.3.26.py
    python SkyyGear/test_skyygear_0.3.26.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.26.py --static [--keep]

  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.26.py, compiles, line endings kept
       A  the anchors: VERSION; no new system / command / class; u26Update / u26Log / migrate0326 after has22 and before the setup call;
          the art block before the 0.3.23 size checks; G26_SHIP_REPOSED off; the 36 rows in the fresh block
  S326 the jar 0.3.25 -> 0.3.26: adds / removes nothing (no model, texture, icon or item JSON change while every Quirk build fails or
       G26_SHIP_REPOSED is off); changes only manifest.json + the classes S326_MUST / S326_MAY; every multitool / Harvester item JSON = 0.3.25's
  H326 (the h319 child, ONE booted engine) - real code:
       A  the fresh file (defaultsText) carries the 36 rows once; after a config apply GearCfg.UTAB holds the 18 ids with their levels
          (15-29, Hepta_Axe 45-59) next to the first batch; GearUtFx.parseRow reads every utfx row with no unknown word; GearUt.checkUt
          accepts every ut value
       B  u26Update on a 0.3.25-shaped file (the fresh text minus the block): the 36 rows + the marker at the END, nothing before changes,
          CRLF kept, 36 change-log rows (key, new); a second run = null (run-once marker); an admin's row in another case kept + noted, never
          doubled; u26Log = "<time> SkyyGear 0.3.26 - update ut[X] (none) <cols> ok" (Undo-able)
  NOT COVERED (smoke test / Skyy in game): migrate0326 on the real config.properties, real orange drops of the Armory ids (the stand-in engine
  has no Armory items: GearUt.ok needs the live item), Quirk's models in the hand (none ship this round - see the build's FIX list).
Scratch: tools/dev/scratch/g326/h326/gear/harness (full run) and .../h326/static (--static), deleted at the end unless --keep.
Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, json, shutil, zipfile, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
STATIC = "--static" in sys.argv
if STATIC:
    sys.dont_write_bytecode = True


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.26"
V325 = "0.3.25"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g326", "h326")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J325 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V325))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_26_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.26.py")
GEN325 = os.path.join(HERE, "build_skyygear_0.3.25.py")
ROOK = ["Rook%s%s" % (p, c) for c in ("Ghost", "Wraith") for p in ("Helm", "Chest", "Gauntlets", "Boots")] + ["RookHelmGhostOpen", "RookHelmWraithOpen"]
U26 = ROOK + ["GhostCalvary" + p for p in ("Helm", "Chest", "Gauntlets", "Leggings")] + ["TarnishedCrown", "VerdantAmulet", "GhostSword", "Hepta_Axe"]
assert len(U26) == len(set(U26)) == 18
ITEMS = (["Tool_Hatchet_Pickaxe_Multitool_%s_SkyWynn" % m for m in ("Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")]
         + ["Tool_Sickle_Harvester_" + m for m in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril")]
         + ["Tool_Sickle_Harvester_%s_SkyWynn" % m for m in ("Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")])

S326_MUST = {"GearCfg": "U26_ rows + u26Update / u26Log / migrate0326", "SkyyGearPlugin": "the migrate0326 call + the version text"}
S326_MAY = {"CfgFn": "config kit: the version", "CfgRows": "config kit: the rows", "CfgFile": "config kit", "CfgDefaults": "config kit: the defaults",
            "CfgKit": "config kit", "CfgPub": "config kit"}

# ---- the 0.3.25 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder (and THIS file)
if not STATIC:
    _H325 = os.path.join(HERE, "test_skyygear_0.3.25.py")
    _T325 = open(_H325, encoding="utf-8").read()
    _cut = _T325.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    sys.argv = [_H325, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--only", arg("--only")] if arg("--only") else []) + (["--out", arg("--out")] if arg("--out") else [])
    H325 = {"__name__": "skyygear_h325", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T325[:_cut], _H325 + " (library)", "exec"), H325)
    sys.argv = _argv
    if arg("--only"):
        _o = ",".join(sorted(set(("h319" if x in ("h321", "h322", "h323", "h325", "h326") else x) for x in arg("--only").split(","))))
        sys.argv[sys.argv.index("--only") + 1] = _o
    H323, H320, H319, H316 = H325["H323"], H325["H320"], H325["H319"], H325["H316"]
    H322 = H323["H322"]
    H321 = H322["H321"]
    for _h in (H325, H323, H322, H321, H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
else:
    FAILS, OKS = [], [0]


def check(cond, what):
    if STATIC:
        if cond:
            OKS[0] += 1
        else:
            FAILS.append(what)
            print("FAIL", what)
        return
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S326
def run_assets326():
    ea, eb = entries(J325), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["manifest.json"], "S326: 0.3.25 -> 0.3.26 adds / removes nothing and changes only the manifest "
          "(+ classes) - no Quirk model / texture / icon ships while her builds fail the held-tool check: added %s gone %s changed %s"
          % (added[:4], gone[:4], changed[:6]))
    man = eb["manifest.json"].decode("utf-8", "replace")
    check('"0.3.26"' in man and "ARMORY UNTIERED: Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword and Hepta Axe" in man, "S326: the manifest says 0.3.26 + the round")
    js = [n for n in eb if n.startswith("Server/Item/Items/SkyyGear/") and os.path.basename(n)[:-5] in ITEMS]
    check(len(js) == 25 and all(ea.get(n) == eb[n] for n in js), "S326: the 25 multitool / Harvester item JSONs = 0.3.25's (%d found)" % len(js))
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.25 -> 0.3.26: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S326_MUST) | set(S326_MAY), "S326: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S326_MUST) - set(S326_MAY)))
    check(set(S326_MUST) <= set(chg), "S326: every class the patch edits really changed: unchanged %s" % sorted(set(S326_MUST) - set(chg)))
    check(all(i.encode() in eb["com/skyy/gear/GearCfg.class"] for i in U26), "S326: GearCfg carries the 18 Armory ids (U26_GL)")


# ====================================================================================================== H326 (in the h319 child)
def _h326(L, K):
    from jpype import JClass, JString
    P = lambda n: JClass(PKG + n)
    Cfg, apply, FRESH = L["Cfg"], L["apply"], L["FRESH"]
    Ut, Fx = P("GearUt"), P("GearUtFx")
    Props, SR, SB = JClass("java.util.Properties"), JClass("java.io.StringReader"), JClass("java.lang.StringBuilder")

    def kc(cond, what):
        K.check(bool(cond), "H326 " + what)
    apply()
    fresh = str(FRESH)
    pf = Props()
    pf.load(SR(fresh))
    ut = dict((i, str(pf.getProperty("ut." + i))) for i in U26)
    fx = dict((i, str(pf.getProperty("utfx." + i))) for i in U26)
    kc(all(fresh.count("\nut.%s=" % i) == 1 and fresh.count("\nutfx.%s=" % i) == 1 for i in U26) and fresh.count(str(Cfg.U26_MARK_ID)) == 1,
       "A: the fresh file carries the 36 rows once + the marker")
    kc(ut["RookHelmGhost"] == "15,29,Hollow guard: take 3% less damage per piece (set 16%) but you move slower." and fx["RookChestWraith"] == "def hprp,taken-5 spd-2"
       and fx["RookBootsGhost"] == "def hprp,taken-5 spd-2" and fx["RookHelmWraithOpen"] == "def hprp,taken-3 spd-2" and fx["GhostCalvaryLeggings"] == "str spd,front+10 back-10"
       and fx["VerdantAmulet"] == "mp hpr,heal+25 dmg-15" and fx["GhostSword"] == "str lsteal,swing=fast taken+5"
       and ut["Hepta_Axe"] == "45,59,Hits 54% harder. Swings 40% slower. You take 10% more damage while held." and fx["Hepta_Axe"] == "str tdmg,swing=slow dmg+10 taken+10",
       "A: the rows are research/UT-Lines-Draft.md 2.1 as drafted (spot checks)")
    t = Cfg.UTAB
    tid = [str(x) for x in t[0]]
    lv = dict((tid[k], (int(t[1][k]), int(t[2][k]))) for k in range(len(tid)))
    kc(all(i in lv for i in U26) and all(lv[i] == ((45, 59) if i == "Hepta_Axe" else (15, 29)) for i in U26) and "Weapon_Sword_UT_Paperweight" in lv and len(tid) >= 40,
       "A: GearCfg.UTAB holds the 18 Armory ids (15-29, Hepta_Axe 45-59) next to the first batch (%d rows)" % len(tid))
    bad = []
    for i in U26:
        b = SB()
        r = Fx.parseRow(JString(fx[i]), b)
        if r is None or b.length() > 0:
            bad.append((i, str(b)))
    kc(not bad, "A: GearUtFx.parseRow reads every utfx row with no unknown word: %s" % bad[:3])
    cu = [(i, str(Ut.checkUt(JString("ut"), JString(ut[i])))) for i in U26 if Ut.checkUt(JString("ut"), JString(ut[i])) is not None]
    kc(not cu, "A: GearUt.checkUt accepts every ut value: %s" % cu[:3])
    # ============================================================== B: u26Update
    zl = fresh.split("\n")
    hi = zl.index(str(Cfg.U26_HEAD))
    blk = 2 + sum(int(x) for x in Cfg.U26_GS) + len(Cfg.U26_GC)
    old = "\r\n".join(x for k, x in enumerate(zl) if not (hi - 1 <= k < hi + blk))
    kc(str(Cfg.U26_MARK_ID) not in old and "ut.GhostSword=" not in old and "ut.Weapon_Sword_UT_Paperweight=" in old, "B: a 0.3.25-shaped file (the fresh text minus the block)")
    r = Cfg.u26Update(old)
    nt = str(r[0]) if r is not None else ""
    pn = Props()
    pn.load(SR(nt))
    rows = [str(x) for x in r[3]] if r is not None else []
    kc(r is not None and nt.startswith(old) and nt.count(str(Cfg.U26_MARK_ID)) == 1 and all(str(pn.getProperty("ut." + i)) == ut[i] and str(pn.getProperty("utfx." + i)) == fx[i] for i in U26)
       and len(str(r[2]).split(", ")) == 36 and "\r\n" in nt[len(old):] and "\n" not in nt[len(old):].replace("\r\n", "") and nt.rstrip().endswith("utfx.Hepta_Axe=" + fx["Hepta_Axe"]),
       "B: u26Update adds the 36 rows + the marker at the END, nothing before changes, CRLF kept: %s" % (str(r[2])[:80] if r is not None else None))
    kc(len(rows) == 72 and rows[0] == "ut[RookHelmGhost]" and rows[1] == ut["RookHelmGhost"].replace(",", "|", 2) and rows[-2] == "utfx[Hepta_Axe]"
       and rows[-1] == fx["Hepta_Axe"].replace(",", "|"), "B: one change-log row per added entry (key[entry], the columns joined by |): %s" % rows[:2])
    kc(Cfg.u26Update(nt) is None, "B: a second run = null (run-once marker)")
    r2 = Cfg.u26Update(old + "\r\nut.ghostsword=20,25,Mine\r\n")
    kc(r2 is not None and "ut.GhostSword is already in the file - kept" in [str(x) for x in r2[1]] and "ut.GhostSword=" not in str(r2[0])
       and "ut.ghostsword=20,25,Mine" in str(r2[0]) and len(str(r2[2]).split(", ")) == 35 and len(list(r2[3])) == 70,
       "B: an admin's row in another case is kept + noted, never doubled")
    lg = str(Cfg.u26Log(JString("ut[GhostSword]"), JString("15|29|x"))).split("\t")
    kc(len(lg) == 8 and lg[1:] == ["SkyyGear 0.3.26", "-", "update", "ut[GhostSword]", "(none)", "15|29|x", "ok"], "B: u26Log = the change-log row (old (none), status ok): %s" % lg)
    print("  note (h326): A + B ran - UTAB %d rows, u26Update added %d entries" % (len(tid), len(rows) // 2))


if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h326(L, K):
        _h319_prev(L, K)
        try:
            _h326(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H326: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h326
    H320["run_assets320"] = run_assets326          # the jar compare of THIS round (0.3.25 -> 0.3.26)
    H320["J319"] = J325


# ====================================================================================================== STATIC (no jars)
def run_static():
    base = os.path.join(SCR_BASE, "static")
    shutil.rmtree(base, ignore_errors=True)
    outs = []
    try:
        for k in range(2):
            r = os.path.join(base, "run%d" % k)
            os.makedirs(os.path.join(r, "tools"))
            os.makedirs(os.path.join(r, "SkyyGear"))
            shutil.copyfile(PATCH, os.path.join(r, "tools", os.path.basename(PATCH)))
            shutil.copyfile(os.path.join(TOOLS, "deploy_set.py"), os.path.join(r, "tools", "deploy_set.py"))
            shutil.copyfile(GEN325, os.path.join(r, "SkyyGear", os.path.basename(GEN325)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.26.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.26.py (the committed file is the patch's output)")
        src = open(GEN325, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.26.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.26"\n' in s and "GENERATED by tools/gear_0_3_26_patch.py" in s, "A: VERSION 0.3.26 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean has22(") < i("public static Object[] u26Update(") < i("public static String u26Log(") < i("public static synchronized String migrate0326()")
              < i("  @PKG@.GearCfg.migrate0326();") and i("  @PKG@.GearCfg.migrate0323();") < i("  @PKG@.GearCfg.migrate0326();"),
              "A: helpers before their callers (javassist order); migrate0326 runs after migrate0323")
        check(i("G26_ART = _g23_art(") < i("assert len(G23_ITEMJ) == 49") and "G26_SHIP_REPOSED = False" in s, "A: the art block before the 0.3.23 checks; the re-placement does not ship")
        check(all(("U26_ROWS.append" in s) for _ in [0]) and s.count('L += [""] + U26_LINES') == 1, "A: the fresh block once")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    assert os.path.isfile(J325), J325
    H320["main"]()


if __name__ == "__main__":
    main()
