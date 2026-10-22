# Radial skill-tree pages + the Rebirth Nexus as one node map (BUILD-READY spec, 2026-10-22)

Where this goes: `research/` (INDEX.md research row). Answers to the questions at the end go word for word into `docs/answered/ui.md`
(`python tools/qa_append.py ui ...`); builds and results go into `docs/log/2026-10.md`. Owner: Skyy (they/them).

**Skyy's words (docs/answered/ui.md 2026-10-22):** "i definitely want to do the rebirth page like this, but id like to do our trees like this.
should we try to do every tree on 1 page? or split it up into a few pages like this? should we do one per tree? or combine a few trees?" +
popups "Grouped pages (Recommended)" and "Separate per tree (Recommended)" + "their skills menu seems buggy" (ours must be solid; UI-Ideas.md:
"before copying a pan / zoom map, prove in a probe that our inline pages can drag / zoom reliably; if not, use a fixed-size radial page (no
drag) that still fits 1080").

**Reference look (learn the LOOK only, never their art):** `research/refs/skill-trees-hylterium-1.webp` / `-2.webp`,
`research/refs/rebirth-tree-hylterium.webp` (local, git-ignored). One map, emblem in the centre, profession hubs around it in their own colour,
dotted-line branches of small round talent nodes with rank dots + lock badges, learnt path lit gold, a banner per tree, left column = trees
(level + points), right panel = talent details (tree + branch, name, Rank n / m, text, REQUIREMENTS, COST, "Ready to unlock", LEARN), legend
(learnt / ready / locked / selected), zoom - 110 % + / Recenter / drag.

---

## 1. FEASIBILITY (the core)

### 1.1 Verdict

**Yes, without pan / zoom, and with almost only proven parts.** Every page (up to 143 nodes on Gathering) fits a **840 x 774 map canvas
inside the normal 1600 x 980 hub page at 1080p**, nodes 32 px, at least 6 px between any two nodes (prototyped against the real
`tools/trees_v3_data.py`, section 2.6). Diagonal dotted lines are **pictures generated at build time** (the UI cannot rotate anything).
**Drag-to-pan and mouse zoom are NOT possible** on a server-driven page (no event reaches the server). We replace zoom with a
**Focus view** (one tree alone, bigger nodes with names): a second layout computed at build time, nothing worked out at run time. This is
also why ours will not be "buggy" like theirs: every coordinate is fixed at build time and asserted.

### 1.2 What the engine and our own pages already prove

| Need | Status | Proof |
|---|---|---|
| Nodes at absolute x / y in a canvas | **PROVEN, deployed** | SkyyRebirth 0.1-0.4.2 Nexus canvas: `SUI.panel(..., layout=None)` + children `anchor={"left": l, "top": t}` (88 discs in 0.1-0.3, 21 discs + labels since 0.4.0; `build_skyyrebirth_0.4.2.py` ~3380-3420, its build asserts in-canvas + >= 6 px gaps). SkyyHud editor previews (absolute Left / Top in a 1280 x 720 group). |
| Child order = draw order (lines under nodes) | proven in practice | Hud editor ("previews drawn BEFORE the grid = behind the invisible handles, proven visible on 0.3.3"); Trees class graph draws bars before cells. Re-checked in probe M2. |
| Our own PNG textures in a jar | **PROVEN, deployed** | Kit Sky Window art `Common/UI/Custom/SkyyKit/*@2x.png` (probe k1a / art1 / art2 PASS 2026-10-15), SkyyMenu hub tab icons `Common/UI/Custom/SkyyHubTabs/*@2x.png` (0.3.30). Rule: path inside `Common/UI/Custom/` (outside = disconnect), markup without `@2x`, client loads the @2x file. |
| Transparent PNG over other elements | proven | hub tab icons sit behind the tab word; Sky Window ornaments. |
| Swap a picture without a rebuild (`b.set("#X.AssetPath", ...)`) | proven on the **HUD** (AssetImage) | SkyyHud minimap tiles, arrow, ring (`build_skyyhud_0.3.34.py` 6079 / 6370 / 6679). On a PAGE + with a jar-shipped texture: probe M4. |
| Move one element (`b.setObject("#X.Anchor", Anchor)`) | proven on the **HUD** | minimap grid pans with ONE Anchor set (6363). On a page via sendUpdate: probe M5. |
| Rotation of an element / image | **NOT AVAILABLE** | 166 vanilla `.ui` files: no rotation / transform property (only "Rotation" labels and sliders in admin tools). Our minimap shows 16 PRE-RENDERED arrow headings for the same reason. |
| Scaling (zoom) | **NOT AVAILABLE** | no scale property on elements; only re-layout from the server (a full rebuild with new anchors). |
| Drag / wheel on the page background | **NOT AVAILABLE** | `CustomUIEventBindingType` (HytaleServer.jar) = Activating, RightClicking, DoubleClicking, MouseEntered / Exited, MouseButtonReleased, ValueChanged, Validating, Dismissing, Focus*, KeyDown, SelectedTabChanged, ElementReordered, Dropped, DragCancelled, Slot* (item slots only). No mouse move, no wheel, no position. Hover events must never update the page (HANDOFF 2 - client crash). |
| Client-side 2-axis scrolling | exists in the client, unused by us | client has `LeftScrolling / RightScrolling / TopScrolling / BottomScrolling` layouts and horizontal + vertical scrollbar state. A nested TopScrolling + LeftScrolling map might scroll natively (wheel / bars). NOT needed by this spec; optional probe M7 only. |
| Packet size | no risk | `CustomPage` is compressed, MAX_SIZE 1,677,721,600 bytes; `CustomUICommand` 49,152,029. A 1,000-element page is ~150-250 KB of markup. |
| Element count | **UNVERIFIED above ~600** | no known client limit; Menu-Pattern 3.3 already flags 200 / 500 rows as UNVERIFIED. Probe M1 opens 1,200 and 1,600 elements and times it. |

