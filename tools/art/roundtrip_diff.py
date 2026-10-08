#!/usr/bin/env python3
"""Compare Blockbench's re-export (plugin codec) of each piece with the generated file, node by node.
Usage: python3 roundtrip_diff.py <models_dir> <roundtrip_dir>"""
import json, os, sys
MD, RT = sys.argv[1], sys.argv[2]

def flat(nodes, out, path=""):
    for n in nodes:
        out[n["name"]] = n
        flat(n.get("children", []), out)
    return out

def cmp(a, b, path, diffs, tol=1e-3):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ("children", "id"):
                continue
            if k not in a or k not in b:
                diffs.append("%s.%s only in %s" % (path, k, "ours" if k in a else "blockbench")); continue
            cmp(a[k], b[k], path + "." + k, diffs, tol)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > tol: diffs.append("%s: %s vs %s" % (path, a, b))
    elif a != b:
        diffs.append("%s: %r vs %r" % (path, a, b))

total = 0
for p in ("Head", "Chest", "Hands", "Legs"):
    A = json.load(open(os.path.join(MD, p + ".blockymodel")))
    B = json.load(open(os.path.join(RT, p + "_bb_roundtrip.blockymodel")))
    fa, fb = flat(A["nodes"], {}), flat(B["nodes"], {})
    diffs = []
    if set(fa) != set(fb):
        diffs.append("node names differ: ours-only %s bb-only %s" % (sorted(set(fa) - set(fb)), sorted(set(fb) - set(fa))))
    for nm in fa:
        if nm in fb:
            pa = [c["name"] for c in fa[nm].get("children", [])]; pb = [c["name"] for c in fb[nm].get("children", [])]
            if pa != pb: diffs.append("%s children %s vs %s" % (nm, pa, pb))
            cmp(fa[nm], fb[nm], nm, diffs)
    cmp({k: v for k, v in A.items() if k != "nodes"}, {k: v for k, v in B.items() if k != "nodes"}, "root", diffs)
    print("%-5s nodes ours %d / blockbench %d : %s" % (p, len(fa), len(fb), "IDENTICAL (within 0.001)" if not diffs else "%d diffs" % len(diffs)))
    for d in diffs[:25]: print("    ", d)
    total += len(diffs)
sys.exit(0)
