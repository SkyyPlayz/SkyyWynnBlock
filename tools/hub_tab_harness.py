"""hub_tab_harness - the HUBS H3 tab phases every H3b / H3c / H3d harness repeats (SkyyBazaar 0.1.13, SkyyAuctions 0.1.8, SkyyMerchants
0.1.5, SkyyParty 0.1.8, SkyyGuilds 0.1.9, SkyyIslands 0.5.14, SkyyExploration 0.2.10, SkyyHud 0.3.26, SkyyVault 0.1.7, SkyyBank 0.1.13).
Built on tools/harness_kit.py (verify / compare / engine-access audit, fresh child JVMs, scratch only under tools/dev/scratch/) and the
SkyyMenu 0.3.19 harness's 0.7 engine stand-ins (SkyyMenu/test_skyymenu_0.3.19.py engine(): a recording packet sink, a component store,
worlds, the Universe, the REAL PageManager / WindowManager, a command manager that records lines, a permissions provider).

A per-mod harness builds a Spec and calls run(spec). Phases (each in its own child JVM):
  A    verify   every class of the jar loads + initialises with -Xverify:all
  C    compare  old -> new: exactly the expected members differ, the added classes are listed; non-class entries: manifest.json + the 59
                Sky Window kit files (+ spec.extra_entries), each = the kit's pinned bytes
  HUB  EXECUTED with -Xverify:all over the engine stand-ins:
       REG   the plugin's register path puts hub:tab:<hub>:<tab> = Object[]{ mod, label, Integer order, command, open Function, visible
             Function or null } exactly as tools/skyyui.py HUB_TABS says; the visible Function answers as specified; the open Function
             refuses junk (not a UUID, an offline player)
       PAGE  HubBar.open(...) through the open Function ("bridge") opens the page class in the REAL PageManager; the page built into a REAL
             UICommandBuilder / UIEventBuilder is a Sky Window hub page: root = the shell, markup rules + parents + no duplicate id
             (SUI.check_page), only kit SkyyKit textures inside Common/UI/Custom (no ../), Header + crest + the hub frame + close X +
             "< Menu" INSIDE the title bar, assert_hub_page (fits 1080p) + assert_hub_fits, the body under the strip fits, one tab button per
             visible tab at hub_tab_width (>= 110, 16 px labels shrinking to 12), the active tab selected, every binding (hub:back /
             hub:close / hub:<tab>) and every b.set names an element that exists, hub:last remembers the tab
       CLICK the page's own tab (same page, ANSWERED), a missing / hidden tab (the page says it could not open), another tab with a
             bridge Function (called with the player's UUID; one that answers TRUE without a page -> this page is ANSWERED; one that
             replaces this page -> NOTHING more is sent to the old page), another tab with only a command (the command runs as the
             player; the page is ANSWERED), "< Menu" without SkyyMenu (closes) and with it (/skymenu runs; ANSWERED), the X (closes);
             non-hub clicks still reach the page (spec.clicks). ANSWERED (review fix 2026-10-15: every handled click is answered, or the
             client stays on "Loading...") = a packet carrying spec.ack_mark (default the hub title set to itself, #<prefix>Title.Text)
       DROP  HubBar.removeAll removes only OUR array (a replaced key and another mod's key stay); setup() calls the register path and
             shutdown() calls HubBar.removeAll (bytecode)
  D    live     two opens of the page on a scratch COPY of the live data folder (the mod's statics pointed at the copy): built, clicked,
                nothing written by either
  AA   engine-access audit
2026-10-15 (SkyyCore pilots): a Spec may say hub_class="com.skyy.core.ui.HubBar" + hub_owner="<Mod>" (the module uses SkyyCore's ONE
HubBar: removeAll(owner)), kit_in_jar=False (the jar ships no kit art - SkyyCore does; KITBYTES then checks the manifest's stable name
+ Skyy:SkyyCore dependency and that the jar has no kit file), removed=[...] (classes the compare expects gone) and extra_phases
[(label, fn(out, jar, scratch, home))]. The defaults keep every older harness exactly as it was.
"""
import os, sys, re, json, shutil, zipfile, importlib.util

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s19 = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
T19 = importlib.util.module_from_spec(_s19)
_s19.loader.exec_module(T19)

