"""Derive SkyyAuctions/build_skyyauctions_0.1.1.py from 0.1 (python tools/auctions_0_1_1_patch.py, then build the result).
0.1.1 (2026-09-25 HOTFIX, Skyy in game): clicking View on a listing DISCONNECTED the client:
  "CustomUI Set command couldn't set value. Selector: #SkyyAhDGrid.Slots -> Failed to convert JSON value (Object) to specified type
  (ClientItemMetadata)" (client log 2026-09-25_05-22-44). The item view put the listed ItemStack WITH its metadata (SkyyRolls rolls /
  ItemDisplay) into an ItemGridSlot; the UI codec sends metadata as a JSON object the client cannot read in a grid. The grid now gets a
  metadata-free copy (same item id + quantity = same icon); the rolls are already shown as text next to it. Nothing else changes.
Rule for every Skyy page: never put an ItemStack that may carry metadata into an ItemGridSlot.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.1.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1"', 'VERSION = "0.1.1"')
rep("      slots.add(new @IGS@(st));",
    "      slots.add(new @IGS@(new @IS@(st.getItemId(), st.getQuantity())));   // 0.1.1: NO metadata in a grid slot (client disconnect)")
first = s.index('"""') + 3
s = s[:first] + ("0.1.1 (2026-09-25): HOTFIX - the item view's grid gets a metadata-free copy of the item (a rolled item disconnected the\n"
                 "  client: ClientItemMetadata). Notes in tools/auctions_0_1_1_patch.py.\n") + s[first:]
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
