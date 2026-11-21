"""Derive SkyyShards/build_skyyshards_0.4.23.py from the GENERATED SkyyShards 0.4.22 (build_skyyshards_0.4.22.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_22_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.22 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_23_patch.py   then   python SkyyShards/build_skyyshards_0.4.23.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.23.py

0.4.23 (2026-11-21) = THE SHARD CLICKER, FORAGING FIRST (round forage1; Skyy 2026-11-14 docs/answered/world.md "SHARDS -> MENU CLICKER": "lets ditch the whole
  separate island thing, and make it more of a minigame that lives in your menu"; "these look good for baic designs, lets make all the real art look better";
  "start with combat, farming, mining, and foraging"; "so farming still does an island per crop, but the zone 2 stuff is in a different cluster of zone 2
  islands"; "have zone locks for all the shards"; research/Shard-Clicker-Idea.md; Skyy 2026-11-21 "build and deploy everything on your list").
  SPEC (short; the survey first):
  - SURVEY. Vanilla (Assets.zip): no clicker / mini-game page or art - the drops are the vanilla logs (Wood_<X>_Trunk, item ids only), every picture is ours.
    Mods: Skyy's Mods folder has pie-clicker 1.0.4 (BackslashRobotics, a Cookie-Clicker page; no licence file = learn only, nothing copied): one page, every
    click = one server event + a page update, a sound per click, buildings bought with the clicked currency, a scheduler ticking every online player and pushing
    page updates. LEARNED: click -> event -> rebuild is fast enough on a local world; a sound on the moments that matter. NOT TAKEN: the periodic page push
    (HANDOFF section 2 "never periodic page updates") - our spirits already work by the clock (ShMath.settle), so the page shows the new counts on every click.
    Existing SkyyShards code reused as it is: the 0.4.22 storage grid (ShCore.gridOf / collect0 / gridFill), the island data (<kind>.i<n>.type / size / amt / deco /
    irr / totems), the purchases (ShCore.purchaseM, buySub, grow, buyIsland), the coin curve (ShIsl.coins x ShCfg.curve) and the offline window.
  - 1. THE CLICKER PAGE = view 5 of the shard page (ShPage; no new page id, no new command). Opened from the Foraging Shard's menu (its portal on your island ->
    the footer button "Shard clicker"); "Shard menu" goes back. Skyglass kit (tools/skyyui.py glass_*), inline, one root, 1560 x 940. Left: the scene (our sky,
    clouds, the island picture of its size, the trees on the island's real tree spots - Tree Amount decides how many -, the spirit totems + spirits on the centre
    pads, the weather totem, the decorations) and the store strip (the 0.4.22 grid's first 8 kinds, click = collect that kind, Collect all, Storage tab). Right:
    the six upgrades. A zoomed-out island map (button "Islands"): the zone clusters.
  - CLICK A TREE = one server event (kt<spot>:<island slot>). At most click.maxPerSec (8) COUNTED clicks a second per player (more do nothing). The hatchet in
    your hand chops (no hatchet = "hold a hatchet") under the WORLD's tier gate (SkyyGear, Skyy 2026-10-13 docs/answered/gear.md "TOOL SPEED": one tier up = 2.5x
    the hits, two up = 10x, three or more up cannot be broken; fixer forage1fix, critic "uses your tool specs ... same amount of hits"): damage = 1 +
    click.tierStep (25 %) x (axe tier - wood tier) at or above the wood's tier (at most x4), click.oneTierUp (40 % = 2.5x the chops) one tier below,
    click.twoTiersUp (10 % = 10x) two below, refused three or more below ("too low a tier"),
    x (1 + the bp.foraging Breaking Power of skill:bonus:<uuid> - accessories, pets, trees; not the gear source, as SkyyGear's own reader). A tree takes
    click.treeHp (12) damage, then falls: click.logs (3) + Tree size x click.treeSizeLogs (1) of the island's log; EACH log rolls the Foraging Fortune of
    skill:bonus:<uuid> (dd.foraging of every source; the gear source only when its only.foraging names the log - SkyySkills' Perks.fortune rule; the level perk
    part is SkyySkills-internal: UNVERIFIED / next round needs a skill:fn:fortune bridge). XP = click.xpPercent (25) % of the overworld XP of the base logs
    (xp.oak, Fortune extras pay none), paid through skill:fn:addxp (source shard:foraging), whole points (the rest waits in memory). A felled tree grows back in
    click.regrowSec (10) - click.weatherSec (1) x Weather level, at least click.minRegrowSec (3) seconds (memory only: a restart regrows every tree).
    Feedback: "4 / 12" while chopping, "+3 Oak Log" when it falls (a gold pop over the tree) + the collect sound.
  - 2. THE DROPS go into the island's 0.4.22 drop store <kind>.i<n>.drops ("id:qty"), saved at once (a refused save = the tree stands again, nothing added).
    They count against the island's storage (ShMath.usedOf counts .drops for every shard since 0.4.22): a full island = "storage full - Collect first". The grid
    shows them (gridOf now merges every shard's .drops), Collect all / a cell / an island row's Collect pay them FIRST (ShCore.collectHeld: debit + save, then
    the inventory, what does not fit goes back; collection credit as Collect; NO XP - the click paid it), then the 0.4.22 Collect runs unchanged (collectS).
  - 3. THE SIX UPGRADES (coins + the island's Enchanted log, ShIsl.mats "ench"): Tree size = NEW key <kind>.i<n>.nsize 0..click.treeSizeMax (10), cost
    click.treeSizeHours[level] hours of the coin curve at the island's tier + click.treeSizeEnch[level] Enchanted logs (numbers below); Tree count = the
    island's Tree Amount (buySub 0), Weather totem = Irrigation (buySub 2), Decorations = Decorations (buySub 1), Island size = Grow (grow) - the SAME costs and
    code as the Map tab (nothing new to balance); Spirit totem = the placed totems (the button opens the Totems tab on this island: place / tier up there).
    Every button carries the level the page showed (ku<row>:<level>): a double click buys once ("the page is up to date now").
  - 4. ISLANDS IN ZONE CLUSTERS: the map shows 5 zone panels of 3 woods each (tools/tier_tags.py LOGS: 3 tiers a zone). Zone z opens at Foraging
    click.zoneLevel[z] (0 / 20 / 40 / 60 / 80 = the 20-levels-a-zone bands): a locked zone shows its lock and its islands cannot be bought (ShCore.buyIsland0 now
    asks ShIsl.zoneNo for Foraging - the Map tab too); an island you already own stays yours and clickable (nothing lost). Open = show that island; Buy = the
    existing buyIsland (tier order, same cost), carrying the next tier the page showed.
  - 5. TODAY'S ISLANDS ARE THE CLICKER LEVELS: the clicker READS the existing keys (size, amt, deco, irr, totems, stored) - nothing is moved, rewritten or
    migrated, so there is no one-time migration (no History copy / Undo / marker needed); the only new keys are .nsize (0 = missing) and the Foraging .drops.
  NUMBERS (new, Server Setup -> Shards -> Shard clicker; all editable): click.xpPercent 25, click.maxPerSec 8, click.treeHp 12, click.logs 3, click.treeSizeLogs 1,
    click.treeSizeMax 10, click.treeSizeHours 0.02,0.04,0.06,0.09,0.12,0.16,0.2,0.25,0.32,0.4 (T1 Oak: 80 .. 1,600 coins; T15: about 105,000 .. 2,135,000), click.treeSizeEnch
    1,2,3,4,6,8,10,14,18,24, click.regrowSec 10, click.weatherSec 1, click.minRegrowSec 3, click.tierStep 25 %, click.oneTierUp 40 %, click.twoTiersUp 10 %, click.zoneLevel 0,20,40,60,80.
  ART: research/ui-theme-art/shard-clicker-foraging*.png were the basic designs; the build draws its own (CLK_ART_SRC: anti-aliased shapes, lit blobs, value
    noise, strata, vines, grass tufts, flowers) - 15 tree kinds (one per wood tier: broadleaf / bottle / conifer / willow / palm / burnt / crystal), a stump +
    sapling while it regrows, 3 island sizes, totem, spirit, weather totem, 5 decorations, clouds, sky, 15 map islands, lock, 6 upgrade icons -> PNGs under
    Common/UI/Custom/SkyyShards/Map/Clk*@2x.png (registered map textures) + the Skyglass theme files (SUI.glass_texture_files). Nothing committed.
  SAVED DATA: <kind>.i<n>.nsize (Foraging, 0..10) and foraging.i<n>.drops (logs clicked, not collected yet). Old files load unchanged.
  ROLLBACK 0.4.23 -> 0.4.22 alone: no migration. 0.4.22 ignores .nsize (kept in the file; back on 0.4.23 the level returns) and never pays foraging .drops
    (kept in the file, still counted against the island's storage = an island full of clicked logs pauses until 0.4.23 is back): before rolling back, Collect
    all on the Foraging Shard (logs clicked go to the inventory). Server Setup rows click.* are ignored by 0.4.22.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.22.py"), os.path.join(HERE, "build_skyyshards_0.4.23.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.22"\n') and P.has("GENERATED by tools/shards_0_4_22_patch.py") and not P.has("ShClk"), "not the generated SkyyShards 0.4.22"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.23 (2026-11-21)"):].rstrip() + "\n"

# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.22 - build script (javassist via jpype). GENERATED by tools/shards_0_4_22_patch.py from build_skyyshards_0.4.21.py
(generated by tools/shards_0_4_21_patch.py from 0.4.20, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.22" /''', '''"""SkyyShards 0.4.23 - build script (javassist via jpype). GENERATED by tools/shards_0_4_23_patch.py from build_skyyshards_0.4.22.py
(generated by tools/shards_0_4_22_patch.py from 0.4.21, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.23" / "0.4.22" /''')
P.rep('''Run:   python SkyyShards/build_skyyshards_0.4.22.py   -> SkyyShards/SkyyShards-0.4.22.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.22.py
''', '''Run:   python SkyyShards/build_skyyshards_0.4.23.py   -> SkyyShards/SkyyShards-0.4.23.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.23.py
''' + NOTE + '''
0.4.22 notes:
''')
P.rep('VERSION = "0.4.22"\n', 'VERSION = "0.4.23"\n')

# ---------------------------------------------------------------------------------------------------- the clicker's own art (pure Python, drawn at build time)
ART_SRC = r'''# SHARD CLICKER ART (SkyyShards 0.4.23): our own pictures, drawn from code at build time (pure Python, no vanilla pixels, nothing committed).
# A small anti-aliased rasterizer (4 sub-rows per pixel row, exact span coverage across a row) + shading helpers; every picture is RGBA,
# deterministic bytes (no time stamps, zlib 9). ART(...) -> {name: Pic}.
import math as _m
import struct as _st
import zlib as _z


def _rgb(h):
    if isinstance(h, tuple):
        return h
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _mix(a, b, t):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def _hash(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def _vnoise(x, y, sc, s=0):
    # smooth value noise in [0, 1] (bilinear between hashed lattice points)
    fx, fy = x / sc, y / sc
    ix, iy = int(_m.floor(fx)), int(_m.floor(fy))
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = _hash(ix, iy, s), _hash(ix + 1, iy, s)
    c, d = _hash(ix, iy + 1, s), _hash(ix + 1, iy + 1, s)
    return (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty


class Pic(object):
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.c = [0.0] * (w * h * 4)   # premultiplied RGBA floats 0..1

    def put(self, i, r, g, b, a):
        c = self.c
        k = i * 4
        ia = 1.0 - a
        c[k] = r / 255.0 * a + c[k] * ia
        c[k + 1] = g / 255.0 * a + c[k + 1] * ia
        c[k + 2] = b / 255.0 * a + c[k + 2] * ia
        c[k + 3] = a + c[k + 3] * ia

    def png(self):
        w, h, c = self.w, self.h, self.c
        raw = bytearray()
        for y in range(h):
            raw.append(0)
            for x in range(w):
                k = (y * w + x) * 4
                a = c[k + 3]
                if a <= 0.0005:
                    raw.extend(b"\x00\x00\x00\x00")
                    continue
                r, g, b = c[k] / a, c[k + 1] / a, c[k + 2] / a
                raw.extend(bytes((min(255, int(r * 255 + 0.5)), min(255, int(g * 255 + 0.5)), min(255, int(b * 255 + 0.5)), min(255, int(a * 255 + 0.5)))))

        def chunk(t, d):
            return _st.pack(">I", len(d)) + t + d + _st.pack(">I", _z.crc32(t + d) & 0xffffffff)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", _st.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", _z.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


SUB = 4   # sub-rows per pixel row


def _cov_row(spans, w):
    cov = {}
    f = 1.0 / SUB
    for row in spans:
        for x0, x1 in row:
            if x0 < 0:
                x0 = 0.0
            if x1 > w:
                x1 = float(w)
            if x1 <= x0:
                continue
            i0, i1 = int(x0), int(x1)
            if i0 == i1:
                cov[i0] = cov.get(i0, 0.0) + (x1 - x0) * f
                continue
            cov[i0] = cov.get(i0, 0.0) + (i0 + 1 - x0) * f
            for x in range(i0 + 1, i1):
                cov[x] = cov.get(x, 0.0) + f
            if i1 < w:
                cov[i1] = cov.get(i1, 0.0) + (x1 - i1) * f
    return cov


def fill(pic, spanfn, y0, y1, col, alpha=1.0):
    fixed = isinstance(col, tuple)
    for y in range(max(0, int(y0)), min(pic.h, int(_m.ceil(y1)) + 1)):
        rows = [spanfn(y + (s + 0.5) / SUB) for s in range(SUB)]
        cov = _cov_row(rows, pic.w)
        base = y * pic.w
        for x, c in cov.items():
            if c <= 0.001:
                continue
            a = (1.0 if c > 1.0 else c) * alpha
            r, g, b = col if fixed else col(x, y)
            pic.put(base + x, r, g, b, a)


def ellipse(pic, cx, cy, rx, ry, col, alpha=1.0):
    def sp(yf):
        d = (yf - cy) / ry
        if d <= -1.0 or d >= 1.0:
            return []
        h = rx * _m.sqrt(1.0 - d * d)
        return [(cx - h, cx + h)]
    fill(pic, sp, cy - ry - 1, cy + ry + 1, col, alpha)


def poly(pic, pts, col, alpha=1.0):
    n = len(pts)
    ys = [p[1] for p in pts]

    def sp(yf):
        xs = []
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if (y1 <= yf < y2) or (y2 <= yf < y1):
                xs.append(x1 + (yf - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    fill(pic, sp, min(ys) - 1, max(ys) + 1, col, alpha)


def line(pic, x1, y1, x2, y2, wd, col, alpha=1.0):
    dx, dy = x2 - x1, y2 - y1
    L = _m.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * wd / 2.0, dx / L * wd / 2.0
    poly(pic, [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], col, alpha)


def disc(pic, cx, cy, r, col, alpha=1.0):
    ellipse(pic, cx, cy, r, r, col, alpha)


def _cl(c):
    return (max(0, min(255, c[0])), max(0, min(255, c[1])), max(0, min(255, c[2])))


def shade(base, light, dark, cx, cy, r, lx=-0.55, ly=-0.65, ns=0.0, nsc=6.0, seed=0):
    # a lit blob colour function: light from the upper left, value noise ns
    B, Li, D = _rgb(base), _rgb(light), _rgb(dark)

    def f(x, y):
        dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
        t = dx * lx + dy * ly
        c = _mix(B, Li, t * 1.3) if t > 0 else _mix(B, D, -t * 1.1)
        if ns:
            v = (_vnoise(x, y, nsc, seed) - 0.5) * ns * 255
            c = (c[0] + v, c[1] + v, c[2] + v)
        return _cl(c)
    return f


def vgrad(top, bot, y0, y1, ns=0.0, nsc=5.0, seed=0):
    T, Bo = _rgb(top), _rgb(bot)

    def f(x, y):
        c = _mix(T, Bo, (y - y0) / float(max(1, y1 - y0)))
        if ns:
            v = (_vnoise(x, y, nsc, seed) - 0.5) * ns * 255
            c = (c[0] + v, c[1] + v, c[2] + v)
        return _cl(c)
    return f


# ---------------------------------------------------------------------------------------------------- the trees (one per wood tier)
# (shape, leaf base, leaf light, leaf dark, trunk, trunk dark, accent): our own palette per tier's first wood (tools/tier_tags.py LOGS)
TREE_STYLE = {
    1: ("broad", "#4fae3c", "#9be36a", "#256b23", "#7a5230", "#4a301a", None),          # Oak  # ui-data (picture colours)
    2: ("broad", "#7cc44e", "#c6ef8a", "#3d7a2a", "#8f7a5a", "#5a4a33", None),          # Beech  # ui-data (picture colours)
    3: ("broad", "#e0722e", "#ffc06a", "#8f3216", "#6e4a2e", "#40291a", "#ffd27a"),     # Maple  # ui-data (picture colours)
    4: ("sparse", "#9aa64a", "#d6dc8a", "#5a6224", "#8a7350", "#57452c", None),         # Dry  # ui-data (picture colours)
    5: ("bottle", "#3fae8e", "#8fe8c8", "#1d6a55", "#a9875c", "#6b5235", None),         # Bottletree  # ui-data (picture colours)
    6: ("bottle", "#a6c23c", "#e2f080", "#5d7420", "#9a7a55", "#5f4932", None),         # Gumboab  # ui-data (picture colours)
    7: ("conifer", "#2f8a4e", "#74c98a", "#14492a", "#6a4528", "#3e2716", None),        # Fir  # ui-data (picture colours)
    8: ("broad", "#9a5cd6", "#d9a8ff", "#552b85", "#5e4a6e", "#372a44", "#ffd1ff"),     # Spiral  # ui-data (picture colours)
    9: ("conifer", "#2d7a3c", "#6fbf6a", "#123f1e", "#a0452e", "#5e2216", None),        # Redwood  # ui-data (picture colours)
    10: ("burnt", "#4a4440", "#8a7f76", "#221e1c", "#3a2e28", "#1c1512", "#ff8a3a"),     # Burnt  # ui-data (picture colours)
    11: ("broad", "#a9a39a", "#e2ddd2", "#625d56", "#8a857c", "#55514b", None),          # Petrified  # ui-data (picture colours)
    12: ("willow", "#b6c95a", "#eaf5a0", "#6c7d2c", "#6e5a3a", "#433522", None),         # Sallow  # ui-data (picture colours)
    13: ("palm", "#2e9e4a", "#7fe08a", "#135a28", "#8a6a3e", "#56401f", None),           # Jungle  # ui-data (picture colours)
    14: ("broad", "#3a9a52", "#86da8a", "#185a2c", "#7d6244", "#4b3a27", "#f2c94c"),     # Banyan  # ui-data (picture colours)
    15: ("crystal", "#5fd8f0", "#d8fbff", "#2a7fa8", "#7a8fb0", "#47587a", "#ffffff"),   # Crystal  # ui-data (picture colours)
}


def _trunk(pic, cx, by, w, h, col, dark, lean=0.0):
    poly(pic, [(cx - w * 0.62, by), (cx - w * 0.36 + lean, by - h), (cx + w * 0.36 + lean, by - h), (cx + w * 0.62, by)],
         shade(col, "#f0d8b0", dark, cx - w * 0.15, by - h * 0.5, w * 1.2, lx=-1.0, ly=0.0, ns=0.10, nsc=3.0, seed=7))  # ui-data (picture colours)
    for i in range(3):
        x = cx - w * 0.2 + i * w * 0.2
        line(pic, x, by - 3, x + lean * 0.8, by - h + 4, max(1.0, w * 0.07), _rgb(dark), 0.45)
    poly(pic, [(cx - w * 0.6, by), (cx - w * 1.05, by + 1.5), (cx - w * 0.35, by - w * 0.3)], _rgb(dark), 0.95)
    poly(pic, [(cx + w * 0.6, by), (cx + w * 1.05, by + 1.5), (cx + w * 0.35, by - w * 0.3)], _rgb(dark), 0.95)


def _blob(pic, cx, cy, r, st, seed=0, ns=0.16):
    disc(pic, cx + r * 0.10, cy + r * 0.14, r, _rgb(st[3]), 0.6)
    disc(pic, cx, cy, r, shade(st[1], st[2], st[3], cx, cy, r, ns=ns, nsc=max(2.0, r / 3.0), seed=seed))


def _leaf_dots(pic, cx, cy, rx, ry, col, n, seed, sz, alpha=0.85):
    for i in range(n):
        a = _hash(i, 1, seed) * 2 * _m.pi
        d = _m.sqrt(_hash(i, 2, seed))
        disc(pic, cx + _m.cos(a) * rx * d, cy + _m.sin(a) * ry * d, sz * (0.6 + 0.6 * _hash(i, 3, seed)), _rgb(col), alpha)


def tree(tier, W, H, s=2):
    # one tree picture W x H (UI) at scale s; its trunk base at (W / 2, H - 10)
    st = TREE_STYLE[tier]
    shape = st[0]
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    S = s
    cx, by = w / 2.0, h - 10.0 * S
    ellipse(pic, cx + 4 * S, by + 2 * S, w * 0.34, 6 * S, (10, 30, 12), 0.38)
    if shape in ("broad", "sparse", "burnt"):
        _trunk(pic, cx, by, 14 * S, 46 * S, _rgb(st[4]), st[5])
        R = 30 * S
        blobs = [(-24, -60, 0.8), (24, -62, 0.8), (0, -64, 0.85), (-30, -84, 0.72), (30, -86, 0.72), (0, -88, 1.0), (-13, -104, 0.64), (14, -106, 0.6)]
        if shape == "sparse":
            for bx, byy in ((-20, -62), (22, -64), (0, -84)):
                line(pic, cx, by - 40 * S, cx + bx * S, by + byy * S, 3 * S, _rgb(st[5]), 1.0)
            blobs = [(-22, -66, 0.6), (22, -68, 0.6), (0, -88, 0.72), (-8, -106, 0.48)]
        if shape == "burnt":
            for bx, byy, wd in ((-26, -82, 4.5), (24, -88, 4.5), (-8, -108, 3.5), (14, -72, 3), (-34, -64, 2.5)):
                line(pic, cx, by - 40 * S, cx + bx * S, by + byy * S, wd * S, _rgb(st[4]), 1.0)
                line(pic, cx + bx * S * 0.6, by + byy * S * 0.8, cx + bx * S * 1.2, by + (byy - 12) * S, wd * 0.55 * S, _rgb(st[4]), 1.0)
            for i, (bx, byy) in enumerate(((-26, -82), (24, -88), (-8, -108), (14, -72))):
                disc(pic, cx + bx * S, by + byy * S, 10 * S, shade(st[1], st[2], st[3], cx + bx * S, by + byy * S, 10 * S, ns=0.2, seed=i), 0.92)
                disc(pic, cx + bx * S + 2 * S, by + byy * S + 2 * S, 2.4 * S, _rgb(st[6]), 0.95)
                disc(pic, cx + bx * S + 2 * S, by + byy * S + 2 * S, 5 * S, _rgb(st[6]), 0.25)
        else:
            for i, (bx, byy, k) in enumerate(sorted(blobs, key=lambda b: b[1])):
                _blob(pic, cx + bx * S, by + byy * S, R * k, st, seed=tier * 10 + i)
            _leaf_dots(pic, cx - 6 * S, by - 86 * S, 34 * S, 28 * S, st[2], 28, tier, 2.2 * S)
            _leaf_dots(pic, cx + 6 * S, by - 70 * S, 36 * S, 22 * S, st[3], 14, tier + 20, 2.0 * S, 0.55)
            if st[6]:
                _leaf_dots(pic, cx, by - 80 * S, 36 * S, 30 * S, st[6], 10, tier + 50, 2.6 * S, 0.95)
    elif shape == "bottle":
        poly(pic, [(cx - 22 * S, by), (cx - 27 * S, by - 24 * S), (cx - 15 * S, by - 52 * S), (cx + 15 * S, by - 52 * S), (cx + 27 * S, by - 24 * S), (cx + 22 * S, by)],
             shade(st[4], "#f8e0b8", st[5], cx - 10 * S, by - 26 * S, 34 * S, lx=-1.0, ly=0.0, ns=0.1, nsc=3, seed=3))  # ui-data (picture colours)
        for bx, byy in ((-26, -72), (0, -80), (26, -72)):
            line(pic, cx, by - 50 * S, cx + bx * S, by + byy * S, 4 * S, _rgb(st[5]), 1.0)
        for i, (bx, byy, k) in enumerate(((-26, -78, 0.62), (26, -78, 0.62), (0, -90, 0.78), (-12, -100, 0.52), (12, -102, 0.52))):
            _blob(pic, cx + bx * S, by + byy * S, 26 * S * k, st, seed=tier * 10 + i)
        _leaf_dots(pic, cx, by - 88 * S, 34 * S, 18 * S, st[2], 18, tier, 2.0 * S)
    elif shape in ("conifer", "crystal"):
        _trunk(pic, cx, by, 10 * S, 24 * S, _rgb(st[4]), st[5])
        for i, hw, yb in ((0, 46, -18), (1, 40, -42), (2, 33, -64), (3, 25, -86), (4, 16, -104)):
            top = by + (yb - 34) * S
            base_y = by + yb * S
            pts = [(cx - hw * S, base_y), (cx, top), (cx + hw * S, base_y), (cx + hw * 0.5 * S, base_y - 4 * S), (cx, base_y + 2 * S), (cx - hw * 0.5 * S, base_y - 4 * S)]
            poly(pic, [(p[0] + 3 * S, p[1] + 3 * S) for p in pts], _rgb(st[3]), 0.55)
            poly(pic, pts, shade(st[1], st[2], st[3], cx - hw * 0.3 * S, base_y - 12 * S, hw * 1.2 * S, ns=0.16, nsc=3 * S, seed=tier + i))
            poly(pic, [(cx - hw * 0.92 * S, base_y - 1 * S), (cx, top + 2 * S), (cx - 2 * S, base_y - 2 * S)], _rgb(st[2]), 0.3)
        if shape == "crystal":
            for i, (bx, byy, r) in enumerate(((-18, -50, 3.5), (14, -74, 3), (-8, -96, 2.5), (20, -40, 2.5), (0, -122, 3))):
                disc(pic, cx + bx * S, by + byy * S, r * 2.6 * S, _rgb(st[2]), 0.22)
                disc(pic, cx + bx * S, by + byy * S, r * S, _rgb(st[6]), 0.95)
        else:
            _leaf_dots(pic, cx, by - 66 * S, 28 * S, 44 * S, st[2], 18, tier, 1.6 * S)
    elif shape == "willow":
        _trunk(pic, cx, by, 14 * S, 52 * S, _rgb(st[4]), st[5], lean=3 * S)
        for i, (bx, byy, k) in enumerate(((-20, -80, 0.8), (22, -82, 0.8), (0, -98, 0.95))):
            _blob(pic, cx + bx * S, by + byy * S, 28 * S * k, st, seed=tier * 10 + i)
        for i in range(17):
            x = cx + (-42 + i * 5.3) * S
            top = by + (-86 + abs(i - 8) * 2.0) * S
            ln = (30 + 24 * _hash(i, 9, tier)) * S
            ex = x + (i - 8) * 0.7 * S
            line(pic, x, top, ex, top + ln, 3.2 * S, _rgb(st[3] if i % 2 else st[1]), 0.95)
            disc(pic, ex, top + ln, 2.3 * S, _rgb(st[2]), 0.9)
    elif shape == "palm":
        for i in range(7):
            yy = by - i * 12 * S
            ellipse(pic, cx + i * 1.6 * S, yy - 6 * S, 8 * S, 7 * S, shade(st[4], "#e8c890", st[5], cx - 4 * S, yy - 6 * S, 10 * S, lx=-1, ly=0))  # ui-data (picture colours)
        tx, ty = cx + 11 * S, by - 88 * S
        for i, a in enumerate((-170, -20, -140, -50, -110, -80, 160, 20)):
            r = _m.radians(a)
            ln = 54 * S if i < 6 else 40 * S
            up, lo = [], []
            for k in range(9):
                t = k / 8.0
                px = tx + _m.cos(r) * ln * t
                py = ty + _m.sin(r) * ln * t * 0.55 + (t * t) * 30 * S - (6 * S if a < 0 else 0) * t
                wdt = _m.sin(_m.pi * min(1.0, t * 1.15)) * 7 * S + 1.0 * S
                up.append((px, py - wdt))
                lo.append((px, py + wdt * 0.6))
            poly(pic, up + lo[::-1], shade(st[1], st[2], st[3], tx, ty, ln, ns=0.10, seed=i))
            line(pic, tx, ty, up[-1][0], (up[-1][1] + lo[-1][1]) / 2, 1.2 * S, _rgb(st[3]), 0.6)
        disc(pic, tx - 4 * S, ty + 6 * S, 5 * S, _rgb("#6b4a22"))  # ui-data (picture colours)
        disc(pic, tx + 5 * S, ty + 7 * S, 5 * S, _rgb("#7a5428"))  # ui-data (picture colours)
    return pic


def stump(W, H, tier, s=2):
    st = TREE_STYLE[tier]
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 10.0 * s
    ellipse(pic, cx + 3 * s, by + 2 * s, w * 0.24, 5 * s, (10, 30, 12), 0.38)
    poly(pic, [(cx - 13 * s, by), (cx - 11 * s, by - 16 * s), (cx + 11 * s, by - 16 * s), (cx + 13 * s, by)],
         shade(st[4], "#f0d8b0", st[5], cx - 4 * s, by - 8 * s, 16 * s, lx=-1.0, ly=0.0, ns=0.1, nsc=3, seed=2))  # ui-data (picture colours)
    ellipse(pic, cx, by - 16 * s, 11 * s, 4.5 * s, _rgb("#e2c48e"))  # ui-data (picture colours)
    ellipse(pic, cx, by - 16 * s, 6.5 * s, 2.6 * s, _rgb("#c8a468"))  # ui-data (picture colours)
    ellipse(pic, cx, by - 16 * s, 2.5 * s, 1.0 * s, _rgb("#a8844a"))  # ui-data (picture colours)
    line(pic, cx + 17 * s, by, cx + 18 * s, by - 20 * s, 2 * s, _rgb(st[5]))
    for a in (-35, 35, -80):
        r = _m.radians(a - 90)
        ellipse(pic, cx + 18 * s + _m.cos(r) * 6 * s, by - 20 * s + _m.sin(r) * 5 * s, 5.5 * s, 3.2 * s, shade(st[1], st[2], st[3], cx + 18 * s, by - 22 * s, 8 * s))
    return pic


# ---------------------------------------------------------------------------------------------------- the island (Small / Medium / Large)
def island(W, H, s=1, seed=1, hue="#5cbf4a"):  # ui-data (picture colours)
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, cy = w / 2.0, h * 0.34
    rx, ry = w * 0.47, w * 0.47 * 0.36
    for i, (fx, fy, r) in enumerate(((0.17, 0.86, 0.025), (0.84, 0.80, 0.03), (0.71, 0.95, 0.018), (0.29, 0.97, 0.014))):
        c0 = (w * fx, h * fy)
        poly(pic, [(c0[0] - r * w, c0[1] - r * w * 0.3), (c0[0] + r * w, c0[1] - r * w * 0.4), (c0[0] + r * w * 0.5, c0[1] + r * w * 0.9), (c0[0] - r * w * 0.3, c0[1] + r * w * 0.6)],
             shade("#7a6a58", "#b8a690", "#3e342a", c0[0] - r * w * 0.4, c0[1] - r * w * 0.3, r * w * 2.2, ns=0.18, nsc=3, seed=i))  # ui-data (picture colours)
    tip_y = h * 0.985
    n = 28
    top = []
    for i in range(n + 1):
        a = _m.pi * i / n
        top.append((cx - _m.cos(a) * rx, cy + _m.sin(a) * ry + h * 0.03))
    under = []
    for i in range(n + 1):
        t = i / float(n)
        j = (_hash(i, 4, seed) - 0.5) * 0.2
        u = abs(t - 0.5) * 2.0
        dep = (1.0 - u ** 1.7) * (tip_y - cy - ry * 0.6) * (0.8 + j) + ry * 0.62
        px = top[n - i][0] * 0.88 + cx * 0.12 + (_hash(i, 5, seed) - 0.5) * w * 0.02
        under.append((px, cy + dep))
    strata = ("#8a7558", "#6e5c46", "#9a8466", "#5c4b39", "#7d694f")  # ui-data (picture colours)

    def rock(x, y):
        k = int(((y - cy) / (h * 0.06)) + (_vnoise(x, y, 18 * s, seed) - 0.5) * 1.4) % len(strata)
        c = _rgb(strata[k])
        lx = (x - cx) / rx
        c = _mix(c, (20, 16, 12), max(0.0, lx * 0.55 + (y - cy) / (h * 1.6)))
        c = _mix(c, (226, 206, 176), max(0.0, -lx - 0.5) * 0.55)
        v = (_vnoise(x, y, 5.0 * s, seed + 3) - 0.5) * 22 + (_vnoise(x, y, 1.6 * s, seed + 5) - 0.5) * 8
        return _cl((c[0] + v, c[1] + v, c[2] + v))
    poly(pic, top + under, rock)
    for i in range(10):
        x0 = cx - rx * 0.88 + i * rx * 0.195 + (_hash(i, 6, seed) - 0.5) * 12 * s
        a = _m.acos(max(-1.0, min(1.0, (cx - x0) / rx)))
        y0 = cy + _m.sin(a) * ry + h * 0.04
        ln = (18 + 42 * _hash(i, 7, seed)) * s
        col = _rgb("#3f7d2a" if i % 3 else "#5a3d22")  # ui-data (picture colours)
        ex = x0 + (_hash(i, 8, seed) - 0.5) * 10 * s
        line(pic, x0, y0, ex, y0 + ln, 2.0 * s, col, 0.9)
        if i % 3:
            for k in range(3):
                ellipse(pic, x0 + (ex - x0) * (k + 1) / 4.0 + 2 * s, y0 + ln * (k + 1) / 4.0, 3 * s, 1.8 * s, _rgb("#6fbf4a"), 0.9)  # ui-data (picture colours)
    ellipse(pic, cx, cy + h * 0.038, rx * 1.004, ry * 1.02, vgrad("#80583a", "#4a3018", cy, cy + ry * 1.05, ns=0.12, nsc=3 * s, seed=seed))  # ui-data (picture colours)
    ellipse(pic, cx, cy + h * 0.012, rx * 1.0, ry * 1.0, _rgb("#3f8a2c"))  # ui-data (picture colours)
    G = _rgb(hue)
    GL, GD = _mix(G, (255, 255, 200), 0.36), _mix(G, (0, 30, 0), 0.40)

    def grass(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        q = dx * dx + dy * dy
        t = -dx * 0.45 - dy * 0.55
        c = _mix(G, GL, t * 0.9) if t > 0 else _mix(G, GD, -t * 0.7)
        c = _mix(c, GD, max(0.0, q - 0.80) * 2.4)
        v = (_vnoise(x, y, 11.0 * s, seed + 9) - 0.5) * 34 + (_vnoise(x, y, 2.4 * s, seed + 11) - 0.5) * 20
        return _cl((c[0] + v * 0.6, c[1] + v, c[2] + v * 0.4))
    ellipse(pic, cx, cy, rx, ry, grass)
    GT = _mix(GD, (0, 0, 0), 0.12)
    for i in range(int(90 * w / 700.0)):
        a = _hash(i, 12, seed) * 2 * _m.pi
        d = 0.15 + 0.8 * _m.sqrt(_hash(i, 13, seed))
        x, y = cx + _m.cos(a) * rx * d, cy + _m.sin(a) * ry * d
        for k in (-1, 0, 1):
            line(pic, x + k * 2 * s, y, x + k * 3.2 * s, y - (5 + 2 * (1 - abs(k))) * s, 1.3 * s, GT, 0.7)
    for i in range(int(50 * w / 700.0)):
        a = _hash(i, 14, seed) * 2 * _m.pi
        d = 0.2 + 0.74 * _m.sqrt(_hash(i, 15, seed))
        col = ("#fff4a8", "#ffffff", "#ff9ad0", "#a8d8ff")[i % 4]  # ui-data (picture colours)
        disc(pic, cx + _m.cos(a) * rx * d, cy + _m.sin(a) * ry * d, 1.7 * s, _rgb(col), 0.95)
    return pic


# ---------------------------------------------------------------------------------------------------- totems, spirits, weather, decorations, map
def totem(W, H, s=2, gem="#45a8ff"):  # ui-data (picture colours)
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 8.0 * s
    ellipse(pic, cx + 2 * s, by + 1 * s, 16 * s, 4.5 * s, (10, 30, 12), 0.38)
    wood = ["#9a6a3a", "#8a5a2b", "#a87444"]  # ui-data (picture colours)
    seg = (H - 36) * s / 3.0
    for i in range(3):
        y1 = by - i * seg
        y0 = y1 - seg + 2 * s
        poly(pic, [(cx - 13 * s, y1), (cx - 12 * s, y0), (cx + 12 * s, y0), (cx + 13 * s, y1)],
             shade(wood[i], "#e6b47a", "#3f2610", cx - 6 * s, (y0 + y1) / 2, 16 * s, lx=-1, ly=0, ns=0.08, nsc=2.5, seed=i))  # ui-data (picture colours)
        line(pic, cx - 12 * s, y0 + 1 * s, cx + 12 * s, y0 + 1 * s, 1.4 * s, _rgb("#3f2610"), 0.8)  # ui-data (picture colours)
        ey = y0 + seg * 0.38
        for ex in (-5.5, 5.5):
            disc(pic, cx + ex * s, ey, 3.3 * s, _rgb("#f2ead8"))  # ui-data (picture colours)
            disc(pic, cx + ex * s + 0.6 * s, ey + 0.4 * s, 1.6 * s, _rgb("#1a1208"))  # ui-data (picture colours)
        line(pic, cx - 5 * s, y0 + seg * 0.74, cx + 5 * s, y0 + seg * 0.74, 2.2 * s, _rgb("#2a1a0c"))  # ui-data (picture colours)
    ty = by - 3 * seg
    for sg in (-1, 1):
        poly(pic, [(cx + sg * 10 * s, ty + 4 * s), (cx + sg * 30 * s, ty - 10 * s), (cx + sg * 26 * s, ty + 2 * s), (cx + sg * 30 * s, ty + 8 * s), (cx + sg * 12 * s, ty + 10 * s)],
             shade("#5fb0ff", "#d8f0ff", "#1f5a9a", cx + sg * 20 * s, ty, 16 * s, ns=0.06))  # ui-data (picture colours)
    disc(pic, cx, ty - 8 * s, 16 * s, _rgb(gem), 0.16)
    disc(pic, cx, ty - 8 * s, 11 * s, _rgb(gem), 0.18)
    poly(pic, [(cx, ty - 21 * s), (cx + 8 * s, ty - 8 * s), (cx, ty + 3 * s), (cx - 8 * s, ty - 8 * s)], shade(gem, "#ffffff", "#0a2a5a", cx - 3 * s, ty - 12 * s, 10 * s))  # ui-data (picture colours)
    return pic


def spirit(W, H, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, cy = w / 2.0, h * 0.47
    r = min(w, h) * 0.30
    disc(pic, cx, cy, r * 1.6, _rgb("#9ff0ff"), 0.14)  # ui-data (picture colours)
    disc(pic, cx, cy, r * 1.3, _rgb("#9ff0ff"), 0.18)  # ui-data (picture colours)
    poly(pic, [(cx - r, cy), (cx - r * 0.9, cy + r * 1.3), (cx - r * 0.4, cy + r * 1.0), (cx, cy + r * 1.35), (cx + r * 0.4, cy + r * 1.0), (cx + r * 0.95, cy + r * 1.3), (cx + r, cy)],
         shade("#bff6ff", "#ffffff", "#4ab8e0", cx, cy, r * 1.3))  # ui-data (picture colours)
    disc(pic, cx, cy, r, shade("#c8f8ff", "#ffffff", "#5ac0e8", cx, cy, r))  # ui-data (picture colours)
    for ex in (-0.36, 0.36):
        ellipse(pic, cx + ex * r, cy - r * 0.05, r * 0.16, r * 0.22, _rgb("#1b2a40"))  # ui-data (picture colours)
        disc(pic, cx + ex * r - r * 0.05, cy - r * 0.12, r * 0.06, _rgb("#ffffff"))  # ui-data (picture colours)
    ellipse(pic, cx - r * 0.56, cy + r * 0.24, r * 0.14, r * 0.08, _rgb("#ff9ab8"), 0.8)  # ui-data (picture colours)
    ellipse(pic, cx + r * 0.56, cy + r * 0.24, r * 0.14, r * 0.08, _rgb("#ff9ab8"), 0.8)  # ui-data (picture colours)
    line(pic, cx, cy - r, cx + r * 0.1, cy - r * 1.35, 1.6 * s, _rgb("#3f8a2a"))  # ui-data (picture colours)
    ellipse(pic, cx + r * 0.32, cy - r * 1.42, r * 0.28, r * 0.14, _rgb("#6fd04a"))  # ui-data (picture colours)
    ellipse(pic, cx - r * 0.16, cy - r * 1.38, r * 0.22, r * 0.12, _rgb("#5ac040"))  # ui-data (picture colours)
    return pic


def cloudpic(W, H, s=1, alpha=0.95):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    blobs = [(0.30, 0.56, 0.34), (0.50, 0.42, 0.44), (0.70, 0.54, 0.34), (0.16, 0.68, 0.22), (0.85, 0.68, 0.22), (0.5, 0.66, 0.3)]
    for fx, fy, fr in blobs:
        disc(pic, w * fx + 2 * s, h * fy + 3 * s, h * fr, _rgb("#a6c8ea"), 0.55 * alpha)  # ui-data (picture colours)
    for fx, fy, fr in blobs:
        disc(pic, w * fx, h * fy, h * fr, shade("#ffffff", "#ffffff", "#d2e6f8", w * fx, h * fy, h * fr), alpha)  # ui-data (picture colours)
    return pic


def weather(W, H, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 8.0 * s
    ellipse(pic, cx + 2 * s, by + 1 * s, 12 * s, 4 * s, (10, 30, 12), 0.38)
    poly(pic, [(cx - 6 * s, by), (cx - 5 * s, by - 64 * s), (cx + 5 * s, by - 64 * s), (cx + 6 * s, by)], shade("#8a5a2b", "#e6b47a", "#3f2610", cx - 3 * s, by - 30 * s, 10 * s, lx=-1, ly=0, ns=0.08))  # ui-data (picture colours)
    for i in range(3):
        disc(pic, cx, by - (16 + i * 18) * s, 3 * s, _rgb("#5fb0ff"), 0.9)  # ui-data (picture colours)
    clx, cly = cx, by - 82 * s
    for i in range(6):
        line(pic, clx - 16 * s + i * 6.5 * s, cly + 10 * s, clx - 18 * s + i * 6.5 * s, cly + 24 * s, 1.8 * s, _rgb("#7fc8ff"), 0.9)  # ui-data (picture colours)
    for fx, fy, fr in ((-12, 2, 10), (0, -4, 13), (12, 2, 10), (0, 6, 12)):
        disc(pic, clx + fx * s + 1.5 * s, cly + fy * s + 2 * s, fr * s, _rgb("#8aa4c0"), 0.6)  # ui-data (picture colours)
    for fx, fy, fr in ((-12, 2, 10), (0, -4, 13), (12, 2, 10), (0, 6, 12)):
        disc(pic, clx + fx * s, cly + fy * s, fr * s, shade("#f4f8ff", "#ffffff", "#b8c8dc", clx + fx * s, cly + fy * s, fr * s))  # ui-data (picture colours)
    return pic


def deco(kind, W, H, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx, by = w / 2.0, h - 6.0 * s
    if kind == "flowers":
        for i in range(9):
            x = cx + (_hash(i, 1, 3) - 0.5) * w * 0.8
            y = by - 6 * s - _hash(i, 2, 3) * h * 0.4
            line(pic, x, y, x, y + 9 * s, 1.2 * s, _rgb("#2f7a2a"))  # ui-data (picture colours)
            col = ("#ff6fb0", "#fff07a", "#ffffff", "#9ad0ff", "#ff9a5a")[i % 5]  # ui-data (picture colours)
            for a in range(5):
                r = a * 2 * _m.pi / 5
                disc(pic, x + _m.cos(r) * 2.6 * s, y + _m.sin(r) * 2.6 * s, 2.2 * s, _rgb(col))
            disc(pic, x, y, 1.6 * s, _rgb("#f2b830"))  # ui-data (picture colours)
    elif kind == "mushrooms":
        for i, (dx, sc) in enumerate(((-10, 1.0), (9, 0.75), (-1, 0.55))):
            x = cx + dx * s
            poly(pic, [(x - 3 * sc * s, by), (x - 2.5 * sc * s, by - 12 * sc * s), (x + 2.5 * sc * s, by - 12 * sc * s), (x + 3 * sc * s, by)], _rgb("#f2ead8"))  # ui-data (picture colours)
            ellipse(pic, x, by - 13 * sc * s, 10 * sc * s, 7 * sc * s, shade("#e0412f", "#ff9a80", "#8a1a10", x - 3 * s, by - 16 * sc * s, 10 * sc * s))  # ui-data (picture colours)
            for k in range(3):
                disc(pic, x + (k - 1) * 4 * sc * s, by - (15 - (k % 2) * 3) * sc * s, 1.5 * sc * s, _rgb("#ffffff"))  # ui-data (picture colours)
    elif kind == "lamp":
        ellipse(pic, cx, by + 1 * s, 8 * s, 3 * s, (10, 30, 12), 0.38)
        line(pic, cx, by, cx, by - 42 * s, 3 * s, _rgb("#2a2a30"))  # ui-data (picture colours)
        disc(pic, cx, by - 48 * s, 15 * s, _rgb("#ffe48a"), 0.2)  # ui-data (picture colours)
        disc(pic, cx, by - 48 * s, 9 * s, _rgb("#ffe48a"), 0.22)  # ui-data (picture colours)
        poly(pic, [(cx - 6 * s, by - 42 * s), (cx - 7 * s, by - 54 * s), (cx + 7 * s, by - 54 * s), (cx + 6 * s, by - 42 * s)], _rgb("#fff2b0"))  # ui-data (picture colours)
        poly(pic, [(cx - 9 * s, by - 54 * s), (cx, by - 60 * s), (cx + 9 * s, by - 54 * s)], _rgb("#2a2a30"))  # ui-data (picture colours)
    elif kind == "fence":
        for yy in (8, 15):
            line(pic, cx - w * 0.43, by - yy * s, cx + w * 0.43, by - yy * s, 2.6 * s, _rgb("#8a5a2b"))  # ui-data (picture colours)
        for i in range(6):
            x = cx - w * 0.4 + i * w * 0.16
            poly(pic, [(x - 2.6 * s, by), (x - 2.6 * s, by - 19 * s), (x, by - 22 * s), (x + 2.6 * s, by - 19 * s), (x + 2.6 * s, by)], shade("#b07a44", "#f0c890", "#5a3818", x - 1 * s, by - 10 * s, 5 * s, lx=-1, ly=0))  # ui-data (picture colours)
    elif kind == "pond":
        ellipse(pic, cx, by - h * 0.36, w * 0.47, h * 0.33, _rgb("#5a8a3a"))  # ui-data (picture colours)
        ellipse(pic, cx, by - h * 0.36, w * 0.43, h * 0.28, vgrad("#2f7fd0", "#86caff", by - h * 0.62, by - h * 0.08))  # ui-data (picture colours)
        ellipse(pic, cx - w * 0.14, by - h * 0.42, w * 0.12, h * 0.06, _rgb("#d8efff"), 0.7)  # ui-data (picture colours)
        ellipse(pic, cx + w * 0.16, by - h * 0.30, w * 0.07, h * 0.045, _rgb("#3f9a3a"))  # ui-data (picture colours)
        disc(pic, cx + w * 0.2, by - h * 0.32, 2 * s, _rgb("#ffffff"))  # ui-data (picture colours)
    return pic


def lock(W, H, s=2):
    w, h = int(W * s), int(H * s)
    pic = Pic(w, h)
    cx = w / 2.0
    ellipse(pic, cx, h * 0.3, w * 0.22 + 2 * s, w * 0.24, _rgb("#c2d1e2"))  # ui-data (picture colours)
    ellipse(pic, cx, h * 0.3, w * 0.22 - 2.5 * s, w * 0.24 - 4.5 * s, (0, 0, 0), 0.0)
    line(pic, cx - w * 0.22, h * 0.48, cx - w * 0.22, h * 0.3, 4.4 * s, _rgb("#c2d1e2"))  # ui-data (picture colours)
    line(pic, cx + w * 0.22, h * 0.48, cx + w * 0.22, h * 0.3, 4.4 * s, _rgb("#c2d1e2"))  # ui-data (picture colours)
    poly(pic, [(cx - w * 0.34, h * 0.46), (cx + w * 0.34, h * 0.46), (cx + w * 0.34, h * 0.9), (cx - w * 0.34, h * 0.9)], shade("#c9a04e", "#f1d58c", "#6b5122", cx - w * 0.1, h * 0.6, w * 0.4))  # ui-data (picture colours)
    disc(pic, cx, h * 0.63, 3.2 * s, _rgb("#2a1a0c"))  # ui-data (picture colours)
    line(pic, cx, h * 0.63, cx, h * 0.77, 2.6 * s, _rgb("#2a1a0c"))  # ui-data (picture colours)
    return pic


def sky(W, H):
    pic = Pic(W, H)
    poly(pic, [(0, 0), (W, 0), (W, H), (0, H)], vgrad("#4f9fea", "#d6edff", 0, H))  # ui-data (picture colours)
    return pic


def paste(dst, src, ox, oy, sc):
    # box-filtered paste of src scaled by sc (<= 1) onto dst at (ox, oy), source-over
    sw, sh = src.w, src.h
    dw, dh = int(sw * sc), int(sh * sc)
    inv = 1.0 / sc
    sc_ = src.c
    for y in range(dh):
        yy = oy + y
        if yy < 0 or yy >= dst.h:
            continue
        sy0 = int(y * inv)
        sy1 = min(sh, max(sy0 + 1, int((y + 1) * inv)))
        for x in range(dw):
            xx = ox + x
            if xx < 0 or xx >= dst.w:
                continue
            sx0 = int(x * inv)
            sx1 = min(sw, max(sx0 + 1, int((x + 1) * inv)))
            r = g = b = a = 0.0
            n = 0
            for y2 in range(sy0, sy1):
                k0 = (y2 * sw + sx0) * 4
                for x2 in range(sx0, sx1):
                    r += sc_[k0]; g += sc_[k0 + 1]; b += sc_[k0 + 2]; a += sc_[k0 + 3]
                    k0 += 4
                    n += 1
            if n == 0 or a <= 0.0:
                continue
            r, g, b, a = r / n, g / n, b / n, a / n
            k = (yy * dst.w + xx) * 4
            ia = 1.0 - a
            dc = dst.c
            dc[k] = r + dc[k] * ia
            dc[k + 1] = g + dc[k + 1] * ia
            dc[k + 2] = b + dc[k + 2] * ia
            dc[k + 3] = a + dc[k + 3] * ia


def mini_island(W, H, tier, s=2):
    # the cluster map's island: a small floating island + 3 trees of that tier
    w, h = int(W * s), int(H * s)
    hue = {10: "#6f7a52", 11: "#8a9a6a", 15: "#6fc8b8"}.get(tier, "#5cbf4a")  # ui-data (picture colours)
    base = Pic(w, h)
    top = int(h * 0.30)
    paste(base, island(W, int(H * 0.70), s, seed=tier, hue=hue), 0, top, 1.0)
    t = tree(tier, 110, 140, s=1)
    gy = top + h * 0.70 * 0.34
    for fx, dy, sc in ((0.30, -0.10, 0.30), (0.70, -0.10, 0.30), (0.5, 0.06, 0.36)):
        paste(base, t, int(w * fx - 110 * sc * s / 2.0), int(gy + dy * h * 0.70 - (140 - 10) * sc * s), sc * s)
    return base


def icon(kind, s=2):
    # the upgrade rows' 56 x 56 icons
    W = 56
    p = Pic(int(W * s), int(W * s))
    if kind == "nsize":
        paste(p, tree(1, 110, 140, s=1), int(2 * s), int(-6 * s), 0.46 * s)
        disc(p, 44 * s, 42 * s, 9 * s, _rgb("#4fd88a"))  # ui-data (picture colours)
        line(p, 44 * s, 37 * s, 44 * s, 47 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
        line(p, 39 * s, 42 * s, 49 * s, 42 * s, 3 * s, _rgb("#0b1322"))  # ui-data (picture colours)
    elif kind == "ncount":
        t = tree(1, 110, 140, s=1)
        for ox, oy, sc in ((-10, -4, 0.32), (20, -6, 0.32), (5, 6, 0.36)):
            paste(p, t, int(ox * s), int(oy * s), sc * s)
    elif kind == "spirit":
        paste(p, totem(60, 110, s=1), int(-2 * s), int(2 * s), 0.46 * s)
        paste(p, spirit(56, 60, s=1), int(24 * s), int(16 * s), 0.55 * s)
    elif kind == "weather":
        paste(p, weather(56, 120, s=1), int(14 * s), int(0 * s), 0.46 * s)
    elif kind == "isize":
        paste(p, island(200, 120, s=1, seed=3), int(0 * s), int(10 * s), 0.28 * s)
    else:
        paste(p, deco("flowers", 60, 40, s=1), int(2 * s), int(24 * s), 0.85 * s)
        paste(p, deco("mushrooms", 50, 40, s=1), int(20 * s), int(6 * s), 0.8 * s)
    return p


def ART(tiers, sizes):
    # every picture of the clicker: {name: Pic}. sizes = {1: (W, H), 2: ..., 3: ...} = the island pictures (UI px, drawn at 1x)
    out = {}
    out["Sky"] = sky(64, 160)
    out["CloudA"] = cloudpic(220, 90, s=1)
    out["CloudB"] = cloudpic(160, 70, s=1, alpha=0.85)
    for sz, (W, H) in sorted(sizes.items()):
        out["Isl%d" % sz] = island(W, H, 1, seed=sz)
    for t in tiers:
        out["Tree%d" % t] = tree(t, 110, 140, s=2)
        out["Stump%d" % t] = stump(110, 140, t, s=2)
        out["Map%d" % t] = mini_island(150, 100, t, s=2)
    out["Totem"] = totem(60, 110, s=2)
    out["Spirit"] = spirit(56, 60, s=2)
    out["Weather"] = weather(56, 120, s=2)
    for k, (W, H) in (("Flowers", (60, 40)), ("Mushrooms", (50, 40)), ("Lamp", (30, 70)), ("Fence", (110, 34)), ("Pond", (120, 60))):
        out["Deco" + k] = deco(k.lower(), W, H, s=2)
    out["Lock"] = lock(40, 48, s=2)
    for k in ("nsize", "ncount", "spirit", "weather", "isize", "deco"):
        out["Up" + k.capitalize()] = icon(k, s=2)
    return out
'''
# ---------------------------------------------------------------------------------------------------- ShClk + the art + the page markup (inserted before ShMap)
CLK_BLOCK = r'''# ================= 0.4.23 THE SHARD CLICKER (Foraging first; tools/shards_0_4_23_patch.py; research/Shard-Clicker-Idea.md) =================
# ---- ShClk: one click = one chop (rate cap, the hatchet in hand, Breaking Power + Fortune from skill:bonus:<uuid>, a tree's damage + regrow in
# memory), a felled tree's logs into <kind>.i<n>.drops (saved at once), the XP; the Tree size purchase (<kind>.i<n>.nsize)
import time as _time423
CK_AXES = [(_i, int(_TT48.tier(_i))) for _i in sorted(_TT48.ROWS) if _i.startswith("Tool_Hatchet_") and _TT48.tier(_i)]
CK_METALS = [(_w, int(_t)) for _w, _t in _TT48.TOOL_METALS]
assert len(CK_AXES) >= 20 and ("Tool_Hatchet_Copper", 1) in CK_AXES and ("Tool_Hatchet_Iron", 2) in CK_AXES, CK_AXES[:4]
CK_NSPOT = max(len(_t) for _t in TREE48)
assert CK_NSPOT == 48 and len(LAD[CK_FK]) == 15 and KINDS[CK_FK] == "Foraging"
ckc = mk("ShClk")
for f in ("public static final int FK = %d;" % CK_FK, "public static final int NSPOT = %d;" % CK_NSPOT,
          "public static final String[] AXE_ID = new String[] { %s };" % ", ".join(jlit(_a) for _a, _t in CK_AXES),
          "public static final int[] AXE_T = new int[] { %s };" % ", ".join(str(_t) for _a, _t in CK_AXES),
          "public static final String[] METAL_W = new String[] { %s };" % ", ".join(jlit(_w) for _w, _t in CK_METALS),
          "public static final int[] METAL_T = new int[] { %s };" % ", ".join(str(_t) for _w, _t in CK_METALS),
          "public static volatile String HAND_TEST = null;",
          "public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap TREES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap XPA = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicLong CHOPS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong FELLS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong CAPPED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong LOGS = new java.util.concurrent.atomic.AtomicLong();"):
    F(ckc, f)
M(ckc, "public static Object[] res(String a, String b) { return new Object[] { a, b }; }")
# the hatchet's tier: tools/tier_tags.py's hatchets (vanilla, the _SkyWynn forever tools, the multitools); another id with "Hatchet" / "Multitool" =
# the best metal word in it (else T1); 0 = not a hatchet
M(ckc, r"""
public static int axeTier(String id) {
  if (id == null || id.length() == 0) return 0;
  for (int i = 0; i < AXE_ID.length; i++) if (AXE_ID[i].equals(id)) return AXE_T[i];
  if (id.indexOf("Hatchet") < 0 && id.indexOf("Multitool") < 0) return 0;
  String[] w = id.split("_");
  int best = 0;
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (METAL_W[j].equals(w[i]) && METAL_T[j] > best) best = METAL_T[j];
  return best > 0 ? best : 1;
}""")
M(ckc, r"""
public static boolean onlyHit(String o, String fam) {
  if (o == null) return true;
  if (fam == null) return false;
  String[] ps = o.split(",");
  for (int i = 0; i < ps.length; i++) {
    String q = ps[i].trim();
    if (q.length() > 0 && fam.indexOf(q) >= 0) return true;
  }
  return false;
}""")
# the sum of `key` over every source of skill:bonus:<uuid> (SkyyTrees nodes, accessories, pets, the held tool = "gear"). block != null: the gear source
# counts only when its only.foraging names the block (SkyySkills Perks.fortune); block == null: the gear source never counts (SkyyGear's accBp)
M(ckc, r"""
public static double bonusSum(java.util.UUID u, String key, String block) {
  if (u == null) return 0.0;
  try {
    Object o = @PKG@.ShCfg.bridge().get("skill:bonus:" + u.toString());
    if (!(o instanceof java.util.Map)) return 0.0;
    double t = 0.0;
    java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getValue() instanceof java.util.Map)) continue;
      java.util.Map m = (java.util.Map) e.getValue();
      Object v = m.get(key);
      if (!(v instanceof Number)) continue;
      double d = ((Number) v).doubleValue();
      if (Double.isNaN(d) || d <= 0.0) continue;
      if ("gear".equals(String.valueOf(e.getKey()))) {
        if (block == null) continue;
        Object on = m.get("only.foraging");
        if (on != null && !onlyHit(String.valueOf(on), block)) continue;
      }
      t += d;
    }
    return t > 100.0 ? 100.0 : t;
  } catch (Throwable x) { return 0.0; }
}""")
M(ckc, "public static double fortune(java.util.UUID u, String block) { return bonusSum(u, \"dd.foraging\", block); }")
M(ckc, "public static double bp(java.util.UUID u) { return bonusSum(u, \"bp.foraging\", (String) null); }")
# SkyySkills Perks.extras: the whole part always + one more when r < the rest (at most 100)
M(ckc, r"""
public static int extras(double t, double r) {
  if (!(t > 0.0) || Double.isNaN(t)) return 0;
  if (t >= 100.0) return 100;
  int w = (int) Math.floor(t);
  return w + (r < t - (double) w ? 1 : 0);
}""")
M(ckc, r"""
public static double dmg(int axeT, int woodT, double bpSum) {
  int up = woodT - axeT;
  if (up >= 3) return 0.0;
  double d;
  if (up == 2) d = (double) @PKG@.ShCfg.CK_UP2 / 100.0;
  else if (up == 1) d = (double) @PKG@.ShCfg.CK_UP1 / 100.0;
  else d = 1.0 + (double) @PKG@.ShCfg.CK_TSTEP / 100.0 * (double) (axeT - woodT);
  if (d > 4.0) d = 4.0;
  if (!(d > 0.0)) return 0.0;
  return d * (1.0 + (bpSum > 0.0 ? bpSum : 0.0));
}""")
# the click cap: at most click.maxPerSec COUNTED clicks in a second per player (the rest do nothing at all)
M(ckc, r"""
public static synchronized boolean tick(java.util.UUID u, long now) {
  if (u == null) return false;
  Object o = RATE.get(u);
  long[] w = o == null ? new long[2] : (long[]) o;
  if (o == null) RATE.put(u, w);
  if (now - w[0] >= 1000L || now < w[0]) { w[0] = now; w[1] = 0L; }
  if (w[1] >= (long) @PKG@.ShCfg.CK_CPS) return false;
  w[1] = w[1] + 1L;
  return true;
}""")
# a tree's state (memory only; key = profile|island slot): damage taken + the time it stands again
M(ckc, r"""
public static synchronized Object[] state(String key) {
  Object o = TREES.get(key);
  if (o == null) { o = new Object[] { new double[NSPOT], new long[NSPOT] }; TREES.put(key, o); }
  return (Object[]) o;
}""")
# one chop: < 0 = growing back (-(ms left) - 1), 0 = it fell now (damage reset, regrowing), > 0 = the damage it can still take
M(ckc, r"""
public static synchronized double hit(String key, int spot, double dmg, double hpMax, long now, long regrowMs) {
  if (spot < 0 || spot >= NSPOT) return -1.0;
  Object[] s = state(key);
  double[] d = (double[]) s[0];
  long[] r = (long[]) s[1];
  if (r[spot] > now) return -1.0 - (double) (r[spot] - now);
  d[spot] = d[spot] + dmg;
  if (d[spot] + 0.0000001 >= hpMax) { d[spot] = 0.0; r[spot] = now + regrowMs; return 0.0; }
  return hpMax - d[spot];
}""")
M(ckc, r"""
public static synchronized void unfell(String key, int spot, double hpMax) {
  if (spot < 0 || spot >= NSPOT) return;
  Object[] s = state(key);
  ((long[]) s[1])[spot] = 0L;
  ((double[]) s[0])[spot] = hpMax * 0.999;
}""")
M(ckc, r"""
public static synchronized long readyAt(String key, int spot) {
  Object o = TREES.get(key);
  if (o == null || spot < 0 || spot >= NSPOT) return 0L;
  return ((long[]) ((Object[]) o)[1])[spot];
}""")
M(ckc, r"""
public static long regrowMs(int irr) {
  long s = (long) @PKG@.ShCfg.CK_REGROW - (long) @PKG@.ShCfg.CK_WSTEP * (long) (irr < 0 ? 0 : irr);
  if (s < (long) @PKG@.ShCfg.CK_RMIN) s = (long) @PKG@.ShCfg.CK_RMIN;
  return s < 0L ? 0L : s * 1000L;
}""")
M(ckc, "public static int nsize(java.util.Properties p, int kd, int slot) { return @PKG@.ShStore.intv(p, @PKG@.ShMath.ik(kd, slot, \"nsize\"), 0, 0, 10); }")
M(ckc, "public static long logsAt(int ns) { return (long) @PKG@.ShCfg.CK_DROPS + (long) ns * (long) @PKG@.ShCfg.CK_NS_PER; }")
# the XP of the clicks: fractions wait in memory per player AND profile (fixer: a profile switch never carries a fraction over), whole points are paid
M(ckc, r"""
public static synchronized long accXp(String xk, double add) {
  if (xk == null || !(add > 0.0)) return 0L;
  Object o = XPA.get(xk);
  double[] a = o == null ? new double[1] : (double[]) o;
  if (o == null) XPA.put(xk, a);
  a[0] = a[0] + add;
  long w = (long) Math.floor(a[0] + 0.000000001);
  a[0] = a[0] - (double) w;
  if (a[0] < 0.0) a[0] = 0.0;
  return w;
}""")
# THE CLICK: Object[]{ status ("+..." / "-..." / "=..." / "" = nothing to say), pop text over the tree }. World thread; the bridges outside the store lock
M(ckc, r"""
public static Object[] chop(java.util.UUID u, String k, int kd, int slot, int spot, String hand) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON) return res("-The shard clicker is switched off on this server.", "");
  if (kd != FK) return res("-Only the Foraging Shard has a clicker so far.", "");
  int at = axeTier(hand);
  if (at <= 0) return res("-Hold a hatchet - the clicker chops with the hatchet in your hand.", "");
  long now = @PKG@.ShCore.now();
  if (!tick(u, now)) { CAPPED.incrementAndGet(); return res("", ""); }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return res("-This shard's file could not be read.", "");
  String no = @PKG@.ShCore.gate(u, k, kd, p);
  if (no != null) return res(no, "");
  int t; int n; int irr; long use; long lim;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return res("-That island is not yours yet.", "");
    t = @PKG@.ShIsl.ty(kd, p, slot);
    n = @PKG@.ShIsl.treeN(@PKG@.ShMath.size(kd, p, slot), @PKG@.ShIsl.sub(p, kd, slot, 0));
    irr = @PKG@.ShIsl.sub(p, kd, slot, 2);
    @PKG@.ShMath.settle(kd, p, slot, now);
    use = @PKG@.ShMath.usedOf(kd, p, slot);
    lim = @PKG@.ShMath.limOf(kd, p, slot);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (spot < 0 || spot >= n || spot >= NSPOT) return res("=The page is up to date now.", "");
  if (use >= lim) return res("-This island's storage is full - Collect first.", "");
  String block = @PKG@.ShIsl.PROD[t];
  double bps = bp(u);
  double f = fortune(u, block);
  String key = k + "|" + slot;
  double hpMax = (double) @PKG@.ShCfg.CK_HP;
  int wt = @PKG@.ShIsl.TIER[t];
  double dm = dmg(at, wt, bps);
  if (!(dm > 0.0)) return res("-Your T" + at + " hatchet is too low a tier for T" + wt + " wood - like in the world, a hatchet chops at most 2 tiers above its own.", "");
  double left = hit(key, spot, dm, hpMax, now, regrowMs(irr));
  CHOPS.incrementAndGet();
  if (left < 0.0) { long ms = (long) (-left - 1.0); return res("=That tree is growing back - " + ((ms + 999L) / 1000L) + " s.", ""); }
  if (left > 0.0) return res("", @PKG@.ShCfg.dec(hpMax - left) + " / " + @PKG@.ShCfg.dec(hpMax));
  long baseN; long total; long got;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t) { unfell(key, spot, hpMax); return res("-That island changed meanwhile - the page is up to date now.", ""); }
    baseN = logsAt(nsize(p, kd, slot));
    long ex = 0L;
    for (long i = 0L; i < baseN && i < 100000L; i++) ex += (long) extras(f, Math.random());
    total = baseN + ex;
    @PKG@.ShMath.settle(kd, p, slot, now);
    long room = @PKG@.ShMath.limOf(kd, p, slot) - @PKG@.ShMath.usedOf(kd, p, slot);
    if (room <= 0L) { unfell(key, spot, hpMax); return res("-This island's storage is full - Collect first.", ""); }
    got = total > room ? room : total;
    String dk = @PKG@.ShMath.ik(kd, slot, "drops");
    String old = p.getProperty(dk);
    java.util.LinkedHashMap m = @PKG@.ShMath.held(kd, p, slot);
    Object o = m.get(block);
    m.put(block, Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + got));
    @PKG@.ShMath.heldSet(kd, p, slot, m);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      if (old == null) p.remove(dk); else p.setProperty(dk, old);
      unfell(key, spot, hpMax);
      @PKG@.ShCfg.warnOnce("clksave", "a felled tree's logs could not be saved (nothing added, the tree stands again; logged once): " + e);
      return res("-The shard file could not be saved - nothing was added.", "");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  FELLS.incrementAndGet();
  LOGS.addAndGet(got);
  long paid = got < baseN ? got : baseN;
  String skill = @PKG@.ShKind.SKILL[kd];
  long xp = accXp(String.valueOf(u) + "|" + @PKG@.ShCfg.pkey(u), (double) paid * (double) @PKG@.ShCfg.xpOf(kd) * (double) @PKG@.ShCfg.CK_XP_PCT / 100.0);
  String xt = "";
  if (xp > 0L) { long xl = @PKG@.ShCore.owedXp(u, skill, xp); xt = xl > 0L ? " (" + @PKG@.ShCfg.num(xl) + " " + skill + " XP waits)" : " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP"; }
  String nm = @PKG@.ShTotem.pretty(block);
  String fit = got < total ? " - the island's storage is full (" + @PKG@.ShCfg.num(total - got) + " did not fit)" : "";
  String r = "+Felled a " + @PKG@.ShIsl.tname(t) + " tree: +" + @PKG@.ShCfg.num(got) + " " + nm + xt + fit + ".";
  @PKG@.ShSnd.ok(u, r, 0);
  return res(r, "+" + @PKG@.ShCfg.num(got) + " " + nm);
}""")
# TREE SIZE: coins = click.treeSizeHours[level] hours of the coin curve at the island's tier + click.treeSizeEnch[level] of the island's Enchanted log
M(ckc, r"""
public static long nodeCoins(int lv, double cv) {
  double[] h = @PKG@.ShCfg.CK_NS_H;
  int i = lv - 1;
  return i < 0 || i >= h.length ? 0L : @PKG@.ShIsl.coins(h[i], cv);
}""")
M(ckc, r"""
public static Object[] nodeMats(int kd, int t, int lv) {
  int[] q = @PKG@.ShCfg.CK_NS_Q;
  int i = lv - 1;
  long n = i < 0 || i >= q.length ? 0L : (long) q[i];
  return @PKG@.ShIsl.mats(kd, t, "ench:" + n, 0, 1L);
}""")
M(ckc, r"""
public static String buyNode(java.util.UUID u, String k, int kd, int slot, int seen, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON || !@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = @PKG@.ShCore.gateOwn(u, k, kd, p);
  if (no != null) return no;
  int t0; int lv; long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    lv = nsize(p, kd, slot);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (seen >= 0 && seen != lv) return "=The page is up to date now - click Upgrade again.";
  int mx = @PKG@.ShCfg.CK_NS_MAX;
  if (lv >= mx) return "=Tree size is at its highest level.";
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));   // the bridge outside the lock
  int nl = lv + 1;
  String r = @PKG@.ShCore.purchaseM(u, k, kd, p, cs, nodeMats(kd, t0, nl), nodeCoins(nl, cv), new String[] { @PKG@.ShMath.ik(kd, slot, "nsize") },
                                    new String[] { String.valueOf(nl) }, "nsize", @PKG@.ShKind.KEYS[kd] + " nsize slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " " + lv + " -> " + nl, ver);
  if (r != null) return r;
  String ok = "+Tree size " + nl + "/" + mx + " on the " + @PKG@.ShIsl.tname(t0) + " island: " + logsAt(nl) + " logs a felled tree.";
  @PKG@.ShSnd.ok(u, ok, 2);
  return ok;
}""")

# ---- THE ART (our own drawings; CLK_ART_SRC above): drawn now, shipped as Common/UI/Custom/SkyyShards/Map/Clk<Name>@2x.png, registered map textures
CLK_ART = {}
exec(compile(CLK_ART_SRC, "clkart", "exec"), CLK_ART)
CK_ISL = {1: (520, 300), 2: (700, 400), 3: (880, 500)}      # the island pictures (UI px, drawn 1:1): Small / Medium / Large
CK_TIERS = sorted(_TT48.LOGS)
assert CK_TIERS == list(range(1, 16)) and [_t["tier"] for _t in LAD[CK_FK]] == CK_TIERS
_ck_t0 = _time423.time()
_ck_pics = CLK_ART["ART"](CK_TIERS, CK_ISL)
CK_TEX = {}
for _n, _pic in sorted(_ck_pics.items()):
    assert re.fullmatch(r"[A-Za-z0-9]+", _n), _n
    CK_TEX[_n] = MDIR + "Clk" + _n + ".png"
    SUI.register_map_textures([CK_TEX[_n]])
    MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"] = _pic.png()
print("0.4.23 clicker art: %d pictures drawn in %.1f s (%d KB)" % (len(_ck_pics), _time423.time() - _ck_t0,
      sum(len(MAP_ASSETS[MJAR + MDIR + "Clk" + _n + "@2x.png"]) for _n in _ck_pics) // 1024))
del _ck_pics

# ---- THE SCENE LAYOUT (build time): the island picture of each size in the 1000 x 600 scene, its trees on the island's REAL tree spots (TREE48: the
# spots Tree Amount fills in order), drawn back to front; the totems on the centre pads, the weather totem, the decorations on the rim
CKP = "SkyyShK"
CK_SW, CK_SH = 1000, 600
CK_TW = {1: 100, 2: 80, 3: 62}           # a tree's width (its picture is 110 x 140)
CK_LAY = {}
for _s in (1, 2, 3):
    _W, _H = CK_ISL[_s]
    _L, _T = (CK_SW - _W) // 2, CK_SH - _H - 4
    _cx, _cy = _L + _W / 2.0, _T + _H * 0.34
    _rx, _ry = _W * 0.47, _W * 0.47 * 0.36
    _h = HALF[_s - 1]
    _bx, _by = _rx * 0.88 / _h, _ry * 0.88 / _h
    # the real spots (4 blocks apart) as a forest: every other row half a step over, a little jitter (fixed), kept inside the grass; back trees smaller
    def _jit(dx, dz, k):
        return (((dx * 73856093) ^ (dz * 19349663) ^ (k * 83492791)) & 0xffff) / 65535.0 - 0.5
    _pos = []
    for _dx, _dz in TREE48[_s - 1]:
        _x = _cx + (_dx + (2 if (_dz // 4) % 2 else 0) + _jit(_dx, _dz, 1) * 1.2) * _bx
        _y = _cy + (_dz + _jit(_dx, _dz, 2) * 0.8) * _by
        _room = 0.82 - ((_y - _cy) / _ry) ** 2
        _xm = _rx * math.sqrt(max(0.05, _room))
        _x = min(max(_x, _cx - _xm), _cx + _xm)
        _pos.append((int(round(_x)), int(round(_y))))
    _wid = [int(round(CK_TW[_s] * (0.8 + 0.2 * (_y - (_cy - _ry)) / (2 * _ry)))) for _x, _y in _pos]
    _ord = sorted(range(len(_pos)), key=lambda _i: (_pos[_i][1], _pos[_i][0]))
    _tot = [(int(round(_cx + math.cos(math.radians(_a)) * 1.55 * _bx)), int(round(_cy + math.sin(math.radians(_a)) * 1.55 * _by))) for _a in (205, 335, 90, 270, 150)]
    _wx = (int(round(_cx + 2.4 * _bx)), int(round(_cy - 2.6 * _by)))

    def _rim(a, r):
        return (int(round(_cx + math.cos(math.radians(a)) * _rx * r)), int(round(_cy + math.sin(math.radians(a)) * _ry * r)))
    _deco = [("DecoFlowers", 48, 32, _rim(118, 0.86)), ("DecoMushrooms", 40, 32, _rim(58, 0.88)), ("DecoLamp", 22, 52, _rim(164, 0.80)),
             ("DecoFence", 80, 25, _rim(92, 0.93)), ("DecoPond", 84, 42, _rim(-32, 0.56))]
    CK_LAY[_s] = dict(L=_L, T=_T, W=_W, H=_H, cx=_cx, cy=int(round(_cy)), pos=_pos, wid=_wid, ord=_ord, tot=_tot, wx=_wx, deco=_deco)
    assert all(0 <= _x < CK_SW and 0 <= _y < CK_SH for _x, _y in _pos), _s
CK_PAGE_STATIC = ["public static final int[] CKTW = new int[] { %d, %d, %d };" % (CK_TW[1], CK_TW[2], CK_TW[3]),
                  "public static final int[] CKCY = new int[] { %d, %d, %d };" % (CK_LAY[1]["cy"], CK_LAY[2]["cy"], CK_LAY[3]["cy"]),
                  "public static final String[] CK_TREE = new String[] { %s };" % ", ".join(jlit(CK_TEX["Tree%d" % _t]) for _t in CK_TIERS),
                  "public static final String[] CK_STUMP = new String[] { %s };" % ", ".join(jlit(CK_TEX["Stump%d" % _t]) for _t in CK_TIERS)]
for _s in (1, 2, 3):
    CK_PAGE_STATIC += ["public static final int[] CKX%d = new int[] { %s };" % (_s, ", ".join(str(_p[0]) for _p in CK_LAY[_s]["pos"])),
                       "public static final int[] CKY%d = new int[] { %s };" % (_s, ", ".join(str(_p[1]) for _p in CK_LAY[_s]["pos"])),
                       "public static final int[] CKO%d = new int[] { %s };" % (_s, ", ".join(str(_i) for _i in CK_LAY[_s]["ord"])),
                       "public static final int[] CKW%d = new int[] { %s };" % (_s, ", ".join(str(_w) for _w in CK_LAY[_s]["wid"]))]
CK_RQN = []
for _n in G422_RNAMES:
    _g = "Quality" + _n if ("Quality" + _n) in SUI.GLASS_EL else "Rarity" + _n
    assert _g in SUI.GLASS_EL, _g
    CK_RQN.append(_g)
CK_PAGE_STATIC.append("public static final String[] CK_RQN = new String[] { %s };" % ", ".join(jlit(_g) for _g in CK_RQN))

# ---- THE PAGE MARKUP (Skyglass; ids SkyyShK...; inline only). Static parts through the kit (SUI.Appends -> Java), the trees / cells / pop drawn at run time from
# TEMPLATES that are checked here with sample values (CK_TPL: @TOKEN@ -> a Java expression)
G_ = SUI
CK_W, CK_H, CK_PAD = 1560, 940, 14
CK_IW = CK_W - 2 * CK_PAD
CK_HOV = SUI.COLOR["hover"]
CK_SAMPLES = []          # the run-time markups with sample values (checked + counted)


def _ck_tpl(markup, toks, sample):
    """a run-time markup template -> a Java string expression; the sample (tokens -> sample values) is kit-checked"""
    s_ = markup
    for k_, v_ in sample.items():
        s_ = s_.replace(k_, v_)
    assert "@" not in s_, s_
    SUI.check_markup(s_, prefix=CKP)
    CK_SAMPLES.append(s_)
    parts = re.split(r"(@[A-Z]+@)", markup)
    out = []
    for p_ in parts:
        if not p_:
            continue
        out.append(toks[p_] if p_ in toks else SUI.java_lit(p_))
    return " + ".join(out)


def _ck_glab(ident, size, col, w, h, bold=False, halign=None, text="", anchor=None):
    return G_.glass_label(ident, text, size, col, bold=bold, w=w, h=h, halign=halign, anchor=anchor)


def _ck_wrap(ident, size, col, w, h, lines=2, anchor=None):
    return "Label #%s { %sStyle: %s; }" % (SUI.check_id(ident), SUI._anchor(w, h, SUI._merge(None, anchor)), SUI.text_style(size, G_.glass_col(col), wrap=True))


def _ck_jset(ident, expr):
    return '  b.set("#%s.Text", "" + (%s));' % (ident, expr)


def _ck_bind(ident, act_expr):
    return '  ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", %s));' % (ident, act_expr)


CKA = {}                 # segment name -> Appends


def _ck_seg(name):
    a_ = SUI.Appends()
    CKA[name] = a_
    return a_


# the frame (always): window, top row (title, island chip, info), the island map button (2 variants), Shard menu, X, separator, body
a_ = _ck_seg("frame")
a_.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (CKP, CK_W, CK_H)))
a_.append(("#" + CKP, G_.glass_group(CKP + "Win", CK_W, CK_H, role="frame", layout="Top", pad=CK_PAD)))
CK_WIN = "#" + CKP + "Win"
a_.append((CK_WIN, G_.glass_group(CKP + "Top", CK_IW, 44, layout="Left")))
CK_TOP = "#" + CKP + "Top"
a_.append((CK_TOP, _ck_glab(CKP + "Title", 22, "title", 250, 44, bold=True, text="FORAGING SHARD")))
a_.append((CK_TOP, G_.glass_group(CKP + "Chip", 360, 36, role="inset", layout="Left", anchor={"top": 4, "right": 12})))
a_.append(("#" + CKP + "Chip", _ck_glab(CKP + "ChipT", 16, "accentHi", 360, 36, bold=True, halign="Center")))
CK_INFO_W = CK_IW - 250 - 372 - 158 - 178 - 40 - 6
a_.append((CK_TOP, _ck_glab(CKP + "Info", 14, "dim", CK_INFO_W, 44)))
a_ = _ck_seg("mapb0")
a_.append((CK_TOP, G_.glass_button(CKP + "MapB", "Islands", "secondary", w=150, h=38, anchor={"top": 3, "right": 8})))
a_ = _ck_seg("mapb1")
a_.append((CK_TOP, G_.glass_button(CKP + "MapB", "Island view", "secondary", w=150, h=38, anchor={"top": 3, "right": 8})))
a_ = _ck_seg("frame2")
a_.append((CK_TOP, G_.glass_button(CKP + "MenuB", "Shard menu", "secondary", w=170, h=38, anchor={"top": 3, "right": 8})))
a_.append((CK_TOP, G_.glass_button(CKP + "Close", "X", "close", w=40, h=40, size=16, anchor={"top": 2})))
a_.append((CK_WIN, 'Group #%sSep { Anchor: (Width: %d, Height: 2, Top: 6, Bottom: 6); Background: "%s"; }' % (CKP, CK_IW, G_.glass_path("Separator"))))
CK_BODY_H = 820
a_.append((CK_WIN, G_.glass_group(CKP + "Body", CK_IW, CK_BODY_H, layout="Left")))
CK_BODY = "#" + CKP + "Body"

# ---- mode 0: the scene + the store strip (left), the six upgrades (right)
a_ = _ck_seg("left")
a_.append((CK_BODY, G_.glass_group(CKP + "Left", CK_SW, CK_BODY_H, layout="Top")))
CK_LEFT = "#" + CKP + "Left"
a_.append((CK_LEFT, 'Group #%sScn { Anchor: (Width: %d, Height: %d); Background: "%s"; }' % (CKP, CK_SW, CK_SH, CK_TEX["Sky"])))
CK_SCN = "#" + CKP + "Scn"
a_.append((CK_SCN, SUI.map_pic(CKP + "Cl1", 40, 26, 220, 90, CK_TEX["CloudA"])))
a_.append((CK_SCN, SUI.map_pic(CKP + "Cl2", 730, 64, 160, 70, CK_TEX["CloudB"])))


def _ck_bot(name, w, h, xy):
    """a picture standing on (x, y): its bottom centre"""
    return (xy[0] - w // 2, xy[1] - h + max(2, h // 14))


for _s in (1, 2, 3):
    lay = CK_LAY[_s]
    a_ = _ck_seg("isl%d" % _s)
    a_.append((CK_SCN, SUI.map_pic(CKP + "Isl", lay["L"], lay["T"], lay["W"], lay["H"], CK_TEX["Isl%d" % _s])))
    for _j, (_dn, _dw, _dh, _dxy) in enumerate(lay["deco"]):
        a_ = _ck_seg("deco%d_%d" % (_s, _j))
        _l, _t = _ck_bot(_dn, _dw, _dh, _dxy)
        a_.append((CK_SCN, SUI.map_pic(CKP + "D%d" % _j, _l, _t, _dw, _dh, CK_TEX[_dn])))
    for _j in range(5):
        a_ = _ck_seg("tot%d_%d" % (_s, _j))
        _l, _t = _ck_bot("Totem", 40, 73, lay["tot"][_j])
        a_.append((CK_SCN, SUI.map_pic(CKP + "To%d" % _j, _l, _t, 40, 73, CK_TEX["Totem"])))
        a_.append((CK_SCN, SUI.map_pic(CKP + "Sp%d" % _j, _l + 26, _t + 6, 34, 36, CK_TEX["Spirit"])))
    a_ = _ck_seg("wx%d" % _s)
    _l, _t = _ck_bot("Weather", 34, 73, lay["wx"])
    a_.append((CK_SCN, SUI.map_pic(CKP + "Wx", _l, _t, 34, 73, CK_TEX["Weather"])))
CK_BACK_DECO = [_j for _j, _d in enumerate(CK_LAY[1]["deco"]) if _d[0] == "DecoPond"]   # behind the trees (the far side)
a_ = _ck_seg("cap")
a_.append((CK_SCN, G_.glass_group(CKP + "CapG", CK_SW - 24, 34, role="inset", layout="Left", anchor={"left": 12, "top": CK_SH - 44})))
a_.append(("#" + CKP + "CapG", _ck_glab(CKP + "Cap", 15, "text", CK_SW - 40, 34, anchor={"left": 8})))
# the store strip
a_.append((CK_LEFT, G_.glass_group(CKP + "Sto", CK_SW, 210, role="panel", layout="Top", pad=12, anchor={"top": 10})))
CK_STO = "#" + CKP + "Sto"
a_.append((CK_STO, G_.glass_group(CKP + "StoH", CK_SW - 24, 28, layout="Left")))
a_.append(("#" + CKP + "StoH", _ck_glab(CKP + "StoT", 16, "gold", 200, 28, bold=True, text="SHARD STORAGE")))
a_.append(("#" + CKP + "StoH", _ck_glab(CKP + "StoHint", 14, "dim", CK_SW - 24 - 200, 28)))
a_.append((CK_STO, G_.glass_group(CKP + "StoB", CK_SW - 24, 148, layout="Left", anchor={"top": 8})))
a_.append(("#" + CKP + "StoB", G_.glass_group(CKP + "Cells", 652, 148, layout="Left")))
a_.append(("#" + CKP + "StoB", G_.glass_group(CKP + "Stats", CK_SW - 24 - 652, 148, layout="Top")))
CK_STATS = "#" + CKP + "Stats"
for _i in range(3):
    a_.append((CK_STATS, _ck_glab(CKP + "St%d" % _i, 14, "text", CK_SW - 24 - 652, 28)))
a_.append((CK_STATS, G_.glass_group(CKP + "StoBt", CK_SW - 24 - 652, 40, layout="Left", anchor={"top": 10})))
a_ = _ck_seg("colall")
a_.append(("#" + CKP + "StoBt", G_.glass_button(CKP + "CAll", "Collect all", "primary", w=160, h=38, anchor={"right": 8})))
a_ = _ck_seg("stotab")
a_.append(("#" + CKP + "StoBt", G_.glass_button(CKP + "STab", "Storage tab", "secondary", w=150, h=38)))
# the six upgrades
CK_UPW = CK_IW - CK_SW - 12
CK_UP_NAMES = ["Tree size", "Tree count", "Spirit totems", "Weather totem", "Island size", "Decorations"]
CK_UP_ICON = ["UpNsize", "UpNcount", "UpSpirit", "UpWeather", "UpIsize", "UpDeco"]
CK_UP_BTN = ["Upgrade", "Upgrade", "Totems", "Upgrade", "Upgrade", "Upgrade"]
a_ = _ck_seg("up")
a_.append((CK_BODY, G_.glass_group(CKP + "Up", CK_UPW, CK_BODY_H, role="panel", layout="Top", pad=12, anchor={"left": 12})))
CK_UP = "#" + CKP + "Up"
CK_UIW = CK_UPW - 24
a_.append((CK_UP, G_.glass_group(CKP + "UpH", CK_UIW, 32, layout="Left")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpT", 18, "gold", 150, 32, bold=True, text="UPGRADES")))
a_.append(("#" + CKP + "UpH", _ck_glab(CKP + "UpCap", 13, "dim", CK_UIW - 150, 32, halign="End")))
CK_ROW_H, CK_TXT_W = 120, CK_UIW - 12 - 64 - 8
for _r in range(6):
    R_ = CKP + "U%d" % _r
    a_.append((CK_UP, G_.glass_group(R_, CK_UIW, CK_ROW_H, role="inset", layout="Left", pad=6, anchor={"top": 5})))
    a_.append(("#" + R_, "Group #%sI { Anchor: (Width: 64, Height: %d); }" % (R_, CK_ROW_H - 12)))
    a_.append(("#" + R_ + "I", SUI.map_pic(R_ + "P", 4, 6, 56, 56, CK_TEX[CK_UP_ICON[_r]])))
    a_.append(("#" + R_, G_.glass_group(R_ + "T", CK_TXT_W, CK_ROW_H - 12, layout="Top", anchor={"left": 8})))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "N", CK_TXT_W, 26, layout="Left")))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "Nm", 17, "title", 250, 26, bold=True, text=CK_UP_NAMES[_r])))
    a_.append(("#" + R_ + "N", _ck_glab(R_ + "L", 15, "xp", CK_TXT_W - 250, 26, bold=True, halign="End")))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "E", 15, "text", CK_TXT_W, 24)))
    a_.append(("#" + R_ + "T", _ck_glab(R_ + "C", 14, "goldHi", CK_TXT_W, 22)))
    a_.append(("#" + R_ + "T", G_.glass_group(R_ + "B", CK_TXT_W, 34, layout="Left")))
    a_.append(("#" + R_ + "B", "Group { Anchor: (Width: %d); }" % (CK_TXT_W - 150)))
    b_ = _ck_seg("upon%d" % _r)
    b_.append(("#" + R_ + "B", G_.glass_button(R_ + "X", CK_UP_BTN[_r], "secondary", w=150, h=32)))
    b_ = _ck_seg("upoff%d" % _r)
    b_.append(("#" + R_ + "B", G_.glass_button(R_ + "X", CK_UP_BTN[_r], "secondary", w=150, h=32, disabled=True)))
assert 32 + 6 * (CK_ROW_H + 5) <= CK_BODY_H - 24, "the six rows fit the panel"

# ---- mode 1: the island map - five zone clusters of three woods (tools/tier_tags.py LOGS, 3 tiers a zone)
CK_ZW = (CK_IW - 4 * 13) // 5
a_ = _ck_seg("map")
a_.append((CK_BODY, G_.glass_group(CKP + "Map", CK_IW, CK_BODY_H, layout="Left")))
CK_CARD_H, CK_CW = 240, CK_ZW - 20
for _z in range(5):
    Z_ = CKP + "Z%d" % _z
    a_.append(("#" + CKP + "Map", G_.glass_group(Z_, CK_ZW, CK_BODY_H, role="panel", layout="Top", pad=10, anchor={"right": 13} if _z < 4 else None)))
    a_.append(("#" + Z_, _ck_glab(Z_ + "N", 18, "gold", CK_CW, 30, bold=True, text="ZONE %d" % (_z + 1))))
    a_.append(("#" + Z_, _ck_glab(Z_ + "S", 14, "dim", CK_CW, 24)))
    for _q in range(3):
        _i = 3 * _z + _q
        M_ = CKP + "M%d" % _i
        a_.append(("#" + Z_, G_.glass_group(M_, CK_CW, CK_CARD_H, role="inset", layout="Top", pad=6, anchor={"top": 6})))
        a_.append(("#" + M_, "Group #%sG { Anchor: (Width: %d, Height: 140); }" % (M_, CK_CW - 12)))
        a_.append(("#" + M_ + "G", SUI.map_pic(M_ + "P", (CK_CW - 12 - 210) // 2, 0, 210, 140, CK_TEX["Map%d" % CK_TIERS[_i]])))
        b_ = _ck_seg("mlock%d" % _i)
        b_.append(("#" + M_ + "G", SUI.map_pic(M_ + "Lk", (CK_CW - 12 - 40) // 2, 40, 40, 48, CK_TEX["Lock"])))
        a_ = CKA["map"]
        a_.append(("#" + M_, _ck_glab(M_ + "N", 16, "title", CK_CW - 12, 22, bold=True)))
        a_.append(("#" + M_, _ck_wrap(M_ + "S", 13, "text", CK_CW - 12, 36)))
        a_.append(("#" + M_, G_.glass_group(M_ + "B", CK_CW - 12, 30, layout="Left")))
        b_ = _ck_seg("mopen%d" % _i)
        b_.append(("#" + M_ + "B", G_.glass_button(M_ + "X", "Open", "secondary", w=CK_CW - 12, h=30)))
        b_ = _ck_seg("mbuy%d" % _i)
        b_.append(("#" + M_ + "B", G_.glass_button(M_ + "X", "Buy", "secondary", w=CK_CW - 12, h=30)))
        a_ = CKA["map"]
assert 30 + 24 + 3 * (CK_CARD_H + 6) <= CK_BODY_H - 20, "the three cards fit a zone panel"
a_ = _ck_seg("foot")
a_.append((CK_WIN, "Group #%sStH { Anchor: (Width: %d, Height: 30, Top: 4); }" % (CKP, CK_IW)))
for _vi, _vc in enumerate(("green", "red", "accentHi")):
    a_.append(("#" + CKP + "StH", _ck_glab(CKP + "Stat%d" % _vi, 15, _vc, CK_IW, 30, bold=True, halign="Center", anchor={"left": 0, "top": 0})))

# the run-time templates (checked with samples)
_tex0 = CK_TEX["Tree1"]
CK_J_TREE = _ck_tpl('Group #SkyyShKT@I@ { Anchor: (Left: @X@, Top: @Y@, Width: @W@, Height: @H@); Background: "@TEX@"; }',
                    {"@I@": "i", "@X@": "(ox[i] - tw / 2)", "@Y@": "(oy[i] - th + th / 14)", "@W@": "tw", "@H@": "th", "@TEX@": "tex"},
                    {"@I@": "0", "@X@": "10", "@Y@": "10", "@W@": "80", "@H@": "101", "@TEX@": _tex0})
CK_J_HIT = _ck_tpl("Button #SkyyShKH@I@ { Anchor: (Left: @X@, Top: @Y@, Width: @W@, Height: @H@); Style: ButtonStyle(Hovered: (Background: %s)); }" % CK_HOV,
                   {"@I@": "i", "@X@": "(ox[i] - tw * 2 / 5)", "@Y@": "(oy[i] - th * 9 / 10)", "@W@": "(tw * 4 / 5)", "@H@": "(th * 17 / 20)"},
                   {"@I@": "0", "@X@": "10", "@Y@": "10", "@W@": "64", "@H@": "86"})
CK_POP_ST = G_.glass_text_style(18, "goldHi", bold=True, halign="Center")
CK_J_POP = _ck_tpl("Label #SkyyShKPop { Anchor: (Left: @X@, Top: @Y@, Width: 180, Height: 30); Style: %s; }" % CK_POP_ST,
                   {"@X@": "(ox[pi] - 90)", "@Y@": "(oy[pi] - th - 26)"}, {"@X@": "10", "@Y@": "10"})
CK_J_CELL = _ck_tpl('Group #SkyyShKC@I@ { Anchor: (Width: 74, Height: 74, Right: 6); Background: "%s"; }' % G_.glass_path("Slot"),
                    {"@I@": "c"}, {"@I@": "0"})
CK_J_CICON = _ck_tpl('ItemIcon #SkyyShKC@I@I { Anchor: (Left: 7, Top: 4, Width: 60, Height: 60); ItemId: "@ID@"; }', {"@I@": "c", "@ID@": "this.sgIc[c]"},
                     {"@I@": "0", "@ID@": "Wood_Oak_Trunk"})
CK_J_CFR = _ck_tpl('Group #SkyyShKC@I@F { Anchor: (Left: 0, Top: 0, Width: 74, Height: 74); Background: (TexturePath: "SkyyGlass/@RQ@.png", Border: %d); }'   # ui-data: the Skyglass rarity frame (SUI.GLASS_EL)
                  
                   % G_.GLASS_EL[CK_RQN[0]][2], {"@I@": "c", "@RQ@": "fr"}, {"@I@": "0", "@RQ@": CK_RQN[0]})   # ui-data: the Skyglass rarity frames (SUI.GLASS_EL)
assert all(G_.GLASS_EL[_g][2] == G_.GLASS_EL[CK_RQN[0]][2] for _g in CK_RQN)
CK_J_CQTY = _ck_tpl("Label #SkyyShKC@I@Q { Anchor: (Left: 2, Top: 50, Width: 68, Height: 22); Style: %s; }" % G_.glass_text_style(14, "title", bold=True, halign="End"),
                    {"@I@": "c"}, {"@I@": "0"})
CK_J_CBTN = _ck_tpl("Button #SkyyShKC@I@B { Anchor: (Left: 0, Top: 0, Width: 74, Height: 74); Style: ButtonStyle(Hovered: (Background: %s)); }" % CK_HOV,
                    {"@I@": "c"}, {"@I@": "0"})


def _ckj(name):
    return CKA[name].java("b")


def _tree_pass(back):
    """the trees of one half (back = behind the centre pads), back to front; a regrowing tree = its stump"""
    return "\n".join([
        "  {",
        "    int sz = this.ckSz < 1 ? 1 : (this.ckSz > 3 ? 3 : this.ckSz);",
        "    int[] ox = sz >= 3 ? CKX3 : (sz == 2 ? CKX2 : CKX1); int[] oy = sz >= 3 ? CKY3 : (sz == 2 ? CKY2 : CKY1); int[] od = sz >= 3 ? CKO3 : (sz == 2 ? CKO2 : CKO1);",
        "    int[] ow = sz >= 3 ? CKW3 : (sz == 2 ? CKW2 : CKW1); int cyy = CKCY[sz - 1];",
        "    for (int q = 0; q < od.length; q++) {",
        "      int i = od[q];",
        "      int tw = i < ow.length ? ow[i] : CKTW[sz - 1]; int th = tw * 140 / 110;",
        "      if (i >= this.ckTn || i >= ox.length || (oy[i] <= cyy) != %s) continue;" % ("true" if back else "false"),
        "      String tex = this.ckGrow != null && i < this.ckGrow.length && this.ckGrow[i] ? this.ckStump : this.ckTree;",
        '      b.appendInline("%s", %s);' % (CK_SCN, CK_J_TREE),
        "    }",
        "  }"])


_ck_j = [_ckj("frame"), "  if (this.ckMode == 1) {", _ckj("mapb1"), "  } else {", _ckj("mapb0"), "  }", _ckj("frame2"),
         _ck_jset(CKP + "ChipT", "this.ckChip"), _ck_jset(CKP + "Info", "this.ckInfo"),
         _ck_bind(CKP + "MapB", '(this.ckMode == 1 ? "kisl" : "kmap")'), _ck_bind(CKP + "MenuB", '"kback"'), _ck_bind(CKP + "Close", '"close"'),
         "  if (this.ckMode == 1) {", _ckj("map")]
for _i in range(15):
    _ck_j += ["  if (this.ckMLock[%d]) {" % _i, _ckj("mlock%d" % _i), "  }",
              "  if (this.ckMB[%d] == 1) {" % _i, _ckj("mopen%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"km%d"' % _i),
              "  } else if (this.ckMB[%d] == 2) {" % _i, _ckj("mbuy%d" % _i), _ck_bind(CKP + "M%dX" % _i, '"kb%d"' % _i), "  }",
              _ck_jset(CKP + "M%dN" % _i, "this.ckMN[%d]" % _i), _ck_jset(CKP + "M%dS" % _i, "this.ckMS[%d]" % _i)]
for _z in range(5):
    _ck_j.append(_ck_jset(CKP + "Z%dS" % _z, "this.ckZS[%d]" % _z))
_ck_j += ["  } else {", _ckj("left")]
for _s in (1, 2, 3):
    _ck_j += ["  if (this.ckSz == %d) {" % _s, _ckj("isl%d" % _s)]
    for _j in CK_BACK_DECO:
        _ck_j += ["    if (this.ckDeco > %d) {" % _j, _ckj("deco%d_%d" % (_s, _j)), "    }"]
    _ck_j += ["  }"]
_ck_j += [_tree_pass(True)]
for _s in (1, 2, 3):
    _ck_j += ["  if (this.ckSz == %d) {" % _s]
    for _j in range(5):
        _ck_j += ["    if (this.ckSpN > %d) {" % _j, _ckj("tot%d_%d" % (_s, _j)), "    }"]
    _ck_j += ["    if (this.ckWx > 0) {", _ckj("wx%d" % _s), "    }", "  }"]
_ck_j += [_tree_pass(False)]
for _s in (1, 2, 3):
    _ck_j += ["  if (this.ckSz == %d) {" % _s]
    for _j in range(5):
        if _j not in CK_BACK_DECO:
            _ck_j += ["    if (this.ckDeco > %d) {" % _j, _ckj("deco%d_%d" % (_s, _j)), "    }"]
    _ck_j += ["  }"]
_ck_j += [
    "  if (this.ckSz >= 1 && this.manage && @PKG@.ShCfg.CK_ON) {   // the click squares over the trees (on top of every picture)",
    "    int sz = this.ckSz > 3 ? 3 : this.ckSz;",
    "    int[] ox = sz >= 3 ? CKX3 : (sz == 2 ? CKX2 : CKX1); int[] oy = sz >= 3 ? CKY3 : (sz == 2 ? CKY2 : CKY1); int[] od = sz >= 3 ? CKO3 : (sz == 2 ? CKO2 : CKO1);",
    "    int[] ow = sz >= 3 ? CKW3 : (sz == 2 ? CKW2 : CKW1);",
    "    for (int q = 0; q < od.length; q++) {",
    "      int i = od[q];",
    "      if (i >= this.ckTn || i >= ox.length) continue;",
    "      int tw = i < ow.length ? ow[i] : CKTW[sz - 1]; int th = tw * 140 / 110;",
    '      b.appendInline("%s", %s);' % (CK_SCN, CK_J_HIT),
    '      ev.addEventBinding(@BT@.Activating, "#SkyyShKH" + i, @EVD@.of("a", "kt" + i + ":" + this.ckSlot));',
    "    }",
    "    int pi = this.ckPopI;",
    "    if (this.ckPop != null && this.ckPop.length() > 0 && pi >= 0 && pi < this.ckTn && pi < ox.length) {",
    "      int th = (pi < ow.length ? ow[pi] : CKTW[sz - 1]) * 140 / 110;",
    '      b.appendInline("%s", %s);' % (CK_SCN, CK_J_POP),
    '      b.set("#SkyyShKPop.Text", this.ckPop);',
    "    }",
    "  }",
    _ckj("cap"), _ck_jset(CKP + "Cap", "this.ckCap"), _ck_jset(CKP + "StoHint", "this.sgHint")]
_ck_j += [_ck_jset(CKP + "St%d" % _i, "this.ckSto[%d]" % _i) for _i in range(3)]
_ck_j += ["  if (this.manage && this.sgN > 0) {", _ckj("colall"), _ck_bind(CKP + "CAll", '"colall"'), "  }",
          _ckj("stotab"), _ck_bind(CKP + "STab", '"kstore"'),
          "  int nc = this.sgN > 8 ? 8 : this.sgN;",
          "  for (int c = 0; c < nc; c++) {",
          '    b.appendInline("#%sCells", %s);' % (CKP, CK_J_CELL),
          '    b.appendInline("#SkyyShKC" + c, %s);' % CK_J_CICON,
          "    int rr = @PKG@.ShCore.rarOf(this.sgId[c]);",
          "    String fr = rr >= 1 && rr <= CK_RQN.length ? CK_RQN[rr - 1] : null;",
          '    if (fr != null) b.appendInline("#SkyyShKC" + c, %s);' % CK_J_CFR,
          '    b.appendInline("#SkyyShKC" + c, %s);' % CK_J_CQTY,
          '    b.set("#SkyyShKC" + c + "Q.Text", this.sgQty[c]);',
          "    if (this.manage) {",
          '      b.appendInline("#SkyyShKC" + c, %s);' % CK_J_CBTN,
          '      ev.addEventBinding(@BT@.Activating, "#SkyyShKC" + c + "B", @EVD@.of("a", "gc:" + this.sgId[c]));',
          "    }",
          "  }",
          _ckj("up"), _ck_jset(CKP + "UpCap", "this.ckUpCap")]
for _r in range(6):
    R_ = CKP + "U%d" % _r
    _ck_j += [_ck_jset(R_ + "L", "this.ckUpL[%d]" % _r), _ck_jset(R_ + "E", "this.ckUpE[%d]" % _r), _ck_jset(R_ + "C", "this.ckUpC[%d]" % _r),
              "  if (this.ckUpOk[%d]) {" % _r, _ckj("upon%d" % _r), _ck_bind(R_ + "X", '"ku%d:" + this.ckUpSeen[%d]' % (_r, _r)),
              "  } else {", _ckj("upoff%d" % _r), "  }"]
_ck_j += ["  }", _ckj("foot"),
          "  boolean sg = this.stText != null && this.stText.length() > 0 && \"%s\".equals(this.stCol);" % GOOD,
          "  boolean sb = this.stText != null && this.stText.length() > 0 && \"%s\".equals(this.stCol);" % BAD,
          '  b.set("#%sStat0.Text", sg ? this.stText : "");' % CKP,
          '  b.set("#%sStat1.Text", sb ? this.stText : "");' % CKP,
          '  b.set("#%sStat2.Text", (!sg && !sb && this.stText != null) ? this.stText : "");' % CKP]
BUILD_CLICK = "\n".join(_ck_j)

# the checks: every variant (each island size with all its parts; the map with every card variant) = unique ids, parents exist, kit-proven markup,
# Skyglass paths real, the window 1560 x 940 (<= 1600 x 980), ONE Primary, the element budget (the worst variant + the run-time parts)
CK_VARS = []
for _s in (1, 2, 3):
    v_ = SUI.Appends()
    for _n in ["frame", "mapb0", "frame2", "left", "isl%d" % _s] + ["deco%d_%d" % (_s, _j) for _j in range(5)] + ["tot%d_%d" % (_s, _j) for _j in range(5)] + \
            ["wx%d" % _s, "cap", "colall", "stotab", "up"] + ["upon%d" % _r for _r in range(6)] + ["foot"]:
        v_.extend(CKA[_n])
    CK_VARS.append(v_)
v_ = SUI.Appends()
for _n in ["frame", "mapb1", "frame2", "map"] + ["mlock%d" % _i for _i in range(15)] + ["mbuy%d" % _i for _i in range(15)] + ["foot"]:
    v_.extend(CKA[_n])
CK_VARS.append(v_)
for _i, v_ in enumerate(CK_VARS):
    v_.check(CKP)
    _pri = sum(1 for p_, mk_ in v_ if 'TexturePath: "SkyyGlass/Primary.png"' in SUI.render(mk_))   # ui-data: counting the Skyglass Primary buttons
    assert _pri <= 1, "0.4.23 clicker variant %d: %d Primary buttons" % (_i, _pri)
SUI.assert_proven([mk_ for v_ in CK_VARS for p_, mk_ in v_] + CK_SAMPLES, what="SkyyShards 0.4.23 shard clicker page")
CK_GLASS_N = SUI.assert_glass_paths([mk_ for v_ in CK_VARS for p_, mk_ in v_] + CK_SAMPLES)
_ck_el = [sum(SUI._strip_quoted(SUI.render(mk_)).count("{") for p_, mk_ in v_) for v_ in CK_VARS]
CK_ELEMENTS = max(_ck_el[:3]) + CK_NSPOT * 2 + 1 + 8 * 5
assert CK_ELEMENTS < 1000 and _ck_el[3] < 1000, "0.4.23: the clicker page stays well under ~1,600 elements: %s / %s" % (CK_ELEMENTS, _ck_el)
print("0.4.23 clicker page: %d x %d, %d variants checked, elements: island %s + %d run-time = %d at most, map %d; %d Skyglass paths; %d run-time templates"
      % (CK_W, CK_H, len(CK_VARS), _ck_el[:3], CK_NSPOT * 2 + 1 + 40, CK_ELEMENTS, _ck_el[3], CK_GLASS_N, len(CK_SAMPLES)))

'''
# ---------------------------------------------------------------------------------------------------- the page methods (inserted before ShPage.build0)
CK_PAGE_METHODS = r'''# 0.4.23 THE CLICKER (view 5): the hatchet in hand (world thread; the harness sets ShClk.HAND_TEST), a cost line, the fill (bridges before the store lock,
# the island + the map read under it), the build (BUILD_CLICK), the clicks
M(page, r"""
public String handId(@REF@ ref, @ST@ st) {
  if (this.testMode) return @PKG@.ShClk.HAND_TEST;
  try {
    if (ref == null || st == null) return null;
    @PLA@ pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = pl == null ? null : pl.getInventory();
    @IS@ it = inv == null ? null : inv.getItemInHand();
    return it == null || it.isEmpty() ? null : it.getItemId();
  } catch (Throwable t) { return null; }
}""")
M(page, r"""
public static String ckCost(long coins, Object[] mats) {
  String m = mats == null ? "" : @PKG@.ShIsl.matsText(mats);
  String c = coins > 0L ? @PKG@.ShCfg.num(coins) + " coins" : "";
  if (m.length() == 0) return c;
  return c.length() == 0 ? m : c + " + " + m;
}""")
M(page, r"""
public static String ckSize(int sz) {
  return sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small");
}""")
M(page, r"""
public void fillClick(String k, @IC@[] cs, @REF@ ref, @ST@ st) {
  this.kind = @PKG@.ShClk.FK;
  int kd = this.kind;
  this.key = k;
  this.title = "Foraging Shard";
  this.ckUpL = new String[6]; this.ckUpE = new String[6]; this.ckUpC = new String[6]; this.ckUpOk = new boolean[6]; this.ckUpSeen = new int[6];
  for (int i = 0; i < 6; i++) { this.ckUpL[i] = ""; this.ckUpE[i] = ""; this.ckUpC[i] = ""; this.ckUpOk[i] = false; this.ckUpSeen[i] = 0; }
  this.ckMN = new String[15]; this.ckMS = new String[15]; this.ckMB = new int[15]; this.ckMLock = new boolean[15]; this.ckMCur = new boolean[15];
  for (int i = 0; i < 15; i++) { this.ckMN[i] = ""; this.ckMS[i] = ""; this.ckMB[i] = 0; this.ckMLock[i] = false; this.ckMCur[i] = false; }
  this.ckZS = new String[5];
  for (int i = 0; i < 5; i++) this.ckZS[i] = "";
  this.ckSto = new String[3];
  for (int i = 0; i < 3; i++) this.ckSto[i] = "";
  this.ckGrow = new boolean[@PKG@.ShClk.NSPOT];
  this.ckSz = 0; this.ckTn = 0; this.ckSpN = 0; this.ckWx = 0; this.ckDeco = 0; this.ckAmt = 0; this.ckNs = 0; this.ckT = -1; this.ckTi = 0; this.ckNext = -1;
  this.ckTree = CK_TREE[0]; this.ckStump = CK_STUMP[0];
  this.ckChip = "No island yet"; this.ckCap = ""; this.ckUpCap = "";
  if (this.ckPop == null) this.ckPop = "";
  this.ckHand = handId(ref, st);
  this.ckAxe = @PKG@.ShClk.axeTier(this.ckHand);
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));
  this.manage = k != null && @PKG@.ShRole.mayManage(this.me, k);
  this.bagT = 0L;
  this.sgN = 0; this.sgId = new String[0]; this.sgIc = new String[0]; this.sgQty = new String[0]; this.sgBg = new String[0]; this.sgHint = "Nothing is stored here yet.";
  this.ckInfo = this.ckAxe > 0 ? "Chopping with your " + @PKG@.ShTotem.pretty(this.ckHand) + " (T" + this.ckAxe + ") - clicks give " + @PKG@.ShCfg.CK_XP_PCT + " % of world XP"
      : "Hold a hatchet to chop - the clicker uses the hatchet in your hand.";
  if (!@PKG@.ShCfg.CK_ON) this.ckInfo = "The shard clicker is switched off on this server.";
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  if (p == null) { this.ckCap = k == null ? "Only the island owner and co-op members can use this shard." : "This shard's file could not be read."; return; }
  int LN = @PKG@.ShIsl.LADN[kd];
  int L0 = @PKG@.ShIsl.LAD0[kd];
  int lv = @PKG@.ShIsl.level(this.me, kd);   // the bridges before the store lock
  this.ckLv = lv;
  double[] tcv = new double[LN];
  for (int i = 0; i < LN; i++) tcv[i] = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[L0 + i]));
  long now = @PKG@.ShCore.now();
  int[] own = new int[LN];
  int[] osz = new int[LN];
  Object[] gd = null;
  int t = -1; int sz = 0; int amt = 0; int deco = 0; int irr = 0; int ns = 0; int tot = 0; double rate = 0.0; long sto = 0L; long cap = 0L; String offw = "";
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);
    for (int i = 0; i < LN; i++) { own[i] = @PKG@.ShIsl.slotOf(kd, p, L0 + i); osz[i] = own[i] >= 0 ? @PKG@.ShMath.size(kd, p, own[i]) : 0; }
    if (this.ckSlot < 0 || this.ckSlot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(kd, p, this.ckSlot)) {
      this.ckSlot = -1;
      for (int i = 0; i < LN && this.ckSlot < 0; i++) if (own[i] >= 0) this.ckSlot = own[i];
    }
    if (this.ckSlot >= 0) {
      int s = this.ckSlot;
      t = @PKG@.ShIsl.ty(kd, p, s); sz = @PKG@.ShMath.size(kd, p, s);
      amt = @PKG@.ShIsl.sub(p, kd, s, 0); deco = @PKG@.ShIsl.sub(p, kd, s, 1); irr = @PKG@.ShIsl.sub(p, kd, s, 2);
      ns = @PKG@.ShClk.nsize(p, kd, s); tot = @PKG@.ShMath.totems(kd, p, s); rate = @PKG@.ShMath.rate(kd, p, s, now);
      sto = @PKG@.ShMath.usedOf(kd, p, s); cap = @PKG@.ShMath.limOf(kd, p, s);
      offw = @PKG@.ShIsl.offWords(kd, p, @PKG@.ShIsl.offLv(kd, p));
    }
    gd = @PKG@.ShCore.gridOf(kd, p);
    this.ckNext = @PKG@.ShIsl.nextTier(kd, p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  gridFill(gd, kd);   // after the lock
  if (t >= 0) {
    this.ckT = t; this.ckTi = t - L0; this.ckSz = sz; this.ckAmt = amt; this.ckDeco = deco; this.ckWx = irr; this.ckNs = ns;
    this.ckSpN = tot > 5 ? 5 : tot;
    this.ckTn = @PKG@.ShIsl.treeN(sz, amt);
    if (this.ckTn > @PKG@.ShClk.NSPOT) this.ckTn = @PKG@.ShClk.NSPOT;
    int tt = @PKG@.ShIsl.TIER[t];
    int ti = tt < 1 ? 0 : (tt > CK_TREE.length ? CK_TREE.length - 1 : tt - 1);
    this.ckTree = CK_TREE[ti]; this.ckStump = CK_STUMP[ti];
    this.ckChip = @PKG@.ShIsl.tname(t) + " Island - " + ckSize(sz);
    String key2 = k + "|" + this.ckSlot;
    for (int i = 0; i < this.ckTn; i++) this.ckGrow[i] = @PKG@.ShClk.readyAt(key2, i) > now;
    String nm = @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[t]);
    this.ckSto[0] = "Spirits: " + tot + (tot == 1 ? " totem works" : " totems work") + " this island";
    this.ckSto[1] = "Rate: " + @PKG@.ShCfg.dec(rate) + " " + nm + " a minute";
    this.ckSto[2] = "Stored here " + @PKG@.ShCfg.num(sto) + " / " + @PKG@.ShCfg.num(cap) + " - offline " + offw;
    this.ckCap = "Click a tree to chop it (" + this.ckTn + " trees, " + @PKG@.ShClk.logsAt(ns) + " logs a tree). Your spirits keep working while you are away.";
    double cv = this.ckTi >= 0 && this.ckTi < LN ? tcv[this.ckTi] : 1.0;
    int mx = @PKG@.ShCfg.CK_NS_MAX;
    // 0 Tree size (new)
    this.ckUpL[0] = "Lv " + ns + " / " + mx; this.ckUpSeen[0] = ns;
    if (ns >= mx) this.ckUpE[0] = "Logs a felled tree: " + @PKG@.ShClk.logsAt(ns) + " (highest)";
    else {
      this.ckUpE[0] = "Logs a felled tree " + @PKG@.ShClk.logsAt(ns) + " -> " + @PKG@.ShClk.logsAt(ns + 1);
      this.ckUpC[0] = ckCost(@PKG@.ShClk.nodeCoins(ns + 1, cv), @PKG@.ShClk.nodeMats(kd, t, ns + 1));
      this.ckUpOk[0] = this.mine;
    }
    // 1 Tree count = Tree Amount (sub 0)
    this.ckUpL[1] = "Lv " + amt + " / 5"; this.ckUpSeen[1] = amt;
    if (amt >= 5) this.ckUpE[1] = "Trees: " + this.ckTn + (sz < 3 ? " - grow the island for more" : " (highest)");
    else {
      this.ckUpE[1] = "Trees " + this.ckTn + " -> " + @PKG@.ShIsl.treeN(sz, amt + 1);
      this.ckUpC[1] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, amt + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 0), sz - 1, (long) (amt + 1)));
      this.ckUpOk[1] = this.mine;
    }
    // 2 Spirit totems = the placed totems (the Totems tab)
    this.ckUpL[2] = tot + (tot == 1 ? " totem" : " totems"); this.ckUpSeen[2] = tot;
    this.ckUpE[2] = "Spirits chop for you, also while you are away";
    this.ckUpC[2] = "Place and tier up totems on the Totems tab";
    this.ckUpOk[2] = true;
    // 3 Weather totem = Irrigation (sub 2): faster regrow + its output bonus
    this.ckUpL[3] = "Lv " + irr + " / 5"; this.ckUpSeen[3] = irr;
    if (irr >= 5) this.ckUpE[3] = "Regrow " + (@PKG@.ShClk.regrowMs(irr) / 1000L) + " s" + (sz < 3 ? " - grow the island for more" : " (highest)");
    else {
      this.ckUpE[3] = "Regrow " + (@PKG@.ShClk.regrowMs(irr) / 1000L) + " s -> " + (@PKG@.ShClk.regrowMs(irr + 1) / 1000L) + " s, +" + @PKG@.ShCfg.dec(@PKG@.ShCfg.IRR_PCT) + " % output";
      this.ckUpC[3] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, irr + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 2), sz - 1, (long) (irr + 1)));
      this.ckUpOk[3] = this.mine;
    }
    // 4 Island size = Grow (needs the three at 5 / 5 / 5)
    this.ckUpL[4] = ckSize(sz) + " (" + sz + " / 3)"; this.ckUpSeen[4] = sz;
    if (sz >= 3) this.ckUpE[4] = "Large - the biggest island";
    else {
      this.ckUpE[4] = ckSize(sz) + " -> " + ckSize(sz + 1) + ": room for " + @PKG@.ShIsl.tx(sz + 1).length + " trees";
      if (amt < 5 || irr < 5 || deco < 5) this.ckUpC[4] = "First Tree count, Weather and Decorations 5/5 (" + amt + ", " + irr + ", " + deco + ")";
      else { this.ckUpC[4] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L)); this.ckUpOk[4] = this.mine; }
    }
    // 5 Decorations (sub 1)
    this.ckUpL[5] = "Lv " + deco + " / 5"; this.ckUpSeen[5] = deco;
    if (deco >= 5) this.ckUpE[5] = "All decorations" + (sz < 3 ? " - grow the island for more" : " (highest)");
    else {
      this.ckUpE[5] = "Looks + " + @PKG@.ShCfg.dec(@PKG@.ShCfg.DECO_PCT) + " % output a level";
      this.ckUpC[5] = ckCost(@PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, deco + 1), cv), @PKG@.ShIsl.mats(kd, t, @PKG@.ShCombat.subMat(kd, 1), sz - 1, (long) (deco + 1)));
      this.ckUpOk[5] = this.mine;
    }
    this.ckUpCap = this.mine ? "coins + " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.tok(kd, t, "ench")) : "the island owner buys upgrades";
  } else this.ckCap = "No Foraging island yet - open Islands to buy the first one.";
  // the island map: five zones of three woods
  for (int i = 0; i < LN && i < 15; i++) {
    int tt = L0 + i;
    int need = @PKG@.ShIsl.zoneNeed(kd, tt);
    boolean open = need <= 0 || lv == -1 || lv >= need;
    this.ckMN[i] = @PKG@.ShIsl.tname(tt);
    this.ckMCur[i] = own[i] >= 0 && own[i] == this.ckSlot;
    this.ckMLock[i] = !open && own[i] < 0;
    if (own[i] >= 0) { this.ckMS[i] = (this.ckMCur[i] ? "Shown now - " : "Yours - ") + ckSize(osz[i]); this.ckMB[i] = this.ckMCur[i] ? 0 : 1; }
    else if (!open) this.ckMS[i] = "Locked: " + @PKG@.ShIsl.skillWord(kd) + " " + need;
    else if (i == this.ckNext) {
      this.ckMS[i] = "Buy: " + ckCost(@PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[i]), @PKG@.ShIsl.mats(kd, tt, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L));
      this.ckMB[i] = this.mine ? 2 : 0;
    }
    else this.ckMS[i] = "Buy the islands before it first";
  }
  for (int z = 0; z < 5; z++) {
    int tz = L0 + 3 * z;
    int need = tz < L0 + LN ? @PKG@.ShIsl.zoneNeed(kd, tz) : 0;
    boolean open = need <= 0 || lv == -1 || lv >= need;
    this.ckZS[z] = need <= 0 ? "Open" : (open ? "Open - " + @PKG@.ShIsl.skillWord(kd) + " " + need : "Locked - " + @PKG@.ShIsl.skillWord(kd) + " " + need + (lv >= 0 ? " (you: " + lv + ")" : ""));
  }
}""")
M(page, r"""
public void buildClick(@UCB@ b, @UEB@ ev) {
@CLICK_JAVA@
}""".replace("@CLICK_JAVA@", BUILD_CLICK))
M(page, r"""
public String actClick(String a, @REF@ ref, @ST@ st) {
  if (!a.startsWith("kt")) this.ckPop = "";
  if (a.equals("kback")) { this.view = 0; this.tab = 1; return ""; }
  if (a.equals("kstore")) { this.view = 0; this.tab = 0; return ""; }
  if (a.equals("kmap")) { this.ckMode = 1; return ""; }
  if (a.equals("kisl")) { this.ckMode = 0; return ""; }
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = @PKG@.ShClk.FK;
  if (a.startsWith("kt")) {   // a tree: "kt<spot>:<island slot>" = what the page showed
    int c = a.indexOf(':');
    int spot = -1; int slot = -1;
    try { spot = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); slot = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { spot = -1; }
    if (spot < 0 || slot < 0 || slot != this.ckSlot) return "=The page is up to date now.";
    Object[] r = @PKG@.ShClk.chop(u, k, kd, slot, spot, handId(ref, st));
    String s0 = (String) r[0];
    String pp = (String) r[1];
    if (pp.length() > 0 || s0.length() > 0) { this.ckPop = pp; this.ckPopI = spot; }
    return s0;
  }
  if (a.startsWith("km")) {   // the map: show an island you own (its tier index)
    int i = -1;
    try { i = Integer.parseInt(a.substring(2)); } catch (Throwable x) { i = -1; }
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null || i < 0 || i >= @PKG@.ShIsl.LADN[kd]) return "";
    int s;
    @PKG@.ShStore.LOCK.lock(); try { s = @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + i); } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (s < 0) return "-That island is not yours yet.";
    this.ckSlot = s; this.ckMode = 0;
    return "";
  }
  if (a.startsWith("kb")) {   // the map: buy the next island (tier order, the zone lock, the same cost as the Map tab)
    int i = -1;
    try { i = Integer.parseInt(a.substring(2)); } catch (Throwable x) { i = -1; }
    if (!this.mine) return "-Only the island owner buys islands.";
    if (i < 0 || i >= @PKG@.ShIsl.LADN[kd]) return "";
    String r = @PKG@.ShCore.buyIsland(u, k, kd, i, invOf(ref, st));
    if (r.startsWith("+")) {
      java.util.Properties p = @PKG@.ShStore.get(k);
      if (p != null) { int s; @PKG@.ShStore.LOCK.lock(); try { s = @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + i); } finally { @PKG@.ShStore.LOCK.unlock(); } if (s >= 0) { this.ckSlot = s; this.ckMode = 0; } }
    }
    return r;
  }
  if (a.startsWith("ku")) {   // an upgrade row: "ku<row>:<level the page showed>" (a double click buys once)
    int c = a.indexOf(':');
    int row = -1; int seen = -1;
    try { row = Integer.parseInt(a.substring(2, c < 0 ? a.length() : c)); seen = c < 0 ? -1 : Integer.parseInt(a.substring(c + 1)); } catch (Throwable x) { row = -1; }
    if (row == 2) { this.view = 0; this.tab = 3; this.sel = this.ckTi; this.tpad = 0; return ""; }
    if (row < 0 || row > 5) return "";
    if (!this.mine) return "-Only the island owner buys upgrades.";
    int s = this.ckSlot;
    if (s < 0) return "-Pick an island first.";
    @IC@[] cs = invOf(ref, st);
    if (row == 0) return @PKG@.ShClk.buyNode(u, k, kd, s, seen, cs);
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null) return "-This shard's file could not be read.";
    int which = row == 1 ? 0 : (row == 3 ? 2 : 1);
    int cur;
    @PKG@.ShStore.LOCK.lock(); try {
      if (!@PKG@.ShMath.hasIsland(kd, p, s)) return "-That island is not yours yet.";
      cur = row == 4 ? @PKG@.ShMath.size(kd, p, s) : @PKG@.ShIsl.sub(p, kd, s, which);
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (seen != cur) return "=The page is up to date now - click Upgrade again.";
    if (row == 4) return @PKG@.ShCore.grow(u, k, kd, s, cs);
    return @PKG@.ShCore.buySub(u, k, kd, s, which, cs);
  }
  if (a.startsWith("gc:")) {   // a store cell = that item kind (the clicked logs first, then the stock)
    if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner collects here.";
    return @PKG@.ShCore.collectKind(u, k, kd, a.substring(3), invOf(ref, st));
  }
  if (a.equals("colall")) {
    if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner collects here.";
    return @PKG@.ShCore.collect(u, k, kd, -1, invOf(ref, st));
  }
  return "";
}""")
'''

# ---------------------------------------------------------------------------------------------------- 1. ShCfg: the clicker's settings (Server Setup -> Shards -> Shard clicker)
P.rep(r'''CATS = [("shards", "Shards"), ("production", "Production"), ("totems", "Totems"), ("costs", "Costs"), ("crafting", "Crafting")]
''', r'''# 0.4.23 THE SHARD CLICKER (Foraging first; tools/shards_0_4_23_patch.py): its settings (Server Setup -> Shards -> Shard clicker; arrays swapped whole)
CK_FK = KINDS.index("Foraging")
CK_NS_H = [0.02, 0.04, 0.06, 0.09, 0.12, 0.16, 0.2, 0.25, 0.32, 0.4]   # Tree size 1..10: hours of the coin curve at the island's tier
CK_NS_Q = [1, 2, 3, 4, 6, 8, 10, 14, 18, 24]                           # Tree size 1..10: Enchanted logs of the island's wood
CK_ZLV = [0, 20, 40, 60, 80]                                           # Zone 1..5 opens at this Foraging level (20 levels a zone)
assert len(CK_NS_H) == len(CK_NS_Q) == 10 and len(CK_ZLV) == 5 and CK_FK == 1
for f in ("public static volatile boolean CK_ON = true;", "public static volatile int CK_XP_PCT = 25;", "public static volatile int CK_CPS = 8;",
          "public static volatile int CK_HP = 12;", "public static volatile int CK_DROPS = 3;", "public static volatile int CK_NS_PER = 1;",
          "public static volatile int CK_NS_MAX = 10;", "public static volatile int CK_REGROW = 10;", "public static volatile int CK_WSTEP = 1;",
          "public static volatile int CK_RMIN = 3;", "public static volatile int CK_TSTEP = 25;", "public static volatile int CK_UP1 = 40;", "public static volatile int CK_UP2 = 10;",
          "public static final double[] DEF_CK_NS_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in CK_NS_H),
          "public static volatile double[] CK_NS_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in CK_NS_H),
          "public static final int[] DEF_CK_NS_Q = new int[] { %s };" % ", ".join(str(_x) for _x in CK_NS_Q),
          "public static volatile int[] CK_NS_Q = new int[] { %s };" % ", ".join(str(_x) for _x in CK_NS_Q),
          "public static final int[] DEF_CK_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in CK_ZLV),
          "public static volatile int[] CK_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in CK_ZLV)):
    F(cfg, f)

CATS = [("shards", "Shards"), ("production", "Production"), ("totems", "Totems"), ("costs", "Costs"), ("crafting", "Crafting")]
''')
P.rep(r'''for _r in ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, "0.4: Server Setup label / help too long: %s" % (_r[0],)
''', r'''# 0.4.23: the shard clicker's rows (reload@: ShCfg.loadCfg fills the fields)
CATS = CATS + [("clicker", "Shard clicker")]
ROWS += [("click.enabled", "Shard clicker", "clicker", "bool", "true", "", "", "", "", "live",
          "Off: the Foraging Shard menu shows no clicker and clicks do nothing. Nothing is deleted.", "reload@config.properties:click.enabled"),
         ("click.xpPercent", "Clicker XP (percent)", "clicker", "int", "25", "0", "100", "", "%", "live",
          "Skill XP of a felled tree, in percent of the overworld XP of its logs (Fortune extras pay none).", "reload@config.properties:click.xpPercent"),
         ("click.maxPerSec", "Counted clicks a second", "clicker", "int", "8", "1", "20", "", "", "live",
          "Clicks above this many a second do nothing (auto-clickers gain nothing).", "reload@config.properties:click.maxPerSec"),
         ("click.treeHp", "Chops to fell a tree", "clicker", "int", "12", "1", "1000", "", "", "live",
          "Damage a tree takes before it falls (1 chop = 1 with a hatchet of the wood's tier).", "reload@config.properties:click.treeHp"),
         ("click.logs", "Logs per felled tree", "clicker", "int", "3", "1", "1000", "", "", "live",
          "Logs a felled tree drops before Tree size and Fortune.", "reload@config.properties:click.logs"),
         ("click.treeSizeLogs", "More logs per Tree size level", "clicker", "int", "1", "0", "100", "", "", "live",
          "Each Tree size level adds this many logs to a felled tree.", "reload@config.properties:click.treeSizeLogs"),
         ("click.treeSizeMax", "Tree size levels", "clicker", "int", "10", "0", "10", "", "", "live",
          "The highest Tree size level (0 = none can be bought).", "reload@config.properties:click.treeSizeMax"),
         ("click.treeSizeHours", "Tree size coins (curve hours)", "clicker", "text", ",".join("%g" % _x for _x in CK_NS_H), "", "120", "", "", "live",
          "10 numbers, level 1..10: hours of the coin curve at the island's tier.", "reload@config.properties:click.treeSizeHours"),
         ("click.treeSizeEnch", "Tree size Enchanted logs", "clicker", "text", ",".join(str(_x) for _x in CK_NS_Q), "", "120", "", "", "live",
          "10 numbers, level 1..10: Enchanted logs of the island's wood.", "reload@config.properties:click.treeSizeEnch"),
         ("click.regrowSec", "A felled tree grows back in", "clicker", "int", "10", "1", "3600", "", "s", "live",
          "Seconds before a felled tree can be chopped again (before the weather totem).", "reload@config.properties:click.regrowSec"),
         ("click.weatherSec", "Weather totem: faster regrow", "clicker", "int", "1", "0", "600", "", "s", "live",
          "Seconds less regrow per Weather totem (Irrigation) level.", "reload@config.properties:click.weatherSec"),
         ("click.minRegrowSec", "Shortest regrow", "clicker", "int", "3", "0", "3600", "", "s", "live",
          "A tree never grows back faster than this.", "reload@config.properties:click.minRegrowSec"),
         ("click.tierStep", "Hatchet tier step (percent)", "clicker", "int", "25", "0", "100", "", "%", "live",
          "More (or less) chop damage per tier your hatchet is above (or below) the wood.", "reload@config.properties:click.tierStep"),
         ("click.oneTierUp", "Wood 1 tier above hatchet: damage", "clicker", "int", "40", "1", "100", "", "%", "live",
          "Chop damage on wood one tier above your hatchet (40 % = 2.5x the chops, as in the world).", "reload@config.properties:click.oneTierUp"),
         ("click.twoTiersUp", "Wood 2 tiers above hatchet: damage", "clicker", "int", "10", "1", "100", "", "%", "live",
          "Chop damage two tiers above (10 % = 10x the chops). 3+ tiers above cannot be chopped.", "reload@config.properties:click.twoTiersUp"),
         ("click.zoneLevel", "Zone opens at Foraging level", "clicker", "text", ",".join(str(_x) for _x in CK_ZLV), "", "60", "", "", "live",
          "5 numbers, Zone 1..5: islands of a zone are bought from this Foraging level.", "reload@config.properties:click.zoneLevel")]
for _r in ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, "0.4: Server Setup label / help too long: %s" % (_r[0],)
''')
P.rep(r'''_load += ["  CB_MAT = cmt;"]
''', r'''_load += ["  CB_MAT = cmt;"]
_load += ["  CK_ON = bool(p.getProperty(\"click.enabled\"), true);",   # 0.4.23 the shard clicker
          "  CK_XP_PCT = intOf(p.getProperty(\"click.xpPercent\"), 25, 0, 100);",
          "  CK_CPS = intOf(p.getProperty(\"click.maxPerSec\"), 8, 1, 20);",
          "  CK_HP = intOf(p.getProperty(\"click.treeHp\"), 12, 1, 1000);",
          "  CK_DROPS = intOf(p.getProperty(\"click.logs\"), 3, 1, 1000);",
          "  CK_NS_PER = intOf(p.getProperty(\"click.treeSizeLogs\"), 1, 0, 100);",
          "  CK_NS_MAX = intOf(p.getProperty(\"click.treeSizeMax\"), 10, 0, 10);",
          "  CK_NS_H = decsOf(p.getProperty(\"click.treeSizeHours\"), DEF_CK_NS_H, 0.0, 1000.0, \"click.treeSizeHours\");",
          "  CK_NS_Q = intsOf(p.getProperty(\"click.treeSizeEnch\"), DEF_CK_NS_Q, 0, 100000, \"click.treeSizeEnch\");",
          "  CK_REGROW = intOf(p.getProperty(\"click.regrowSec\"), 10, 1, 3600);",
          "  CK_WSTEP = intOf(p.getProperty(\"click.weatherSec\"), 1, 0, 600);",
          "  CK_RMIN = intOf(p.getProperty(\"click.minRegrowSec\"), 3, 0, 3600);",
          "  CK_TSTEP = intOf(p.getProperty(\"click.tierStep\"), 25, 0, 100);",
          "  CK_UP1 = intOf(p.getProperty(\"click.oneTierUp\"), 40, 1, 100);",
          "  CK_UP2 = intOf(p.getProperty(\"click.twoTiersUp\"), 10, 1, 100);",
          "  CK_ZLV = intsOf(p.getProperty(\"click.zoneLevel\"), DEF_CK_ZLV, 0, 1000, \"click.zoneLevel\");"]
''')

# ---------------------------------------------------------------------------------------------------- 2. ShIsl: the zone of a wood tier + its lock
P.rep(r'''# MANUAL PHASE seeds (spec 7): `made` items of island `slot`''', r'''# 0.4.23 ZONE LOCKS (Foraging first; Skyy 2026-11-14 "have zone locks for all the shards"): a tier's zone (3 tiers a zone, tools/tier_tags.py LOGS),
# the Foraging level it opens at (click.zoneLevel) and why an island of it cannot be bought yet (null = it can; no SkyySkills = open, an unread level = locked)
M(isl48, r"""
public static int zoneOf(int t) {
  int tr = t < 0 || t >= TN ? 1 : TIER[t];
  int z = (tr - 1) / 3 + 1;
  return z < 1 ? 1 : (z > 5 ? 5 : z);
}""")
M(isl48, r"""
public static int zoneNeed(int kd, int t) {
  if (kd != @CKFK@) return 0;
  int[] a = @PKG@.ShCfg.CK_ZLV;
  int z = zoneOf(t);
  return a == null || z - 1 >= a.length ? 0 : a[z - 1];
}""".replace("@CKFK@", str(CK_FK)))
M(isl48, r"""
public static String zoneNo(java.util.UUID u, int kd, int t) {
  int need = zoneNeed(kd, t);
  if (need <= 0) return null;
  int lv = level(u, kd);
  if (lv == -1) return null;
  if (lv == -2) return "-Your " + skillWord(kd) + " level could not be read right now - try again in a moment.";
  if (lv >= need) return null;
  return "-Zone " + zoneOf(t) + " is locked: the " + tname(t) + " island needs " + skillWord(kd) + " " + need + " (you: " + lv + ").";
}""")
# MANUAL PHASE seeds (spec 7): `made` items of island `slot`''')

# ---------------------------------------------------------------------------------------------------- 3. buying an island: the zone lock (Foraging)
P.rep(r'''  int slot;
  long ver;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it (purchaseM commits while nothing was saved since)
    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0) return "=You own the "''', r'''  String zno = @PKG@.ShIsl.zoneNo(u, kd, t);   // 0.4.23: a locked zone's islands wait (Foraging; asked before the lock)
  if (zno != null) return zno;
  int slot;
  long ver;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it (purchaseM commits while nothing was saved since)
    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0) return "=You own the "''')

# ---------------------------------------------------------------------------------------------------- 4. the store grid shows the clicked drops of every shard
P.rep(r'''      gAdd(m, out, s - 100L * e);
    }
    if (bon.length() > 0) gAdd(m, bon, @PKG@.ShMath.ench(kd, p, i));''', r'''      gAdd(m, out, s - 100L * e);
    }
    if (!isC) {   // 0.4.23: the clicker's drops (<kind>.i<n>.drops) of every other shard
      java.util.Iterator hj = @PKG@.ShMath.held(kd, p, i).entrySet().iterator();
      while (hj.hasNext()) { java.util.Map.Entry he2 = (java.util.Map.Entry) hj.next(); gAdd(m, (String) he2.getKey(), ((Long) he2.getValue()).longValue()); }
    }
    if (bon.length() > 0) gAdd(m, bon, @PKG@.ShMath.ench(kd, p, i));''')

# ---------------------------------------------------------------------------------------------------- 5. Collect: the clicked drops first (collectHeld), then the 0.4.22 Collect (collectS)
P.rep(r'''public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.3.1''',
      r'''public static String collectS(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.4.23: the 0.4.22 collect0 (stored stock), renamed; 0.3.1''')
P.rep(r'''# 0.3.1 sound pass: the wrapper - the 0.3 body, then the collect sting on a "+" result (after the shard lock is released)
''', r'''# 0.4.23 THE CLICKED DROPS (<kind>.i<n>.drops of a non-Combat shard - what the clicker felled): the Collect pattern (debit + SAVE first, a refused save
# takes nothing; then the inventory, what does not fit goes back to its island); the collection credit as Collect; NO XP (the click paid it).
# null = nothing clicked is stored there (the 0.4.22 Collect alone answers)
M(core, r"""
public static String collectHeld(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {
  if (kd == @PKG@.ShCombat.CK || !@PKG@.ShCfg.ON || cs == null) return null;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return null;
  if (gate(u, k, kd, p) != null) return null;
  int n = @PKG@.ShMath.SLOTS;
  Object[] tk = new Object[n];
  java.util.LinkedHashMap got = new java.util.LinkedHashMap();
  long want = 0L; long given = 0L; long back = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties old = new java.util.Properties();
    for (int i = 0; i < n; i++) {
      if (slot >= 0 && i != slot) continue;
      String dk = @PKG@.ShMath.ik(kd, i, "drops");
      if (@PKG@.ShStore.str(p, dk).length() == 0) continue;
      java.util.LinkedHashMap tm = new java.util.LinkedHashMap();
      java.util.LinkedHashMap rest = new java.util.LinkedHashMap();
      java.util.Iterator it = @PKG@.ShMath.held(kd, p, i).entrySet().iterator();
      while (it.hasNext()) {
        java.util.Map.Entry e = (java.util.Map.Entry) it.next();
        if (only != null && !only.equals(e.getKey())) { rest.put(e.getKey(), e.getValue()); continue; }
        tm.put(e.getKey(), e.getValue());
        want += ((Long) e.getValue()).longValue();
      }
      if (tm.isEmpty()) continue;
      old.setProperty(dk, @PKG@.ShStore.str(p, dk));
      tk[i] = tm;
      @PKG@.ShMath.heldSet(kd, p, i, rest);
    }
    if (want <= 0L) return null;
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) {
      java.util.Iterator oi = old.entrySet().iterator();
      while (oi.hasNext()) { java.util.Map.Entry oe = (java.util.Map.Entry) oi.next(); p.setProperty((String) oe.getKey(), (String) oe.getValue()); }
      @PKG@.ShCfg.warn("Collect refused (chopped drops, debit not written): " + err);
      return "-Collect failed: the shard file could not be saved. Nothing was taken.";
    }
    for (int i = 0; i < n; i++) {
      if (tk[i] == null) continue;
      java.util.LinkedHashMap bk = new java.util.LinkedHashMap();
      java.util.Iterator ti = ((java.util.LinkedHashMap) tk[i]).entrySet().iterator();
      while (ti.hasNext()) {
        java.util.Map.Entry te = (java.util.Map.Entry) ti.next();
        String id = (String) te.getKey();
        long q = ((Long) te.getValue()).longValue();
        long g = @PKG@.ShInv.give(cs, id, q);
        if (g > 0L) { given += g; got.put(id, Long.valueOf((got.get(id) == null ? 0L : ((Long) got.get(id)).longValue()) + g)); }
        if (q > g) bk.put(id, Long.valueOf(q - g));
      }
      if (!bk.isEmpty()) {
        java.util.LinkedHashMap hb = @PKG@.ShMath.held(kd, p, i);
        java.util.Iterator bi = bk.entrySet().iterator();
        while (bi.hasNext()) {
          java.util.Map.Entry be = (java.util.Map.Entry) bi.next();
          Object o = hb.get(be.getKey());
          long l = ((Long) be.getValue()).longValue();
          back += l;
          hb.put(be.getKey(), Long.valueOf((o == null ? 0L : ((Long) o).longValue()) + l));
        }
        @PKG@.ShMath.heldSet(kd, p, i, hb);
      }
    }
    if (back > 0L) { String e2 = @PKG@.ShStore.save(k, p); if (e2 != null) @PKG@.ShCfg.warn("Collect: " + back + " chopped items that did not fit are back in memory but not on disk yet: " + e2); }
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " slot " + slot + " chopped debit " + want + " given " + given + " back " + back + (only != null ? " only " + only : "") + " " + got.toString());
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (given <= 0L) return "-Your inventory is full - nothing was collected.";
  StringBuilder gt = new StringBuilder();
  String extra = "";
  java.util.Iterator gi = got.entrySet().iterator();
  while (gi.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) gi.next();
    long c = ((Long) en.getValue()).longValue();
    if (gt.length() > 0) gt.append(" + ");
    gt.append(@PKG@.ShCfg.num(c)).append(' ').append(@PKG@.ShTotem.pretty((String) en.getKey()));
    long oc = owed(u, (String) en.getKey(), c);   // the collection credit, as Collect (no lock held)
    if (oc > 0L) extra = extra + " - " + @PKG@.ShCfg.num(oc) + " " + @PKG@.ShTotem.pretty((String) en.getKey()) + " collection count waiting";
  }
  return "+Collected " + gt.toString() + " (chopped)" + extra + (back > 0L ? ". " + @PKG@.ShCfg.num(back) + " did not fit and stay in the shard." : ".");
}""")
M(core, r"""
public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only) {   // 0.4.23: the chopped drops first, then the 0.4.22 Collect
  String h = collectHeld(u, k, kd, slot, cs, only);
  if (h != null && h.startsWith("-Collect failed")) return h;
  String r = collectS(u, k, kd, slot, cs, only);
  if (h == null) return r;
  if (r != null && r.startsWith("+")) return h.startsWith("+") ? "+" + h.substring(1, h.endsWith(".") ? h.length() - 1 : h.length()) + "; " + r.substring(1) : r;
  return h;
}""")
# 0.3.1 sound pass: the wrapper - the 0.3 body, then the collect sting on a "+" result (after the shard lock is released)
''')

# ---------------------------------------------------------------------------------------------------- 6. the Foraging Shard menu's footer: "Shard clicker"
P.rep(r'''s_nopick = seg("nopick")
s_nopick.append((FOOT, SUI.spacer(w=IW - 172)))
''', r'''s_nopick = seg("nopick")
s_nopick.append((FOOT, SUI.spacer(w=IW - 172)))
# 0.4.23: the Foraging Shard's footer opens the clicker (view 5) - the same footers with one more Secondary button
CK_BTN_W = 220
s_pickf = seg("pickF")
s_pickf.append((FOOT, SUI.button(P + "Pick", "Pick up Shard", "secondary", w=200)))
s_pickf.append((FOOT, SUI.spacer(w=12)))
s_pickf.append((FOOT, SUI.button(P + "Clk", "Shard clicker", "secondary", w=CK_BTN_W)))
s_pickf.append((FOOT, SUI.spacer(w=IW - 200 - 12 - CK_BTN_W - 172)))
s_precf = seg("pickrecF")
s_precf.append((FOOT, SUI.button(P + "Pick", "Pick up Shard", "secondary", w=200)))
s_precf.append((FOOT, SUI.spacer(w=12)))
s_precf.append((FOOT, SUI.button(P + "Rec", "Get back lost shard", "secondary", w=REC_W)))
s_precf.append((FOOT, SUI.spacer(w=12)))
s_precf.append((FOOT, SUI.button(P + "Clk", "Shard clicker", "secondary", w=CK_BTN_W)))
s_precf.append((FOOT, SUI.spacer(w=IW - 200 - 12 - REC_W - 12 - CK_BTN_W - 172)))
s_nopickf = seg("nopickF")
s_nopickf.append((FOOT, SUI.button(P + "Clk", "Shard clicker", "secondary", w=CK_BTN_W)))
s_nopickf.append((FOOT, SUI.spacer(w=IW - CK_BTN_W - 172)))
assert IW - 200 - 12 - REC_W - 12 - CK_BTN_W - 172 >= 0
''')
P.rep(r'''v = _menu("tabs3"); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"]); v.extend(SEG["pempty"]); v.extend(SEG["tside"]); VARIANTS.append(_foot(v))
''', r'''v = _menu("tabs3"); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"]); v.extend(SEG["pempty"]); v.extend(SEG["tside"]); VARIANTS.append(_foot(v))
for _fk in ("pickF", "pickrecF", "nopickF"):   # 0.4.23: the Foraging footers with the clicker button
    v = _menu("tabs0"); v.extend(SEG["c0"]); v.extend(SEG["cempty"]); v.extend(SEG["c1"]); VARIANTS.append(_foot(v, _fk))
''')
P.rep(r'''    "  if (this.mine && this.lostKind >= 0) {", jseg("pickrec"), binds([(P + "Pick", "pick"), (P + "Rec", "reclaim")]),
    "  } else if (this.mine) {", jseg("pick"), binds([(P + "Pick", "pick")]), "  } else {", jseg("nopick"), "  }",
''', r'''    "  boolean ckF = this.kind == %d && @PKG@.ShCfg.CK_ON;   // 0.4.23: the Foraging Shard's footer opens the clicker" % CK_FK,
    "  if (this.mine && this.lostKind >= 0) {",
    "  if (ckF) {", jseg("pickrecF"), binds([(P + "Pick", "pick"), (P + "Rec", "reclaim"), (P + "Clk", "kopen")]),
    "  } else {", jseg("pickrec"), binds([(P + "Pick", "pick"), (P + "Rec", "reclaim")]), "  }",
    "  } else if (this.mine) {",
    "  if (ckF) {", jseg("pickF"), binds([(P + "Pick", "pick"), (P + "Clk", "kopen")]), "  } else {", jseg("pick"), binds([(P + "Pick", "pick")]), "  }",
    "  } else {",
    "  if (ckF) {", jseg("nopickF"), binds([(P + "Clk", "kopen")]), "  } else {", jseg("nopick"), "  }",
    "  }",
''')

# ---------------------------------------------------------------------------------------------------- 7. the page: view 5 (fill / build / clicks), opened by "kopen"
P.rep(r'''  if (this.view == 4) return actBench(a, ref, st);
  if (a.startsWith("tab")) {''', r'''  if (this.view == 4) return actBench(a, ref, st);
  if (this.view == 5) return actClick(a, ref, st);   // 0.4.23 the clicker
  if (a.startsWith("tab")) {''')
P.rep(r'''  if (a.equals("tmodnext")) { this.modSel = (this.modSel + 1) % 6; return ""; }
  String k = resolve(st);''', r'''  if (a.equals("tmodnext")) { this.modSel = (this.modSel + 1) % 6; return ""; }
  if (a.equals("kopen")) {   // 0.4.23: the Foraging Shard's clicker (the same page, view 5)
    if (this.view != 0 || this.kind != @PKG@.ShClk.FK) return "";
    if (!@PKG@.ShCfg.CK_ON) return "-The shard clicker is switched off on this server.";
    this.view = 5; this.ckMode = 0; this.ckSlot = -1; this.ckPop = ""; this.ckPopI = -1;
    return "";
  }
  String k = resolve(st);''')
P.rep(r'''  if (this.view == 4) fillBench(k, cs);
  else if (this.view == 1) fillExit(k);
''', r'''  if (this.view == 4) fillBench(k, cs);
  else if (this.view == 1) fillExit(k);
  else if (this.view == 5) fillClick(k, cs, ref, st);   // 0.4.23
''')
P.rep(r'''  if (this.view == 1) buildExit(b, ev);
  else if (this.view == 3) buildTotem(b, ev);''', r'''  if (this.view == 1) buildExit(b, ev);
  else if (this.view == 5) buildClick(b, ev);   // 0.4.23
  else if (this.view == 3) buildTotem(b, ev);''')
P.rep(r'''M(page, r"""
public void build0(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''', CK_PAGE_METHODS + r'''M(page, r"""
public void build0(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {''')
P.rep(r'''          "public String[] rTy;", "public String[] rCost;"):
    F(page, f)
''', r'''          "public String[] rTy;", "public String[] rCost;"):
    F(page, f)
# 0.4.23 THE CLICKER (view 5): the mode (0 island / 1 the zone map), the island shown, its scene, the upgrade rows, the map cards; the layout tables
for f in ("public int ckMode;", "public int ckSlot;", "public int ckTi;", "public int ckT;", "public int ckSz;", "public int ckTn;", "public int ckSpN;",
          "public int ckWx;", "public int ckDeco;", "public int ckAmt;", "public int ckNs;", "public boolean[] ckGrow;", "public String ckTree;",
          "public String ckStump;", "public String ckChip;", "public String ckInfo;", "public String ckCap;", "public String ckPop;", "public int ckPopI;",
          "public String ckHand;", "public int ckAxe;", "public int ckLv;", "public int ckNext;", "public String[] ckSto;",
          "public String[] ckUpL;", "public String[] ckUpE;", "public String[] ckUpC;", "public boolean[] ckUpOk;", "public int[] ckUpSeen;", "public String ckUpCap;",
          "public String[] ckMN;", "public String[] ckMS;", "public int[] ckMB;", "public boolean[] ckMLock;", "public boolean[] ckMCur;", "public String[] ckZS;"):
    F(page, f)
for f in CK_PAGE_STATIC:
    F(page, f)
''')

# ---------------------------------------------------------------------------------------------------- 8. the assets: the clicker pictures (MAP_ASSETS, registered) + the Skyglass theme files
P.rep(r'''    for _p, _b in sorted(MAP_ASSETS.items()):   # 0.4.9: the shard map pictures (our own geometry) + page data
        _jz.writestr(_p, _b)
''', r'''    for _p, _b in sorted(MAP_ASSETS.items()):   # 0.4.9: the shard map pictures (our own geometry) + page data
        _jz.writestr(_p, _b)
    for _p, _b in sorted(SUI.glass_texture_files().items()):   # 0.4.23: the Skyglass theme (the clicker page; our own drawings, SkyyMenu ships the same bytes)
        _jz.writestr(_p, _b)
''')

# ---------------------------------------------------------------------------------------------------- 9. the ready line
P.rep(r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.22:''', r'''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.23: the Foraging Shard clicker (Shard clicker in the Foraging Shard menu: chop trees with your hatchet, upgrades, zone islands); 0.4.22:''')

# ---------------------------------------------------------------------------------------------------- 10. the clicker block: ShClk + the art + the page markup (before ShMap)
P.rep(r'''# ================= 0.4.9 ShMap: the Map tab's tables''', "CLK_ART_SRC = r'''" + ART_SRC + "'''\n" + CLK_BLOCK + r'''# ================= 0.4.9 ShMap: the Map tab's tables''')

P.rep('''for c in ALLC:
    c.writeFile(OUT)
kit.write(OUT)''', '''ALLC = ALLC + [ckc]   # 0.4.23: ShClk
for c in ALLC:
    c.writeFile(OUT)
kit.write(OUT)''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