KIT_FILES = sorted(SUI.SKY_JAR_DIR + f[0] for f in SUI.SKY_FILES)
LIVE_ROOT = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods")
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")
WH_RE = re.compile(r"Anchor: \(Width: (\d+), Height: (\d+)\)")


class Spec(object):
    """name, version, old_version, pkg ("com.skyy.x."), hub, tab, mod (the registry's mod name), open_cls, vis_cls (None = always),
    page_cls, prefix (the hub shell prefix), idp (the page's id prefix), register(J) -> int, vis_cases(K, E, J, vis) (optional),
    prep(E, J, home) (point the mod's statics at home; no threads), expect / added (the class compare), extra_entries (non-class jar
    entries that changed besides manifest + kit), clicks [(json data, check(K, E, P, page_before, page_after, what))] (optional),
    plugin_cls, register_call (the method name setup() must invoke), drop_call (shutdown() must invoke), live (the live folder name)"""

    def __init__(self, **kw):
        self.vis_cls = None
        self.vis_cases = None
        self.extra_entries = []
        self.clicks = []
        self.drop_call = "HubBar.removeAll"
        self.after_open = None
        self.fail_text = "could not open right now"
        self.self_redraw = False
        self.ack_mark = None          # None = "#<prefix>Title.Text" (hubAck); else the selector the page's own answer sets
        self.replace_prep = None      # (J, on): makes the page's own open Function REPLACE the page for the "replaced" click check
        self.hub_class = None         # 2026-10-15: None = <pkg>HubBar (the jar's own); "com.skyy.core.ui.HubBar" = SkyyCore's
        self.hub_owner = None         # SkyyCore's HubBar: removeAll(<owner>)
        self.kit_in_jar = True        # False = SkyyCore ships the kit art (KITBYTES checks the jar has none + the Core dependency)
        self.removed = []
        self.extra_phases = []
        self.__dict__.update(kw)
        row = [r for r in SUI.HUB_TABS if r[0] == self.hub and r[1] == self.tab]
        assert len(row) == 1, (self.hub, self.tab)
        _h, _t, self.order, owner, self.label, self.cmd = row[0]
        assert owner == self.mod, (owner, self.mod)


def jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def cmds_of(b):
    """the commands of a real UICommandBuilder: [(type, selector or None, text, data)]"""
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(jf(c.getClass(), n).get(c))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    """every binding of a UIEventBuilder as (selector, the binding's text)"""
    from jpype import JClass
    out = []
    Coll = JClass("java.util.Collection")
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is None or not Coll.class_.isInstance(v_):
            continue
        for e in list(v_):
            sel, parts = None, []
            c = e.getClass()
            while c is not None and str(c.getName()) != "java.lang.Object":
                for g in c.getDeclaredFields():
                    try:
                        g.setAccessible(True)
                        x = g.get(e)
                        if x is None:
                            continue
                        if str(g.getName()) == "selector":
                            sel = str(x)
                        parts.append(str(x))
                        for h in x.getClass().getDeclaredFields():
                            try:
                                h.setAccessible(True)
                                y = h.get(x)
                                if y is not None:
                                    parts.append(str(y))
                            except Exception:
                                pass
                    except Exception:
                        pass
                c = c.getSuperclass()
            out.append((sel, " | ".join(parts)))
    return out


def _blank(mk, texts):
    for t in texts:
        mk = mk.replace('"%s"' % t, '"x"')
    return mk


