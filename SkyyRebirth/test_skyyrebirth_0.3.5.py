"""SkyyRebirth 0.3.5 - harness for MENU PATTERN sweep S4 (tools/rebirth_0_3_5_patch.py): /rebirth on the kit 1.7 hub page (1600 x 980, row 1 +
row 2 with Character / Profiles selected, the ONE sub-tab row YOUR REBIRTH | TREE NODE, no Back button), layout only.
Build first: python tools/rebirth_0_3_5_patch.py && python SkyyRebirth/build_skyyrebirth_0.3.5.py

    python SkyyRebirth/test_skyyrebirth_0.3.5.py --dir <empty folder inside tools/dev/scratch/> [--keep]

  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.3.4 -> 0.3.5: exactly the planned members differ (RbPage build / handleDataEvent; the version texts), HubBar added; the
               jar's non-class entries = manifest.json + the kit's 59 Sky Window files
  P   page     THE REAL PAGE built (UICommandBuilder / UIEventBuilder) with the hubs + Character tabs on the bridge and without them, in the
               rebirth view (rebirth off / Rebirth offered) and the node view (Buy off / on): SUI.check_page, check_sky_paths, assert_menu_page
               (1600 x 980, rows 1 + 2, one sub row, no back / menu text inline or b.set, no pager, content fits) on every built page;
               row 1 = 8 hubs (Character selected), row 2 = the Character tabs (Profiles selected); every binding names an element; the
               exact bindings per view (88 nodes + Nexus + X + row 1 + row 2 + Close / Rebirth / Continue | YOUR REBIRTH / Buy); no Back
               button anywhere; the clicks: the X (hub:close), row 1 Character (self = the rebirth view, disarmed), row 2 Profiles (opens
               through its bridge Function), another hub, YOUR REBIRTH = back; the old actions unchanged (n<i>, back, nexus, buy, rbgo);
               THE FIT of every real node-view text at the new 456 px panel; the page packet < CustomPage.MAX_SIZE; the jar's kit art
  X   exec     test_skyyrebirth_0.3.py's exec phase (tree, markets, CONTINUE end to end, the Nexus click, Buy) with the 4-part World of
               test_skyyrebirth_0.3.2.py on this jar; expected deviations: the binding counts (+ the X / rows) and the FIT at 236 px
               (both re-checked at the new values in P)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.3.5"
RB = "com.skyy.rebirth."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRebirth-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRebirth-0.3.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS4", "rebirth", "rb")))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T32 = _load("t_rb032", os.path.join(HERE, "test_skyyrebirth_0.3.2.py"))
for _m in (T32, T32.T31, T32.T3, T32.T2):
    _m.VERSION = VERSION
    _m.JAR = JAR
T3, T2 = T32.T3, T32.T2
# the participant jars of the older harnesses (0.4.38 / 0.1.8 / ...) are long tidied away: the World runs on the CURRENT SET jars
# (tools/deploy_set.py SET, 2026-10-16) - a stronger check of the real pack
_J = lambda mod, v: os.path.join(ROOT, mod, "%s-%s.jar" % (mod, v))
T2.SK_JAR, T2.CO_JAR, T2.BK_JAR, T2.PF_JAR = _J("SkyySkills", "0.4.47"), _J("SkyyCoins", "0.1.9"), _J("SkyyBank", "0.1.16"), _J("SkyyProfiles", "0.1.16")
T3.AH_JAR, T3.BZ_JAR, T32.GEAR_JAR = _J("SkyyAuctions", "0.1.10"), _J("SkyyBazaar", "0.1.18"), _J("SkyyGear", "0.3.16")
CORE_JAR = _J("SkyyCore", "1.0.0")     # SkyyBank 0.1.14+ links against SkyyCore (com.skyy.core.Core): every child JVM's class path
os.environ["SKYY_HARNESS_CP"] = os.pathsep.join([p_ for p_ in os.environ.get("SKYY_HARNESS_CP", "").split(os.pathsep) if p_] + [CORE_JAR])

EXPECT = {
    "RbPage": ["~m build", "~m handleDataEvent"],                 # the hub page (rows 1 + 2, the sub row) + HubBar.route first
    "SkyyRebirthPlugin": ["~m setup"],                             # the ready line (version)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],             # the kit's version text
    "RbStore": ["~m writeNow"],                                    # the file comment's version
}
ADDED = ["HubBar"]
KIT_FILES = sorted(SUI.kit_texture_files())

# C: the jar now carries the kit's Sky Window art - the compare's non-class list is manifest.json + those 59 files
_orig_compare = HK.run_compare


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(["manifest.json"] + KIT_FILES)
        return orig_eq(self, got, want, what)
    HK.Child.eq = eq
    try:
        return _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = run_compare

# X: checks of test_skyyrebirth_0.3.py whose expected values changed ON PURPOSE (re-checked at the new values in phase P)
X03_DEV = {
    "PAGE view 0: 88 node bindings": "the binding count +1 (the hub page X) + row 1 / row 2",
    "Rebirth is switched off - only admins can buy while it is off.": "the node view binding count (+ X, rows; YOUR REBIRTH replaces Back)",
    "Press Buy to spend": "the node view binding count with Buy (+ X, rows)",
    "PAGE on + everything met": "the rebirth view binding count with Rebirth (+ X, rows)",
    "FIT:": "0.3.5 rows are sized for the 456 px panel (the old check measures at 236 px); P re-checks every text at 432 px",
}


def cmds_of(b):
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(getattr(c, n, None))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    out = []
    for e in list(ev.getEvents()):
        out.append((str(e.selector), str(getattr(e, "data", None))))
    return out


def unq(d):
    """a b.set value as text (the builder stores it JSON-encoded)"""
    if d is None:
        return ""
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def run_page(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    k = T2.U0
    W0 = T2.World(os.path.join(scratch, "w0"))
    CK = T2.Checker(K, W0)
    base = os.path.join(scratch, "page")
    T2.seed(base, k, CK.cls_total)
    W = T2.World(base)
    W.br.put("class:" + k, "Archer")
    HB = JClass(RB + "HubBar", loader=W.L)
    u = W.uuid(k)
    opened = []

    @JImplements("java.util.function.Function")
    class Opener(object):
        def __init__(self, tab):
            self.tab = tab

        @JOverride
        def apply(self, o):
            opened.append(self.tab)
            return JClass("java.lang.Boolean").TRUE

    def build(pg):
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        return b_, e_, cmds_of(b_), events_of(e_)

    def built(pg, what, rows):
        b_, e_, c, ev = build(pg)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t_) for ty, s_, t_, d_ in c if t_ is not None and ty and "Append" in ty])
        sets = [(s_, d_) for ty, s_, t_, d_ in c if ty == "Set"]
        try:
            SUI.check_page(apps, "Skyy")
            K.check(True, "P %s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as ex:
            K.check(False, "P %s: check_page: %s" % (what, ex))
        try:
            SUI.check_sky_paths(apps, tab_icons=True)
            allp = [m_.group(0) for mk in apps.markups() for m_ in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
            K.check(not [p_ for p_ in allp if p_.startswith('"../')], "P %s: kit textures only, no path leaves Common/UI/Custom (%d)" % (what, len(allp)))
        except Exception as ex:
            K.check(False, "P %s: sky paths: %s" % (what, ex))
        try:
            info = SUI.assert_menu_page(apps, hub="character", what="P " + what, sets=[(s_, unq(d_)) for s_, d_ in sets])
            K.check(info["rows"] == 2 and info["subs"] == 1, "P %s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button, no pager)"
                    % (what, info["rows"], info["subs"]))
        except Exception as ex:
            K.check(False, "P %s: assert_menu_page: %s" % (what, ex))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_, _d in ev if s_.lstrip("#") not in ids]
        K.check(not bad, "P %s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(ev), bad[:4]))
        texts = [t_ for _ty, _s, t_, _d in c if t_] + [d_ for _s, d_ in sets if d_]
        K.check(not any("SkyyRbBack" in t_ for t_ in texts) and not any(re.search(r'Text: "(< ?)?(Back|Go Back|< ?Menu)"', t_) for t_ in texts),
                "P %s: no Back / < Menu button" % what)
        nrow1 = len([1 for t_ in texts if re.search(r"Button #SkyyRbBigR\d+ ", t_)])
        nrow2 = len([1 for t_ in texts if re.search(r"Button #SkyyRbBigT\d+ ", t_)])
        K.check((nrow1, nrow2) == rows, "P %s: row 1 has %d hub buttons, row 2 %d tabs (want %s)" % (what, nrow1, nrow2, rows))
        return c, ev, sets, b_, e_

    def binds(ev):
        return sorted(s_.lstrip("#") for s_, _d in ev)

    nodes = ["SkyyRbN%dB" % i for i in range(88)]
    # ---------------------------------------------------------------- 1. no hub data on the bridge (SkyyMenu absent): the shell still draws rows 1 + 2
    W.Cfg.ON = False
    pg = W.Page(u, "hub")
    c0, ev0, _s0, _b0, _e0 = built(pg, "rebirth view, no hub data", (0, 0))
    K.eq(binds(ev0), sorted(nodes + ["SkyyRbNexusB", "SkyyRbClose", "SkyyRbHubClose"]), "P rebirth view (off, no hubs): the bindings")
    K.check(any(t_ and "Label #SkyyRbBigRowT" in t_ for _ty, _s, t_, _d in c0), "P without SkyyMenu row 1 shows the hub title (kit)")
    # ---------------------------------------------------------------- 2. the hubs + the Character tabs on the bridge (what SkyyMenu + the mods put)
    for hid in SUI.HUB_ROW_IDS:
        HB.def4(hid, SUI.hub_title_now(hid) if hid != "home" else "Home", hid if hid != "home" else "skymenu", "Skyy_Menu", None)
    O, I, S_ = JClass("java.lang.Object"), JClass("java.lang.Integer"), JClass("java.lang.String")
    from jpype import JArray
    tabs = [r[0] for r in SUI.hub_page_tabs("character")]
    for i_, t_ in enumerate(tabs):
        W.br.put("hub:tab:character:" + t_, JArray(O)([S_("Skyy" + t_), S_(SUI.hub_tab_label("character", t_)), I(10 * (i_ + 1)), S_(t_), Opener(t_), None]))
    pg = W.Page(u, "hub")
    c1, ev1, s1, b1, e1 = built(pg, "rebirth view (off)", (8, len(tabs)))
    rowb = ["SkyyRbBigR%d" % i for i in range(8)] + ["SkyyRbBigT%d" % i for i in range(len(tabs))]
    K.eq(binds(ev1), sorted(nodes + ["SkyyRbNexusB", "SkyyRbClose", "SkyyRbHubClose"] + rowb), "P rebirth view (off): 88 nodes + Nexus + Close + X + rows")
    sel_r = [t_ for _ty, _s, t_, _d in c1 if t_ and re.search(r"Button #SkyyRbBigR1 ", t_)]
    sel_t = [t_ for _ty, _s, t_, _d in c1 if t_ and re.search(r"Button #SkyyRbBigT%d " % tabs.index("profiles"), t_)]
    sel_o = [t_ for _ty, _s, t_, _d in c1 if t_ and re.search(r"Button #SkyyRbBigT0 ", t_)]
    K.check(sel_r and sel_t and sel_o and sel_t[0].split("{", 1)[1] != sel_o[0].split("{", 1)[1], "P row 2: Profiles drawn selected (its style differs from Skills)")
    evd = dict((s_.lstrip("#"), d_) for s_, d_ in ev1)
    K.check("hub:h:character" in evd.get("SkyyRbBigR1", "") and "hub:profiles" in evd.get("SkyyRbBigT%d" % tabs.index("profiles"), "")
            and "hub:close" in evd.get("SkyyRbHubClose", ""), "P row 1 Character = hub:h:character, row 2 Profiles = hub:profiles, the X = hub:close: %s"
            % [evd.get("SkyyRbBigR1"), evd.get("SkyyRbHubClose")])
    sub = [t_ for _ty, s_, t_, _d in c1 if t_ and s_ == "#SkyyRbSub"]
    K.check(len([x for x in sub if "TextButton #SkyyRbSub0" in x]) == 1 and not any("SkyyRbSub1" in x for x in sub) and any("SkyyRbHint" in x for x in sub),
            "P rebirth view sub row: YOUR REBIRTH (selected) + the hint line, no TREE NODE")
    K.check(any(s_ == "#SkyyRbHint.Text" and "levels in a row open the next row" in str(d_) for s_, d_ in s1), "P the hint line = the live footer text (tree.rowNeed)")
    hint_set = [d_ for s_, d_ in s1 if s_ == "#SkyyRbHint.Text"]
    # the X / row 1 / row 2 clicks (test mode: nothing closes)
    pg.handleDataEvent(None, None, '{"a":"hub:close"}')
    K.check(str(pg.last) == "=hub close" and not pg.gone, "P the X = HubBar close (test mode: the page stays) (%s)" % pg.last)
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    K.check(int(pg.view) == 1 and int(pg.sel) == 25, "P a node click opens the node view (unchanged)")
    c2, ev2, s2, _b2, _e2 = built(pg, "node view (off)", (8, len(tabs)))
    K.eq(binds(ev2), sorted(nodes + ["SkyyRbNexusB", "SkyyRbSub0", "SkyyRbHubClose"] + rowb), "P node view (off, no Buy): 88 nodes + Nexus + YOUR REBIRTH + X + rows")
    K.check("\"back\"" in dict(ev2).get("#SkyyRbSub0", "") or "back" in dict((s_.lstrip("#"), d_) for s_, d_ in ev2).get("SkyyRbSub0", ""),
            "P YOUR REBIRTH sends back (0.3.4's Back button)")
    sub2 = [t_ for _ty, s_, t_, _d in c2 if t_ and s_ == "#SkyyRbSub"]
    K.check(any("TextButton #SkyyRbSub1" in x and "Tree node" in x for x in sub2) and any("TextButton #SkyyRbSub0" in x for x in sub2), "P node view sub row: YOUR REBIRTH | TREE NODE")
    pg.handleDataEvent(None, None, '{"a":"hub:h:character"}')
    K.check(str(pg.last) == "=hub self" and int(pg.view) == 0 and int(pg.sel) == -1 and int(pg.armedAt) == 0, "P row 1 Character = self = the rebirth view (%s)" % pg.last)
    pg.handleDataEvent(None, None, '{"a":"hub:profiles"}')
    K.check(str(pg.last) == "=hub bridge" and opened == ["profiles"], "P row 2 Profiles opens the Profiles page through its bridge Function (%s, %s)" % (pg.last, opened))
    pg.handleDataEvent(None, None, '{"a":"hub:skills"}')
    K.check(str(pg.last) == "=hub bridge" and opened == ["profiles", "skills"], "P row 2 Skills opens Skills (%s)" % opened)
    pg.handleDataEvent(None, None, '{"a":"hub:h:market"}')
    K.check(str(pg.last).startswith("=hub ") and int(pg.view) == 0, "P row 1 another hub goes through HubBar.goHub (%s)" % pg.last)
    pg.handleDataEvent(None, None, '{"a":"n25"}')
    pg.handleDataEvent(None, None, '{"a":"back"}')
    K.check(int(pg.view) == 0 and int(pg.sel) == -1, "P back (YOUR REBIRTH) = the rebirth view (unchanged action)")
    # ---------------------------------------------------------------- 3. rebirth ON + every requirement met: Rebirth offered; Buy offered in the node view
    W.Cfg.ON = True
    W.Cfg.HUB_TEST = "hub"
    T3.write_rb(base, k, dict([("n", 0)] + [("pts." + a_, 500) for a_ in T3.ARMS]))
    W.Sto.CACHE.clear()
    now = int(JClass("java.lang.System").currentTimeMillis())
    bz0, bz1 = T3.bazaar_fns()
    W.br.put("bazaar:fn:closeall", bz0)
    W.br.put("bazaar:fn:wouldclose", bz1)
    for nm_, kinds_, want_gk, btn in (("ah_close", ["closable"], 2, "SkyyRbCont"), ("ah_ok", [], 1, "SkyyRbGo")):
        a_ = T3.ah_world(os.path.join(base, "Skyy_SkyyAuctions_" + nm_), T3.ah_recs(k, now, kinds_))
        W.br.put("ah:fn:closeall", a_.Fn(0))
        W.br.put("ah:fn:wouldclose", a_.Fn(1))
        pg = W.Page(u, "hub")
        c3, ev3, _s3, _b3, _e3 = built(pg, "rebirth view (on, %s)" % nm_, (8, len(tabs)))
        gk = int(pg.goKind)
        K.check(gk == want_gk, "P rebirth view (on, %s): goKind %d (want %d): %s" % (nm_, gk, want_gk, [str(x) for x in pg.rt]))
        K.eq(binds(ev3), sorted(nodes + ["SkyyRbNexusB", "SkyyRbClose", "SkyyRbHubClose", btn] + rowb), "P rebirth view (on, %s): + %s bound" % (nm_, btn))
        t1 = int(JClass("java.lang.System").currentTimeMillis())
        K.check(str(pg.click(t1, "hub", gk == 2)) == "=armed" and str(pg.click(t1 + 300, "hub", gk == 2)) == "=armed",
                "P %s: the first press arms, a double click (< 0.8 s) does not confirm (unchanged)" % btn)
        pg.handleDataEvent(None, None, '{"a":"hub:h:character"}')
        K.check(int(pg.armedAt) == 0 and int(pg.view) == 0, "P %s: a row 1 Character click disarms (like Back)" % btn)
    pg.handleDataEvent(None, None, '{"a":"n22"}')
    c4, ev4, _s4, _b4, _e4 = built(pg, "node view (on)", (8, len(tabs)))
    K.eq(binds(ev4), sorted(nodes + ["SkyyRbNexusB", "SkyyRbSub0", "SkyyRbHubClose"] + rowb + (["SkyyRbBuy"] if pg.canBuy else [])),
         "P node view (on, canBuy %s): the bindings" % bool(pg.canBuy))
    K.check(bool(pg.canBuy), "P node view: Buy offered with 500 points (%s)" % pg.nvStatus)
    pg.handleDataEvent(None, None, '{"a":"buy"}')
    p_ = T2.props(T3.rb_file(base, k))
    K.check(p_.get("node.Mining.xp") == "1" and str(pg.status).startswith("+"), "P Buy (unchanged): a level bought inline (%s)" % pg.status)
    # ---------------------------------------------------------------- 4. THE FIT: every node-view text at the 456 px panel (inner 432)
    heights = {}
    for view in ("n25", "back"):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % view)
        _b, _e, cc, _ev = build(pg)
        for _ty, _s, tx, _d in cc:
            for m_ in re.finditer(r"Label #(SkyyRb(?:Nv\w+|Pt\d|Req\d|Note|Extra|Arm\d)) \{ Anchor: \(([^)]*)\)", tx or ""):
                hm = re.search(r"Height: (\d+)", m_.group(2))
                if hm:
                    heights[m_.group(1)] = int(hm.group(1))
    SZ = {"SkyyRbNvName": (16, True), "SkyyRbNvSub": (13, True), "SkyyRbNvLive": (12, False), "SkyyRbNvLevel": (14, True), "SkyyRbNvNow": (13, False),
          "SkyyRbNvNext": (13, False), "SkyyRbNvCost": (14, False), "SkyyRbNvHave": (14, False), "SkyyRbNvRow": (13, False), "SkyyRbNvStatus": (13, True)}
    SZ.update(dict(("SkyyRbPt%d" % i_, (13, False)) for i_ in range(8)))
    texts = []
    T3.write_rb(base, k, dict([("n", 10), ("title", "x")] + [("pts." + a_, 999999999) for a_ in T3.ARMS]))
    JP = JClass("java.util.Properties")
    ids = [str(x) for x in JClass(RB + "RbTree", loader=W.L).NID]
    NMAX = JClass(RB + "RbTree", loader=W.L).NMAX
    W.Cfg.DUST_NODE = 5.0
    for idx in range(88):
        for l in range(int(NMAX[idx]) + 1):
            pp = JP()
            for a_, b_ in [("n", 10)] + [("pts." + a_, 999999999) for a_ in T3.ARMS] + [("node." + ids[idx], l)]:
                pp.setProperty(a_, str(b_))
            W.Sto.CACHE.put(k, pp)
            pg.sel = idx
            pg.view = 1
            pg.status = None
            pg.build(None, UCB(), UEB(), None)
            for fld in ("nvName", "nvSub", "nvLive", "nvLevel", "nvNow", "nvNext", "nvCost", "nvHave", "nvRow", "nvStatus"):
                texts.append(("SkyyRb" + fld[0].upper() + fld[1:], str(getattr(pg, fld))))
            texts += [("SkyyRbPt%d" % i_, str(x)) for i_, x in enumerate(pg.pt)]
    W.Cfg.DUST_NODE = 0.25
    over = []
    for rid, tx in texts:
        if not tx or rid not in heights or rid not in SZ:
            continue
        sz, bd = SZ[rid]
        lines = SUI.text_lines(tx, SUI.DETAIL_W - 24, SUI.fs(sz), bold=bd)
        if lines * SUI.line_height(SUI.fs(sz), bold=bd) > heights[rid] + 0.5:
            over.append((rid, tx, lines, heights[rid]))
    K.check(not over and len(texts) > 4000 and len([h for h in heights if h.startswith("SkyyRbNv")]) == 11,
            "P FIT: %d real node-view texts fit their rows at the 456 px panel: %s" % (len(texts), over[:3]))
    # ---------------------------------------------------------------- 5. the page packet + the jar's kit art
    CP = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPage")
    LIFE = JClass("com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime")
    sizes = []
    for view in ("back", "n32"):
        pg.handleDataEvent(None, None, '{"a":"%s"}' % view)
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        sizes.append(int(CP("SkyyRb", True, True, LIFE.CanDismiss, b_.getCommands(), e_.getEvents()).computeSize()))
    K.check(max(sizes) < int(CP.MAX_SIZE), "P packet: rebirth view %d / node view %d bytes < CustomPage.MAX_SIZE %d" % (sizes[0], sizes[1], int(CP.MAX_SIZE)))
    K.notes.append("P packet sizes: rebirth view %d, node view %d of %d" % (sizes[0], sizes[1], int(CP.MAX_SIZE)))
    try:
        n_kit = SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", "Frame_Character", "Tertiary"))
        K.check(n_kit == 59, "P the jar carries the kit's 59 Sky Window files (sha256 pinned)")
    except Exception as ex:
        K.check(False, "P the jar's kit art: %s" % ex)
    import zipfile
    man = json.loads(zipfile.ZipFile(jar).read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "P manifest: IncludesAssetPack true, version %s" % man.get("Version"))
    K.save()


if __name__ == "__main__":
    if "--phase" in sys.argv and HK.arg("--phase") == "treekiller":
        T3.run_treekiller(None, JAR, SCRATCH, None)
        sys.exit(0)
    for j_ in (T2.SK_JAR, T2.CO_JAR, T2.BK_JAR, T2.PF_JAR, T3.AH_JAR, T3.BZ_JAR, T32.GEAR_JAR, OLD_JAR):
        assert os.path.isfile(j_), j_
    HK.run(name="SkyyRebirth", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=RB, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("page", T32.sub(run_page, "p")), ("exec", T32.sub(T32.dev(T3.run_exec, X03_DEV), "x3"))],
           script=__file__)
