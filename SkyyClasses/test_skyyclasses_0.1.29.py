"""SkyyClasses 0.1.29 - harness for "the Assassin kit gets a Crude Kunai" (tools/classes_0_1_29_patch.py). Build first:
python tools/classes_0_1_29_patch.py && python SkyyClasses/build_skyyclasses_0.1.29.py

    python SkyyClasses/test_skyyclasses_0.1.29.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Every JVM: the game's JRE, -Xverify:all (the KIT / MIG phases), -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data
(the test world's Skyy_SkyyClasses) is only READ - copied into scratch first.
  OLD  the WHOLE 0.1.28 harness (which runs the 0.1.27 one, which runs the 0.1.26 one) on the 0.1.29 jar; its compare lines pin
       0.1.27 -> 0.1.28 (ours: C below), so those are expected to differ (EXPECTED_OLD, each with its reason). The 0.1.26 harness stops
       before its own phases here (its compare's old jar SkyyClasses-0.1.25.jar is no longer on disk), so OLD-26 runs its exec phase
       (X1-X70 on the engine stand-ins) and its config write proof (cwnew) on our jar directly
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.28 -> 0.1.29: exactly the members of EXPECT differ; no class added / removed; non-class entries: manifest.json only
  MGOLD  0.1.28's ClassCfg.mgUpdate on the sample texts (the OLD jar) -> scratch JSON
  MIG  the config update on scratch files: 0.1.29's mgUpdate (now mgUpdateT with 0.1.10's table) = 0.1.28's on every sample, byte for
       byte; mgUpdateT with the 0.1.29 table (live copy LF / CRLF, hand-edited, missing line, marker present, continued line);
       ClassCfg.migrate0129 on a scratch COPY of the live config folder (History version with the old bytes first, one change-log line in
       the Undo format, the INFO line, run-once, load() sees the kunai); 0.1.10 + 0.1.29 in a row on a 0.1.9-era file; a fresh default
       file carries both markers and is never rewritten
  KIT  the kit + the one-time top-up on REAL engine containers (the 0.1.10 harness's Z stand-ins: SimpleItemContainer hotbar 9 / storage
       36, the real InventoryComponent$Utility, an Item asset map with the test items): a NEW Assassin (daggers + kunai in the hotbar, the
       top-up writes only its marker), an EXISTING Assassin (a scratch COPY of the live test world's Assassin file when there is one: the
       kunai owed once, delivered by the quiet claim, the tip line; re-login, a server restart and a profile switch never give a second),
       a FULL hotbar (the waiting line once per session, retried after re-login, /class kit into storage), hotbar + storage full, other
       classes / pending / old / off / in-flight / another kitClass / a hand-edited kit / an unknown kunai / a loading profile / kits off
       (nothing written), an owed Assassin (the kunai joins the owed list); claim reads kitClaimBegin's list (bytecode order)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION = "0.1.29"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.28.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "class0129", "cls")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
ADDED = []
EXPECT = {
    "ClassCfg": ["+f MG29_KEY", "+f MG29_MARK", "+f MG29_MARK_ID", "+f MG29_NEW", "+f MG29_OLD", "+f MG29_WHO", "+f MG29_WHY",
                 "+m mgIdxT", "+m mgLogT", "+m mgUpdateT", "+m migrate0129", "~<clinit>", "~m mgUpdate",
                 "~m load"],                                  # load: the kit.Assassin code default (read while the line is missing)
    "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],     # the config kit's row tables: the kit.Assassin row default
    "ClassStore": ["+m topupKey"],
    "ClassTick": ["~m run"],
    "Kit": ["+f TOPDONE", "+f TOPTOLD", "+f TOP_CLASS", "+f TOP_ITEM", "+f TOP_MARK", "+f TOP_TIP", "+f TOP_WAIT",
            "+m dropKeys", "+m topConsider", "+m topTick", "+m topWait", "~<clinit>", "~m claim", "~m forget"],
    "KitCfg": ["+m amountOf", "~<clinit>"],
    "SkyyClassesPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],      # the inlined version constant
}
EXPECTED_OLD = [
    ("compare: C: the classes that differ", "its compare is 0.1.27 -> 0.1.28 against our jar (ours: phase C)"),
    ("compare: C: ", "its member lists pin 0.1.27 -> 0.1.28; 0.1.29 changes ClassCfg / Kit / KitCfg / ClassStore / ClassTick / setup (ours: phase C)"),
    ("OLD: no failure outside the listed identity checks", "its nested 0.1.27 harness's compare (0.1.26 -> 0.1.27) also sees the 0.1.29 changes"),
]
SAMPLE_019 = ("# SkyyClasses config\nswitchCost=5000\nkits.enabled=true\nkit.Archer=Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64\n"
              "kit.Warrior=Weapon_Sword_Crude:1\nkit.Mage=Weapon_Staff_Wood:1\nkit.Assassin=Weapon_Daggers_Crude:1\n"
              "# Priest heal\npriestHeal.selfPercent=50\n")


def samples():
    """texts both jars' mgUpdate run on (the identity of the 0.1.10 update through mgUpdateT)"""
    out = {"019": SAMPLE_019, "019crlf": SAMPLE_019.replace("\n", "\r\n"),
           "custom": SAMPLE_019.replace("kit.Warrior=Weapon_Sword_Crude:1", "kit.Warrior=Weapon_Sword_Iron:1").replace("=50", "=75"),
           "marked": "# SkyyClasses 0.1.10 defaults (x)\n" + SAMPLE_019, "empty": "", "nolines": "switchCost=1\n",
           "cont": "kit.Warrior=Weapon_Sword_Crude:1,\\\n  Weapon_Shield_Wood:1\npriestHeal.selfPercent=50\n",
           "comment": "a=1\n# the Warrior kit\nkit.Warrior=Weapon_Sword_Crude:1\n", "noeol": "kit.Warrior=Weapon_Sword_Crude:1"}
    lf = os.path.join(LIVE, "config.properties")
    if os.path.isfile(lf):
        out["live"] = open(lf, "rb").read().decode("latin-1")
    return out


def jlist(r):
    if r is None:
        return None
    return [str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]]


