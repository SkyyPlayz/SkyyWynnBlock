"""Harness for SkyyGear 0.3.18 (tools/gear_0_3_18_patch.py header = lean round gear0318) = the 0.3.17 harness's children run on the 0.3.18 jar
+ S318 + the Upgrade-page checks (inside the 0.3.16 page child) + H318:
    python tools/gear_0_3_18_patch.py && python SkyyGear/build_skyygear_0.3.18.py
    python SkyyGear/test_skyygear_0.3.18.py [--keep] [--only assets,h318,h317,h316,...]

  S318 the jar 0.3.17 -> 0.3.18: one class added (GearReq), every non-class file identical except manifest.json
  P318 (in the 0.3.16 page child, the booted page rig): the pickaxe's Upgrade panel lists Breaking Speed FIRST, then Breaking Power,
       Fortune, Wisdom, Vein Mine; every row's name, element ids and click carry ITS perk index; real clicks buy the right perk (Breaking
       Speed, then Breaking Power); the tier row = a title + the colour list (green / red rows); assert_menu_page on the Upgrade page
  H318 ONE booted engine (the 0.3.5 life setup):
       A  GearReq: the row texts ("Farming Lv 10 : 6", "Copper Ingot 25 (need 13)", "Coins ..."), the colours, draw / drawRow markup
       B  ACCESSORY BREAKING POWER: accBp sums bp.<skill> over every skill:bonus source except "gear"; bad values skipped; the guards;
          onDamage / mdamage x(1 + BP) on the tool's own blocks only (pickaxe ore / rock, hatchet logs, the multitool's two sides),
          under-level tools too, never a non-tool or another block; no source = exactly the 0.3.17 numbers
       C  skill:bonus:reads:bp in SkyyGearPlugin start (put TRUE) + shutdown (remove only our TRUE), by the class file
Scratch: tools/dev/scratch/gear0318/gear/harness (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.18"
V317 = "0.3.17"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0318", "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J317 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V317))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.17 harness as a library (it loads the older ones); its main runs every child on THIS jar in THIS scratch folder
_H317 = os.path.join(HERE, "test_skyygear_0.3.17.py")
_T317 = open(_H317, encoding="utf-8").read()
_cut = _T317.rindex('if __name__ == "__main__":')
# P318: appended to the 0.3.17 tools-page block (it runs inside the 0.3.16 page child: lp, render, click, appends, sets, page_ok, kc, LL ...)
_A317 = '''       "P 0.3.17: the pickaxe panel = 5 perk rows (Breaking Power, Fortune, Wisdom, Vein Mine, Breaking Speed), %d px <= 662 (#SkyyGMain)" % h17)
"""'''
assert _T317.count(_A317) == 1, "the 0.3.17 tools-page block moved"
_B318 = '''       "P 0.3.17: the pickaxe panel = 5 perk rows (Breaking Power, Fortune, Wisdom, Vein Mine, Breaking Speed), %d px <= 662 (#SkyyGMain)" % h17)
    # 0.3.18 (test_skyygear_0.3.18.py P318, Skyy 2026-10-17 "move breaking speed to the top"): the row order, ids and clicks by perk index
    ids18 = [int(mk.split(" ")[1][len("#SkyyGPk"):]) for mk in rows17]
    nm18 = [str(LL.PKN[p_]) for p_ in ids18]
    _v18 = lambda x: str(json.loads(x).get("0", x)) if str(x).startswith("{") else str(x)
    sv18 = dict((k_, _v18(v_)) for k_, v_ in sets(cl17))
    bind18 = list(zip(ev17, ed17))
    kc(nm18 == ["Breaking Speed", "Breaking Power", "Fortune", "Wisdom", "Vein Mine"],
       "P318: the pickaxe's perk rows = Breaking Speed FIRST, then Breaking Power, Fortune, Wisdom, Vein Mine: %s" % nm18)
    kc(all(str(sv18.get("#SkyyGPk%dN.Text" % p_, "")).startswith(str(LL.PKN[p_]) + "   Lv") for p_ in ids18)
       and all(any(str(se_) == "#SkyyGPk%dB" % p_ and ("buy:%d:" % p_) in str(d_) for se_, d_ in bind18) for p_ in ids18),
       "P318: each row's name, ids (#SkyyGPk<perk>) and button click (buy:<perk>:<token>) carry ITS perk index: %s" % [(str(se_), str(d_)) for se_, d_ in bind18 if "buy:" in str(d_)][:6])
    tr18 = [mk for p_, mk in appends(cl17) if p_ == "SkyyGPTierL" or p_ == "SkyyGPReq"]
    ts18 = str(sv18.get("#SkyyGPTier.Text", ""))
    rq18 = [(str(sv18.get("#SkyyGPReqL%d.Text" % i_, "")), mk) for i_, mk in enumerate([mk for p_, mk in appends(cl17) if p_ == "SkyyGPReq"])]
    K.notes.append("P318 the pickaxe tier row: %r + %s" % (ts18, [t_ for t_, _m in rq18]))
    kc(ts18.startswith("Tier: ") and " - Next: " in ts18 and rq18 and any(" Lv " in t_ and " : " in t_ for t_, _m in rq18)
       and all(("TextColor: " + str(P("GearDefs").C_OK)) in m_ or ("TextColor: " + str(P("GearDefs").C_BAD)) in m_ or "TextColor: #ffffff(0.8)" in m_ for _t, m_ in rq18)
       and not any("You need" in t_ or "(you: " in t_ for t_, _m in rq18),
       "P318: the tier row = 'Tier: X - Next: Y' + the colour list (a 'Mining Lv N : M' row, materials, green / red, no 'You need ... (you: M)' sentence)")
    SK18 = None
    try:
        SK18 = dict(L["SK"])
    except Exception:
        SK18 = None
    pr18 = br.get("gear:perk:readers")
    br.put("gear:perk:readers", JString("vein,fell,swing"))
    skills(Mining=30)
    R18 = LL.reg(str(Gear.pkey(U1)))
    SW18 = int(LL.PK_SWING)
    old18 = dict((k_, R18.getProperty(k_)) for k_ in ("pickaxe.up.swing", "pickaxe.up.spd", "pickaxe.up.fort"))
    b0 = [int(LL.perkOf(R18, 0, p_)) for p_ in (SW18, 0, 1)]
    page_ok("Upgrade (tools) pickaxe, Breaking Speed first (0.3.18)", lp, "Upgrade")
    c1 = click(lp, '{"a":"buy:%d:%d"}' % (SW18, int(lp.tok)))
    b1 = [int(LL.perkOf(R18, 0, p_)) for p_ in (SW18, 0, 1)]
    render(lp)
    c2 = click(lp, '{"a":"buy:0:%d"}' % int(lp.tok))
    b2 = [int(LL.perkOf(R18, 0, p_)) for p_ in (SW18, 0, 1)]
    kc(b1 == [b0[0] + 1, b0[1], b0[2]] and b2 == [b0[0] + 1, b0[1] + 1, b0[2]] and c1 >= 1 and c2 >= 1,
       "P318: real clicks: the TOP row's button buys Breaking Speed (swing %d -> %d), the second row's Breaking Power (spd %d -> %d), Fortune untouched: %s %s %s / %s"
       % (b0[0], b1[0], b0[1], b2[1], b0, b1, b2, lp.info))
    for k_, v_ in old18.items():
        if v_ is None:
            R18.remove(k_)
        else:
            R18.setProperty(k_, v_)
    if pr18 is None:
        br.remove("gear:perk:readers")
    else:
        br.put("gear:perk:readers", pr18)
    if SK18 is not None:
        L["SK"].clear()
        L["SK"].update(SK18)
    try:
        P("GearGate").forget(U1)
    except Exception:
        pass
    lp.sel = JInt(5)
    t5, cl5, ev5, ed5 = render(lp)
    sv5 = dict((k_, _v18(v_)) for k_, v_ in sets(cl5))
    rq5 = [str(sv5.get("#SkyyGPReqL%d.Text" % i_, "")) for i_ in range(4) if ("#SkyyGPReqL%d.Text" % i_) in sv5]
    K.notes.append("P318 the watering can tier row (Skyy's screenshot): %r + %s" % (str(sv5.get("#SkyyGPTier.Text", "")), rq5))
    page_ok("Upgrade (tools) watering can, the colour list (0.3.18)", lp, "Upgrade")
    lp.sel = JInt(0)
