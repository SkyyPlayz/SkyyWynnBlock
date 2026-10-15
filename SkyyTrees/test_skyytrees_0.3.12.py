"""SkyyTrees 0.3.12 - harness for EVERY TREE BRANCHES DOWN (tools/trees_0_3_12_patch.py; R1 of research/Ability-Tree-Redesign-Spec.md), on top
of every 0.3.11 / 0.3.10 section (test_skyytrees_0.3.11.py + test_skyytrees_0.3.10.py, kept as the regression on the 0.3.12 jar). Child JVMs
run the game's own JRE with the cached HytaleServer.jar copy, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder. The live
save data is only READ and copied into scratch.

    python SkyyTrees/test_skyytrees_0.3.12.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS: A load + verify both jars; CC class compare 0.3.11 -> 0.3.12 (no class added / removed, structural changes only where the patch
works); JT assets + manifest; LY THE LAYOUT, executed on the real classes of BOTH jars:
  LY1 every static field of TreeDefs / TreeCalc / TreeClassOps is byte-for-byte 0.3.11's, and of TreeClass all but the position tables
      (NROW, NCOL, NSLOT, SK, SN, SARMS, SR, SD, PL1-PL3): every node keeps id, AP, parents, need, lock, lane, role, kind, amount, level,
      name, icon, texts; the same links;
  LY2 the graph model from the new tables: one node per cell, every node in its slot, every link from a higher row to a lower row, every
      drawn piece belongs to a link and is drawn (kind / arms / stubs agree), every link's pieces join its two cells unbroken (pixel model of
      the real sizes) and never rise above the parent's row, no orphan bar;
  LY3 the REAL TreePage.build for all 9 skill trees (fresh / tier I / tiers I-III / all owned) and both pages of all 8 classes (nothing /
      a chain / a path) on both jars: no exception; the b.set texts and event bindings are exactly 0.3.11's (positions only); tier rows I..VI
      top to bottom with the 5 link rows between them, their colour gold exactly when a node of the tier above is owned; the class
      graph has 7 rows; gold bars appear only with owned chains; a markup layout model: every flow container's children fit inside it (the
      page root 1440 / 1600 x 941 <= 1600 x 980, the grid well, every row, slot, link row) and the anchored children of a cell stay inside
      it without overlapping;
RP / AB every 0.3.11 / 0.3.10 scenario on the 0.3.12 jar; ST start twice on a scratch copy of the live Skyy_SkyyTrees (= 0.3.11's start);
Z the engine-access audit.
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.3.12", "0.3.11"
PKG = "com.skyy.trees."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "trees0312", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyTrees-%s.jar" % PREV_VERSION)))
_saved = list(sys.argv)
sys.argv = [sys.argv[0], "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR]
_spec = importlib.util.spec_from_file_location("test_skyytrees_0_3_11", os.path.join(HERE, "test_skyytrees_0.3.11.py"))
T311 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T311)
sys.argv = _saved
T311.SCRATCH, T311.JAR, T311.PREV_JAR = SCRATCH, JAR, PREV_JAR
T310 = T311.T310
T310.SCRATCH, T310.JAR, T310.PREV_JAR = SCRATCH, JAR, PREV_JAR
CL_JAR, LIVE = T310.CL_JAR, T310.LIVE
FAILS, OKS = [], [0]

# the real sizes (build_skyytrees_0.3.12.py): class graph slot / cell / bar, template link rows
SLOT_W, SLOT_H, CELL_W, CELL_H, BAR = 92, 78, 88, 74, 6
BAR_X, BAR_Y = (CELL_W - BAR) // 2, (CELL_H - BAR) // 2
GOLD, GREY = "#E8A93B", "#797b7c"
TR_CELL_H, TR_ROW_GAP, TR_GRID_TOP = 84, 16, 8   # fixer: the six tier rows + 5 link rows sit centred in the 600 px grid well
LAYOUT_FIELDS = {"NROW", "NCOL", "NSLOT", "SK", "SN", "SARMS", "SR", "SD", "PL1", "PL2", "PL3"}


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ============================================================================================================ the markup model
def _parse(markup):
    """Parse one appended markup into [element, ...]; element = dict(type, id, props {name: raw}, kids [...])."""
    i, n = [0], len(markup)

    def ws():
        while i[0] < n and markup[i[0]] in " \t\r\n":
            i[0] += 1

    def ident():
        ws()
        j = i[0]
        while i[0] < n and (markup[i[0]].isalnum() or markup[i[0]] in "_"):
            i[0] += 1
        return markup[j:i[0]]

    def value():
        depth, q, j = 0, False, i[0]
        while i[0] < n:
            ch = markup[i[0]]
            if q:
                if ch == "\\":
                    i[0] += 1
                elif ch == '"':
                    q = False
            elif ch == '"':
                q = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == ";" and depth == 0:
                v = markup[j:i[0]].strip()
                i[0] += 1
                return v
            i[0] += 1
        raise ValueError("unterminated value in %s" % markup[j:j + 80])

    def element():
        t = ident()
        ws()
        eid = None
        if markup[i[0]] == "#":
            i[0] += 1
            eid = ident()
            ws()
        assert markup[i[0]] == "{", markup[i[0]:i[0] + 60]
        i[0] += 1
        e = {"type": t, "id": eid, "props": {}, "kids": []}
        while True:
            ws()
            if markup[i[0]] == "}":
                i[0] += 1
                return e
            j = i[0]
            name = ident()
            ws()
            if markup[i[0]] == ":":
                i[0] += 1
                e["props"][name] = value()
            else:
                i[0] = j
                e["kids"].append(element())

    out = []
    ws()
    while i[0] < n:
        out.append(element())
        ws()
    return out


def _pairs(raw):
    o = {}
    if not raw or not raw.startswith("("):
        return o
    for part in raw.strip("()").split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            try:
                o[k.strip()] = int(v.strip())
            except ValueError:
                pass
    return o


def build_tree(cmds):
    """The page as an element tree from its AppendInline commands (selector = the parent id)."""
    byid, roots = {}, []

    def index(e):
        if e["id"]:
            byid[e["id"]] = e
        for k in e["kids"]:
            index(k)
    for typ, sel, _data, text in cmds:
        if typ != "AppendInline" or text is None:
            continue
        for e in _parse(text):
            index(e)
            if sel is None:
                roots.append(e)
            else:
                pid = sel.lstrip("#")
                byid[pid]["kids"].append(e)
    return roots, byid


def layout_problems(roots):
    """Every flow container (LayoutMode Left / Top) of known size: its children's main sizes + margins fit its inner size and every child's
    cross size + margins fits too; a container without LayoutMode (a cell): its anchored children stay inside it and do not overlap."""
    probs = []

    def pad(e):
        p = _pairs(e["props"].get("Padding"))
        full = p.get("Full", 0)
        h, v = p.get("Horizontal", full), p.get("Vertical", full)
        return p.get("Left", h), p.get("Right", h), p.get("Top", v), p.get("Bottom", v)

    def walk(e, w, h, path):
        a = _pairs(e["props"].get("Anchor"))
        lm = e["props"].get("LayoutMode")
        pl, pr, pt, pb = pad(e)
        iw = None if w is None else w - pl - pr
        ih = None if h is None else h - pt - pb
        name = path + "/" + (e["id"] or e["type"])
        if lm in ("Left", "Top"):
            main_sum = 0
            for k in e["kids"]:
                ka = _pairs(k["props"].get("Anchor"))
                kw, kh = ka.get("Width"), ka.get("Height")
                if lm == "Left":
                    main_sum += (kw or 0) + ka.get("Left", 0) + ka.get("Right", 0)
                    if ih is not None and kh is not None and kh + ka.get("Top", 0) + ka.get("Bottom", 0) > ih:
                        probs.append("%s: child %s is %d high in a %d row" % (name, k["id"] or k["type"], kh, ih))
                    walk(k, kw, kh if kh is not None else ih, name)
                else:
                    main_sum += (kh or 0) + ka.get("Top", 0) + ka.get("Bottom", 0)
                    cw = kw if kw is not None else (None if iw is None else iw - ka.get("Left", 0) - ka.get("Right", 0))
                    if iw is not None and kw is not None and kw + ka.get("Left", 0) + ka.get("Right", 0) > iw:
                        probs.append("%s: child %s is %d wide in a %d column" % (name, k["id"] or k["type"], kw, iw))
                    walk(k, cw, kh, name)
            lim = iw if lm == "Left" else ih
            if lim is not None and main_sum > lim:
                probs.append("%s: children take %d px of %d (%s)" % (name, main_sum, lim, lm))
        else:
            boxes = []
            for k in e["kids"]:
                ka = _pairs(k["props"].get("Anchor"))
                if "Full" in ka:
                    walk(k, iw, ih, name)
                    continue
                kw, kh = ka.get("Width"), ka.get("Height")
                x, y = ka.get("Left", 0), ka.get("Top", 0)
                if kw is not None and kh is not None and iw is not None and ih is not None:
                    if x + kw > iw or y + kh > ih:
                        probs.append("%s: anchored %s (%d,%d %dx%d) leaves the %dx%d cell" % (name, k["id"] or k["type"], x, y, kw, kh, iw, ih))
                    boxes.append((x, y, kw, kh, k["id"] or k["type"]))
                walk(k, kw if kw is not None else iw, kh if kh is not None else ih, name)
            for p_ in range(len(boxes)):
                for q_ in range(p_ + 1, len(boxes)):
                    A, B_ = boxes[p_], boxes[q_]
                    if A[0] < B_[0] + B_[2] and B_[0] < A[0] + A[2] and A[1] < B_[1] + B_[3] and B_[1] < A[1] + A[3]:
                        probs.append("%s: %s and %s overlap" % (name, A[4], B_[4]))
    for r in roots:
        a = _pairs(r["props"].get("Anchor"))
        if a.get("Width", 0) > 1600 or a.get("Height", 0) > 980:
            probs.append("page root %sx%s is larger than 1600 x 980" % (a.get("Width"), a.get("Height")))
        walk(r, a.get("Width"), a.get("Height"), "")
    return probs


def colours(e):
    """Every Background colour inside element e (its own + its children's), in document order."""
    out = []
    bg = e["props"].get("Background")
    if bg and bg.startswith("#"):
        out.append(bg)
    for k in e["kids"]:
        out += colours(k)
    return out


# ============================================================================================================ child: LY (one jar)
def run_ly(jar, out):
    from jpype import JClass, JString, JImplements, JOverride
    import skyybuild as B
    import harness_kit as HK
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    R = {"fields": {}, "pages": {}, "notes": [], "errors": []}
    T = lambda n: JClass(PKG + n)
    Page, Store, Cfg, Data, Cls, Calc, Defs = T("TreePage"), T("TreeStore"), T("TreeCfg"), T("TreeData"), T("TreeClass"), T("TreeCalc"), T("TreeDefs")
    Modifier = JClass("java.lang.reflect.Modifier")

    def dump(cname):
        c = JClass(PKG + cname).class_
        o = {}
        for f in c.getDeclaredFields():
            if not Modifier.isStatic(f.getModifiers()) or not Modifier.isFinal(f.getModifiers()):
                continue
            f.setAccessible(True)
            v = f.get(None)
            t = str(f.getType().getName())
            if t in ("int", "long", "boolean", "double", "float", "java.lang.String"):
                o[str(f.getName())] = str(v)
            elif t.startswith("["):
                try:
                    o[str(f.getName())] = [str(x) for x in v]
                except Exception:
                    o[str(f.getName())] = "<%s>" % t
        return o
    for cname in ("TreeDefs", "TreeCalc", "TreeClassOps", "TreeClass"):
        R["fields"][cname] = dump(cname)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    UUID, Integer = JClass("java.util.UUID"), JClass("java.lang.Integer")
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    me = UUID(0x7ee5, 312)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    bridge = Store.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    LV = {"lvl": 100}
    bridge.put("skill:fn:level", Fn(lambda o: Integer.valueOf(LV["lvl"])))
    pdir = os.path.join(SCRATCH, "ly-home", os.path.basename(jar))
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = JClass("java.nio.file.Paths").get(pdir)
    NT, NN = int(Defs.NT), int(Cls.NN)
    NID = [str(x) for x in Cls.NID]
    MIX = dict((n, i) for i, n in enumerate(NID))
    TIER = [int(x) for x in Defs.TIER]

    def render(page):
        b, ev = UCB(), UEB()
        err = None
        try:
            page.build(None, b, ev, None)
        except Exception as e:
            err = str(e)[:300]
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data)] for e in ev.getEvents()]
        return {"err": err, "cmds": cmds, "evs": evs}

    def fresh():
        Store.DATA.clear()
        Store.DIRTY.clear()
        d = Data()
        Store.DATA.put(str(me), d)
        return d
    # ---- the 9 template trees x 4 states (+ fixer: "skip<k>" = own tier k-1 only, where tier k waits whole for its reader mod)
    R["coming"] = dict((str(t), [bool(Calc.allComing(t, k)) for k in range(1, 7)]) for t in range(NT))
    states = [(t, st, set(k for k in range(1, 7) if k <= tiers)) for t in range(NT)
              for st, tiers in (("fresh", 0), ("tier1", 1), ("tiers1-3", 3), ("all", 6))]
    for t in range(NT):
        for k in range(2, 6):
            if R["coming"][str(t)][k - 1] and not R["coming"][str(t)][k - 2]:
                states.append((t, "skip%d" % k, set([k - 1])))
    for t, st, own in states:
        d = fresh()
        for s in range(12):
            i = t * 12 + s
            if TIER[i] in own and not bool(Defs.soon(i)):
                d.lv[i] = 1
        page = Page(pr, t)
        r = render(page)
        r["path"] = [any(TIER[t * 12 + s_] == k and int(d.lv[t * 12 + s_]) >= 1 and not bool(Defs.soon(t * 12 + s_)) for s_ in range(12)) for k in range(1, 6)]
        R["pages"]["tree %d %s" % (t, st)] = r
    # ---- the 8 classes x 2 pages x 3 states
    Cfg.CLASS_ON = True
    for ci, cn in enumerate([str(x) for x in Cls.CLASSES]):
        bridge.put("class:" + str(me), cn)
        bridge.put("profile:class:" + str(me), cn)
        for st, ids in (("none", ()), ("chain", ("ROOT", "P1", "P2", "X1", "P3", "A1", "M1A", "A3")), ("path", ("ROOT", "T1", "T2", "PA1", "PA2", "PA3"))):
            for cp in (0, 1):
                d = fresh()
                for nid in ids:
                    d.cown[ci * NN + MIX[nid]] = True
                page = Page(pr, NT)
                page.cpage = cp
                r = render(page)
                R["pages"]["class %s %s p%d" % (cn, st, cp)] = r
    json.dump(R, open(out, "w"))
    sys.stdout.flush()
    os._exit(0)


