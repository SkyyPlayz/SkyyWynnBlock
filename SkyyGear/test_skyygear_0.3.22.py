"""Harness for SkyyGear 0.3.22 (tools/gear_0_3_22_patch.py header = THE 15-STEP METAL LADDER, round G1) = the 0.3.21 harness (and through it the
whole older chain) run on the 0.3.22 jar + S322 (the jar compare 0.3.21 -> 0.3.22, replacing S321) + H322 (inside the h319 child, after H319 +
H320 + H321, on the same booted engine), plus a --static phase that needs no jar:
    python tools/gear_0_3_22_patch.py && python SkyyGear/build_skyygear_0.3.22.py
    python SkyyGear/test_skyygear_0.3.22.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.22.py --static [--keep]          (no jars, no Assets.zip, no server jar)

  STATIC (--static)
       G  THE PATCH: tools/gear_0_3_22_patch.py run TWICE into a scratch tree (a copy of the patch + build_skyygear_0.3.21.py + deploy_set.py)
          -> byte-identical outputs, = SkyyGear/build_skyygear_0.3.22.py, compiles as Python, keeps the source's line endings
       A  THE ANCHORS: VERSION; the ore table + tier power defaults; catOf -> oreM, decideI -> oreI before the old tier maths; slowF 4;
          GearToolHitSys -> oreDr; pfort in perkFx + LifePage.effect; tierFor from LEVEL_BANDS; UpgPage.tierTag from the ladder;
          migrate0322 = the migrate0321 shape on the M22_ block, called after migrate0321; the fresh block before the zone armor block
  S322 the jar 0.3.21 -> 0.3.22: adds / removes nothing, changes only manifest.json + server.lang (exactly the 38 tagged descriptions: the cans,
       Harvesters, zone Mining sets - only their "T<n> " number); the changed classes = S322_MUST (+ S322_MAY)
  H322 (the h319 child, ONE booted engine) - real code:
       A  the ladder table (GearLL.LT_* = tools/tier_tags.py TOOL_METALS), ltier / ltag / lnoun / nextPick
       B  gate.oreTiers: oreM codes, catOf on the REAL ore BlockTypes (vanilla + none of the zone blocks needed), a live edit, a bad text =
          the default, checkOreTiers; tool.tierPower: tp, a live edit, checkTierPower
       C  decideI on ore = the python model for every vanilla pickaxe x every table ore (result, speed code, ladder T); a hatchet / bare hands
          on ore are still refused; logs + crops untouched
       D  oreDr on the real BlockTypes: normal = max(vanilla, 0.25 x tp ratio), slow = 0.25; LL.hit speed codes; slowF + gate.halfFactor
       E  the pickaxe Mining Fortune: pfort, LifePage.effect, a live lifelong.perkFortune.mining edit; hatchet / pole unchanged
       F  the shown numbers: GearView.tierFor = tools/tier_tags.py tier_for_level (Lv 0-100), flavTag, UpgPage.tierTag (tools + the pole)
       G  level bands: the 8 new metals by id word (Weapon_Wand_Lead_SkyWynn 22-30 ... Lumen 50-60), Bronze 15-23 and the zone armor unchanged;
          m22Update on a file without the block (8 rows at the END, CRLF kept, run once, an admin's row in any case kept + noted)
  NOT COVERED (smoke test / Skyy in game): real hits through the DamageBlockEvent on a live world, the migration on the real config.properties.
Older checks this round changes on purpose are WAIVED with the reason (WAIVE_322: the renumbered tags, ore never refused, the ore codes).
Scratch: tools/dev/scratch/g1/h322/gear/harness (full run) and .../h322/static (--static), deleted at the end unless --keep.
Exit code 1 on any failure (--static: 0 = PASS).
"""
import os, sys, json, shutil, zipfile, re, subprocess, math

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