def page_check(K, E, S, P, page, hb, what):
    """build the page into REAL builders and check it as a hub page (PAGE in the module docstring); returns (cmds, events)"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = cmds_of(b)
    evs = events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets (%s)" % (what, len(apps), len(sets),
            sorted(set(ty for ty, _s, _t, _d in cmds))))
    legacy = list(getattr(S, "legacy_texts", []))
    capps = apps
    if legacy:
        # texts the page carried LIVE before this round (hand-made markup, seen in game): blanked for the kit's stricter text rule only;
        # ids, parents, duplicates and every other markup rule are still checked
        capps = SUI.Appends([(p, SUI.render(mk).replace('"%s"' % legacy[0], '"x"') if len(legacy) == 1 else
                              _blank(SUI.render(mk), legacy)) for p, mk in apps])
    try:
        SUI.check_page(capps, S.idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)%s" % (what, " - legacy texts blanked: %s" % legacy if legacy else ""))
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    nvis = len(list(hb.tabs(S.hub, P.pr.getUuid())))
    try:
        els = SUI.check_sky_paths(apps)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
        need = {"Header", "HeaderOrnament", SUI.HUB_FRAME[S.hub], "Close", "Tertiary", "Tab_Selected"} | ({"Tab"} if nvis > 1 else set())
        K.check(need <= set(els), "%s: the Sky Window shell: Header + crest + %s + close X + < Menu + tabs (%s)" % (what, SUI.HUB_FRAME[S.hub], els))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    m = WH_RE.search(root)
    w, h = int(m.group(1)), int(m.group(2))
    K.check(apps[0][0] is None and root.startswith("Group #%s " % S.prefix), "%s: the root is the hub shell #%s" % (what, S.prefix))
    strip = w - 2 * 24
    try:
        SUI.assert_page_size(w, h)
        K.eq(SUI.assert_hub_page(w, h - SUI.HUB_BAR_H, old_title_h=0, hub=S.hub, pad=24), (w, h), "%s: assert_hub_page %d x %d (fits 1080p)" % (what, w, h))
        K.check(SUI.assert_hub_fits(S.hub, strip) >= 110, "%s: assert_hub_fits %s in %d px (every contract tab)" % (what, S.hub, strip))
    except Exception as e:
        K.check(False, "%s: page size: %s" % (what, e))
    bid = [DECL_RE.search(mk).group(2) for p, mk in apps if p == S.prefix and "Anchor: (Top: 38)" in mk]
    K.check(len(bid) == 1, "%s: one body under the title bar (%s)" % (what, bid))
    if bid:
        try:
            used = SUI.used_height(apps, bid[0])
            K.check(used <= h - SUI.TITLE_H - 48, "%s: the body content fits (strip + content %d <= %d)" % (what, used, h - SUI.TITLE_H - 48))
            K.check([mk for p, mk in apps if p == bid[0]][0].startswith("Group #%sHubTabs " % S.prefix),
                    "%s: the tab strip is the body's FIRST child" % what)
        except Exception as e:
            K.check(False, "%s: used_height: %s" % (what, e))
    bar = [mk for p, mk in apps if p == S.prefix + "Bar"]
    K.check(any(("#%sHubMenu " % S.prefix) in mk and '"< Menu"' in mk for mk in bar), "%s: < Menu sits INSIDE the title bar #%sBar" % (what, S.prefix))
    K.check([p for p, mk in apps if ("#%sHubClose " % S.prefix) in mk] == [S.prefix], "%s: the close X in the root" % what)
    barmk = [mk for p, mk in apps if ("Group #%sBar " % S.prefix) in mk]
    K.check(len(barmk) == 1 and ('Text: "%s"' % SUI.HUB_DEFS[S.hub][0]) in barmk[0], "%s: the hub title %s in the title bar" % (what, SUI.HUB_DEFS[S.hub][0]))
    tabs = [mk for p, mk in apps if p == S.prefix + "HubTabs" and mk.startswith("TextButton")]
    vis = [str(r[0]) for r in hb.tabs(S.hub, P.pr.getUuid())]
    K.eq(len(tabs), len(vis), "%s: one tab per visible tab %s" % (what, vis))
    tw = SUI.hub_tab_width(strip, max(1, len(vis)))
    K.check(all(("Width: %d, Height: 44" % tw) in mk and "ShrinkTextToFit: true" in mk and "MinShrinkTextToFitFontSize: 12" in mk
                and "FontSize: 16" in mk for mk in tabs) and tw >= 110, "%s: tabs %d px wide (>= 110), 16 px labels that shrink to 12" % (what, tw))
    sel = [mk for mk in tabs if "Tab_Selected" in mk]
    K.check(len(sel) == 1 and ('Text: "%s"' % S.label) in sel[0], "%s: the active tab %s is selected" % (what, S.label))
    bs = [s for s, _t in evs]
    K.check(any("hub:back" in t for s, t in evs if s == "#%sHubMenu" % S.prefix) and any("hub:close" in t for s, t in evs if s == "#%sHubClose" % S.prefix),
            "%s: < Menu = hub:back, the X = hub:close" % what)
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sHubT%d" % (S.prefix, k)), "%s: tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == S.tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, S.tab))
    return cmds, evs


def hub_of(S, J):
    """the HubBar class the page uses: the jar's own (<pkg>HubBar) or SkyyCore's (S.hub_class)"""
    from jpype import JClass
    return JClass(S.hub_class) if S.hub_class else J("HubBar")


def drop_all(S, HB):
    """HubBar.removeAll() of the jar's own class / removeAll(owner) of SkyyCore's shared one"""
    return HB.removeAll(S.hub_owner) if S.hub_class else HB.removeAll()


def calls_of(jar, cname, mname):
    """the method calls (Class.method) in one method's bytecode (javassist InstructionPrinter)"""
    from jpype import JClass
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    cc = CP.get(cname)
    out = set()
    for m in cc.getDeclaredMethods():
        if str(m.getName()) != mname:
            continue
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        it = ca.iterator()
        while it.hasNext():
            pos = it.next()
            ln = str(IP.instructionString(it, pos, mi.getConstPool()))
            mm = re.match(r"invoke\w+ (?:#\d+ = )?(?:Method|InterfaceMethod) ([\w.$]+)\.(\w+)\(", ln)
            if mm:
                out.add(mm.group(1).rsplit(".", 1)[-1] + "." + mm.group(2))
    return out


