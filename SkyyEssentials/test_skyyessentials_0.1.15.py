"""Bare-JVM check for SkyyEssentials 0.1.15 (the Void Charms rename texts + long warp icon ids; tools/essentials_0_1_15_patch.py). Build first:
    python tools/essentials_0_1_15_patch.py && python SkyyEssentials/build_skyyessentials_0.1.15.py

    python SkyyEssentials/test_skyyessentials_0.1.15.py [--jar <SkyyEssentials-0.1.15.jar>] [--dir <scratch folder>] [--keep] [--only wicon,...]

The 0.1.14 harness (test_skyyessentials_0.1.14.py, loaded as a module; it loads 0.1.13's, 0.1.12's and 0.1.11's) runs its phases wicon / back /
menu / main / trade / tpa / chat / keep / compost / live1 / live2 against this jar, each in a fresh JVM; the checks that change ON PURPOSE (the
old trade texts naming "the Accessory Bag") are listed in SUPERSEDED and re-checked here. Phase wicon gets these extra checks (W5):
  W5 a warp whose id has 40 characters: the pick is saved and survives a "restart" (load) - 0.1.14 dropped it; an id of 210 characters is
     refused AT SET TIME on /warpadmin ("-Warp <id>'s icon can't be saved: ...", nothing written); keyErr: '=', '#' first, a line break,
     empty = refused, a dotted id ok; a rename to an id the file can't hold drops the icon (the file has no line for it)
  R  the rename texts, live: TBlock.what / whatAll / why / refused name "the Old Accessory Bag"; the Server Setup help; audit line
  Z  class compare 0.1.14 -> 0.1.15 by constant pools: no class added / removed; every changed string of every class but EssWIcon / WarpPage
     is exactly a planned rename (PAIRS) or the version; EssWIcon / WarpPage carry the new keyErr texts; tpa / msg / homes byte-identical
NOT runnable in a bare JVM: the client. Default scratch: tools/dev/scratch/vcrename/ess (deleted unless --keep).
"""
import os, sys, re, json, shutil, subprocess, zipfile, struct, inspect, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))

_s14 = importlib.util.spec_from_file_location("test_skyyessentials_0_1_14", os.path.join(HERE, "test_skyyessentials_0.1.14.py"))
T14 = importlib.util.module_from_spec(_s14)
_s14.loader.exec_module(T14)
T13, T12, T11 = T14.T13, T14.T12, T14.T11

# THE OLD WORDS: the 0.1.11 harness (T11 - the trade phases of 0.1.7 onwards) compares the exact refusal / audit / check= / row texts. It is
# re-read with "the Accessory Bag" -> "the Old Accessory Bag" in its expectations (and in the old build scripts' KIT_ROWS it compares the
# published rows with) and executed into the SAME module (so T12 / T13 / T14 keep their references); every value they set is restored.
import types
_REN = [("the Accessory Bag", "the Old Accessory Bag"), ("The Accessory Bag", "The Old Accessory Bag")]


def _ren15(rows):
    def one(x):
        if isinstance(x, str):
            for o_, n_ in _REN:
                x = x.replace(o_, n_).replace("Old Old ", "Old ")
            return x
        if isinstance(x, (list, tuple)):
            return type(x)(one(y) for y in x)
        return x
    return [one(r) for r in rows]


_src11 = open(T11.__file__, encoding="utf8").read()
_k19 = '    kit19 = script_list("build_skyyessentials_%s.py" % PREV, "KIT_ROWS", {"CF": "@config.properties:"})\n'
assert _src11.count(_k19) == 1, "the 0.1.11 harness changed (kit19)"
_src11 = _src11.replace(_k19, _k19 + "    kit18, kit19 = _ren15(kit18), _ren15(kit19)\n")
_n0 = _src11.count("ccessory Bag")
for _o, _n in _REN:
    _src11 = _src11.replace(_o, _n)
assert _n0 >= 20, _n0
_saved11 = dict(T11.__dict__)
T11.__dict__["_ren15"] = _ren15
exec(compile(_src11, T11.__file__, "exec"), T11.__dict__)
for _k, _v in _saved11.items():
    if not isinstance(_v, types.FunctionType) or _k == "check":
        T11.__dict__[_k] = _v