# ============================================================================================================ parent: LY checks
def ly_checks(new, old):
    fn, fo = new["fields"], old["fields"]
    for cname in ("TreeDefs", "TreeCalc", "TreeClassOps", "TreeClass"):
        diff = sorted(k for k in set(fn[cname]) | set(fo[cname]) if fn[cname].get(k) != fo[cname].get(k))
        allowed = LAYOUT_FIELDS if cname == "TreeClass" else set()
        check(set(diff) <= allowed, "LY1 %s: only the position tables differ from 0.3.11: %s" % (cname, sorted(set(diff) - allowed)))
        if cname == "TreeClass":
            print("LY1. TreeClass position tables changed: %s" % diff)
    C = fn["TreeClass"]
    NN, NSLOT = int(C["NN"]), int(C["NSLOT"])
    NID = C["NID"]
    pg, row, col = [int(x) for x in C["NPAGE"]], [int(x) for x in C["NROW"]], [int(x) for x in C["NCOL"]]
    SK, SN, SA = [int(x) for x in C["SK"]], [int(x) for x in C["SN"]], [int(x) for x in C["SARMS"]]
    SR, SD = [x.lower() == "true" for x in C["SR"]], [x.lower() == "true" for x in C["SD"]]
    PL = [[int(x) for x in C["PL1"]], [int(x) for x in C["PL2"]], [int(x) for x in C["PL3"]]]
    LA, LB = [int(x) for x in C["LA"]], [int(x) for x in C["LB"]]
    ROWS = NSLOT // 9
    check(NSLOT == 63 and ROWS == 7 and len(SK) == 2 * NSLOT, "LY2 7 graph rows x 9 per page (NSLOT %d)" % NSLOT)
    cells = [(pg[n], row[n], col[n]) for n in range(NN)]
    check(len(set(cells)) == NN and all(0 <= r < ROWS and 0 <= c < 9 for (_p, r, c) in cells), "LY2 one node per cell, all inside the grid")
    check(all(SK[p * NSLOT + r * 9 + c] == 1 and SN[p * NSLOT + r * 9 + c] == n for n, (p, r, c) in enumerate(cells))
          and SK.count(1) == NN, "LY2 every node sits in its slot (SK / SN)")
    down = [(NID[a], NID[b]) for a, b in zip(LA, LB) if not (pg[a] == pg[b] and row[b] > row[a])]
    check(not down, "LY2 every connector runs from a higher row to a lower row on its page: %s" % down)

    def rects(k, role):
        p, rest = divmod(k, NSLOT)
        r, c = divmod(rest, 9)
        x0, y0 = c * SLOT_W, r * SLOT_H
        if role == 0:
            return (x0, y0 + BAR_Y, CELL_W, BAR) if SK[k] == 2 else (x0 + BAR_X, y0, BAR, CELL_H)
        return {1: (x0 + BAR_X, y0, BAR, BAR_Y), 2: (x0, y0 + BAR_Y, BAR_X, BAR), 3: (x0 + BAR_X, y0 + BAR_Y, BAR, BAR),
                4: (x0 + BAR_X + BAR, y0 + BAR_Y, CELL_W - BAR_X - BAR, BAR), 5: (x0 + BAR_X, y0 + BAR_Y + BAR, BAR, CELL_H - BAR_Y - BAR),
                6: (x0 + CELL_W, y0 + BAR_Y, SLOT_W - CELL_W, BAR), 7: (x0 + BAR_X, y0 + CELL_H, BAR, SLOT_H - CELL_H)}[role]

    def drawn(k, role):
        if role == 0:
            return SK[k] in (2, 3)
        if role in (1, 2, 4, 5):
            return SK[k] == 4 and (SA[k] & {1: 1, 2: 2, 4: 4, 5: 8}[role]) != 0
        if role == 3:
            return SK[k] == 4
        return SR[k] if role == 6 else SD[k]

    def touch(A, B_):
        ox = min(A[0] + A[2], B_[0] + B_[2]) - max(A[0], B_[0])
        oy = min(A[1] + A[3], B_[1] + B_[3]) - max(A[1], B_[1])
        return ox >= 0 and oy >= 0 and (ox > 0 or oy > 0)
    bad_draw, orphans, broken, rises = [], [], [], []
    per_link = dict((li, []) for li in range(len(LA)))
    for k in range(2 * NSLOT):
        for role in range(8):
            ls = [PL[j][k * 8 + role] for j in range(3) if PL[j][k * 8 + role] >= 0]
            if ls and not drawn(k, role):
                bad_draw.append((k, role, ls))
            if drawn(k, role) and not ls:
                orphans.append((k, role))
            for li in ls:
                per_link[li].append(rects(k, role))
    for li, rs in per_link.items():
        a, b = LA[li], LB[li]
        ca = (col[a] * SLOT_W, row[a] * SLOT_H, CELL_W, CELL_H)
        cb = (col[b] * SLOT_W, row[b] * SLOT_H, CELL_W, CELL_H)
        if not rs:
            broken.append((NID[a], NID[b], "no pieces"))
            continue
        if any(r_[1] < ca[1] for r_ in rs) or any(r_[1] + r_[3] > cb[1] + cb[3] for r_ in rs):
            rises.append((NID[a], NID[b]))
        nodes = [ca, cb] + rs
        seen, todo = {0}, [0]
        while todo:
            x = todo.pop()
            for y in range(len(nodes)):
                if y not in seen and touch(nodes[x], nodes[y]):
                    seen.add(y)
                    todo.append(y)
        if len(seen) != len(nodes):
            broken.append((NID[a], NID[b], "%d of %d parts joined" % (len(seen), len(nodes))))
    check(not bad_draw, "LY2 every piece a link uses is drawn (kind / arms / stubs agree): %s" % bad_draw[:5])
    check(not orphans, "LY2 no orphan bar (every drawn piece belongs to a link): %s" % orphans[:5])
    check(not broken, "LY2 every connector joins its two cells unbroken (pixel model): %s" % broken[:5])
    check(not rises, "LY2 no connector rises above its parent's row or below its child: %s" % rises[:5])
    check(len(per_link) == 41, "LY2 41 links drawn (%d)" % len(per_link))
    # ---- LY3 the rendered pages
    nt = len(fn["TreeDefs"]["TREES"])
    for name in sorted(new["pages"]):
        pn, po = new["pages"][name], old["pages"].get(name)
        check(pn["err"] is None, "LY3 %s builds: %s" % (name, pn["err"]))
        if po is None:
            check(False, "LY3 %s rendered on 0.3.11 too" % name)
            continue
        sets_n = Counter((c[1], c[2]) for c in pn["cmds"] if c[0] != "AppendInline")
        sets_o = Counter((c[1], c[2]) for c in po["cmds"] if c[0] != "AppendInline")
        check(sets_n == sets_o, "LY3 %s: every b.set text = 0.3.11's (positions only): +%s -%s" % (name, list((sets_n - sets_o).items())[:3], list((sets_o - sets_n).items())[:3]))
        check(Counter(map(tuple, pn["evs"])) == Counter(map(tuple, po["evs"])), "LY3 %s: the same event bindings as 0.3.11" % name)
        roots, byid = build_tree(pn["cmds"])
        probs = layout_problems(roots)
        check(not probs, "LY3 %s: the layout model fits (%d problems): %s" % (name, len(probs), probs[:4]))
        grid = byid.get("SkyyTrGrid")
        if name.startswith("tree "):
            pad_ = grid["kids"][0] if grid["kids"] else None
            pa_ = _pairs(pad_["props"].get("Anchor")) if pad_ else {}
            check(pad_ is not None and pad_["id"] is None and not pad_["kids"] and pa_ == {"Height": TR_GRID_TOP},
                  "LY3 %s (fix 4): an %d px spacer tops the grid well: %s" % (name, TR_GRID_TOP, pa_))
            hs = sum(_pairs(k_["props"].get("Anchor")).get("Height", 0) for k_ in grid["kids"])
            check(hs == 6 * TR_CELL_H + 5 * TR_ROW_GAP + TR_GRID_TOP and 600 - hs == TR_GRID_TOP,
                  "LY3 %s (fix 4): the tiers sit centred in the 600 px well (%d px used, %d above, %d below)" % (name, hs, TR_GRID_TOP, 600 - hs))
            kids = [k["id"] for k in grid["kids"][1:]]
            want = []
            for kk in range(1, 7):
                want.append("SkyyTrRow%d" % kk)
                if kk < 6:
                    want.append("SkyyTrLk%d" % kk)
            check(kids == want, "LY3 %s: tier I on top, I..VI downwards with a link row under every tier but the last: %s" % (name, kids))
            # fix 2: gold = a node of the tier above owned, OR that tier waits whole for its reader and the link above it is gold (needTier)
            ac_ = new["coming"][name.split()[1]]
            prev_gold, exp_l = False, []
            for kk in range(1, 6):
                g_ = pn["path"][kk - 1] or (ac_[kk - 1] and prev_gold)
                exp_l.append(g_)
                prev_gold = g_
            for kk in range(1, 6):
                cs = colours(byid["SkyyTrLk%d" % kk])
                exp = GOLD if exp_l[kk - 1] else GREY
                check(cs and all(c == exp for c in cs), "LY3 %s: link %d is %s (a tier %d node owned = %s, tier waits for its reader = %s): %s" % (name, kk, "gold" if exp == GOLD else "grey", kk, pn["path"][kk - 1], ac_[kk - 1], sorted(set(cs))))
            if " skip" in name:
                kk = int(name.split("skip")[1])
                check(exp_l[kk - 2] and exp_l[kk - 1] and not pn["path"][kk - 1],
                      "LY3 %s (fix 2): tier %d owned, tier %d waits for its reader -> links %d and %d gold (the line runs on to tier %d)" % (name, kk - 1, kk, kk - 1, kk, kk + 1))
            if name.endswith(" fresh"):
                check(not any(pn["path"]), "LY3 %s: nothing owned = every link grey" % name)
            if name.endswith(" all") and not name.startswith("tree 5 "):
                check(all(pn["path"]), "LY3 %s: everything owned = every link gold" % name)
        else:
            rows = [k for k in grid["kids"] if (k["id"] or "").startswith("SkyyTrCR")]
            check(len(rows) == 7, "LY3 %s: 7 graph rows (%d)" % (name, len(rows)))
            gold = sum(1 for r_ in rows for c in colours(r_) if c == GOLD)
            if " none " in name:
                check(gold == 0, "LY3 %s: nothing owned = no gold bar (%d)" % (name, gold))
            if " chain p0" in name or " path p1" in name:
                check(gold > 0, "LY3 %s: the owned chain shows gold bars (%d)" % (name, gold))
    nskip = len([n for n in new["pages"] if " skip" in n])
    check(nskip >= 1, "LY3 (fix 2): at least one tree has a tier waiting whole for its reader (%d skip scenarios: %s)" % (nskip, sorted(n for n in new["pages"] if " skip" in n)))
    check(len([n for n in new["pages"] if n.startswith("tree ")]) == 4 * nt + nskip and len([n for n in new["pages"] if n.startswith("class ")]) == 48,
          "LY3 every page rendered (%d tree, %d class)" % (len([n for n in new["pages"] if n.startswith("tree ")]), len([n for n in new["pages"] if n.startswith("class ")])))


