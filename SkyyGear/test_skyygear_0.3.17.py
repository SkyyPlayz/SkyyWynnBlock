"""Harness for SkyyGear 0.3.17 (tools/gear_0_3_17_patch.py header = round T1) = the 0.3.16 harness's children run on the 0.3.17 jar + S317 + H317:
    python tools/gear_0_3_17_patch.py && python SkyyGear/build_skyygear_0.3.17.py
    python SkyyGear/test_skyygear_0.3.17.py [--keep] [--only assets,h317,h316,h315,...]

  S317 the jar 0.3.16 -> 0.3.17: two classes added (GearSalv, GearSalvFn), every non-class file identical except manifest.json + the fresh
       config text inside GearCfg
  H317 ONE booted engine (the 0.3.5 life setup):
       A  ROWS + migrate0317: the 11 new rows (danger), the fresh file block + marker + the new defaults; h7Update on texts (old defaults by number,
          CRLF kept, hand edits kept + noted, a later entry wins, the marker = run once); migrate0317 on a scratch file twice (History copy, rows)
       B  LINE MATH: flat 1-point lines at many levels, the 10 x tier caps on every ladder (top tier uncapped), the doubling ability costs, the
          ability caps by tool level, perkEff, spent
       C  THE STATS: Breaking Power / Fortune on a real kit pickaxe (inside the tier cap), no Fortune cap (past 100 = dd above 1 = triple drops in
          SkyySkills), the Power guard row, Breaking Speed published as gear:swing:<uuid>
       D  THE MULTITOOL'S TWO SETS + the two pools
       E  COLLECTION POINTS (coll:fn:toolPts, cache, off, absent)
       F  THE COLLECTION TIER-UP GATE (coll:fn:tierup: locked / unlocked / not gated / error / off; the token words)
       G  BUYING: flat costs, the tier cap refusal (points banked), the ability tool-level refusal, Breaking Speed waits for SkyyTrees' readers
       H  gear:fn:perk answers the level that works now
       I  t1Mig: levels above the new caps lowered once (history copy, marker, log), nothing else; unknown skill = retried; a clean profile = marker only
       J  SALVAGE: the materials (recipe + ladder steps x rarity %, rounded down, never coins), commit once (journal), refusals, the bridge shapes
Scratch: tools/dev/scratch/t1/gear/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.17"
V316 = "0.3.16"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "t1", "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J316 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V316))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.16 harness as a library (it loads the older ones); its main runs every child on THIS jar in THIS scratch folder
_H316 = os.path.join(HERE, "test_skyygear_0.3.16.py")
_T316 = open(_H316, encoding="utf-8").read()
_cut = _T316.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H316, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
    (["--only", arg("--only")] if arg("--only") else [])
H316 = {"__name__": "skyygear_h316", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
_A316 = """    txt, cl, ev, ed = render(lp)
    kc('Text: "Upgrade"' in txt and "#SkyyGPReset " in txt,"""
assert _T316.count(_A316) == 1, "the 0.3.16 tools-page anchor moved"
_B317 = """    # 0.3.17 (test_skyygear_0.3.17.py, critic item 4): the pickaxe's panel with FIVE perk rows (Breaking Speed added) passes assert_menu_page and
    # fits #SkyyGMain (662 px): the panel's own children add up
    lp.sel = JInt(0)
    page_ok("Upgrade (tools) pickaxe, 5 perk rows (0.3.17)", lp, "Upgrade")
    txt17, cl17, ev17, ed17 = render(lp)
    pan17 = [mk for p_, mk in appends(cl17) if p_ == "SkyyGPanel"]
    rows17 = [mk for mk in pan17 if mk.startswith("Group #SkyyGPk")]
    h17 = 0
    for mk in pan17:
        m_ = re.match(r"(?:Group|Label|TextButton)(?:\\s+#\\S+)?\\s*\\{\\s*Anchor:\\s*\\((?:Width:\\s*\\d+,\\s*)?Height:\\s*(\\d+)", mk)
        if m_:
            h17 += int(m_.group(1))
    kc(len(rows17) == 5 and 0 < h17 <= 662 and "Breaking Power   Lv" in txt17 and "Breaking Speed   Lv" in txt17,
       "P 0.3.17: the pickaxe panel = 5 perk rows (Breaking Power, Fortune, Wisdom, Vein Mine, Breaking Speed), %d px <= 662 (#SkyyGMain)" % h17)
"""
_T316 = _T316.replace(_A316, _B317 + _A316)
exec(compile(_T316[:_cut + len(_B317)], _H316 + " (library, + the 0.3.17 tools-page check)", "exec"), H316)
sys.argv = _argv
H316["VERSION"] = VERSION
H35, H36 = H316["H35"], H316["H36"]
FI7_SRC = H316["FI7_SRC"]

_WHY_LINES = ("0.3.17 by design (round T1; Skyy 2026-10-16 'i wouldnt cap either' + 'lets drop the scaling. keep it to 1 point is 1 level' + "
              "'Yes, 10 levels per tier'): Breaking Power / Fortune have no max of 10 any more (a flat point a level, capped by 10 x tier), "
              "lifelong.perkSpeed 2 -> 5 and perkFortune 1 -> 2, Speed is called Breaking Power; H317 B / C / G check the new numbers")
_WHY_ABIL = ("0.3.17 by design (Skyy 2026-10-16 'capped by the tools level (so your skill level.) and not the tier' + 'double price every "
             "time'): Vein Mine / Tree Feller cost 1, 2, 4 ... and need tool Lv 8 / 16 / 24 ... instead of an Iron / Thorium / Cobalt tier; H317 B / G")
_WHY_FCAP = ("0.3.17 by design (Skyy 2026-10-16 'no max %'): tool.fortune.cap defaults to 0 = no cap (was 25); H317 A / C")
WAIVE_317 = [          # (prefix, why) - each one an explained 0.3.17 change of an older check (from the first 0.3.17 run)
    ("R3: +1 at Max = refused ('top level')", _WHY_LINES + " (the 0.3.10 check maxed Fortune at 10: now that is the Crude tier cap and the refusal says so)"),
    ("G36 P5: gear:fn:fishx: Fortune 1 -> +1", _WHY_LINES + " (the pole's Fortune line follows lifelong.perkFortune 2: Fortune 1 = +2 % double catch)"),
    ("G36 P6: END TO END", _WHY_LINES + " (the same: double catch 2.0 at Fortune 1, the 0.3.6 check expected 1.0)"),
    ("L1 (0.3.1): the fresh config: the 16 lifelong rows", _WHY_LINES + " (the fresh file says lifelong.perkSpeed=5 / perkFortune=2; H317 A checks them)"),
    ("L11: buy Speed for the hatchet", _WHY_LINES + " (the answer names Breaking Power; buying + Reset unchanged)")]
H316["WAIVE_316"].extend(WAIVE_317)
FAILS, OKS = H316["FAILS"], H316["OKS"]


def check(cond, what):
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S317
def run_assets317():
    ea, eb = entries(J316), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(added) == ["com/skyy/gear/GearSalv.class", "com/skyy/gear/GearSalvFn.class"] and not gone and changed == ["manifest.json"],
          "S317: 0.3.16 -> 0.3.17 adds GearSalv + GearSalvFn, removes nothing, changes only manifest.json among the files: added %s, gone %s, changed %s"
          % (added[:4], gone[:4], changed))
    check('"0.3.17"' in eb["manifest.json"].decode("utf-8"), "S317: the manifest says 0.3.17")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.16 -> 0.3.17: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    want_c = {"GearLL", "GearLife", "LifePage", "GearTool", "GearCfg", "GearLLFn", "GearGArm", "SkyyGearPlugin", "CfgFn", "CfgRows", "CfgDefaults",
              "CfgKit", "CfgPub", "CfgFile"}
    check(set(chg) <= want_c, "S317: only the tool-upgrade classes (+ config / version text) changed: unexpected %s" % sorted(set(chg) - want_c))


# ====================================================================================================== H317
def run_h317(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h317(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H317: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h317(L, K):
    from jpype import JClass, JInt, JLong, JDouble, JObject, JArray, JString, JImplements, JOverride
    br, Gear, Cfg, LL, Life, Up, Data = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Life"], L["Up"], L["Data"]
    mkinv, PR1, U1, stack, doc, skills, apply, logs, lls = L["mkinv"], L["PR1"], L["U1"], L["stack"], L["doc"], L["skills"], L["apply"], L["logs"], L["lls"]
    HOME, SK, wipe_home = L["HOME"], L["SK"], L["wipe_home"]
    P = lambda n: JClass(PKG + n)
    Tool, Salv, SalvFn, Multi, Defs, CRows = P("GearTool"), P("GearSalv"), P("GearSalvFn"), P("GearMulti"), P("GearDefs"), P("CfgRows")
    Paths = JClass("java.nio.file.Paths")
    Props = JClass("java.util.Properties")
    BD, BS, BI, BL = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonInt64")
    Long_ = JClass("java.lang.Long")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))

    def look(pr_, inv_):
        LL.LAST.clear()
        Life.sweep(pr_, inv_, True)
    apply()
    BIG = int(LL.LINE_BIG)
    SPD, FORT, WIS, VEIN, FELL, SWING = 0, 1, 2, int(LL.PK_VEIN), int(LL.PK_FELL), int(LL.PK_SWING)
    eq((VEIN, FELL, SWING, [str(x) for x in LL.PK][SWING], str(LL.PKN[0]), str(LL.PKN[SWING])), (3, 4, 10, "swing", "Breaking Power", "Breaking Speed"),
       "H317 setup: the saved order kept, Breaking Speed appended as key swing, Speed renamed Breaking Power")

    # ============================================================== A: rows + migrate0317
    keys = ["tool.power.max", "lifelong.perkSwing", "lifelong.lineCost", "lifelong.lineCapPerTier", "lifelong.abilityMax", "lifelong.abilityLevelStep",
            "lifelong.abilityCost", "lifelong.collPoints", "lifelong.collGate", "salvage.on", "salvage.pct"]
    kc(all(int(CRows.index(k)) >= 0 and bool(CRows.flag(int(CRows.index(k)), "danger")) for k in keys), "A: the 11 new Server Setup rows exist (danger rows)")
    FRESH = L["FRESH"]
    kc(str(Cfg.H7_MARK_ID) in FRESH and FRESH.count(str(Cfg.H7_MARK_ID)) == 1 and "\nlifelong.perkSpeed=5\n" in FRESH and "\nlifelong.perkFortune=2\n" in FRESH
       and "\ntool.fortune.cap=0\n" in FRESH and "\nlifelong.lineCapPerTier=10\n" in FRESH and "\nsalvage.pct=25,30,35,40,45,50\n" in FRESH
       and "\nlifelong.abilityMax=6\n" in FRESH and "\ntool.power.max=1000\n" in FRESH,
       "A: a fresh config.properties: the 0.3.17 block + the migrate0317 marker; the new defaults (Breaking Power 5, Fortune 2, no Fortune cap)")
    kc(abs(float(Cfg.LL_PSPD) - 5.0) < 1e-12 and abs(float(Cfg.LL_PFORT) - 2.0) < 1e-12 and abs(float(Cfg.LL_PSWING) - 3.0) < 1e-12 and float(Cfg.TOOL_FCAP) == 0.0
       and float(Cfg.fcap()) >= 1e8 and abs(float(Cfg.pmax()) - 1000.0) < 1e-9 and int(Cfg.LL_LCOST) == 1 and int(Cfg.LL_LCAPT) == 10
       and int(Cfg.LL_ABMAX) == 6 and int(Cfg.LL_ABSTEP) == 8 and int(Cfg.LL_ABCOST) == 1 and bool(Cfg.LL_COLLPTS) and bool(Cfg.LL_COLLGATE) and bool(Cfg.SALV_ON),
       "A: the loaded defaults")
    t1 = "# head\r\na=1\r\nlifelong.perkSpeed=2\r\nlifelong.perkFortune = 1.0\r\ntool.fortune.cap=25.0\r\nb=2\r\n"
    r1 = Cfg.h7Update(JString(t1))
    o1 = str(r1[0]) if r1 is not None else ""
    kc(r1 is not None and "lifelong.perkSpeed=5\r\n" in o1 and "lifelong.perkFortune = 2\r\n" in o1 and "tool.fortune.cap=0\r\n" in o1 and o1.startswith("# head\r\na=1\r\n")
       and "b=2\r\n" in o1 and str(Cfg.H7_MARK) + "\r" in o1 and len(list(r1[3])) == 9 and "lifelong.perkSpeed 2 -> 5" in str(r1[1]),
       "A: h7Update rewrites the three old defaults by number (value text only, CRLF kept), the marker at the end, 3 change-log rows: %r" % o1[-200:])
    r2 = Cfg.h7Update(JString("lifelong.perkSpeed=3\nlifelong.perkFortune=1\ntool.fortune.cap=40\n"))
    o2 = str(r2[0])
    kc("lifelong.perkSpeed=3\n" in o2 and "lifelong.perkFortune=2\n" in o2 and "tool.fortune.cap=40\n" in o2 and len(list(r2[3])) == 3 and len(list(r2[2])) == 2,
       "A: hand-edited values are kept + noted (perkSpeed 3, cap 40), the untouched one moves: %s" % list(r2[2]))
    kc(Cfg.h7Update(JString("x=1\n" + str(Cfg.H7_MARK) + "\n")) is None, "A: the marker = run once (null)")
    r4 = Cfg.h7Update(JString("tool.fortune.cap=25\ntool.fortune.cap=30\n"))
    kc("tool.fortune.cap=25\ntool.fortune.cap=30\n" in str(r4[0]) and len(list(r4[3])) == 0, "A: a later entry that is not the old default wins - nothing rewritten")
    cf = os.path.join(SCRATCH, "m317", "config.properties")
    os.makedirs(os.path.dirname(cf), exist_ok=True)
    body = (FRESH.replace("lifelong.perkSpeed=5", "lifelong.perkSpeed=2").replace("lifelong.perkFortune=2", "lifelong.perkFortune=1")
            .replace("tool.fortune.cap=0", "tool.fortune.cap=25.0").replace(str(Cfg.H7_MARK) + "\n", ""))
    open(cf, "wb").write(body.replace("\n", "\r\n").encode("ISO-8859-1"))
    oldF = Cfg.FILE
    try:
        Cfg.FILE = Paths.get(cf)
        m1 = str(Cfg.migrate0317())
        b1 = open(cf, "rb").read()
        m2 = str(Cfg.migrate0317())
        b2 = open(cf, "rb").read()
        hist = glob.glob(os.path.join(os.path.dirname(cf), "**", "*"), recursive=True)
        lines_b = body.replace("\n", "\r\n").encode("ISO-8859-1").split(b"\r\n")
        lines_a = b1.split(b"\r\n")
        diff = [(x, y) for x, y in zip(lines_b, lines_a) if x != y and x != b""]
        kc("lifelong.perkSpeed 2 -> 5" in m1 and "tool.fortune.cap 25.0 -> 0" in m1 and m2 == "" and b1 == b2 and len(lines_a) == len(lines_b) + 1
           and sorted(d[1].decode() for d in diff) == ["lifelong.perkFortune=2", "lifelong.perkSpeed=5", "tool.fortune.cap=0"]
           and lines_a[-2].decode() == str(Cfg.H7_MARK) and lines_a[-1] == b"",
           "A: migrate0317 on a file: the three lines move (nothing else; the marker last), the second start changes nothing: %s / %s / %s" % (m1[:140], m2, diff[:3]))
        kc(any("history" in h_.lower() for h_ in hist), "A: a History copy was made (%s)" % [os.path.relpath(h_, os.path.dirname(cf)) for h_ in hist][:6])
    finally:
        Cfg.FILE = oldF
    apply()

    # ============================================================== B: line math
    kc(all(int(LL.pkCost(p, n)) == 1 for p in (SPD, FORT, SWING) for n in (1, 2, 9, 10, 11, 40, 99, 100, 500, 5000)),
       "B: Breaking Power / Fortune / Breaking Speed cost a FLAT 1 point a level at every level (Skyy 'keep it to 1 point is 1 level')")
    eq([int(LL.pkCost(VEIN, n)) for n in range(1, 8)], [1, 2, 4, 8, 16, 32, 0], "B: Vein Mine levels 1-6 cost 1, 2, 4, 8, 16, 32 (7 = past the max)")
    eq([int(LL.pkCost(FELL, n)) for n in range(1, 7)], [1, 2, 4, 8, 16, 32], "B: Tree Feller costs double each level too")
    eq((int(LL.pkMax(SPD)), int(LL.pkMax(FORT)), int(LL.pkMax(SWING)), int(LL.pkMax(VEIN)), int(LL.pkMax(FELL)), int(LL.pkMax(WIS))), (BIG, BIG, BIG, 6, 6, 5),
       "B: the hard max: lines none (LINE_BIG), abilities 6, Wisdom 5 (unchanged)")
    eq([int(LL.pkCost(WIS, n)) for n in range(1, 6)] + [int(LL.pkNeed(WIS, 1))], [2, 2, 2, 2, 2, 2], "B: Wisdom unchanged (2 a level, Iron needed)")
    apply(lifelong__lineCost="3", lifelong__abilityCost="5", lifelong__abilityMax="4")
    eq((int(LL.pkCost(SPD, 7)), [int(LL.pkCost(VEIN, n)) for n in range(1, 6)], int(LL.pkMax(VEIN))), (3, [5, 10, 20, 40, 0], 4), "B: the cost / max rows apply live")
    apply()

    def reg(**kv):
        p_ = Props()
        for k_, v_ in kv.items():
            p_.setProperty(k_.replace("__", "."), str(v_))
        return p_
    TW = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite"]
    caps = [int(LL.lineCap(reg(pickaxe__id="Tool_Pickaxe_" + t), 0)) for t in TW]
    capsH = [int(LL.lineCap(reg(hatchet__id="Tool_Hatchet_" + t), 1)) for t in TW]
    eq((caps, capsH), ([10, 20, 30, 40, 50, BIG], [10, 20, 30, 40, 50, BIG]),
       "B: each line caps at 10 x tier (Crude 10, Copper 20, Iron 30, Thorium 40, Cobalt 50) and the ladder's top (Adamantite) is uncapped")
    hv = [int(LL.lineCap(reg(sickle__id=i), 3)) for i in ("Tool_Sickle_Harvester_Crude", "Tool_Sickle_Harvester_Copper", "Tool_Sickle_Harvester_Iron", "Tool_Sickle_Harvester_Thorium")]
    pole = [int(LL.lineCap(reg(pole__id="SkyyFishing_Rod_" + t), 4)) for t in ("Bamboo", "Copper", "Iron")]
    eq((hv, pole, int(LL.lineCap(reg(), 0))), ([10, 20, 30, BIG], [10, 20, BIG], 10),
       "B: the Harvester (top Thorium) and the pole (top Iron) cap the same way; no tool yet = Crude's 10")
    apply(lifelong__lineCapPerTier="0")
    eq(int(LL.lineCap(reg(pickaxe__id="Tool_Pickaxe_Crude"), 0)), BIG, "B: lifelong.lineCapPerTier 0 = no tier cap")
    apply()
    Pq = reg(pickaxe__id="Tool_Pickaxe_Copper", pickaxe__up__spd=35, pickaxe__up__fort=12, pickaxe__up__swing=21, pickaxe__up__wis=3, pickaxe__up__vein=4)
    skills(Mining=24, Foraging=4, Farming=4, Fishing=4)
    eq([int(LL.perkOf(Pq, 0, p)) for p in (SPD, FORT, SWING, WIS, VEIN)], [35, 12, 21, 3, 4], "B: perkOf = the saved level")
    eq([int(LL.perkEff(U1, Pq, 0, p)) for p in (SPD, FORT, SWING, WIS, VEIN)], [20, 12, 20, 3, 2],
       "B: perkEff = inside the cap: a Copper pickaxe's lines stop at 20; Vein Mine at tool Lv 18 (Copper band top) / 8 = 2")
    eq(int(LL.spent(Pq, 0)), 35 + 12 + 21 + 6 + (1 + 2 + 4 + 8), "B: spent = every saved level's cost (lines 1 each, Wisdom 2 each, Vein Mine 1+2+4+8)")
    lvls = {}
    for mining, tid in ((1, "Crude"), (7, "Crude"), (8, "Crude"), (13, "Crude"), (30, "Iron"), (30, "Thorium"), (49, "Cobalt"), (60, "Adamantite")):
        skills(Mining=mining)
        lvls[(mining, tid)] = (int(LL.levelFor(U1, "Tool_Pickaxe_" + tid)), int(LL.abilCap(U1, reg(pickaxe__id="Tool_Pickaxe_" + tid), 0)))
    eq(lvls, {(1, "Crude"): (1, 0), (7, "Crude"): (7, 0), (8, "Crude"): (8, 1), (13, "Crude"): (13, 1), (30, "Iron"): (23, 2), (30, "Thorium"): (28, 3),
              (49, "Cobalt"): (38, 4), (60, "Adamantite"): (43, 5)},
       "B: the ability cap follows the TOOL LEVEL (skill level inside the tier's band) / 8 - Skyy 'capped by the tools level (so your skill level.)'")
    eq([int(LL.pkNeedLv(VEIN, n)) for n in range(1, 7)], [8, 16, 24, 32, 40, 48], "B: Vein Mine level n needs tool Lv 8n")
    del SK[(str(U1), "Mining")]
    Gate = P("GearGate")
    Gate.forget(U1)
    eq(int(LL.abilCap(U1, reg(pickaxe__id="Tool_Pickaxe_Crude"), 0)), 0, "B: SkyySkills loaded but no level for this player yet = tool Lv 1 = no ability level")
    sfn = br.get("skill:fn:level")
    br.remove("skill:fn:level")
    Gate.forget(U1)
    eq(int(LL.abilCap(U1, reg(pickaxe__id="Tool_Pickaxe_Crude"), 0)), 6, "B: no SkyySkills at all = the ability max (no refusal by guessing)")
    br.put("skill:fn:level", sfn)
    Gate.forget(U1)
    skills(Mining=24, Foraging=4, Farming=4, Fishing=4)

    # ============================================================== C: the stats on a real kit pickaxe
    wipe_home()
    skills(Mining=12, Foraging=12, Farming=4, Fishing=4)
    inv, cs = mkinv()
    look(PR1, inv)
    look(PR1, inv)
    pk = str(Gear.pkey(U1))
    mine = [x for x in lls(cs, pk) if x[2] == 0]
    hatch = [x for x in lls(cs, pk) if x[2] == 1]
    kc(mine and hatch, "C setup: the kit gave a lifelong pickaxe and hatchet (%s)" % [x[6].getItemId() for x in lls(cs, pk)])
    if not (mine and hatch):
        return
    ps, pd = mine[0][6], doc(mine[0][6])
    R = LL.reg(pk)
    R.setProperty("pickaxe.up.spd", "8")
    R.setProperty("pickaxe.up.fort", "10")
    fx = [float(x) for x in LL.perkFx(U1, 1, pd)]
    kc(abs(fx[0] - 1.4) < 1e-9 and abs(fx[1] - 20.0) < 1e-9 and fx[2] == 0.0, "C: Breaking Power 8 = x1.40 Power (5 %% a level), Fortune 10 = +20 Fortune: %s" % fx)
    R.setProperty("pickaxe.up.spd", "15")
    kc(abs(float(LL.perkFx(U1, 1, pd)[0]) - 1.5) < 1e-9, "C: a Crude pickaxe works at most at Breaking Power 10 (x1.5) - the 15 saved stay banked")
    Tool.LAST.clear()
    st0 = [float(x) for x in Tool.stats(U1, ps)]
    R.setProperty("pickaxe.id", "Tool_Pickaxe_Adamantite")
    R.setProperty("pickaxe.up.fort", "150")
    R.setProperty("pickaxe.up.spd", "60")
    Tool.LAST.clear()
    st1 = [float(x) for x in Tool.stats(U1, ps)]
    kc(st1[5] > 300.0 and abs(st1[5] - st0[5] - (300.0 - 20.0)) < 0.2 and abs(st1[4] / st0[4] - (1.0 + 60 * 0.05) / 1.5) < 1e-6,
       "C: no tool Fortune cap: Fortune 150 levels = +300 (was capped at 25), Power x4.0 from Breaking Power 60 (the registry tier sets the cap): %s / %s" % (st0[4:6], st1[4:6]))
    Tool.held(U1, ps)
    gsrc = br.get("skill:bonus:" + str(U1))
    dd = None if gsrc is None or gsrc.get("gear") is None else gsrc.get("gear").get("dd.mining")
    kc(dd is not None and float(dd) > 3.0, "C: the post = Fortune / 100 = %s extra drops (past 1.0 = a third drop chance, 2.0 = always 3 drops in SkyySkills)" % dd)
    apply(tool__power__max="2")
    Tool.LAST.clear()
    kc(abs(float(Tool.stats(U1, ps)[4]) - 2.0) < 1e-9, "C: tool.power.max is the only Power guard (set to 2 here)")
    apply(tool__fortune__cap="25")
    Tool.LAST.clear()
    kc(abs(float(Tool.stats(U1, ps)[5]) - 25.0) < 1e-9, "C: an admin's tool.fortune.cap (25) still caps")
    apply()
    br.remove("gear:swing:" + str(U1))
    R.setProperty("pickaxe.up.swing", "7")
    Tool.LAST.clear()
    Tool.held(U1, ps)
    sw = br.get("gear:swing:" + str(U1))
    kc(sw is not None and abs(float(sw) - 21.0) < 1e-9, "C: Breaking Speed 7 is published as gear:swing:<uuid> = 21 %% (SkyyTrees applies it in T2): %s" % sw)
    R.remove("pickaxe.up.swing")
    Tool.LAST.clear()
    Tool.held(U1, ps)
    kc(br.get("gear:swing:" + str(U1)) is None, "C: no Breaking Speed = the bridge key is removed")
    Tool.forget(U1)
    Tool.back(U1)

    # ============================================================== D: the multitool's two sets + the two pools
    for k_ in ("pickaxe.up.spd", "pickaxe.up.fort", "hatchet.up.spd", "hatchet.up.fort"):
        R.remove(k_)
    R.setProperty("pickaxe.id", "Tool_Pickaxe_Copper")
    R.setProperty("hatchet.id", "Tool_Hatchet_Copper")
    md = pd.clone()
    mid = str(Multi.mid(1))
    m0 = [float(x) for x in Tool.mstats(U1, mid, md)]
    R.setProperty("pickaxe.up.spd", "10")
    R.setProperty("pickaxe.up.fort", "5")
    R.setProperty("hatchet.up.fort", "20")
    m1 = [float(x) for x in Tool.mstats(U1, mid, md)]
    kc(abs(m1[4] / m0[4] - 1.5) < 1e-6 and abs(m1[9] - m0[9]) < 1e-9 and abs(m1[5] - m0[5] - 10.0) < 0.11 and abs(m1[10] - m0[10] - 40.0) < 0.11,
       "D: a lifelong multitool = TWO sets: stone / ore use the pickaxe kind's lines (Power x1.5, +10 Fortune), logs the hatchet kind's (+40 Fortune, "
       "Power unchanged): %s -> %s" % ([m0[4], m0[5], m0[9], m0[10]], [m1[4], m1[5], m1[9], m1[10]]))
    pd2 = md.clone()
    pd2.put("lo", BS("someone-else"))
    m2 = [float(x) for x in Tool.mstats(U1, mid, pd2)]
    kc(abs(m2[4] - m0[4]) < 1e-9 and abs(m2[10] - m0[10]) < 1e-9, "D: another player's (or a plain) multitool gets no lifelong lines")
    skills(Mining=20, Foraging=5)
    LL.CPTS.clear()
    eq((int(LL.earned(U1, 0)), int(LL.earned(U1, 1))), (19, 4), "D: the two pools: the pickaxe set earns Mining points, the hatchet set Foraging points")

    # ============================================================== E: collection points
    ASK = []
    CP = {"Mining": 30, "Foraging": 50}

    @JImplements("java.util.function.Function")
    class TpFn(object):
        @JOverride
        def apply(self, o):
            ASK.append((str(o[0]), str(o[1])))
            v_ = CP.get(str(o[1]))
            return None if v_ is None else JObject(JLong(v_), Long_)
    br.put("coll:fn:toolPts", TpFn())
    LL.CPTS.clear()
    eq((int(LL.earned(U1, 0)), int(LL.earned(U1, 1)), int(LL.earned(U1, 2))), (19 + 30, 4 + 50, 3 + 0),
       "E: earned = (skill level - 1) + coll:fn:toolPts for the kind's skill (Mining 30, Foraging 50, Farming none)")
    kc(("p1", "Mining") in ASK or (pk, "Mining") in ASK, "E: asked with the profile key + the skill name: %s" % ASK[:3])
    CP["Mining"] = 99
    eq(int(LL.earned(U1, 0)), 49, "E: cached for 2 s (no bridge call per look)")
    LL.CPTS.clear()
    eq(int(LL.earned(U1, 0)), 19 + 99, "E: a fresh ask after the cache")
    apply(lifelong__collPoints="false")
    eq(int(LL.earned(U1, 0)), 19, "E: lifelong.collPoints off = skill points only")
    apply()

    @JImplements("java.util.function.Function")
    class BadFn(object):
        @JOverride
        def apply(self, o):
            raise RuntimeError("boom")
    br.put("coll:fn:toolPts", BadFn())
    LL.CPTS.clear()
    eq(int(LL.earned(U1, 0)), 19, "E: a failing SkyyCollections = 0 collection points (no throw)")
    br.remove("coll:fn:toolPts")
    LL.CPTS.clear()
    eq(int(LL.earned(U1, 0)), 19, "E: no SkyyCollections = 0 collection points")

    # ============================================================== F: the collection tier-up gate
    TA = []
    GATE = {"pickaxe:Thorium": "0|Iron|Iron Ore|4|500|312", "pickaxe:Iron": "1|Copper|Copper Ore|4|500|900", "harvester:Copper": "0|Wheat|Wheat|3|250|10"}

    @JImplements("java.util.function.Function")
    class TuFn(object):
        @JOverride
        def apply(self, o):
            TA.append((str(o[0]), str(o[1])))
            v_ = GATE.get(str(o[1]))
            return None if v_ is None else JString(v_)
    br.put("coll:fn:tierup", TuFn())
    skills(Mining=60, Foraging=60, Farming=60, Fishing=60)
    w_th = LL.tierWhy(U1, "Tool_Pickaxe_Thorium")
    w_ir = LL.tierWhy(U1, "Tool_Pickaxe_Iron")
    w_hv = LL.tierWhy(U1, "Tool_Sickle_Harvester_Copper")
    w_co = LL.tierWhy(U1, "Tool_Hatchet_Cobalt")
    w_po = LL.tierWhy(U1, "SkyyFishing_Rod_Copper")
    kc(w_th is not None and "Needs the Iron Ore collection IV (312 / 500)" in str(w_th) and "Thorium" in str(w_th),
       "F: a locked tier-up says which collection tier it needs + the progress: %s" % w_th)
    kc(w_ir is None and w_hv is not None and "Wheat collection III" in str(w_hv) and w_co is None and w_po is None,
       "F: unlocked = open; the Harvester asks harvester:<Tier>; a tier no collection lists = open; the pole is never asked: %s / %s / %s / %s" % (w_ir, w_hv, w_co, w_po))
    kc(("p1", "pickaxe:Thorium") in TA or (pk, "pickaxe:Thorium") in TA, "F: the token words: %s" % TA[:4])
    skills(Mining=10)
    w_lv = LL.tierWhy(U1, "Tool_Pickaxe_Thorium")
    kc(w_lv is not None and "Mining 20" in str(w_lv), "F: the skill level rule still comes first: %s" % w_lv)
    skills(Mining=60)
    apply(lifelong__collGate="false")
    kc(LL.tierWhy(U1, "Tool_Pickaxe_Thorium") is None, "F: lifelong.collGate off = no collection gate")
    apply()
    br.put("coll:fn:tierup", BadFn())
    kc(LL.tierWhy(U1, "Tool_Pickaxe_Thorium") is None, "F: a failing SkyyCollections = open (no throw)")
    br.remove("coll:fn:tierup")
    kc(LL.tierWhy(U1, "Tool_Pickaxe_Thorium") is None, "F: no SkyyCollections = open")

    # ============================================================== G: buying
    wipe_home()
    skills(Mining=40, Foraging=12, Farming=4, Fishing=4)
    inv, cs = mkinv()
    look(PR1, inv)
    R = LL.reg(pk)
    eq(str(R.getProperty("pickaxe.id")), "Tool_Pickaxe_Crude", "G setup: a fresh Crude pickaxe")
    old_rd = br.get("gear:perk:readers")
    br.put("gear:perk:readers", "vein,fell")
    got = [str(Life.buy(U1, 0, SPD)) for _ in range(10)]
    kc(all(g_.startswith("+") for g_ in got) and int(LL.perkOf(R, 0, SPD)) == 10 and int(LL.spent(R, 0)) == 10,
       "G: 10 Breaking Power levels for 10 points: %s" % got[-1])
    g11 = str(Life.buy(U1, 0, SPD))
    kc(g11.startswith("-") and "tier it up" in g11 and "banked" in g11 and int(LL.perkOf(R, 0, SPD)) == 10 and int(LL.free(U1, R, 0)) == 39 - 10,
       "G: the 11th level on a Crude pickaxe is refused (the 10 x tier cap), the points stay free: %s" % g11)
    skills(Mining=7)
    gv = str(Life.buy(U1, 0, VEIN))
    kc(gv.startswith("-") and "needs tool Lv 8" in gv, "G: Vein Mine 1 needs tool Lv 8 (Mining 7 = tool Lv 7): %s" % gv)
    skills(Mining=40)
    gv1, gv2 = str(Life.buy(U1, 0, VEIN)), str(Life.buy(U1, 0, VEIN))
    kc(gv1.startswith("+") and gv2.startswith("-") and "needs tool Lv 16" in gv2 and int(LL.perkOf(R, 0, VEIN)) == 1,
       "G: the Crude pickaxe's tool Lv 13 allows Vein Mine 1 (cost 1), not 2 (needs Lv 16): %s / %s" % (gv1, gv2))
    gs = str(Life.buy(U1, 0, SWING))
    kc(gs.startswith("-") and "SkyyTrees" in gs, "G: Breaking Speed waits for SkyyTrees (gear:perk:readers has no swing): %s" % gs)
    br.put("gear:perk:readers", "vein,fell,swing")
    gs2 = str(Life.buy(U1, 0, SWING))
    kc(gs2.startswith("+") and int(LL.perkOf(R, 0, SWING)) == 1, "G: with SkyyTrees reading swing, Breaking Speed buys like the other lines: %s" % gs2)
    if old_rd is None:
        br.remove("gear:perk:readers")
    else:
        br.put("gear:perk:readers", old_rd)
    reg_file = open(os.path.join(HOME, "lifelong", pk + ".properties"), encoding="utf-8").read()
    kc("pickaxe.up.spd=10" in reg_file and "pickaxe.up.vein=1" in reg_file and "pickaxe.up.swing=1" in reg_file, "G: the levels are saved by key in the registry")

    # ============================================================== H: gear:fn:perk = the level that works now
    PF = JClass(PKG + "GearLLFn")(JInt(1))
    R.setProperty("pickaxe.up.vein", "3")
    skills(Mining=40)
    a1 = PF.apply(JArray(JObject)([U1, JString("pickaxe"), JString("vein")]))
    R.setProperty("pickaxe.id", "Tool_Pickaxe_Cobalt")
    a2 = PF.apply(JArray(JObject)([U1, JString("pickaxe"), JString("vein")]))
    eq((int(a1), int(a2)), (1, 3), "H: gear:fn:perk = the Vein Mine level the tool may use now (Crude Lv 13 -> 1; Cobalt Lv 38 -> 3 of the 3 saved)")
    R.setProperty("pickaxe.id", "Tool_Pickaxe_Crude")
    R.setProperty("pickaxe.up.vein", "1")

    # ============================================================== I: t1Mig
    wipe_home()
    skills(Mining=40, Foraging=12, Farming=4, Fishing=4)
    inv, cs = mkinv()
    look(PR1, inv)
    R = LL.reg(pk)
    R.remove("t1")
    R.setProperty("pickaxe.up.spd", "15")
    R.setProperty("pickaxe.up.fort", "9")
    R.setProperty("pickaxe.up.vein", "3")
    R.setProperty("hatchet.up.fell", "2")
    kc(bool(LL.save(pk, R)), "I setup: a registry with Breaking Power 15 on a Crude pickaxe (cap 10), Vein Mine 3 (tool Lv 13 allows 1), Tree Feller 2 (Foraging 12 = Lv 12 allows 1)")
    hist_dir = os.path.join(HOME, "lifelong", "history")
    shutil.rmtree(hist_dir, ignore_errors=True)
    logs()
    ch1 = bool(Life.t1Mig(PR1, pk, R))
    lg = logs()
    hist = glob.glob(os.path.join(hist_dir, "*"))
    eq((ch1, [int(LL.perkOf(R, 0, p)) for p in (SPD, FORT, VEIN)], int(LL.perkOf(R, 1, FELL)), str(R.getProperty("t1"))), (True, [10, 9, 3], 2, "1"),
       "I: t1Mig lowers only the LINE levels above the 10 x tier cap (15 -> 10; Fortune 9 kept); Vein Mine 3 / Tree Feller 2 are never lowered "
       "(they follow the skill live: perkEff = 1 / 1 now), marker t1=1")
    eq((int(LL.perkEff(U1, R, 0, VEIN)), int(LL.perkEff(U1, R, 1, FELL))), (1, 1), "I: ... the abilities work at the tool level's cap until the skill grows")
    kc(len(hist) == 1 and "pickaxe.up.spd=15" in open(hist[0], encoding="utf-8").read() and any("LL-T1MIG" in x and "Breaking Power 15 -> 10" in x for x in lg),
       "I: the history copy holds the old levels; a LL-T1MIG log line: %s" % [x[:140] for x in lg if "T1MIG" in x])
    on_disk = open(os.path.join(HOME, "lifelong", pk + ".properties"), encoding="utf-8").read()
    kc("pickaxe.up.spd=10" in on_disk and "t1=1" in on_disk, "I: the lowered levels + the marker are on disk")
    ch2 = bool(Life.t1Mig(PR1, pk, R))
    eq((ch2, len(glob.glob(os.path.join(hist_dir, "*")))), (False, 1), "I: run once: the second look changes nothing")
    R.remove("t1")
    ch4 = bool(Life.t1Mig(PR1, pk, R))
    eq((ch4, str(R.getProperty("t1"))), (False, "1"), "I: a profile with nothing above a cap = only the marker (no write, no history)")

    # ============================================================== J: salvage
    def gdoc(r_, ident=True, ll=False, src="craft"):
        d_ = Data.base(JString("tool"), JInt(r_), ident, JString(src))
        if ll:
            d_.put("ll", BI(JInt(1)))
            d_.put("lu", BS("abc"))
            d_.put("lo", BS(pk))
        md_ = BD()
        md_.put(str(Defs.DOC_KEY), d_)
        return md_
    COINS0 = L["COINS"][0] if "COINS" in L else None
    mR = gdoc(2)
    q = Salv.quote(U1, JString("Tool_Pickaxe_Iron"), mR)
    ids_ = [str(x) for x in q[1]]
    qty_ = [int(x) for x in q[2]]
    mats = dict((str(k_), int(v_)) for k_, v_ in Salv.mats(JString("Tool_Pickaxe_Iron")).items())
    kc(q[0] is None and "Ingredient_Bar_Copper" in ids_ and dict(zip(ids_, qty_))["Ingredient_Bar_Copper"] == 25 * 35 // 100
       and mats.get("Ingredient_Bar_Copper") == 25 and mats.get("Skyy_Ench_Iron") == 1 and "Skyy_Ench_Iron" not in ids_,
       "J: a Rare Iron pickaxe salvages 35 %% of the Crude recipe + the Copper step (25 Copper Ingots -> 8) + the Iron step (1 Enchanted Iron -> 0, "
       "rounded down): %s from %s" % (dict(zip(ids_, qty_)), mats))
    K.notes.append("J example: a Rare Tool_Pickaxe_Iron salvages %s (its materials %s)" % (dict(zip(ids_, qty_)), mats))
    kc(not [i for i in ids_ if "coin" in i.lower()] and (COINS0 is None or L["COINS"][0] == COINS0), "J: never coins (no coin item, the purse untouched)")
    qM = Salv.quote(U1, JString("Tool_Pickaxe_Iron"), gdoc(5))
    kc(dict(zip([str(x) for x in qM[1]], [int(x) for x in qM[2]]))["Ingredient_Bar_Copper"] == 12, "J: a Mythic piece gets 50 %% (12 of 25)")
    jf_ = os.path.join(HOME, "salvage", pk + ".properties")
    if os.path.isfile(jf_):
        os.remove(jf_)
    c1 = Salv.commit(U1, JString("Tool_Pickaxe_Iron"), mR)
    c2 = Salv.commit(U1, JString("Tool_Pickaxe_Iron"), mR)
    kc(c1[0] is None and list(c1[1]) == list(q[1]) and c2[0] is not None and "salvaged already" in str(c2[0]) and len(list(c2[1])) == 0
       and os.path.isfile(jf_) and str(q[3]).split("|")[0] == "Tool_Pickaxe_Iron",
       "J: commit gives the materials ONCE (the journal), the same piece again is refused: %s" % c2[0])
    dmR = gdoc(2, src="loot")
    qd = Salv.quote(U1, JString("Tool_Pickaxe_Iron"), dmR)
    dids = dict(zip([str(x) for x in qd[1]], [int(x) for x in qd[2]]))
    base = dict((str(k_), int(v_)) for k_, v_ in Salv.baseMats(JString("Tool_Pickaxe_Iron")).items())
    big = max(base.items(), key=lambda kv: kv[1])[0] if base else None
    want = dict((k_, v_ * 10 // 100) for k_, v_ in base.items() if v_ * 10 // 100 > 0) or ({big: 1} if big else {})
    kc(qd[0] is None and base and dids == want and "Ingredient_Bar_Copper" not in base and "Skyy_Ench_Iron" not in dids,
       "J: a DROPPED piece (src loot) gives salvage.dropPct 10 %% of its BASE recipe only (no tier-up materials): %s from %s" % (dids, base))
    K.notes.append("J example (dropped): a Rare looted Tool_Pickaxe_Iron salvages %s (its base recipe %s)" % (dids, base))
    apply(salvage__dropPct="50")
    kc(dict(zip([str(x) for x in Salv.quote(U1, JString("Tool_Pickaxe_Iron"), dmR)[1]], [int(x) for x in Salv.quote(U1, JString("Tool_Pickaxe_Iron"), dmR)[2]]))
       == dict((k_, v_ // 2) for k_, v_ in base.items() if v_ // 2 > 0), "J: salvage.dropPct applies live (50)")
    apply()
    kc(int(CRows.index("salvage.dropPct")) >= 0 and bool(CRows.flag(int(CRows.index("salvage.dropPct")), "danger")), "J: the salvage.dropPct row (danger)")
    used = BD()
    used.put(str(Defs.DOC_KEY), mR.get(str(Defs.DOC_KEY)).asDocument().clone())
    used.get(str(Defs.DOC_KEY)).asDocument().put("lvl", BI(JInt(33)))
    used.get(str(Defs.DOC_KEY)).asDocument().put("ll2", BI(JInt(7)))
    kc(str(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), used)[3]) == str(q[3]) and "salvaged already" in str(Salv.commit(U1, JString("Tool_Pickaxe_Iron"), used)[0]),
       "J: the key uses stable fields only (id, at, b0, rolls): a re-levelled copy of the same piece has the same key and is refused")
    rl = Salv.release(U1, JString("Tool_Pickaxe_Iron"), mR)
    c3 = Salv.commit(U1, JString("Tool_Pickaxe_Iron"), mR)
    kc(rl[0] is None and c3[0] is None and Salv.release(U1, JString("Tool_Pickaxe_Iron"), gdoc(3))[0] is not None,
       "J: release (the caller's removal failed after a commit) takes the key back out - the piece can be committed again; an unknown piece = refused")
    other = gdoc(2)
    other.get(str(Defs.DOC_KEY)).asDocument().put("at", BL(JLong(12345)))
    kc(Salv.commit(U1, JString("Tool_Pickaxe_Iron"), other)[0] is None, "J: another piece of the same kind salvages (its own key)")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), gdoc(2, ll=True))[0] is not None and "Lifelong" in str(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), gdoc(2, ll=True))[0]),
       "J: a lifelong tool is never salvaged")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), gdoc(2, ident=False))[0] is not None, "J: an unidentified piece is refused")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), None)[0] is not None and Salv.quote(U1, JString("Nope_Item"), mR)[0] is not None,
       "J: no gear document / an unknown item = refused")
    apply(salvage__on="false")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), mR)[0] is not None, "J: salvage.on off = refused")
    apply(salvage__pct="0,0,0,0,0,0")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), mR)[0] is not None, "J: salvage.pct 0 = nothing back (refused, not an empty gift)")
    apply(salvage__pct="bad")
    kc(Salv.quote(U1, JString("Tool_Pickaxe_Iron"), mR)[0] is None and Salv.check(JString("salvage.pct"), JString("bad")) is not None
       and Salv.check(JString("salvage.pct"), JString("25,30,35,40,45,50")) is None, "J: a bad salvage.pct = the default (one WARN) + Server Setup refuses it")
    apply()
    FN = SalvFn()
    f1 = FN.apply(JArray(JObject)([U1, JString("Tool_Pickaxe_Iron"), mR, JString("quote")]))
    item = BD()
    item.put("Id", BS("Tool_Pickaxe_Iron"))
    item.put("Metadata", mR)
    f2 = FN.apply(JArray(JObject)([U1, item]))
    f3 = FN.apply(JString("x"))
    f4 = FN.apply(JArray(JObject)([U1, JString("Tool_Pickaxe_Iron"), mR, JString("release")]))
    f5 = FN.apply(JArray(JObject)([U1, JString("Tool_Pickaxe_Iron"), mR, JString("commit")]))
    kc(f4[0] is None and f5[0] is None, "J: the bridge's release + commit modes")
    kc(f1[0] is None and f2[0] is None and list(f1[1]) == list(f2[1]) and f3[0] is not None,
       "J: gear:fn:salvage takes { UUID, id, metadata, mode } or { UUID, item doc {Id, Metadata} } and answers { why, String[] ids, Long[] qty, key }")
    kc(str(type(f1[2][0])).find("Long") >= 0, "J: quantities are java.lang.Long: %s" % type(f1[2][0]))
    K.notes.append("H317 counters: %s; salvage %s" % (list(LL.TN17), str(Salv.statusText())))
    K.notes.append("H317 logs: %s" % [x[:160] for x in logs() if "WARN" in x][:6])


# ====================================================================================================== main
def main():
    if "--h317" in sys.argv:
        run_h317(arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--only", "--keep", "--dir", "--jar", "--root", "--out") for a in sys.argv[1:]):
        H316["main"]()          # a 0.3.16 child flag (it dispatches and returns)
        return
    assert os.path.isfile(J316), J316
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    H316["run_assets316"] = run_assets317          # the jar compare of THIS round (0.3.16 -> 0.3.17)
    _orig_children = H316["child"]

    def child2(env, *args):
        return _orig_children(env, *args)
    # ours runs after the 0.3.16 children: wrap take() so the h316 result is followed by h317 inside the same scratch folder
    _take = H316["take"]

    def take2(path, label):
        d = _take(path, label)
        if label == "h316" and want("h317"):
            env = dict(os.environ)
            env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
            env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
            out = os.path.join(SCRATCH, "h317.json")
            pr = child2(env, "--h317", "--out", out)
            check(pr.returncode == 0, "h317: the child exited cleanly (%s)" % pr.returncode)
            _take(out, "h317")
        return d
    H316["take"] = take2
    if only and "h317" in only.split(",") and "h316" not in only.split(","):
        sys.argv[sys.argv.index("--only") + 1] = only + ",h316"
    H316["main"]()


if __name__ == "__main__":
    main()