VERSION = "0.1.15"
PREV = "0.1.14"
PKG = "com.skyy.essentials."
SCRATCH = os.path.abspath(T11.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "vcrename", "ess")))
JAR = os.path.abspath(T11.arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv
for _m in (T11, T12, T13, T14):
    _m.VERSION, _m.SCRATCH, _m.JAR, _m.KEEP = VERSION, SCRATCH, JAR, KEEP
T13.PREV, T13.PREV_JAR = "0.1.13", os.path.join(HERE, "SkyyEssentials-0.1.13.jar")
T14.PREV, T14.PREV_JAR = PREV, PREV_JAR

# the old checks that compare the exact old words (the item is the Old Accessory Bag now) - re-checked in phase R / Z
T14.SUPERSEDED += [
    (re.compile(r"^Z: "), "the 0.1.14 byte-compare (0.1.13 -> 0.1.14) - replaced by this harness's Z"),
]
FAILS = T14.FAILS
check = T14.check
PAIRS = [("the Accessory Bag", "the Old Accessory Bag")]
NEW_TEXT = {"EssWIcon": ["its name is longer than 200 characters", "its name has = or a line break in it", "its name starts with #",
                         ": its icon was dropped - "],
            "WarpPage": ["'s icon can't be saved: "]}

# ---------------------------------------------------------------------------------------------- W5: phase wicon + the long-id checks
W5 = r'''
    # ---------------- W5 (0.1.15): long warp icon ids are kept; ids the file can't hold are refused at set time
    L40 = "deep_mine_level_two_entrance_north_gate"
    L40 = L40 + "x" * (40 - len(L40))
    L210 = "z" * 210
    mkwarp(L40)
    mkwarp(L210)
    wA.pickId = L40
    T12.click(wA, "pk:%d" % fi)
    check(str(wA.info).startswith("+Warp " + L40) and (L40.lower() + "=fishing") in open(f, encoding="utf8").read(), "W5: a 40-character warp id's pick is saved (%s)" % str(wA.info)[:80])
    WI.MAP.clear()
    WI.load(Paths.get(f))
    check(str(WI.get(L40)) == "fishing", "W5: ... and survives a restart (0.1.14 dropped ids over 32 characters)")
    wA.pickId = L210
    T12.click(wA, "pk:%d" % fi)
    check(str(wA.info).startswith("-Warp " + L210 + "'s icon can't be saved: its name is longer than 200 characters")
          and L210 not in open(f, encoding="utf8").read() and str(WI.get(L210)) == "warp", "W5: a 210-character id is refused at set time, nothing written (%s)" % str(wA.info)[-60:])
    check(not bool(WI.set(L210, "fishing")) and str(WI.get(L210)) == "warp", "W5: EssWIcon.set refuses it too")
    check(WI.keyErr("a=b") is not None and WI.keyErr("#a") is not None and WI.keyErr("a\nb") is not None and WI.keyErr("") is not None
          and WI.keyErr("mine.deep") is None and WI.keyErr("y" * 200) is None and WI.keyErr("y" * 201) is not None, "W5: keyErr - the file's key rule")
    WI.rename(L40, "q" * 201)
    check(str(WI.get(L40)) == "warp" and ("q" * 201) not in open(f, encoding="utf8").read() and L40.lower() not in open(f, encoding="utf8").read(),
          "W5: a rename to an id the file can't hold drops the icon (no line written)")
    WI.MAP.clear()
    WI.load(Paths.get(f))
    check(str(WI.get("mines")) == "fishing", "W5: the other picks are untouched")
    BK.stop()
    check(br.get("essentials:fn:warps") is None'''
_src = inspect.getsource(T14.run_wicon)
_anchor = '''
    BK.stop()
    check(br.get("essentials:fn:warps") is None'''
assert _src.count(_anchor) == 1, "the 0.1.14 harness changed (BK.stop anchor)"
_src = _src.replace("def run_wicon(jar):", "def run_wicon15(jar):").replace(_anchor, W5)
exec(compile(_src, T14.__file__, "exec"), T14.__dict__)


def run_rename(jar):
    B = T11.boot(jar)
    from jpype import JClass
    TB = JClass(PKG + "TBlock")
    check(str(TB.what("Skyy_Accessory_Bag")) == "the Old Accessory Bag" and str(TB.whatAll("Skyy_Accessory_Bag")) == "the Old Accessory Bag",
          "R: TBlock.what / whatAll name the Old Accessory Bag")
    check(str(TB.why("Skyy_Sack_Mining_Normal")) == "Magic Bags and the Old Accessory Bag open their owner's own storage, so they can't be traded", "R: why")
    check(str(TB.refused("Skyy_Accessory_Bag")) == "-The Old Accessory Bag can't go in a trade - Magic Bags and the Old Accessory Bag open their owner's own storage. It stays in your inventory.",
          "R: the refusal line: %s" % str(TB.refused("Skyy_Accessory_Bag")))
    check(str(TB.refused("Skyy_Sack_Mining_Normal")).startswith("-A Magic Bag can't go in a trade - Magic Bags and the Old Accessory Bag"), "R: a Magic Bag's refusal")
    print("rename phase done")


def cp_strings(b):
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        t = b[i]
        if t == 1:
            L = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append(b[i + 3:i + 3 + L].decode("utf8", "replace"))
            i += 3 + L
        elif t in (3, 4):
            i += 5
        elif t in (5, 6):
            i += 9
            k += 1
        elif t in (7, 8, 16, 19, 20):
            i += 3
        elif t in (9, 10, 11, 12, 17, 18):
            i += 5
        elif t == 15:
            i += 4
        else:
            raise ValueError("constant tag %d" % t)
        k += 1
    return out


def compare_jars():
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    check(sorted(ca) == sorted(cb), "Z: the same classes (none added / removed)")
    changed = sorted(short(n) for n in set(ca) & set(cb) if ca[n] != cb[n])
    odd, used = [], set()
    for n in sorted(set(ca) & set(cb)):
        if ca[n] == cb[n]:
            continue
        sa, sb = set(cp_strings(ca[n])), set(cp_strings(cb[n]))
        gone, new = sa - sb, sb - sa
        if short(n) in NEW_TEXT:
            miss = [t for t in NEW_TEXT[short(n)] if not [s for s in new if t in s]]
            check(not miss, "Z: %s carries its new keyErr texts: missing %s" % (short(n), miss))
            continue
        mapped = set()
        for s in gone:
            t = s
            for i, (o, w) in enumerate(PAIRS):
                if o in t and "Old Accessory" not in t:
                    used.add(i)
                    t = t.replace(o, w)
            mapped.add(t.replace(PREV, VERSION))
        if mapped != new:
            odd.append("%s: -%s +%s" % (short(n), sorted(mapped - new)[:2], sorted(new - mapped)[:2]))
    check(not odd, "Z: every other changed class differs only in the planned texts / the version: %s" % odd[:4])
    check(used == {0}, "Z: the rename pair was used")
    check({"TBlock", "EssWIcon", "WarpPage", "SkyyEssentialsPlugin"} <= set(changed), "Z: TBlock + EssWIcon + WarpPage + the plugin changed: %s" % changed)
    keep = ["TpaCmd", "MsgCmd", "TStore", "TradePage", "HubBar", "EssDur", "EssHome", "EssBackSys", "EssBack", "EssWarp"]
    check(all(c not in changed for c in keep), "Z: tpa / msg / trade store / homes / back / warps byte-identical: %s" % [c for c in keep if c in changed])
    bad = [(short(n), s[:100]) for n in cb for s in cp_strings(cb[n]) if re.search(r"\bthe Accessory Bag\b", s) and "Old Accessory Bag" not in s]
    check(not bad, "Z: no class text says 'the Accessory Bag' any more: %s" % bad[:4])
    print("Z. constant-pool compare %s -> %s: changed %s" % (PREV, VERSION, changed))


def main():
    ph = T11.arg("--phase")
    if "--run" in sys.argv:
        jar = T11.arg("--run")
        if ph == "wicon":
            T14.run_wicon15(jar)
        elif ph == "rename":
            run_rename(jar)
        elif ph == "back":
            T13.run_back(jar)
        elif ph == "menu":
            T12.run_menu(jar)
        elif ph in ("main", "trade", "tpa", "chat", "keep", "compost"):
            getattr(T11, "run_" + ph)(jar)
        else:
            T11.run_live(jar, ph)
        tf = list(T13.FAILS)
        for s_ in T14.SKIPPED:
            print("  superseded:", s_)
        print("%s: %d checks passed, %d failed, %d superseded" % (ph, T14.OKS[0], len(FAILS) + len(tf), len(T14.SKIPPED)))
        for f in FAILS + tf:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS or tf else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep), "the scratch folder must be inside tools/dev/scratch/"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    only = T11.arg("--only")
    for ph in ("wicon", "rename", "back", "menu", "main", "trade", "tpa", "chat", "keep", "compost"):
        if only and ph not in only.split(","):
            continue
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
        print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
        rc |= p.returncode
    if not only:
        if os.path.isdir(T11.LIVE):
            dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
            shutil.copytree(T11.LIVE, dstl)
            for ph in ("live1", "live2"):
                p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
                print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
                rc |= p.returncode
        else:
            print("FAIL no live folder at %s" % T11.LIVE)
            rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (T14.OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