# ======================================================================================================== MGOLD: 0.1.28's mgUpdate
def run_mgold(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=False)
    Cfg = JClass(PKG + "ClassCfg")
    res = dict((n, jlist(Cfg.mgUpdate(t))) for n, t in samples().items())
    json.dump(res, open(os.path.join(scratch, "mgold-data.json"), "w"))
    K.check(len(res) >= 9, "MGOLD: 0.1.28's mgUpdate ran on %d sample texts" % len(res))
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ======================================================================================================== MIG: the config update
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Cfg, KitCfg = JClass(PKG + "ClassCfg"), JClass(PKG + "KitCfg")
    Paths = JClass("java.nio.file.Paths")
    # ---------------- 0.1.10's update through mgUpdateT = 0.1.28's mgUpdate, byte for byte
    old = json.load(open(os.path.join(scratch, "mgold-data.json")))
    smp = samples()
    same = [n for n in smp if jlist(Cfg.mgUpdate(smp[n])) == old.get(n, "missing")]
    for n in sorted(set(smp) - set(same))[:2]:
        print("MIG identity differs on %s: 0.1.28 %r / 0.1.29 %r" % (n, old.get(n, "missing"), jlist(Cfg.mgUpdate(smp[n]))))
    K.check(sorted(same) == sorted(smp), "MIG: 0.1.10's update (mgUpdate -> mgUpdateT) = 0.1.28's on every sample (%d): differ %s"
            % (len(smp), sorted(set(smp) - set(same))))
    MARK, MID, WHO = str(Cfg.MG29_MARK), str(Cfg.MG29_MARK_ID), str(Cfg.MG29_WHO)
    OLDV, NEWV = "Weapon_Daggers_Crude:1", "Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1"
    K.check([str(x) for x in Cfg.MG29_KEY] == ["kit.Assassin"] and [str(x) for x in Cfg.MG29_OLD] == [OLDV]
            and [str(x) for x in Cfg.MG29_NEW] == [NEWV] and WHO == "SkyyClasses 0.1.29" and MID in MARK and "=" not in MARK
            and str(KitCfg.K_ASSASSIN) == NEWV, "MIG: the 0.1.29 table, marker (doc comment) and the code default kit.Assassin=%s" % NEWV)

    def upd(text):
        return jlist(Cfg.mgUpdateT(text, Cfg.MG29_KEY, Cfg.MG29_OLD, Cfg.MG29_NEW, Cfg.MG29_WHY, Cfg.MG29_MARK, Cfg.MG29_MARK_ID, "0.1.29"))

    def want_of(text, line_old, line_new):
        """the expected text: the marker above the kit.Assassin entry (above its comment when one sits right on top), value changed"""
        crlf = "\r\n" in text
        ls = text.replace("\r\n", "\n").split("\n")
        i = [j for j, l in enumerate(ls) if l.startswith("kit.Assassin")][0]
        at = i - 1 if i > 0 and ls[i - 1].lstrip().startswith(("#", "!")) else i
        ls[i] = line_new if line_new is not None else ls[i]
        ls = ls[:at] + [MARK] + ls[at:]
        t = "\n".join(ls)
        return t.replace("\n", "\r\n") if crlf else t
    # ---------------- mgUpdateT with the 0.1.29 table
    base = smp.get("live", SAMPLE_019)
    if "kit.Assassin=" + OLDV + "\n" not in base.replace("\r\n", "\n"):
        base = SAMPLE_019
    for tag, t in (("LF", base.replace("\r\n", "\n")), ("CRLF", base.replace("\r\n", "\n").replace("\n", "\r\n"))):
        r = upd(t)
        K.check(r is not None and r[0] == want_of(t, "kit.Assassin=" + OLDV, "kit.Assassin=" + NEWV),
                "MIG %s: an untouched kit.Assassin line -> + the Crude Kunai, the marker right above it, every other byte kept" % tag)
        K.check(r is not None and r[1] == "kit.Assassin %s -> %s (Assassins also start with a Crude Kunai)" % (OLDV, NEWV) and r[2] == []
                and r[3] == ["kit.Assassin", OLDV, NEWV], "MIG %s: the change text + the one update row: %s" % (tag, r and r[1:]))
        K.check(r is not None and (("\r\n" in r[0]) == (tag == "CRLF")) and r[0].count("\r\n") == (t.count("\r\n") + (1 if tag == "CRLF" else 0)),
                "MIG %s: line endings kept (the marker line too)" % tag)
    t = base.replace("\r\n", "\n").replace("kit.Assassin=" + OLDV, "kit.Assassin=Weapon_Daggers_Iron:1")
    r = upd(t)
    K.check(r is not None and r[0] == want_of(t, "", None) and r[1] == "" and r[3] == []
            and r[2] == ["kit.Assassin=Weapon_Daggers_Iron:1 kept (custom) - the 0.1.29 default is " + NEWV],
            "MIG: a hand-edited kit.Assassin is kept (marker only) and noted once: %s" % (r and r[2]))
    t = base.replace("\r\n", "\n").replace("kit.Assassin=" + OLDV, "kit.Assassin=" + NEWV)
    r = upd(t)
    K.check(r is not None and r[0] == want_of(t, "", None) and r[1] == "" and r[2] == [], "MIG: a line already holding the new kit: marker only, no note")
    t = "\n".join(l for l in base.replace("\r\n", "\n").split("\n") if not l.startswith("kit.Assassin"))
    r = upd(t)
    K.check(r is not None and r[0] == MARK + "\n" + t and r[1] == "" and r[2] == [] and r[3] == [],
            "MIG: no kit.Assassin line (the loader's default = the new kit): only the marker, on top")
    K.check(upd(MARK + "\n" + SAMPLE_019) is None and upd("a=1\n#   " + MID + " old\n" + SAMPLE_019) is None,
            "MIG: the marker in a comment line = nothing to do (runs once)")
    t = "kit.Assassin=Weapon_Daggers_Crude:1,\\\n  Weapon_Kunai_Crude:1\n"
    r = upd(t)
    K.check(r is not None and r[0] == MARK + "\n" + t and r[3] == [] and len(r[2]) == 1, "MIG: a continued kit.Assassin entry is kept and noted")
    K.check(upd(MARK.replace(MID, "SkyyClasses 0.1.10 defaults") + "\n" + SAMPLE_019) is not None and
            jlist(Cfg.mgUpdate(MARK + "\n" + SAMPLE_019)) is not None, "MIG: the two updates' markers never stand for each other")

    # ---------------- migrate0129 on scratch files
    mroot = os.path.join(scratch, "mig")

    def setup(name, text=None, copy_live=False):
        home = os.path.join(mroot, name, "Skyy_SkyyClasses")
        os.makedirs(home)
        if copy_live:
            for f_ in ("config.properties", "config-changes.log"):
                if os.path.isfile(os.path.join(LIVE, f_)):
                    shutil.copy(os.path.join(LIVE, f_), os.path.join(home, f_))
            if os.path.isdir(os.path.join(LIVE, "config-history")):
                shutil.copytree(os.path.join(LIVE, "config-history"), os.path.join(home, "config-history"))
        f = os.path.join(home, "config.properties")
        if text is not None:
            open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        return home, f

    def hist(home):
        d = os.path.join(home, "config-history")
        return sorted(x for x in os.listdir(d) if x.endswith(".bak")) if os.path.isdir(d) else []

    def logl(home):
        f = os.path.join(home, "config-changes.log")
        return [l for l in open(f, encoding="utf8").read().split("\n") if l] if os.path.isfile(f) else []

    def rd(f):
        return open(f, "rb").read()

    def saved(home, data):
        return any(open(os.path.join(home, "config-history", x), "rb").read() == data for x in hist(home))

    def once(name, home, f):
        b1, h1, l1 = rd(f), hist(home), logl(home)
        r2 = str(Cfg.migrate0129())
        K.check(r2 == "" and rd(f) == b1 and hist(home) == h1 and logl(home) == l1, "MIG %s: the second start changes nothing (%r)" % (name, r2))

    live_ok = os.path.isfile(os.path.join(LIVE, "config.properties"))
    if live_ok:
        home, f = setup("live", copy_live=True)
    else:
        home, f = setup("live", text=SAMPLE_019)
    b0, h0, l0 = rd(f), hist(home), logl(home)
    t0 = b0.decode("latin-1")
    untouched = ("kit.Assassin=" + OLDV) in t0.replace("\r\n", "\n").split("\n")
    r = str(Cfg.migrate0129())
    t1 = rd(f).decode("latin-1")
    print("MIG: %s config: kit.Assassin %s, %d history files, %d change-log lines -> %r" % ("the live test world's" if live_ok else "a sample",
          "untouched" if untouched else "edited / missing", len(h0), len(l0), r))
    if untouched:
        K.check(t1 == want_of(t0, "kit.Assassin=" + OLDV, "kit.Assassin=" + NEWV), "MIG live copy: kit.Assassin updated + the marker, every other byte kept")
        nl = logl(home)[len(l0):]
        rows = [l.split("\t") for l in nl]
        K.check(len(rows) == 1 and len(rows[0]) == 8 and rows[0][1:4] == [WHO, "-", "update"] and rows[0][4:8] == ["kit.Assassin", OLDV, NEWV, "ok"],
                "MIG live copy: one config-changes.log line in the kit's scalar-row format (Server Setup -> Changes -> Undo): %s" % nl)
        # the line = mgLog's format under the 0.1.29 name (the 0.1.10 lines Undo the same way)
        a_, b_ = str(Cfg.mgLogT(WHO, "kit.Assassin", OLDV, NEWV)).split("\t"), str(Cfg.mgLog("kit.Assassin", OLDV, NEWV)).split("\t")
        K.check(a_[2:] == b_[2:] and a_[1] == WHO and b_[1] == str(Cfg.MG_WHO), "MIG: mgLogT = mgLog's columns with the update's own name")
        K.check("kit.Assassin %s -> %s" % (OLDV, NEWV) in r and "config-history" in r, "MIG live copy: the INFO line: %r" % r)
    else:
        K.check(r != "" and MARK in t1, "MIG live copy: marked (%r)" % r)
    K.check(len(hist(home)) == len(h0) + 1 and saved(home, b0) and all(x in hist(home) for x in h0),
            "MIG live copy: one new History version holding the old bytes (verified before the rewrite); old versions kept")
    idx_ = open(os.path.join(home, "config-history", "index.log"), encoding="utf8").read()
    K.check(WHO in idx_ and "before the 0.1.29 defaults update" in idx_, "MIG: the History index names the update")
    once("live", home, f)
    Cfg.load()
    K.check(str(KitCfg.K_ASSASSIN) == (NEWV if untouched else str(KitCfg.K_ASSASSIN)), "MIG live copy: load() reads kit.Assassin = %s" % KitCfg.K_ASSASSIN)
    # a hand-edited file: untouched bytes except the marker; no change-log line; an INFO note
    home, f = setup("edited", text=SAMPLE_019.replace("kit.Assassin=" + OLDV, "kit.Assassin=Weapon_Daggers_Crude:2"))
    b1 = rd(f)
    r = str(Cfg.migrate0129())
    K.check(rd(f).decode("latin-1") == want_of(b1.decode("latin-1"), "", None) and not logl(home) and "nothing changed" in r
            and "kit.Assassin=Weapon_Daggers_Crude:2 kept (custom) - the 0.1.29 default is " + NEWV in r, "MIG edited: kept, marker only, noted: %r" % r)
    once("edited", home, f)
    Cfg.load()
    K.check(str(KitCfg.K_ASSASSIN) == "Weapon_Daggers_Crude:2", "MIG edited: load() keeps the hand-edited kit")
    # a 0.1.9-era file: 0.1.10, then 0.1.29 (setup's order)
    home, f = setup("chain", text=SAMPLE_019.replace("\n", "\r\n"))
    r10, r29 = str(Cfg.migrate0110()), str(Cfg.migrate0129())
    tc = rd(f).decode("latin-1")
    K.check("kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\r\n" in tc and "kit.Assassin=" + NEWV + "\r\n" in tc
            and "priestHeal.selfPercent=100\r\n" in tc and tc.count(str(Cfg.MG_MARK)) == 1 and tc.count(MARK) == 1 and "\n" not in tc.replace("\r\n", ""),
            "MIG chain: 0.1.10 then 0.1.29 on a CRLF 0.1.9 file: both updates, both markers once, CRLF kept")
    rows = [l.split("\t") for l in logl(home)]
    K.check(sorted((x[1], x[4]) for x in rows) == sorted([(str(Cfg.MG_WHO), "kit.Warrior"), (str(Cfg.MG_WHO), "priestHeal.selfPercent"), (WHO, "kit.Assassin")])
            and len(hist(home)) == 2, "MIG chain: three change-log lines (two 0.1.10, one 0.1.29), two History versions")
    once("chain", home, f)
    # no file: nothing; then load() writes the 0.1.29 default (both markers) and the update leaves it alone
    home, f = setup("fresh")
    K.check(str(Cfg.migrate0129()) == "" and not os.path.exists(f) and not hist(home), "MIG fresh: no file = nothing (no file, no history)")
    Cfg.load()
    if os.path.isfile(f):
        tf_ = rd(f).decode("latin-1")
        K.check(MARK in tf_ and str(Cfg.MG_MARK) in tf_ and ("kit.Assassin=" + NEWV) in tf_.replace("\r\n", "\n").split("\n")
                and tf_.replace("\r\n", "\n").split("\n").index(MARK) + 1 == tf_.replace("\r\n", "\n").split("\n").index("kit.Assassin=" + NEWV),
                "MIG fresh: the default file has kit.Assassin=%s with the 0.1.29 marker right above it (and the 0.1.10 marker)" % NEWV)
        b2 = rd(f)
        K.check(str(Cfg.migrate0110()) == "" and str(Cfg.migrate0129()) == "" and rd(f) == b2 and not hist(home), "MIG fresh: neither update touches a fresh default file")
    else:
        K.check(False, "MIG fresh: load() wrote no default file")
    K.save()
    sys.stdout.flush()
    os._exit(0)