### 1.3 How the dotted lines are drawn (options compared)

| Option | Elements | Files | Risk | Verdict |
|---|---|---|---|---|
| A. Many small dot images per line (1 element per dot) | ~1,500 per page | 2 | too many elements, slow rebuild | no |
| B. One rotated thin image per line | - | - | rotation does not exist | impossible |
| C. **One pre-rendered PNG per edge** (its bounding box, @2x, transparent), grey and gold variants | ~165 per page | ~330 per layout | proven parts only | fallback |
| D. **One BASE picture per layout** with every line grey + junction diamonds + hub rings, plus **one gold PNG per edge only where lit** | 1 + lit edges (0-165) | 1 base + 1 gold per edge per layout | proven parts only; one big texture (840 x 774, @2x 1680 x 1548) | **RECOMMENDED** |

D keeps the page smallest (a new player = 1 line element). Base PNGs are mostly transparent (~20-60 KB each). Lit = gold: a spine segment
into row r when row r is OPEN (tree points spent >= its gate, `TreeV3.GATES`); a spoke into a node when that node has >= 1 rank; hub ->
row-1 junction always lit (row 1 is always open). This is the 0.3.12 "gold rule" of the class graph, kept.

### 1.4 The node (3 elements, state in the picture)

- **Disc** (32 x 32; Focus view 44; Nexus 40): a picture per state, baked at build time - no runtime colour maths:
  `locked` (dark disc, grey ring, padlock badge bottom right), `soon` (locked look + "..." badge: dead hook, "coming soon"), `ready`
  (dark disc, gold ring = can learn now), `learnt k / m` (ring in the TREE colour with k of m rank pips lit along the bottom of the ring =
  Hylterium's rank dots), `max` (tree-colour ring + gold pips + soft glow). Free perk / row ability = a **diamond** (22 px) on the branch
  spine with the same states. Capstone = 40 px disc with a star badge.
  Count: pip variants for max 1..5 (k = 1..m: 15) x 13 tree colours + 6 shared (locked, soon, ready per size) + diamonds = ~230 PNGs of
  64 x 64 @2x (~0.5 KB) per mod. Pips in the picture = no rank Label, so text never has to fit a 32 px disc.
- **Icon:** `ItemIcon` 18 px centred (the node's icon item; `NODE_ICON_ART` hook stays, empty = today's icon).
- **Hit box:** a transparent `Button` (kit `hover_row`, silent), **26 x 26 centred** in the disc (the generator asserts no two hit boxes
  touch); `TooltipText` = name + "Rank 2 / 5" (trial key "tooltip"; the right panel shows everything, nothing depends on it).
- **Selected:** ONE halo picture (cyan ring, 44 px) for the whole page, moved by `b.setObject("#SkyyTmSel.Anchor", ...)` (probe M5) - else
  placed at build time on rebuild (proven).
- Disc state change: rebuild (proven). Faster path if probe M4 passes: the disc is an `AssetImage` and Learn sends only
  `b.set("#SkyyTmN<k>.AssetPath", ...)` for the changed node + its gold edges' Visible + the panel texts.

### 1.5 Element count (worst case: Gathering, every edge lit)

| Part | Elements |
|---|---|
| Hub page rows 1 + 2 (kit `hub_page`) | ~50 |
| Left rail (5 page rows + 13 tree rows x 3 + legend 4 x 2) | ~52 |
| Right panel (tree head + talent detail + 2 buttons + status) | ~45 |
| Map: base picture 1, emblem 2, 4 hubs x 3, 4 banners x 2, halo 1 | 24 |
| Map: 143 nodes x 3 | 429 |
| Map: gold edges (all lit, worst) | 165 |
| **Total** | **~765 (new player ~600)** |

Rebuild cost per click is the same order as today's class graph page (9 x 7 cells + bars + Abilities + Lattice). Probe M1 tests 1,200 and
1,600 so there is room for the Focus labels and later growth.

### 1.6 Disconnect risks checked (HANDOFF section 2)

No underscores in ids (`#SkyyTmN12`, `#SkyyTmN12B`, `#SkyyTmE40`, `#SkyyTmBase`, `#SkyyTmSel`); inline only; page root Width / Height only;
textures only under `Common/UI/Custom/SkyyTrees/Map/` and `.../SkyyRebirth/Map/` written without @2x; every property in the kit's
`PROVEN_*` table or behind a probe key (`assert_proven`); no ItemGridSlot (ItemIcon by id only); no update from MouseEntered / Exited;
never close a page right before opening another (rail jumps to the Nexus = SkyyRebirth opens its page in place of ours, the hub way).

### 1.7 The probe (SkyyUiProbe 0.7, op only, one session, then retired with the probe jars)

`/skyprobe map <case>` (admin `requirePermission` + `setPermissionGroups(new String[0])`), each case one page that shows its own
"PROBE <name> - WHAT TO SEE" list (kit `probe_page` rules). Art = the real generated textures (section 3.2) for one layout (Gathering).

| Case | Page | Pass when |
|---|---|---|
| M1 `map-count` | Gathering at full size: base PNG + 143 nodes (3 elements) + all 165 gold edges + rail + panel (~765); `M1b` the same + 450 dummy nodes (~1,200); `M1c` ~1,600 | opens, no disconnect; open time felt < 1 s (server logs build ms + markup bytes); clicking 10 nodes fast = 10 chat lines naming the node; 10 rebuilds in a row, no crash |
| M2 `map-order` | base lines under gold edges under discs; a node Button overlapping a line picture | lines under nodes; a click on a node over a line reaches the server; a click on bare line / background does nothing |
| M3 `map-crisp` | the base + gold PNGs at @2x | dotted diagonals crisp at 1080p and Skyy's own resolution (screenshot), no seams between a gold edge and the base line under it |
| M4 `map-assetimage` | disc as `AssetImage` with `AssetPath` of a JAR-shipped texture; button "next state" sends `b.set(".AssetPath")` via sendUpdate (no rebuild) | the disc shows; the state picture swaps in place; no "Could not find" fallback |
| M5 `map-anchor` | the halo moved with `b.setObject("#SkyyTmSel.Anchor", ...)` via sendUpdate on a click | halo jumps to the clicked node, nothing else redraws |
| M6 `map-tooltip` | TooltipText on 3 node buttons (with the `tooltip` probe key) | hover shows name + rank; Esc with a tooltip open is safe |
| M7 `map-scroll` (optional) | a 1680 x 1548 map inside an 840 x 774 TopScrolling holding a LeftScrolling | learn only: does the wheel / scrollbars pan both ways? (not used by this spec) |

Results go into `docs/log/` and the passing keys into `skyyui.PROBED` (`map-assetimage`, `map-anchor`; `tooltip` if M6 passes). If M1b
fails, Focus view only shows ONE tree per page by default (the layouts already exist, section 2.5) - no redesign needed.

---

## 2. LAYOUT

### 2.1 The page (every tree page and the Nexus; Menu-Pattern 3.1 / 3.4)

Kit `hub_page(P, "character", sub=False, footer=False)` = 1600 x 980, rows 1 + 2 (Character tabs, Trees selected; the Nexus page keeps
Profiles selected as today), content **1552 x 774**:

```
| left rail 232 | 12 | map canvas 840 x 774 (well, layout None) | 12 | right panel 456 (Menu-Pattern detail panel) |
```

No sub-tab row: the rail IS the navigation. No footer: Learn / Respec / status live in the right panel. Legend in the rail's foot.

- **Left rail (232):** five PAGE rows (28 high: "Gathering", "Crafting", "Adventure", "Class", "Rebirth Nexus"; the open page = selected
  style) and under each its TREE rows (42 high: 24 px tree icon, name 15 bold in the tree colour, "Lv 23 - 4 points" 13 px; the selected
  tree = selected bar #4274a5). Click a page row = that page (whole view). Click a tree row = its page with that tree selected (hub halo +
  right panel tree head); a second click = Focus view of that tree. Nexus row opens SkyyRebirth's page through the new bridge key
  `rebirth:fn:open` (section 3); hidden when SkyyRebirth is missing; greyed "Rebirth is off" for players while rebirth.on=false.
  Sizes (asserted with `SUI.fit`): 5 x 28 + 13 x 42 + legend 84 = 770 <= 774.
- **Legend (rail foot):** 4 rows: learnt (tree-colour ring) / ready (gold ring) / locked (grey + padlock) / selected (cyan halo) - the
  same pictures at 20 px + a 13 px caption.
- **Right panel (456, `panel("well")`):** TREE HEAD (hub icon 40, tree name 18 bold tree colour, "Level 23 / 50", XP line gold
  #e8c25a, "4 points free - 19 spent - row 5 opens at 20", respec price line) + a 2-button segmented row **Whole page | Focus**; then
  TALENT (after a node click; before: "Click a talent to see its ranks and learn it." captionLight): caption "Mining - Vein Delver - Row 3",
  name (tipName 18, tree colour), "Rank 2 / 5" (gold), what it does (Style Guide 15: Now value green, Next blue / green, coming soon grey),
  REQUIREMENTS (red / green lines: "Row 3 opens at 10 points in Mining - you have 8", "Needs SkyyFishing" for a dead hook), COST
  ("1 point" gold), status ("Ready to unlock" green / "Locked" red / "Max rank" gold), **Learn** (Primary, 44 high, full width; Secondary
  disabled when it cannot) and **Respec tree - 2,300 coins** (Destructive, "Click again to respec" for 5 s - the existing pattern; free
  respec shown "Respec tree - free (1 left this run)"). The existing TR_DET texts and fit checks (`tr_fit_check`) are reused.
- **Class page right panel:** the same + a third segmented button **Loadout** that swaps the panel to today's Abilities + Lattice view
  (unchanged code, it already fits the detail well width 424).

### 2.2 The map canvas (840 x 774, origin top-left)

Centre C = (420, 387). Emblem 96 px (picture, our art) at C. Hubs 44 px at **84 px from C** (emblem 48 + hub 22 + 14) in their tree's
centre direction. Rows on concentric **ellipses** around C: ellipse radii `ax = (420 - 24) x f`, `ay = (387 - 24) x f` with
`f(row) = ring0 + (1 - ring0) x (row - 1) / 5` (row 1..6; light trees spread their 4 rows over the same 6 rings: f at rows 1, 2.67, 4.33, 6).
Angles 0 = up, clockwise. Each tree owns a SECTOR sized by what its branches need (2.4); each branch a sub-sector; in a branch row the items
(ups + the free diamond in the middle) are spread along the ellipse 40-48 px apart around the branch's centre angle; then a relax pass
pushes same-ring neighbours apart along their ellipse until every gap >= 6 px.

Edges (one picture each, 1.3): hub -> J(b, 1), J(b, r) -> J(b, r + 1) along the branch spine, J(b, r) -> each up of row r (short spoke).
J(b, r) = the row's free diamond if it has one, else a 10 px junction diamond drawn in the base picture (not a node).

**Banners** (Hylterium labels): 200 x 44 at the canvas corner nearest each tree's centre angle (4-tree pages: the 4 corners; 3-tree pages:
top-centre, bottom-left, bottom-right): line 1 tree name 15 bold uppercase in the tree colour, line 2 a short motto 12 px caption
(defaults in 2.3). The generator asserts banners overlap no node / hub (it rotates the page start angle by 5 degree steps until clear).

### 2.3 Per page

| Page | Trees (clockwise, sector centre) | Nodes | Node px | Emblem (centre) | Notes |
|---|---|---|---|---|---|
| Gathering | Mining 45, Foraging 135, Farming 225, Fishing 315 | 143 (+4 hubs) | 32 | SkyWynn crest | densest page (prototype min gap 6.5 px at 840 wide) |
| Crafting | Smithing 0, Cooking 120, Alchemy 240 | 99 | 32 (36 if it passes) | anvil + cauldron emblem | light Smithing on top (fewest rows, most space for its banner) |
| Adventure | Combat 45, Acrobatics 135, Exploration 225, Beastmastery 315 | 119 | 32 | crossed swords + compass | **Beastmastery slot always drawn** (positions never move): until the Beastmastery skill exists (P8c) its hub, nodes and banner show the `soon` look, banner line 2 "Arrives with Beastmastery", Learn disabled. Data is already in trees_v3_data (36 upgrades). |
| Class | the player's class tree: its 3 BRANCHES are the 3 hubs (0, 120, 240) | 37-46 | 40 (largest that passes from 44 / 40 / 36 / 32) | the class emblem (Trees 0.4.x root emblem) | capstones 44 px with a star; the row abilities (free) are diamonds 28 px; no class = the "Choose a class" text in the canvas (today's text) |
| Rebirth Nexus (SkyyRebirth) | black hole centre; Void Insight + Head Start beside it (left / right, 130 px); then ONE ARM PER SKILL clockwise from the top: Class, Mining, Foraging, Combat, Beastmastery, Farming, Fishing, Cooking, Alchemy, Smithing, Acrobatics (11 arms) | 21 | 40 | Nexus emblem (approved 2026-10-13, cloud art) 140 px | each arm = its Echo / Hand node at ring 1 + its Void-Forged tool nodes (Mining / Foraging / Farming / Fishing: tool, tool2) at ring 2; arm banner = a 92 x 18 name label at the arm's tip; node ids, ladders, costs, keep line UNCHANGED - positions and pictures only. The Nexus click / hover / Rebirth / Continue rules stay. |

