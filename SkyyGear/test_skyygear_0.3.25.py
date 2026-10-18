"""Harness for SkyyGear 0.3.25 (tools/gear_0_3_25_patch.py header = the lifelong multitool merge + accBp cache + GearReq rows + the A2 Charged trust)
= the 0.3.23 harness (and through it the whole older chain, or its fallback: assets + the h319 child) run on the 0.3.25 jar + S325 (the jar compare
0.3.24 -> 0.3.25, replacing S323) + H325 (inside the h319 child, after H319 .. H323, on the same booted engine), plus a --static phase (no jar):
    python tools/gear_0_3_25_patch.py && python SkyyGear/build_skyygear_0.3.25.py
    python SkyyGear/test_skyygear_0.3.25.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.25.py --static [--keep]

  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.25.py, compiles, line endings kept
       A  the anchors: VERSION; no new system / command / class; helpers before their callers (javassist order)
  S325 the jar 0.3.24 -> 0.3.25: nothing added / removed; only manifest.json + the patched classes change (S325_MUST every one, S325_MAY the kit)
  H325 (the h319 child, ONE booted engine) - real code:
       A  kinds + the ladder: kOf(multitool) = 0 (whatever part.multitool says), crudeOf / ladOf / kname, MT_LAD 16 steps, GearUp.next along it,
          the written step cost = the hatchet's (bars + log), noCraft unchanged for multitools, the two new rows' defaults
       B  THE MERGE on a stand-in inventory: refused before the migration / with different tiers / with the hatchet away; the merge itself
          (the pickaxe's slot = the multitool with the pickaxe's uid, the hatchet gone, counts -1 / -1 / +1, every line of both kept, the better
          rarity, both sets of points kept, hatchet tool keys gone, mt=1, the snapshot names the multitool, History copy + record line), a
          second merge refused; the sweep afterwards: the old hatchet RETIRED, an old pickaxe copy with the multitool's uid removed; perkFx of
          both sets; multi.lifelongFull = no speed share; levelK = Foraging for the hatchet set; gear:fn:lifelong "hatchet" = the multitool uid
          and still four kinds; the tier-up gate asks Mining AND Foraging (+ the GearReq rows)
       C  crash at each step (61 / 62 / 63, the journal on disk): the next look drops it (nothing happened) or finishes it (one tool, no journal)
       D  accBp: cached per player + skill inside 50 ms, a config apply (epoch) re-reads
       E  Charged trust: GearChg.TRUST holds the 72 A2 ids, FALLBACK the 64 non-club ones, no club
  NOT COVERED (smoke test / Skyy in game): the real multitool items (the stand-in engine decodes no tool items: GearLife.TEST_ANYITEM), the Tools
  tab drawing + the two-click arm in game, real block hits with the multitool, a real tier-up payment, SkyyTrees' Tree Feller with the multitool.
Older checks this round changes on purpose are WAIVED with the reason (WAIVE_325).
Scratch: tools/dev/scratch/g325/h325/gear/harness (full run) and .../h325/static (--static), deleted at the end unless --keep.
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


VERSION = "0.3.25"
V324 = "0.3.24"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g325", "h325")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J324 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V324))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_25_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.25.py")
GEN324 = os.path.join(HERE, "build_skyygear_0.3.24.py")
MPRE = "Tool_Hatchet_Pickaxe_Multitool_"
ORDER = ["Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril",
         "Titanium", "Lumen"]
VAN = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
MT_LAD = [MPRE + "Crude"] + [MPRE + (m if m in VAN else m + "_SkyWynn") for m in ORDER]
A2 = ["Weapon_%s_%s_SkyWynn" % (f, m) for f in ("Sword", "Longsword", "Axe", "Battleaxe", "Mace", "Club", "Daggers", "Spear", "Shortbow")
      for m in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")]

S325_MUST = {"GearLL": "kOf / mtm / hostK / kid / levelK / MT_LAD / collWhy / tierWhy / lines / ladders", "GearLife": "the merge + recover + sweep rules",
             "LifePage": "the Make multitool row + the two sets", "GearTool": "mstats (two sets, no downside) + the accBp cache",
             "GearReq": "the multitool rows + collRow0", "UpgPage": "the Requip row's collection row", "GearUp": "the plain-tool text",
             "GearMerge": "the lifelong text", "GearLLFn": "hatchet = the multitool", "GearChg": "TRUST + FALLBACK (A2)",
             "GearCfg": "the two rows + defaultsText in parts", "GearNorm": "ready waits on mt.pend (critic L2)"}
S325_MAY = {"SkyyGearPlugin": "the version text", "CfgFn": "config kit: the version", "CfgRows": "config kit: the rows", "CfgFile": "config kit",
            "CfgDefaults": "config kit", "CfgKit": "config kit", "CfgPub": "config kit"}


# ---- the 0.3.23 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder (and THIS file)
if not STATIC:
    _H323 = os.path.join(HERE, "test_skyygear_0.3.23.py")
    _T323 = open(_H323, encoding="utf-8").read()
    _cut = _T323.rindex('if __name__ == "__main__":')
    _argv = sys.argv
    _only = arg("--only")
    if _only:          # h325 runs inside the h319 child (like h320 .. h323)
        _only = ",".join(sorted(set(("h319" if x in ("h321", "h322", "h323", "h325") else x) for x in _only.split(","))))
    sys.argv = [_H323, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
        (["--only", _only] if _only else []) + [a for a in _argv[1:] if a in ("--h319",)] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H323 = {"__name__": "skyygear_h323", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T323[:_cut], _H323 + " (library)", "exec"), H323)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = _only
    H323["VERSION"] = VERSION
    H322 = H323["H322"]
    H322["VERSION"] = VERSION
    H321, H320, H319, H316 = H322["H321"], H322["H320"], H322["H319"], H322["H316"]
    for _h in (H321, H320, H319):
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


# ====================================================================================================== S325
def run_assets325():
    ea, eb = entries(J324), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["manifest.json"], "S325: 0.3.24 -> 0.3.25 adds / removes nothing and changes only the manifest "
          "(+ classes): added %s gone %s changed %s" % (added[:4], gone[:4], changed))
    man = eb["manifest.json"].decode("utf-8", "replace")
    check('"0.3.25"' in man and "LIFELONG MULTITOOL: merge your lifelong pickaxe + hatchet" in man, "S325: the manifest says 0.3.25 + the round")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.24 -> 0.3.25: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S325_MUST) | set(S325_MAY), "S325: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S325_MUST) - set(S325_MAY)))
    check(set(S325_MUST) <= set(chg), "S325: every class the patch edits really changed: unchanged %s" % sorted(set(S325_MUST) - set(chg)))
    b = eb["com/skyy/gear/UpgPage.class"]
    g = open(GEN, encoding="utf8").read() if os.path.isfile(GEN) else ""
    check("@PKG@.GearReq.collRow(u, id, to0, rqs); @PKG@.GearReq.costRows(inv, u, @PKG@.GearUp.cost(id, to0), rqs); }          // 0.3.25" in g,
          "S325: the Upgrade list's Requip row asks GearReq.collRow too (the generated script)")


# ====================================================================================================== H325 (in the h319 child)
def _h325(L, K):
    from jpype import JClass, JInt, JString, JShort, JImplements, JOverride
    P = lambda n: JClass(PKG + n)
    LL, Cfg, Data, Defs, apply, FRESH = L["LL"], L["Cfg"], L["Data"], L["Defs"], L["apply"], L["FRESH"]
    mkinv, lls, ids, doc, skills, mkpr, said, br = L["mkinv"], L["lls"], L["ids"], L["doc"], L["skills"], L["mkpr"], L["said"], L["br"]
    Life, Tool, Up, Req, Fn, Chg, Gear = P("GearLife"), P("GearTool"), P("GearUp"), P("GearReq"), P("GearLLFn"), P("GearChg"), P("Gear")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")

    def kc(cond, what):
        K.check(bool(cond), "H325 " + what)
    apply()
    # ============================================================== A: kinds + the ladder + rows
    kd = [int(LL.kOf(i)) for i in (MPRE + "Crude", MPRE + "Lead_SkyWynn", "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", MPRE + "Firetine")]
    apply(part__multitool="false")
    kd_off = int(LL.kOf(MPRE + "Iron"))
    apply()
    kc(kd == [0, 0, 0, 1, 1] and kd_off == 0, "A: kOf(multitool) = 0 (the pickaxe kind), also with part.multitool off; an unknown multitool tier stays a hatchet: %s %s" % (kd, kd_off))
    kc(str(LL.crudeOf(JInt(0), MPRE + "Iron")) == MPRE + "Crude" and str(LL.crudeOf(JInt(0), "Tool_Pickaxe_Iron")) == "Tool_Pickaxe_Crude"
       and str(LL.kname(JInt(1), MPRE + "Iron")) == "Multitool" and str(LL.kname(JInt(0), "Tool_Pickaxe_Iron")) == "Pickaxe"
       and str(LL.ladOf(JInt(0), MPRE + "Iron")).split(",") == MT_LAD and str(LL.MT_LAD).split(",") == MT_LAD,
       "A: crudeOf / kname / ladOf of a multitool = the multitool ladder (16 steps, IBC vanilla tiers + our zone metals)")
    bad = [(a, str(Up.next(a))) for a, b in zip(MT_LAD, MT_LAD[1:]) if str(Up.next(a)) != b]
    kc(not bad, "A: GearUp.next walks the multitool ladder Crude .. Lumen: %s" % bad[:3])

    def wc(a, b):
        w = Up.written(a, b)
        return None if w is None else dict(zip([str(x) for x in w[0]], [int(x) for x in w[1]]))
    wm, wh = wc(MPRE + "Copper", MPRE + "Iron"), wc("Tool_Hatchet_Copper", "Tool_Hatchet_Iron")
    wm2, wh2 = wc(MPRE + "Titanium_SkyWynn", MPRE + "Lumen_SkyWynn"), wc("Tool_Hatchet_Titanium_SkyWynn", "Tool_Hatchet_Lumen_SkyWynn")
    kc(wm == wh and wm2 == wh2 and wm is not None, "A: a multitool step costs the hatchet step (one tier-up, both sets): %s %s" % (wm, wm2))
    kc(not bool(LL.noCraft(MPRE + "Iron")) and bool(LL.noCraft("Tool_Pickaxe_Iron")) and bool(LL.ladderTool(MPRE + "Iron")),
       "A: noCraft unchanged for multitools (0.3.24: craftable), pickaxes still refused; the multitool ladder is a lifelong-only ladder")
    kc(bool(Cfg.MULTI_LLFULL) and str(Cfg.MULTI_LADDERS).split(">")[0] == MPRE + "Crude" and "multi.ladders=" in str(FRESH) and "multi.lifelongFull=true" in str(FRESH),
       "A: the two new rows: defaults in the fresh file + GearCfg")
    apply(part__multitool="false")
    kc(Up.next(MPRE + "Iron") is None, "A: part.multitool off = no multitool ladder")
    apply()
    # ============================================================== B: THE MERGE
    Life.TEST_ANYITEM = True
    Um = UUID.fromString("00000000-0000-0000-0000-000000000325")
    pk = "pmt325"
    L["PKEY"][str(Um)] = pk
    PRm = mkpr(Um, "Multi")
    skills(u=Um, Mining=30, Foraging=12, Farming=4, Fishing=4)
    inv, cs = mkinv()
    Life.sweep(PRm, inv, True)
    R = LL.reg(pk)
    tools = dict((x[2], x) for x in lls(cs, pk))
    kc(0 in tools and 1 in tools and str(R.getProperty("migrated")) == "1", "B: the stand-in profile has its lifelong pickaxe + hatchet: %s" % sorted(tools))
    if not (0 in tools and 1 in tools):
        return
    pX, hX = tools[0], tools[1]
    pu, hu = pX[3], hX[3]

    def at(x):
        return cs[x[0]].getItemStack(JShort(x[1]))

    def setdoc(x, fn):
        s0 = at(x)
        d0 = doc(s0).clone()
        fn(d0)
        cs[x[0]].setItemStackForSlot(JShort(x[1]), Data.put(s0, d0, Um))
    BA = JClass("org.bson.BsonArray")

    def mods(*kv):
        def f(d0):
            a = BA()
            for k_, v_ in kv:
                a.add(Data.mod(JString(k_), JInt(v_)))
            d0.put("mods", a)
            d0.put("r", JClass("org.bson.BsonString")(str(Defs.R_ID[2])))
        return f
    setdoc(pX, mods(("mpow", 3), ("mfort", 2)))
    setdoc(hX, mods(("cpow", 4), ("fwis", 1)))
    R.setProperty("pickaxe.up.spd", "3")
    R.setProperty("hatchet.up.spd", "2")
    R.setProperty("hatchet.up.fort", "1")
    R.setProperty("hatchet.resets", "1")
    LL.save(pk, R)
    # refused: the hatchet of another tier
    hs0 = at(hX)
    cs[hX[0]].setItemStackForSlot(JShort(hX[1]), IS(JString("Tool_Hatchet_Copper"), JInt(1)).withMetadata(hs0.getMetadata()))
    c1 = Life.mtCheck(Um, inv, JString(pk), R)
    kc(c1[0] is not None and "not the same tier" in str(c1[0]), "B: a Crude pickaxe + a Copper hatchet are refused with the reason: %s" % c1[0])
    cs[hX[0]].setItemStackForSlot(JShort(hX[1]), hs0)
    # refused: the hatchet away
    cs[hX[0]].removeItemStackFromSlot(JShort(hX[1]))
    c2 = Life.mtCheck(Um, inv, JString(pk), R)
    kc(c2[0] is not None and "hatchet too" in str(c2[0]), "B: the hatchet not on you = refused: %s" % c2[0])
    cs[hX[0]].setItemStackForSlot(JShort(hX[1]), hs0)
    R.remove("migrated")
    c3 = Life.mtCheck(Um, inv, JString(pk), R)
    R.setProperty("migrated", "1")
    kc(c3[0] is not None and "starting tools" in str(c3[0]), "B: no merge before the one-time migration finished: %s" % c3[0])
    R.setProperty("pickaxe.rp", "1")
    c3b = Life.mtCheck(Um, inv, JString(pk), R)
    R.setProperty("pickaxe.rp", "0")
    kc(c3b[0] is not None and "replacement copy" in str(c3b[0]), "B (critic L1): a /pickaxe replacement copy can't be merged: %s" % c3b[0])
    c4 = Life.mtCheck(Um, inv, JString(pk), R)
    kc(c4[0] is None and str(c4[3]) == MPRE + "Crude" and "keeps all 4 lines" in str(Life.mtSummary(c4)), "B: the pair can merge, the preview: %s / %s" % (c4[0], Life.mtSummary(c4) if c4[0] is None else ""))
    before = ids(cs)
    r = str(Life.mtMerge(PRm, inv))
    R = LL.reg(pk)
    after = ids(cs)
    now = [x for x in lls(cs, pk)]
    mt = [x for x in now if str(x[6].getItemId()) == MPRE + "Crude"]
    kc(r.startswith("+") and len(mt) == 1 and mt[0][3] == pu and (mt[0][0], mt[0][1]) == (pX[0], pX[1]) and not [x for x in now if x[3] == hu],
       "B: merged - the pickaxe's slot is the multitool with the pickaxe's uid, the hatchet is gone: %s" % r[:120])
    kc(after.get("Tool_Pickaxe_Crude", 0) == before.get("Tool_Pickaxe_Crude", 0) - 1 and after.get("Tool_Hatchet_Crude", 0) == before.get("Tool_Hatchet_Crude", 0) - 1
       and after.get(MPRE + "Crude", 0) == before.get(MPRE + "Crude", 0) + 1, "B: counts: one pickaxe and one hatchet out, one multitool in")
    md = doc(mt[0][6]) if mt else None
    ml = sorted((str(Data.str(m.asDocument(), "s", "")), int(Data.num(m.asDocument(), "v", 0))) for m in Data.mods(md)) if md is not None else []
    kc(ml == [("cpow", 4), ("fwis", 1), ("mfort", 2), ("mpow", 3)] and int(Data.rarity(md)) == 2 and bool(LL.isLL(md)) and str(LL.owner(md)) == pk,
       "B: every line of both tools is kept, the better rarity, still lifelong + yours: %s" % ml)
    kc(str(R.getProperty("mt")) == "1" and str(R.getProperty("pickaxe.id")) == MPRE + "Crude" and R.getProperty("hatchet.uid") is None and R.getProperty("hatchet.id") is None
       and str(R.getProperty("pickaxe.up.spd")) == "3" and str(R.getProperty("hatchet.up.spd")) == "2" and str(R.getProperty("hatchet.up.fort")) == "1"
       and str(R.getProperty("hatchet.resets")) == "1" and str(R.getProperty("mtHatch")) == hu and R.getProperty("mt.pend") is None
       and str(R.getProperty("pickaxe.snapId")) == MPRE + "Crude", "B: the registry: mt=1, pickaxe.id = the multitool, the hatchet's tool keys gone, BOTH sets of points kept, no journal, the snapshot names the multitool")
    home = os.path.dirname(os.path.dirname(str(LL.file(pk))))
    rec = os.path.join(home, "mtmerge", pk + ".log")
    hist = os.path.join(home, "mtmerge", "history")
    rl = open(rec, encoding="utf-8").read().splitlines() if os.path.isfile(rec) else []
    kc(rl and rl[0].startswith("MERGE ") and any(x.startswith("FINAL ") for x in rl) and os.path.isdir(hist) and os.listdir(hist),
       "B: the record (MERGE + FINAL) and the verified History copy exist: %s" % [x[:40] for x in rl])
    kc(str(Life.mtMerge(PRm, inv)) == "-You already have your multitool.", "B: a second merge is refused")
    qa = LL.perkFx(Um, JInt(1), md)
    qb = LL.perkFx(Um, JInt(3), md)
    kc(abs(float(qa[0]) - (1.0 + 3 * float(Cfg.LL_PSPD) / 100.0)) < 1e-9 and abs(float(qb[0]) - (1.0 + 2 * float(Cfg.LL_PSPD) / 100.0)) < 1e-9 and float(qb[1]) > 0,
       "B: the two sets: stone / ore = the pickaxe set (Breaking Power 3), logs = the hatchet set (2 + its Fortune): %s %s" % (list(qa), list(qb)))
    st_on = Tool.mstats(Um, JString(MPRE + "Crude"), md)
    apply(multi__lifelongFull="false")
    st_off = Tool.mstats(Um, JString(MPRE + "Crude"), md)
    apply()
    kc(float(st_off[4]) > 0 and abs(float(st_on[4]) / float(st_off[4]) * float(Cfg.MULTI_SPD) / 100.0 - 1.0) < 1e-6,
       "B: multi.lifelongFull = no speed share for the lifelong multitool (on / off = 1 / %s): %s %s" % (Cfg.MULTI_SPD, float(st_on[4]), float(st_off[4])))
    kc(int(LL.levelK(Um, JInt(1), MPRE + "Iron")) == min(12, int(LL.cap(MPRE + "Iron"))) and int(LL.levelK(Um, JInt(0), MPRE + "Iron")) == min(30, int(LL.cap(MPRE + "Iron"))),
       "B: levelK: the hatchet set levels with Foraging, the pickaxe set with Mining")
    tw = str(LL.tierWhy(Um, MPRE + "Iron"))
    rq = AL()
    Req.levelRow(Um, JString(MPRE + "Copper"), JString(MPRE + "Iron"), rq)
    rows = [(str(Req.tx(rq, JInt(i))), int(Req.st(rq, JInt(i)))) for i in range(int(rq.size()))]
    skills(u=Um, Mining=30, Foraging=1, Farming=4, Fishing=4)
    tw2 = str(LL.tierWhy(Um, MPRE + "Iron"))
    rq2 = AL()
    Req.levelRow(Um, JString(MPRE + "Copper"), JString(MPRE + "Iron"), rq2)
    rows2 = [(str(Req.tx(rq2, JInt(i))), int(Req.st(rq2, JInt(i)))) for i in range(int(rq2.size()))]
    lst = bool(Req.listed(None, Um, JString(MPRE + "Iron"), None, JString(tw2)))
    skills(u=Um, Mining=30, Foraging=12, Farming=4, Fishing=4)
    kc(len(rows) == 2 and "Foraging" in tw2 and len(rows2) == 2 and rows2[1][1] == 0 and "Foraging" in rows2[1][0] and lst,
       "B: a multitool tier-up needs Mining AND Foraging - two level rows, the Foraging one red when short (and listed): %s %s / %s %s listed %s" % (tw, rows, tw2, rows2, lst))
    fn0 = Fn(JInt(0))
    O = JClass("java.lang.Object")
    JA = JClass("java.lang.reflect.Array")
    a2 = JA.newInstance(O.class_, JInt(2))
    a2[0] = Um
    a2[1] = JString("hatchet")
    kc(str(fn0.apply(a2)) == pu and int(fn0.apply(Um)) == 4, "B: gear:fn:lifelong 'hatchet' = the multitool's uid (Tree Feller on logs), still four kinds")
    # the sweep afterwards: the old hatchet turns up -> retired; an old pickaxe stack with the multitool's uid -> removed
    free_ = [i for i in range(int(cs["storage"].getCapacity())) if cs["storage"].getItemStack(JShort(i)) is None or cs["storage"].getItemStack(JShort(i)).isEmpty()]
    cs["storage"].setItemStackForSlot(JShort(free_[0]), hs0)
    LL.LAST.clear()
    Life.sweep(PRm, inv, True)
    oldh = [x for x in lls(cs, pk) if x[3] == hu]
    kc(oldh and bool(LL.isRt(doc(oldh[0][6]))) and LL.reg(pk).getProperty("hatchet.uid") is None, "B: the old hatchet that turned up is RETIRED, the hatchet kind stays merged")
    pcopy = IS(JString("Tool_Pickaxe_Crude"), JInt(1)).withMetadata(mt[0][6].getMetadata())
    cs["storage"].setItemStackForSlot(JShort(free_[1]), pcopy)
    LL.LAST.clear()
    Life.sweep(PRm, inv, True)
    left = [x for x in lls(cs, pk) if x[3] == pu]
    kc(len(left) == 1 and str(left[0][6].getItemId()) == MPRE + "Crude", "B: an old pickaxe copy with the multitool's uid is removed, the multitool stays: %s" % [str(x[6].getItemId()) for x in left])
    # ============================================================== C: the crash paths
    rows_c = []
    for step, want in ((61, "dropped"), (62, "finished"), (63, "finished")):
        Uc = UUID.fromString("00000000-0000-0000-0000-0000000003%02d" % (step - 30))
        pkc = "pmtc%d" % step
        L["PKEY"][str(Uc)] = pkc
        PRc = mkpr(Uc, "Crash%d" % step)
        skills(u=Uc, Mining=10, Foraging=10, Farming=4, Fishing=4)
        invc, csc = mkinv()
        Life.sweep(PRc, invc, True)
        Life.CRASH_AT = JInt(step)
        try:
            Life.mtMerge(PRc, invc)
        except Exception:
            pass
        Life.CRASH_AT = JInt(0)
        pend = LL.reg(pkc).getProperty("mt.pend")
        LL.REG.clear()
        LL.LAST.clear()
        Life.sweep(PRc, invc, True)
        Rc = LL.reg(pkc)
        mts = [x for x in lls(csc, pkc) if str(x[6].getItemId()).startswith(MPRE)]
        hts = [x for x in lls(csc, pkc) if x[2] == 1 and not str(x[6].getItemId()).startswith(MPRE)]
        pks = [x for x in lls(csc, pkc) if str(x[6].getItemId()) == "Tool_Pickaxe_Crude"]
        got = "finished" if (str(Rc.getProperty("mt")) == "1" and len(mts) == 1 and not hts and not pks) else \
            ("dropped" if (Rc.getProperty("mt") is None and len(hts) == 1 and len(pks) == 1 and not mts) else "?")
        rows_c.append((step, pend is not None, got, Rc.getProperty("mt.pend")))
        kc(pend is not None and got == want and Rc.getProperty("mt.pend") is None,
           "C: a crash at step %d (journal on disk): the next look %s the merge (one tool, no journal): %s" % (step, want, rows_c[-1]))
    # critic L3: a crash at step 62 (the hatchet gone, the multitool not written) + a rebirth committed before the next look
    Ur = UUID.fromString("00000000-0000-0000-0000-0000000003b2")
    pkr = "pmtrb"
    L["PKEY"][str(Ur)] = pkr
    PRr = mkpr(Ur, "CrashRb")
    skills(u=Ur, Mining=10, Foraging=10, Farming=4, Fishing=4)
    invr, csr = mkinv()
    Life.sweep(PRr, invr, True)
    Life.CRASH_AT = JInt(62)
    try:
        Life.mtMerge(PRr, invr)
    except Exception:
        pass
    Life.CRASH_AT = JInt(0)
    rbp = JClass("java.util.Properties")()
    rbp.setProperty("rb.lastTx", "tx325")
    rbp.setProperty("rb.n", "1")
    rbp.setProperty("rb.at", str(int(JClass("java.lang.System").currentTimeMillis())))
    LL.REG.clear()
    LL.LAST.clear()
    LL.RBREC.put(pkr, rbp)
    Life.sweep(PRr, invr, True)
    LL.RBREC.remove(pkr)
    Rr = LL.reg(pkr)
    mtr = [x for x in lls(csr, pkr) if str(x[6].getItemId()).startswith(MPRE)]
    rest = [x for x in lls(csr, pkr) if x[2] in (0, 1) and not str(x[6].getItemId()).startswith(MPRE) and not bool(LL.isRt(doc(x[6])))]
    kc(str(Rr.getProperty("mt")) == "1" and len(mtr) == 1 and not rest and Rr.getProperty("mt.pend") is None and str(Rr.getProperty("rb.applied")) == "tx325"
       and str(Data.str(doc(mtr[0][6]), "rbx", "")) == "tx325",
       "C (critic L3): crash 62 + a committed rebirth: the next look applies the rebirth, finishes the multitool and stamps it for the rebirth: %s" % [(str(x[6].getItemId()), str(Data.str(doc(x[6]), "rbx", ""))) for x in lls(csr, pkr)])
    # critic M1: a hard stop AFTER the registry commit, BEFORE the inventory save - the inventory holds the plain pickaxe + hatchet again
    Uw = UUID.fromString("00000000-0000-0000-0000-0000000003b3")
    pkw = "pmtwin"
    L["PKEY"][str(Uw)] = pkw
    PRw = mkpr(Uw, "Window")
    skills(u=Uw, Mining=10, Foraging=10, Farming=4, Fishing=4)
    invw, csw = mkinv()
    Life.sweep(PRw, invw, True)
    tw0 = dict((x[2], x) for x in lls(csw, pkw))
    pw, hw = tw0[0], tw0[1]
    rw = str(Life.mtMerge(PRw, invw))
    csw[pw[0]].setItemStackForSlot(JShort(pw[1]), pw[6])          # the engine never saved: the old stacks are back
    csw[hw[0]].setItemStackForSlot(JShort(hw[1]), hw[6])
    LL.REG.clear()
    LL.LAST.clear()
    Life.sweep(PRw, invw, True)
    Rw = LL.reg(pkw)
    nw = lls(csw, pkw)
    slot_now = csw[pw[0]].getItemStack(JShort(pw[1]))
    kc(rw.startswith("+") and str(Rw.getProperty("mt")) == "1" and slot_now is not None and str(slot_now.getItemId()) == MPRE + "Crude" and str(LL.uid(doc(slot_now))) == pw[3]
       and not [x for x in nw if str(x[6].getItemId()) == "Tool_Pickaxe_Crude"] and [x for x in nw if x[3] == hw[3] and bool(LL.isRt(doc(x[6])))],
       "C (critic M1): the plain pickaxe with the committed multitool's uid becomes the multitool IN PLACE (never removed), the hatchet is retired: %s" % [(str(x[6].getItemId()), x[3] == pw[3]) for x in nw])
    Life.TEST_ANYITEM = False
    # critic L2: the normal-tools sweep waits on an open multitool journal
    Pn = JClass("java.util.Properties")()
    for k_, v_ in (("migrated", "1"), ("poleKit", "1"), ("canKit", "1")):
        Pn.setProperty(k_, v_)
    r0 = bool(P("GearNorm").ready(Pn))
    Pn.setProperty("mt.pend", "abc")
    kc(r0 and not bool(P("GearNorm").ready(Pn)), "C (critic L2): GearNorm.ready waits on mt.pend")
    # ============================================================== D: accBp cache
    Map = JClass("java.util.HashMap")
    Ua = UUID.fromString("00000000-0000-0000-0000-0000000003aa")
    src = Map()
    src.put("bp.mining", JClass("java.lang.Double")(0.25))
    top = Map()
    top.put("acc", src)
    br.put("skill:bonus:" + str(Ua), top)
    n0 = int(Tool.BPN[1])
    v1 = float(Tool.accBp(Ua, JString("mining")))
    src.put("bp.mining", JClass("java.lang.Double")(0.5))
    v2 = float(Tool.accBp(Ua, JString("mining")))
    hit = int(Tool.BPN[1]) - n0
    apply()
    v3 = float(Tool.accBp(Ua, JString("mining")))
    br.remove("skill:bonus:" + str(Ua))
    kc(abs(v1 - 1.25) < 1e-9 and (v2 == v1 and hit >= 1 or v2 == 1.5) and abs(v3 - 1.5) < 1e-9 and abs(float(Tool.accBp0(Ua, JString("mining"))) - 1.0) < 1e-9,
       "D: accBp cached inside 50 ms (%s, hits %d), a config apply re-reads (%s); accBp0 = the uncached math" % ((v1, v2), hit, v3))
    # ============================================================== E: Charged trust
    tr = set(str(x) for x in Chg.TRUST)
    fb = set(str(x) for x in Chg.FALLBACK)
    kc(set(A2) <= tr and set(i for i in A2 if not i.startswith("Weapon_Club_")) <= fb and not [i for i in A2 if i.startswith("Weapon_Club_") and i in fb],
       "E: GearChg.TRUST holds the 72 A2 weapons, FALLBACK the 64 non-club ones (clubs stay out): missing %s" % sorted(set(A2) - tr)[:4])


# ---- older checks this round changes ON PURPOSE (prefix, why)
_WHY_KIND = ("0.3.25 by design (Skyy 2026-10-11 'merge pickaxe + axe' + 2026-10-16 two stat sets): a multitool is the PICKAXE kind's tool (kOf 0) - "
             "the lifelong merge makes it the profile's pickaxe-kind tool; H325 A / B check the new kind rules")
WAIVE_325 = [("H323 B: kinds / families / multitool ids of the new tools", _WHY_KIND)]
if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h325(L, K):
        _h319_prev(L, K)
        try:
            _h325(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H325: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h325
    H320["run_assets320"] = run_assets325          # the jar compare of THIS round (0.3.24 -> 0.3.25)
    H320["J319"] = J324
    H316["WAIVE_316"].extend(WAIVE_325)


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
            shutil.copyfile(GEN324, os.path.join(r, "SkyyGear", os.path.basename(GEN324)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.25.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.25.py (the committed file is the patch's output)")
        src = open(GEN324, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.25.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.25"\n' in s and "GENERATED by tools/gear_0_3_25_patch.py" in s, "A: VERSION 0.3.25 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean mtm(java.util.Properties P)") < i("public static int levelK(") < i("public static int lineCap(java.util.Properties P, int k) {")
              < i("public static String collWhy(java.util.UUID u, String to) {") < i("public static double[] mstats(") < i("public static double accBp(java.util.UUID u, String sk) {")
              < i("public static boolean mtRecover(") < i("public static void sweep0(") < i("public void llMtRow("), "A: helpers before their callers (javassist order)")
        check('"multi.ladders", "multi.lifelongFull"}' in s and s.count('("multi.ladders", ') == 1 and s.count('("multi.lifelongFull", ') == 1,
              "A: the two rows (danger list)")
        check(".toString(); }\")          # 0.3.25: < 64 KB per constant" in s, "A: defaultsText built from parts (the 64 KB constant limit)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    assert os.path.isfile(J324), J324
    H320["main"]()


if __name__ == "__main__":
    main()