class World(object):
    pass


def boot(scratch, jar, label):
    """the JVM (-Xverify:all) + the engine stand-ins + two players in the Universe; returns W (E, J, players, HubBar, bridge)"""
    from jpype import JClass
    hcls = os.path.join(scratch, "hcls_" + label)
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    W = World()
    W.E = E
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = UniC.get()
    byU = jf(UniC.class_, "playersByUuid").get(uni)

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    W.mkp = mkp
    W.P = mkp(E.PLAIN, "SkyyPlain")
    W.O = mkp(E.OP, "SkyyOp")
    return W


def run_hub(S, out, jar, scratch):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    W = boot(scratch, jar, "hub")
    E = W.E
    J = lambda n: JClass(S.pkg + n)
    home = os.path.join(scratch, "home_hub")
    os.makedirs(home, exist_ok=True)
    HB = hub_of(S, J)
    E.br = HB.map()
    _sb = JClass("java.lang.System").getProperties().get("skyy.bridge")
    K.check(E.br is not None and int(JClass("java.lang.System").identityHashCode(E.br)) == int(JClass("java.lang.System").identityHashCode(_sb)),
            "the kit HubBar uses skyy.bridge")
    S.prep(E, J, home)
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    Fn = JClass("java.util.function.Function")
    P, O = W.P, W.O
    u = P.pr.getUuid()
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())

    # ---------------------------------------------------------------- REG
    n = int(S.register(J))
    K.eq(n, 1, "REG: the register path put the tab")
    key = "hub:tab:%s:%s" % (S.hub, S.tab)
    e = E.br.get(key)
    ok = (e is not None and len(e) == 6 and str(e[0]) == S.mod and str(e[1]) == S.label and JClass("java.lang.Integer").class_.isInstance(e[2])
          and int(e[2]) == S.order and (str(e[3]) if e[3] is not None else None) == S.cmd and Fn.class_.isInstance(e[4])
          and str(e[4].getClass().getName()) == S.pkg + S.open_cls
          and ((e[5] is not None and str(e[5].getClass().getName()) == S.pkg + S.vis_cls) if S.vis_cls else e[5] is None))
    K.check(ok, "REG: %s = {%s, %s, %d, %s, %s, %s}" % (key, S.mod, S.label, S.order, S.cmd, S.open_cls, S.vis_cls or "null"))
    if e is None:
        K.save()
        return
    opn, vis = e[4], e[5]
    K.check(opn.apply("not a uuid") == FALSE and opn.apply(E.UUID.randomUUID()) == FALSE,
            "OPEN: not a UUID / an offline player = FALSE (the bar then runs %s)" % S.cmd)
    if S.vis_cls:
        K.check(vis.apply(u) == TRUE, "VIS: %s shows the tab by default" % S.vis_cls)
        if S.vis_cases:
            S.vis_cases(K, E, J, vis, u)
    K.eq([str(x[0]) for x in HB.tabs(S.hub, u)], [S.tab], "VIS: HubBar.tabs(%s) = our tab only (no other mod loaded)" % S.hub)

    # ---------------------------------------------------------------- PAGE (through the bar's open path: the bridge Function)
    def openp(X):
        r = str(HB.open(X.pr, X.pr.getUuid(), S.hub, S.tab))
        E.pump(X)
        return r, X.pm.getCustomPage()
    r, pg = openp(P)
    K.check(r == "bridge" and pg is not None and str(pg.getClass().getName()) == S.pkg + S.page_cls,
            "PAGE: HubBar.open(%s, %s) = %s -> %s" % (S.hub, S.tab, r, None if pg is None else pg.getClass().getSimpleName()))
    if pg is None or str(pg.getClass().getName()) != S.pkg + S.page_cls:
        K.notes.append("PAGE: lines %s, sent %s" % (list(E.CM.lines), E.kinds(P)[-5:]))
        K.save()
        return
    if S.after_open:
        S.after_open(K, E, J, P, pg)
    page_check(K, E, S, P, pg, HB, "PAGE")
    # with the other contract tabs of the hub registered (as when every hub mod is loaded): one button each, ours selected
    others = [(t, o, m_, l, c) for t, o, m_, l, c in SUI.hub_tabs(S.hub) if t != S.tab]

    @JImplements("java.util.function.Function")
    class Rec:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    recs = {}
    for t, o, m_, l, c in others:
        recs[t] = Rec(TRUE)
        E.br.put("hub:tab:%s:%s" % (S.hub, t), jpype.JArray(JClass("java.lang.Object"))([m_, l, JClass("java.lang.Integer")(o), c, recs[t], None]))
    page_check(K, E, S, P, pg, HB, "PAGE (full hub)")

    # ---------------------------------------------------------------- CLICK
    def click(X, page, a):
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        E.pump(X)
        return X.pm.getCustomPage()

    same = lambda a, b_: a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))
    mark = S.ack_mark or ("#%sTitle.Text" % S.prefix)
    answered = lambda n: len(E.sent(P)) > n and mark in E.strs_of(P, n)
    n0 = len(E.sent(P))
    p2 = click(P, pg, "hub:" + S.tab)
    K.check(same(p2, pg) and (len(E.sent(P)) > n0 if S.self_redraw else answered(n0)),
            "CLICK: the page's own tab keeps the page and answers it (%s; %d packets)" % ("redraws" if S.self_redraw else mark, len(E.sent(P)) - n0))
    if others:
        t, o, m_, l, c = others[0]
        n1 = len(E.sent(P))
        p3 = click(P, pg, "hub:" + t)
        K.check(recs[t].calls == [str(u)], "CLICK: another tab (%s) opens through its bridge Function with the player's UUID (%s)" % (t, recs[t].calls))
        K.check(same(p3, pg) and answered(n1), "CLICK: a Function that answered TRUE but opened no page (as the Vault refusal) -> this page is answered (%s)" % mark)
        r2, pg = openp(P)

    # a tab whose Function REPLACES this page (here: our own open Function, a fresh page): nothing more goes to the old page
    @JImplements("java.util.function.Function")
    class Reopen:
        @JOverride
        def apply(self, o):
            return opn.apply(o)
    E.br.put("hub:tab:%s:zzopen" % S.hub, jpype.JArray(JClass("java.lang.Object"))(["SkyyTest", "Reopen", JClass("java.lang.Integer")(94), "zzopencmd", Reopen(), None]))
    if S.replace_prep:
        S.replace_prep(J, True)       # (SkyyVault: chest mode - its page-mode open re-shows the SAME page instead of replacing it)
    n6 = len(E.sent(P))
    p6 = click(P, pg, "hub:zzopen")
    E.pump(P)
    if S.replace_prep:
        S.replace_prep(J, False)
    K.check(p6 is not None and not same(p6, pg) and str(p6.getClass().getName()) == S.pkg + S.page_cls
            and (S.ack_mark is not None or mark not in E.strs_of(P, n6)),
            "CLICK: a tab that replaced this page -> no answer to the old page (%s %s)" % (None if p6 is None else p6.getClass().getSimpleName(), E.kinds(P, n6)))
    E.br.remove("hub:tab:%s:zzopen" % S.hub)
    r2, pg = openp(P)
    # a tab with only a command (another mod's, no Function): the command runs as the player
    E.br.put("hub:tab:%s:zzcmd" % S.hub, jpype.JArray(JClass("java.lang.Object"))(["SkyyTest", "Cmd tab", JClass("java.lang.Integer")(95), "zzfakecmd", None, None]))
    E.CM.lines.clear()
    n4 = len(E.sent(P))
    p4 = click(P, pg, "hub:zzcmd")
    K.check("zzfakecmd" in [str(x) for x in E.CM.lines], "CLICK: a command-only tab runs its command as the player (%s)" % list(E.CM.lines))
    K.check(same(p4, pg) and answered(n4), "CLICK: the command-only tab -> the page (still open: the command opens its page later) is answered")
    E.br.remove("hub:tab:%s:zzcmd" % S.hub)
    r2, pg = openp(P)
    # a missing tab and a hidden tab: the page stays and says it could not open
    for fake, entry in (("zzgone", None), ("zzhide", "hide")):
        if entry:
            E.br.put("hub:tab:%s:%s" % (S.hub, fake), jpype.JArray(JClass("java.lang.Object"))(["SkyyTest", "Hidden", JClass("java.lang.Integer")(96), "zzhidecmd", Rec(TRUE), Rec(FALSE)]))
        f0 = len(E.sent(P))
        p5 = click(P, pg, "hub:" + fake)
        txt = E.strs_of(P, f0)
        K.check(same(p5, pg) and S.fail_text in txt, "CLICK: a %s tab keeps the page and says it %s" % ("hidden" if entry else "missing", S.fail_text))
        if entry:
            E.br.remove("hub:tab:%s:%s" % (S.hub, fake))
    # < Menu: without SkyyMenu the page closes; with SkyyMenu /skymenu runs as the player
    E.br.remove("config:def:SkyyMenu")
    K.check(click(P, pg, "hub:back") is None, "CLICK: < Menu without SkyyMenu closes the page")
    r2, pg = openp(P)
    E.br.put("config:def:SkyyMenu", "x")
    E.CM.lines.clear()
    n5 = len(E.sent(P))
    p5b = click(P, pg, "hub:back")
    K.check("skymenu" in [str(x) for x in E.CM.lines], "CLICK: < Menu with SkyyMenu runs /skymenu (%s)" % list(E.CM.lines))
    K.check(same(p5b, pg) and answered(n5), "CLICK: < Menu -> the page (still open until the menu opens) is answered")
    E.br.remove("config:def:SkyyMenu")
    r2, pg = openp(P)
    K.check(click(P, pg, "hub:close") is None, "CLICK: the X closes the page")
    # the page's own clicks still work after the hub check (non-hub data reaches the page)
    for data, chk in S.clicks:
        r2, pg = openp(P)
        f0 = len(E.sent(P))
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, data))
        E.pump(P)
        chk(K, E, J, P, pg, P.pm.getCustomPage(), f0)

    # ---------------------------------------------------------------- DROP
    for t, *_x in others:
        E.br.remove("hub:tab:%s:%s" % (S.hub, t))
    E.br.put("hub:tab:%s:zzother" % S.hub, jpype.JArray(JClass("java.lang.Object"))(["SkyyOther", "Other", JClass("java.lang.Integer")(97), "x", None, None]))
    K.eq(int(drop_all(S, HB)), 1, "DROP: removeAll removed our one key")
    K.check(E.br.get(key) is None and E.br.get("hub:tab:%s:zzother" % S.hub) is not None, "DROP: our tab gone, another mod's tab kept")
    S.register(J)
    mine = E.br.get(key)
    E.br.put(key, jpype.JArray(JClass("java.lang.Object"))(["SkyyNewer", "X", JClass("java.lang.Integer")(1), "x", None, None]))
    K.eq(int(drop_all(S, HB)), 0, "DROP: a key another jar replaced is left alone")
    K.check(str(E.br.get(key)[0]) == "SkyyNewer", "DROP: the replacing jar's tab stays")
    E.br.remove(key)
    E.br.remove("hub:tab:%s:zzother" % S.hub)
    su = calls_of(jar, S.pkg + S.plugin_cls, "setup")
    sd = calls_of(jar, S.pkg + S.plugin_cls, "shutdown")
    K.check(S.register_call in su, "DROP: %s.setup calls %s (%s)" % (S.plugin_cls, S.register_call, sorted(x for x in su if "Hub" in x)))
    K.check(S.drop_call in sd, "DROP: %s.shutdown calls %s (%s)" % (S.plugin_cls, S.drop_call, sorted(x for x in sd if "Hub" in x)))
    if getattr(S, "extra_hub", None):
        S.extra_hub(K, W, J)
    K.save()