# ============================================================================================================ parent
def icon_hook_checks():
    """Fix 3: the build script's node_icon, executed: a game id missing in the 0.7 pre-release Assets.zip stops the build (as must_icon)."""
    src = open(os.path.join(HERE, "build_skyytrees_%s.py" % VERSION), encoding="utf8").read().replace(chr(13) + chr(10), chr(10))
    parts = []
    for fn_ in ("must", "must_icon", "node_icon"):
        m = re.search(r"^def %s\(.*?(?=^\S)" % fn_, src, re.M | re.S)
        check(m is not None, "IH: def %s found in the build script" % fn_)
        if m is None:
            return
        parts.append(m.group(0))
    def run(art, ids, ids07, own=()):
        g = {"ITEM_IDS": set(ids), "ITEM_IDS_07": ids07, "ASSETS_07": "<0.7>", "NODE_ICON_ART": dict(art), "OWN_ICON_IDS": set(own)}
        exec(chr(10).join(parts), g)
        try:
            return g["node_icon"]("Mage.A1", "Fallback_Icon")
        except SystemExit as e:
            return "STOP: %s" % e
    check(run({}, ["A"], {"A"}) == "Fallback_Icon", "IH: no entry = today's icon")
    check(run({"Mage.A1": "A"}, ["A"], {"A"}) == "A", "IH: a game id in both Assets.zip versions is used")
    check(run({"Mage.A1": "A"}, ["A"], None) == "A", "IH: no 0.7 pre-release installed = the release check only")
    r = run({"Mage.A1": "A"}, ["A"], {"B"})
    check(str(r).startswith("STOP") and "0.7 pre-release" in str(r), "IH (fix 3): a game id missing in the 0.7 pre-release stops the build: %s" % r)
    r = run({"Mage.A1": "Z"}, ["A"], {"A"})
    check(str(r).startswith("STOP") and "NODE_ICON_ART" in str(r), "IH: an unknown id stops the build: %s" % r)
    check(run({"Mage.A1": "Own"}, ["A"], {"A"}, own=["Own"]) == "Own", "IH: an id this jar ships passes without the game checks")