"""'''
_T317 = _T317.replace(_A317, _B318)
_argv = sys.argv
sys.argv = [_H317, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep",)] + \
    (["--only", arg("--only")] if arg("--only") else [])
H317 = {"__name__": "skyygear_h317", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T317[:_cut + len(_B318) - len(_A317)], _H317 + " (library, + the 0.3.18 tools-page checks)", "exec"), H317)
sys.argv = _argv
H317["VERSION"] = VERSION
H317["H316"]["VERSION"] = VERSION
H316 = H317["H316"]
H35 = H317["H35"]
FI7_SRC = H317["FI7_SRC"]

_WHY_REQ = ("0.3.18 by design (Skyy 2026-10-17 'do a color coded list (level 10 (IN RED) :6 my lvl  Copper 25 (in green) (use this pattern "
            "everywhere'): the Upgrade list's second line is the colour list side by side (#SkyyGURow<i>QL<n>: 'Mining Lv 5 : 1', "
            "'Copper Ingot 25 (need 25)', 'In Requip - take it out') instead of one gold sentence; P318 / H318 A check the list")
WAIVE_318 = [          # (prefix, why) - each one an explained 0.3.18 change of an older check
    ("U the list: the lifelong pickaxe first, 'T1 Crude -> T2 Copper: <Copper Pickaxe>'", _WHY_REQ),
    ("U (fix round) gear IN Requip is listed: tier line, cost, 'In Requip: take it out'", _WHY_REQ)]
H316["WAIVE_316"].extend(WAIVE_318)
FAILS, OKS = H316["FAILS"], H316["OKS"]


def check(cond, what):
    H316["check"](cond, what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S318
def run_assets318():
    ea, eb = entries(J317), entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(added == ["com/skyy/gear/GearReq.class"] and not gone and changed == ["manifest.json"],
          "S318: 0.3.17 -> 0.3.18 adds GearReq, removes nothing, changes only manifest.json among the files: added %s, gone %s, changed %s"
          % (added[:4], gone[:4], changed))
    check('"0.3.18"' in eb["manifest.json"].decode("utf-8"), "S318: the manifest says 0.3.18")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.17 -> 0.3.18: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    want_c = {"GearLL", "LifePage", "GearTool", "UpgPage", "ReforgePage", "SmithPage", "SkyyGearPlugin", "CfgFn", "CfgRows", "CfgDefaults",
              "CfgKit", "CfgPub", "CfgFile", "GearCfg"}
    check(set(chg) <= want_c, "S318: only the page / tool / plugin classes (+ config / version text) changed: unexpected %s" % sorted(set(chg) - want_c))
    # C: the reads flag, by the class file (the harness never boots the plugin)
    pb = eb.get("com/skyy/gear/SkyyGearPlugin.class", b"")
    check(b"skill:bonus:reads:bp" in pb and b"(Ljava/lang/Object;Ljava/lang/Object;)Z" in pb,
          "S318 C: SkyyGearPlugin puts skill:bonus:reads:bp and removes it with Map.remove(key, TRUE) (only our own TRUE)")


# ====================================================================================================== H318
def run_h318(out):
    fi7 = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.7.jar")
    shutil.copyfile(FI7_SRC, fi7)
    H35["FI_JAR"] = fi7
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h318(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H318: the phase raised: %s" % traceback.format_exc()[-1800:])
    K.save()


def _h318(L, K):
    from jpype import JClass, JInt, JFloat, JDouble, JObject, JString, JLong
    br, Gear, Cfg, LL, Data = L["br"], L["Gear"], L["Cfg"], L["LL"], L["Data"]
    PR1, U1, stack, skills, apply, mkinv = L["PR1"], L["U1"], L["stack"], L["skills"], L["apply"], L["mkinv"]
    P = lambda n: JClass(PKG + n)
    Tool, Req, Defs, Multi = P("GearTool"), P("GearReq"), P("GearDefs"), P("GearMulti")
    CHM, HM = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap")
    Dbl = JClass("java.lang.Double")
    AL = JClass("java.util.ArrayList")

    def kc(cond, what):
        K.check(bool(cond), what)

    def eq(got, want, what):
        K.check(got == want, "%s: got %s, want %s" % (what, got, want))
    apply()

    # ============================================================== A: GearReq
    eq(str(Req.lvl(JString("Farming"), JInt(10), JInt(6))), "Farming Lv 10 : 6", "A: the level row (Skyy 'level 10 (IN RED) :6 my lvl')")
    eq(str(Req.item(JString("Copper Ingot"), JLong(25), JLong(25))), "Copper Ingot 25", "A: a met material = name + amount")
    eq(str(Req.item(JString("Copper Ingot"), JLong(25), JLong(12))), "Copper Ingot 25 (need 13)", "A: a short material adds (need N)")
    eq(str(Req.item(JString("Iron Bar"), JLong(6), JLong(-1))), "Iron Bar 6 (?)", "A: an unknown count")
    kc(str(Req.coins(JLong(1200), JLong(900))).startswith("Coins 1") and "(need 300)" in str(Req.coins(JLong(1200), JLong(900)))
       and "need" not in str(Req.coins(JLong(1200), JLong(5000))) and "need" not in str(Req.coins(JLong(1200), JLong(-1))),
       "A: the coins row: %s / %s" % (Req.coins(JLong(1200), JLong(900)), Req.coins(JLong(1200), JLong(5000))))
    eq((str(Req.col(JInt(1))), str(Req.col(JInt(0))), str(Req.col(JInt(-1)))), (str(Defs.C_OK), str(Defs.C_BAD), "#ffffff(0.8)"),
       "A: green met / red not met / white neutral (the vanilla C_OK / C_BAD)")
    rows = AL()
    Req.add(rows, JString("Farming Lv 10 : 6"), JInt(0))
    Req.add(rows, JString("Copper Ingot 25"), JInt(1))
    Req.add(rows, None, JInt(1))
    kc(int(rows.size()) == 2 and not bool(Req.allMet(rows)), "A: rows + allMet (a null text is skipped)")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    ub = UCB()
    hgt = int(Req.draw(ub, JString("#X"), JString("SkyyGTq"), rows, JInt(18), JInt(14), JInt(4)))
    cmds = [str(c_) for c_ in ub.getCommands()]
    kc(hgt == 36, "A: draw = 18 px a line (%d)" % hgt)
    for i_ in range(5):
        Req.add(rows, JString("Mat %d 1 (need 1)" % i_), JInt(0))
    ub2 = UCB()
    hg2 = int(Req.draw(ub2, JString("#X"), JString("SkyyGTq"), rows, JInt(18), JInt(14), JInt(4)))
    kc(hg2 == 72, "A: at most 4 lines (the last lists the rest): %d px" % hg2)
    ub3 = UCB()
    Req.drawRow(ub3, JString("#SkyyGURow0B"), JString("SkyyGURow0Q"), rows, JInt(786), JInt(13), JInt(4))
    kc(len(list(ub3.getCommands())) == 8, "A: drawRow = 4 labels side by side + their texts (%d commands)" % len(list(ub3.getCommands())))

    # ============================================================== B: accessory Breaking Power
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    BL = dict((n, bmap.get(n)) for n in ("Ore_Iron_Stone", "Wood_Oak_Trunk", "Rock_Stone"))
    kc(all(v is not None for v in BL.values()), "B setup: the real BlockTypes: %s" % [k for k, v in BL.items() if v is None])
    skills(Mining=30, Foraging=30)
    key = "skill:bonus:" + str(U1)

    def srcmap(**kv):
        m_ = HM()
        for k_, v_ in kv.items():
            m_.put(k_.replace("__", "."), v_ if not isinstance(v_, float) else Dbl.valueOf(JDouble(v_)))
        return m_

    def bonus(**srcs):
        if not srcs:
            br.remove(key)
            return
        c_ = CHM()
        for n_, m_ in srcs.items():
            c_.put(n_, m_)
        br.put(key, c_)

    def dmg(sid, bn):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, stack(sid), BL[bn], JFloat(0.3)))

    def ab(sk):
        return float(Tool.accBp(U1, JString(sk)))
    bonus()
    pk0, ht0, pkw0, rock0 = dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone"), dmg("Tool_Hatchet_Iron", "Wood_Oak_Trunk"), dmg("Tool_Pickaxe_Iron", "Wood_Oak_Trunk"), dmg("Tool_Pickaxe_Iron", "Rock_Stone")
    sw0 = dmg("Ingredient_Bar_Iron", "Ore_Iron_Stone")
    eq((ab("mining"), ab("foraging")), (1.0, 1.0), "B: no skill:bonus map = x1")
    K.notes.append("B base damage (0.3 in): pickaxe ore %.4f, hatchet oak %.4f, pickaxe on oak %.4f, pickaxe rock %.4f, iron bar %.4f" % (pk0, ht0, pkw0, rock0, sw0))
    bonus(accessories=srcmap(bp__mining=0.5, swing__mining=0.2, dd__mining=0.3))
    kc(abs(ab("mining") - 1.5) < 1e-9 and ab("foraging") == 1.0, "B: accessories bp.mining 0.5 = x1.5 for mining, foraging untouched")
    kc(abs(dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") - pk0 * 1.5) < 1e-4 and abs(dmg("Tool_Pickaxe_Iron", "Rock_Stone") - rock0 * 1.5) < 1e-4,
       "B: the pickaxe on ore / rock hits x(1 + BP): %.4f -> %.4f" % (pk0, dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone")))
    kc(abs(dmg("Tool_Pickaxe_Iron", "Wood_Oak_Trunk") - pkw0) < 1e-6 and abs(dmg("Tool_Hatchet_Iron", "Wood_Oak_Trunk") - ht0) < 1e-6
       and abs(dmg("Ingredient_Bar_Iron", "Ore_Iron_Stone") - sw0) < 1e-6,
       "B: never on another block (pickaxe on oak), never the hatchet with bp.mining, never a non-tool (an iron bar)")
    bonus(accessories=srcmap(bp__foraging=0.25))
    kc(abs(dmg("Tool_Hatchet_Iron", "Wood_Oak_Trunk") - ht0 * 1.25) < 1e-4 and abs(dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") - pk0) < 1e-6,
       "B: bp.foraging 0.25 = the hatchet on logs x1.25, the pickaxe unchanged")
    bonus(gear=srcmap(bp__mining=9.0, dd__mining=1.0))
    eq(ab("mining"), 1.0, "B: our own 'gear' source is never counted")
    bonus(gear=srcmap(bp__mining=9.0), accessories=srcmap(bp__mining=0.3), pets=srcmap(bp__mining=0.2), trees=srcmap(dd__mining=0.5))
    kc(abs(ab("mining") - 1.5) < 1e-9, "B: every other source adds up (accessories 0.3 + pets 0.2 = x1.5; gear ignored): %s" % ab("mining"))
    bonus(accessories=srcmap(bp__mining=JString("x")), pets=srcmap(bp__mining=float("nan")), b=srcmap(bp__mining=float("inf")), c=JString("notamap"))
    eq(ab("mining"), 1.0, "B: bad values (a String, NaN, infinite, a source that is not a map) are skipped")
    bonus(accessories=srcmap(bp__mining=-0.5))
    kc(abs(ab("mining") - 0.5) < 1e-9 and abs(dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") - pk0 * 0.5) < 1e-4, "B: a debuff lowers it (signed): x0.5")
    bonus(accessories=srcmap(bp__mining=-5.0))
    kc(abs(ab("mining") - 0.05) < 1e-9 and dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") > 0.0, "B: the floor guard x0.05 (never 0 / negative)")
    bonus(accessories=srcmap(bp__mining=1e9))
    pmax = float(Cfg.pmax())
    kc(abs(ab("mining") - pmax) < 1e-6 and dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") <= 0.3 * pmax + 1e-3, "B: the top guard tool.power.max (x%s)" % pmax)
    apply(tool__power__max="2")
    kc(abs(ab("mining") - 2.0) < 1e-9 and dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") <= 0.6 + 1e-4, "B: tool.power.max applies live to the total (2)")
    apply()
    # under level: Mining 1 with an Iron pickaxe (the tool's own bonus goes; the accessory part still works, like the Mining Sets' Power)
    skills(Mining=1, Foraging=1)
    P("GearGate").forget(U1)
    bonus()
    pu0 = dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone")
    bonus(accessories=srcmap(bp__mining=0.5))
    pu1 = dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone")
    kc(abs(pu1 - pu0 * 1.5) < 1e-4, "B: an under-level tool still gets the accessory part: %.4f -> %.4f" % (pu0, pu1))
    skills(Mining=30, Foraging=30)
    P("GearGate").forget(U1)
    # the multitool's two sides
    mid = str(Multi.mid(1))
    bonus()
    mo0, mw0 = dmg(mid, "Ore_Iron_Stone"), dmg(mid, "Wood_Oak_Trunk")
    bonus(accessories=srcmap(bp__mining=0.5, bp__foraging=0.25))
    mo1, mw1 = dmg(mid, "Ore_Iron_Stone"), dmg(mid, "Wood_Oak_Trunk")
    kc(abs(mo1 - mo0 * 1.5) < 1e-3 and abs(mw1 - mw0 * 1.25) < 1e-3,
       "B: a multitool: stone / ore x(1 + bp.mining), logs x(1 + bp.foraging): %.4f -> %.4f, %.4f -> %.4f" % (mo0, mo1, mw0, mw1))
    bonus()
    kc(abs(dmg("Tool_Pickaxe_Iron", "Ore_Iron_Stone") - pk0) < 1e-6 and abs(dmg(mid, "Ore_Iron_Stone") - mo0) < 1e-6,
       "B: the source gone = exactly the 0.3.17 numbers again")


# ====================================================================================================== main
def main():
    if "--h318" in sys.argv:
        run_h318(arg("--out"))
        return
    if any(a.startswith("--") and a not in ("--only", "--keep", "--dir", "--jar", "--root", "--out") for a in sys.argv[1:]):
        H317["main"]()          # an older child flag (0.3.17 dispatches --h317, the rest goes on down)
        return
    assert os.path.isfile(J317), J317
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    H317["run_assets317"] = run_assets318          # the jar compare of THIS round (0.3.17 -> 0.3.18)
    _take = H316["take"]          # = the 0.3.17 take2 once its main has run; wrap at call time below

    def run():
        H317["main"]()
    # ours runs after h317: H317.main installs its take2 into H316 and calls H316.main; wrap H316["take"] lazily through a proxy
    _orig_main316 = H316["main"]

    def main316():
        take17 = H316["take"]

        def take3(path, label):
            d = take17(path, label)
            if label == "h316" and want("h318"):          # the 0.3.17 take2 has run h317 inside take17 by now
                env = dict(os.environ)
                env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
                env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
                out = os.path.join(SCRATCH, "h318.json")
                pr = H316["child"](env, "--h318", "--out", out)
                check(pr.returncode == 0, "h318: the child exited cleanly (%s)" % pr.returncode)
                take17(out, "h318")
            return d
        H316["take"] = take3
        return _orig_main316()
    H316["main"] = main316
    if only and "h318" in only.split(","):
        extra = [x for x in ("h317", "h316") if x not in only.split(",")]
        if extra:
            sys.argv[sys.argv.index("--only") + 1] = only + "," + ",".join(extra)
    run()


if __name__ == "__main__":
    main()