# ======================================================================================================== KIT: the kit + the top-up
def ordered_calls(jar, cls, meth):
    """the invoke instructions of one method, in order ("Owner.name")"""
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    CPool = JClass("javassist.bytecode.ConstPool")
    out = []
    for mi in cp.get(PKG + cls).getClassFile2().getMethods():
        if str(mi.getName()) != meth:
            continue
        ca = mi.getCodeAttribute()
        cpl, it = mi.getConstPool(), ca.iterator()
        while it.hasNext():
            p = it.next()
            if it.byteAt(p) not in (0xb6, 0xb7, 0xb8, 0xb9):
                continue
            idx = it.u16bitAt(p + 1)
            if cpl.getTag(idx) == CPool.CONST_InterfaceMethodref:
                c_, n_ = str(cpl.getInterfaceMethodrefClassName(idx)), str(cpl.getInterfaceMethodrefName(idx))
            else:
                c_, n_ = str(cpl.getMethodrefClassName(idx)), str(cpl.getMethodrefName(idx))
            out.append("%s.%s" % (c_.rsplit(".", 1)[-1], n_))
    return out


def run_kit(out, jar, scratch, _home):
    from jpype import JClass, JShort, JByte, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def jfield(cls, name):
        c = cls.class_ if hasattr(cls, "class_") else cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    # ---------------- the Item asset map with the test items (the 0.1.10 harness's Z stand-ins)
    Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IU = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemUtility")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    astore = us.allocateInstance(fake.toClass(AS.class_))
    dam = DAM()
    jfield(AS, "assetMap").set(astore, dam)
    jfield(Item, "ASSET_STORE").set(None, astore)
    amap = jfield(DAM, "assetMap").get(dam)
    unknown = Item.UNKNOWN
    items = {}

    def mk_item(iid, stack, usable):
        it = us.allocateInstance(Item.class_)
        for f in Item.class_.getDeclaredFields():
            if Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            f.set(it, f.get(unknown))
        u_ = IU()
        jfield(IU, "usable").setBoolean(u_, bool(usable))
        jfield(Item, "id").set(it, iid)
        jfield(Item, "maxStack").setInt(it, int(stack))
        jfield(Item, "utility").set(it, u_)
        amap.put(iid, it)
        items[iid] = it
        return it
    DAG, KUN, STICK, SWORD, SHIELD, TORCH = "Weapon_Daggers_Crude", "Weapon_Kunai_Crude", "Ingredient_Stick", "Weapon_Sword_Crude", "Weapon_Shield_Wood", "Furniture_Crude_Torch"
    # the Crude Kunai as SkyyArmory ships it: stack 1 (no MaxStack), NOT Utility.Usable (a main-hand throw)
    for iid, st_, usable in ((DAG, 1, False), (KUN, 1, False), (STICK, 1, False), (SWORD, 1, False), (SHIELD, 1, True), (TORCH, 25, True)):
        mk_item(iid, st_, usable)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    # ---------------- engine containers: hotbar + storage = SimpleItemContainer, the utility = the REAL InventoryComponent$Utility
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INVC = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    UT = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility")
    UCAP = int(INVC.DEFAULT_UTILITY_CAPACITY)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    UTN = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    for f_, t_ in (("h", ICN), ("s", ICN), ("u", UTN)):
        tinv.addField(CtF.make("public %s %s;" % (t_, f_), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s h, %s s, %s u) { super(); this.h = h; this.s = s; this.u = u; }" % (ICN, ICN, UTN), tinv))
    for src_ in ("public %s getHotbar() { return this.h; }" % ICN,
                 "public %s getStorage() { return this.s; }" % ICN,
                 "public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer getCombinedHotbarFirst() { return new "
                 "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer(new %s[] { this.h, this.s }); }" % ICN,
                 "public %s getUtility() { return this.u.getInventory(); }" % ICN,
                 "public byte getActiveUtilitySlot() { return this.u.getActiveSlot(); }",
                 "public void setActiveUtilitySlot(com.hypixel.hytale.component.Ref r, byte b, com.hypixel.hytale.component.ComponentAccessor a) "
                 "{ this.u.setActiveSlot(b, r, a); }",
                 "public com.hypixel.hytale.server.core.inventory.ItemStack getUtilityItem() { return this.u.getActiveItem(); }"):
        tinv.addMethod(CtM.make(src_, tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    tst = jp.makeClass("com.hypixel.hytale.component.SkyyTestStore", jp.get("com.hypixel.hytale.component.Store"))
    tst.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { }", tst))
    TStore = JClass(tst.toClass(JClass("com.hypixel.hytale.component.Store").class_))
    tph = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyTestPH", jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    tph.addField(CtF.make("public static java.util.ArrayList OUT;", tph))
    tph.addMethod(CtM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    tph.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    TPH = JClass(tph.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
    ArrayList, UUID, Paths = JClass("java.util.ArrayList"), JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    TPH.OUT = ArrayList()
    REF, PRN, PLA = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), \
        JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    SMSG = JClass("com.hypixel.hytale.protocol.packets.interface_.ServerMessage")
    J = lambda n: JClass(PKG + n)
    Kit, Store, KitCfg, Defs, Cfg = J("Kit"), J("ClassStore"), J("KitCfg"), J("ClassDefs"), J("ClassCfg")
    pdir = os.path.join(scratch, "kit", "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    NAMES = [str(x) for x in Defs.NAMES]
    ASN, WAR = NAMES.index("Assassin"), NAMES.index("Warrior")
    bridge = Cfg.bridge()
    K.check(str(Kit.TOP_CLASS) == "Assassin" and str(Kit.TOP_ITEM) == KUN and str(Kit.TOP_MARK) == "kitTopup0129"
            and str(KitCfg.K_ASSASSIN) == DAG + ":1," + KUN + ":1" and bool(KitCfg.known(KUN)), "KIT: the top-up constants + the 0.1.29 Assassin kit")
    ucls = [0]

    def player(hot=(), sto=(), uid=None, name="Tester"):
        h, s_, u = SIC(JShort(9)), SIC(JShort(36)), UT(JShort(UCAP))
        for cont, its in ((h, hot), (s_, sto)):
            for (sl, iid, q) in its:
                tx = cont.setItemStackForSlot(JShort(sl), IS(iid, q))
                assert tx.succeeded(), (iid, sl)
        jfield(UT, "activeSlot").setByte(u, JByte(-1))
        p = us.allocateInstance(PLA.class_)
        jfield(PLA, "inventory").set(p, TInv(h, s_, u))
        stv = us.allocateInstance(TStore.class_)
        ref = us.allocateInstance(REF.class_)
        jfield(REF, "store").set(ref, stv)
        jfield(REF, "index").setInt(ref, 0)
        pr = us.allocateInstance(PRN.class_)
        ucls[0] += 1
        if uid is None:
            uid = UUID.fromString("00000000-0000-0000-0000-%012x" % (0xb000 + ucls[0]))
        jfield(PRN, "uuid").set(pr, uid)
        jfield(PRN, "username").set(pr, name)
        jfield(PRN, "entity").set(pr, ref)
        jfield(PRN, "packetHandler").set(pr, us.allocateInstance(TPH.class_))
        return p, pr

    def counts(p):
        inv = p.getInventory()
        o = {}
        for cont in (inv.getHotbar(), inv.getStorage(), inv.getUtility()):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is None or it.isEmpty():
                    continue
                o[str(it.getItemId())] = o.get(str(it.getItemId()), 0) + int(it.getQuantity())
        return o

    def where(p, iid):
        inv = p.getInventory()
        res = []
        for tag, cont in (("h", inv.getHotbar()), ("s", inv.getStorage()), ("u", inv.getUtility())):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    res.append((tag, i, int(it.getQuantity())))
        return res
    JProps = JClass("java.util.Properties")

    def fpath(k):
        return os.path.join(pdir, k + ".properties")

    def kitfile(k):
        f = fpath(k)
        if not os.path.isfile(f):
            return {}
        pp = JProps()
        pp.load(JClass("java.io.StringReader")(open(f, encoding="latin-1").read()))
        return dict((str(x), str(pp.getProperty(x))) for x in pp.stringPropertyNames())

    def write(k, d):
        pp = JProps()
        for a, b in d.items():
            pp.setProperty(a, b)
        sw = JClass("java.io.StringWriter")()
        pp.store(sw, "SkyyClasses player")
        open(fpath(k), "w", encoding="latin-1").write(str(sw.toString()))
        Store.DATA.remove(k)
        Store.CLS.remove(k)
        Store.KITQ.remove(k)

    def raw(k):
        return open(fpath(k), "rb").read() if os.path.isfile(fpath(k)) else None

    def chat():
        o = []
        for x in TPH.OUT:
            if isinstance(x, SMSG):
                try:
                    o.append(str(x.message.rawText))
                except Exception:
                    o.append(str(jfield(JClass("com.hypixel.hytale.protocol.FormattedMessage"), "rawText").get(jfield(SMSG, "message").get(x))))
        return o

    def reset():
        TPH.OUT.clear()

    def relog(pr):
        """the player leaves and comes back (ClassQuit -> Kit.forget; the class file stays cached like a running server)"""
        Kit.forget(pr.getUuid())

    def restart():
        """a server restart: every cache empty, the files are read again"""
        Store.DATA.clear()
        Store.CLS.clear()
        Store.KITQ.clear()
        Kit.TOPDONE.clear()
        Kit.TOPTOLD.clear()
    TIP, WAIT = "[Classes] " + str(Kit.TOP_TIP), "[Classes] " + str(Kit.TOP_WAIT)
    GIVEN = {"class": "Assassin", "kit": "given", "kitClass": "Assassin", "kitAt": "1792120414555", "kitGivenAt": "1792120414882",
             "kitItems": DAG + ":1", "chosenAt": "1792120414000", "played": "Assassin"}
    # the live test world's Assassin file (read only; copied) = the shape of Skyy's friend's profile
    live_given, live_name = None, None
    lp = os.path.join(LIVE, "players")
    if os.path.isdir(lp):
        for n in sorted(os.listdir(lp)):
            if n.endswith(".properties"):
                pp = JProps()
                pp.load(JClass("java.io.StringReader")(open(os.path.join(lp, n), encoding="latin-1").read()))
                d = dict((str(x), str(pp.getProperty(x))) for x in pp.stringPropertyNames())
                if d.get("class") == "Assassin" and d.get("kit") == "given" and d.get("kitClass") == "Assassin" and KUN not in d.get("kitItems", ""):
                    live_given, live_name = n[:-len(".properties")], n
                    break

    # ---------------- K1: a NEW Assassin: the kit = daggers + kunai in the hotbar; the top-up writes its marker only
    reset()
    p, pr = player(name="NewAssassin")
    k = str(pr.getUuid())
    write(k, {"class": "Assassin"})
    K.check(int(Store.markKitKey(k, "Assassin")) == 0, "K1: the new profile's kit is pending")
    K.check(Kit.give(pr, p, k, ASN, False, None) is None, "K1: the automatic kit was given")
    K.check(where(p, DAG) == [("h", 0, 1)] and where(p, KUN) == [("h", 1, 1)] and counts(p) == {DAG: 1, KUN: 1},
            "K1: Crude Daggers + ONE Crude Kunai in the HOTBAR (not the utility slot): %s" % counts(p))
    K.check("[Classes] Your Assassin kit is in your hotbar: Daggers Crude x1, Kunai Crude x1." in chat(), "K1: the kit line names both: %s" % chat())
    kf = kitfile(k)
    K.check(kf.get("kit") == "given" and kf.get("kitItems") == DAG + ":1," + KUN + ":1" and not kf.get("kitOwed"), "K1: the kit record: %s" % kf)
    K.check(int(Kit.topConsider(pr)) == 1 and kitfile(k).get("kitTopup0129", "").endswith(" had") and kitfile(k).get("kit") == "given"
            and counts(p) == {DAG: 1, KUN: 1}, "K1: the top-up sees the kunai in the record: marker 'had' only, nothing owed, no second kunai")
    b = raw(k)
    K.check(int(Kit.topConsider(pr)) == -1 and raw(k) == b, "K1: looked at this session -> nothing more")
    relog(pr)
    K.check(int(Kit.topConsider(pr)) == 3 and raw(k) == b, "K1: re-login -> the marker is there (3), the file is not written")

    # ---------------- K2: an EXISTING Assassin (the friend): the kunai owed once, delivered by the quiet claim
    reset()
    if live_given:
        uid = UUID.fromString(live_given[:36])
        shutil.copy(os.path.join(lp, live_name), fpath(live_given))
        k = live_given
        print("K2: using a scratch COPY of the live test world's Assassin file %s" % live_name)
    else:
        uid = UUID.fromString("00000000-0000-0000-0000-00000000c002")
        k = str(uid)
        write(k, GIVEN)
        print("K2: no live Assassin file with a pre-0.1.29 kit - a synthetic one")
    Store.DATA.remove(k)
    p, pr = player(hot=[(0, DAG, 1), (1, STICK, 1)], uid=uid, name="Friend")
    before = kitfile(k)
    r = int(Kit.topConsider(pr))
    kf = kitfile(k)
    K.check(r == 2 and kf.get("kit") == "owed" and kf.get("kitOwed") == KUN + ":1" and kf.get("kitItems") == before.get("kitItems") + "," + KUN + ":1"
            and kf.get("kitTopup0129", "").endswith(" owed " + KUN + ":1") and str(Store.KITQ.get(k)) == "owed",
            "K2: ONE save: marker + kit=owed + kitOwed=%s:1 + kitItems += it; KITQ owed (%s)" % (KUN, kf))
    K.check(all(kf.get(x) == before.get(x) for x in before if x not in ("kit", "kitItems")), "K2: every other key of the file kept")
    K.check(counts(p) == {DAG: 1, STICK: 1}, "K2: the top-up itself moves no item (the claim does, on the world thread)")
    Kit.claim(pr, p, k, True)
    K.check(where(p, KUN) == [("h", 2, 1)] and counts(p) == {DAG: 1, STICK: 1, KUN: 1}, "K2: the quiet (arrival) claim puts the kunai into the hotbar: %s" % where(p, KUN))
    kf = kitfile(k)
    K.check(kf.get("kit") == "given" and not kf.get("kitOwed") and "kitTopup0129" in kf, "K2: the record: given, nothing owed, the marker stays (%s)" % kf)
    K.check("[Classes] Collected 1 kit item: Kunai Crude x1." in chat() and TIP in chat(), "K2: the collected line + the kunai tip: %s" % chat())
    K.check(Store.KITQ.get(k) is None, "K2: nothing queued any more")
    b = raw(k)
    for what, fn in (("the same session", lambda: None), ("re-login", lambda: relog(pr)), ("a server restart", restart)):
        fn()
        r = int(Kit.topConsider(pr))
        Kit.claim(pr, p, k, True)
        K.check(r in (-1, 3) and raw(k) == b and counts(p) == {DAG: 1, STICK: 1, KUN: 1}, "K2: %s -> no second kunai, the file untouched (%d)" % (what, r))
    reset()
    Kit.claim(pr, p, k, False)
    sl = str(Kit.stateLine(Store.loadKey(k)))
    K.check(chat() == ["[Classes] Nothing is waiting."] and counts(p) == {DAG: 1, STICK: 1, KUN: 1}
            and sl.startswith("Nothing is waiting. Your Assassin kit (Daggers Crude x1, Kunai Crude x1) was given"),
            "K2: /class kit afterwards: nothing more; its state line lists the kunai: %r" % sl)

    # ---------------- K3: profile switch: two profiles of one player; each topped up on its own, once
    reset()
    uid = UUID.fromString("00000000-0000-0000-0000-00000000c003")
    us3 = str(uid)
    cur = [us3 + "-p1"]

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, o):
            return cur[0]
    bridge.put("profile:fn:key", KeyFn())
    write(us3 + "-p1", GIVEN)
    write(us3 + "-p2", GIVEN)
    write(us3 + "-p3", dict(GIVEN, **{"class": "Warrior", "kitClass": "Warrior", "kitItems": SWORD + ":1", "played": "Warrior"}))
    p, pr = player(uid=uid, name="Switcher")
    bridge.put("profile:class:" + us3, "Assassin")
    K.check(int(Kit.topConsider(pr)) == 2 and kitfile(us3 + "-p1").get("kitOwed") == KUN + ":1" and "kitTopup0129" not in kitfile(us3 + "-p2"),
            "K3: profile 1 active -> only profile 1 is topped up")
    Kit.claim(pr, p, us3 + "-p1", True)
    K.check(counts(p) == {KUN: 1}, "K3: profile 1 got its kunai")
    # switch: SkyyProfiles marks the player busy while it swaps the inventory -> nothing; then profile 2 (its own inventory)
    bridge.put("profile:busy:" + us3, "1")
    cur[0] = us3 + "-p2"
    b2 = raw(us3 + "-p2")
    K.check(int(Kit.topConsider(pr)) == -1 and raw(us3 + "-p2") == b2, "K3: while the profile is loading (profile:busy) nothing is written")
    bridge.remove("profile:busy:" + us3)
    p2, _ = player(uid=uid, name="Switcher")   # profile 2's own inventory (SkyyProfiles swapped it)
    K.check(int(Kit.topConsider(pr)) == 2 and kitfile(us3 + "-p2").get("kitOwed") == KUN + ":1", "K3: profile 2 active -> profile 2 topped up on its own")
    Kit.claim(pr, p2, us3 + "-p2", True)
    K.check(counts(p2) == {KUN: 1}, "K3: profile 2 got its kunai")
    # profile 3 = a Warrior: nothing
    cur[0] = us3 + "-p3"
    bridge.put("profile:class:" + us3, "Warrior")
    b3 = raw(us3 + "-p3")
    K.check(int(Kit.topConsider(pr)) == 0 and raw(us3 + "-p3") == b3, "K3: profile 3 (a Warrior) -> nothing written")
    # back to profile 1 and 2, after a re-login and after a restart: never a second
    for what, fn in (("switch back", lambda: None), ("re-login", lambda: relog(pr)), ("restart", restart)):
        fn()
        bridge.put("profile:class:" + us3, "Assassin")
        for kk in (us3 + "-p1", us3 + "-p2"):
            cur[0] = kk
            bk = raw(kk)
            r = int(Kit.topConsider(pr))
            Kit.claim(pr, p if kk.endswith("p1") else p2, kk, True)
            K.check(r in (-1, 3) and raw(kk) == bk, "K3: %s to %s -> nothing new (%d)" % (what, kk[-2:], r))
    K.check(counts(p) == {KUN: 1} and counts(p2) == {KUN: 1}, "K3: one kunai per profile, in total")
    bridge.remove("profile:fn:key")
    bridge.remove("profile:class:" + us3)

    # ---------------- K4: a FULL hotbar: the waiting line once per session; re-login retries; /class kit = storage
    reset()
    p, pr = player(hot=[(i, STICK, 1) for i in range(9)], name="FullBar")
    k = str(pr.getUuid())
    write(k, GIVEN)
    K.check(int(Kit.topConsider(pr)) == 2, "K4: topped up (owed)")
    Kit.claim(pr, p, k, True)
    K.check(not where(p, KUN) and kitfile(k).get("kit") == "owed" and chat().count(WAIT) == 1, "K4: hotbar full -> nothing moves, still owed, the waiting line: %s" % chat())
    Kit.claim(pr, p, k, True)
    K.check(chat().count(WAIT) == 1 and kitfile(k).get("kitOwed") == KUN + ":1", "K4: a second world arrival this session: no second line, still owed")
    relog(pr)
    Kit.claim(pr, p, k, True)
    K.check(chat().count(WAIT) == 2 and not where(p, KUN), "K4: after a re-login the line comes again (retried at every login)")
    K.check(int(Kit.topConsider(pr)) == 3 and kitfile(k).get("kitOwed") == KUN + ":1", "K4: the re-login's top-up check: marker -> not owed twice")
    reset()
    Kit.claim(pr, p, k, False)
    K.check(where(p, KUN) == [("s", 0, 1)] and kitfile(k).get("kit") == "given" and TIP in chat(), "K4: /class kit -> the kunai into storage + the tip: %s" % chat())
    restart()
    K.check(int(Kit.topConsider(pr)) == 3 and counts(p).get(KUN) == 1, "K4: after a restart: still one kunai")
    # hotbar AND storage full: /class kit says so, nothing moves, still owed
    reset()
    p, pr = player(hot=[(i, STICK, 1) for i in range(9)], sto=[(i, STICK, 1) for i in range(36)], name="AllFull")
    k = str(pr.getUuid())
    write(k, GIVEN)
    Kit.topConsider(pr)
    Kit.claim(pr, p, k, False)
    K.check(not where(p, KUN) and kitfile(k).get("kitOwed") == KUN + ":1" and any("hotbar and storage are full" in c for c in chat()),
            "K4: hotbar + storage full -> /class kit says so, the kunai stays owed: %s" % chat())

    # ---------------- K5: nothing for every other case (no write at all)
    cases = [("a Warrior (given)", dict(GIVEN, **{"class": "Warrior", "kitClass": "Warrior", "kitItems": SWORD + ":1"}), "Warrior"),
             ("an Assassin with a pending kit", {"class": "Assassin", "kit": "pending", "kitClass": "Assassin"}, None),
             ("an Assassin who picked before kits (old)", {"class": "Assassin", "kit": "old"}, None),
             ("an Assassin whose kit was off", {"class": "Assassin", "kit": "off", "kitClass": "Assassin"}, None),
             ("an Assassin without a kit record", {"class": "Assassin"}, None),
             ("an interrupted give (given + in-flight kitOwed)", dict(GIVEN, kitOwed=DAG + ":1"), None),
             ("an Assassin whose kit was another class's", dict(GIVEN, kitClass="Warrior", kitItems=SWORD + ":1"), None)]
    for what, d, _c in cases:
        reset()
        p, pr = player(name="Other")
        k = str(pr.getUuid())
        write(k, d)
        b = raw(k)
        r = int(Kit.topConsider(pr))
        K.check(r == 0 and raw(k) == b and not counts(p) and not chat(), "K5: %s -> nothing (no marker, no item): %d" % (what, r))
    # review fix: no class known yet (the file has none / the class is not published at the first tick) = -1, NOT marked as looked at:
    # the next tick tries again and tops the profile up once the class is known
    reset()
    p, pr = player(name="NoClassYet")
    k = str(pr.getUuid())
    noc = dict(GIVEN)
    del noc["class"]
    write(k, noc)
    b = raw(k)
    r = int(Kit.topConsider(pr))
    K.check(r == -1 and raw(k) == b and not Kit.TOPDONE.containsKey(k) and not counts(p),
            "K5: no class known yet -> -1, nothing written, NOT marked looked-at (retried next tick): %d" % r)
    K.check(int(Kit.topConsider(pr)) == -1 and not Kit.TOPDONE.containsKey(k), "K5: ... the next tick asks again (still no class)")
    bridge.put("profile:class:" + str(pr.getUuid()), "Assassin")   # the class is published (SkyyProfiles) a moment later
    r = int(Kit.topConsider(pr))
    K.check(r == 2 and kitfile(k).get("kitOwed") == KUN + ":1" and Kit.TOPDONE.containsKey(k), "K5: ... once the class is known, the same session tops it up (%d)" % r)
    bridge.remove("profile:class:" + str(pr.getUuid()))
    # a real other class IS marked looked-at for the session
    reset()
    p, pr = player(name="RealWarrior")
    k = str(pr.getUuid())
    write(k, dict(GIVEN, **{"class": "Warrior", "kitClass": "Warrior", "kitItems": SWORD + ":1"}))
    K.check(int(Kit.topConsider(pr)) == 0 and Kit.TOPDONE.containsKey(k), "K5: a real Warrior -> 0 and marked looked-at for the session")
    # a hand-edited kit without the kunai / no SkyyArmory (unknown kunai): nothing, looked at again next session
    for what, on, off in (("a hand-edited kit.Assassin without the kunai", lambda: setattr(KitCfg, "K_ASSASSIN", DAG + ":1"),
                           lambda: setattr(KitCfg, "K_ASSASSIN", DAG + ":1," + KUN + ":1")),
                          ("no SkyyArmory (the kunai is unknown)", lambda: amap.remove(KUN), lambda: amap.put(KUN, items[KUN]))):
        reset()
        p, pr = player(name="Edge")
        k = str(pr.getUuid())
        write(k, GIVEN)
        b = raw(k)
        on()
        r = int(Kit.topConsider(pr))
        off()
        K.check(r == 0 and raw(k) == b and "kitTopup0129" not in kitfile(k), "K5: %s -> nothing written (%d)" % (what, r))
        relog(pr)
        K.check(int(Kit.topConsider(pr)) == 2, "K5: ... and once it is back (next session) the profile is topped up")
    # kits off: topTick does nothing (returns before it looks at a player)
    KitCfg.ON = False
    try:
        Kit.topTick()
        K.check(True, "K5: kits off -> topTick returns at once")
    except Exception as e:
        K.check(False, "K5: kits off -> topTick returns at once (%s)" % e)
    KitCfg.ON = True

    # ---------------- K6: an Assassin with items already owed: the kunai joins the owed list; one claim gives both
    reset()
    p, pr = player(name="Owed")
    k = str(pr.getUuid())
    write(k, dict(GIVEN, kit="owed", kitOwed=DAG + ":1"))
    K.check(int(Kit.topConsider(pr)) == 2 and kitfile(k).get("kitOwed") == DAG + ":1," + KUN + ":1", "K6: the kunai joins the owed daggers")
    Kit.claim(pr, p, k, True)
    K.check(counts(p) == {DAG: 1, KUN: 1} and kitfile(k).get("kit") == "given" and not kitfile(k).get("kitOwed"), "K6: one quiet claim gives both")
    # a record that already OWES the kunai (an admin's kit): marker only
    reset()
    p, pr = player(name="OwedKunai")
    k = str(pr.getUuid())
    write(k, dict(GIVEN, kit="owed", kitOwed=KUN + ":1"))
    K.check(int(Kit.topConsider(pr)) == 1 and kitfile(k).get("kitOwed") == KUN + ":1", "K6: the kunai already owed -> marker only, owed once")

    # ---------------- K7: the claim reads kitClaimBegin's own list; the top-up hands the kunai to the owed claim (bytecode order)
    cl = ordered_calls(jar, "Kit", "claim")
    i_b = cl.index("ClassStore.kitClaimBegin") if "ClassStore.kitClaimBegin" in cl else -1
    K.check(i_b >= 0 and "KitCfg.parse" in cl[i_b:] and cl.index("Kit.put") > cl.index("KitCfg.parse", i_b) and cl.count("KitCfg.parse") == 2,
            "K7: claim: kitClaimBegin -> KitCfg.parse (of its list) -> put")
    tc = ordered_calls(jar, "Kit", "topConsider")
    K.check(tc.index("Kit.busy") < tc.index("ClassStore.classIndex") < tc.index("KitCfg.known") < tc.index("ClassStore.topupKey") < tc.index("Kit.owedLater"),
            "K7: topConsider: busy -> class -> known item -> topupKey -> owedLater (the arrival claim path)")
    tt = ordered_calls(jar, "ClassTick", "run")
    K.check(tt.index("Kit.tick") < tt.index("Kit.topTick"), "K7: the 2 s ClassTick runs Kit.topTick after Kit.tick")
    st = ordered_calls(jar, "SkyyClassesPlugin", "setup")
    K.check(st.index("ClassCfg.migrate0110") < st.index("ClassCfg.migrate0129") < st.index("ClassCfg.load"), "K7: setup: migrate0110 -> migrate0129 -> load")
    fg = ordered_calls(jar, "Kit", "forget")
    K.check(fg.count("Kit.dropKeys") == 2, "K7: Kit.forget drops TOPDONE + TOPTOLD (a re-login looks again)")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_old():
    sc = os.path.join(os.path.dirname(SCRATCH), "cls-old")
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyclasses_0.1.28.py"), "--jar", JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(os.path.join(os.path.dirname(SCRATCH), "cls-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAIL: "):] for l in lines if l.strip().startswith("FAIL: ")]
    unexp = [l.strip()[len("OLD unexpected: "):] for l in lines if l.strip().startswith("OLD unexpected: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED_OLD if f.startswith(e[0])] else bad).append(f)
    # the nested harnesses' unexpected lines: only their compare phases may differ (they compare older versions against our jar), and the
    # 0.1.26 harness can no longer reach its summary here: its HK.run asserts SkyyClasses-0.1.25.jar (its compare's old jar), which the
    # tidy removed from disk (the same on the 0.1.28 jar) - its exec + cwnew phases are run directly instead (run_h26 below)
    bad += ["nested: " + x for x in unexp if not (x.startswith("compare: ") or x.startswith("nested 0.1.26: compare: ")
                                                  or (x == "OLD: the 0.1.26 harness ran to its summary" and not os.path.isfile(H26_OLD_JAR)))]
    return oks, bad, exp, unexp, p.returncode


H26_OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.25.jar")


def run_h26():
    """the 0.1.26 harness's own executed phases on our jar (X1-X70 on the engine stand-ins + the config write proof of the new jar)"""
    d = os.path.join(os.path.dirname(SCRATCH), "h26")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "tmp"))
    os.makedirs(os.path.join(d, "fake"))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(d, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    res = {}
    for ph in ("exec", "cwnew"):
        o = os.path.join(d, ph + ".json")
        p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyclasses_0.1.26.py"), "--phase", ph, "--out", o, "--dir", d, "--jar", JAR],
                           env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        res[ph] = (p.returncode, json.load(open(o)) if os.path.isfile(o) else None)
    shutil.rmtree(d, ignore_errors=True)
    return res


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, unexp, rc = run_old()
        print("OLD. the 0.1.28 harness on the 0.1.29 jar: %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.1.29: %s" % e[:240])
        for x in unexp:
            print("  note (old, nested): %s" % x[:240])
        for b in bad:
            print("  OLD unexpected: %s" % b[:400])
        HK.check(bool(oks), "OLD: the 0.1.28 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the listed identity checks: %s" % bad[:5])
        for ph, (rc_, r_) in run_h26().items():
            HK.check(rc_ == 0 and r_ is not None and not r_["fails"] and r_["ok"] > 0, "OLD-26 %s: the 0.1.26 harness's %s phase on the 0.1.29 jar: %s ok, fails %s"
                     % (ph, ph, r_ and r_["ok"], (r_ or {}).get("fails", "no result")[:3]))
            print("OLD-26. the 0.1.26 harness's %s phase on the 0.1.29 jar: %s ok, %s fail(s)" % (ph, r_ and r_["ok"], r_ and len(r_["fails"])))
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("mgold", run_mgold), ("mig", run_mig), ("kit", run_kit)], script=__file__)
