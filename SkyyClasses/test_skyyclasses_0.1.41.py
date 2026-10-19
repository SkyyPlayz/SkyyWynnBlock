"""Harness for SkyyClasses 0.1.41 (Sacred Heal cooldown 8 s in every shape + the one-time update ClassCfg.migrate0141;
tools/classes_0_1_41_patch.py). Build first:
    python tools/classes_0_1_41_patch.py && python SkyyClasses/build_skyyclasses_0.1.41.py
    python SkyyClasses/test_skyyclasses_0.1.41.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/cr41/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.40 -> 0.1.41: exactly the planned members (EXPECT)
  O   old      dumps every static number of AbilCfg on the OLD 0.1.40 jar (the baseline for X)
  X   exec     AbilCfg.S_CD / _SP / _AI / _CR = 8 (were 14 / 14 / 14 / 16); every other AbilCfg number identical to 0.1.40; the Server Setup
               rows' defaults = 8; the old-default table + marker
  MIG the one-time update on scratch files (the live test world's config COPY when it still holds the old rows: History first, one Undo
      line per row, INFO, runs once, load() reads 8; a hand-edited row kept + noted, the others still updated; marker right above the
      first row; LF + CRLF byte-exact; chain 0.1.10 -> 0.1.29 -> 0.1.32 -> 0.1.41; a fresh default file is never rewritten)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order: migrations, load, CfgPub): start 1 writes only
      the update (config.properties + its History version + the change log), start 2 writes nothing; the live folder is only read
  AA  engine-access audit
"""
import os, sys, json, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, OLD = "0.1.41", "0.1.40"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "cr41", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
ADDED = []
EXPECT = {
    "ClassCfg": ["+f MG41_KEY", "+f MG41_MARK", "+f MG41_MARK_ID", "+f MG41_NEW", "+f MG41_OLD", "+f MG41_WHO", "+f MG41_WHY",
                 "+m migrate0141", "~<clinit>"],
    "AbilCfg": ["~<clinit>", "~m read"],                        # the 4 cooldown defaults (field + read fallback)
    "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],       # the config kit's row table (the 4 defaults + the default file text)
    "SkyyClassesPlugin": ["~m setup"],                          # migrate0141 (and the version text)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}
KEYS = ["ab.SacredHeal.%s.cooldown" % s for s in ("walk", "sprint", "air", "crouch")]
OLDV = ["14", "14", "14", "16"]
CDF = ["S_CD", "S_CD_SP", "S_CD_AI", "S_CD_CR"]


def live_text():
    f = os.path.join(LIVE, "config.properties")
    return open(f, "rb").read().decode("latin-1") if os.path.isfile(f) else None


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def dump(cls):
    from jpype import JClass
    C = JClass(PKG + cls)
    Mod = JClass("java.lang.reflect.Modifier")
    out = {}
    for f in C.class_.getDeclaredFields():
        if not Mod.isStatic(f.getModifiers()):
            continue
        t = str(f.getType().getName())
        if t not in ("double", "int", "long", "boolean", "java.lang.String"):
            continue
        f.setAccessible(True)
        v = f.get(None)
        out[str(f.getName())] = None if v is None else str(v)
    return out


def run_old(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=True)
    d = dump("AbilCfg")
    json.dump(d, open(os.path.join(scratch, "old-abilcfg.json"), "w"))
    K.check(len(d) > 50 and float(d["S_CD"]) == 14.0 and float(d["S_CD_CR"]) == 16.0, "O: AbilCfg of 0.1.40 dumped (%d fields; S_CD 14, crouch 16)" % len(d))
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    new = dump("AbilCfg")
    old = json.load(open(os.path.join(scratch, "old-abilcfg.json")))
    K.eq([float(new[f]) for f in CDF], [8.0] * 4, "X: Sacred Heal cooldown 8 s walking / sprinting / mid-air / crouching")
    diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    K.eq(diff, sorted(CDF), "X: only the 4 Sacred Heal cooldowns changed in AbilCfg (Meteor 14 s, Mana, Stamina ... identical)")
    K.check(float(new["S_MANA"]) == 18.0 and float(new["S_STAM"]) == 2.0 and float(new["M_CD"]) == 14.0, "X: Sacred Heal 18 Mana + 2 Stamina, Meteor 14 s unchanged")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.eq([rows[k][4] for k in KEYS], ["8"] * 4, "X: the 4 Server Setup rows default to 8")
    Cfg = JClass(PKG + "ClassCfg")
    K.eq([str(x) for x in Cfg.MG41_KEY], KEYS, "X: the update's keys")
    K.eq([str(x) for x in Cfg.MG41_OLD], OLDV, "X: the update's old defaults 14 / 14 / 14 / 16")
    K.eq([str(x) for x in Cfg.MG41_NEW], ["8"] * 4, "X: the update's new defaults")
    K.check(str(Cfg.MG41_WHO) == "SkyyClasses 0.1.41" and "=" not in str(Cfg.MG41_MARK) and str(Cfg.MG41_MARK_ID) in str(Cfg.MG41_MARK), "X: who + marker")
    K.save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Cfg, AC = JClass(PKG + "ClassCfg"), JClass(PKG + "AbilCfg")
    Paths = JClass("java.nio.file.Paths")
    MARK, WHO = str(Cfg.MG41_MARK), str(Cfg.MG41_WHO)
    sample = ("# SkyyClasses config\nswitchCost=5000\nab.SacredHeal.walk.mana=18\nab.SacredHeal.walk.stamina=2\n%s=14\nab.SacredHeal.heal=25\n"
              "ab.Meteor.sprint.cooldown=14\n%s=14\n%s=14\n%s=16\nab.ShieldBubble.sprint.cooldown=24\n" % tuple(KEYS))

    def upd(text):
        r = Cfg.mgUpdateT(text, Cfg.MG41_KEY, Cfg.MG41_OLD, Cfg.MG41_NEW, Cfg.MG41_WHY, Cfg.MG41_MARK, Cfg.MG41_MARK_ID, "0.1.41")
        return None if r is None else [str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]]

    def want_of(t, nl, skip=()):
        w = t
        for k, o in zip(KEYS, OLDV):
            if k in skip:
                continue
            w = w.replace(nl + k + "=" + o + nl, nl + k + "=8" + nl, 1)
        return w.replace(nl + KEYS[0] + "=", nl + MARK + nl + KEYS[0] + "=", 1)

    def untouched_all(t):
        ls = t.replace("\r\n", "\n").split("\n")
        return all((k + "=" + o) in ls for k, o in zip(KEYS, OLDV))
    lt = live_text()
    base = lt if (lt is not None and untouched_all(lt)) else sample
    for tag, t in (("LF", base.replace("\r\n", "\n")), ("CRLF", base.replace("\r\n", "\n").replace("\n", "\r\n"))):
        nl = "\r\n" if tag == "CRLF" else "\n"
        r = upd(t)
        want = want_of(t, nl)
        K.check(r is not None and r[0] == want and want != t, "MIG %s: the 4 untouched rows -> 8, the marker right above the walking row, every other byte kept" % tag)
        K.check(r is not None and r[3] == sum([[k, o, "8"] for k, o in zip(KEYS, OLDV)], []) and r[2] == [], "MIG %s: 4 change rows (%s)" % (tag, r and r[1][:160]))
    t = sample.replace(KEYS[3] + "=16", KEYS[3] + "=12")
    r = upd(t)
    K.check(r is not None and r[0] == want_of(t, "\n", skip=(KEYS[3],)) and r[3] == sum([[k, o, "8"] for k, o in zip(KEYS[:3], OLDV[:3])], [])
            and len(r[2]) == 1 and r[2][0].startswith(KEYS[3] + "=12 kept (custom)"), "MIG: a hand-edited crouch row (12) is kept and noted; the other 3 updated: %s" % (r and r[2]))
    t = sample.replace(KEYS[0] + "=14", KEYS[0] + "=8")
    r = upd(t)
    K.check(r is not None and r[2] == [] and len(r[3]) == 9 and (KEYS[0] + "=8") in r[0], "MIG: a row already at 8 (set in Server Setup) is left alone, not noted")
    t = "\n".join(l for l in sample.split("\n") if not l.startswith("ab.SacredHeal."))
    r = upd(t)
    K.check(r is not None and r[0] == MARK + "\n" + t and r[3] == [] and r[2] == [], "MIG: no rows (the default = 8): only the marker, on top")
    K.check(upd(MARK + "\n" + sample) is None, "MIG: the marker in a comment line = nothing to do (runs once)")
    K.check(upd(str(Cfg.MG32_MARK) + "\n" + sample) is not None and Cfg.mgUpdateT(MARK + "\n" + sample, Cfg.MG32_KEY, Cfg.MG32_OLD, Cfg.MG32_NEW, Cfg.MG32_WHY,
            Cfg.MG32_MARK, Cfg.MG32_MARK_ID, "0.1.32") is not None, "MIG: the 0.1.32 / 0.1.41 markers never stand for each other")
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

    rd = lambda f: open(f, "rb").read()
    live_ok = lt is not None
    home, f = setup("live", copy_live=True) if live_ok else setup("live", text=sample)
    Cfg.migrate0110()
    Cfg.migrate0129()
    Cfg.migrate0132()
    b1, h1, l1 = rd(f), hist(home), logl(home)
    t1o = b1.decode("latin-1")
    untouched = untouched_all(t1o)
    r = str(Cfg.migrate0141())
    t1 = rd(f).decode("latin-1")
    print("MIG: %s config: %s -> %r" % ("the live test world's" if live_ok else "a sample", "untouched" if untouched else "edited / missing", r[:300]))
    if untouched:
        nl = "\r\n" if "\r\n" in t1o else "\n"
        K.check(t1 == want_of(t1o, nl), "MIG live copy: the 4 rows -> 8 + the marker, every other byte kept")
        rows = [l.split("\t") for l in logl(home)[len(l1):]]
        K.check(len(rows) == 4 and all(x[1:4] == [WHO, "-", "update"] and x[4:8] == [k, o, "8", "ok"] for x, k, o in zip(rows, KEYS, OLDV)),
                "MIG live copy: 4 config-changes.log lines in the Undo format: %s" % rows)
        K.check(KEYS[0] + " 14 -> 8" in r and KEYS[3] + " 16 -> 8" in r and "config-history" in r, "MIG live copy: the INFO line")
    else:
        K.check(MARK in t1, "MIG live copy: marked (%r)" % r[:200])
    K.check(len(hist(home)) == len(h1) + 1 and any(rd(os.path.join(home, "config-history", x)) == b1 for x in hist(home)) and all(x in hist(home) for x in h1),
            "MIG live copy: one new History version with the old bytes; the old versions kept")
    K.check(WHO in open(os.path.join(home, "config-history", "index.log"), encoding="utf8").read(), "MIG: the History index names the update")
    b2, h2, l2 = rd(f), hist(home), logl(home)
    K.check(str(Cfg.migrate0141()) == "" and rd(f) == b2 and hist(home) == h2 and logl(home) == l2, "MIG live copy: the second start changes nothing")
    Cfg.load()
    if untouched:
        K.check([float(getattr(AC, x)) for x in CDF] == [8.0] * 4, "MIG live copy: load() reads 8 s for all 4 shapes")
    # hand-edited: kept + noted, the rest updated
    home, f = setup("edited", text=sample.replace(KEYS[1] + "=14", KEYS[1] + "=10"))
    r = str(Cfg.migrate0141())
    Cfg.load()
    K.check([float(getattr(AC, x)) for x in CDF] == [8.0, 10.0, 8.0, 8.0] and "kept (custom)" in r and len(logl(home)) == 3,
            "MIG edited: the hand-edited sprint row (10) is kept, the other 3 read 8, 3 log lines (%r)" % r[:200])
    # a 0.1.9-era CRLF file: the four updates in setup's order
    home, f = setup("chain", text=("kit.Warrior=Weapon_Sword_Crude:1\nkit.Assassin=Weapon_Daggers_Crude:1\npriestHeal.selfPercent=50\n%s=%s\n" % ("ab.ArcaneBreach.numbers", str(Cfg.MG32_OLD[0])) + sample).replace("\n", "\r\n"))
    Cfg.migrate0110()
    Cfg.migrate0129()
    Cfg.migrate0132()
    Cfg.migrate0141()
    tc = rd(f).decode("latin-1")
    K.check(all((k + "=8\r\n") in tc for k in KEYS) and "kit.Assassin=Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1\r\n" in tc and tc.count(MARK) == 1
            and tc.count(str(Cfg.MG32_MARK)) == 1 and tc.count(str(Cfg.MG29_MARK)) == 1 and tc.count(str(Cfg.MG_MARK)) == 1
            and "\n" not in tc.replace("\r\n", ""), "MIG chain: all four updates, CRLF kept")
    K.check(len(hist(home)) == 4 and sorted(l.split("\t")[1] for l in logl(home)).count(WHO) == 4, "MIG chain: four History versions, four 0.1.41 log lines")
    # fresh: load() writes the 0.1.41 default (with the marker); the update never rewrites it
    home, f = setup("fresh")
    Cfg.load()
    fb = rd(f)
    ft = fb.decode("latin-1").replace("\r\n", "\n")
    K.check(str(Cfg.migrate0141()) == "" and rd(f) == fb and not hist(home), "MIG fresh: the 0.1.41 default file is never rewritten by the update")
    K.check((MARK + "\n" + KEYS[0] + "=8\n") in ft and all(("\n" + k + "=8\n") in ft for k in KEYS), "MIG fresh: the default file holds the marker + 8 for all 4 rows")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "m41": str(Cfg.migrate0141()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":
        okset = all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch)
        K.check(okset and "config.properties" in ch and o["m41"].startswith("config.properties"),
                "ST start 1 on a scratch COPY of the live data: only the one-time update is written (%s) %s" % (ch, o["m41"][:200]))
    else:
        K.check(not ch and o["m41"] == "", "ST start 2: nothing written (%s)" % ch)
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("old", run_old), ("exec", run_exec), ("mig", run_mig), ("st1", run_st1), ("st2", run_st2)], script=__file__)