VERSION = "0.3.22"
V321 = "0.3.21"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g1", "h322")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J321 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V321))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_22_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.22.py")
GEN321 = os.path.join(HERE, "build_skyygear_0.3.21.py")
ORE_DEF = "Copper:1,Iron:2:1,Silver:2:1,Gold:2:1,Thorium:3,Lead:4:3,Cobalt:6,Chromium:7:6,Adamantite:9,Slag:10:9,Mithril:12,Titanium:13:12,Onyxium:15"
ORES = [(w, int(x.split(":")[1]), int(x.split(":")[2]) if x.count(":") == 2 else 0) for x in ORE_DEF.split(",") for w in [x.split(":")[0]]]
TP = [round(1.4 ** (t - 1), 2) for t in range(1, 17)]
PICK_T = [1, 2, 4, 7, 10, 13, 16]
PICKS = [("Crude", 1), ("Wood", 1), ("Copper", 1), ("Scrap", 1), ("Iron", 2), ("Thorium", 4), ("Cobalt", 7), ("Adamantite", 10), ("Mithril", 13),
         ("Onyxium", 16)]
BANDS22 = [("Lead", 22, 30), ("Dusk", 24, 32), ("Chromium", 28, 40), ("Azurvane", 31, 41), ("Slag", 37, 45), ("Cinder", 39, 47),
           ("Titanium", 45, 55), ("Lumen", 50, 60)]

S322_MUST = {"GearLL": "ladder table, ore gate (oreM / oreI / oreDr / tp), pfort", "GearCfg": "4 new rows + migrate0322",
             "GearView": "tierFor from LEVEL_BANDS", "GearToolHitSys": "oreDr + the half speed code", "LifePage": "pfort in effect",
             "UpgPage": "tierTag from the ladder", "GearPackId": "the pack tags renumbered (tools/pack_drops.py tag_of)"}
S322_MAY = {"SkyyGearPlugin": "the version text + the migrate0322 call", "Gear": "the setup call", "CfgFn": "config kit: the version",
            "CfgRows": "config kit: the version", "CfgFile": "config kit", "CfgDefaults": "config kit", "CfgKit": "config kit", "CfgPub": "config kit",
            "GearCfgRows": "the row table"}


def model(t, n, h):
    """(result, speed code) of a ladder-T pickaxe on an ore (normal n, half h)"""
    if t >= n:
        return 0, 0
    if h and t >= h:
        return 1, 4
    nxt = min([p for p in PICK_T if p > t] or [999])
    return 1, (1 if nxt >= n else 3)


# ---- the 0.3.21 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder (and THIS file)
if not STATIC:
    _H321 = os.path.join(HERE, "test_skyygear_0.3.21.py")
    _T321 = open(_H321, encoding="utf-8").read()
    _cut = _T321.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    _only = arg("--only")
    if _only:          # h322 runs inside the h319 child (like h320 / h321)
        _only = ",".join(sorted(set(("h319" if x in ("h321", "h322") else x) for x in _only.split(","))))
    sys.argv = [_H321, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", _only] if _only else []) + [a for a in _argv[1:] if a in ("--h319",)] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H321 = {"__name__": "skyygear_h321", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T321[:_cut], _H321 + " (library)", "exec"), H321)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = _only
    H321["VERSION"] = VERSION
    H320 = H321["H320"]
    H320["VERSION"] = VERSION
    H319 = H321["H319"]
    H319["VERSION"] = VERSION
    H316 = H321["H316"]
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


# ====================================================================================================== S322
def run_assets322():
    ea, eb = entries(J321), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "S322: 0.3.21 -> 0.3.22 adds / removes nothing, changes only manifest.json + server.lang: added %s gone %s changed %s" % (added[:4], gone[:4], changed))
    check('"0.3.22"' in eb.get("manifest.json", b"").decode("utf-8", "replace"), "S322: the manifest says 0.3.22")
    la = ea["Server/Languages/en-US/server.lang"].decode("utf-8").splitlines()
    lb = eb["Server/Languages/en-US/server.lang"].decode("utf-8").splitlines()
    d = [(x, y) for x, y in zip(la, lb) if x != y]
    num = re.compile(r"^(items\.[A-Za-z_]+\.description = )T(\d+) (.*)$")
    ok = len(la) == len(lb) and len(d) == 38
    for x, y in d:
        mx, my = num.match(x), num.match(y)
        ok = ok and mx is not None and my is not None and mx.group(1) == my.group(1) and mx.group(3) == my.group(3)
    import tier_tags as TT
    want = dict(("items.%s.description = " % i, TT.tag_for(i)) for i in TT.ids_for("SkyyGear") if i in TT.OWN_IDS)
    tags_ok = all(any(y.startswith(k + want[k] + " - ") for k in want if y.startswith(k)) for x, y in d)
    check(ok and tags_ok, "S322: server.lang = 0.3.21's with exactly 38 description tags renumbered (cans, Harvesters, zone Mining sets; only "
                          "the T number, = tools/tier_tags.py): %d changed, e.g. %s" % (len(d), [y[:60] for x, y in d[:2]]))
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.21 -> 0.3.22: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S322_MUST) | set(S322_MAY), "S322: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S322_MUST) - set(S322_MAY)))
    check(set(S322_MUST) <= set(chg), "S322: every class the patch edits really changed: unchanged %s" % sorted(set(S322_MUST) - set(chg)))