def run_live(S, out, jar, scratch, home):
    """D: two opens of the page on the scratch copy of the live data (the statics pointed at the copy): built + a click; no file written"""
    K = HK.Child(out)
    W = boot(scratch, jar, "live")
    E = W.E
    from jpype import JClass
    J = lambda n: JClass(S.pkg + n)
    HB = hub_of(S, J)
    E.br = HB.map()
    S.prep(E, J, home)
    if getattr(S, "live_prep", None):
        S.live_prep(E, J, home)
    h0 = HK.tree_hash(home)          # after the mod's own start-up loads (prep / live_prep): the page opens must write nothing
    X = W.P
    lp = S.live_player(home) if getattr(S, "live_player", None) else None
    if lp:
        X = W.mkp(E.UUID.fromString(lp[0]), lp[1])
        K.notes.append("D: the live copy's own player %s (%s)" % (lp[1], lp[0]))
    W.P = X
    for start in (1, 2):
        K.eq(int(S.register(J)), 1, "D%d: register on the live copy" % start)
        r = str(HB.open(W.P.pr, W.P.pr.getUuid(), S.hub, S.tab))
        E.pump(W.P)
        pg = W.P.pm.getCustomPage()
        K.check(r == "bridge" and pg is not None and str(pg.getClass().getName()) == S.pkg + S.page_cls, "D%d: the page opens on the live copy (%s)" % (start, r))
        if pg is not None:
            b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
            ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
            pg.build(W.P.ref, b, ev, W.P.st)
            cm = cmds_of(b)
            K.check(len(cm) > 10 and cm[0][2].startswith("Group #%s " % S.prefix), "D%d: built from the live data (%d commands)" % (start, len(cm)))
            W.P.pm.handleLegacyCustomPageEvent(W.P.ref, W.P.st, E.CPE(E.CPT.Data, '{"a":"hub:%s"}' % S.tab))
            E.pump(W.P)
            W.P.pm.handleLegacyCustomPageEvent(W.P.ref, W.P.st, E.CPE(E.CPT.Data, '{"a":"hub:close"}'))
            E.pump(W.P)
        K.check(int(drop_all(S, HB)) == 1, "D%d: removeAll" % start)
        if getattr(S, "live_flush", None):
            S.live_flush(E, J)
        K.eq(HK.tree_hash(home), h0, "D%d: no file written in the live copy" % start)
    K.save()


