#!/usr/bin/env python3
"""validate_ability_icons - checks the 10 Mage + Priest ability icons.

Checks: file exists at Common/Icons/Abilities/<Class>/<Name>.png, 64x64 RGBA, alpha only 0 / 255, corners transparent and centre
opaque, no pure #000000 / #ffffff pixel, the symbol is not a near-copy of another icon (mean abs diff of the 32 px versions),
and the generator is deterministic (re-render in memory == bytes on disk, pixel for pixel).
Run:  python3 validate_ability_icons.py [--out DIR]
"""
import argparse
import itertools
import os
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ability_icons as M  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=M.DEFAULT_OUT)
    a = ap.parse_args()
    bad = 0
    small = {}
    for st, fn, disp, painter in M.ICONS:
        p = os.path.join(a.out, M.rel_path(st, fn))
        errs = []
        if not os.path.exists(p):
            print("MISSING", p)
            bad += 1
            continue
        im = Image.open(p)
        if im.size != (64, 64):
            errs.append("size %s" % (im.size,))
        if im.mode != "RGBA":
            errs.append("mode %s" % im.mode)
        arr = np.asarray(im.convert("RGBA"))
        al = arr[..., 3]
        if not set(np.unique(al)).issubset({0, 255}):
            errs.append("partial alpha")
        if al[0, 0] or al[0, 63] or al[63, 0] or al[63, 63]:
            errs.append("corner not transparent")
        if al[32, 32] != 255:
            errs.append("centre not opaque")
        vis = arr[al == 255][:, :3]
        if ((vis == 0).all(axis=1)).any():
            errs.append("pure black pixel")
        if ((vis == 255).all(axis=1)).any():
            errs.append("pure white pixel")
        again = np.asarray(M.render(painter, st))
        if not np.array_equal(again, arr):
            errs.append("not deterministic (re-render differs)")
        small[fn] = np.asarray(im.convert("RGBA").resize((32, 32), Image.BOX), float)
        ncol = len(np.unique(vis.reshape(-1, 3), axis=0))
        print("%-7s %-15s %s  colours=%d" % (st.name, fn, "OK" if not errs else "FAIL: " + ", ".join(errs), ncol))
        bad += bool(errs)
    worst = min(((np.abs(small[x] - small[y]).mean(), x, y) for x, y in itertools.combinations(small, 2)))
    print("most similar pair at 32 px: %s vs %s, mean abs diff %.1f (want > 10)" % (worst[1], worst[2], worst[0]))
    if worst[0] <= 10:
        bad += 1
    print("RESULT:", "PASS" if not bad else "FAIL (%d)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