Tree colours (one kit table `SUI.TREE_COLOR`, the SkyyRebirth arm colours where they exist; Skyy may change - Q5): Class #E8A93B,
Mining #8fc8ff, Foraging #8fe08a, Farming #f0d060, Fishing #6fb7e8, Smithing #c0c8d0, Cooking #ffb070, Alchemy #7fe0d0, Combat
#ff8a7a, Acrobatics #a8f0ff, Exploration #b8e07a, Beastmastery #d68fd0, Void #b58cff. Class page hubs: branch 1 / 2 / 3 = the class colour,
then the class colour lighter / darker (no new hue per branch).

Default mottos (Q4): Mining "dig - smelt - prosper", Foraging "fell - gather - replant", Farming "sow - tend - harvest", Fishing "cast -
reel - land", Smithing "forge - temper - refine", Cooking "chop - season - feast", Alchemy "brew - distil - transmute", Combat "fight -
endure - prevail", Acrobatics "leap - roll - fly", Exploration "seek - map - discover", Beastmastery "tame - bond - command".

Points stay per tree (Skyy's popup). Every number (gates 0 / 5 / 10 / 15 / 20 / 25, light 0 / 5 / 10 / 15; 1 point a rank; capstone 1 point
after 25 / 15; respec price) stays where Skill Trees 3 put it (`tools/trees_v3_data.py`, `TreeV3`).

