"""Bare-JVM check for SkyyGear 0.2.8 (THE KUNAI LADDER'S LEVEL BANDS: SkyyArmory 0.1.6's Weapon_Kunai_<Crude ... Onyxium> look from their metal
word, the vanilla Kunai / spellbooks stay their own family base; research/cloud/Kunai-Ladder.md section 9 item 1, Skyy LOCKED
docs/answered/gear.md 2026-10-07 "SPELLBOOKS + KUNAI"). The 0.2.7 harness (SkyyGear/test_skyygear_0.2.7.py, read only: every 0.1 ... 0.2.7
section) runs on the 0.2.8 jar with VERSION 0.2.8 and the new section AI.

    python SkyyGear/test_skyygear_0.2.8.py [--jar <SkyyGear-0.2.8.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

  AI 0.2.8 - every new path EXECUTED on the real classes:
     AI1 GearLevel.band / entry / level for the kunai ladder (Crude 1-13 ... Onyxium 40-49), the vanilla Kunai (Kunai row 20-27), the spellbook
         ladder (its metal) and a METAL_FIRST id without a metal word (falls back to the Kunai row); negative control: with METAL_FIRST blanked
         the jar resolves the ladder to the Kunai row again (the 0.2.7 trap);
     AI2 GearBase.baseOf with Weapon_Kunai_Crude / _Copper present in the live item map: the vanilla Kunai + spellbooks stay their own base
         (OWN_BASE), Weapon_Kunai_Copper takes Weapon_Kunai_Crude (band start 1 -> divisor 1); negative control: OWN_BASE blanked -> the vanilla
         Kunai would take the Crude kunai;
     AI3 (fix round) the KUNAI TWIN: Weapon_Kunai_<Metal> takes the same-metal dagger's K (ratio + divisor), so the kunai stays 1.12 x the
         dagger average hit (80 % of its DPS) with SkyyGear at every metal; the vanilla Kunai / an id with no dagger twin keep themselves;
     AI4 the class byte-compare 0.2.7 -> 0.2.8 (every difference listed) + the non-class entries (only manifest.json).
  The carried AH3 (start twice on a live copy) runs on the 0.2.8 jar unchanged; the carried AH4 (0.2.6 -> 0.2.7 compare) is a listed deviation.
Scratch: only under --dir (default tools/dev/scratch/gear028/harness), deleted at the end unless --keep. Exit code 1 on any unexpected failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
H27 = os.path.join(HERE, "test_skyygear_0.2.7.py")
_t27 = open(H27, encoding="utf-8").read()
_cut = _t27.rindex('_g = {"__name__": "__main__"')
_n27 = {"__name__": "skyygear_h27", "__file__": H27, "__builtins__": __builtins__}
exec(compile(_t27[:_cut], H27 + " (the 0.2.7 harness text, not run)", "exec"), _n27)
src = _n27["src"]
DEV27 = _n27["DEV26"] + _n27["DEVIATIONS27"]


def sub(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
    src = src.replace(old, new)


DEVIATIONS28 = [
    ("AH4: no difference outside the listed 0.2.7 parts", "the historical 0.2.6 -> 0.2.7 compare against the 0.2.8 jar: GearLevel / GearBase / "
     "GearDefs differ too (the 0.2.8 look + own-base pin) - AI4 compares 0.2.7 -> 0.2.8"),
]
sub('VERSION = "0.2.7"\nDEVIATIONS = %r' % (DEV27,), 'VERSION = "0.2.8"\nDEVIATIONS = %r' % (DEV27 + DEVIATIONS28,))
sub('os.path.join(TOOLS, "dev", "scratch", "gear027", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "gear028", "harness")')
sub('print("DEVIATION (0.2.5/0.2.6/0.2.7, expected):"', 'print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8, expected):"')
sub('expected 0.2.5 / 0.2.6 / 0.2.7 deviations (%d listed kinds seen)', 'expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 deviations (%d listed kinds seen)')

AI_SRC = r'''    # ======================================================================================================================== AI 0.2.8
    print("AI. 0.2.8: the kunai ladder's level bands + the own-base pin - executed, class compare")
    Cfg.apply(Props(), False)
    LADK = ["Weapon_Kunai_%s" % m_ for m_ in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
    LADB = ["Weapon_Spellbook_%s" % m_ for m_ in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
    WANTK = [[1, 13], [10, 18], [15, 23], [20, 28], [25, 38], [35, 43], [40, 49], [40, 49]]
    bk_ = [[int(x) for x in Lvl.band(i_)][:2] for i_ in LADK]
    ek_ = [str(Lvl.entry(i_)) for i_ in LADK]
    lk_ = [int(Lvl.level(i_, None)) for i_ in LADK]
    check(bk_ == WANTK and ek_ == ["crude", "copper", "iron", "thorium", "cobalt", "adamantite", "mithril", "onyxium"]
          and lk_ == [w_[0] for w_ in WANTK] and [int(x) for x in Lvl.band(LADK[0])][2] == 1,
          "AI1: GearLevel.band / entry / level of the kunai ladder = its metal band (Crude 1-13 ... Onyxium 40-49, kind 1 = by material): %s %s %s"
          % (bk_, ek_, lk_))
    bb_ = [[int(x) for x in Lvl.band(i_)][:2] for i_ in LADB]
    check(bb_ == WANTK[1:] and [str(Lvl.entry(i_)) for i_ in LADB] == [i_.split("_")[2].lower() for i_ in LADB],
          "AI1: the spellbook ladder = its metal band (no fix needed: no 'spellbook' row): %s" % bb_)
    check([int(x) for x in Lvl.band("Weapon_Kunai")][:2] == [20, 27] and str(Lvl.entry("Weapon_Kunai")) == "kunai"
          and str(Lvl.entry("Weapon_Kunai_Foo")) == "kunai" and str(Lvl.entry("Weapon_Daggers_Copper")) == "copper"
          and str(Lvl.entry("Weapon_Sword_Steel_Rusty")) == "steel_rusty" and int(Lvl.first(JArray(JString)(["Weapon", "Kunai", "Copper"]))) == 2
          and int(Lvl.first(JArray(JString)(["Weapon", "Kunai"]))) == 0 and int(Lvl.first(JArray(JString)(["Weapon", "Sword", "Iron"]))) == 0,
          "AI1: the vanilla Kunai keeps its row 20-27; Weapon_Kunai_Foo (no metal word) falls back to the Kunai row; other ids unchanged; first()")
    mf_ = Defs.METAL_FIRST
    keep_ = str(mf_[0])
    mf_[0] = "zzz"
    trap_ = [[int(x) for x in Lvl.band(i_)][:2] for i_ in LADK]
    mf_[0] = keep_
    check(trap_ == [[20, 27]] * 8 and [[int(x) for x in Lvl.band(i_)][:2] for i_ in LADK] == WANTK,
          "AI1 negative control: with METAL_FIRST blanked the jar puts the whole ladder in the Kunai row 20-27 (the 0.2.7 trap); restored = metal bands")
    print("AI1. kunai ladder %s, spellbooks %s" % (bk_, bb_))
    # ---- AI2. the family base with our kunai in the live item map (the run-time Crude / Wood / Iron search)
    ITc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    am_ = ITc.getAssetMap()
    fam_ = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_.getDeclaredField("assetMap")
    fam_.setAccessible(True)
    mp_ = fam_.get(am_)
    Unsafe2 = JClass("sun.misc.Unsafe")
    uf2 = Unsafe2.class_.getDeclaredField("theUnsafe")
    uf2.setAccessible(True)
    fake_ = uf2.get(None).allocateInstance(ITc.class_)
    added_ = []
    for k_ in ("Weapon_Kunai_Crude", "Weapon_Kunai_Copper", "Weapon_Kunai", "Weapon_Spellbook_Iron", "Weapon_Spellbook_Fire"):
        if mp_.get(k_) is None:
            mp_.put(k_, fake_)
            added_.append(k_)
    Base.clear()
    b1_ = [str(Base.baseOf(i_)) for i_ in ("Weapon_Kunai", "Weapon_Kunai_Copper", "Weapon_Kunai_Crude", "Weapon_Spellbook_Fire")]
    ob_ = Defs.OWN_BASE
    own_ = [str(x) for x in ob_]
    ki_ = own_.index("Weapon_Kunai")
    ob_[ki_] = "zzz"
    Base.clear()
    b2_ = str(Base.baseOf("Weapon_Kunai"))
    ob_[ki_] = "Weapon_Kunai"
    Base.clear()
    for k_ in added_:
        mp_.remove(k_)
    check(b1_ == ["Weapon_Kunai", "Weapon_Kunai_Crude", "Weapon_Kunai_Crude", "Weapon_Spellbook_Fire"] and b2_ == "Weapon_Kunai_Crude"
          and "Weapon_Kunai" in own_ and not [x_ for x_ in own_ if x_.startswith("Weapon_Kunai_")],
          "AI2: with Weapon_Kunai_Crude in the item map the vanilla Kunai + spellbooks stay their own base (OWN_BASE %s) and Weapon_Kunai_Copper "
          "takes the Crude kunai (band start 1 -> divisor 1); negative control: OWN_BASE blanked -> the vanilla Kunai takes %s: %s"
          % (own_, b2_, b1_))
    print("AI2. bases %s (pin off: %s)" % (b1_, b2_))
    # ---- AI3. KUNAI TWIN (fix round): a Weapon_Kunai_<Metal> takes the same-metal dagger's K (ratio + base divisor), so kunai / dagger at the
    # same level = SkyyArmory's 1.12 x the dagger average at every metal (was 0.93-1.11, 0.62 at Onyxium); the vanilla Kunai + an id without a
    # dagger twin keep the old path
    Base.clear()
    METS_ = ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
    tw_ = [str(Base.kunaiTwin("Weapon_Kunai_" + m_)) for m_ in METS_]
    kk_ = [float(Base.kOf("Weapon_Kunai_" + m_, False)) for m_ in METS_]
    kd_ = [float(Base.kOf("Weapon_Daggers_" + m_, False)) for m_ in METS_]
    rk_ = [float(Base.ratio("Weapon_Kunai_" + m_)) for m_ in METS_]
    rd_ = [float(Base.ratio("Weapon_Daggers_" + m_)) for m_ in METS_]
    kv_ = (str(Base.kunaiTwin("Weapon_Kunai")), str(Base.kunaiTwin("Weapon_Kunai_Foo")), str(Base.kunaiTwin("Weapon_Sword_Copper")),
           float(Base.kOf("Weapon_Kunai", False)))
    Base.clear()
    check(tw_ == ["Weapon_Daggers_" + m_ for m_ in METS_] and kk_ == kd_ and rk_ == rd_ and all(k_ > 0.0 for k_ in kk_)
          and len(set(round(k_, 6) for k_ in kd_)) > 1 and kv_[:3] == ("Weapon_Kunai", "Weapon_Kunai_Foo", "Weapon_Sword_Copper") and kv_[3] > 0.0,
          "AI3 FIX (kunai DPS = 80 %% of the dagger WITH SkyyGear): every Weapon_Kunai_<Metal> takes its Weapon_Daggers_<Metal> twin's K (ratio + "
          "divisor) - kunai %s == daggers %s; the vanilla Kunai / Weapon_Kunai_Foo / other ids keep themselves: %s" % (kk_, kd_, kv_))
    print("AI3. kunai K = dagger K per metal: %s" % ", ".join("%s %.3f" % (m_, k_) for m_, k_ in zip(METS_, kk_)))

    # ---- AI4. class byte-compare 0.2.7 -> 0.2.8
    EXPECT028 = @@EXPECT028@@
    jar027 = os.path.join(HERE, "SkyyGear-0.2.7.jar")
    if os.path.isfile(jar027) and "cls_members" in dir():
        pa9 = Pool(False)
        pa9.appendClassPath(jar027)
        pa9.appendClassPath(B.SERVER_JAR)
        pa9.appendSystemPath()
        pb9 = Pool(False)
        pb9.appendClassPath(jar)
        pb9.appendClassPath(B.SERVER_JAR)
        pb9.appendSystemPath()
        na9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar027).namelist() if n_.endswith(".class"))
        nb9 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        diffs9 = {}
        for cn_ in sorted(set(na9) & set(nb9)):
            ma_, mb_ = cls_members(pa9, cn_), cls_members(pb9, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs9[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        print("AI4. class compare 0.2.7 -> 0.2.8: %s" % json.dumps(diffs9, sort_keys=True))
        check(na9 == nb9, "AI4: no class added or removed: %s" % sorted(set(na9) ^ set(nb9)))
        unexp9 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT028.get(c_, [])]) for c_, v_ in diffs9.items())
        unexp9 = dict((c_, v_) for c_, v_ in unexp9.items() if v_)
        missing9 = dict((c_, [m_ for m_ in v_ if m_ not in diffs9.get(c_, [])]) for c_, v_ in EXPECT028.items())
        missing9 = dict((c_, v_) for c_, v_ in missing9.items() if v_)
        check(not unexp9, "AI4: no difference outside the listed 0.2.8 parts: %s" % unexp9)
        check(not missing9, "AI4: every listed 0.2.8 part is really in the jar: %s" % missing9)
        za9, zb9 = zipfile.ZipFile(jar027), zipfile.ZipFile(jar)
        ea9 = [n_ for n_ in za9.namelist() if not n_.endswith(".class")]
        eb9 = [n_ for n_ in zb9.namelist() if not n_.endswith(".class")]
        ediff9 = sorted(n_ for n_ in set(ea9) | set(eb9) if n_ not in ea9 or n_ not in eb9 or za9.read(n_) != zb9.read(n_))
        check(ediff9 == ["manifest.json"], "AI4: non-class entries: only manifest.json changed: %s" % ediff9)
    else:
        check(False, "AI4: SkyyGear-0.2.7.jar (or the compare helper) not found - the class compare could not run")
    Cfg.apply(Props(), False)
    print("AI. 0.2.8 done")

'''
EXPECT028 = {
    # VERSION text only: CfgRows VERSION, the export header, the fresh file's first line, the ready line
    'CfgFn': ['~m opExport([Ljava/lang/Object;)Ljava/lang/Object;'],
    'CfgRows': ['~<clinit>', '~f VERSION', '~m header()[Ljava/lang/Object;'],
    'GearCfg': ['~m defaultsText()Ljava/lang/String;'],
    'SkyyGearPlugin': ['~m setup()V'],
    # the two new tables
    'GearDefs': ['~<clinit>', '+f METAL_FIRST', '+f OWN_BASE'],
    # the look (first / keyFrom / look) used by level + entry
    'GearLevel': ['+m first([Ljava/lang/String;)I', '+m keyFrom([Ljava/lang/String;ILjava/util/HashMap;I)Ljava/lang/String;',
                  '+m look([Ljava/lang/String;Ljava/util/HashMap;I)Ljava/lang/String;',
                  '~m level(Ljava/lang/String;Lorg/bson/BsonDocument;)I', '~m entry(Ljava/lang/String;)Ljava/lang/String;'],
    # the own-base pin
    'GearBase': ['~m baseOf(Ljava/lang/String;)Ljava/lang/String;', '+m kunaiTwin(Ljava/lang/String;)Ljava/lang/String;',
                 '~m ratio(Ljava/lang/String;)D', '~m kOf(Ljava/lang/String;Z)D'],
}
AI_SRC = AI_SRC.replace("@@EXPECT028@@", repr(EXPECT028))
RESTORE = "    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)\n"
sub(RESTORE, AI_SRC + "\n" + RESTORE)
_g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(src, H27 + " (run as the SkyyGear 0.2.8 harness)", "exec"), _g)
