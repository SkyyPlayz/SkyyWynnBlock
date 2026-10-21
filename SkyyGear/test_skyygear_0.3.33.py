"""Harness for SkyyGear 0.3.33 (tools/gear_0_3_33_patch.py header = Skill Trees 3 R3c: Weapon Tempering + the Masterwork Pick capstone,
tools/trees_v3_effects.py)
    python tools/gear_0_3_33_patch.py && python SkyyGear/build_skyygear_0.3.33.py
    python SkyyGear/test_skyygear_0.3.33.py [--keep]

  The 0.3.32 harness is loaded as a library (it loads 0.3.31's, 0.3.30's ... the engine boot + H329 .. H332, which still hold on this jar:
  0.3.33 changes no R3b row, band, ore, bag, bucket or migration behaviour); H333 runs right after them on the same booted engine.
  S333 the jar 0.3.32 -> 0.3.33: nothing added or removed; only class files + the manifest change; the changed classes = GearV3, GearTool,
       GearStats, GearCfg (+ the kit's tables and version texts)
  A    every class loads + initialises with -Xverify:all (harness_kit, own child)
  AA   engine-access audit (harness_kit, own child)
  H333 (the h319 child) - REAL code on the booted engine, a fake SkyyTrees tree:fn:level answering the ranks:
       T  GearV3 = the 13 trees_v3_effects rows of SkyyGear; tree:reads:SkyyGear lists Weapon Tempering + Masterwork Pick; GearCfg.V3P / V3X
          10-12 = the table
       W  Weapon Tempering through GearStats.totals0 AND totals (the snapshot path) with withExtra: rank 0 = exactly 0.3.32's totals; rank 4 =
          +1 Damage a tier above Iron for every real gear weapon found (Iron 0 .. Onyxium 5); withExtra false / a tool / bare hands / a block =
          nothing; a lowered ceiling / a raised per-rank number; wsteps of the tier words (zone words only in _SkyWynn ids)
       P  Masterwork Pick: GearTool.held keeps the scale (an Iron pickaxe 1, YOUR OWN lifelong pickaxe 2, another profile's / a retired one 1,
          a hatchet / hoe / bare hands 0); GearTool.onDamage on the real ore / rock BlockTypes = x1.25 / x1.5 (inside the Power guards), oak and
          the hatchet unchanged; the held pickaxe's posted Fortune +7.5 / +15 (dd.mining 0.075 / 0.15 in the "gear" source); the multitool post
          (mpost's new argument) adds it to dd.mining; mdamage (a multitool hit) x the factor; a ceiling; rank 0 again = 0.3.32's numbers;
          forget clears the scale
Scratch: tools/dev/scratch/st3r3cfix/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, shutil, zipfile, json, subprocess, atexit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HKIT
import trees_v3_effects as V3E


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.33"
V332 = "0.3.32"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "st3r3cfix", "gear")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J332 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V332))                       # read only
PKG = "com.skyy.gear."

if "--hkverify" not in sys.argv and "--hkaudit" not in sys.argv and "--hkfake" not in sys.argv:
    _H332 = os.path.join(HERE, "test_skyygear_0.3.32.py")
    _T332 = open(_H332, encoding="utf-8").read()
    _T332 = _T332[:_T332.rindex('if __name__ == "__main__":')]
    # 0.3.32's H332 pinned "the 10 keys" only in a message; its own scratch folder is ours here
    _argv = sys.argv
    sys.argv = [_H332, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H332 = {"__name__": "skyygear_h332", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T332, _H332 + " (library, 0.3.33)", "exec"), H332)
    sys.argv = _argv
    # every chained library's scratch path (st3r3b / iwb / g330 / g329 ... - other rounds' folders) is moved under OURS: module-level path
    # strings under tools/dev/scratch/<x> -> tools/dev/scratch/st3r3cfix/gear/lib/<x> (the functions read them as globals)
    _SCR = os.path.join(TOOLS, "dev", "scratch")
    _MOVED = []

    def _remap(d, seen):
        if id(d) in seen:
            return
        seen.add(id(d))
        for _k in list(d.keys()):
            _v = d[_k]
            if isinstance(_v, dict) and "__name__" in _v and "__builtins__" in _v:
                _remap(_v, seen)
            elif isinstance(_v, str) and os.path.isabs(_v) and os.path.normcase(os.path.abspath(_v)).startswith(os.path.normcase(_SCR) + os.sep)                     and not _v.endswith(".jar") and not os.path.isfile(_v):          # a read-only source (the archived SkyyFishing jar) stays
                _rel = os.path.relpath(os.path.abspath(_v), _SCR)
                if _rel.split(os.sep)[0] != "st3r3cfix":
                    d[_k] = os.path.join(SCR_BASE, "lib", _rel)
                    _MOVED.append((d.get("__name__"), _k))
    _remap(H332, set())
    H331 = H332["H331"]
    H330, H319, H320, H316 = H331["H330"], H331["H319"], H331["H320"], H331["H316"]
    H329 = H330["H329"]
    H328 = H329["H328"]
    for _h in (H332, H331, H330, H329, H328, H328["H327"], H328["H326"], H328["H325"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
    check = H316["check"]


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S333 (the parent, no engine)
WANT_CHANGED = {"GearV3", "GearTool", "GearStats", "GearCfg"}
KIT_CHANGED = {"CfgRows", "CfgRows1", "CfgRows2", "CfgFile", "CfgDefaults"}          # the kit's tables (6 new rows, the trees.properties default)
VERSION_TEXT = {"CfgFn", "CfgKit", "CfgPub", "SkyyGearPlugin"}


def run_assets333():
    ea, eb = entries(J332), entries(JAR)
    add, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    check(not add and not gone, "S333: nothing added or removed: + %s - %s" % (add, gone))
    diff = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    other = [n for n in diff if not n.endswith(".class") and n != "manifest.json"]
    check(not other, "S333: only class files + the manifest change: other %s" % other[:6])
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in diff if n.endswith(".class"))
    print("  class compare 0.3.32 -> 0.3.33: %d changed (%s)" % (len(chg), ", ".join(chg)))
    check(WANT_CHANGED <= set(chg) and set(chg) <= WANT_CHANGED | VERSION_TEXT | KIT_CHANGED,
          "S333: the changed classes = GearV3 / GearTool / GearStats / GearCfg (+ kit tables / version texts only): unexpected %s, missing %s"
          % (sorted(set(chg) - WANT_CHANGED - VERSION_TEXT - KIT_CHANGED), sorted(WANT_CHANGED - set(chg))))
    for c in sorted(set(chg) & {"CfgFn", "CfgKit", "CfgPub"}):
        a_, b_ = ea["com/skyy/gear/%s.class" % c], eb["com/skyy/gear/%s.class" % c]
        check(len(a_) == len(b_) and b"0.3.32" in a_ and b_.replace(b"0.3.33", b"0.3.32") == a_, "S333: %s differs only by the version text" % c)
    g3 = eb["com/skyy/gear/GearV3.class"]
    check(b"Skill.Combat.b1.r5b" in g3 and b"Skill.Mining.b2.r6" in g3 and b"weaponInto" in g3 and b"pickBp" in g3,
          "S333: GearV3 knows the R3c keys + weaponInto / pickBp")
    print("  row holder sizes: %s" % [(n, len(eb[n])) for n in sorted(eb) if "/CfgRows" in n])


# ====================================================================================================== H333 (the h319 child, real code)
def _h333(L, K):
    from jpype import JClass, JString, JInt, JFloat, JShort, JDouble, JObject, JArray, JImplements, JOverride
    P = lambda n: JClass(PKG + n)
    br, apply, stack, skills, U1 = L["br"], L["apply"], L["stack"], L["skills"], L["U1"]
    Roll, Data, SIC = L["Roll"], L["Data"], L["SIC"]
    V3, Tool, Stats, LLc, Cfg, Defs, GearC = P("GearV3"), P("GearTool"), P("GearStats"), P("GearLL"), P("GearCfg"), P("GearDefs"), P("Gear")
    BS, BI = JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")

    def kc(cond, what):
        K.check(bool(cond), "H333 " + what)
    apply()
    rows = V3E.rows("SkyyGear")
    # ============================================================== T: the table
    kc(len(rows) == 13 and [str(x) for x in V3.KEY] == [V3E.key(e[0], e[1], e[2]) for e in rows] and [str(x) for x in V3.SCALE] == [e[6] or "" for e in rows]
       and [int(x) for x in V3.CAP] == [int(e[7]) for e in rows] and [int(x) for x in V3.MAX] == [V3E.maxrank(e[0], e[1], e[2]) for e in rows],
       "T: GearV3 = the 13 rows of SkyyGear (scales %s)" % [str(x) for x in V3.SCALE][10:])
    kc(str(V3.READS) == V3E.reads_csv("SkyyGear") and "Skill.Combat.b1.r5b" in str(V3.READS) and "Skill.Mining.b2.r6" in str(V3.READS),
       "T: tree:reads:SkyyGear lists Weapon Tempering + Masterwork Pick (12 keys)")
    iW = [i for i, e in enumerate(rows) if e[6] == "weapon"][0]
    iPB = [i for i, e in enumerate(rows) if e[6] == "pick" and e[4] == "bp.mining"][0]
    iPF = [i for i, e in enumerate(rows) if e[6] == "pick" and e[4] == "dd.mining"][0]
    kc((iW, iPB, iPF) == (10, 11, 12) and [round(float(getattr(Cfg, "V3P%d" % i)), 6) for i in (iW, iPB, iPF)] == [1.0, 25.0, 7.5]
       and [round(float(getattr(Cfg, "V3X%d" % i)), 6) for i in (iW, iPB, iPF)] == [20.0, 50.0, 15.0],
       "T: GearCfg.V3P / V3X 10-12 = 1 / 25 / 7.5 a rank, at most 20 / 50 / 15")
    RANK = {}

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            v = RANK.get(str(a[1]), 0)
            if v == "boom":
                raise RuntimeError("boom")
            return JString(v) if isinstance(v, str) else JObject(JInt(v), JClass("java.lang.Integer"))
    br.put("tree:fn:level", Tr())

    def setr(**kv):
        RANK.clear()
        for k_, v_ in kv.items():
            t_, b_, i_ = k_.split("_")
            RANK[V3E.key(t_, int(b_[1:]), i_)] = v_
        V3.RK.clear()
        V3.CMB.clear()
    # ============================================================== W: Weapon Tempering
    ws = dict((w, int(V3.wsteps(JString(w)))) for w in ("Weapon_Sword_Iron", "Weapon_Sword_Steel", "Weapon_Sword_Thorium", "Weapon_Sword_Bronze",
                                                        "Weapon_Sword_Cobalt", "Weapon_Sword_Adamantite", "Weapon_Sword_Mithril", "Weapon_Sword_Onyxium",
                                                        "Weapon_Sword_Crude", "Weapon_Sword_Copper", "Weapon_Sword_Lead", "Weapon_Sword_Lead_SkyWynn",
                                                        "Weapon_Sword_Lumen_SkyWynn", "Weapon_Sword"))
    kc(ws == {"Weapon_Sword_Iron": 0, "Weapon_Sword_Steel": 0, "Weapon_Sword_Thorium": 1, "Weapon_Sword_Bronze": 1, "Weapon_Sword_Cobalt": 2,
              "Weapon_Sword_Adamantite": 3, "Weapon_Sword_Mithril": 4, "Weapon_Sword_Onyxium": 5, "Weapon_Sword_Crude": 0, "Weapon_Sword_Copper": 0,
              "Weapon_Sword_Lead": 0, "Weapon_Sword_Lead_SkyWynn": 2, "Weapon_Sword_Lumen_SkyWynn": 5, "Weapon_Sword": 0},
       "W: wsteps = the metal's tier - Iron (zone words only in _SkyWynn ids): %s" % ws)
    DataC = P("GearData")
    cands = []
    for t_ in ("Sword", "Longsword", "Battleaxe", "Mace", "Spear", "Daggers", "Shortbow", "Staff", "Axe", "Crossbow"):
        for m_ in ("Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
            w_ = "Weapon_%s_%s" % (t_, m_)
            try:
                if int(DataC.slotOf(JString(w_))) in (0, 1):
                    cands.append(w_)
            except Exception:
                pass
    kc(len(cands) >= 3, "W setup: real gear weapons found: %s" % cands)
    di = int(Defs.sIndex(JString("dmg")))
    br.remove("pets:stats:" + str(U1))
    br.remove("gear:extra:" + str(U1))
    V3.PCS.remove(U1)
    arm = SIC(JShort(4))
    Snap = P("GearSnap")
    snap_on = Snap.entry(U1, arm) is not None
    K.notes.append("H333 W: GearSnap.entry with an empty armor container = %s (totals' snapshot path %s)" % (snap_on, "ran" if snap_on else "fell back to totals0"))

    def dmgs(w, extra=True):
        a_ = int(Stats.totals0(U1, stack(w) if w else None, None, None, extra)[di])
        b_ = int(Stats.totals(U1, stack(w) if w else None, arm, None, extra)[di])
        return a_, b_
    setr()
    base = dict((w, dmgs(w)) for w in cands + ["Tool_Pickaxe_Onyxium", "Rock_Stone", None])
    base_nx = dict((w, dmgs(w, False)) for w in cands)
    setr(Combat_b1_r5b=4)
    got = dict((w, dmgs(w)) for w in base)
    bad = [(w, base[w], got[w], ws.get("Weapon_Sword_" + w.split("_")[-1])) for w in cands
           if got[w][0] - base[w][0] != 4 * int(V3.wsteps(JString(w))) or got[w][1] - base[w][1] != 4 * int(V3.wsteps(JString(w)))]
    kc(not bad, "W: rank 4 = +4 Damage a tier above Iron on totals0 AND totals, every weapon (Iron +0 .. Onyxium +20): %s"
       % dict((w, got[w][0] - base[w][0]) for w in cands) if not bad else "W: wrong: %s" % bad)
    K.notes.append("H333 W: rank 4 Damage added (totals0, totals) per weapon: %s" % dict((w, (got[w][0] - base[w][0], got[w][1] - base[w][1])) for w in cands))
    kc(all(got[w] == base[w] for w in ("Tool_Pickaxe_Onyxium", "Rock_Stone", None)), "W: a tool / a block / bare hands get nothing: %s" % [(w, base[w], got[w]) for w in ("Tool_Pickaxe_Onyxium", "Rock_Stone", None)])
    kc(all(dmgs(w, False) == base_nx[w] for w in cands), "W: withExtra false (the cached weapon + armor part) = unchanged")
    top = [w for w in cands if int(V3.wsteps(JString(w))) == 5]
    if top:
        w5 = top[0]
        setr(Combat_b1_r5b=2)
        kc(dmgs(w5)[0] - base[w5][0] == 10, "W: rank 2 x Onyxium (5) = +10")
        setr(Combat_b1_r5b=99)
        kc(dmgs(w5)[0] - base[w5][0] == 20, "W: a rank of 99 is clamped to the max 4 = +20 = the ceiling (every rank adds)")
        setattr(Cfg, "V3X%d" % iW, 12.0)
        kc(dmgs(w5)[0] - base[w5][0] == 12, "W: a Server Setup ceiling of 12 cuts it to +12")
        setattr(Cfg, "V3X%d" % iW, 20.0)
        setattr(Cfg, "V3P%d" % iW, 2.0)
        kc(dmgs(w5)[0] - base[w5][0] == 20, "W: the tree text's 2 a rank (40) stops at the ceiling 20")
        setattr(Cfg, "V3P%d" % iW, 1.0)
        RANK[V3E.key("Combat", 1, "r5b")] = "boom"
        V3.RK.clear()
        kc(dmgs(w5) == base[w5], "W: a throwing SkyyTrees = nothing")
    else:
        K.notes.append("H333 W: no Onyxium-tier gear weapon in this engine - the ceiling checks ran on wsteps only")
    t_ = JArray(JInt)([0] * int(Defs.NS))
    kc(int(V3.weaponInto(U1, None, t_)) == 0 and int(V3.weaponInto(None, stack(cands[0]), t_)) == 0, "W: weaponInto(null weapon / null player) = 0")
    setr()
    kc(all(dmgs(w) == base[w] for w in base), "W: rank 0 again = exactly 0.3.32's totals")
    # ============================================================== P: Masterwork Pick
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    BL = dict((n, bmap.get(n)) for n in ("Ore_Iron_Stone", "Wood_Oak_Trunk", "Rock_Stone"))
    kc(all(v is not None for v in BL.values()), "P setup: the real BlockTypes")
    skills(Mining=30, Foraging=30, Farming=30)
    br.remove("skill:bonus:" + str(U1))
    pk = str(GearC.pkey(U1))

    def llpick(owner, retired=False, sid="Tool_Pickaxe_Iron"):
        d_ = Data.base(JString("tool"), JInt(1), True, JString("craft"))
        d_.put("ll", BI(JInt(1)))
        d_.put("lu", BS("r3c-test"))
        d_.put("lo", BS(owner))
        if retired:
            d_.put("lrt", BI(JInt(1)))
        return Data.put(stack(sid), d_, None)
    STK = {"iron": lambda: stack("Tool_Pickaxe_Iron"), "mine": lambda: llpick(pk), "other": lambda: llpick("someone-else"),
           "retired": lambda: llpick(pk, True), "hatchet": lambda: stack("Tool_Hatchet_Iron"), "hoe": lambda: stack("Tool_Hoe_Iron")}

    def scale(k_):
        Tool.LAST.clear()
        Tool.held(U1, STK[k_]())
        return int(V3.pickOf(U1))
    sc = dict((k_, scale(k_)) for k_ in STK)
    Tool.LAST.clear()
    Tool.held(U1, None)
    sc["hands"] = int(V3.pickOf(U1))
    kc(bool(Cfg.LL_ON) and sc == {"iron": 1, "mine": 2, "other": 1, "retired": 1, "hatchet": 0, "hoe": 0, "hands": 0},
       "P: the pick scale on held(): an Iron pickaxe 1, your own lifelong one 2, another profile's / a retired one 1, hatchet / hoe / hands 0: %s" % sc)

    def dmg(k_, bn):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, STK[k_](), BL[bn], JFloat(0.3)))

    def gear_src():
        m_ = br.get("skill:bonus:" + str(U1))
        v_ = None if m_ is None else m_.get("gear")
        return {} if v_ is None else dict((str(k_), v_.get(k_)) for k_ in v_.keySet())

    def fort(k_):
        Tool.LAST.clear()
        Tool.held(U1, STK[k_]())
        return float(gear_src().get("dd.mining", 0.0) or 0.0)
    keys_ = [(k_, b_) for k_ in ("iron", "mine", "hatchet") for b_ in ("Ore_Iron_Stone", "Rock_Stone", "Wood_Oak_Trunk")]
    setr()
    d0 = dict((kb, dmg(*kb)) for kb in keys_)
    f0 = dict((k_, fort(k_)) for k_ in ("iron", "mine", "hatchet"))
    setr(Mining_b2_r6=1)
    d1 = dict((kb, dmg(*kb)) for kb in keys_)
    f1 = dict((k_, fort(k_)) for k_ in ("iron", "mine", "hatchet"))
    pmax = float(Cfg.pmax())
    K.notes.append("H333 P: rank 0 hits %s; rank 1 %s; pmax %.2f" % (dict((("%s/%s" % kb), round(v, 4)) for kb, v in d0.items()),
                                                                  dict((("%s/%s" % kb), round(v, 4)) for kb, v in d1.items()), pmax))

    def near(a, b):
        return abs(a - b) < 1e-4

    def want(k_, f_):
        return min(d0[(k_, "Ore_Iron_Stone")] * f_, 0.3 * pmax)
    kc(near(d1[("iron", "Ore_Iron_Stone")], d0[("iron", "Ore_Iron_Stone")] * 1.25) and near(d1[("iron", "Rock_Stone")], d0[("iron", "Rock_Stone")] * 1.25),
       "P: Masterwork Pick, an Iron pickaxe on ore / rock = x1.25 (%.4f -> %.4f)" % (d0[("iron", "Ore_Iron_Stone")], d1[("iron", "Ore_Iron_Stone")]))
    kc(near(d1[("mine", "Ore_Iron_Stone")], min(d0[("mine", "Ore_Iron_Stone")] * 1.5, 0.3 * pmax)) and near(d1[("mine", "Rock_Stone")], min(d0[("mine", "Rock_Stone")] * 1.5, 0.3 * pmax)),
       "P: ... your own lifelong pickaxe = x1.5 (%.4f -> %.4f, inside the Power guard x%.1f)" % (d0[("mine", "Ore_Iron_Stone")], d1[("mine", "Ore_Iron_Stone")], pmax))
    kc(all(near(d1[kb], d0[kb]) for kb in keys_ if kb[0] == "hatchet" or kb[1] == "Wood_Oak_Trunk"), "P: the hatchet and oak unchanged")
    kc(abs(f1["iron"] - f0["iron"] - 0.075) < 1e-6 and abs(f1["mine"] - f0["mine"] - 0.15) < 1e-6 and abs(f1["hatchet"] - f0["hatchet"]) < 1e-9,
       "P: posted Mining Fortune +7.5 (Iron pickaxe) / +15 (your lifelong one), the hatchet nothing: %s -> %s" % (f0, f1))
    Tool.LAST.clear()
    Tool.held(U1, STK["iron"]())
    kc("only.mining" in gear_src(), "P: the pick's Fortune keeps the pickaxe's own block filter (only.mining): %s" % gear_src())
    # the multitool: mpost's new argument + mdamage
    st = JArray(JDouble)([6.0, 0.0, 30.0, 1.0, 1.0, 2.0, 1.0, 2.0, 0.0, 1.0, 0.0, 0.0])
    Tool.mpost(U1, st, 0.0)
    m0 = float(gear_src().get("dd.mining", 0.0) or 0.0)
    Tool.mpost(U1, st, 15.0)
    m1 = float(gear_src().get("dd.mining", 0.0) or 0.0)
    Tool.mpost(U1, st, float("nan"))
    m2 = float(gear_src().get("dd.mining", 0.0) or 0.0)
    kc(abs(m1 - m0 - 0.15) < 1e-9 and abs(m2 - m0) < 1e-9, "P: mpost(xf) adds the pick's Fortune to dd.mining (%.4f -> %.4f), a NaN adds nothing" % (m0, m1))
    V3.PICK.put(U1, JArray(JClass("java.lang.Object"))([JObject(JInt(2), JClass("java.lang.Integer")), JString(pk)]))
    md1 = float(Tool.mdamage(U1, st, BL["Ore_Iron_Stone"], JFloat(0.3)))
    md1w = float(Tool.mdamage(U1, st, BL["Wood_Oak_Trunk"], JFloat(0.3)))
    setr()
    md0 = float(Tool.mdamage(U1, st, BL["Ore_Iron_Stone"], JFloat(0.3)))
    md0w = float(Tool.mdamage(U1, st, BL["Wood_Oak_Trunk"], JFloat(0.3)))
    kc(near(md1, min(md0 * 1.5, 0.3 * pmax)) and near(md1w, md0w), "P: a multitool hit (mdamage) on ore x1.5 (%.4f -> %.4f), on oak unchanged" % (md0, md1))
    mid = "Tool_Hatchet_Pickaxe_Multitool_Iron"
    try:
        Tool.LAST.clear()
        smt = Tool.held(U1, stack(mid))
        K.notes.append("H333 P: held(%s) -> fam %s, pick scale %d (the multitool item %s in this engine)" % (
            mid, None if smt is None else float(smt[0]), int(V3.pickOf(U1)), "exists" if smt is not None else "is missing"))
    except Exception as ex:
        K.notes.append("H333 P: held(%s) not executable here: %s" % (mid, ex))
    # the ceiling
    setr(Mining_b2_r6=1)
    setattr(Cfg, "V3X%d" % iPF, 10.0)
    kc(abs(fort("mine") - f0["mine"] - 0.10) < 1e-6 and abs(fort("iron") - f0["iron"] - 0.075) < 1e-6, "P: a Fortune ceiling of 10 cuts the lifelong pick to +10, the Iron pick stays +7.5")
    setattr(Cfg, "V3X%d" % iPF, 15.0)
    setattr(Cfg, "V3P%d" % iPB, 0.0)
    kc(near(dmg("mine", "Ore_Iron_Stone"), d0[("mine", "Ore_Iron_Stone")]), "P: per rank 0 = no Breaking Power")
    setattr(Cfg, "V3P%d" % iPB, 25.0)
    setr()
    kc(all(near(dmg(*kb), d0[kb]) for kb in keys_) and all(abs(fort(k_) - f0[k_]) < 1e-9 for k_ in f0), "P: rank 0 again = exactly 0.3.32's hits and Fortune")
    # fixer (critic LOW 2): the scale belongs to the profile it was worked out on - a profile switch inside held()'s 1 s cache gives nothing
    setr(Mining_b2_r6=1)
    Tool.LAST.clear()
    Tool.held(U1, STK["mine"]())
    sA = int(V3.pickOf(U1))
    bpA = float(V3.pickBp(U1))

    @JImplements("java.util.function.Function")
    class PkB(object):
        @JOverride
        def apply(self, a):
            return JString("profile-B")
    br.put("profile:fn:key", PkB())
    sB, bpB, fB = int(V3.pickOf(U1)), float(V3.pickBp(U1)), float(V3.pickFort(U1))
    br.remove("profile:fn:key")
    sA2 = int(V3.pickOf(U1))
    kc(sA == 2 and abs(bpA - 1.5) < 1e-9 and sB == 0 and abs(bpB - 1.0) < 1e-9 and fB == 0.0 and sA2 == 2,
       "P: profile switch: your lifelong pick x2 on profile A (%d, x%.2f); the same cached scale read on profile B = none (%d, x%.2f, Fortune %.2f); back on A = %d"
       % (sA, bpA, sB, bpB, fB, sA2))
    setr()
    V3.forget(U1)
    kc(V3.PICK.get(U1) is None, "P: forget clears the pick scale")
    # ============================================================== LIVE: GearCfg.load twice on a scratch COPY of the live Skyy_SkyyGear config
    Paths = JClass("java.nio.file.Paths")
    try:
        import deploy_set
        wld = deploy_set.WORLD
    except Exception:
        wld = "NewBetaTest"
    lsrc = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", wld, "mods", "Skyy_SkyyGear")
    ldst = os.path.join(SCR_BASE, "livecopy", "Skyy_SkyyGear")
    os.makedirs(ldst, exist_ok=True)
    if os.path.isfile(os.path.join(lsrc, "config.properties")):
        for fn in ("config.properties", "trees.properties"):
            if os.path.isfile(os.path.join(lsrc, fn)):
                shutil.copyfile(os.path.join(lsrc, fn), os.path.join(ldst, fn))          # read-only source, a copy
        had_trees = os.path.isfile(os.path.join(ldst, "trees.properties"))
        cfg0 = open(os.path.join(ldst, "config.properties"), "rb").read()
        f_old = Cfg.FILE
        Cfg.FILE = Paths.get(os.path.join(ldst, "config.properties"))
        Cfg.load()
        t1 = open(os.path.join(ldst, "trees.properties"), "rb").read()
        Cfg.load()
        t2 = open(os.path.join(ldst, "trees.properties"), "rb").read()
        cfg2 = open(os.path.join(ldst, "config.properties"), "rb").read()
        kc(cfg2 == cfg0 and t1 == t2 and (had_trees or t1.decode("latin-1") == V3E.cfg_text("SkyyGear"))
           and [round(float(getattr(Cfg, "V3P%d" % i)), 6) for i in (iW, iPB, iPF)] == [1.0, 25.0, 7.5],
           "LIVE: two GearCfg.load starts on a copy of the live config (trees.properties %s): config.properties unchanged, trees.properties "
           "written once (13 rows) and not rewritten, the R3c numbers = the table" % ("present" if had_trees else "missing -> seeded"))
        # an OLD (0.3.32-seeded) trees.properties: no R3c lines + a hand edit -> read, not rewritten; the R3c rows take the built-in numbers
        old = "".join(l for l in V3E.cfg_text("SkyyGear").splitlines(True) if "r5b.dmg" not in l and "b2.r6." not in l
                      and "Weapon Tempering" not in l and "Masterwork" not in l).replace("tree.Combat.b1.r1a.dmg.per=2", "tree.Combat.b1.r1a.dmg.per=3")
        open(os.path.join(ldst, "trees.properties"), "w", encoding="latin-1", newline="").write(old)
        setattr(Cfg, "V3P%d" % iW, 9.0)
        Cfg.load()
        Cfg.load()
        kc(open(os.path.join(ldst, "trees.properties"), encoding="latin-1", newline="").read() == old and abs(float(getattr(Cfg, "V3P%d" % [i for i, e in enumerate(rows) if (e[0], e[2]) == ("Combat", "r1a")][0])) - 3.0) < 1e-9
           and abs(float(getattr(Cfg, "V3P%d" % iW)) - 1.0) < 1e-9 and abs(float(getattr(Cfg, "V3X%d" % iPF)) - 15.0) < 1e-9,
           "LIVE: an old 0.3.32 trees.properties (no R3c lines, Hone Edge hand-edited to 3) is read twice, never rewritten; the R3c rows use the built-in numbers")
        Cfg.FILE = f_old
        Cfg.load()
    else:
        K.notes.append("H333 LIVE: no live Skyy_SkyyGear/config.properties at %s - skipped" % lsrc)
    br.remove("tree:fn:level")
    br.remove("skill:bonus:" + str(U1))
    print("  note (h333): T W P ran")


if "--hkverify" not in sys.argv and "--hkaudit" not in sys.argv and "--hkfake" not in sys.argv:
    _H332_PHASE = H319["_h319"]          # the 0.3.32 lib's wrapper (H329 .. H332)

    def _h319_h333(L, K):
        _H332_PHASE(L, K)
        try:
            _h333(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H333: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_h333


def run_hk():
    """A (-Xverify:all) + AA (engine-access audit) through tools/harness_kit.py in their own child JVMs"""
    sc = os.path.join(SCR_BASE, "hk")
    os.makedirs(os.path.join(sc, "fake"), exist_ok=True)
    os.makedirs(os.path.join(sc, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(sc, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    for flag in ("--hkfake", "--hkverify", "--hkaudit"):
        out = os.path.join(sc, flag[2:] + ".json")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), flag, "--out", out, "--dir", sc, "--jar", JAR], env=env)
        check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (flag, p.returncode))
        if flag == "--hkverify" and os.path.isfile(out):
            d = json.load(open(out))
            check(not d["fails"], "A: -Xverify:all: %s" % d["fails"][:3])
            print("  A: %s" % "; ".join(d.get("notes", [])))
        if flag == "--hkaudit" and os.path.isfile(out):
            a = json.load(open(out))
            check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("  AA: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))


def main():
    if "--hkfake" in sys.argv:
        HKIT.run_mkfake(os.path.join(arg("--dir"), "fake"), JAR)
        return
    if "--hkverify" in sys.argv:
        HKIT.run_verify(arg("--out"), JAR)
        return
    if "--hkaudit" in sys.argv:
        HKIT.run_audit(arg("--out"), JAR, os.path.join(arg("--dir"), "fake"))
        return
    if "--h319" in sys.argv:
        H319["run_h319"](arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--keep", "--dir", "--jar", "--root", "--out", "--only") for a in sys.argv[1:]):
        H320["main"]()          # an older child flag (--mkfake ...) - the chain dispatches it; never the full run again
        return
    assert os.path.isfile(J332) and os.path.isfile(JAR), (J332, JAR)
    if "--keep" not in sys.argv:
        atexit.register(lambda: shutil.rmtree(SCR_BASE, ignore_errors=True))
    run_assets333()
    run_hk()
    H331["_live_copy"]()
    H320["run_fallback"](lambda x: x == "h319", [])


if __name__ == "__main__":
    main()
