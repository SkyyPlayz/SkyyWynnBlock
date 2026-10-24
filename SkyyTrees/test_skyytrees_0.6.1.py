"""Harness for SkyyTrees 0.6.1 (modifier unlock nodes are named "<Ability>: <Modifier> Modifier"; cosmetic).
Build first:  python tools/trees_0_6_1_patch.py && python SkyyTrees/build_skyytrees_0.6.1.py
Run:          python SkyyTrees/test_skyytrees_0.6.1.py
Phases: static (patch output = the generated script, 0.6.0 re-generates byte for byte; version / one header), data (every modifier node's
display name, no doubled word, no saved-key / hook / max / cost / text change against the 0.6.0 data, non-modifier names untouched),
jar (the names are in the jar's name table, the bare 0.6.0 modifier names are gone, the manifest says 0.6.1). The build itself already
ran the fit checks (tr_fit_check / tv3_fit: panel title width, cell name lines) - a failing fit stops the build.
"""
import os, sys, json, subprocess, zipfile, tempfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
FAILS = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


DUMP = r'''
import sys, json
sys.path.insert(0, %r)
import trees_v3_data as D
D.V4_MODNAME_SUFFIX = bool(int(sys.argv[1]))
D.v4_apply()
out = []
for t in D.TREES:
    if t["kind"] != "class":
        continue
    for b in t["branches"]:
        for r in b["rows"]:
            for u in r["ups"]:
                h = u["hook"] or (None,)
                out.append([t["name"], u["key"], u["name"], h[0], list(h[1:]) if h[0] == "mod" else [], u["max"], u["cost"], u["text"]])
print(json.dumps(out))
''' % TOOLS


def dump(flag):
    r = subprocess.run([sys.executable, "-c", DUMP, str(flag)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    # static
    gen = os.path.join(HERE, "build_skyytrees_0.6.1.py")
    s = open(gen, encoding="utf-8").read()
    ok('VERSION = "0.6.1"' in s and s.count("SkyyTrees 0.6.1 - build script") == 1, "static: version 0.6.1, one header")
    for patch, dst in (("trees_0_6_1_patch.py", "b061.py"), ("trees_0_6_0_patch.py", "b060.py")):
        d = os.path.join(tempfile.gettempdir(), "trees061chk")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, dst)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, patch), "--out", out], capture_output=True, text=True)
        ref = gen if dst == "b061.py" else os.path.join(HERE, "build_skyytrees_0.6.0.py")
        ok(r.returncode == 0 and open(out, "rb").read() == open(ref, "rb").read(), "static: %s re-generates its script byte for byte" % patch)
    # data
    old, new = dump(0), dump(1)
    ok(len(old) == len(new), "data: same node count (%d)" % len(old))
    mods = 0
    for o, n in zip(old, new):
        if o[3] != "mod":
            ok(o == n, "data: non-modifier node untouched %s" % o[1]) if o != n else None
            continue
        mods += 1
        ab, mod = n[2].split(": ", 1)[0], o[4][1]
        want = o[2] + " Modifier" if not o[2].endswith("Modifier") else o[2]
        if n[2] != want or re.search(r"\b(\w+) \1\b", n[2]) or n[2].count("Modifier") != 1:
            ok(False, "data: modifier name %s -> %s (want %s)" % (o[2], n[2], want))
        if n[:2] != o[:2] or n[3:] != o[3:]:
            ok(False, "data: key / hook / max / cost / text changed on %s" % n[1])
    ok(mods > 0, "data: %d modifier nodes all named '<Ability>: <Modifier> Modifier', no doubled word, keys / hooks / ranks / texts unchanged" % mods)
    ok(any(n[2] == "Martyr's Grace: Power Modifier" for n in new), "data: Martyr's Grace: Power Modifier exists (Skyy's example)")
    ok(not any(n[2].endswith("Modifier Modifier") for n in new), "data: nothing doubled")
    print("longest modifier name: %d chars: %s" % (max(len(n[2]) for n in new if n[3] == "mod"), max((n[2] for n in new if n[3] == "mod"), key=len)))
    # jar
    jar = os.path.join(HERE, "SkyyTrees-0.6.1.jar")
    z = zipfile.ZipFile(jar)
    blob = z.read("com/skyy/trees/TreeV3.class")
    names = set(n[2] for n in new if n[3] == "mod")
    miss = [n for n in names if n.encode("utf-8") not in blob]
    ok(not miss, "jar: all %d modifier names in the name table%s" % (len(names), (" (missing " + str(miss[:3]) + ")") if miss else ""))
    ok(b"Martyr's Grace: Power\x00" not in blob and b"Martyr's Grace: Power\x01" not in blob, "jar: bare name gone")
    man = [n for n in z.namelist() if n.endswith("manifest.json")]
    ok(man and '"0.6.1"' in z.read(man[0]).decode("utf-8"), "jar: manifest 0.6.1")
    print("RESULT: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "ALL PASS"))
    return 1 if FAILS else 0


sys.exit(main())
