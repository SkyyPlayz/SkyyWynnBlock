"""Bare-JVM check for SkyyGear 0.2.7 (the Charged-hit trust list for OUR OWN crossbows: SkyyArmory 0.1.3's Weapon_Crossbow_Copper_Wynn /
Weapon_Crossbow_Onyxium_Wynn, Skyy LOCKED "Copper + Onyxium (Recommended)", docs/answered/gear.md). The 0.2.6 harness
(SkyyGear/test_skyygear_0.2.6.py, read only: every 0.1 ... 0.2.6 section) runs on the 0.2.7 jar with VERSION 0.2.7 and the new section AH.

    python SkyyGear/test_skyygear_0.2.7.py [--jar <SkyyGear-0.2.7.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

The carried Z3 / Z4 / Z5 engine model (the build's Python walk vs the JAR's engine walk over real interaction objects) now also carries the two
own crossbows, read from SkyyArmory/SkyyArmory-0.1.3.jar (read only) like the build reads them: the trust list check, the per-calculator walk
compare, the runtime eligibility == the baked FALLBACK and the crossbow family row (2 vanilla + 4 pack + 2 own) all include them.
  AH 0.2.7 - every new path EXECUTED:
     AH1 (inside the Z4 model) each own crossbow's 3rd bolt (Hytale's Class Charged combo, no hold) judged by the REAL GearChg.judgeCalc
         counts exactly like the Iron crossbow's (melee call + as the projectile hit it is), trusted() / hasCharged() true; the SAME combo
         calculator on a look-alike unknown id (Weapon_Crossbow_Copper_Wynn_Copy: the Copper crossbow's chains under a modded id) and on
         the loose-tagged modded sword is still "untrusted - ignored" and never rolls;
     AH2 the jar's lists: TRUST = vanilla + pack + own (own exactly the two), FALLBACK has both, PARTIAL neither; Charged Attack Damage
         may roll on both (Roll.pool); levels: GearLevel.band = Copper 10-18 / Onyxium 40-49, both gear, family base the Iron crossbow;
     AH3 start twice on a scratch COPY of the live Skyy_SkyyGear folder (the whole setup() file chain twice, no change the second time);
     AH4 the class byte-compare 0.2.6 -> 0.2.7 (every difference listed) + the non-class entries (only manifest.json).
Scratch: only under --dir (default tools/dev/scratch/gear027/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H26 = os.path.join(HERE, "test_skyygear_0.2.6.py")
_t26 = open(H26, encoding="utf-8").read()
_cut = _t26.rindex('_g = {"__name__": "__main__"')
_n26 = {"__name__": "skyygear_h26", "__file__": H26, "__builtins__": __builtins__}
exec(compile(_t26[:_cut], H26 + " (the 0.2.6 harness text, not run)", "exec"), _n26)
src = _n26["src"]
DEV26 = _n26["DEV25"] + _n26["DEVIATIONS26"]


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


_GONE = "the historical jar is no longer on disk (old builds removed by tools/tidy_local.py; git-ignored) - a past compare, AH4 compares 0.2.6 -> 0.2.7"
DEVIATIONS27 = [
    ("AA9: SkyyGear-0.1.2.jar / SkyyGear-0.1.3.jar not found", _GONE),
    ("AB9: SkyyGear-0.1.3.jar / SkyyGear-0.2.jar not found", _GONE),
    ("AC10: SkyyGear-0.2.jar not found", _GONE),
    ("AD10: SkyyGear-0.2.1.jar (or the compare helper) not found", _GONE),
    ("AE10: SkyyGear-0.2.2.jar (or the compare helper) not found", _GONE),
    ("AG10: no difference outside the listed 0.2.6 parts", "the historical 0.2.5 -> 0.2.6 compare against the 0.2.7 jar: GearChg's TRUST / "
     "FALLBACK arrays (<clinit>: + the two own crossbows) differ too - AH4 compares 0.2.6 -> 0.2.7"),
]
OWN = ["Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Onyxium_Wynn"]

sub('VERSION = "0.2.6"\nDEVIATIONS = %r' % (DEV26,), 'VERSION = "0.2.7"\nDEVIATIONS = %r' % (DEV26 + DEVIATIONS27,))
sub('os.path.join(TOOLS, "dev", "scratch", "gear026", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "gear027", "harness")')
sub('print("DEVIATION (0.2.5/0.2.6, expected):"', 'print("DEVIATION (0.2.5/0.2.6/0.2.7, expected):"')
sub('expected 0.2.5 / 0.2.6 deviations (%d listed kinds seen)', 'expected 0.2.5 / 0.2.6 / 0.2.7 deviations (%d listed kinds seen)')

# ---- the class-compare helper (Z10) is defined even when the historical 0.1.1 / 0.1.2 jars are gone from disk (tools/tidy_local.py
# removes old builds), so AF10 / AG10 / AH4 - whose jars ARE there - can run; the Z10 compare itself still needs both old jars
sub('''    if os.path.isfile(jar011) and os.path.isfile(jar012z):
        def cls_members(p_, cn):''', '''    if True:            # 0.2.7 harness: the helper always exists (see the patch note in test_skyygear_0.2.7.py)
        def cls_members(p_, cn):''')
sub('''            return mem

        pa = Pool(False)
        pa.appendClassPath(jar011)''', '''            return mem

    if os.path.isfile(jar011) and os.path.isfile(jar012z):
        pa = Pool(False)
        pa.appendClassPath(jar011)''')
# AD3: SkyyArmory 0.1.3 (the SET pin since 2026-10-06 20:15) ships 17 weapon item files (15 + the two Wynn crossbows)
sub('''overr_.get("SkyyArmory", 0) == 15,''', '''overr_.get("SkyyArmory", 0) == 17,''')
# AG0: the fresh file's header carries the running version
sub('''check(dt6.startswith("# SkyyGear 0.2.6 - ")''', '''check(dt6.startswith("# SkyyGear %s - " % VERSION)''')

# ---- Z3: the walk model also carries our own crossbows (read from SkyyArmory's release jar, read only - the build's first source)
sub('''    WK = AzWalker(azz, azz.namelist(), mct)
''', '''    WK = AzWalker(azz, azz.namelist(), mct)
    # 0.2.7: our own SkyyArmory crossbows join the model as overlays (the build reads the same jar first)
    OWNI = %r
    ownd = {}
    with _zf.ZipFile(os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.3.jar")) as zo_:
        for n_ in zo_.namelist():
            if n_.startswith("Server/Item/Items/") and n_.endswith(".json") and os.path.basename(n_)[:-5] in OWNI:
                ownd[os.path.basename(n_)[:-5]] = json.loads(zo_.read(n_).decode("utf-8-sig"))
    check(sorted(ownd) == OWNI, "AH0: both own crossbows read from SkyyArmory/SkyyArmory-0.1.3.jar: %%s" %% sorted(ownd))
    ovl_ = dict(mct)
    ovl_.update(ownd)
    WK = AzWalker(azz, azz.namelist(), ovl_)
''' % (OWN,))
sub('''    check(sorted([str(x) for x in Chg.TRUST]) == sorted(set(VAN) | set(PACKI)) and len(PACKI) in (0, 4),
          "Z3: the jar's trust list = every vanilla weapon id + the pack's More Crossbow Tiers ids (%d + %d)" % (len(VAN), len(PACKI)))''',
    '''    check(sorted([str(x) for x in Chg.TRUST]) == sorted(set(VAN) | set(PACKI) | set(OWNI)) and len(PACKI) in (0, 4),
          "Z3: the jar's trust list = every vanilla weapon id + the pack's More Crossbow Tiers ids + our own crossbows (%d + %d + %d)" % (
              len(VAN), len(PACKI), len(OWNI)))''')
sub('''    ALLW = sorted(set(VAN) | set(PACKI))''', '''    ALLW = sorted(set(VAN) | set(PACKI) | set(OWNI))''')
# a look-alike unknown id with the Copper crossbow's own chains (trust must be the exact id, never a prefix)
sub('''    zitems["Weapon_Crossbow_Modded"] = MZ.item("Weapon_Crossbow_Iron", "Weapon_Crossbow_Modded")''',
    '''    zitems["Weapon_Crossbow_Modded"] = MZ.item("Weapon_Crossbow_Iron", "Weapon_Crossbow_Modded")
    zitems["Weapon_Crossbow_Copper_Wynn_Copy"] = MZ.item("Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Copper_Wynn_Copy")''')
sub('''"Weapon_Crossbow_": (2 + len(PACKI), 2 + len(PACKI)),''', '''"Weapon_Crossbow_": (2 + len(PACKI) + len(OWNI), 2 + len(PACKI) + len(OWNI)),''')

# ---- AH1 inside Z4 (the engine model is live there): the own crossbows' 3rd bolt, the look-alike, the loose tag
AH1 = r'''
    # ---- AH1 (0.2.7): our own crossbows' 3rd bolt in a row counts exactly like the Iron crossbow's; unknown ids still never
    XWHY = "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)"
    UWHY = "Charged tag on an untrusted item (not vanilla or pack) - ignored"
    for oid_ in OWNI:
        xo_ = zcalcs(oid_, NORM_, "Charged")
        pe_ = WK.summary(oid_, True)
        check(len(xo_) == 1 and jc(xo_[0][0], oid_) == (1, XWHY) and jc(xo_[0][0], oid_, proj=True, alts=[oid_]) == (1, XWHY)
              and jc(xo_[0][0], oid_, proj=True) == (1, XWHY) and bool(Chg.trusted(oid_)) and bool(Chg.hasCharged(oid_))
              and not bool(Chg.trusted(oid_ + "_Copy")) and len(pe_["combo"]) == 1 and not pe_["partial"],
              "AH1: %s - its 3rd bolt (Hytale's Class Charged combo, no hold) counts like the Iron crossbow's (melee call, its own launch "
              "record, the picked record), trusted, may roll; one combo step, no partial levels" % oid_)
        sh_ = sorted((v_[0], v_[1]) for v_ in pe_["calcs"].values())
        check(sh_ == sorted((v_[0], v_[1]) for v_ in zsum["Weapon_Crossbow_Iron"][1]["calcs"].values()),
              "AH1: %s walks exactly like the Iron crossbow (flags + class per damage step): %s" % (oid_, sh_))
    xcp_ = zcalcs("Weapon_Crossbow_Copper_Wynn", NORM_, "Charged")[0][0]
    ecp_ = Chg.ensure("Weapon_Crossbow_Copper_Wynn_Copy")
    ccp_ = [c_ for c_ in ecp_[0].keySet() if int(ecp_[0].get(c_)[1]) == 2 and int(ecp_[0].get(c_)[0]) == NORM_]
    check(len(ccp_) == 1 and same(ccp_[0], xcp_) and jc(ccp_[0], "Weapon_Crossbow_Copper_Wynn_Copy") == (0, UWHY)
          and jc(xcp_, "Weapon_Crossbow_Copper_Wynn_Copy", proj=True, alts=["Weapon_Crossbow_Copper_Wynn_Copy"]) == (0, UWHY)
          and not bool(Chg.hasCharged("Weapon_Crossbow_Copper_Wynn_Copy")),
          "AH1: the SAME combo bolt on a look-alike unknown id (Weapon_Crossbow_Copper_Wynn_Copy) is untrusted - ignored, never rolls (exact ids)")
    check(jc(loose_calc, "Weapon_Sword_LooseTag") == (0, UWHY) and jc(xcp_, "Weapon_Sword_LooseTag")[0] == 0
          and not bool(Chg.trusted("Weapon_Sword_LooseTag")),
          "AH1: an unknown loose-tagged id is still never trusted (its own tagged swing and the Copper crossbow's combo calculator)")
    print("AH1. own crossbows: 3rd bolt trusted on both, look-alike / loose-tag ids untrusted")
'''
sub('''          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")), "Z4: the same combo bolt on an untrusted (modded) id never counts and never rolls")
''', '''          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")), "Z4: the same combo bolt on an untrusted (modded) id never counts and never rolls")
''' + AH1)

AH_SRC = r'''    # ======================================================================================================================== AH 0.2.7
    print("AH. 0.2.7: own crossbows in the charged trust list - lists, levels, live copy, class compare")
    OWNI7 = @@OWN@@
    # ---- AH2. the jar's lists + levels
    tr7 = [str(x) for x in Chg.TRUST]
    fb7 = [str(x) for x in Chg.FALLBACK]
    pa7 = [str(x) for x in Chg.PARTIAL]
    check(all(o_ in tr7 and o_ in fb7 and o_ not in pa7 for o_ in OWNI7) and not [x_ for x_ in tr7 if "_Wynn" in x_ and x_ not in OWNI7],
          "AH2: GearChg.TRUST + FALLBACK hold both own crossbows (no other _Wynn id), PARTIAL neither")
    Cfg.apply(Props(), False)
    Chg.clear()
    pool7 = [I_CHG in [int(x) for x in Roll.pool(int(Data.slotOf(o_)), o_)] for o_ in OWNI7]
    check(pool7 == [True, True] and bool(Cfg.CHG_ON), "AH2: Charged Attack Damage may roll on both own crossbows (Roll.pool, charged.on default): %s" % pool7)
    bd7 = [[int(x) for x in Lvl.band(o_)][:2] for o_ in OWNI7]
    gg7 = [bool(Data.isGear(o_)) for o_ in OWNI7]
    bs7 = [str(Base.baseOf(o_)) for o_ in OWNI7]
    check(bd7 == [[10, 18], [40, 49]] and gg7 == [True, True] and bs7 == ["Weapon_Crossbow_Iron"] * 2,
          "AH2: levels - Copper crossbow band 10-18 (Copper), Onyxium crossbow band 40-49 (Onyxium), both gear, family base the Iron crossbow: %s %s %s"
          % (bd7, gg7, bs7))
    print("AH2. bands %s, bases %s" % (bd7, bs7))

    # ---- AH3. start twice on a scratch COPY of the live Skyy_SkyyGear folder (read only)
    MD7 = os.path.join(SCRATCH, "work", "mc027")
    shutil.rmtree(MD7, ignore_errors=True)
    if os.path.isfile(LIVE):
        d8_ = os.path.join(MD7, "live", "mods", "Skyy_SkyyGear")
        shutil.copytree(os.path.dirname(LIVE), d8_)
        cfg_quiet()
        Cfg.DIR = Paths.get(d8_)
        Cfg.FILE = Paths.get(os.path.join(d8_, "config.properties"))
        Log.FILE = None

        def chain8():
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(d8_, "..", "Skyy_SkyyRolls", "reforge.properties")))
            for m_ in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
                getattr(Cfg, m_)()
            Cfg.load()

        def snap8(dd_):
            out_ = {}
            for rt_, _ds, fs_ in os.walk(dd_):
                for fn_ in fs_:
                    if fn_ != "gear.log":
                        out_[os.path.relpath(os.path.join(rt_, fn_), dd_)] = rb(os.path.join(rt_, fn_))
            return out_
        s0_ = snap8(d8_)
        chain8()
        s1_ = snap8(d8_)
        chain8()
        s2_ = snap8(d8_)
        check(s1_ == s2_,
              "AH3: START TWICE on a scratch copy of the live folder (%d files, %s): the second start changes no file (0.2.7 adds no key)"
              % (len(s1_), "unchanged by the first start" if s0_ == s1_ else "the first start updated it once"))
        Cfg.FILE = None
        Cfg.DIR = None
        Cfg.apply(Props(), False)
        cfg_quiet()
    else:
        check(False, "AH3: no live config.properties at %s - the live start-twice check could not run" % LIVE)
    shutil.rmtree(MD7, ignore_errors=True)
    print("AH3. live copy done")

    # ---- AH4. class byte-compare 0.2.6 -> 0.2.7
    EXPECT027 = @@EXPECT027@@
    jar026 = os.path.join(HERE, "SkyyGear-0.2.6.jar")
    if os.path.isfile(jar026) and "cls_members" in dir():
        pa8 = Pool(False)
        pa8.appendClassPath(jar026)
        pa8.appendClassPath(B.SERVER_JAR)
        pa8.appendSystemPath()
        pb8 = Pool(False)
        pb8.appendClassPath(jar)
        pb8.appendClassPath(B.SERVER_JAR)
        pb8.appendSystemPath()
        na8 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar026).namelist() if n_.endswith(".class"))
        nb8 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs8 = {}
        for cn_ in sorted(set(na8) & set(nb8)):
            ma_, mb_ = cls_members(pa8, cn_), cls_members(pb8, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs8[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AH4. class compare 0.2.6 -> 0.2.7: %s" % json.dumps(diffs8, sort_keys=True))
        check(na8 == nb8, "AH4: no class added or removed: %s" % sorted(set(na8) ^ set(nb8)))
        unexp8 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT027.get(c_, [])]) for c_, v_ in diffs8.items())
        unexp8 = dict((c_, v_) for c_, v_ in unexp8.items() if v_)
        missing8 = dict((c_, [m_ for m_ in v_ if m_ not in diffs8.get(c_, [])]) for c_, v_ in EXPECT027.items())
        missing8 = dict((c_, v_) for c_, v_ in missing8.items() if v_)
        check(not unexp8, "AH4: no difference outside the listed 0.2.7 parts: %s" % unexp8)
        check(not missing8, "AH4: every listed 0.2.7 part is really in the jar: %s" % missing8)
        za8, zb8 = zipfile.ZipFile(jar026), zipfile.ZipFile(jar)
        ea8 = [n_ for n_ in za8.namelist() if not n_.endswith(".class")]
        eb8 = [n_ for n_ in zb8.namelist() if not n_.endswith(".class")]
        ediff8 = sorted(n_ for n_ in set(ea8) | set(eb8) if n_ not in ea8 or n_ not in eb8 or za8.read(n_) != zb8.read(n_))
        check(ediff8 == ["manifest.json"], "AH4: non-class entries: only manifest.json changed: %s" % ediff8)
    else:
        check(False, "AH4: SkyyGear-0.2.6.jar (or the compare helper) not found - the class compare could not run")
    Chg.clear()
    print("AH. 0.2.7 done")

'''

# AH4: the members 0.2.6 -> 0.2.7 may differ in (filled from the reviewed compare; anything else fails)
EXPECT027 = {
    # VERSION text only (checked string by string): CfgRows VERSION, the export header (CfgFn.opExport), the fresh file's first line
    # "# SkyyGear 0.2.7 - Server Setup ..." (GearCfg.defaultsText), the "[SkyyGear] 0.2.7 ready" line (SkyyGearPlugin.setup)
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    'GearCfg': ['~m defaultsText()Ljava/lang/String;'],
    'SkyyGearPlugin': ['~m setup()V'],
    # the trust list + the baked roll fallback gain the two own crossbows (static arrays)
    'GearChg': ['~<clinit>'],
}
AH_SRC = AH_SRC.replace("@@EXPECT027@@", repr(EXPECT027)).replace("@@OWN@@", repr(OWN))
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AH_SRC + "\n" + RESTORE)
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, H26 + " (run as the SkyyGear 0.2.7 harness)", "exec"), _g)