# ====================================================================================================== H322 (in the h319 child)
def _h322(L, K):
    from jpype import JClass, JInt, JFloat, JString
    import tier_tags as TT
    P = lambda n: JClass(PKG + n)
    LL, Cfg, Lvl, View, stack, apply, FRESH = L["LL"], L["Cfg"], L["Lvl"], L["View"], L["stack"], L["apply"], L["FRESH"]
    PR1 = L["PR1"]
    Life, Upg = P("LifePage"), P("UpgPage")
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()

    def kc(cond, what):
        K.check(bool(cond), "H322 " + what)
    apply()
    # ============================================================== A
    kc([str(x) for x in LL.LT_W] == [w for w, t in TT.TOOL_METALS] and [int(x) for x in LL.LT_N] == [t for w, t in TT.TOOL_METALS]
       and [str(x) for x in LL.LT_WORD] == [TT.metal_word(w) for w, t in TT.TOOL_METALS] and [str(x) for x in LL.LT_NOUN] == list(TT.LADDER)
       and [int(x) for x in LL.PICK_T] == PICK_T, "A: GearLL.LT_* = tools/tier_tags.py TOOL_METALS / LADDER; PICK_T %s" % [int(x) for x in LL.PICK_T])
    kc([int(LL.ltier("Tool_Pickaxe_" + m)) for m, t in PICKS] == [t for m, t in PICKS] and int(LL.ltier("Tool_Hatchet_Pickaxe_Multitool_Iron")) == 2
       and int(LL.ltier("Tool_Pickaxe_Lead_SkyWynn")) == 5 and int(LL.ltier("Weapon_Wand_Lumen_SkyWynn")) == 15 and int(LL.ltier("Rock_Stone")) == 0,
       "A: ltier = the 15-step ladder of the id's metal word (Crude / Copper T1, Iron T2, Thorium T4, Cobalt T7 ... Lead T5, Lumen T15)")
    kc(str(LL.ltag("Tool_Pickaxe_Wood", JInt(1))) == "T1 Crude" and str(LL.ltag("Tool_Sickle_Steel_Rusty", JInt(1))) == "T2 Iron"
       and str(LL.ltag("Tool_Pickaxe_Scrap", JInt(1))) == "T1 Copper" and str(LL.lnoun(JInt(3))) == "Bronze" and str(LL.lnoun(JInt(16))) == "Onyxium"
       and [int(LL.nextPick(JInt(t))) for t in (1, 2, 3, 4, 13, 16)] == [2, 4, 4, 7, 16, 999], "A: ltag / lnoun / nextPick")
    # ============================================================== B
    kc([int(LL.oreM(w)) for w, n, h in ORES] == [n * 100 + h for w, n, h in ORES] and int(LL.oreM("lead")) == 403 and int(LL.oreM("Prisma")) == -1,
       "B: oreM = the default gate.oreTiers (normal x 100 + half), any case; Prisma not gated")
    real = {}
    for b_ in sorted(str(k) for k in bmap.keySet()):
        if b_.startswith("Ore_") and not b_.startswith("*") and b_.split("_")[1] in dict((w, 1) for w, n, h in ORES) and b_.split("_")[1] not in real:
            real[b_.split("_")[1]] = b_
    kc(len(real) >= 7 and all(list(LL.catOf(b_)) == [1, int(LL.oreM(w))] for w, b_ in real.items()) and list(LL.catOf("*Ore_Iron_Stone")) == [1, 201]
       and list(LL.catOf("Ore_Lead_Sandstone_SkyWynn")) == [1, 403] and list(LL.catOf("Ore_Titanium_Basalt_SkyWynn")) == [1, 1312]
       and int(list(LL.catOf("Ore_Prisma_Stone"))[1]) == -1 and list(LL.catOf("Wood_Oak_Trunk")) == [3, 1],
       "B: catOf on the real ore blocks %s + the zone ore ids (by their 2nd word); logs unchanged" % sorted(real.values())[:4])
    apply(gate__oreTiers="Copper:5:2,Lead:9")
    e1 = (int(LL.oreM("Copper")), int(LL.oreM("Iron")), int(LL.oreM("Lead")))
    apply(gate__oreTiers="Copper:0,Iron")
    e2 = int(LL.oreM("Iron"))
    apply()
    kc(e1 == (502, -1, 900) and e2 == 201, "B: a live gate.oreTiers edit (%s); a bad text = the default (%s, one WARN)" % (e1, e2))
    kc(LL.checkOreTiers("gate.oreTiers", ORE_DEF) is None and LL.checkOreTiers("gate.oreTiers", "Copper:1") is None
       and all(LL.checkOreTiers("gate.oreTiers", v) is not None for v in ("Copper", "Copper:0", "Iron:2:2", "Iron:2:3", "Co pper:1", "Iron:2,iron:3", "Iron:x")),
       "B: checkOreTiers")
    kc([round(float(LL.tp(JInt(t))), 2) for t in range(1, 17)] == TP and float(LL.tp(JInt(40))) == TP[-1] and float(LL.tp(JInt(0))) == 1.0,
       "B: tool.tierPower default 1.4^(T-1), clamped at both ends")
    apply(tool__tierPower="1,2,4")
    t1 = [float(LL.tp(JInt(t))) for t in (1, 2, 3, 9)]
    apply(tool__tierPower="1,-2")
    t2 = float(LL.tp(JInt(2)))
    apply()
    kc(t1 == [1.0, 2.0, 4.0, 4.0] and t2 == 1.4 and LL.checkTierPower("tool.tierPower", "1,1.4") is None and LL.checkTierPower("tool.tierPower", "1,0") is not None
       and LL.checkTierPower("tool.tierPower", "a") is not None, "B: tool.tierPower live edit / bad text = the default / checkTierPower")
    # ============================================================== C
    bad = []
    for m, t in PICKS:
        for w, n, h in ORES:
            d = [int(x) for x in LL.decideI("Tool_Pickaxe_" + m, JInt(1), JInt(n * 100 + h))]
            r, q = model(t, n, h)
            if len(d) < 9 or d[0] != r or d[8] != q or d[3] != t or d[6] != n:
                bad.append((m, w, d, (r, q)))
    for w, n, h in ORES:
        d = [int(x) for x in LL.decideI("Tool_Hatchet_Pickaxe_Multitool_Cobalt", JInt(1), JInt(n * 100 + h))]
        if model(7, n, h) != (d[0], d[8]):
            bad.append(("multitool", w, d))
    kc(not bad, "C: decideI on ore = the model for 10 pickaxes x 13 ores + the Cobalt multitool (never 2): %s" % bad[:3])
    dh = [int(x) for x in LL.decideI("Tool_Hatchet_Iron", JInt(1), JInt(201))]
    dn = [int(x) for x in LL.decideI(None, JInt(1), JInt(201))]
    dl = [int(x) for x in LL.decideI("Tool_Hatchet_Copper", JInt(3), JInt(3))]
    kc(dh[0] == 2 and dh[3] == -1 and dn[0] == 2 and dl[0] == 1 and dl[5] == 2, "C: a hatchet / bare hands on ore still refused; logs keep the old tiers (%s %s %s)" % (dh, dn, dl))
    # ============================================================== D
    blk = dict((w, bmap.get(real[w])) for w in real)
    dd = []
    for m, t in (("Copper", 1), ("Iron", 2), ("Thorium", 4), ("Cobalt", 7), ("Mithril", 13)):
        for w in sorted(blk):
            n, h = [(n_, h_) for w_, n_, h_ in ORES if w_ == w][0]
            r, q = model(t, n, h)
            lo = float(LL.oreDr(stack("Tool_Pickaxe_" + m), blk[w], JFloat(0.01)))
            hi = float(LL.oreDr(stack("Tool_Pickaxe_" + m), blk[w], JFloat(9.0)))
            rp = float(LL.rpow(blk[w], JInt(n)))
            want_lo = 0.25 * TP[t - 1] / TP[n - 1] if r == 0 else rp
            want_hi = max(9.0, want_lo) if r == 0 else rp
            if abs(lo - want_lo) > 1e-5 * max(1.0, want_lo) or abs(hi - want_hi) > 1e-5 * max(1.0, want_hi):
                dd.append((m, w, lo, hi, want_lo))
    kc(blk and not dd, "D: oreDr on the real ore blocks: normal = max(vanilla, 0.25 x tp[T] / tp[normal]), slow = the right-tier pickaxe's power: %s" % dd[:3])
    rq = [round(float(LL.rpow(blk[w], JInt(n))), 3) for w, n in (("Copper", 1), ("Iron", 2), ("Cobalt", 6), ("Mithril", 12))]
    kc(rq == [0.25, 0.25, 0.25, 1.0] and [str(x) for x in LL.PICK_ID] == ["Tool_Pickaxe_" + m for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")],
       "D (critic M1): rpow = the right-tier pickaxe on the block (Mithril ore is Rocks: the Mithril pickaxe's 1.0, like 0.3.21's refPow): %s" % rq)
    fl = [bool(LL.floorOre(w)) for w in ("Lead", "chromium", "Slag", "Titanium", "Thorium", "Copper")]
    apply(gate__oreFloor="Thorium")
    f_lo = float(LL.oreDr(stack("Tool_Pickaxe_Copper"), blk["Thorium"], JFloat(0.084))) * float(LL.slowF(JInt(3)))
    f_hi = float(LL.oreDr(stack("Tool_Pickaxe_Copper"), blk["Thorium"], JFloat(0.001))) * float(LL.slowF(JInt(3)))
    apply(gate__oreFloor="Lead,9")
    fbad = bool(LL.floorOre("Lead"))
    apply()
    kc(fl == [True, True, True, True, False, False] and abs(f_lo - 0.084) < 1e-5 and abs(f_hi - 0.025) < 1e-5 and fbad
       and LL.checkOreFloor("gate.oreFloor", "Lead,Slag") is None and LL.checkOreFloor("gate.oreFloor", "") is None and LL.checkOreFloor("gate.oreFloor", "Lead,9") is not None,
       "D (critic M1): gate.oreFloor (default the 4 zone ores): a floored ore's slowed hit never ends below vanilla (%.4f / %.4f), a bad text = the default" % (f_lo, f_hi))
    kc(float(LL.oreDr(stack("Tool_Hatchet_Iron"), blk["Iron"], JFloat(0.3))) < 0 and float(LL.oreDr(stack("Tool_Pickaxe_Iron"), bmap.get("Rock_Stone"), JFloat(0.3))) < 0
       and float(LL.oreDr(stack("Tool_Pickaxe_Iron"), bmap.get("Wood_Oak_Trunk"), JFloat(0.3))) < 0, "D: oreDr = -1 for a hatchet on ore, rock, logs")
    hq = [int(LL.hit(PR1, stack("Tool_Pickaxe_" + m), blk[w])) for m, w in (("Copper", "Copper"), ("Copper", "Iron"), ("Iron", "Thorium"), ("Copper", "Thorium"), ("Thorium", "Cobalt"))]
    hq.append(int(LL.hit(PR1, stack("Tool_Pickaxe_Copper"), blk["Cobalt"])))
    kc(hq == [0, 4, 1, 3, 1, 3], "D: LL.hit speed codes: normal 0, Copper on Iron half 4, Iron on Thorium / Thorium on Cobalt one pickaxe step below 1, "
                                 "Copper on Thorium / Cobalt further 3 (never 2): %s" % hq)
    s0 = [float(LL.slowF(JInt(q))) for q in (0, 1, 3, 4)]
    apply(gate__halfFactor="0.25")
    s1 = float(LL.slowF(JInt(4)))
    apply()
    kc(s0 == [1.0, 0.4, 0.1, 0.5] and s1 == 0.25, "D: slowF 1 / 0.4 / 0.1 / 0.5 (half) + a live gate.halfFactor edit: %s %s" % (s0, s1))
    kc("ore by its ladder tier (gate.oreTiers, half x0.5, never refused)" in str(LL.statusText()), "D: statusText names the ore gate")
    # ============================================================== E
    pf = [float(LL.pfort(JInt(k))) for k in range(6)]
    e0 = str(Life.effect(JInt(0), JInt(1), JInt(3)))
    e1 = str(Life.effect(JInt(1), JInt(1), JInt(3)))
    apply(lifelong__perkFortune__mining="7")
    pf7 = float(LL.pfort(JInt(0)))
    apply()
    kc(pf == [10.0, 2.0, 2.0, 2.0, 2.0, 2.0] and e0 == "+30 Mining Fortune" and e1 == "+6 Foraging Fortune" and pf7 == 7.0,
       "D/E: the pickaxe Mining Fortune +10 a level (lifelong.perkFortune.mining), others 2: %s / %s / %s" % (pf, e0, e1))
    # ============================================================== F
    kc(all(int(View.tierFor(JInt(lv), "x")) == TT.tier_for_level(lv) for lv in range(0, 101)) and int(View.tierFor(JInt(1), "Armor_Onyxium_Head")) == 16,
       "F: GearView.tierFor = tools/tier_tags.py tier_for_level (Lv 0-100), Onyxium ids T16")
    ft = View.flavTag("Armor_Bronze_Head")
    kc(ft is not None and str(ft) == "T3 Bronze Heavy" and str(View.flavTag("Armor_Bronze_Ornate_Chest")) == "T3 Bronze Heavy",
       "F (critic M2): vanilla Bronze armor = its metal word first, 'T3 Bronze Heavy' (not the Lv 15 band's T2 Iron): %s" % ft)
    kt = [str(x) if x is not None else None for x in (View.flavTag("Armor_Kweebec_Chest"),)]
    kc(kt[0] is None or kt[0].startswith("T") and not kt[0].startswith("T3 Bronze"), "F: an armor without a metal word keeps its level band tag: %s" % kt)
    lo = dict((i, None if View.flavTag(i) is None else str(View.flavTag(i))) for i in ("Armor_Cloth_Wool_Chest", "Armor_Leather_Soft_Head"))
    kc(lo == {"Armor_Cloth_Wool_Chest": "T1 Crude Cloth", "Armor_Leather_Soft_Head": "T1 Crude Light"},
       "F: a Lv 1 band armor keeps 'T1 Crude' (tools/tier_tags.py level_tag): %s" % lo)
    tg = dict((i, str(Upg.tierTag(i))) for i in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Wood", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Cobalt", "Tool_Sickle_Steel_Rusty",
                                                 "Tool_Hatchet_Adamantite", "Tool_WaterCan_Iron", "Rock_Stone"))
    kc(tg == {"Tool_Pickaxe_Crude": "T1 Crude", "Tool_Pickaxe_Wood": "T1 Crude", "Tool_Pickaxe_Copper": "T1 Copper", "Tool_Pickaxe_Cobalt": "T7 Cobalt",
              "Tool_Sickle_Steel_Rusty": "T2 Iron", "Tool_Hatchet_Adamantite": "T10 Adamantite", "Tool_WaterCan_Iron": "T2 Iron", "Rock_Stone": ""},
       "F: UpgPage.tierTag = the 15-step ladder: %s" % tg)
    pl = str(LL.KLAD[int(LL.POLE)]).split(",")
    pt = [str(Upg.tierTag(i)) for i in pl[:3]]
    kc(pt[0] == "T1 Crude" and pt[1].startswith("T1 ") and pt[2].startswith("T2 "), "F: the pole ladder tags (Wooden T1 Crude, then T1, T2): %s" % pt)
    GPI = P("GearPackId")
    kc(str(GPI.tag("RookChestBlack")) == "T2 Iron" and str(GPI.tier("RookChestBlack")) == "iron" and int(GPI.at("WardenChest")) == 2
       and int(GPI.at("RookChestBlack")) == 1 and int(GPI.at("Sword_Iron_Black")) == 0 and GPI.tier("Armor_Iron_Chest") is None
       and all(str(GPI.tag(i)) == __import__("pack_drops").tag_of(str(GPI.tier(i))) for i in ("RookChestBlack", "WardenChest", "Sword_Iron_Black")),
       "F: the pack tags follow the ladder (RookChestBlack iron 'T2 Iron' Heavy, WardenChest Light, a weapon 0, a vanilla id none; = tools/pack_drops.py tag_of)")
    # ============================================================== G
    bd = dict((m, [int(x) for x in Lvl.band("Weapon_Wand_%s_SkyWynn" % m)]) for m, a, b in BANDS22)
    kc(all(bd[m] == [a, b, 1] for m, a, b in BANDS22), "G: the 8 new metals' level bands by id words <Metal>_SkyWynn: %s" % bd)
    tb = [[int(x) for x in Lvl.band(i)] for i in ("Armor_Lead_Chest", "Tool_Pickaxe_Lead", "Weapon_Sword_Titanium")]
    kc(all(not (b_[2] == 1 and b_[0] in (22, 45)) for b_ in tb), "G (critic L1): another mod's Lead / Titanium id never gets our band: %s" % tb)
    kc([int(x) for x in Lvl.band("Armor_Bronze_Head")][:2] == [15, 23] and [int(x) for x in Lvl.band("Armor_Mining_Lead_Head")][:2] == [22, 27]
       and [int(x) for x in Lvl.band("Weapon_Sword_Mithril")][:2] == [40, 49], "G: Bronze 15-23, the zone Lead armor 22-27, Mithril 40-49 unchanged")
    fresh = str(FRESH)
    zl = fresh.split("\n")
    hi = zl.index(str(Cfg.M22_HEAD)) if str(Cfg.M22_HEAD) in zl else -1
    blk_len = 2 + sum(int(x) for x in Cfg.M22_GS) + len(Cfg.M22_GC)
    old = "\r\n".join(x for k, x in enumerate(zl) if not (hi - 1 <= k < hi + blk_len))
    kc(hi > 0 and str(Cfg.M22_MARK_ID) not in old and "level.material.Lead_SkyWynn" not in old, "G: a 0.3.21-shaped file (the fresh text minus the block)")
    r = Cfg.m22Update(old)
    nt = str(r[0]) if r is not None else ""
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    pn = Props()
    pn.load(SR(nt))
    kc(r is not None and nt.startswith(old) and nt.count(str(Cfg.M22_MARK_ID)) == 1 and all(str(pn.getProperty("level.material.%s_SkyWynn" % m)) == "%d,%d" % (a, b) for m, a, b in BANDS22)
       and len(str(r[2]).split(", ")) == 8 and "\r\n" in nt[len(old):] and nt.rstrip().endswith("level.material.Lumen_SkyWynn=50,60"),
       "G: m22Update adds the 8 rows + the marker at the END, nothing before changes, CRLF kept: %s" % (str(r[2])[:80] if r is not None else None))
    kc(Cfg.m22Update(nt) is None, "G: a second run = null (run-once marker)")
    r2 = Cfg.m22Update(old + "\r\nlevel.material.lead_skywynn=1,5\r\n")
    kc(r2 is not None and "level.material.Lead_SkyWynn is already in the file - kept" in [str(x) for x in r2[1]] and "level.material.Lead_SkyWynn=" not in str(r2[0])
       and len(str(r2[2]).split(", ")) == 7, "G: an admin's row in another case is kept + noted, never doubled")


