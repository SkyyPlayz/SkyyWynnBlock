#!/usr/bin/env python3
"""preview_ability_icons - a quick working preview (not the review sheet): each icon at 6x (nearest), 64 px and 32 px."""
import os
import sys

from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ability_icons as M  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ability_preview.png"
S = 6
W = 5 * (64 * S + 20) + 20
im = Image.new("RGBA", (W, 2 * (64 * S + 140) + 20), (40, 44, 52, 255))
for i, (st, fn, _d, _p) in enumerate(M.ICONS):
    ic = Image.open(os.path.join(M.DEFAULT_OUT, M.rel_path(st, fn))).convert("RGBA")
    x = 20 + (i % 5) * (64 * S + 20)
    y = 20 + (i // 5) * (64 * S + 140)
    im.alpha_composite(ic.resize((64 * S, 64 * S), Image.NEAREST), (x, y))
    im.alpha_composite(ic, (x, y + 64 * S + 8))
    im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 80, y + 64 * S + 8))
    im.alpha_composite(ic.resize((32, 32), Image.BOX).resize((96, 96), Image.NEAREST), (x + 130, y + 64 * S + 8))
im.save(out)
print(out)
