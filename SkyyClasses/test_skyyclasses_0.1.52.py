"""Harness for SkyyClasses 0.1.52 (rarity + tooltip pass: the colour-coded ability rune descriptions; tools/classes_0_1_52_patch.py). Build first:
    python tools/classes_0_1_52_patch.py && python SkyyClasses/build_skyyclasses_0.1.52.py
    python SkyyClasses/test_skyyclasses_0.1.52.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new class / system / command; line endings kept; the jar has the same file names;
                 the only non-class changes = server.lang + the manifest; server.lang: the same keys in the same order, exactly the 39 rune
                 description lines changed, each one RENDERED (its spans parsed): yellow #ffcc00 'Ability 2 / 3 key:' then gold #e8c25a
                 <the rune's class>, balanced + never nested, ASCII, one line, and without its spans the plain sentence; every other line
                 (names, keyword, art items) byte for byte 0.1.51; every item / effect JSON unchanged (no Quality / id change)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.51 -> 0.1.52 (EXPECT below: only the version strings)
  X46 / W46 / W47 / X48 / ALT / SM / W50 / EL / BR / W  the 0.1.51 harness's EXEC + WIRE phases on the 0.1.52 jar (unchanged behaviour)
  LIVE  start twice on a scratch COPY of Skyy's live Skyy_SkyyClasses
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the <color> spans in the rune's popup (the same span syntax SkyyArmory 0.1.49 ships;
the runes are Quality Debug items that only show in the ability slot).
Scratch: tools/dev/scratch/rar_classes/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rar_classes", "cls")]
import harness_kit as HK

_ORIG_COMPARE0 = HK.run_compare
_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_51", os.path.join(HERE, "test_skyyclasses_0.1.51.py"))
T51 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T51)
sys.argv[:] = _argv
HK.run_compare = _ORIG_COMPARE0          # 0.1.51's compare drops its 2 new effect files; both jars have them now
T50, T48 = T51.T50, T51.T48

VERSION, OLD = "0.1.52", "0.1.51"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_52_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
T51.GEN = GEN          # the 0.1.51 wire phase reads the generated script: read THIS one
LANG = "Server/Languages/en-US/server.lang"
ADDED = []
EXPECT = {   # checked 2026-11-01 (the class compare 0.1.51 -> 0.1.52: only the version strings - the kit's export / header / migrate texts + the plugin)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit compare on copies WITHOUT server.lang (the static phase checks every changed line of it exactly)"""
    cps = []
    for j_, tag_ in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag_)
        with zipfile.ZipFile(j_) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
            for n in zi.namelist():
                if n != LANG:
                    zo.writestr(n, zi.read(n))
        cps.append(cp)
    _ORIG_COMPARE0(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare
OLD_DESC = "Your %s ability - the Ability 2 / 3 key casts it (crouch = your alts). It lives in your ability slot and goes back there by itself."
PLAIN = "Ability 2 / 3 key: casts your %s ability (crouch = your alts). Lives in your ability slot and goes back there by itself."
SPAN = re.compile(r'<color is="(#[0-9a-f]{6})">([^<]*)</color>')


def render(t):
    """what the client draws: [(colour or None, text)] runs; None = the plain default colour"""
    runs, at = [], 0
    for m in SPAN.finditer(t):
        if m.start() > at:
            runs.append((None, t[at:m.start()]))
        runs.append((m.group(1), m.group(2)))
        at = m.end()
    if at < len(t):
        runs.append((None, t[at:]))
    return runs


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.52 - build script') and g.count('VERSION = "0.1.52"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem("), g.count("registerCommand("), g.count("makeClass(")), (o.count("registerSystem("), o.count("registerCommand("), o.count("makeClass(")),
         "S no new class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S the jar has exactly the 0.1.51 file names (no id added / lost)")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), [LANG, "manifest.json"],
         "S the only non-class changes: server.lang + the manifest (every item / effect JSON byte for byte: Quality Debug, same ids)")
    la, lb = za.read(LANG).decode("utf8").split("\n"), zb.read(LANG).decode("utf8").split("\n")
    ka, kb = [l.split(" = ", 1)[0] for l in la if " = " in l], [l.split(" = ", 1)[0] for l in lb if " = " in l]
    K.check(ka == kb and len(kb) == len(set(kb)) and len(la) == len(lb), "S server.lang: the same %d keys in the same order, each once" % len(kb))
    runes = {}
    for n in nb:
        m = re.fullmatch(r"Server/Item/Items/SkyyClasses/(SkyyAbility_([A-Za-z]+)_[A-Za-z]+)\.json", n)
        if m:
            runes[m.group(1)] = m.group(2)
            it = json.loads(zb.read(n).decode("utf8"))
            K.check(it["Quality"] == "Debug" and it["TranslationProperties"]["Description"] == "server.items.%s.description" % m.group(1), "S %s stays Quality Debug" % m.group(1))
    K.eq(len(runes), 39, "S 39 rune items")
    changed, bad = 0, []
    for a_, b_ in zip(la, lb):
        if a_ == b_:
            continue
        k, t = b_.split(" = ", 1)
        mk = re.fullmatch(r"items\.(SkyyAbility_[A-Za-z]+_[A-Za-z]+)\.description", k)
        if not mk or mk.group(1) not in runes:
            bad.append(k)
            continue
        cls = runes[mk.group(1)]
        changed += 1
        if a_ != "%s = %s" % (k, OLD_DESC % cls):
            bad.append(k + " (old text)")
        if render(t) != [("#ffcc00", "Ability 2 / 3 key:"), (None, " casts your "), ("#e8c25a", cls),
                         (None, " ability (crouch = your alts). Lives in your ability slot and goes back there by itself.")]:
            bad.append(k + " (render %s)" % render(t))
        if not (t.isascii() and "\r" not in t and t.count("<color ") == t.count("</color>") == 2 and not re.search(r"<color[^>]*>[^<]*<color", t)):
            bad.append(k + " (spans)")
        if re.sub(r"</?color[^>]*>", "", t) != PLAIN % cls:
            bad.append(k + " (plain)")
    K.check(changed == 39 and not bad, "S exactly the 39 rune descriptions changed, each rendered yellow action + gold class, balanced, plain = the sentence: %d %s" % (changed, bad[:4]))
    K.check(not [l for l in lb if "<color" in l and ".description = " not in l], "S names / keyword / art items stay plain")
    sm = [l for l in lb if l.startswith("items.SkyyAbility_Assassin_ShadowMark.description = ")]
    K.eq(sm, ['items.SkyyAbility_Assassin_ShadowMark.description = <color is="#ffcc00">Ability 2 / 3 key:</color> casts your <color is="#e8c25a">Assassin</color> ability (crouch = your alts). Lives in your ability slot and goes back there by itself.'],
         "S the Shadow Mark rune line, literally")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec46", T48.run_exec46), ("wire46", T48.run_wire46), ("wire47", T48.run_wire47), ("exec48", T48.run_exec),
                   ("alt", T50.run_alt), ("sm", T50.run_exec), ("wire50", T50.run_wire), ("elem", T51.run_elem), ("wire", T51.run_wire), ("live", T48.run_live)],
           script=__file__, live=(T48.LIVE_DIR, "Skyy_SkyyClasses"))
