"""Harness for SkyyGear 0.3.28 (tools/gear_0_3_28_patch.py header = Fortune +3 a level on every lifelong tool, no Fortune cap, weapon bags pick
their type at identify, retired hoes / sickles off the Upgrade list)
= the 0.3.27 harness (and through it the whole older chain) run on the 0.3.28 jar + S328 (the jar compare 0.3.27 -> 0.3.28, replacing S327) + H328
(inside the h319 child, after H319 .. H327, on the same booted engine), plus a --static phase (no jar):
    python tools/gear_0_3_28_patch.py && python SkyyGear/build_skyygear_0.3.28.py
    python SkyyGear/test_skyygear_0.3.28.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.28.py --static [--keep]

  The 0.3.27 harness runs with the older children's literals that 0.3.28 changes ON PURPOSE moved (H327_MOVE / OLDER_MOVE below: the Fortune
  rates 2 / 10 -> 3, the armor Fortune cap 15 -> 0, the old "% extra ... chance" tooltip texts, "Unidentified <Type>" on random weapon bags).
  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.28.py, compiles, line endings kept
       A  the anchors: VERSION; no new system / command / class; h28Update / h28Log / migrate0328 after h7Old and migrate0327, before the setup
          call; fdrops before its callers; GearUp.rows skips retired ids; GearUnid.open picks the weapon type of a grp bag
  S328 the jar 0.3.27 -> 0.3.28: adds / removes nothing; changes only manifest.json + the classes S328_MUST / S328_MAY
  H328 (the h319 child, ONE booted engine) - real code:
       A  the fresh file + GearCfg after apply: Fortune 3 / 3 a level, armor.fortune.cap 0 (= none, fcapA huge), unid.typeAtIdentify, marker once;
          GearLL.pfort 3 for the pickaxe AND the hatchet / Harvester / hoe / pole kinds
       B  h28Update on a 0.3.27-shaped file: the 3 old defaults rewritten in place (number compare: 2.0 = 2), CRLF kept, marker at the END, a hand
          edit kept + noted, one change-log row per change, second run = null; h28Log = the change-log row
       C  the texts: GearTool.fdrops (0 / 30 / 100 / 150 / 300 / 1010 / 21 %), LifePage.effect (pickaxe, hatchet: "+30% Mining Fortune = 1 drop
          + 30% for a 2nd"; the pole's double catch), GearSickle.roll floor + chance, no 5 cap (1000 % = 10), the 100 safety stop
       D  bug 12: GearUnid.roll random weapon bags carry grp w + "Unidentified Weapon"; armor / forced-type bags do not; open() picks among
          several weapon types; pickW with a class lean at 100 % = only lean types; no candidate = the stored type; an old bag (no grp) opens
          as its stored type; unid.typeAtIdentify=false = the stored type name
       E  bug 17: GearUp.retired - plain hoes / sickles yes, Harvesters / pickaxes no, harvester.only off = nothing retired
       F  the T3 Fortune cap: GearLL.lineCapP - Bronze Fortune 33 (other lines 40), Thorium 40, Iron 30 ...; a saved 40 works as 33
  NOT COVERED (smoke test / Skyy in game): migrate0328 on the real config.properties, the Upgrade page on a real inventory with a hoe, the class
  lean read from SkyyClasses' bridge on a real player.
Scratch: tools/dev/scratch/g328/h328/gear/harness (full run) and .../h328/static (--static), deleted at the end unless --keep.
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


VERSION = "0.3.28"
V327 = "0.3.27"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g328", "h328")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J327 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V327))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_28_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.28.py")
GEN327 = os.path.join(HERE, "build_skyygear_0.3.27.py")

S328_MUST = {"GearCfg": "H28_ rows + h28Update / h28Log / migrate0328 + fcapA + the new defaults", "GearTool": "fdrops + the Fortune lines",
             "LifePage": "effect: the Fortune line text", "GearSickle": "roll: no 5 cap", "GearMine": "fcapA", "GearGArm": "fcapA",
             "GearUnid": "grp w bags + pickW at identify", "GearUp": "retired", "UpgPage": "no retired kind row",
             "SkyyGearPlugin": "the migrate0328 call + the version text", "GearLL": "lineCapP + perkEff (the T3 Fortune cap)",
             "GearLife": "capWhy uses lineCapP"}
S328_MAY = {"CfgFn": "config kit: the version", "CfgRows": "config kit: the rows", "CfgFile": "config kit", "CfgDefaults": "config kit: the defaults",
            "CfgKit": "config kit", "CfgPub": "config kit", "IdentifyPage": "the bag panel name", "ReforgePage": "the bag panel name",
            "GearIdPage": "the bag panel name", "AnvilPage": "the bag panel name"}

# ---- the 0.3.27 harness as a library (it loads the older ones). Literals 0.3.28 changes on purpose are moved in the OLDER children's sources
# through a hook on the library loader (each move is asserted to hit).
H327_MOVE = []
if not STATIC:
    _H327 = os.path.join(HERE, "test_skyygear_0.3.27.py")
    _T327 = open(_H327, encoding="utf-8").read()
    _cut = _T327.rindex('if __name__ == "__main__":')
    _T327 = _T327[:_cut]
    for _a, _b in H327_MOVE:
        assert _T327.count(_a) == 1, _a
        _T327 = _T327.replace(_a, _b)
    _argv = sys.argv
    _only = arg("--only")
    if _only:
        _only = ",".join(sorted(set(("h319" if x == "h328" else x) for x in _only.split(","))))
    sys.argv = [_H327, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--only", _only] if _only else []) + (["--out", arg("--out")] if arg("--out") else [])
    H327 = {"__name__": "skyygear_h327", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T327, _H327 + " (library, 0.3.28)", "exec"), H327)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = ",".join(sorted(set(("h319" if x in ("h321", "h322", "h323", "h325", "h326", "h327") else x) for x in _only.split(","))))
    H326 = H327["H326"]
    H325 = H326["H325"]
    H323, H320, H319, H316 = H325["H323"], H325["H320"], H325["H319"], H325["H316"]
    for _h in (H327, H326, H325, H323, H323["H322"], H323["H322"]["H321"], H320, H319):
        _h["VERSION"] = VERSION
    FAILS, OKS = H316["FAILS"], H316["OKS"]
    # the older children's literals 0.3.28 changes on purpose: their phase function is recompiled from the moved source into ITS globals
    OLDER_MOVE = [
        ("test_skyygear_0.3.22.py", "_h322", H323["H322"], [
            ('kc(pf == [10.0, 2.0, 2.0, 2.0, 2.0, 2.0] and e0 == "+30 Mining Fortune" and e1 == "+6 Foraging Fortune" and pf7 == 7.0,\n'
             '       "D/E: the pickaxe Mining Fortune +10 a level (lifelong.perkFortune.mining), others 2: %s / %s / %s" % (pf, e0, e1))',
             'kc(pf == [3.0] * 6 and e0 == "+9% Mining Fortune" and e1 == "+9% Foraging Fortune" and pf7 == 7.0,\n'
             '       "D/E (0.3.28 rates): the Mining Fortune row 3 a level, every other kind 3: %s / %s / %s" % (pf, e0, e1))'),
        ]),
    ]
    for _fn, _func, _g, _mv in OLDER_MOVE:
        _src = open(os.path.join(HERE, _fn), encoding="utf-8").read()
        _a = _src.index("\ndef %s(" % _func) + 1
        _b = min(_x for _x in (_src.find("\ndef ", _a + 1), _src.find("\nif not STATIC:", _a + 1)) if _x > 0)
        _body = _src[_a:_b]
        for _o, _n in _mv:
            assert _body.count(_o) == 1, (_fn, _o[:80])
            _body = _body.replace(_o, _n)
        exec(compile("\n" * _src[:_a].count("\n") + _body, os.path.join(HERE, _fn) + " (0.3.28 moves)", "exec"), _g)
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


# ====================================================================================================== S328
def run_assets328():
    ea, eb = entries(J327), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["manifest.json"], "S328: 0.3.27 -> 0.3.28 adds / removes nothing and changes only the manifest "
          "(+ classes): added %s gone %s changed %s" % (added[:4], gone[:4], changed[:6]))
    man = eb["manifest.json"].decode("utf-8", "replace")
    check('"0.3.28"' in man and "FORTUNE: every lifelong tool's Fortune line +3 a level" in man, "S328: the manifest says 0.3.28 + the round")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.27 -> 0.3.28: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S328_MUST) | set(S328_MAY), "S328: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S328_MUST) - set(S328_MAY)))
    check(set(S328_MUST) <= set(chg), "S328: every class the patch edits really changed: unchanged %s" % sorted(set(S328_MUST) - set(chg)))


# ====================================================================================================== H328 (in the h319 child)
def _h328(L, K):
    from jpype import JClass, JString, JInt, JArray, JObject
    P = lambda n: JClass(PKG + n)
    Cfg, apply, FRESH = L["Cfg"], L["apply"], L["FRESH"]
    LL, Tool, LPage, Sck, Unid, Pool, GData, Up = (P("GearLL"), P("GearTool"), P("LifePage"), P("GearSickle"), P("GearUnid"), P("GearPool"),
                                                   P("GearData"), P("GearUp"))
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")

    def kc(cond, what):
        K.check(bool(cond), "H328 " + what)
    apply()
    fresh = str(FRESH)
    pf = Props()
    pf.load(SR(fresh))
    keys = [str(x) for x in Cfg.H28_KEYS]
    old = [str(x) for x in Cfg.H28_OLD]
    new = [str(x) for x in Cfg.H28_NEW]
    # ============================================================== A
    kc(keys == ["lifelong.perkFortune", "lifelong.perkFortune.mining", "armor.fortune.cap"] and old == ["2", "10", "15"] and new == ["3", "3", "100"],
       "A: the migrate0328 table: %s %s %s" % (keys, old, new))
    kc(all(str(pf.getProperty(k)) == n for k, n in zip(keys, new)) and fresh.count(str(Cfg.H28_MARK_ID)) == 1
       and str(pf.getProperty("unid.typeAtIdentify")) == "true", "A: the fresh file holds the new defaults, unid.typeAtIdentify and the marker once")
    kc(float(Cfg.LL_PFORT) == 3.0 and float(Cfg.LL_PFORTM) == 3.0 and float(Cfg.GM_FCAP) == 100.0 and float(Cfg.fcapA()) == 100.0
       and float(Cfg.fcap()) > 1.0e8 and bool(Cfg.UNID_TYPEID),
       "A: after apply - Fortune 3 / 3 a level, armor Fortune cap 100 (no real cap, inside 0.3.27's 0-100), no tool cap, unid.typeAtIdentify on")
    Cfg.GM_FCAP = 0.0
    c0 = float(Cfg.fcapA())
    apply()
    kc(c0 > 1.0e8, "A: armor.fortune.cap 0 parses as no cap (%s)" % c0)
    pk = [float(LL.pfort(JInt(k))) for k in range(len(LL.KIND))]
    kc(all(v == 3.0 for v in pk), "A: GearLL.pfort = 3 for every kind (pickaxe, hatchet, hoe, Harvester / sickle, pole, can): %s" % pk)
    Cfg.GM_FCAP = 12.0
    c12 = float(Cfg.fcapA())
    apply()
    kc(c12 == 12.0, "A: an armor.fortune.cap above 0 still caps (%s)" % c12)
    # ============================================================== B: h28Update
    fl = fresh.split("\n")
    m = str(Cfg.H28_MARK)
    kc(fl.count(m) == 1, "B: the marker line is in the fresh file")
    o27 = []
    for x in fl:
        if x == m:
            continue
        k_ = x.split("=", 1)[0] if "=" in x and not x.startswith("#") else None
        if k_ in keys:
            x = k_ + "=" + old[keys.index(k_)]
        o27.append(x)
    i_m = o27.index("lifelong.perkFortune.mining=10")
    o27[i_m] = "lifelong.perkFortune.mining=10.0"          # number compare: still the old default
    text = "\r\n".join(o27)
    r = Cfg.h28Update(JString(text))
    nt = str(r[0]) if r is not None else ""
    nl = nt.split("\r\n")
    rows = [str(x) for x in r[3]] if r is not None else []
    nm = [x for x in nl if x != m]
    diff = [(a_, b_) for a_, b_ in zip(o27, nm) if a_ != b_]
    kc(r is not None and len(nl) == len(o27) + 1 and len(nm) == len(o27) and [x for x in nl if x.strip()][-1] == m and len(diff) == 3
       and sorted(b_ for a_, b_ in diff) == sorted(k_ + "=" + n_ for k_, n_ in zip(keys, new)) and "\n" not in nt.replace("\r\n", ""),
       "B: h28Update rewrites the 3 untouched old defaults in place (10.0 = 10), CRLF kept, the marker at the END: %s" % diff)
    kc(rows == ["lifelong.perkFortune", "2", "3", "lifelong.perkFortune.mining", "10.0", "3", "armor.fortune.cap", "15", "100"] and "3 rows" in str(r[1]),
       "B: one change-log row per change (key, old as written, new): %s / %s" % (rows, str(r[1]) if r is not None else None))
    kc(Cfg.h28Update(JString(nt)) is None, "B: a second run = null (run-once marker)")
    o2 = list(o27)
    o2[o2.index("lifelong.perkFortune=2")] = "lifelong.perkFortune=5"
    r2 = Cfg.h28Update(JString("\n".join(o2)))
    notes = [str(x) for x in r2[2]] if r2 is not None else []
    kc(r2 is not None and "lifelong.perkFortune=5" in str(r2[0]).split("\n") and len(notes) == 1 and notes[0].startswith("lifelong.perkFortune=5 kept")
       and len(list(r2[3])) == 6 and "\r" not in str(r2[0]), "B: a hand edit kept + noted, the others rewritten, LF file stays LF: %s" % notes)
    o3 = list(o27)
    o3[o3.index("armor.fortune.cap=15")] = "armor.fortune.cap=0"
    r3 = Cfg.h28Update(JString("\r\n".join(o3)))
    n3 = [str(x) for x in r3[2]] if r3 is not None else []
    kc(r3 is not None and "armor.fortune.cap=0" in str(r3[0]).split("\r\n") and len(n3) == 1 and n3[0].startswith("armor.fortune.cap=0 kept"),
       "B: a hand-set armor.fortune.cap=0 is a hand edit - kept + noted: %s" % n3)
    lg = str(Cfg.h28Log(JString("armor.fortune.cap"), JString("15"), JString("0"))).split("\t")
    kc(len(lg) == 8 and lg[1:] == ["SkyyGear 0.3.28", "-", "update", "armor.fortune.cap", "15", "0", "ok"], "B: h28Log = the change-log row: %s" % lg)
    # ============================================================== C: texts + the sickle roll
    fd = dict((v, str(Tool.fdrops(float(v)))) for v in (0, 30, 100, 150, 300, 1010, 21, 199.96, -5))
    want = {0: "1 drop", 30: "1 drop + 30% for a 2nd", 100: "2 drops", 150: "2 drops + 50% for a 3rd", 300: "4 drops",
            1010: "11 drops + 10% for a 12th", 21: "1 drop + 21% for a 2nd", 199.96: "3 drops", -5: "1 drop"}
    kc(fd == want, "C: GearTool.fdrops: %s" % fd)
    e0 = str(LPage.effect(JInt(0), JInt(1), JInt(10)))
    e1 = str(LPage.effect(JInt(1), JInt(1), JInt(50)))
    ep = str(LPage.effect(JInt(int(LL.POLE)), JInt(1), JInt(4)))
    kc(e0 == "+30% Mining Fortune" and e1 == "+150% Foraging Fortune" and ep == "+12% double catch",
       "C: LifePage.effect - pickaxe %r, hatchet %r, pole %r" % (e0, e1, ep))
    r1000 = [int(Sck.roll(1000.0)) for _ in range(50)]
    rg = [int(Sck.roll(50000.0)) for _ in range(5)]
    r150 = [int(Sck.roll(150.0)) for _ in range(4000)]
    mean = sum(r150) / float(len(r150))
    kc(set(r1000) == {10} and set(rg) == {100} and set(r150) == {1, 2} and 1.42 < mean < 1.58 and int(Sck.roll(0.0)) == 0,
       "C: GearSickle.roll - 1000 %% = 10 (no 5 cap), 50000 %% = the 100 stop, 150 %% = 1 + 50 %% of 2 (mean %.3f)" % mean)
    # ============================================================== D: bug 12
    WT = [t for t in range(len(Pool.T_KEY)) if not bool(Pool.T_ARM[t])]
    bags = [Unid.roll(JInt(20), JInt(-1), "mob", "mob", JInt(0), None, JInt(1), JInt(20)) for _ in range(120)]
    bags = [b for b in bags if b is not None]
    wb, ab = [], []
    for b in bags:
        d = Unid.doc(b)
        (ab if bool(Pool.T_ARM[int(Unid.type(d))]) else wb).append((b, d))
    kc(len(wb) > 10 and len(ab) > 10 and all(str(GData.str(d, "grp", "")) == "w" and str(Unid.title(d)) == "Unidentified Weapon" for b, d in wb)
       and all(str(GData.str(d, "grp", "")) == "" and str(Unid.title(d)) != "Unidentified Weapon" for b, d in ab),
       "D: random weapon bags carry grp w + 'Unidentified Weapon', armor bags do not (%d weapon, %d armor)" % (len(wb), len(ab)))
    fb = Unid.roll(JInt(20), JInt(WT[0]), "mob", "mob", JInt(0), None, JInt(1), JInt(20))
    kc(fb is None or str(GData.str(Unid.doc(fb), "grp", "")) == "", "D: a forced-type bag keeps its type (no grp)")
    tys = set()
    okall = True
    for b, d in wb[:12]:
        for _ in range(4):
            o = Unid.open(d, None)
            if o is None:
                okall = False
                continue
            tys.add(int(Pool.typeOfId(str(o[0]))))
    kc(okall and len(tys) >= 3 and all(t in WT for t in tys), "D: open() of grp bags gives weapons of several types (%d types)" % len(tys))
    d0 = wb[0][1]
    lo, hi = int(Unid.lo(d0)), int(Unid.hi(d0))
    cand = [t for t in WT if int(Pool.levelCount(JInt(t), JInt(0), JInt(lo), JInt(hi))) > 0]
    lt = cand[0]
    lean = JArray(JString)([str(Pool.T_KEY[lt])])
    cl0 = Cfg.CLASS_LEAN
    Cfg.CLASS_LEAN = 100
    pl = set(int(Unid.pickW(JInt(-7), JInt(lo), JInt(hi), lean)) for _ in range(60))
    Cfg.CLASS_LEAN = 0
    pn = set(int(Unid.pickW(JInt(-7), JInt(lo), JInt(hi), lean)) for _ in range(200))
    Cfg.CLASS_LEAN = cl0
    none = int(Unid.pickW(JInt(-7), JInt(990), JInt(995), None))
    kc(pl == {lt} and len(pn) >= 2 and pn <= set(cand) and none == -7,
       "D: pickW - lean 100 %% = only the lean type %s, lean 0 = any candidate (%d), no candidate = the stored type" % (pl, len(pn)))
    od = d0.clone()
    od.remove("grp")
    st = int(Unid.type(od))
    ot = set(int(Pool.typeOfId(str(Unid.open(od, None)[0]))) for _ in range(6))
    kc(ot == {st} and str(Unid.title(od)) == "Unidentified " + str(Unid.typeName(st)), "D: an old bag (no grp) opens as its stored type %s: %s" % (st, ot))
    Cfg.UNID_TYPEID = False
    off = (str(Unid.title(d0)), set(int(Pool.typeOfId(str(Unid.open(d0, None)[0]))) for _ in range(6)))
    apply()
    kc(Unid.why(d0) is None and Unid.why(od) is None, "D: why() lets a grp bag and an old bag open")
    kc(off[0] == "Unidentified " + str(Unid.typeName(int(Unid.type(d0)))) and off[1] == {int(Unid.type(d0))},
       "D: unid.typeAtIdentify=false - the stored type's name + item: %s" % (off,))
    # ============================================================== E: bug 17
    hp = str(L.get("HARV_PRE") or "Tool_Sickle_Harvester_")
    ret = [bool(Up.retired(x)) for x in ("Tool_Hoe_Crude", "Tool_Hoe_Iron", "Tool_Sickle_Crude", "Tool_Sickle_Copper", hp + "Crude", hp + "Iron",
                                         "Tool_Pickaxe_Crude", "Tool_Hatchet_Iron", None)]
    Cfg.HARV_ONLY = False
    roff = bool(Up.retired("Tool_Hoe_Crude"))
    apply()
    kc(ret == [True, True, True, True, False, False, False, False, False] and not roff and bool(Cfg.HARV_ONLY),
       "E: GearUp.retired - hoes / sickles yes, Harvesters / pickaxes / hatchets no; harvester.only off = none: %s %s" % (ret, roff))
    # ============================================================== F: the T3 Fortune cap (Bronze 33 = 99 %, Thorium 40)
    def caps(k, iid):
        pp = Props()
        pp.setProperty(str(LL.KIND[k]) + ".id", iid)
        return (int(LL.lineCapP(pp, JInt(k), JInt(1))), int(LL.lineCapP(pp, JInt(k), JInt(0))), int(LL.lineCap(pp, JInt(k))))
    cs = dict((iid, caps(k, iid)) for k, iid in ((0, "Tool_Pickaxe_Bronze_SkyWynn"), (1, "Tool_Hatchet_Bronze_SkyWynn"), (0, "Tool_Pickaxe_Thorium"),
                                                 (0, "Tool_Pickaxe_Iron"), (0, "Tool_Pickaxe_Copper"), (0, "Tool_Pickaxe_Crude")))
    kc(cs["Tool_Pickaxe_Bronze_SkyWynn"] == (33, 40, 40) and cs["Tool_Hatchet_Bronze_SkyWynn"] == (33, 40, 40)
       and cs["Tool_Pickaxe_Thorium"] == (40, 40, 40) and cs["Tool_Pickaxe_Iron"] == (30, 30, 30) and cs["Tool_Pickaxe_Copper"] == (20, 20, 20)
       and cs["Tool_Pickaxe_Crude"] == (10, 10, 10),
       "F: Fortune line caps - Bronze 33 (= 99 %% at 3 a level; its other lines 40), Thorium 40, Iron 30, Copper 20, Crude 10: %s" % cs)
    pb = Props()
    pb.setProperty(str(LL.KIND[0]) + ".id", "Tool_Pickaxe_Bronze_SkyWynn")
    pb.setProperty(str(LL.KIND[0]) + ".up." + str(LL.PK[1]), "40")
    kc(int(LL.perkEff(None, pb, JInt(0), JInt(1))) == 33 and int(LL.perkOf(pb, JInt(0), JInt(1))) == 40,
       "F: a Bronze pickaxe holding 40 Fortune levels keeps them saved, 33 work (99 %%)")
    print("  note (h328): A-F ran - fdrops %s; %d weapon / %d armor bags, %d weapon types at identify" % (fd[150], len(wb), len(ab), len(tys)))


if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h328(L, K):
        _h319_prev(L, K)
        try:
            _h328(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H328: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h328
    H320["run_assets320"] = run_assets328          # the jar compare of THIS round (0.3.27 -> 0.3.28)
    H320["J319"] = J327


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
            for _m in ("tier_tags.py", "skyyench.py", "skyyeggs.py"):
                shutil.copyfile(os.path.join(TOOLS, _m), os.path.join(r, "tools", _m))
            shutil.copyfile(GEN327, os.path.join(r, "SkyyGear", os.path.basename(GEN327)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.28.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.28.py (the committed file is the patch's output)")
        src = open(GEN327, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.28.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.28"\n' in s and "GENERATED by tools/gear_0_3_28_patch.py" in s, "A: VERSION 0.3.28 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean h7Old(") < i("public static Object[] h28Update(") < i("public static String h28Log(") < i("public static synchronized String migrate0328()")
              < i("  @PKG@.GearCfg.migrate0328();") and i("  @PKG@.GearCfg.migrate0327();") < i("  @PKG@.GearCfg.migrate0328();"),
              "A: helpers before their callers (javassist order); migrate0328 runs after migrate0327")
        check(i("public static String fdrops(double f)") < i("public static void mlines(") and s.count("fdrops(") >= 5
              and "% extra log chance" not in s and "if (x > 5.0) x = 5.0;" not in s,
              "A: fdrops before its callers; the old 'extra ... chance' texts and the 5-drop cap are gone")
        check(i("public static boolean retired(String id)") < i("next(it.getItemId()) == null || retired(it.getItemId())")
              and i("public static int pickW(") < i("if (grpW(d)) ty = pickW(") and i("public static @IS@ grouped(") < i("public static @IS@ roll(int L, int forceType"),
              "A: GearUp.rows skips retired ids; GearUnid.open picks a grp bag's weapon type; grouped before roll")
        check(i("public static int lineCap(java.util.Properties P, int k)") < i("public static int lineCapP(") < i("public static int perkEff(")
              and s.count("lineCapP(P, k, p)") == 3 and s.count('nx = "Next: +" + @PKG@.Gear.fnum(fv) + "% = " + @PKG@.GearTool.fdrops(fv)') == 1
              and "typeName(ty).toLowerCase() + \" exists in" not in s and s.count("if (!grpW(d) && fit(ty, at(d), lo(d), hi(d)) == null)") == 1
              and "the rest a chance; at most 5\n" not in s, "A: lineCapP after lineCap, before perkEff; perkEff / capWhy / the Upgrade page use it; the Next line carries the drop math; why() never names a hidden type")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    assert os.path.isfile(J327), J327
    H320["main"]()


if __name__ == "__main__":
    main()
