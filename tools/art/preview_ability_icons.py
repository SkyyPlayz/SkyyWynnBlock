#!/usr/bin/env python3
"""preview_ability_icons - a quick working preview (not the review sheet): icons at 5x (nearest), 64 px, and the 32 px copy at 4x.
Run:  python3 preview_ability_icons.py [OUT.png] [Class,Class]"""
import os
import sys

from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ability_icons as M  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ability_preview.png"
classes = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
icons = [ic for ic in M.ICONS if classes is None or ic[0].name in classes]
S = 5
CW = 64 * S + 20
rows = (len(icons) + 4) // 5
im = Image.new("RGBA", (5 * CW + 20, rows * (64 * S + 160) + 20), (40, 44, 52, 255))
for i, (st, fn, _d, _p) in enumerate(icons):
    ic = Image.open(os.path.join(M.DEFAULT_OUT, M.rel_path(st, fn))).convert("RGBA")
    x = 20 + (i % 5) * CW
    y = 20 + (i // 5) * (64 * S + 160)
    im.alpha_composite(ic.resize((64 * S, 64 * S), Image.NEAREST), (x, y))
    im.alpha_composite(ic, (x, y + 64 * S + 8))
    im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 76, y + 64 * S + 8))
    im.alpha_composite(ic.resize((32, 32), Image.BOX).resize((128, 128), Image.NEAREST), (x + 120, y + 64 * S + 8))
im.save(out)
print(out)