def run(S):
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                want2 = sorted(["manifest.json"] + KIT_FILES + list(S.extra_entries))
                return self.check(sorted(got) == want2, "C: non-class entries changed = manifest.json + the 59 kit files%s (%d entries; extra %s)"
                                  % (" + " + ", ".join(S.extra_entries) if S.extra_entries else "", len(got), sorted(set(got) - set(want2))[:5]))
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    if HK.arg("--phase") == "kitbytes" and not S.kit_in_jar:
        K = HK.Child(HK.arg("--out"))
        files = SUI.kit_texture_files()
        with zipfile.ZipFile(S.jar) as z:
            names = z.namelist()
            mf = json.loads(z.read("manifest.json"))
        K.eq([n for n in names if "SkyyKit" in n or (not n.endswith(".class") and n != "manifest.json")], [],
             "C: no kit art and no other asset in the jar (SkyyCore ships the 59 Sky Window files)")
        K.check(mf.get("Version") == S.version and mf.get("Name") == S.name and mf.get("IncludesAssetPack") is False
                and (mf.get("Dependencies") or {}).get("Skyy:SkyyCore") == ">=1.0.0 <2.0.0",
                "C: manifest %s %s: stable name, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0 (%s)" % (mf.get("Name"), mf.get("Version"), mf.get("Dependencies")))
        import skyybuild as _B
        with zipfile.ZipFile(_B.core_jar()) as z:
            K.check(all(z.read(p) == d for p, d in files.items()), "C: SkyyCore's jar carries the 59 kit files the page names (the kit's pinned bytes)")
        K.save()
        return
    if HK.arg("--phase") == "kitbytes":
        K = HK.Child(HK.arg("--out"))
        files = SUI.kit_texture_files()
        with zipfile.ZipFile(S.jar) as z:
            for p, data in files.items():
                K.check(z.read(p) == data, "C: %s = the kit's pinned bytes" % p)
            mf = json.loads(z.read("manifest.json"))
            K.check(mf.get("Version") == S.version and mf.get("IncludesAssetPack") is True, "C: manifest %s, IncludesAssetPack %s" % (mf.get("Version"), mf.get("IncludesAssetPack")))
        try:
            K.eq(SUI.check_jar_kit(S.jar), 59, "C: check_jar_kit = 59 files")
        except Exception as e:
            K.check(False, "C: check_jar_kit: %s" % e)
        K.save()
        return
    live = (os.path.join(LIVE_ROOT, "Skyy_" + S.name), "Skyy_" + S.name)
    HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
           phases=[("kitbytes", lambda out, jar, scratch, home: None),
                   ("hub", lambda out, jar, scratch, home: run_hub(S, out, jar, scratch)),
                   ("live", lambda out, jar, scratch, home: run_live(S, out, jar, scratch, home))] + list(S.extra_phases),
           script=S.script, live=live, removed=S.removed)
