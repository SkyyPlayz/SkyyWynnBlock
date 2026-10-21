"""Harness for SkyyGear 0.3.32 (tools/gear_0_3_32_patch.py header = Skill Trees 3 R3b: the tool / armor / combat rows of the skill trees,
tools/trees_v3_effects.py)
    python tools/gear_0_3_32_patch.py && python SkyyGear/build_skyygear_0.3.32.py
    python SkyyGear/test_skyygear_0.3.32.py [--keep]

  The 0.3.31 harness is loaded as a library (it loads 0.3.30's, 0.3.29's ... the engine boot + H329 + H330 + H331, which still hold on this jar:
  0.3.32 changes no band, ore, bag, bucket or migration behaviour); H332 runs right after them on the same booted engine.
  S332 the jar 0.3.31 -> 0.3.32: added = GearV3.class only; nothing removed; only class files + the manifest change; the changed classes =
       GearTool, GearStats, GearGArm, SkyyGearPlugin + the version texts (CfgFn / CfgRows / CfgFile / CfgDefaults / GearCfg / ...)
  A    every class loads + initialises with -Xverify:all (harness_kit, own child)
  AA   engine-access audit (harness_kit, own child)
  H332 (the h319 child) - REAL code on the booted engine, a fake SkyyTrees tree:fn:level answering the ranks:
       T  GearV3 = the trees_v3_effects rows of SkyyGear (keys, effects, numbers, caps, max ranks); tree:reads:SkyyGear published / only ours
          removed; a rank above max is clamped, a bad / throwing answer = 0, the 1 s cache (a change shows after the TTL)
       B  GearTool.onDamage on the real BlockTypes: rank 0 = exactly 0.3.31's damage; Tool Mastery rank 2 with an Iron pickaxe (tier 2) on ore
          and rock = x1.08; Tool Tier Bonus rank 3 with an Iron hatchet on oak = x1.12; never across (pickaxe on oak, hatchet with the
          mining row); a Crude pickaxe (tier 0) = nothing; a non-tool = nothing
       C  GearTool.held on an Iron hoe: Scythe Tempering rank 2 = +2.8 Farming Fortune in the "gear" source (dd.farming + 0.028; fixer 2: 0.7)
       D  GearGArm.note on real worn armor (Roll.newDoc pieces): GearV3.PCS counts mining / foraging / combat pieces; Mining Gear Resonance
          rank 2 x 4 metal pieces = bp.mining + 0.08 in "garmor"; Foraging Gear Resonance rank 1 x 4 bark pieces = dd.foraging + 0.03 on top
          of the set's own; the cap (4)
       E  GearStats.extra: Hone Edge 3 / Weak Spot 2 / Crit Mastery 1 = dmg +6, cc +4, cd +3 on top of gear:extra + pets:stats; Combat Gear
          Resonance x the combat pieces; rank 0 = exactly 0.3.31's totals; no SkyyTrees = nothing
       F  (fixer) the ceilings (Foraging Gear Resonance rank 5 x 4 pieces = exactly the 15 ceiling (fixer 2: every rank adds), a lowered
          ceiling 10 cuts it, a raised per-rank number stops at 15 and a raised ceiling lets it through; Scythe Tempering under a lowered ceiling);
          GearCfg.V3P / V3X = the table, a changed per-rank number changes the hit; loadV3 seeds trees.properties (= cfg_text) and reads
          hand edits (a bad line keeps the built-in number); the PROFILE cache: a profile switch reads the new profile's ranks at once
Scratch: tools/dev/scratch/st3r3b/gear (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.32"
V331 = "0.3.31"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "st3r3b", "gear")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J331 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V331))                       # read only
PKG = "com.skyy.gear."

if "--hkverify" not in sys.argv and "--hkaudit" not in sys.argv and "--hkfake" not in sys.argv:
    _H331 = os.path.join(HERE, "test_skyygear_0.3.31.py")
    _T331 = open(_H331, encoding="utf-8").read()
    _T331 = _T331[:_T331.rindex('if __name__ == "__main__":')]
    _argv = sys.argv
    sys.argv = [_H331, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--out", arg("--out")] if arg("--out") else [])
    H331 = {"__name__": "skyygear_h331", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T331, _H331 + " (library, 0.3.32)", "exec"), H331)
    sys.argv = _argv
    H330, H319, H320, H316 = H331["H330"], H331["H319"], H331["H320"], H331["H316"]
    H329 = H330["H329"]
    H328 = H329["H328"]
    for _h in (H331, H330, H329, H328, H328["H327"], H328["H326"], H328["H325"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
    check = H316["check"]


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S332 (the parent, no engine)
WANT_CHANGED = {"GearTool", "GearStats", "GearGArm", "SkyyGearPlugin", "GearCfg"}
HOLDER_ADDED = ["com/skyy/gear/CfgRows1.class", "com/skyy/gear/CfgRows2.class"]          # fixer 2: HOLDERS=2 (the kit's row holders)          # fixer: + GearCfg (the trees.properties numbers)
KIT_CHANGED = {"CfgRows", "CfgFile", "CfgDefaults"}          # fixer: the kit's tables (20 new rows, the second file + its defaults)
VERSION_TEXT = {"CfgFn", "CfgKit", "CfgPub"}


def run_assets332():
    ea, eb = entries(J331), entries(JAR)
    add, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    check(add == sorted(["com/skyy/gear/GearV3.class"] + HOLDER_ADDED) and not gone, "S332: added = GearV3.class + the 2 row holders only, nothing removed: + %s - %s" % (add, gone))
    big = [(n, len(eb[n])) for n in HOLDER_ADDED + ["com/skyy/gear/CfgRows.class"] if n in eb]
    print("  fixer 2: row holder class sizes %s" % big)
    diff = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    other = [n for n in diff if not n.endswith(".class") and n != "manifest.json"]
    check(not other, "S332: only class files + the manifest change: other %s" % other[:6])
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in diff if n.endswith(".class"))
    print("  class compare 0.3.31 -> 0.3.32: %d changed (%s)" % (len(chg), ", ".join(chg)))
    check(WANT_CHANGED <= set(chg) and set(chg) <= WANT_CHANGED | VERSION_TEXT | KIT_CHANGED,
          "S332: the changed classes = GearTool / GearStats / GearGArm / SkyyGearPlugin (+ version texts only): unexpected %s, missing %s"
          % (sorted(set(chg) - WANT_CHANGED - VERSION_TEXT - KIT_CHANGED), sorted(WANT_CHANGED - set(chg))))
    check(b"trees.properties" in eb["com/skyy/gear/CfgRows.class"] or b"trees.properties" in eb.get("com/skyy/gear/CfgFile.class", b""),
          "S332: the kit knows Skyy_SkyyGear/trees.properties (fixer)")
    for c in sorted(set(chg) & VERSION_TEXT):
        a_, b_ = ea["com/skyy/gear/%s.class" % c], eb["com/skyy/gear/%s.class" % c]
        check(len(a_) == len(b_) and b"0.3.31" in a_ and b_.replace(b"0.3.32", b"0.3.31") == a_, "S332: %s differs only by the version text" % c)
    check(b"tree:reads:SkyyGear" in eb["com/skyy/gear/GearV3.class"] and b"tree:fn:level" in eb["com/skyy/gear/GearV3.class"],
          "S332: GearV3 reads tree:fn:level and publishes tree:reads:SkyyGear")


# ====================================================================================================== H332 (the h319 child, real code)
def _h332(L, K):
    from jpype import JClass, JString, JInt, JFloat, JShort, JDouble, JObject, JImplements, JOverride
    P = lambda n: JClass(PKG + n)
    br, apply, stack, skills, U1 = L["br"], L["apply"], L["stack"], L["skills"], L["U1"]
    Roll, Data, SIC = L["Roll"], L["Data"], L["SIC"]
    V3, Tool, Stats, GA = P("GearV3"), P("GearTool"), P("GearStats"), P("GearGArm")
    CHM, HM, Dbl = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap"), JClass("java.lang.Double")

    def kc(cond, what):
        K.check(bool(cond), "H332 " + what)
    apply()
    # ============================================================== T: the table + the rank read
    rows = V3E.rows("SkyyGear")
    kc([str(x) for x in V3.KEY] == [V3E.key(e[0], e[1], e[2]) for e in rows] and [str(x) for x in V3.EFF] == [e[4] for e in rows]
       and [float(x) for x in V3.PER] == [float(e[5]) for e in rows] and [int(x) for x in V3.CAP] == [int(e[7]) for e in rows]
       and [str(x) for x in V3.SCALE] == [e[6] or "" for e in rows], "T: GearV3 = the %d trees_v3_effects rows of SkyyGear" % len(rows))
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
    ix = dict((str(V3.KEY[i]), i) for i in range(len(V3.KEY)))
    kTM = V3E.key("Mining", 2, "r1a")
    setr(Mining_b2_r1a=99)
    kc(int(V3.rank(U1, ix[kTM])) == 5, "T: a rank of 99 is clamped to Tool Mastery's max 5")
    RANK[kTM] = 2
    kc(int(V3.rank(U1, ix[kTM])) == 5, "T: the 1 s cache keeps the last answer inside the TTL")
    V3.RK.clear()
    kc(int(V3.rank(U1, ix[kTM])) == 2, "T: ... and reads again after it")
    RANK[kTM] = "boom"
    V3.RK.clear()
    kc(int(V3.rank(U1, ix[kTM])) == 0, "T: a throwing SkyyTrees = 0")
    RANK[kTM] = "x"
    V3.RK.clear()
    kc(int(V3.rank(U1, ix[kTM])) == 0, "T: a non-number = 0")
    V3.reads(True)
    kc(str(br.get("tree:reads:SkyyGear")) == V3E.reads_csv("SkyyGear"), "T: tree:reads:SkyyGear = the 10 keys")
    br.put("tree:reads:SkyyGear", JString("other"))
    V3.reads(False)
    kc(str(br.get("tree:reads:SkyyGear")) == "other", "T: shutdown removes only our own value")
    br.remove("tree:reads:SkyyGear")
    # ============================================================== B: the hits
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    BL = dict((n, bmap.get(n)) for n in ("Ore_Iron_Stone", "Wood_Oak_Trunk", "Rock_Stone"))
    kc(all(v is not None for v in BL.values()), "B setup: the real BlockTypes")
    skills(Mining=30, Foraging=30, Farming=30)
    br.remove("skill:bonus:" + str(U1))

    def dmg(sid, bn):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, stack(sid), BL[bn], JFloat(0.3)))
    setr()
    base = dict(((s, b), dmg(s, b)) for s in ("Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Pickaxe_Crude", "Ingredient_Bar_Iron")
                for b in ("Ore_Iron_Stone", "Wood_Oak_Trunk", "Rock_Stone"))
    kc(int(Tool.tier(JString("Tool_Pickaxe_Iron"))) == 2 and int(Tool.tier(JString("Tool_Pickaxe_Crude"))) == 0, "B: Iron = tier 2, Crude = tier 0")
    setr(Mining_b2_r1a=2)
    got = dict(((s, b), dmg(s, b)) for (s, b) in base)
    kc(abs(got[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")] - base[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")] * 1.08) < 1e-4
       and abs(got[("Tool_Pickaxe_Iron", "Rock_Stone")] - base[("Tool_Pickaxe_Iron", "Rock_Stone")] * 1.08) < 1e-4,
       "B: Tool Mastery rank 2, Iron pickaxe (tier 2) = x1.08 on ore and rock: %.4f -> %.4f" % (base[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")], got[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")]))
    same = [k for k in base if k not in (("Tool_Pickaxe_Iron", "Ore_Iron_Stone"), ("Tool_Pickaxe_Iron", "Rock_Stone")) and abs(got[k] - base[k]) > 1e-6]
    kc(not same, "B: nothing else moves (pickaxe on oak, the hatchet, a Crude pickaxe = tier 0, an iron bar): %s" % same)
    setr(Foraging_b3_r1b=3)
    got2 = dict(((s, b), dmg(s, b)) for (s, b) in base)
    kc(abs(got2[("Tool_Hatchet_Iron", "Wood_Oak_Trunk")] - base[("Tool_Hatchet_Iron", "Wood_Oak_Trunk")] * 1.12) < 1e-4
       and abs(got2[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")] - base[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")]) < 1e-6,
       "B: Tool Tier Bonus rank 3, Iron hatchet on oak = x1.12, the pickaxe unchanged")
    setr()
    kc(all(abs(dmg(s, b) - base[(s, b)]) < 1e-6 for (s, b) in base), "B: rank 0 again = exactly the 0.3.31 damage")
    # ============================================================== C: Scythe Tempering on a held hoe
    def gear_src():
        m_ = br.get("skill:bonus:" + str(U1))
        v_ = None if m_ is None else m_.get("gear")
        return {} if v_ is None else dict((str(k_), v_.get(k_)) for k_ in v_.keySet())
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Hoe_Iron"))
    c0 = gear_src()
    setr(Farming_b1_r5b=2)
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Hoe_Iron"))
    c1 = gear_src()
    f0 = float(c0.get("dd.farming", 0.0) or 0.0)
    f1 = float(c1.get("dd.farming", 0.0) or 0.0)
    kc(int(Tool.tier(JString("Tool_Hoe_Iron"))) == 2 and abs(f1 - f0 - 0.028) < 1e-6, "C: Scythe Tempering rank 2, Iron hoe (tier 2) = +2.8 Farming Fortune (dd.farming %.4f -> %.4f)" % (f0, f1))
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Pickaxe_Iron"))
    kc(abs(float(gear_src().get("dd.farming", 0.0) or 0.0)) < 1e-9, "C: never on a pickaxe")
    setr()
    # ============================================================== D: worn armor
    def armor_of(pieces, lvl=20):
        a_ = SIC(JShort(4))
        for k_, i_ in enumerate(pieces):
            if i_ is None:
                continue
            d_ = Roll.newDoc(i_, JInt(0), True, "craft", JInt(lvl))
            a_.setItemStackForSlot(JShort(k_), Data.put(stack(i_), d_, None))
        return a_

    def garmor():
        m_ = br.get("skill:bonus:" + str(U1))
        v_ = None if m_ is None else m_.get("garmor")
        return {} if v_ is None else dict((str(k_), float(v_.get(k_))) for k_ in v_.keySet())
    skills(Foraging=20, Farming=45, Mining=30)
    F1 = ["Armor_Foraging_F1_%s" % s_ for s_ in ("Head", "Chest", "Hands", "Legs")]
    MI = ["Armor_Iron_%s" % s_ for s_ in ("Head", "Chest", "Hands", "Legs")]
    GA.note(U1, armor_of(F1, 18))
    pf = [int(x) for x in V3.PCS.get(U1)]
    g0 = garmor()
    setr(Foraging_b3_r3a=1)
    GA.note(U1, armor_of(F1, 18))
    g1 = garmor()
    kc(pf == [0, 4, 0, 0] and abs(g1.get("dd.foraging", 0) - g0.get("dd.foraging", 0) - 0.03) < 1e-9,
       "D: 4 bark pieces counted %s; Foraging Gear Resonance rank 1 = +3 %% Foraging Fortune on top of the set's own (%s -> %s)" % (pf, g0, g1))
    setr(Mining_b2_r3a=2)
    GA.note(U1, armor_of(MI, 25))
    pm = [int(x) for x in V3.PCS.get(U1)]
    g2 = garmor()
    setr()
    GA.note(U1, armor_of(MI, 25))
    g2b = garmor()
    if pm[0] == 4:
        kc(abs(g2.get("bp.mining", 0) - g2b.get("bp.mining", 0) - 0.08) < 1e-9, "D: 4 metal pieces %s; Mining Gear Resonance rank 2 = bp.mining +0.08 (%s vs %s)" % (pm, g2, g2b))
    else:
        K.notes.append("H332 D: the metal pieces did not count as active here (%s) - Mining Gear Resonance checked on GearV3.armorInto below" % pm)
    m_ = HM()
    V3.PCS.put(U1, JClass("int[]")([7, 2, 1, 0]))
    setr(Mining_b2_r3a=2, Foraging_b3_r3a=1, Farming_b3_r3c=3)
    n_ = int(V3.armorInto(U1, m_))
    vals = dict((str(k_), float(m_.get(k_))) for k_ in m_.keySet())
    kc(n_ == 3 and abs(vals.get("bp.mining", 0) - 0.08) < 1e-9 and abs(vals.get("dd.foraging", 0) - 0.015) < 1e-9 and abs(vals.get("dd.farming", 0) - 0.0375) < 1e-9,
       "D: armorInto = per x rank x min(pieces, 4): mining 7 -> 4 x 2 x 1 %% = 0.08, foraging 2 x 0.75 %% = 0.015, farming 1 x 3 x 1.25 %% = 0.0375: %s" % vals)
    # ============================================================== E: combat rows through GearStats.extra
    br.remove("pets:stats:" + str(U1))
    br.remove("gear:extra:" + str(U1))
    setr()
    V3.PCS.put(U1, JClass("int[]")([0, 0, 0, 3]))
    e0 = Stats.extra(U1)
    kc(e0 is None, "E: rank 0, no other mod = no extra stats (0.3.31)")
    setr(Combat_b1_r1a=3, Combat_b1_r1b=2, Combat_b1_r4a=1, Combat_b1_r4b=2)
    e1 = Stats.extra(U1)
    Defs = P("GearDefs")
    gi = lambda k_: int(e1[int(Defs.sIndex(JString(k_)))]) if e1 is not None else None
    kc(e1 is not None and gi("dmg") == 6 + 12 and gi("cc") == 4 and gi("cd") == 3,
       "E: Hone Edge 3 (+6 %%) + Combat Gear Resonance 2 x 3 combat pieces (+12 %%) = dmg 18, Weak Spot 2 = cc 4, Crit Mastery 1 = cd 3: dmg %s cc %s cd %s" % (gi("dmg"), gi("cc"), gi("cd")))
    pm2 = HM()
    pm2.put("dmg", Dbl.valueOf(JDouble(5.0)))
    br.put("pets:stats:" + str(U1), JClass("java.util.Collections").unmodifiableMap(pm2))
    V3.CMB.clear()
    e2 = Stats.extra(U1)
    kc(e2 is not None and int(e2[int(Defs.sIndex(JString("dmg")))]) == 23, "E: + SkyyPets' dmg 5 = 23 (summed)")
    br.remove("pets:stats:" + str(U1))
    br.remove("tree:fn:level")
    V3.RK.clear()
    V3.CMB.clear()
    kc(Stats.extra(U1) is None, "E: no SkyyTrees = nothing")
    V3.forget(U1)
    kc(V3.PCS.get(U1) is None, "E: forget drops the player's pieces")
    # ============================================================== F (fixer): ceilings, Server Setup numbers, trees.properties, profiles
    Cfg = P("GearCfg")
    br.put("tree:fn:level", Tr())
    kc([round(float(getattr(Cfg, "V3P%d" % i)), 6) for i in range(len(rows))] == [round(e[5] * V3E.unit(e[4]), 6) for e in rows]
       and [round(float(getattr(Cfg, "V3X%d" % i)), 6) for i in range(len(rows))] == [round(V3E.vmax(e) * V3E.unit(e[4]), 6) for e in rows],
       "F: GearCfg.V3P / V3X = the table's per-rank numbers and ceilings (display units)")
    iFG = [i for i, e in enumerate(rows) if (e[0], e[2]) == ("Foraging", "r3a")][0]
    iSC = [i for i, e in enumerate(rows) if (e[0], e[2]) == ("Farming", "r5b")][0]
    iTM = [i for i, e in enumerate(rows) if (e[0], e[2]) == ("Mining", "r1a")][0]
    m_ = HM()
    V3.PCS.put(U1, JClass("int[]")([0, 4, 0, 0]))
    setr(Foraging_b3_r3a=5)
    V3.armorInto(U1, m_)
    kc(abs(float(m_.get("dd.foraging")) - 0.15) < 1e-9, "F: Foraging Gear Resonance rank 5 x 4 pieces = 15 %% = exactly the ceiling (fixer 2: every rank adds): %s" % m_)
    setr(Foraging_b3_r3a=4)
    m_ = HM()
    V3.armorInto(U1, m_)
    kc(abs(float(m_.get("dd.foraging")) - 0.12) < 1e-9, "F: ... rank 4 = 12 %% (the last rank still adds 3): %s" % m_)
    setr(Foraging_b3_r3a=5)
    setattr(Cfg, "V3X%d" % iFG, 10.0)
    m_ = HM()
    V3.armorInto(U1, m_)
    kc(abs(float(m_.get("dd.foraging")) - 0.10) < 1e-9, "F: ... a Server Setup ceiling of 10 cuts it to 10 %%: %s" % m_)
    setattr(Cfg, "V3X%d" % iFG, 15.0)
    setattr(Cfg, "V3P%d" % iFG, 1.0)
    m_ = HM()
    V3.armorInto(U1, m_)
    kc(abs(float(m_.get("dd.foraging")) - 0.15) < 1e-9, "F: ... a per-rank number of 1 (20 %%) stops at the 15 ceiling: %s" % m_)
    setattr(Cfg, "V3X%d" % iFG, 30.0)
    m_ = HM()
    V3.armorInto(U1, m_)
    kc(abs(float(m_.get("dd.foraging")) - 0.20) < 1e-9, "F: ... and a ceiling of 30 lets the full 20 %% through: %s" % m_)
    setattr(Cfg, "V3X%d" % iFG, 15.0)
    setattr(Cfg, "V3P%d" % iFG, 0.75)
    setattr(Cfg, "V3X%d" % iSC, 2.0)
    setr(Farming_b1_r5b=2)
    Tool.LAST.clear()
    Tool.held(U1, stack("Tool_Hoe_Iron"))
    f2 = float(gear_src().get("dd.farming", 0.0) or 0.0)
    kc(abs(f2 - f0 - 0.02) < 1e-6, "F: Scythe Tempering rank 2, Iron hoe = 2.8 -> a lowered ceiling of 2 gives +2 (%.4f)" % f2)
    setattr(Cfg, "V3X%d" % iSC, 15.0)
    setr(Mining_b2_r1a=2)
    setattr(Cfg, "V3P%d" % iTM, 3.0)
    d3 = dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone")
    kc(abs(d3 - base[("Tool_Pickaxe_Iron", "Ore_Iron_Stone")] * 1.12) < 1e-4, "F: Tool Mastery per rank set to 3 %%: rank 2 x tier 2 = x1.12 (%.4f)" % d3)
    setattr(Cfg, "V3P%d" % iTM, 2.0)
    # trees.properties
    Paths = JClass("java.nio.file.Paths")
    td = os.path.join(SCR_BASE, "v3cfg")
    os.makedirs(td, exist_ok=True)
    tf = os.path.join(td, "trees.properties")
    if os.path.exists(tf):
        os.remove(tf)
    res = str(Cfg.loadV3(Paths.get(td)))
    kc(os.path.exists(tf) and open(tf, encoding="latin-1", newline="").read() == V3E.cfg_text("SkyyGear") and res == "trees.properties read",
       "F: a missing trees.properties is written with the table's defaults (%s)" % res)
    ck = V3E.ckey(rows[iTM])
    t_ = open(tf, encoding="latin-1", newline="").read().replace("%s.per=2\n" % ck, "%s.per=2.5\n" % ck).replace("%s.max=70\n" % ck, "%s.max=abc\n" % ck)
    open(tf, "w", encoding="latin-1", newline="").write(t_)
    Cfg.loadV3(Paths.get(td))
    kc(abs(float(getattr(Cfg, "V3P%d" % iTM)) - 2.5) < 1e-9 and abs(float(getattr(Cfg, "V3X%d" % iTM)) - 70.0) < 1e-9 and abs(float(Cfg.v3per(iTM)) - 0.025) < 1e-12,
       "F: a hand edit (per 2.5) is read, a bad line (max abc) keeps 70; v3per answers the fraction")
    setattr(Cfg, "V3P%d" % iTM, 2.0)
    # the profile cache (critic: the first second after a switch used the old profile's ranks)
    PK = ["main"]

    @JImplements("java.util.function.Function")
    class Pk(object):
        @JOverride
        def apply(self, a):
            return JString(str(a) + "-" + PK[0])
    br.put("profile:fn:key", Pk())
    br.remove("pets:stats:" + str(U1))
    br.remove("gear:extra:" + str(U1))
    V3.PCS.put(U1, JClass("int[]")([0, 0, 0, 0]))
    setr(Combat_b1_r1a=3)
    ea_ = Stats.extra(U1)
    RANK[V3E.key("Combat", 1, "r1a")] = 1
    eb_ = Stats.extra(U1)
    kc(ea_ is not None and eb_ is not None and int(ea_[int(Defs.sIndex(JString("dmg")))]) == 6 and int(eb_[int(Defs.sIndex(JString("dmg")))]) == 6,
       "F: the same profile inside the 1 s cache keeps its answer (dmg 6)")
    PK[0] = "second"
    ec_ = Stats.extra(U1)
    kc(ec_ is not None and int(ec_[int(Defs.sIndex(JString("dmg")))]) == 2, "F: a profile switch reads the new profile's rank at once (dmg 6 -> 2, no 1 s of the old ranks)")
    kc(int(V3.rank(U1, ix[V3E.key("Combat", 1, "r1a")])) == 1, "F: ... and the rank cache is the new profile's too")
    br.remove("profile:fn:key")
    br.remove("tree:fn:level")
    V3.forget(U1)
    print("  note (h332): T-F ran")


if "--hkverify" not in sys.argv and "--hkaudit" not in sys.argv and "--hkfake" not in sys.argv:
    _H331_PHASE = H319["_h319"]          # the 0.3.31 lib's wrapper (H329 + H330 + H331)

    def _h319_h332(L, K):
        _H331_PHASE(L, K)
        try:
            _h332(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H332: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_h332


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
    assert os.path.isfile(J331) and os.path.isfile(JAR), (J331, JAR)
    if "--keep" not in sys.argv:
        atexit.register(lambda: shutil.rmtree(SCR_BASE, ignore_errors=True))
    run_assets332()
    run_hk()
    H331["_live_copy"]()
    H320["run_fallback"](lambda x: x == "h319", [])


if __name__ == "__main__":
    main()
