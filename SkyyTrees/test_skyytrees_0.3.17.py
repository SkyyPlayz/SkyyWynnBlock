"""SkyyTrees 0.3.17 - harness for TREE FELLER EARLIER (tools/trees_0_3_17_patch.py): Foraging Tier III = Replanter + Tree Feller (Foraging 20),
Tier VI = Pocket Change (Foraging 60); ids, slots, saved keys unchanged; Tree Feller on row III costs (1 token, B 100), Pocket Change on
Tier VI capstone costs (3 tokens, B 7,400 = ~15M Dust to max like the other capstones) and 0.6 % per level; the one-time trees.properties update TreeMig317. Build first:
    python tools/trees_0_3_17_patch.py && python SkyyTrees/build_skyytrees_0.3.17.py

    python SkyyTrees/test_skyytrees_0.3.17.py [--dir <folder inside tools/dev/scratch/>] [--jar <jar>] [--keep] [--tree-kit]

KIT: the jar is built on the COMMITTED kit (skyyui 1.5). While tools/skyyui.py differs from git HEAD (another builder's uncommitted edits),
this harness - in the parent and in every child - first loads `git show HEAD:tools/skyyui.py` (copied to <dir>/../kit-head/skyyui.py) as
the `skyyui` module, so the page checks use the kit the jar was built with. --tree-kit uses the working-tree file instead.

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch. Nothing outside scratch is written or read but the jars.
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.16 -> 0.3.17: + TreeMig317; TreeDefs (+ SHOW, the tables), TreePage.build (the slot label), setup (TreeMig317.run),
                the version / kit / default-file texts
  MF   manifest = 0.3.16's but Name / Version
  TB   EXECUTED (both jars' TreeDefs, the old one in its own class loader): every static field of TreeDefs is 0.3.16's but TIER, D_TOK,
       D_B, D_PER (+ the new SHOW), and those differ only at Foraging.FCoins (tier 3 -> 6, tokens 1 -> 3, B 500 -> 7400, per 0.002 ->
       0.006) and Foraging.FFeller (tier 6 -> 3, tokens 3 -> 1, B 150000 -> 100); ids, indexes, keys, max, feller.logs unchanged; every
       other tree keeps the template tiers and S numbers; every tree keeps the template's tier sizes 3 / 2 / 2 / 2 / 2 / 1
  LY   EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL page builder): the Foraging page as a hub page (check_page, sizes, ids);
       grid row III = Tier head + Replanter (#SkyyTrN6) + Tree Feller (#SkyyTrN12), row VI = Tier head + Pocket Change (#SkyyTrN7), each
       row centred (rp) so the static link rows' ticks sit on the node centres (parsed from the link markup); tier heads "Tier III -
       Foraging 20" / "Tier VI - Foraging 60"; the II->III link turns gold with a Tier II node, the III->IV link with Tree Feller alone;
       every skill tree page builds with 6 rows + 5 link rows
  PR   EXECUTED prerequisites (TreeCalc.state / lockShort, the real TreeOps.buy): Tree Feller needs Foraging 20 + a Tier II node + 1
       token; then a Tier IV node unlocks through Tree Feller; Pocket Change needs Foraging 60 + a Tier V node + 3 tokens; Dust costs
       (TreeCalc.cost) = B x n^3 with the new B
  SV   EXECUTED saved data (player files written as 0.3.16 wrote them, read by the real TreeStore): Pocket Change maxed / mid-level below
       Foraging 60 without a Tier V node, Tree Feller 6 / 2: every level loads, the node shows owned / maxed, its effect works
       (TreeFx.compute, Pocket Change at 0.6 % per level), an owned node levels up below its new gate, a Tier IV node owned through the
       old Pocket Change path stays; a save writes the same keys back; a Tree Feller owner gets 2 tokens back; a Pocket Change owner whose
       Dust balance the new price makes negative keeps levels + effect, buys wait, the Foraging respec is free and immediate
  MG   EXECUTED TreeMig317 (bare JVM, every start in a fresh class loader, CfgPub.start like the server): scratch COPIES of the two live
       trees.properties (NewBetaTest, HUD mod; read only): exactly the 5 value lines change + the marker line, every other byte kept;
       History copy = the old bytes; 5 change-log lines (nodes.Foraging[...] old -> new); the new costs apply; start 2 writes nothing;
       the kit's Undo (tset back) restores a value and start 3 keeps it. A CRLF file with one LF line, hand edits (kept + named), a
       numerically equal old value (moved), a doubled line (kept), a missing line, no final newline; a file already on the new values;
       a fresh start (the default file carries the marker: nothing to do); the marker = never again
  CT16 the 0.3.16 harness's CT phase (tree:fn:classPage, Class tab mode, hub clicks) on THIS jar
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)


def _arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(_arg("--dir", os.path.join(TOOLS, "dev", "scratch", "trees0317", "h")))


def _blob(d):
    import hashlib
    return hashlib.sha1(("blob %d" % len(d)).encode("ascii") + b"\x00" + d).hexdigest()


def _load_kit():
    """the committed kit as `skyyui` (see KIT above); returns a note"""
    tree = os.path.join(TOOLS, "skyyui.py")
    if "--tree-kit" in sys.argv:
        return "working-tree kit (--tree-kit)"
    head = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=ROOT, capture_output=True).stdout
    if not head or _blob(open(tree, "rb").read()) == _blob(head):
        return "tools/skyyui.py = HEAD"
    kd = os.path.join(os.path.dirname(SCRATCH), "kit-head")
    kf = os.path.join(kd, "skyyui.py")
    assert os.path.realpath(kd).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
    if not os.path.isfile(kf) or open(kf, "rb").read() != head:
        os.makedirs(kd, exist_ok=True)
        open(kf, "wb").write(head)
    sp = importlib.util.spec_from_file_location("skyyui", kf)
    m = importlib.util.module_from_spec(sp)
    sys.modules["skyyui"] = m
    sp.loader.exec_module(m)
    m.SKY_ART_DIR = os.path.join(ROOT, "art", "ui-kit-sky")
    return "the committed kit %s (git HEAD, loaded from %s)" % (m.kit_id(), kf)


KIT_NOTE = _load_kit()
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT

VERSION, PREV = "0.3.17", "0.3.16"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-%s.jar" % PREV)
ADDED = ["TreeMig317"]
EXPECT = {"TreeDefs": ["~<clinit>", "+f SHOW"], "TreePage": ["~m build"], "SkyyTreesPlugin": ["~m setup"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~<clinit>", "~m header"], "TreeCfg": ["~m load"]}
# why: TreeDefs = the TIER / cost tables + SHOW; TreePage.build = the "(S7)" label; SkyyTreesPlugin.setup = TreeMig317.run + the ready line
# (version + kit id); CfgFn / CfgRows / TreeCfg.load = the version
# texts and the default trees.properties text (its "# Foraging S7 / S12 ... (tier ...)" comment lines live in TreeCfg.load + CfgRows)
SLOT_TIER = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6]
FOR_TIERS = [1, 1, 1, 2, 2, 3, 6, 4, 4, 5, 5, 3]
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")
W_RE = re.compile(r"Width: (\d+)")
CELL_W, CELL_GAP, TIER_W = 242, 4, 204
HALF = (CELL_W + CELL_GAP) // 2
GEOM = [([325, 571, 817], [448, 694]), ([448, 694], [448, 694]), ([448, 694], [448, 694]), ([448, 694], [448, 694]), ([448, 694], [571])]


def centres(nk):
    return [TIER_W + (3 - nk) * HALF + j * (CELL_W + CELL_GAP) + CELL_W // 2 for j in range(nk)]


# ============================================================================================================ TB: the table, both jars
def run_tb(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Defs = JClass(PKG + "TreeDefs")
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    CL = JClass("java.lang.ClassLoader")
    ucl = JClass("java.net.URLClassLoader")(JArray(URL)([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                                             CL.getPlatformClassLoader())
    Old = ucl.loadClass(PKG + "TreeDefs")
    New = Defs.class_
    K.check(Old.getClassLoader() is not None and str(Old.getClassLoader()) != str(New.getClassLoader()), "TB: the 0.3.16 TreeDefs in its own loader")
    Arrays = JClass("java.util.Arrays")
    Mod = JClass("java.lang.reflect.Modifier")

    def statics(c):
        d = {}
        for f in c.getDeclaredFields():
            if not Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            v = f.get(None)
            d[str(f.getName())] = str(Arrays.deepToString(JArray(JClass("java.lang.Object"))([v]))) if v is not None else "null"
        return d
    a, b = statics(Old), statics(New)
    K.eq(sorted(set(b) - set(a)), ["SHOW"], "TB: TreeDefs gains only SHOW")
    diff = sorted(k for k in a if a.get(k) != b.get(k))
    K.eq(diff, ["D_B", "D_PER", "D_TOK", "TIER"], "TB: every TreeDefs static field is 0.3.16's but TIER, D_TOK, D_B, D_PER")
    ID = [str(x) for x in Defs.ID]
    fo = list(Defs.TREES).index("Foraging")
    for fld, want in (("TIER", [("FCoins", 3, 6), ("FFeller", 6, 3)]), ("D_TOK", [("FCoins", 1, 3), ("FFeller", 3, 1)]),
                      ("D_B", [("FCoins", 500, 7400), ("FFeller", 150000, 100)]), ("D_PER", [("FCoins", 0.002, 0.006)])):
        ov = list(Old.getDeclaredField(fld).get(None))
        nv = list(getattr(Defs, fld))
        cv = float if fld == "D_PER" else int
        K.eq(sorted((ID[i], cv(ov[i]), cv(nv[i])) for i in range(len(nv)) if ov[i] != nv[i]), want, "TB: %s changes only %s" % (fld, want))
    newT = [int(x) for x in Defs.TIER]
    show = [int(x) for x in Defs.SHOW]
    K.eq(show[fo * 12:fo * 12 + 12], [1, 2, 3, 4, 5, 6, 12, 8, 9, 10, 11, 7], "TB: Foraging slot labels in reading order (Tree Feller S7, Pocket Change S12)")
    K.check(all(show[i] == i % 12 + 1 for i in range(len(show)) if i // 12 != fo), "TB: every other tree keeps its S numbers")
    K.eq(newT[fo * 12:fo * 12 + 12], FOR_TIERS, "TB: the Foraging tiers by slot (S1..S12)")
    for t in range(int(Defs.NT)):
        if t != fo:
            K.eq(newT[t * 12:t * 12 + 12], SLOT_TIER, "TB: %s keeps the template tiers" % Defs.TREES[t])
        K.eq([newT[t * 12:t * 12 + 12].count(k) for k in range(1, 7)], [3, 2, 2, 2, 2, 1], "TB: %s tier sizes (the static link rows)" % Defs.TREES[t])
    ff, fc = ID.index("FFeller"), ID.index("FCoins")
    K.eq((ff, fc, str(Defs.KEY[ff]), str(Defs.KEY[fc])), (23, 18, "Foraging.FFeller", "Foraging.FCoins"), "TB: indexes + saved keys unchanged")
    rp = ID.index("FSapling")
    K.eq((int(Defs.D_MAX[ff]), int(Defs.D_TOK[ff]), int(Defs.D_B[ff])), (6, int(Defs.D_TOK[rp]), int(Defs.D_B[rp])), "TB: Tree Feller max 6, Replanter's token + B (1, 100)")
    K.eq((int(Defs.D_TOK[rp]), int(Defs.D_B[rp])), (1, 100), "TB: Replanter 1 token, B 100")
    cap = [i for i in range(len(ID)) if i // 12 != fo and newT[i] == 6 and not bool(Defs.soon(i))]
    K.check(len(cap) >= 5 and all((int(Defs.D_TOK[i]), int(Defs.D_B[i])) == (3, 150000) for i in cap), "TB: the other Tier VI capstones cost 3 tokens, B 150,000 (%d)" % len(cap))
    K.eq((int(Defs.D_MAX[fc]), int(Defs.D_TOK[fc]), int(Defs.D_B[fc]), float(Defs.D_PER[fc])), (10, 3, 7400, 0.006), "TB: Pocket Change max 10, 3 tokens, B 7,400, 0.6 % / level")
    tot = lambda i: sum(int(Defs.D_B[i]) * n ** 3 for n in range(1, int(Defs.D_MAX[i])))
    K.check(tot(fc) == 14985000 and all(tot(i) == 15000000 for i in cap if int(Defs.D_MAX[i]) == 5),
            "TB: Pocket Change costs 14,985,000 Dust to max, the max-5 capstones 15,000,000")
    Cfg = JClass(PKG + "TreeCfg")
    K.eq([int(x) for x in Cfg.FELLER_LOGS], [1, 2, 4, 5, 6, 10], "TB: feller.logs default 1, 2, 4, 5, 6, 10 (kept)")
    K.eq([int(x) for x in Cfg.TIER_LV], [1, 10, 20, 30, 45, 60], "TB: tier.levels 1 / 10 / 20 / 30 / 45 / 60")
    dft = str(Cfg.DEFAULTS)
    K.check("# Foraging S7 Tree Feller (tier III)" in dft and "# Foraging S12 Pocket Change (tier VI)" in dft and "# Foraging S6 Replanter (tier III)" in dft
            and "\nForaging.FFeller.max=6\n" in dft and "\nForaging.FFeller.tokens=1\n" in dft and "\nForaging.FFeller.B=100\n" in dft
            and "\nForaging.FCoins.tokens=3\n" in dft and "\nForaging.FCoins.B=7400\n" in dft and "\nForaging.FCoins.per=0.006\n" in dft
            and "\nForaging.FCoins.max=10\n" in dft and dft.count("skyytrees-0.3.17-foraging") == 1, "TB: the default trees.properties: new tiers, S numbers, costs, the 0.3.17 marker")
    K.save()


# ============================================================================================================ LY / PR / SV (one engine)
def run_ly(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Sto, Cfg, Defs, Calc, Ops, HO, Page, Fx = J("TreeStore"), J("TreeCfg"), J("TreeDefs"), J("TreeCalc"), J("TreeOps"), J("TreesHubOpen"), J("TreePage"), J("TreeFx")
    pdir = os.path.join(scratch, "ly-mods", "Skyy_SkyyTrees", "players")
    os.makedirs(pdir, exist_ok=True)
    Sto.DIR = E.Paths.get(pdir)
    Int = JClass("java.lang.Integer")
    FO = list(Defs.TREES).index("Foraging")
    ID = [str(x) for x in Defs.ID]
    IX = dict((n, i) for i, n in enumerate(ID))
    LV = {}

    @JImplements("java.util.function.Function")
    class LvFn(object):
        @JOverride
        def apply(self, a):
            return Int.valueOf(LV.get(str(a[0]), 0))
    E.bridge.put("skill:fn:level", LvFn())
    E.bridge.remove("skill:fn:xp")
    Cfg.EXTRA_DUST = 10 ** 10      # Dust is not what this round tests (levels-ups below need it)
    HO.register()
    n_ = [0]

    def player(level, lines=None):
        n_[0] += 1
        u = E.UUID.fromString("00000000-0000-0000-0000-%012d" % (317000 + n_[0]))
        if lines is not None:
            open(os.path.join(pdir, str(u) + ".properties"), "w", encoding="utf-8").write("v=2\nquiet=false\n" + "".join("%s\n" % x for x in lines))
        P = E.mkp(u, "Forager%d" % n_[0])
        LV[str(u)] = level
        return P

    def bal(u):
        d = Sto.data(u)
        lvl = int(Calc.level(u, FO))
        b = Calc.balance(u, d, FO, lvl)
        return d, lvl, int(b[0]) - int(b[1])

    def st(P, nid):
        d, lvl, tok = bal(P.pr.getUuid())
        i = IX[nid]
        return int(Calc.state(d, i, lvl, tok)), str(Calc.lockShort(d, i, lvl, tok))

    def buy(P, nid):
        r = str(Ops.buy(P.pr, FO, IX[nid] - FO * 12 + 1))
        E.pump(P)
        return r

    def page(P):
        Page.LASTTREE.put(P.pr.getUuid(), Int.valueOf(FO))
        r = HO().apply(P.pr.getUuid())
        E.pump(P)
        pg = E.pg(P)
        K.check(r == E.TRUE and pg is not None and int(pg.tree) == FO, "LY the Trees tab opens the Foraging tree")
        return pg

    def grid(built):
        rows, links = {}, {}
        for ty, sel, txt, _d in built[0]:
            if not txt or not ty or "Append" not in ty or not sel:
                continue
            m = DECL_RE.search(txt)
            if sel.startswith("#SkyyTrRow") and m:
                rows.setdefault(int(sel[len("#SkyyTrRow"):]), []).append((m.group(2), txt))
            if sel == "#SkyyTrGrid" and m and m.group(2).startswith("SkyyTrLk"):
                links[int(m.group(2)[len("SkyyTrLk"):])] = txt
        return rows, links

    def ticks(txt):
        """the link row markup -> (upper tick centres, the bar's [lo, hi), lower tick centres) from its spacer / bar widths"""
        body = txt[txt.index("{") + 1:]
        parts, depth, cur = [], 0, ""
        for ch in body:        # the three direct child groups (ticks up, bus, ticks down)
            if ch == "{":
                depth += 1
            if depth >= 1:
                cur += ch
            if ch == "}":
                depth -= 1
                if depth == 0:
                    parts.append(cur)
                    cur = ""
            if depth < 0:
                break
        res = []
        for pt in parts:
            ws = [int(x) for x in W_RE.findall(pt)]
            res.append(ws)
        return res

    # ---------------------------------------------------------------- LY: the Foraging page
    A = player(20)
    pg = page(A)
    built = HT.build(pg, A)
    w, h, sets, evs = HT.page_check(K, E, A, built, "SkyyTrF", "character", "trees", "Trees", "LY Foraging page", idp="SkyyTr")
    rows, links = grid(built)
    K.eq(sorted(rows), [1, 2, 3, 4, 5, 6], "LY six tier rows")
    want = {1: ["SkyyTrTier1", "SkyyTrN1", "SkyyTrN2", "SkyyTrN3"], 2: ["SkyyTrTier2", "SkyyTrN4", "SkyyTrN5"], 3: ["SkyyTrTier3", "SkyyTrN6", "SkyyTrN12"],
            4: ["SkyyTrTier4", "SkyyTrN8", "SkyyTrN9"], 5: ["SkyyTrTier5", "SkyyTrN10", "SkyyTrN11"], 6: ["SkyyTrTier6", "SkyyTrN7"]}
    for k in range(1, 7):
        K.eq([e for e, _t in rows.get(k, [])], want[k], "LY row %d: tier head + cells in order" % k)
        nk = len(want[k]) - 1
        hw = [int(W_RE.search(t).group(1)) for e, t in rows.get(k, []) if e.startswith("SkyyTrTier")]
        K.eq(hw, [TIER_W + (3 - nk) * HALF], "LY row %d: the tier head width = 204 + rp (the row centred for %d node(s))" % (k, nk))
        cw = [int(W_RE.search(t).group(1)) for e, t in rows.get(k, []) if e.startswith("SkyyTrN")]
        K.check(cw == [CELL_W] * nk, "LY row %d: cells %d px wide (%s)" % (k, CELL_W, cw))
    for k, nm in ((3, "Tier III - Foraging 20"), (6, "Tier VI - Foraging 60")):
        K.check(nm in str(sets.get("#SkyyTrTier%d.Text" % k)), "LY %s (%s)" % (nm, sets.get("#SkyyTrTier%d.Text" % k)))
    for s, nm in ((6, "Replanter"), (12, "Tree Feller"), (7, "Pocket Change")):
        K.check(nm in str(sets.get("#SkyyTrN%dNm.Text" % s)), "LY #SkyyTrN%d = %s" % (s, nm))
        K.check(any(sel == "#SkyyTrN%d" % s and ("trnode%d" % s) in tx for sel, tx in evs), "LY #SkyyTrN%d bound to trnode%d" % (s, s))
    K.check("Tier II first" in str(sets.get("#SkyyTrN12Sb.Text")), "LY Tree Feller at Foraging 20 without Tier II: 'Tier II first' (%s)" % sets.get("#SkyyTrN12Sb.Text"))
    K.check("Foraging 60" in str(sets.get("#SkyyTrN7Sb.Text")), "LY Pocket Change at Foraging 20: 'Foraging 60' (%s)" % sets.get("#SkyyTrN7Sb.Text"))
    # the link rows: static ticks on the node centres of the rows above / below (for THIS tree's rows)
    K.eq(sorted(links), [1, 2, 3, 4, 5], "LY five link rows")
    for k in range(1, 6):
        up, dn = centres(len(want[k]) - 1), centres(len(want[k + 1]) - 1)
        K.eq((up, dn), GEOM[k - 1], "LY link %d: the node centres of rows %d / %d = the build's link geometry" % (k, k, k + 1))
        g = ticks(links.get(k, ""))
        ok = len(g) == 3
        if ok:
            def tx(ws):
                xs, cur = [], 0
                for j in range(0, len(ws) - 1, 2):
                    cur += ws[j]
                    xs.append(cur + ws[j + 1] // 2)
                    cur += ws[j + 1]
                return xs
            ok = tx(g[0]) == up and tx(g[2]) == dn and g[1][0] == min(up + dn) - 3 and g[1][0] + g[1][1] == max(up + dn) + 3
        K.check(ok, "LY link %d: ticks at %s / %s and the bar spans them (parsed %s)" % (k, up, dn, g))
    gold, grey = "E8A93B", "797b7c"
    K.check(all(grey.lower() in links[k].lower() and gold.lower() not in links[k].lower() for k in links), "LY nothing owned: every link row grey")
    # ---------------------------------------------------------------- PR: prerequisites (the real buy)
    K.eq(st(A, "FFeller"), (0, "Tier II first"), "PR Foraging 20, no Tier II: Tree Feller locked 'Tier II first'")
    LV[str(A.pr.getUuid())] = 19
    K.eq(st(A, "FFeller"), (0, "Foraging 20"), "PR Foraging 19: Tree Feller locked 'Foraging 20'")
    K.eq(st(A, "FSapling"), (0, "Foraging 20"), "PR Foraging 19: Replanter locked 'Foraging 20' (the same row)")
    LV[str(A.pr.getUuid())] = 20
    K.eq(buy(A, "FFeller"), "Unlock a Tier II node first", "PR buy Tree Feller without Tier II refused")
    K.eq(buy(A, "FSpeed"), "Unlocked Chopping Speed!", "PR buy Chopping Speed (Tier I)")
    K.eq(buy(A, "FVigor"), "Unlocked Forest Vigor!", "PR buy Forest Vigor (Tier II)")
    K.eq(st(A, "FFeller"), (1, "Locked"), "PR Foraging 20 + Tier II + a token: Tree Feller unlockable")
    built = HT.build(pg, A)
    rows, links = grid(built)
    K.check(gold.lower() in links[1].lower() and gold.lower() in links[2].lower() and gold.lower() not in links[3].lower(),
            "LY Tier I + II owned: links I->II and II->III gold, III->IV grey")
    K.eq(buy(A, "FFeller"), "Unlocked Tree Feller!", "PR buy Tree Feller at Foraging 20 (1 token: 5 earned, 2 spent before)")
    d, lvl, tok = bal(A.pr.getUuid())
    K.eq((int(d.lv[IX["FFeller"]]), tok), (1, 2), "PR Tree Feller level 1, 2 tokens left")
    K.eq([int(Calc.cost(IX["FFeller"], n)) for n in range(1, 6)], [100, 800, 2700, 6400, 12500], "PR Tree Feller Dust per level = Replanter's scale 100 x n^3")
    K.eq([int(Calc.cost(IX["FCoins"], n)) for n in (1, 2, 9)], [7400, 59200, 5394600], "PR Pocket Change Dust per level = 7,400 x n^3")
    built = HT.build(pg, A)
    rows, links = grid(built)
    K.check(gold.lower() in links[3].lower() and gold.lower() not in links[4].lower(), "LY Tree Feller owned (the only Tier III node): link III->IV gold")
    K.check(abs(float(Fx.compute(A.pr.getUuid())[IX["FFeller"]]) - 1.0) < 1e-9, "PR Tree Feller level 1 = 1 more log (feller.logs[0])")
    LV[str(A.pr.getUuid())] = 30
    K.eq(buy(A, "FSpread"), "Unlocked Timber Spread!", "PR Foraging 30: a Tier IV node unlocks through Tree Feller (Tier III)")
    K.eq(buy(A, "FSapling"), "Unlocked Replanter!", "PR Replanter too (row III, 1 token)")
    K.eq(st(A, "FCoins"), (0, "Foraging 60"), "PR Foraging 30: Pocket Change locked 'Foraging 60'")
    LV[str(A.pr.getUuid())] = 60
    K.eq(st(A, "FCoins"), (0, "Tier V first"), "PR Foraging 60 without Tier V: Pocket Change 'Tier V first'")
    K.eq(buy(A, "FCoins"), "Unlock a Tier V node first", "PR buy Pocket Change without Tier V refused")
    K.eq(buy(A, "FSpeed2"), "Unlocked Heavy Hatchet!", "PR buy Heavy Hatchet (Tier V)")
    d, lvl, tok = bal(A.pr.getUuid())
    K.eq(tok, 13 - 7, "PR Foraging 60: 13 tokens earned, 7 spent (Tree Feller 1, Heavy Hatchet 2)")
    K.eq(buy(A, "FCoins"), "Unlocked Pocket Change!", "PR buy Pocket Change at Foraging 60 with Tier V (3 tokens)")
    K.eq(bal(A.pr.getUuid())[2], 3, "PR Pocket Change took 3 tokens")
    K.check(abs(float(Fx.compute(A.pr.getUuid())[IX["FCoins"]]) - 0.006) < 1e-9, "PR Pocket Change level 1 = 0.6 % per log")
    built = HT.build(pg, A)
    rows, links = grid(built)
    K.check(all(gold.lower() in links[k].lower() for k in (1, 2, 3, 4, 5)), "LY a path down to Tier VI: every link row gold")
    HT.page_check(K, E, A, built, "SkyyTrF", "character", "trees", "Trees", "LY Foraging page (path to VI)", idp="SkyyTr")
    # every skill tree still builds the same frame (6 rows of the template sizes, 5 links)
    for t in range(int(Defs.NT)):
        pg.tree = t
        pg.sel = 1
        try:
            rw, lk = grid(HT.build(pg, A))
            K.check(sorted(rw) == [1, 2, 3, 4, 5, 6] and [len(rw[k]) - 1 for k in range(1, 7)] == [3, 2, 2, 2, 2, 1] and sorted(lk) == [1, 2, 3, 4, 5],
                    "LY %s page: 6 rows of 3/2/2/2/2/1 nodes + 5 link rows" % Defs.TREES[t])
        except Exception as e:
            K.check(False, "LY %s page builds: %s" % (Defs.TREES[t], e))
    pg.tree = FO
    for s in (6, 12, 7):        # the detail panel of the moved nodes
        pg.sel = s
        bs = dict((sel, dd) for ty, sel, _t, dd in HT.build(pg, A)[0] if ty == "Set")
        want_ = {6: "Replanter  (S6)", 12: "Tree Feller  (S7)", 7: "Pocket Change  (S12)"}[s]
        K.check(want_ in str(bs.get("#SkyyTrDetName.Text")), "LY detail of slot %d: %s (reading order)" % (s, bs.get("#SkyyTrDetName.Text")))
    # ---------------------------------------------------------------- SV: saved data of 0.3.16 players
    # B: Pocket Change MAXED + a Tier IV node bought through the old Tier III Pocket Change, no Tier V, Foraging 30
    Bp = player(30, ["Foraging.FSpeed=1", "Foraging.FVigor=1", "Foraging.FCoins=10", "Foraging.FSpread=3", "Mining.MSpeed=2", "Foraging.respecAt=0"])
    ub = Bp.pr.getUuid()
    d = Sto.data(ub)
    K.eq([int(d.lv[IX[n]]) for n in ("FSpeed", "FVigor", "FCoins", "FSpread", "MSpeed")], [1, 1, 10, 3, 2], "SV B: every saved level loads")
    K.eq(st(Bp, "FCoins")[0], 3, "SV B: Pocket Change (Tier VI now, player at Foraging 30, no Tier V) stays MAXED")
    K.eq(st(Bp, "FSpread")[0], 2, "SV B: Timber Spread (bought through the old Tier III Pocket Change) stays owned")
    v = Fx.compute(ub)
    K.check(abs(float(v[IX["FCoins"]]) - 0.06) < 1e-9 and abs(float(v[IX["FSpread"]]) - 0.09) < 1e-9, "SV B: Pocket Change 10 = 6 % (0.6 % / level), Timber Spread 9 % (TreeFx)")
    K.eq(buy(Bp, "FSpread"), "Timber Spread is now level 4", "SV B: the owned Tier IV node still levels up")
    K.eq(buy(Bp, "FCoins"), "Pocket Change is already maxed", "SV B: Pocket Change already maxed")
    K.eq(buy(Bp, "FStride"), "Unlock a Tier III node first", "SV B: a NEW Tier IV node needs Replanter or Tree Feller (Pocket Change is Tier VI now)")
    K.check(bool(Sto.saveSync(str(ub))), "SV B: saved")
    txt = open(os.path.join(pdir, str(ub) + ".properties"), encoding="utf-8").read()
    K.check(all(x in txt for x in ("Foraging.FCoins=10", "Foraging.FSpread=4", "Foraging.FSpeed=1", "Foraging.FVigor=1", "Mining.MSpeed=2")),
            "SV B: the file keeps the same keys (Foraging.FCoins=10, Foraging.FSpread=4 ...)")
    K.check(not re.search(r"^Foraging\.(?!FCoins|FSpread|FSpeed|FVigor|respecAt|dustCredit|off)", txt, re.M), "SV B: no new Foraging key written")
    # C: Pocket Change level 4 at Foraging 25 (below its new gate 60, no Tier V): owned, works, levels up
    Cp = player(25, ["Foraging.FSpeed=1", "Foraging.FVigor=1", "Foraging.FCoins=4"])
    uc = Cp.pr.getUuid()
    K.eq(st(Cp, "FCoins")[0], 2, "SV C: Pocket Change level 4 below Foraging 60 = owned")
    K.eq(buy(Cp, "FCoins"), "Pocket Change is now level 5", "SV C: it levels up below its new gate (no gate / path re-check for owned nodes)")
    K.check(abs(float(Fx.compute(uc)[IX["FCoins"]]) - 0.030) < 1e-9, "SV C: Pocket Change level 5 = 3 % per log")
    # D: the old capstone owner: Tree Feller 6 at Foraging 60
    Dp = player(60, ["Foraging.FSpeed=1", "Foraging.FSap=1", "Foraging.FSpread=1", "Foraging.FSpeed2=1", "Foraging.FFeller=6"])
    ud = Dp.pr.getUuid()
    K.eq(int(Sto.data(ud).lv[IX["FFeller"]]), 6, "SV D: Tree Feller 6 loads")
    K.eq(st(Dp, "FFeller")[0], 3, "SV D: Tree Feller 6 = maxed")
    K.check(abs(float(Fx.compute(ud)[IX["FFeller"]]) - 10.0) < 1e-9, "SV D: Tree Feller 6 still fells 10 more logs")
    K.eq(st(Dp, "FCoins"), (1, "Locked"), "SV D: Foraging 60 + a Tier V node: Pocket Change unlockable for the old capstone owner")
    K.eq(bal(ud)[2], 13 - 6, "SV D: tokens re-counted at the new costs - Tree Feller 1 (was 3): 7 free (0.3.16: 5)")
    # E: Tree Feller 2 at Foraging 22 (a Tier II node owned)
    Ep = player(22, ["Foraging.FSpeed=1", "Foraging.FSap=1", "Foraging.FFeller=2"])
    ue = Ep.pr.getUuid()
    K.eq(st(Ep, "FFeller")[0], 2, "SV E: Tree Feller 2 owned")
    K.eq(buy(Ep, "FFeller"), "Tree Feller is now level 3", "SV E: Tree Feller levels up at Foraging 22 (Dust)")
    K.check(abs(float(Fx.compute(ue)[IX["FFeller"]]) - 4.0) < 1e-9, "SV E: Tree Feller 3 = 4 more logs")
    K.check(bool(Sto.saveSync(str(ue))) and "Foraging.FFeller=3" in open(os.path.join(pdir, str(ue) + ".properties"), encoding="utf-8").read(),
            "SV E: saved as Foraging.FFeller=3")
    # F: a Pocket Change owner whose Dust the new price makes negative (no debug Dust): levels + effect stay, buys wait, respec free
    Cfg.EXTRA_DUST = 0
    Fp = player(30, ["Foraging.FSpeed=1", "Foraging.FVigor=1", "Foraging.FCoins=10"])
    uf = Fp.pr.getUuid()
    d, lvl, tok = bal(uf)
    b4 = Calc.balance(uf, d, FO, lvl)
    K.check(int(b4[2]) < int(b4[3]) and int(b4[3]) == 7400 * 2025, "SV F: Pocket Change 10 now counts 14,985,000 Dust spent (earned %s)" % format(int(b4[2]), ","))
    K.eq(st(Fp, "FCoins")[0], 3, "SV F: still maxed")
    K.check(abs(float(Fx.compute(uf)[IX["FCoins"]]) - 0.06) < 1e-9, "SV F: still works (6 %)")
    K.eq(buy(Fp, "FSap"), "Your Foraging balance is negative (costs changed) - respec first, it is free right now", "SV F: new buys wait (the existing negative-balance rule)")
    r_ = str(Ops.respec(Fp.pr, FO))
    E.pump(Fp)
    d = Sto.data(uf)
    K.check(r_.startswith("Respec done") and int(d.lv[IX["FCoins"]]) == 0 and bal(uf)[2] == 7, "SV F: the Foraging respec is free and immediate, every token back: %s" % r_)
    Cfg.EXTRA_DUST = 10 ** 10
    K.notes.append("Tree Feller Dust per level (B 100 x n^3): " + ", ".join("%d->%d %s" % (n, n + 1, format(int(Calc.cost(IX["FFeller"], n)), ",")) for n in range(1, 6)))
    K.save()


# ============================================================================================================ MG: TreeMig317
LIVE_WORLDS = ["NewBetaTest", "HUD mod"]
MK317 = "skyytrees-0.3.17-foraging"
MOVES = [("Foraging.FFeller.tokens", "3", "1"), ("Foraging.FFeller.B", "150000", "100"), ("Foraging.FCoins.tokens", "1", "3"),
         ("Foraging.FCoins.B", "500", "7400"), ("Foraging.FCoins.per", "0.002", "0.006")]
LOGRE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\tSkyyTrees 0\.3\.17\t-\tupdate\tnodes\.Foraging\[([A-Za-z.]+)\]\t(\S+)\t(\S+)\tok$")


def live_dir(w):
    return os.path.join(B.HYTALE, "UserData", "Saves", w, "mods", "Skyy_SkyyTrees")


def run_mg(out, jar, scratch, _home):
    import shutil
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    Paths = JClass("java.nio.file.Paths")

    def loader():
        u = JArray(URL)(1)
        u[0] = File(jar).toURI().toURL()
        return URLCL(u, sysl)

    def start(base):
        ld = loader()
        C = lambda n: JClass(PKG + n, loader=ld)
        b = Paths.get(base)
        C("TreeCfg").FILE = b.resolve("trees.properties")
        C("TreeStore").DIR = b.resolve("players")
        C("TreeCfg").load()
        r = [str(C(n).run(b)) for n in ("TreeMig", "TreeMig32", "TreeMig33", "TreeMig317")]
        C("CfgPub").start(b.getParent(), None)
        cfg = C("TreeCfg")
        nums = (int(cfg.TOK[23]), int(cfg.B[23]), int(cfg.TOK[18]), int(cfg.B[18]), float(cfg.PER[18]))
        return {"C": C, "old": r[:3], "m": r[3], "nums": nums}

    def snap(d):
        o = {}
        for r_, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(r_, f)
                o[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
        return o

    def changed(a, b):
        return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    MARK = str(JClass(PKG + "TreeMig317", loader=loader()).MARK_LINE)
    K.check(MK317 in MARK and MARK.startswith("# "), "MG the marker line is a comment carrying %s" % MK317)
    n_ = [0]

    def case(name, src_dir, body):
        n_[0] += 1
        base = os.path.join(scratch, "mg", "%02d" % n_[0], "mods", "Skyy_SkyyTrees")
        if src_dir:
            shutil.copytree(src_dir, base)
        else:
            os.makedirs(base)
        if body is not None:
            open(os.path.join(base, "trees.properties"), "wb").write(body)
        return base

    def moved(b, eol=b"\n"):
        for k, o, n in MOVES:
            a_ = b"\n" + k.encode() + b"=" + o.encode() + eol
            assert b.count(a_) == 1, k
            b = b.replace(a_, b"\n" + k.encode() + b"=" + n.encode() + eol)
        return b
    NEW = (1, 100, 3, 7400, 0.006)
    OLDN = (3, 150000, 1, 500, 0.002)
    seen = 0
    for w in LIVE_WORLDS:
        src = live_dir(w)
        tp = os.path.join(src, "trees.properties")
        if not os.path.isfile(tp):
            K.notes.append("MG %s: no live trees.properties - skipped" % w)
            continue
        seen += 1
        live_before = open(tp, "rb").read()
        live_snap = snap(src)
        K.check(b"\r\n" not in live_before and live_before.endswith(b"\n") and MK317.encode() not in live_before
                and all(live_before.count(("\n%s=%s\n" % (k, o)).encode()) == 1 for k, o, n in MOVES),
                "MG %s: the live file holds the 5 old default lines once, LF, no 0.3.17 marker" % w)
        lc = case(w, src, None)
        s0 = snap(lc)
        a = start(lc)
        sa = snap(lc)
        ch = changed(s0, sa)
        bak = [k for k in ch if k.startswith("config-history/") and k.endswith(".bak")]
        K.check(ch == sorted(["trees.properties", "config-changes.log", "config-history/index.log"] + bak) and len(bak) == 1,
                "MG %s: start 1 writes only trees.properties, one History copy + index.log, config-changes.log: %s" % (w, ch))
        K.check(len(bak) == 1 and sa[bak[0]] == live_before, "MG %s: the History copy = the old bytes" % w)
        want = moved(live_before) + MARK.encode("latin-1") + b"\n"
        K.check(sa["trees.properties"] == want, "MG %s: exactly the 5 value lines change + the marker line (every other byte kept)" % w)
        nl = [l for l in sa["config-changes.log"].decode("utf8")[len(s0.get("config-changes.log", b"").decode("utf8")):].split("\n") if l.strip()]
        rows = [LOGRE.match(l).groups() if LOGRE.match(l) else ("?", l, "") for l in nl]
        K.eq(rows, [(k[len("Foraging."):], o, n) for k, o, n in MOVES], "MG %s: 5 change-log lines nodes.Foraging[...] old -> new in the kit's format" % w)
        K.check(sa["config-changes.log"].startswith(s0.get("config-changes.log", b"")), "MG %s: the change log only grew" % w)
        K.eq(a["nums"], NEW, "MG %s: the new costs apply at this start (TOK / B Tree Feller, TOK / B / per Pocket Change)" % w)
        K.check(a["m"].startswith("trees.properties updated for SkyyTrees 0.3.17") and "nodes.Foraging[FFeller.tokens] 3 -> 1" in a["m"]
                and "[marker %s added, runs once]" % MK317 in a["m"] and a["old"] == ["", "", ""], "MG %s: the INFO line: %r" % (w, a["m"][:200]))
        b2 = start(lc)
        K.check(changed(sa, snap(lc)) == [] and b2["m"] == "" and b2["nums"] == NEW, "MG %s: start 2 writes nothing" % w)
        Cb = b2["C"]
        lg = [str(x) for x in Cb("CfgFn")().apply(JArray(JObject)(["log", JClass("java.lang.Integer").valueOf(40)]))]
        mine = [x for x in lg if "\tSkyyTrees 0.3.17\t" in x]
        K.eq(sorted(x.split("\t")[4] for x in mine), sorted("nodes.Foraging[%s]" % k[len("Foraging."):] for k, o, n in MOVES), "MG %s: the kit's log lists the 5 changes for Undo" % w)
        un = Cb("CfgFn")().apply(JArray(JObject)(["tset", "nodes.Foraging", "FFeller.tokens", "3", None, "console", "yes", "console"]))
        Cb("CfgPub").flush()
        sc = snap(lc)
        K.check(un is not None and str(un[0]) == "ok" and sc["trees.properties"].count(b"\nForaging.FFeller.tokens=3\n") == 1
                and int(Cb("TreeCfg").TOK[23]) == 3, "MG %s: Undo (tset nodes.Foraging FFeller.tokens back to 3) writes 3 and applies it: %s" % (w, None if un is None else [str(x) for x in un]))
        c3 = start(lc)
        K.check(c3["m"] == "" and snap(lc)["trees.properties"] == sc["trees.properties"] and c3["nums"][0] == 3, "MG %s: start 3 keeps the undone value (marker)" % w)
        K.check(open(tp, "rb").read() == live_before and snap(src) == live_snap, "MG %s: the LIVE folder was never written" % w)
    K.check(seen >= 1, "MG at least one live trees.properties copied (%d)" % seen)
    base_src = live_dir(LIVE_WORLDS[0])
    lb = open(os.path.join(base_src, "trees.properties"), "rb").read()
    # a CRLF file with one LF line, a hand edit, a numerically equal old value, a missing line, a doubled line, no final newline
    t = lb.decode("latin-1")
    t = t.replace("\nForaging.FFeller.tokens=3\n", "\nForaging.FFeller.tokens=2\n").replace("\nForaging.FCoins.per=0.002\n", "\nForaging.FCoins.per=0.0020\n")
    t = t.replace("\nForaging.FFeller.B=150000\n", "\n").replace("\n", "\r\n").replace("Foraging.FCoins.tokens=1\r\n", "Foraging.FCoins.tokens=1\n")
    t = t + "Foraging.FCoins.B=500"
    old = t.encode("latin-1")
    want = (t.replace("Foraging.FCoins.per=0.0020\r\n", "Foraging.FCoins.per=0.006\r\n").replace("Foraging.FCoins.tokens=1\n", "Foraging.FCoins.tokens=3\n")
            + "\r\n" + MARK + "\r\n").encode("latin-1")
    oc = case("odd", base_src, old)
    s0 = snap(oc)
    o = start(oc)
    so = snap(oc)
    K.check(so["trees.properties"] == want, "MG odd: CRLF kept, the LF line kept LF, only FCoins.tokens + FCoins.per (0.0020 = the old default) moved, CRLF + marker appended")
    nl = [l for l in so["config-changes.log"].decode("utf8")[len(s0.get("config-changes.log", b"").decode("utf8")):].split("\n") if "SkyyTrees 0.3.17" in l]
    K.eq([LOGRE.match(l).groups() if LOGRE.match(l) else l for l in nl], [("FCoins.tokens", "1", "3"), ("FCoins.per", "0.0020", "0.006")], "MG odd: 2 change-log lines")
    K.check("Foraging.FFeller.tokens=2 kept - an admin changed it" in o["m"] and "Foraging.FCoins.B=500 kept - the line is doubled" in o["m"],
            "MG odd: the hand edit and the doubled line are kept and named: %r" % o["m"][-400:])
    K.eq(o["nums"], (2, 100, 3, 500, 0.006), "MG odd: hand value 2 kept, missing FFeller.B = the built-in 100, doubled FCoins.B 500 kept")
    K.check(start(oc)["m"] == "" and snap(oc)["trees.properties"] == want, "MG odd: start 2 writes nothing")
    # already on the new values (no marker): only the marker line is added, no change-log line
    t2 = lb
    for k, o_, n in MOVES:
        t2 = t2.replace(("\n%s=%s\n" % (k, o_)).encode(), ("\n%s=%s\n" % (k, n)).encode())
    nc = case("new", base_src, t2)
    s0 = snap(nc)
    r = start(nc)
    sn = snap(nc)
    K.check(sn["trees.properties"] == t2 + MARK.encode() + b"\n" and "no cost line held the old default" in r["m"]
            and b"SkyyTrees 0.3.17" not in sn.get("config-changes.log", b"")[len(s0.get("config-changes.log", b"")):] and r["nums"] == NEW,
            "MG new values already: marker only, no change-log line: %r" % r["m"][:160])
    # the marker already there (a hand-added copy): nothing at all
    mc = case("marked", base_src, lb + MARK.encode() + b"\n")
    s0 = snap(mc)
    r = start(mc)
    K.check(r["m"] == "" and snap(mc)["trees.properties"] == lb + MARK.encode() + b"\n" and r["nums"] == OLDN, "MG marker present: never again (old values stay)")
    # a fresh server: the default file carries the marker - nothing to move
    fc = case("fresh", None, None)
    r = start(fc)
    f1 = open(os.path.join(fc, "trees.properties"), "rb").read()
    K.check(r["m"] == "" and f1 == str(r["C"]("TreeCfg").DEFAULTS).encode("utf8") and f1.count(MK317.encode()) == 1 and r["nums"] == NEW,
            "MG fresh: the default file (marker once, new costs), the update does nothing")
    s1 = snap(fc)
    K.check(start(fc)["m"] == "" and snap(fc) == s1, "MG fresh: a second start writes nothing")
    K.save()


def run_ct16(out, jar, scratch, home):
    """the 0.3.16 harness's CT phase on this jar (its module loads with this process's kit)"""
    sp = importlib.util.spec_from_file_location("test_skyytrees_0_3_16", os.path.join(HERE, "test_skyytrees_0.3.16.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.run_ct(out, jar, scratch, home)


def check_manifest():
    a = json.loads(zipfile.ZipFile(OLD_JAR).read("manifest.json"))
    b = json.loads(zipfile.ZipFile(JAR).read("manifest.json"))
    d = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    HK.check(d == ["Name", "Version"] and b["Version"] == VERSION and b["Name"] == VERSION + " SkyyTrees" and b.get("IncludesAssetPack") is True,
             "MF: the manifest = 0.3.16's but Name / Version (%s)" % d)


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        print("kit: " + KIT_NOTE)
        check_manifest()
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tb", run_tb), ("ly", run_ly), ("mg", run_mg), ("ct16", run_ct16)], script=__file__)
