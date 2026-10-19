"""Harness for SkyyArmory 0.1.40 (the Soul Cage locks on faster: soul.stabilize about halved + migrate040; tools/armory_0_1_40_patch.py). Build first:
    python tools/armory_0_1_40_patch.py && python SkyyArmory/build_skyyarmory_0.1.40.py

    python SkyyArmory/test_skyyarmory_0.1.40.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.39 -> 0.1.40: exactly the planned members (EXPECT); non-class entries: manifest.json + server.lang only
  L   lang     server.lang vs 0.1.39 = exactly the 16 Soul Orb / Cage descriptions, each only its "Look N s" number (the new default)
  X   exec     the defaults (16 tiers: about half of 0.1.39, the ladder falls), the loader (defaults, missing lines, clamps), the Server Setup row
               help text, Soul.stabMs; migrate040's text step (old defaults -> new + marker above the first key, hand values kept + named,
               CRLF kept, marker = never again, no soul lines = marker only); a 0.1.20 file runs 2.5 -> 1.75 (migrate021) -> 0.9 (migrate040)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): the 1st start changes exactly
               the 8 soul.stabilize lines + the marker (History copy + 8 change-log lines), the 2nd start changes nothing
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the feel of a 0.5 - 0.9 s lock-on.
Exit code 1 on any failure.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.40", "0.1.39"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "a140", "harness")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
LANG = "Server/Languages/en-US/server.lang"
TIERS = ["Orb", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"] + [w + "_SkyWynn" for w in
         ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen")]
OLD16 = ["1.75", "1.6", "1.45", "1.35", "1.2", "1.1", "1.05", "1", "1.3", "1.25", "1.17", "1.13", "1.08", "1.07", "1.03", "1.02"]
NEW16 = ["0.9", "0.8", "0.75", "0.7", "0.6", "0.55", "0.52", "0.5", "0.66", "0.63", "0.58", "0.57", "0.54", "0.53", "0.51", "0.5"]
EXPECT = {"ArmoryCfg": ["+f M40_KEYS", "+f M40_OLD", "+f M40_NEW", "+f M40_MARK", "+f M40_MARK_ID", "+f M40_WHO", "+f M40_LAST",
                        "+m m40Key", "+m m40Update", "+m m40Log", "+m migrate040", "~<clinit>",
                        "~m load", "~m reloadAll", "~m useDefaults"],          # (DEF_CFG, an inlined constant)
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],          # DEF_CFG + the soul.stabilize row (help text)
          "SkyyArmoryPlugin": ["~m setup", "~m start"]}          # migrate040 + its line, the version text
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040")

_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    E = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(["manifest.json", LANG])
        return E(self, got, want, what)
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = E
HK.run_compare = _compare


def setup_jvm(jar, *more):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR] + list(more) + [jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    return JClass


def lang(j):
    with zipfile.ZipFile(j) as z:
        return z.read(LANG).decode("utf-8").split("\n")


# ---------------------------------------------------------------------------------------------------------------- L: the tooltips
def run_lang(out, jar, scratch, _home):
    K = HK.Child(out)
    a, b = lang(OLD_JAR), lang(jar)
    K.eq(len(a), len(b), "L: same number of server.lang lines")
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    K.eq(len(diff), 16, "L: exactly 16 lines differ (the Soul Orb + 15 Soul Cages)")
    bad = []
    for i, (x, y) in enumerate(diff):
        key = x.split(" = ", 1)[0]
        ok = key.startswith("items.Weapon_Wand_Soul") and key.endswith(".description") and y.split(" = ", 1)[0] == key
        t = TIERS.index("Orb") if "SoulOrb" in key else [n for n, m in enumerate(TIERS) if key == "items.Weapon_Wand_SoulCage_%s.description" % m]
        t = t if isinstance(t, int) else (t[0] if t else -1)
        ok = ok and t >= 0 and ("Look %s s to make a Binding solid" % OLD16[t]) in x and x.replace("Look %s s " % OLD16[t], "Look %s s " % NEW16[t]) == y
        if not ok:
            bad.append((x[:90], y[:90]))
    K.check(not bad, "L: each differs only in its 'Look N s to make a Binding solid' number (0.1.39 default -> 0.1.40): %s" % bad[:3])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: defaults, loader, migration
def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    JClass = setup_jvm(jar, B.JAVASSIST)
    Cfg, Defs = JClass(PKG + "ArmoryCfg"), JClass(PKG + "ArmoryDefs")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    K.eq([str(x) for x in Defs.SOUL_TIERS], TIERS, "X1: the 16 soul tiers")
    K.eq([str(x) for x in Cfg.M40_KEYS], ["soul.stabilize." + m for m in TIERS], "X1: migrate040 knows all 16 tiers")
    K.eq([[str(x) for x in Cfg.M40_OLD], [str(x) for x in Cfg.M40_NEW]], [OLD16, NEW16], "X1: old (0.1.39) / new defaults")
    K.check(all(abs(float(n) - float(o) / 2.0) <= 0.03 + 1e-9 for n, o in zip(NEW16, OLD16)), "X1: every tier about half (within 0.03 s)")
    K.check(all(float(a) > float(b) for a, b in zip(NEW16[:8], NEW16[1:8])), "X1: the Orb .. Onyxium ladder still falls every tier")
    DEF = str(Cfg.DEF_CFG)
    K.check(all(("\nsoul.stabilize.%s=%s\n" % (m, v)) in DEF for m, v in zip(TIERS, NEW16)) and DEF.count(str(Cfg.M40_MARK)) == 1
            and DEF.count(str(Cfg.M21_MARK)) == 1, "X1: a fresh config.properties carries the 16 new values + the 0.1.21 and 0.1.40 markers")
    K.check("(0.9-0.5 s)" in DEF and "(1.75-1.0 s)" not in DEF, "X1: the row help text names 0.9-0.5 s")
    K.eq([str(x) for x in Cfg.M21_NEW], ["1.75", "1.6", "1.45", "1.35", "1.2", "1.1", "1.05", "1", "64"], "X1: migrate021 keeps its own 0.1.21 targets")

    def apply(drop=(), **kv):
        p = Props()
        p.load(SR(DEF))
        for k in drop:
            p.remove(k)
        for k, v in kv.items():
            p.setProperty(k, v)
        Cfg.apply(p)

    def cur():
        return [round(float(x), 4) for x in Cfg.SOUL_STAB]
    apply()
    K.eq(cur(), [float(x) for x in NEW16], "X2: the loader reads the 16 new defaults")
    apply(drop=["soul.stabilize." + m for m in TIERS])
    K.eq(cur(), [float(x) for x in NEW16], "X2: missing lines = the new defaults")
    apply(**{"soul.stabilize.Orb": "99", "soul.stabilize.Iron": "-1", "soul.stabilize.Cobalt": "1.75"})
    K.eq(cur()[:5], [10.0, 0.8, 0.0, 0.7, 1.75], "X2: hand values read / clamped to the row (0 .. 10)")
    apply()
    Soul = JClass(PKG + "Soul")
    K.eq([int(Soul.stabMs(float(x))) for x in NEW16[:8]], [900, 800, 750, 700, 600, 550, 520, 500], "X2: Soul.stabMs = the ms a Binding needs to turn solid")

    # ---- migrate040's text step
    def upd(t):
        r = Cfg.m40Update(t)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]])
    MK = str(Cfg.M40_MARK)
    src = "# a\nsoul.wispyGrace=0.4\n# b\n" + "".join("soul.stabilize.%s=%s\n" % (m, v) for m, v in zip(TIERS[:8], OLD16[:8])) + "soul.storeCap.Orb=10\n"
    a = upd(src)
    exp = src.replace("soul.stabilize.Orb=1.75", MK + "\nsoul.stabilize.Orb=0.9")
    for m, o, n in zip(TIERS[1:8], OLD16[1:8], NEW16[1:8]):
        exp = exp.replace("soul.stabilize.%s=%s\n" % (m, o), "soul.stabilize.%s=%s\n" % (m, n))
    K.check(a is not None and a[0] == exp and len(a[3]) == 24 and a[3][:3] == ["soul.stabilize.Orb", "1.75", "0.9"] and a[2] == []
            and a[1].startswith("soul.stabilize.Orb 1.75 -> 0.9, soul.stabilize.Copper 1.6 -> 0.8"),
            "X3: the 8 lines still at the 0.1.39 defaults -> the new ones + the marker above the first, nothing else changed: %s" % (a and a[1][:120]))
    K.check(upd(a[0]) is None, "X3: the marker = never again")
    h = upd(src.replace("soul.stabilize.Iron=1.45", "soul.stabilize.Iron=2").replace("soul.stabilize.Orb=1.75", "soul.stabilize.Orb=1.750"))
    K.check(h is not None and "soul.stabilize.Iron=2\n" in h[0] and "soul.stabilize.Orb=0.9\n" in h[0] and len(h[2]) == 1 and "Iron=2 kept (custom)" in h[2][0]
            and "0.1.40 default is 0.75" in h[2][0], "X3: a hand-set Iron 2 is kept + named, 1.750 (= the default) updates: %s" % (h and h[2]))
    nl = upd("# x\nquick.size=40\n")
    K.check(nl is not None and nl[0] == "# x\nquick.size=40\n" + MK + "\n" and nl[1] == "", "X3: no soul lines = the marker only")
    cr = upd(src.replace("\n", "\r\n"))
    K.check(cr is not None and "soul.stabilize.Onyxium=0.5\r\n" in cr[0] and cr[0].count("\r\n") == src.count("\n") + 1
            and "\n" not in cr[0].replace("\r\n", ""), "X3: CRLF kept (every line, the marker too)")
    # the chain on a 0.1.20 file (2.5 .. 1.5, no markers): migrate021 -> 1.75 .. 1.0, migrate040 -> 0.9 .. 0.5, in setup's order
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "chain")
    os.makedirs(home, exist_ok=True)
    f = os.path.join(home, "config.properties")
    v20 = ["2.5", "2.3", "2.1", "1.9", "1.7", "1.6", "1.5", "1.5"]
    open(f, "wb").write(("# old\r\n" + "".join("soul.stabilize.%s=%s\r\n" % (m, v) for m, v in zip(TIERS[:8], v20))).encode("latin-1"))
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(f)
    for m in MIGS:
        getattr(Cfg, m)()
    t = open(f, "rb").read().decode("latin-1")
    K.check(all(("\r\nsoul.stabilize.%s=%s\r\n" % (m, v)) in t for m, v in zip(TIERS[:8], NEW16[:8])) and MK in t and str(Cfg.M21_MARK) in t
            and "\n" not in t.replace("\r\n", ""), "X3: a 0.1.20 file runs 2.5 .. 1.5 -> 1.75 .. 1.0 -> 0.9 .. 0.5 (CRLF kept): %s" % [
                l for l in t.split("\r\n") if l.startswith("soul.")])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: Skyy's live file
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read()
    snaps, msgs = [], []
    for start in (1, 2):
        for m in MIGS:
            r = str(getattr(Cfg, m)())
            if m == "migrate040":
                msgs.append(r)
        Cfg.load()
        snaps.append(open(f, "rb").read())
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D: the 2nd start changes nothing")
    b, a = before.decode("latin-1"), snaps[0].decode("latin-1")
    eol = "\r\n" if "\r\n" in b else "\n"
    present = [(m, o, n) for m, o, n in zip(TIERS, OLD16, NEW16) if (eol + "soul.stabilize.%s=%s" % (m, o) + eol) in b]
    K.check(len(present) == 8 and [p[0] for p in present] == TIERS[:8], "D: Skyy's live file holds the 8 old-tier soul.stabilize lines at the 0.1.39 defaults")
    exp = b
    for i, (m, o, n) in enumerate(present):
        exp = exp.replace(eol + "soul.stabilize.%s=%s" % (m, o) + eol, eol + (str(Cfg.M40_MARK) + eol if i == 0 else "") + "soul.stabilize.%s=%s" % (m, n) + eol)
    K.check(a == exp and a.count(str(Cfg.M40_MARK)) == 1, "D: the 1st start changed only the 8 soul.stabilize lines + added the marker (bytes + line ends kept): %s" % msgs[0][:200])
    K.eq([round(float(x), 4) for x in Cfg.SOUL_STAB], [float(x) for x in NEW16], "D: the loader reads the 16 new values (the zone-metal tiers from the defaults)")
    hist = [os.path.join(dp, fn) for dp, _d, fns in os.walk(home) for fn in fns if fn != "config.properties"]
    held = [p for p in hist if open(p, "rb").read() == before]
    logl = [l for p in hist for l in open(p, "rb").read().decode("latin-1").splitlines() if "SkyyArmory 0.1.40" in l and "\tupdate\tsoul.stabilize." in l]
    K.check(held and len(logl) == 8 and all(any(("\tsoul.stabilize.%s\t%s\t%s\tok" % p) in l for l in logl) for p in present),
            "D: a History copy holds the old bytes (%d) and the change log has the 8 lines (Server Setup -> Changes can undo): %d" % (len(held), len(logl)))
    K.notes.append("D: live config %d bytes, eol %r" % (len(before), eol))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("lang", run_lang), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