# ---- older checks this round changes ON PURPOSE (prefix, why)
_WHY_TAG = ("0.3.22 by design (Skyy 2026-10-17 'Yes, full 15-step ladder'): the tier tags renumber to the 15-step ladder (tools/tier_tags.py "
            "TT_VERSION 2) - H322 F / S322 check the new numbers")
_WHY_ORE = ("0.3.22 by design (spec 3.2, Skyy 'Yes, all defaults'): ore is gated by gate.oreTiers on the 15-step ladder (normal / half / slower, "
            "never refused); catOf codes are normal x 100 + half - H322 B-D check the new gate")
WAIVE_322 = [("A: has / tier / tag / at of named ids (RookChestBlack iron 'T3 Iron' Heavy", _WHY_TAG + " (H322 F re-checks the same ids with 'T2 Iron')"),
             ("H321 F: vanilla Bronze armor (Lv 15 band) = 'T3 Iron Heavy'", _WHY_TAG + " (H322 F: 'T2 Iron Heavy')"),
             ("H321 F: tierFor = tools/tier_tags.py tier_for_level", _WHY_TAG + " (H322 F: tierFor = tier_for_level for Lv 0-100)")]
if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h322(L, K):
        _h319_prev(L, K)
        try:
            _h322(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H322: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h322
    H320["run_assets320"] = run_assets322          # the jar compare of THIS round (0.3.21 -> 0.3.22)
    H320["J319"] = J321
    H316["WAIVE_316"].extend(WAIVE_322)


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
            shutil.copyfile(GEN321, os.path.join(r, "SkyyGear", os.path.basename(GEN321)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.22.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.22.py (the committed file is the patch's output)")
        src = open(GEN321, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.22.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.22"\n' in s and "GENERATED by tools/gear_0_3_22_patch.py" in s, "A: VERSION 0.3.22 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        check("TIER_POW_STEP = 1.4" in s and "G22_OWN_PICKS = []" in s and "ORE_BASE = 0.25" in s and s.index("G22_ORE = [") < s.index("CFG_ROWS = ["),
              "A: the ore table / tier power / own-pick hook are defined before the Server Setup rows")
        check("return new int[] { 1, oreM(w[1]) };" in s and "find(ORE_W, ORE_M, w[1])" not in s, "A: catOf asks gate.oreTiers for ore")
        i_d = s.index("public static int[] decideI(String id, int c, int m) {")
        dI = s[i_d:s.index('}""")', i_d)]
        check(dI.index("if (!fits) {") < dI.index("if (c == 1) return oreI(id, f, m);") < dI.index("int t = tier(id);"),
              "A: decideI: ore goes to oreI after the fitting-tool check, before the log / crop tier maths")
        check("(q == 4 ? @PKG@.GearCfg.GATE_HALF : 1.0)" in s and "if (gq == 1 || gq == 3 || gq == 4) d1 = " in s
              and "float dr = od >= 0.0f ? od : (gq == 1 || gq == 3 ? @PKG@.GearLL.refPow(" in s, "A: the hit system: oreDr first, the half speed code 4")
        check("double fo = (double) perkEff(u, P, k, 1) * pfort(k);" in s and "@PKG@.GearLL.pfort(k)) + \" \" + @PKG@.GearLL.KSKILL[k] + \" Fortune\"" in s,
              "A: the Fortune line reads pfort (perkFx + the Upgrade page text)")
        check('F(gvw, "public static final int[] LB_LO = %s;" % jints([_l for _l, _t in TT.LEVEL_BANDS]))' in s and "return @PKG@.GearLL.ltag(id, 1);" in s,
              "A: GearView.tierFor from LEVEL_BANDS; UpgPage.tierTag from the ladder")
        i_z = s.index("public static Object[] zmUpdate(String text) {")
        i_m = s.index("public static Object[] m22Update(String text) {")
        zu = s[i_z:s.index('}""")', i_z)]
        mu = s[i_m:s.index('}""")', i_m)]
        check(mu == zu.replace("zmUpdate", "m22Update").replace("ZM_", "M22_").replace("if (pp.getProperty(M22_GK[x]) != null)", "if (has22(pp, M22_GK[x]))"),
              "A: m22Update = the zmUpdate text on the M22_ block (case-blind key check)")
        check(s.index("@PKG@.GearCfg.migrate0321();") < s.index("@PKG@.GearCfg.migrate0322();") and s.count("@PKG@.GearCfg.migrate0322();") == 1
              and "CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M22_WHO" in s, "A: migrate0322 after migrate0321, History snapshot first")
        check(s.index('L += [""] + M22_LINES') < s.index('L += [""] + ZM_LINES'), "A: the fresh block before the zone mining armor block")
        for k_ in ("gate.oreTiers", "gate.halfFactor", "tool.tierPower", "lifelong.perkFortune.mining", "gate.oreFloor"):
            check(('("%s", ' % k_) in s and ('"%s"' % k_) in s[s.index("_DANGER"):s.index("_DANGER") + 20000], "A: the Server Setup row %s (danger list)" % k_)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
            try:
                os.rmdir(SCR_BASE)
            except OSError:
                pass
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    assert os.path.isfile(J321), J321
    H320["main"]()


if __name__ == "__main__":
    main()