### 2.4 Focus view (replaces zoom - Skyy: "their skills menu seems buggy")

Same page, same canvas, ONE tree: hub at C (emblem hidden), its branches fan over the full 360 degrees, nodes **44 px** with a name label
under each (92 x 16, 13 px, 2 px under the disc; labels in the overlap check), capstones 52. Entered by the second click on a tree row /
a hub / the "Focus" button; left by "Whole page", a page row, or another tree row (navigation - no Back button, Menu-Pattern rule 8).
Precomputed at build time per tree (11 skill trees + 8 class trees), so it is as solid as the whole-page layout.

### 2.5 The coordinate generator (one Python function, in `tools/skyymap.py`, imported by SkyyTrees and SkyyRebirth builds)

New nodes slot in automatically: a new upgrade in `trees_v3_data.py` gets its place at the next build; the build fails loudly if it no
longer fits (then the node size steps down 32 -> 30 -> 28, else the build stops and names the crowded pair).

```python
import math
NODE_SIZES = (44, 40, 36, 32, 30, 28)        # largest that fits wins (whole page: start at 32; Class / Focus: 44)
GAP = 6                                       # min px between two discs (and between disc + label / banner / hub / emblem)
HIT = 26                                      # the click square inside a 32 px disc (scaled with the node)

def items_of(row):                            # one row of one branch: ups with the free diamond in the middle
    ups = [("up", u["id"]) for u in row["ups"]]
    fr = [("free", "free")] if row.get("free") else []
    h = len(ups) // 2
    return ups[:h] + fr + ups[h:]

def ring_f(ri, nrows, ring0):                 # row index 0.. -> ellipse fraction; light trees spread 4 rows over 6 rings
    pos = ri if nrows == 6 else ri * 5.0 / 3.0
    return ring0 + (1.0 - ring0) * pos / 5.0

def radial_layout(groups, W=840, H=774, node=32, ring0=0.46, s=40.0, start=None, emb=96, hub=44,
                  tree_gap=0.6, branch_gap=0.25):
    """groups = [(key, colour, [branch, ...])] in clockwise order (a skill page: one group per tree; the Class page: one group
    per BRANCH). Returns dict(nodes, hubs, edges, junctions, banners) in canvas px (centres)."""
    cx, cy = W / 2.0, H / 2.0
    axm, aym = cx - 8 - node / 2.0, cy - 8 - node / 2.0
    avg = math.sqrt((axm * axm + aym * aym) / 2.0)
    need = []                                 # radians each branch needs at its widest row
    for _, _, branches in groups:
        bn = []
        for b in branches:
            m = max(((len(items_of(r)) - 1) * s + node + GAP) / (avg * ring_f(i, len(b["rows"]), ring0))
                    for i, r in enumerate(b["rows"]))
            bn.append(m + branch_gap * s / (avg * ring0))
        need.append(bn)
    tg = tree_gap * s / (avg * ring0)
    scale = 2 * math.pi / (sum(sum(b) for b in need) + tg * len(groups))
    if start is None:
        start = {3: 0.0, 4: 45.0}.get(len(groups), 0.0)
    ang = math.radians(start) - (sum(need[0]) + tg) * scale / 2.0
    out = dict(nodes=[], hubs=[], edges=[], junctions=[])
    hub_r = emb / 2.0 + hub / 2.0 + 14
    for k, (key, col, branches) in enumerate(groups):
        span = (sum(need[k]) + tg) * scale
        tc = ang + span / 2.0
        out["hubs"].append(dict(key=key, x=cx + hub_r * math.sin(tc), y=cy - hub_r * math.cos(tc), a=tc, col=col))
        ab = ang + tg * scale / 2.0
        for bi, b in enumerate(branches):
            bc = ab + need[k][bi] * scale / 2.0
            prev = ("hub", key)
            for ri, row in enumerate(b["rows"]):
                f = ring_f(ri, len(b["rows"]), ring0)
                ax, ay = axm * f, aym * f
                its = items_of(row)
                da = s / math.hypot(ax * math.cos(bc), ay * math.sin(bc))
                junc = (key, bi, ri, "J")
                out["junctions"].append(dict(id=junc, x=cx + ax * math.sin(bc), y=cy - ay * math.cos(bc)))
                out["edges"].append((prev, junc, "spine", ri))          # lit when row ri is open
                for j, (kind, uid) in enumerate(its):
                    a = bc + (j - (len(its) - 1) / 2.0) * da
                    nid = (key, bi, ri, uid)
                    out["nodes"].append(dict(id=nid, kind=kind, a=a, ax=ax, ay=ay, col=col,
                                             size=node if kind == "up" else int(node * 0.7),
                                             x=cx + ax * math.sin(a), y=cy - ay * math.cos(a)))
                    if kind == "free":                                  # the free diamond IS the junction
                        out["junctions"][-1].update(x=out["nodes"][-1]["x"], y=out["nodes"][-1]["y"], node=nid)
                    else:
                        out["edges"].append((junc, nid, "spoke", ri))   # lit when the node has >= 1 rank
                prev = junc
            ab += need[k][bi] * scale
        ang += span
    relax(out["nodes"], cx, cy)
    return out

def relax(nodes, cx, cy, rounds=200):
    """Deterministic: push same-ring neighbours apart along their own ellipse (radius kept) until every gap >= GAP."""
    for _ in range(rounds):
        moved = False
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                p, q = nodes[i], nodes[j]
                if p["ay"] != q["ay"]:
                    continue
                want = (p["size"] + q["size"]) / 2.0 + GAP + 0.5
                d = math.hypot(p["x"] - q["x"], p["y"] - q["y"])
                if d < want:
                    da = (want - d) / math.hypot(p["ax"] * math.cos(p["a"]), p["ay"] * math.sin(p["a"])) / 2.0
                    if p["a"] > q["a"]:
                        da = -da
                    p["a"] -= da; q["a"] += da
                    for n in (p, q):
                        n["x"], n["y"] = cx + n["ax"] * math.sin(n["a"]), cy - n["ay"] * math.cos(n["a"])
                    moved = True
        if not moved:
            return

def fit_page(groups, sizes=NODE_SIZES, **kw):
    """Try node sizes largest first and ring0 0.38-0.54 / spacing node+6 .. node+20; return the first layout that passes check()
    with the largest min gap; raise SystemExit naming the crowded pair when nothing fits."""
```

