"""Harness for SkyyGear 0.3.27 (tools/gear_0_3_27_patch.py header = Untiered at the zone's alloy band, from dungeons / mini bosses / elites only)
= the 0.3.26 harness (and through it the whole older chain) run on the 0.3.27 jar + S327 (the jar compare 0.3.26 -> 0.3.27, replacing S326) + H327
(inside the h319 child, after H319 .. H326, on the same booted engine), plus a --static phase (no jar):
    python tools/gear_0_3_27_patch.py && python SkyyGear/build_skyygear_0.3.27.py
    python SkyyGear/test_skyygear_0.3.27.py [--keep] [--only assets,h319,...]
    python SkyyGear/test_skyygear_0.3.27.py --static [--keep]

  The 0.3.26 harness runs with ITS band literals moved to the 0.3.27 bands (H326 A: Rook / Armory rows 15,29 -> 15,23, Hepta_Axe 45,59 -> 39,47);
  every other 0.3.26 check is unchanged.
  STATIC (--static)
       G  the patch run TWICE in a scratch tree -> byte-identical, = SkyyGear/build_skyygear_0.3.27.py, compiles, line endings kept
       A  the anchors: VERSION; no new system / command / class; h27Update / h27Log / migrate0327 after h23Old and migrate0326, before the setup
          call; GearUt.source before swap / mobRoll; the 5-argument chestExtra before the 0.2.11 one; the call site passes dl + wk
  S327 the jar 0.3.26 -> 0.3.27: adds / removes nothing; changes only manifest.json + the classes S327_MUST / S327_MAY
  H327 (the h319 child, ONE booted engine) - real code:
       A  the fresh file: every Untiered row at its zone's alloy band (40 rows; first batch + 17 Armory 15-23, Hepta_Axe 39-47), luggage 0 0 0 0,
          utdrop.dungeon, the migrate0327 marker once; after a config apply GearCfg.UTAB / UT_LUG / UT_DUNG hold them
       B  GearUt.source: elites / mini bosses 1 (boss words win), Dungeon_ roles / instance- and dungeon_ worlds / Portals_ + Coffer_ lists 2,
          normal mobs / chests / bosses 0, blank list = no dungeon; the REAL GearLoot.chestExtra at 100 %: orange only for a dungeon list / world,
          the 0.2.11 3-argument call never orange; the REAL gear:fn:box luggage at the new default never orange
       C  h27Update on a 0.3.26-shaped file: the 41 old defaults rewritten in place (value text only, CRLF kept, nothing else changes), a hand
          edit kept + noted, the marker at the END, 41 change-log rows (ut[X] 15|29|.. -> 15|23|..); a second run = null; a 0.3.25 file (u26Update
          first) gets no note for the Armory rows; h27Log = the change-log row (Undo-able)
  NOT COVERED (smoke test / Skyy in game): migrate0327 on the real config.properties, the REAL mobRoll role read (GearDeathMark on a real dying
  NPC), real dungeon mobs (instance worlds need a SkyyMobs level band to roll any bag at all).
Scratch: tools/dev/scratch/g327/h327/gear/harness (full run) and .../h327/static (--static), deleted at the end unless --keep.
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


VERSION = "0.3.27"
V326 = "0.3.26"
SCR_BASE = os.path.join(TOOLS, "dev", "scratch", "g327", "h327")
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(SCR_BASE, "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J326 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V326))                       # read only
PKG = "com.skyy.gear."
PATCH = os.path.join(TOOLS, "gear_0_3_27_patch.py")
GEN = os.path.join(HERE, "build_skyygear_0.3.27.py")
GEN326 = os.path.join(HERE, "build_skyygear_0.3.26.py")

S327_MUST = {"GearCfg": "H27_ rows + h27Update / h27Log / migrate0327 + UT_DUNG", "GearUt": "dgStart / roleWord / source + the drops text",
             "GearLoot": "mobRoll / chestExtra read the source", "GearChestTag": "the chestExtra call passes dl + wk",
             "SkyyGearPlugin": "the migrate0327 call + the version text"}
S327_MAY = {"CfgFn": "config kit: the version", "CfgRows": "config kit: the rows", "CfgFile": "config kit", "CfgDefaults": "config kit: the defaults",
            "CfgKit": "config kit", "CfgPub": "config kit"}

# ---- the 0.3.26 harness as a library (it loads the older ones); its children run on THIS jar in THIS scratch folder (and THIS file). Its H326 A
# band literals move to the 0.3.27 bands (exactly these, each once) - everything else it checks is unchanged.
H326_MOVE = [
    ('kc(ut["RookHelmGhost"] == "15,29,Hollow guard', 'kc(ut["RookHelmGhost"] == "15,23,Hollow guard'),
    ('and ut["Hepta_Axe"] == "45,59,Hits 54% harder.', 'and ut["Hepta_Axe"] == "39,47,Hits 54% harder.'),
    ('lv[i] == ((45, 59) if i == "Hepta_Axe" else (15, 29))', 'lv[i] == ((39, 47) if i == "Hepta_Axe" else (15, 23))'),
    ('Armory ids (15-29, Hepta_Axe 45-59) next to', 'Armory ids (0.3.27 bands 15-23, Hepta_Axe 39-47) next to'),
]
if not STATIC:
    _H326 = os.path.join(HERE, "test_skyygear_0.3.26.py")
    _T326 = open(_H326, encoding="utf-8").read()
    _cut = _T326.rindex('if __name__ == "__main__":')
    _T326 = _T326[:_cut]
    for _a, _b in H326_MOVE:
        assert _T326.count(_a) == 1, _a
        _T326 = _T326.replace(_a, _b)
    _argv = sys.argv
    _only = arg("--only")
    if _only:
        _only = ",".join(sorted(set(("h319" if x == "h327" else x) for x in _only.split(","))))
    sys.argv = [_H326, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH] + [a for a in _argv[1:] if a in ("--keep", "--h319")] + \
        (["--only", _only] if _only else []) + (["--out", arg("--out")] if arg("--out") else [])
    H326 = {"__name__": "skyygear_h326", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    exec(compile(_T326, _H326 + " (library, 0.3.27 bands)", "exec"), H326)
    sys.argv = _argv
    if _only:
        sys.argv[sys.argv.index("--only") + 1] = ",".join(sorted(set(("h319" if x in ("h321", "h322", "h323", "h325", "h326") else x) for x in _only.split(","))))
    H325 = H326["H325"]
    H323, H320, H319, H316 = H325["H323"], H325["H320"], H325["H319"], H325["H316"]
    for _h in (H326, H325, H323, H323["H322"], H323["H322"]["H321"], H320, H319):
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


# ====================================================================================================== S327
def run_assets327():
    ea, eb = entries(J326), entries(JAR)
    added, gone = sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(not added and not gone and changed == ["manifest.json"], "S327: 0.3.26 -> 0.3.27 adds / removes nothing and changes only the manifest "
          "(+ classes): added %s gone %s changed %s" % (added[:4], gone[:4], changed[:6]))
    man = eb["manifest.json"].decode("utf-8", "replace")
    check('"0.3.27"' in man and "UNTIERED SOURCES: each zone's Untiered items sit at its alloy band" in man, "S327: the manifest says 0.3.27 + the round")
    ca = set(n for n in ea if n.endswith(".class"))
    chg = sorted(n.rsplit("/", 1)[1][:-6] for n in ca if ea[n] != eb.get(n))
    print("  class compare 0.3.26 -> 0.3.27: %d classes, %d changed (%s)" % (len(ca), len(chg), ", ".join(chg)))
    check(set(chg) <= set(S327_MUST) | set(S327_MAY), "S327: only the patched classes changed: unexpected %s" % sorted(set(chg) - set(S327_MUST) - set(S327_MAY)))
    check(set(S327_MUST) <= set(chg), "S327: every class the patch edits really changed: unchanged %s" % sorted(set(S327_MUST) - set(chg)))


# ====================================================================================================== H327 (in the h319 child)
def _h327(L, K):
    from jpype import JClass, JString, JInt, JShort, JArray, JObject
    P = lambda n: JClass(PKG + n)
    Cfg, apply, FRESH = L["Cfg"], L["apply"], L["FRESH"]
    Ut, Loot, BoxFn = P("GearUt"), P("GearLoot"), P("GearBoxFn")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    UUID = JClass("java.util.UUID")

    def kc(cond, what):
        K.check(bool(cond), "H327 " + what)
    apply()
    fresh = str(FRESH)
    pf = Props()
    pf.load(SR(fresh))
    keys = [str(x) for x in Cfg.H27_KEYS]
    old = [str(x) for x in Cfg.H27_OLD]
    new = [str(x) for x in Cfg.H27_NEW]
    # ============================================================== A: the fresh file + the loaded table
    uts = [k for k in keys if k.startswith("ut.")]
    kc(len(keys) == 41 and len(uts) == 40 and keys[-1] == "utdrop.luggage" and new[-1] == "0 0 0 0" and old[-1] == "1 2 4 8",
       "A: 41 migrate0327 rows (40 Untiered + luggage)")
    kc(all(str(pf.getProperty(k)) == n for k, n in zip(keys, new)) and fresh.count(str(Cfg.H27_MARK_ID)) == 1
       and str(pf.getProperty("utdrop.dungeon")) == "Dungeon_,instance-,Portals_,Coffer_",
       "A: the fresh file holds every new default, utdrop.dungeon and the marker once")
    bands = dict((k[3:], tuple(int(x) for x in str(pf.getProperty(k)).split(",")[:2])) for k in uts)
    kc(bands["Hepta_Axe"] == (39, 47) and all(v == (15, 23) for i, v in bands.items() if i != "Hepta_Axe") and len(bands) == 40,
       "A: every Zone 1 row at the Bronze band 15-23, Hepta_Axe (Zone 4) at the Cinder band 39-47: %s" % sorted(set(bands.values())))
    t = Cfg.UTAB
    tid = [str(x) for x in t[0]]
    lv = dict((tid[k], (int(t[1][k]), int(t[2][k]))) for k in range(len(tid)))
    kc(all(lv.get(i) == b for i, b in bands.items()) and str(Cfg.UT_LUG) == "0 0 0 0" and str(Cfg.UT_DUNG) == "Dungeon_,instance-,Portals_,Coffer_",
       "A: after apply GearCfg.UTAB holds the 40 rows at their bands; UT_LUG 0 0 0 0; UT_DUNG")
    # ============================================================== B: the sources
    cases = [(("w", "Skeleton_Elite", None), 1), (("w", "Golem_Frost", None), 1), (("w", "Yeti", None), 1), (("w", "Golem_Guardian_Void", None), 0),
             (("w", "Goblin_Duke", None), 0), (("w", "Trork_Chieftain", None), 0), (("w", "Trork_Warrior", None), 0), (("w", "Eliteish_Wolf", None), 0),
             (("w", "Dungeon_Goblin_Scrapper", None), 2), (("w", "dungeon_feastmaster_boss", None), 2), (("instance-Forgotten_Temple-1a2b", "Trork_Warrior", None), 2),
             (("dungeon_1", "Skeleton", None), 2), (("w", None, "Portals_Goblin_Chest_Tier1"), 2), (("w", None, "Coffer_Goblin_Loot_Wave3"), 2),
             (("w", None, "Zone1_Undead_Tier1"), 0), (("skyy-island-abc", None, "Zone1_Encounters_Tier1"), 0), ((None, None, None), 0), (("", "", ""), 0)]
    got = [(c, int(Ut.source(*c))) for c, _w in cases]
    bad = [(c, g, w) for (c, g), (_c, w) in zip(got, cases) if g != w]
    kc(not bad, "B: GearUt.source - elites / mini bosses 1 (boss words win), dungeon roles / worlds / chest lists 2, the rest 0: wrong %s" % bad[:4])
    Cfg.UT_DUNG = " , "
    b2 = (int(Ut.source("instance-x", "Dungeon_Goblin_Scrapper", "Portals_Oasis")), int(Ut.source("w", "Skeleton_Elite", None)))
    apply()
    kc(b2 == (0, 1), "B: a blank utdrop.dungeon = no dungeon source (elites still 1): %s" % (b2,))
    # the REAL chestExtra at 100 % (extra bag + orange share)
    Cfg.LOOT_CHEST = True
    Cfg.LOOT_CHEST_PCT = 100.0
    Cfg.UT_CHEST = 100.0

    def chest(*a):
        c = SIC(JShort(3))
        n = int(Loot.chestExtra(c, JInt(20), "h327", *a))
        return n, [str(c.getItemStack(JShort(i)).getItemId()) for i in range(3) if c.getItemStack(JShort(i)) is not None and not c.getItemStack(JShort(i)).isEmpty()]
    OR = "Skyy_Unid_Bag_Untiered"
    cx = [chest("Portals_Goblin_Chest_Tier1", "w"), chest(None, "instance-Forgotten_Temple-1"), chest("Zone1_Undead_Tier1", "w"), chest()]
    apply()
    kc(cx[0][1] == [OR] and cx[1][1] == [OR] and len(cx[2][1]) == 1 and cx[2][1][0] != OR and len(cx[3][1]) == 1 and cx[3][1][0] != OR,
       "B: the REAL chestExtra at 100 %%: orange for a Portals_ list / an instance- world, a normal bag for a Zone1_Undead chest and the 0.2.11 call: %s" % cx)
    # the REAL gear:fn:box luggage at the new default (0 0 0 0) never turns orange; at 100 it still can (the row works)
    bx = BoxFn()
    U1 = L["U1"]

    def lug(tier, n):
        o_ = 0
        for _ in range(n):
            b_ = bx.apply(JArray(JObject)([None, JInt(20), "lootchest", JInt(tier), U1]))
            if b_ is not None and str(b_.getItemId()) == OR:
                o_ += 1
        return o_
    l0 = [lug(t_, 500) for t_ in (1, 2, 3, 4)]
    Cfg.UT_LUG = "100 100 100 100"
    l1 = lug(4, 3)
    apply()
    kc(l0 == [0, 0, 0, 0] and l1 == 3, "B: luggage at 0 0 0 0 never orange (%s over 500 each); at 100 %% still orange (%d / 3)" % (l0, l1))
    # ============================================================== C: h27Update
    fl = fresh.split("\n")
    m = str(Cfg.H27_MARK)
    kc(fl.count(m) == 1, "C: the marker line is in the fresh file")
    o26 = []
    for x in fl:
        if x == m:
            continue
        k_ = x.split("=", 1)[0] if "=" in x and not x.startswith("#") else None
        if k_ in keys:
            x = k_ + "=" + old[keys.index(k_)]
        o26.append(x)
    o26 = [x for x in o26]
    i_pw = o26.index("ut.Weapon_Sword_UT_Paperweight=" + old[keys.index("ut.Weapon_Sword_UT_Paperweight")])
    o26[i_pw] = "ut.Weapon_Sword_UT_Paperweight=15,20,Mine"
    text = "\r\n".join(o26)
    r = Cfg.h27Update(JString(text))
    nt = str(r[0]) if r is not None else ""
    nl = nt.split("\r\n")
    notes = [str(x) for x in r[2]] if r is not None else []
    rows = [str(x) for x in r[3]] if r is not None else []
    nm = [x for x in nl if x != m]
    diff = [(a_, b_) for a_, b_ in zip(o26, nm) if a_ != b_]
    kc(r is not None and len(nl) == len(o26) + 1 and len(nm) == len(o26) and [x for x in nl if x.strip()][-1] == m and len(diff) == 40 and all(a_.split("=", 1)[0] == b_.split("=", 1)[0] for a_, b_ in diff)
       and all(b_ == k_ + "=" + new[keys.index(k_)] for a_, b_ in diff for k_ in [b_.split("=", 1)[0]]) and "\n" not in nt.replace("\r\n", ""),
       "C: h27Update rewrites the 40 untouched old defaults in place, CRLF kept, the marker at the END, nothing else changes (%d diffs)" % len(diff))
    kc(nl[i_pw] == "ut.Weapon_Sword_UT_Paperweight=15,20,Mine" and len(notes) == 1 and notes[0].startswith("ut.Weapon_Sword_UT_Paperweight=15,20,Mine kept"),
       "C: a hand-edited row is kept + noted: %s" % notes[:2])
    kc(len(rows) == 120 and rows[0].startswith("ut[") and rows[1].startswith("15|29|") and rows[2].startswith("15|23|")
       and ["utdrop.luggage", "1 2 4 8", "0 0 0 0"] == rows[-3:] and ("ut[Hepta_Axe]" in rows and rows[rows.index("ut[Hepta_Axe]") + 1].startswith("45|59|")
                                                                     and rows[rows.index("ut[Hepta_Axe]") + 2].startswith("39|47|")),
       "C: one change-log row per change (key[entry], the columns joined by |): %s" % rows[:3])
    kc("40 rows" in str(r[1]) and "luggage" in str(r[1]), "C: the change summary: %s" % (str(r[1]) if r is not None else None))
    kc(Cfg.h27Update(JString(nt)) is None, "C: a second run = null (run-once marker)")
    # a 0.3.25 file: u26Update first (it adds the Armory rows at the NEW band) -> h27Update notes none of them
    zl = [x for x in o26]
    zl[i_pw] = "ut.Weapon_Sword_UT_Paperweight=" + old[keys.index("ut.Weapon_Sword_UT_Paperweight")]
    hi = zl.index(str(Cfg.U26_HEAD))
    blk = 2 + sum(int(x) for x in Cfg.U26_GS) + len(Cfg.U26_GC)
    t25 = "\r\n".join(x for k, x in enumerate(zl) if not (hi - 1 <= k < hi + blk))
    r25 = Cfg.u26Update(JString(t25))
    r27 = Cfg.h27Update(JString(str(r25[0]))) if r25 is not None else None
    p27 = Props()
    if r27 is not None:
        p27.load(SR(str(r27[0])))
    kc(r27 is not None and len(list(r27[2])) == 0 and len(list(r27[3])) == 3 * 23 and all(str(p27.getProperty(k)) == n for k, n in zip(keys, new)),
       "C: a 0.3.25 file (u26Update, then h27Update): the 22 first-batch rows + luggage rewritten, the 18 new Armory rows already right, no note: %s"
       % ([str(x) for x in r27[2]][:2] if r27 is not None else None))
    lg = str(Cfg.h27Log(JString("ut[GhostSword]"), JString("15|29|x"), JString("15|23|x"))).split("\t")
    kc(len(lg) == 8 and lg[1:] == ["SkyyGear 0.3.27", "-", "update", "ut[GhostSword]", "15|29|x", "15|23|x", "ok"], "C: h27Log = the change-log row: %s" % lg)
    print("  note (h327): A + B + C ran - %d source cases, chests %s, luggage %s, %d rewrites" % (len(cases), [c_[1] for c_ in cx], l0, len(rows) // 3))


if not STATIC:
    _h319_prev = H319["_h319"]

    def _h319_to_h327(L, K):
        _h319_prev(L, K)
        try:
            _h327(L, K)
        except Exception:
            import traceback
            traceback.print_exc()
            K.check(False, "H327: the phase raised: %s" % traceback.format_exc()[-1800:])
    H319["_h319"] = _h319_to_h327
    H320["run_assets320"] = run_assets327          # the jar compare of THIS round (0.3.26 -> 0.3.27)
    H320["J319"] = J326


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
            shutil.copyfile(GEN326, os.path.join(r, "SkyyGear", os.path.basename(GEN326)))
            p = os.path.join(r, "tools", os.path.basename(PATCH))
            pr = subprocess.run([sys.executable, "-B", "-c",
                                 "import sys\nsys.dont_write_bytecode = True\np = sys.argv[1]\n"
                                 "g = {'__name__': '__main__', '__file__': p}\nexec(compile(open(p, encoding='utf8').read(), p, 'exec'), g)\n", p],
                                capture_output=True, text=True)
            check(pr.returncode == 0, "G: the patch runs in a scratch tree (run %d): %s" % (k, (pr.stderr or "")[-600:]))
            f = os.path.join(r, "SkyyGear", "build_skyygear_0.3.27.py")
            outs.append(open(f, "rb").read() if os.path.isfile(f) else b"")
        check(outs[0] and outs[0] == outs[1], "G: two runs give byte-identical scripts (deterministic)")
        if os.path.isfile(GEN):
            check(outs[0] == open(GEN, "rb").read(), "G: = SkyyGear/build_skyygear_0.3.27.py (the committed file is the patch's output)")
        src = open(GEN326, "rb").read()
        check((b"\r\n" in src) == (b"\r\n" in outs[0]), "G: the source's line endings are kept")
        s = outs[0].decode("utf8").replace("\r\n", "\n")
        try:
            compile(s, "build_skyygear_0.3.27.py", "exec")
            check(True, "G")
        except SyntaxError as e:
            check(False, "G: the generated script compiles: %s" % e)
        s0 = src.decode("utf8").replace("\r\n", "\n")
        check('VERSION = "0.3.27"\n' in s and "GENERATED by tools/gear_0_3_27_patch.py" in s, "A: VERSION 0.3.27 + the GENERATED header")
        check(s.count("registerSystem(") == s0.count("registerSystem(") and s.count("registerCommand(") == s0.count("registerCommand(")
              and s.count(' = mk("') == s0.count(' = mk("'), "A: no new system, command or class")
        i = s.index
        check(i("public static boolean h23Old(") < i("public static Object[] h27Update(") < i("public static String h27Log(") < i("public static synchronized String migrate0327()")
              < i("  @PKG@.GearCfg.migrate0327();") and i("  @PKG@.GearCfg.migrate0326();") < i("  @PKG@.GearCfg.migrate0327();"),
              "A: helpers before their callers (javassist order); migrate0327 runs after migrate0326")
        check(i("public static int source(String world") < i("public static @IS@ swap(") < i("public static int mobRoll(")
              and i("public static int chestExtra(@IC@ c, int L, String where, String dl, String wk)") < i("public static int chestExtra(@IC@ c, int L, String where) {")
              and s.count("@PKG@.GearLoot.chestExtra(icb.getItemContainer(), lvl, where, dl, wk);") == 1
              and s.count("GearUt.source(wk, rn, null) > 0") == 1 and s.count("GearUt.source(wk, null, dl) > 0") == 1,
              "A: GearUt.source before its callers; mobRoll + chestExtra gate the orange swap; the chest call passes dl + wk")
        check(s.count('L += ["", G327_HEAD]') == 1 and "UT_LO, UT_HI = 15, 29" not in s and 'U26_ROWS.append(("Hepta_Axe", UT_BANDS[4][0], UT_BANDS[4][1],' in s,
              "A: the fresh block once; the bands come from the alloy rows")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(base, ignore_errors=True)
    print("STATIC %s: %d ok, %d failed" % ("PASS" if not FAILS else "FAIL", OKS[0], len(FAILS)))
    return 0 if not FAILS else 1


# ====================================================================================================== main
def main():
    if STATIC:
        sys.exit(run_static())
    assert os.path.isfile(J326), J326
    H320["main"]()


if __name__ == "__main__":
    main()
