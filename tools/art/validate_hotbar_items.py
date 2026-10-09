"""validate_hotbar_items - checks the hotbar ability item icons: 64x64 RGBA, hard alpha, transparent corners, opaque centre, no pure
#000 / #fff, deterministic (re-render == file), every pair different at 32 px (mean abs diff > 10), and every MIRROR item clearly
different from its own round ability icon at 32 px (mean abs diff > 25, so the hotbar item is not mistaken for the HUD icon).
    python3 tools/art/validate_hotbar_items.py [--out DIR]"""
import argparse
import itertools
import os
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_hotbar_items as H     # noqa: E402
import make_ability_icons as M    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=H.DEFAULT_OUT)
    ap.add_argument("--abilities", default=M.DEFAULT_OUT)
    a = ap.parse_args()
    bad = 0
    small = {}
    vs_hud = []
    for item_id, disp, cls, kind, fn, rend in H.items():
        p = os.path.join(a.out, H.rel(item_id))
        if not os.path.exists(p):
            print("MISSING", p)
            bad += 1
            continue
        im = Image.open(p)
        arr = np.asarray(im.convert("RGBA"))
        errs = []
        if im.size != (64, 64):
            errs.append("size %s" % (im.size,))
        if im.mode != "RGBA":
            errs.append("mode " + im.mode)
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
        if not np.array_equal(np.asarray(rend()), arr):
            errs.append("not deterministic")
        small[item_id] = np.asarray(im.convert("RGBA").resize((32, 32), Image.BOX), float)
        extra = ""
        if kind == "mirror":
            st = next(s for s, f, *_r in M.ICONS if f == fn)
            hud = Image.open(os.path.join(a.abilities, M.rel_path(st, fn))).convert("RGBA").resize((32, 32), Image.BOX)
            d = np.abs(np.asarray(hud, float) - small[item_id]).mean()
            vs_hud.append((d, item_id))
            extra = "  vs HUD icon %.1f" % d
            if d <= 25:
                errs.append("too close to its round ability icon (%.1f)" % d)
        print("%-9s %-15s %s%s" % (cls, fn, "OK" if not errs else "FAIL: " + ", ".join(errs), extra))
        bad += bool(errs)
    worst = min((np.abs(small[x] - small[y]).mean(), x, y) for x, y in itertools.combinations(small, 2))
    print("most similar pair at 32 px: %s vs %s, mean abs diff %.1f (want > 10)" % (worst[1], worst[2], worst[0]))
    if worst[0] <= 10:
        bad += 1
    if vs_hud:
        print("closest item to its own round ability icon: %s (%.1f, want > 25)" % (min(vs_hud)[1], min(vs_hud)[0]))
    print("RESULT:", "PASS" if not bad else "FAIL (%d)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