def main():
    if "--ab" in sys.argv:
        return T310.run_ab(arg("--out"))
    if "--rp" in sys.argv:
        return T311.run_rp(arg("--out"))
    if "--ly" in sys.argv:
        return run_ly(arg("--ly"), arg("--out"))
    T = T310.t36()
    if "--load" in sys.argv:
        return T.run_load(arg("--load"), arg("--out"))
    if "--cc" in sys.argv:
        return T.sk().run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--st" in sys.argv:
        return T.t34().run_start(arg("--st"), arg("--fake"), arg("--live"), arg("--out"), arg("--tag"))
    if "--mkfake" in sys.argv:
        T.t34().t33().H.run_mkfake(arg("--mkfake"))
        return
    if "--audit" in sys.argv:
        H = T.t34().t33().H
        H.SCRATCH = SCRATCH
        H.run_audit(arg("--audit"), arg("--fake"), arg("--out"))
        return
    for j in (JAR, PREV_JAR, CL_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = T310.snap(LIVE)
    me = os.path.abspath(__file__)

    def child(args_, out_):
        with open(out_ + ".log", "wb") as lf:
            subprocess.run([sys.executable, me] + args_ + ["--out", out_, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        if not os.path.isfile(out_):
            print(open(out_ + ".log", encoding="utf8", errors="replace").read()[-3000:])
            return None
        return json.load(open(out_))
    try:
        icon_hook_checks()
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            r = child(["--load", j], os.path.join(SCRATCH, "load-%s.json" % tag)) or {}
            check(r and not r.get("load_fails") and r.get("classes", 0) >= 30,
                  "A (%s): %s classes load, verify (-Xverify:all), initialise %s" % (tag, r.get("classes"), r.get("load_fails", [])[:3]))
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        cc = child(["--cc", JAR, "--prevjar", PREV_JAR, "--repl", json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules})],
                   os.path.join(SCRATCH, "cc.json"))
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            KIT = {"CfgFn", "CfgRows", "CfgPub", "CfgKit", "CfgHist", "CfgImp", "CfgText"}
            check(not cc["added"] and not cc["gone"], "CC: no class added or removed: %s %s" % (cc["added"], cc["gone"]))
            gone = dict((c, v["fields_gone"]) for c, v in cls_.items() if v["fields_gone"])
            check(not gone, "CC: no field removed: %s" % gone)
            struct = dict((c, sorted(m.split("(")[0] for m in v["structural"])) for c, v in cls_.items() if v["structural"] and c not in KIT)
            print("CC. 0.3.11 -> 0.3.12 structural: %s" % struct)
            newf = dict((c, v["fields_new"]) for c, v in cls_.items() if v["fields_new"])
            check(not newf, "CC: no new field: %s" % newf)
            # TreePage: build (tier order + link rows) / buildClass (7 rows); TreeClass: the position tables (<clinit>); CfgFile: the version
            allowed = {"TreePage", "TreeClass", "CfgFile"}
            check(set(struct) <= allowed, "CC: structural changes only in %s: %s" % (sorted(allowed), sorted(set(struct) - allowed)))
            check(set(struct.get("TreePage", [])) <= {"build", "buildClass"}, "CC: TreePage changes only in build / buildClass: %s" % struct.get("TreePage"))
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        np_ = set(n for n in zp.namelist() if not n.endswith(".class"))
        diff = sorted(n for n in (nn | np_) if n != "manifest.json" and (n not in nn or n not in np_ or zj.read(n) != zp.read(n)))
        check(not diff, "JT: every asset is byte for byte 0.3.11's: %s" % diff[:5])
        mn, mp = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        mnd, mpd = dict(mn), dict(mp)
        mnd.pop("Description", None)
        mpd.pop("Description", None)
        check(json.dumps(mnd, sort_keys=True) == json.dumps(mpd, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.3.11's but the version (+ description)")
        lyn = child(["--ly", JAR], os.path.join(SCRATCH, "ly-new.json"))
        lyo = child(["--ly", PREV_JAR], os.path.join(SCRATCH, "ly-prev.json"))
        check(lyn is not None and lyo is not None, "LY ran on both jars")
        if lyn and lyo:
            n0 = OKS[0] + len(FAILS)
            ly_checks(lyn, lyo)
            print("LY. %d layout checks (%d pages per jar)" % (OKS[0] + len(FAILS) - n0, len(lyn["pages"])))
        rp = child(["--rp"], os.path.join(SCRATCH, "rp.json"))
        check(rp is not None, "RP ran")
        if rp:
            for ok, what in rp.get("checks", []):
                check(ok, what)
            check(len(rp.get("checks", [])) >= 65, "RP: every 0.3.11 replant scenario ran on 0.3.12 (%d checks)" % len(rp.get("checks", [])))
        ab = child(["--ab"], os.path.join(SCRATCH, "ab.json"))
        check(ab is not None, "AB ran")
        if ab:
            for ok, what in ab.get("checks", []):
                check(ok, what)
            print("AB. %d executed checks (the 0.3.10 scenarios on the 0.3.12 jar)" % len(ab.get("checks", [])))
            check(len(ab.get("checks", [])) >= 40, "AB: every scenario ran (%d checks)" % len(ab.get("checks", [])))
        fake = os.path.join(SCRATCH, "fake")
        subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=SCRATCH)
        sts = {}
        for tag, j in (("new", JAR), ("prev", PREV_JAR)):
            sts[tag] = child(["--st", j, "--fake", fake, "--live", LIVE, "--tag", tag], os.path.join(SCRATCH, "st-%s.json" % tag))
            check(sts[tag] is not None and len(sts[tag].get("starts", [])) == 2, "ST (%s): two starts ran" % tag)
        if sts.get("new") and sts.get("prev"):
            T34 = T.t34()
            nz = lambda r: T34.norm_start(r).replace(VERSION, "0.3.X").replace(PREV_VERSION, "0.3.X")
            sn, sp = sts["new"]["starts"], sts["prev"]["starts"]
            check(nz(sn[0]) == nz(sp[0]), "ST: start 1 of 0.3.12 = 0.3.11's (the live file is not rewritten): %s / %s" % (sn[0]["changed"], sp[0]["changed"]))
            check(sn[1]["changed"] == [] and sn[1]["sum"] == sn[0]["sum"], "ST: start 2 changes nothing and reads the same: %s" % sn[1]["changed"])
            print("ST. start twice on the live copy: start 1 changed %s (same as 0.3.11), start 2 nothing" % sn[0]["changed"])
        au = child(["--audit", JAR, "--fake", fake], os.path.join(SCRATCH, "audit.json"))
        check(au is not None, "Z: the audit child ran")
        if au:
            check(not au.get("refused") and au.get("refs", 0) > 2000, "Z: engine-access audit: %s references, 0 refused: %s" % (au.get("refs"), str(au.get("refused"))[:400]))
            check(len(au.get("control") or []) >= 1, "Z: the audit's control is refused")
            print("Z. %s references, %d refused" % (au.get("refs"), len(au.get("refused") or [])))
        check(T310.snap(LIVE) == live_before, "the live Skyy_SkyyTrees folder was never written (only read + copied)")
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyTrees %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