`check(layout)` (the build calls it for every page and Focus layout; the harness repeats it on the built jar's markup):
1. every disc, hub, emblem, junction, label and banner box inside the canvas with a 4 px margin;
2. any two discs (circles) >= GAP apart; disc vs hub / emblem / banner / Focus label >= GAP;
3. any two HIT squares (26 / 32 of the disc size, centred) do not touch (>= 2 px);
4. every node of `trees_v3_data.TREES` placed exactly once, no extra; ids unique; positions rounded to whole px;
5. every edge goes from a junction / hub to a node or the next junction (the spine never jumps a row); spine edges into a row point
   outward (radius grows);
6. line count printed: base edges, gold edges (per page) + element count per page (worst case = all lit) + markup bytes; build fails above
   1,000 elements per page until probe M1b passes (then the limit is M1b's number minus 20 %).

Prototype numbers (scratch run on 2026-10-22, the real data, 840 x 774, s and ring0 searched): Gathering 143 nodes at 32 px min gap 6.5,
Adventure 119 at 32 px 6.5, Crafting 99 at 32 px 11.0, Class (Warrior / Assassin / Mage / Priest, 37-46 nodes) at 32 px 13+ (40 px fits
too); 26 px hit squares never touch on any page (circles at 32 px: worst square overlap -4.6 px -> 26 px hit boxes +1.4 px).

### 2.6 Pictures generated at build time (`tools/skyymap.py`, pure Python like `tools/skyyart.py`, our own geometry - committed generator,
no vanilla pixels)

- `map_base(layout)` -> one RGBA @2x PNG per layout: grey dotted lines (dot 2 px every 8 px at @2x, colour `disabled` #797b7c at 60 %),
  junction diamonds, hub rings. Fast encoder (filter 0, zlib 9) added to skyyart as `png_encode(img, fast=True)` (the 5-filter search takes
  ~1 min per 1680 x 1548 picture in pure Python).
- `map_gold(layout)` -> one small PNG per edge (its bounding box + 4 px, @2x), gold #E8A93B dots, same dot phase as the base so they
  cover it exactly.
- `node_textures(colours)` -> the disc / diamond / capstone state pictures (1.4), the halo, the legend minis.
- Files: `Common/UI/Custom/SkyyTrees/Map/<page>/Base@2x.png`, `.../<page>/E<k>@2x.png`, `.../Node/<Colour>-<state>@2x.png`;
  SkyyRebirth the same under `SkyyRebirth/Map/`. Names have no underscores (ids derive from them). Deterministic bytes (same input, same
  jar), so a rebuild without data changes is byte-identical.
- Emblems (Gathering / Crafting / Adventure crest, per-page) = art queue via the skywynn-art skill (cloud draws, local review); until then
  the page shows the SkyWynn crest from the kit art.

---

## 3. BUILD PLAN

### 3.1 Who owns what

| Part | Owner | Notes |
|---|---|---|
| `tools/skyymap.py` (layout, checks, pictures) + `tools/test_skyymap.py` | shared tool (R1) | imported by both builds; layout of every page printed by `python tools/skyymap.py --preview` into `tools/dev/scratch/skyymap/` (PNG previews for review, never committed) |
| kit 1.8: `SUI.node_map(prefix, layout, textures, ...)` (markup for base / edges / nodes / hubs / banners / halo + `assert_proven` + the 1,000-element guard), `SUI.TREE_COLOR`, `SUI.map_rail(...)`, legend block; probe keys `map-assetimage`, `map-anchor`; `tools/skyyui_test.py` + Style Guide new section 16 "Node maps" | tools/skyyui.py (R1) | AssetImage only behind its probe key; Group Background TexturePath is the proven default |
| Probe M1-M7 | SkyyUiProbe 0.7 (R0) | op only; retire after the session |
| Gathering / Crafting / Adventure / Class pages, rail, right panel, Focus, Learn / Respec on the map | SkyyTrees 0.5.0 (R2) | `TreePage` replaces the list well; TreeV3 / buy / respec / hooks / saved data UNCHANGED |
| Nexus page on the node map + the 11-arm layout + `rebirth:fn:open` (`apply(Object[] { Ref, Store }) -> Boolean`: opens /rebirth for that player, false when not allowed) | SkyyRebirth 0.5.0 (R3) | node ids, ladders, VP, respec, Rebirth / Continue unchanged |

### 3.2 Rounds

| Round | Size | What | Waits for |
|---|---|---|---|
| R0 | lean (probe jar, op only) | SkyyUiProbe 0.7 cases M1-M7 with real generated textures for Gathering | R1's `skyymap.py` pictures (build R1's tool part first, same day) |
| R1 | full round (shared kit, several mods depend on it) | `tools/skyymap.py` + kit 1.8 blocks + tests + Style Guide 16 | nothing; kit changes must keep every SET build byte-identical where unused (`tools/test_skyyui_hubs.py`) |
| R2 | full round | SkyyTrees 0.5.0 from the then SET pin (today 0.4.5; 0.4.6 is being built - derive from whatever is pinned) via `tools/trees_0_5_0_patch.py` | Skyy's M1-M5 probe session (or ship with Background-texture + rebuild only, which needs only M1 + M2) |
| R3 | lean round | SkyyRebirth 0.5.0 Nexus restyle + `rebirth:fn:open` via `tools/rebirth_0_5_0_patch.py` | R1 (+ R2 for the rail jump back: Trees publishes `tree:fn:open`, the same shape, used by the Nexus page's own rail) |
| R4 | art | Gathering / Crafting / Adventure emblems + any node icons (NODE_ICON_ART) | skywynn-art queue |

Commands: none added, none removed. `/tree` opens the page of the last tree (today's TreePage.LASTTREE); `/tree <name>` opens its page
with that tree selected (today's forms keep working); `/rebirth` unchanged. Every command keeps `setPermissionGroups(hytale:Adventurer)`.

Migration: **none** - no saved data holds a position; layouts are code. Rollback of R2 / R3 = the previous jar (layout only), no data step.

### 3.3 Harness checks (each build's test script)

- `skyymap.check()` passes for every page + every Focus layout + the Nexus (2.5 list) - re-run on the markup pulled out of the BUILT jar
  (anchors parsed back), not only on the Python data.
- Overlap: no two discs closer than 6 px; no two hit squares touching; labels / banners / legend clear; everything inside 840 x 774.
- Fit: the page = 1600 x 980 (`SUI.assert_menu_page`), rail 770 <= 774, right panel texts measured with `SUI.text_lines` at their widths
  (the longest tree / branch / upgrade names in trees_v3_data, "Rank 5 / 5", the longest requirement line at 99999 points).
- Line count + element count per page printed; fail > 1,000 (until M1b raises it).
- Every node of trees_v3_data reachable by a click id (`trn<k>`) and every click id maps back to exactly one (tree, branch, id).
- Gold rule: a fixture player per page (fresh, mid, full) -> the set of lit edges equals the rule in 1.3; a dead-hook node never shows
  `ready`.
- Jar: every texture path inside `Common/UI/Custom/`, no `@2x` in markup, PNG sizes even (2x), byte-identical on a second build.
- The existing TreeV3 tests (buy, gates, respec, migration none) still pass unchanged; bare JVM -Xverify:all; access audit; start twice.
- Crosscheck: `python tools/ci/crosscheck.py --jar <Trees jar> <Rebirth jar> --baseline`; lint 0 fails; smoke test.

### 3.4 In-game test steps (for docs/tests after the deploy)

1. `/tree` -> the Gathering map: crest in the middle, 4 coloured hubs (Mining blue top right, Foraging green bottom right, Farming yellow
   bottom left, Fishing blue top left), dotted grey branches, 4 corner banners; nothing overlaps; the page fits the screen (1080p).
2. Left rail: 5 page rows + 13 tree rows with levels and points; legend at the bottom. Click "Crafting", "Adventure", "Class": each map
   opens in place, the rail keeps its place.
3. Click a ready (gold) node: cyan halo on it, the right panel shows tree - branch - row, name, Rank 0 / n, text, requirements green,
   Cost 1 point, "Ready to unlock". Learn: the ring turns the tree colour with 1 pip, its spoke turns gold, points go down by 1.
4. Spend up to 5 points: row 2's spine lights gold on every branch of that tree; its nodes turn gold-ringed (ready).
5. A locked node: padlock, panel says "Row 4 opens at 15 points in Mining - you have 6" in red, Learn greyed.
6. Click a tree row twice (or Focus): that tree alone, big nodes with names; "Whole page" returns.
7. Adventure: Beastmastery shows greyed with "Arrives with Beastmastery"; its nodes cannot be learnt.
8. Class page: 3 branch hubs around your class emblem; Loadout button shows the Abilities + Lattice exactly as before.
9. Respec: "Click again" pattern, coins taken (or the free one), every ring back to grey / gold, spines unlit except row 1.
10. Rail -> Rebirth Nexus: the black hole page with 11 skill arms + Insight / Head Start beside it; buy a rank (VP), hover the Nexus
    (requirements), everything as before.
11. Hover a node (if the tooltip probe passed): name + rank.
12. Reconnect after the deploy is enough (no .ui files).

### 3.5 UNVERIFIED (probe or first test decides)

1. More than ~600 elements on one page (M1 / M1b / M1c) - the main risk; fallback: Focus-only (one tree per view).
2. `AssetImage` + `b.set(.AssetPath)` with a jar texture on a PAGE (M4) - fallback: Group Background + rebuild (proven).
3. `b.setObject(.Anchor)` via sendUpdate on a page (M5) - fallback: halo placed at rebuild.
4. Crisp @2x diagonal dotted lines and no visible seam between gold edge pictures and the base (M3).
5. Clicks on a Button sitting over a transparent picture element (M2); draw order = child order on a page (proven on HUD / in practice).
6. TooltipText inline (existing `tooltip` key, M6).
7. Client 2-axis scroll (M7) - only informational.
8. Build time of the pure-Python pictures (~18 base pictures + ~1,400 small ones): target < 60 s with the fast encoder.
9. Common-asset count: ~1,700 small PNGs across Trees + Rebirth are sent at join once (cached by hash) - measure join time in the smoke test.

### 3.6 Existing-mod check (PROJECT-RULES 2, done 2026-10-22)

| Mod | What its tree UI is | Verdict |
|---|---|---|
| MMOSkillTree 1.7.3 (Skyy's Mods folder; also SkillHud) | `SkillTreePage.ui` = a header + a TIERS list (rows / cards, LayoutModes Left / Top / TopScrolling) - no node map | nothing to pack; licence gate classes inside (entitlements) |
| EndlessLeveling (Mods folder) | augment cards grid (`AugmentsPage.ui`), passives as cards - no map | nothing to pack |
| RPG Leveling 0.4.2 (Hylterium's base mod, ARR) | no `.ui` files with trees; Hylterium's SKILL TREES map is their own server plugin | look only (already decided in UI-Ideas.md) |
| PathForge 0.0.17 (CurseForge, ARR, Hytale 0.5-0.6, needs HyUI + MultipleHUD) | "Passive Tree" tab (PoE-inspired, data-driven Core / Offense / Defense / Utility); page does not say if it is a drawn node map | not packable (ARR, old Hytale, extra UI library); a read-only look at HyUI's image / line support could be a later study, not needed |
| HyRPG (CurseForge) | "Skill Tree UI: modal" with 18 skills in 3 categories + prerequisites | list-style, nothing to learn |

No Hytale mod we can pack draws a radial talent web; ours is built from our own proven pieces (Nexus canvas, kit textures, minimap tricks).

---

## 4. Questions for Skyy (default in [brackets])

1. Rank on the map: pips in the node's ring like Hylterium's dots, or small numbers? [pips in the ring; the exact "Rank 2 / 5" is in the
   right panel and the hover]
2. No drag / mouse zoom (the server never sees the mouse). OK to replace zoom with a Focus view (one tree alone, bigger nodes with names)?
   [yes - second click on a tree / its hub, "Whole page" to return]
3. Class page: Abilities + Lattice loadout as a "Loadout" button in the right panel? [yes, same code as today]
4. Banner mottos (line 2 under each tree name)? [the short lines in 2.3, e.g. Mining "dig - smelt - prosper"; change any]
5. Tree colours (2.3)? [the table as listed - Rebirth arm colours kept, new ones for Farming / Fishing / Acrobatics / Exploration /
   Beastmastery]
6. Beastmastery before it exists: drawn greyed on Adventure, or hidden until P8c? [drawn greyed "Arrives with Beastmastery" - the map
   never moves later]
7. Nexus: one arm per skill around the black hole (11 arms; the Hand Echo nodes move onto their own skill's arm) instead of today's 6
   arms? [yes - "every skill around it"; node ids, costs and VP unchanged]
8. Page emblems for Gathering / Crafting / Adventure: new art (cloud draws, skywynn-art) or the SkyWynn crest on all three? [new art; crest
   until it is approved]
9. Rebirth Nexus in the trees' left rail while rebirth is off? [shown greyed "Rebirth is off" for players, opens for admins]
