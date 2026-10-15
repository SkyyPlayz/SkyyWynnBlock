"""hub_tab_kit - the shared checks of the hub TAB harnesses (H3 rounds: one mod's page as a tab of a hub, kit skyyui 1.5,
tools/HUBS-CONTRACT.md). First used by the H3a Character-tab harnesses (SkyySkills 0.4.41, SkyyTrees 0.3.15, SkyyClasses 0.1.27,
SkyyPets 0.2.7, SkyyCollections 0.2.17, SkyyProfiles 0.1.14). Runs inside a harness_kit child JVM.

  allow_kit_entries()     the C compare phase: the non-class entries that changed = manifest.json + the 59 Sky Window kit files (call
                          at import time of the harness, when --phase compare)
  stage(scratch)          the SkyyMenu 0.3.19 harness's engine stand-ins (the REAL PageManager / WindowManager, a component store,
                          worlds, the Universe, a CommandManager that RECORDS command lines, a permissions provider; T19.engine) in a
                          -Xverify:all JVM with the server jar + javassist + the harness classes + the jar; returns E with E.mkp(uuid,
                          name) (a player known to Universe.getPlayer), E.bridge (skyy.bridge), E.pg(P) (the open page)
  build(page, P)          page.build(...) into a REAL UICommandBuilder / UIEventBuilder -> (cmds, events)
  page_check(...)         a built page checked as a hub page: markup rules + parents + no duplicate id (SUI.check_page), every texture a
                          kit SkyyKit element inside Common/UI/Custom (no ../), the Header + crest + the hub's Frame mood + < Menu inside
                          the title bar + the close X, the root size (assert_hub_page / assert_hub_fits, <= 1600 x 980), the body content
                          under the strip (used_height), one tab per visible registry tab at hub_tab_width (>= 110, 16 px labels that
                          shrink to 12), the active tab selected, the bindings hub:back / hub:close / hub:<tab>, every b.set and binding
                          names an element that exists (a missing one disconnects the client), hub:last remembers the tab
  reg_check(...)          hub:tab:<hub>:<tab> = Object[]{mod, label, Integer order, command, open Function of the class, visible}
  Fakes(E, hub)           stand-in tabs of OTHER mods in the same hub: "fnok" (open Function answers TRUE), "fnno" (FALSE -> the
                          command fallback), "hide" (visible FALSE), each recording its calls
  clicks(...)             the bar on an open page: its own tab (the caller's self check), a tab through its Function, a tab through
                          the command fallback (the line the CommandManager recorded), a hidden / missing tab (the page stays and says
                          it could not open), "< Menu" with SkyyMenu loaded (/skymenu ran) and without (closes), the X (closes)
"""
import os, re, importlib.util

import skyybuild as B
import harness_kit as HK
import skyyui as SUI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT_FILES = sorted(SUI.SKY_JAR_DIR + f[0] for f in SUI.SKY_FILES)
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")
WH_RE = re.compile(r"Anchor: \(Width: (\d+), Height: (\d+)\)")


def allow_kit_entries():
    """harness_kit's compare allows only manifest.json among the non-class entries: + the 59 kit files (byte-identical to the kit's)"""
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            return self.check(sorted(got) == sorted(["manifest.json"] + KIT_FILES),
                              "C: non-class entries changed = manifest.json + the 59 kit files (%d entries)" % len(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def t19():
    sp = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def stage(scratch, jar, extra_cp=()):
    from jpype import JClass
    hcls = os.path.join(scratch, "hcls_hub")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar] + list(extra_cp), verify=True)
    E = t19().engine(scratch, hcls)
    Sys = JClass("java.lang.System")
    br = Sys.getProperties().get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        Sys.getProperties().put("skyy.bridge", br)
    E.bridge = br
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    E.mkp = mkp
    E.pg = lambda P: P.pm.getCustomPage()
    E.TRUE, E.FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    def same(a, b_):
        if a is None or b_ is None:
            return a is None and b_ is None
        return int(Sys.identityHashCode(a)) == int(Sys.identityHashCode(b_))
    E.same = same
    return E


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


def build(page, P):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    return cmds_of(b), events_of(ev)


def hub_tabs(E, hub, u):
    from jpype import JClass
    return [str(x[0]) for x in JClass(E.HB).tabs(hub, u)]


def page_check(K, E, P, built, prefix, hub, tab, label, what, idp=None):
    """built = build(page, P); prefix = the hub shell's prefix (its root id); idp = the id prefix of every element (default prefix).
    Returns (w, h, sets {selector: data}, bindings [(selector, text)])."""
    cmds, evs = built
    idp = idp or prefix
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets (%s)" % (what, len(apps), len(sets),
            sorted(set(ty for ty, _s, _t, _d in cmds))))
    try:
        SUI.check_page(apps, idp)
        K.check(True, "%s: check_page" % what)
    except Exception as e:
        K.check(False, "%s: check_page (markup rules, parents, no duplicate id): %s" % (what, e))
    u = P.pr.getUuid()
    vis = hub_tabs(E, hub, u)
    try:
        els = SUI.check_sky_paths(apps)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
        need = {"Header", "HeaderOrnament", SUI.HUB_FRAME[hub], "Close", "Tertiary", "Tab_Selected"} | ({"Tab"} if len(vis) > 1 else set())
        K.check(need <= set(els), "%s: the Sky Window shell: Header + crest + %s + close X + < Menu + tabs (%s)" % (what, SUI.HUB_FRAME[hub], sorted(els)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    m = WH_RE.search(root)
    w, h = int(m.group(1)), int(m.group(2))
    strip = w - 2 * SUI.THEME_PAD["sky"]
    K.check(apps[0][0] is None and root.startswith("Group #%s " % prefix), "%s: the root is the hub shell #%s" % (what, prefix))
    try:
        SUI.assert_page_size(w, h)
        K.eq(SUI.assert_hub_page(w, h - SUI.HUB_BAR_H, old_title_h=0, hub=hub, pad=SUI.THEME_PAD["sky"]), (w, h),
             "%s: assert_hub_page %d x %d (fits 1080p)" % (what, w, h))
        K.check(SUI.assert_hub_fits(hub, strip) >= 110, "%s: assert_hub_fits %s in %d px (every contract tab of the hub)" % (what, hub, strip))
    except Exception as e:
        K.check(False, "%s: page size: %s" % (what, e))
    bid = [DECL_RE.search(mk).group(2) for p, mk in apps if p == prefix and "Anchor: (Top: 38)" in mk]
    K.check(len(bid) == 1, "%s: one body under the title bar (%s)" % (what, bid))
    if bid:
        try:
            used = SUI.used_height(apps, bid[0])
            K.check(used <= h - SUI.TITLE_H - 2 * SUI.THEME_PAD["sky"], "%s: the body content fits (strip + content %d <= %d)" % (
                what, used, h - SUI.TITLE_H - 2 * SUI.THEME_PAD["sky"]))
        except Exception as e:
            K.check(False, "%s: used_height: %s" % (what, e))
        first = [mk for p, mk in apps if p == bid[0]][:1]
        K.check(bool(first) and first[0].startswith("Group #%sHubTabs " % prefix), "%s: the tab strip is the body's FIRST child" % what)
    bar = [mk for p, mk in apps if p == prefix + "Bar"]
    K.check(any(("#%sHubMenu " % prefix) in mk and '"< Menu"' in mk for mk in bar), "%s: < Menu sits INSIDE the title bar #%sBar" % (what, prefix))
    K.check(any(("#%sTitle " % prefix) in mk and ('Text: "%s"' % SUI.HUB_DEFS[hub][0]) in mk for _p, mk in apps), "%s: the hub title %s" % (what, SUI.HUB_DEFS[hub][0]))
    K.check([p for p, mk in apps if ("#%sHubClose " % prefix) in mk] == [prefix], "%s: the close X in the root" % what)
    tabs = [mk for p, mk in apps if p == prefix + "HubTabs" and mk.startswith("TextButton")]
    K.eq(len(tabs), len(vis), "%s: one tab per visible tab %s" % (what, vis))
    tw = SUI.hub_tab_width(strip, max(1, len(vis)))
    K.check(all(("Width: %d, Height: 44" % tw) in mk and "ShrinkTextToFit: true" in mk and "MinShrinkTextToFitFontSize: 12" in mk
                and "FontSize: 16" in mk for mk in tabs) and tw >= 110, "%s: tabs %d px wide (>= 110), 16 px labels that shrink to 12" % (what, tw))
    sel = [mk for mk in tabs if "Tab_Selected" in mk]
    K.check(len(sel) == 1 and ('Text: "%s"' % label) in sel[0], "%s: the active tab %s is the selected one" % (what, label))
    bs = [s for s, _t in evs]
    K.check(any("hub:back" in t for s, t in evs if s == "#%sHubMenu" % prefix) and any("hub:close" in t for s, t in evs if s == "#%sHubClose" % prefix),
            "%s: < Menu = hub:back, the X = hub:close" % what)
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sHubT%d" % (prefix, k)), "%s: tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.bridge.get("hub:last:" + str(u))
    K.check(last is None or str(last.get(hub)) == tab, "%s: hub:last (when SkyyMenu made it) remembers %s -> %s" % (what, hub, tab))
    return w, h, dict((s, d) for s, d in sets), evs


def reg_check(K, E, hub, tab, mod, label, order, cmd, open_cls, visible_cls=None):
    from jpype import JClass
    e = E.bridge.get("hub:tab:%s:%s" % (hub, tab))
    Fn = JClass("java.util.function.Function")
    ok = e is not None and len(e) == 6 and str(e[0]) == mod and str(e[1]) == label and JClass("java.lang.Integer").class_.isInstance(e[2]) \
        and int(e[2]) == order and (str(e[3]) if e[3] is not None else None) == cmd and Fn.class_.isInstance(e[4]) \
        and str(e[4].getClass().getName()) == open_cls \
        and ((e[5] is not None and str(e[5].getClass().getName()) == visible_cls) if visible_cls else e[5] is None)
    K.check(ok, "REG: hub:tab:%s:%s = {%s, %s, %d, %s, %s, %s} (%s)" % (hub, tab, mod, label, order, cmd, open_cls.rsplit(".", 1)[-1],
                                                                       visible_cls or "null", None if e is None else [str(x) for x in e]))
    return e


class Fakes(object):
    """stand-in tabs of other mods in one hub (orders between / after the contract ones)"""

    def __init__(self, E, hub):
        from jpype import JClass, JImplements, JOverride, JArray, JObject
        self.calls = {"fnok": [], "fnno": [], "hide": []}
        me = self

        @JImplements("java.util.function.Function")
        class Fn:
            def __init__(self, k, ans):
                self.k, self.ans = k, ans

            @JOverride
            def apply(self, u):
                me.calls[self.k].append(str(u))
                return self.ans
        self.fns = [Fn("fnok", E.TRUE), Fn("fnno", E.FALSE), Fn("hide", E.FALSE)]
        Int = JClass("java.lang.Integer")
        rows = [("fnok", "Fn Ok", 91, "fakeok", self.fns[0], None), ("fnno", "Fn No", 92, "fakeno", self.fns[1], None),
                ("hide", "Hidden", 93, "fakehide", self.fns[1], self.fns[2])]
        self.keys = []
        for t, l, o, c, op, vis in rows:
            arr = JArray(JObject)([JClass("java.lang.String")("SkyyFake"), JClass("java.lang.String")(l), Int.valueOf(o),
                                   JClass("java.lang.String")(c), op, vis])
            k = "hub:tab:%s:%s" % (hub, t)
            E.bridge.put(k, arr)
            self.keys.append(k)
        self.E = E

    def remove(self):
        for k in self.keys:
            self.E.bridge.remove(k)


def clicks(K, E, P, open_page, hub, tab, what, fakes, self_check=None, fail_text=None, self_new=None):
    """the bar's clicks on a page open_page() opens (into P's page manager): returns nothing; checks as in the module docstring.
    self_check(page) -> bool after the own tab (the page stays); self_new(open page) -> bool instead when the own tab opens ANOTHER page
    (a sub-page's tab = back to the tab's main page); fail_text = the text the page shows when a tab could not open (searched in the
    sent page packets)."""
    u = str(P.pr.getUuid())

    def click(pg, a):
        n0 = len(E.sent(P))
        pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P), n0
    pg = open_page()
    K.check(pg is not None, "%s: the page is open" % what)
    if pg is None:
        return
    cur, _n = click(pg, "hub:" + tab)
    if self_new is not None:
        K.check(cur is not None and not E.same(cur, pg) and self_new(cur), "%s: its own tab opens the tab's main page" % what)
    else:
        K.check(E.same(cur, pg) and (self_check is None or self_check(pg)), "%s: its own tab keeps the page (the tab's main view)" % what)
    E.CM.lines.clear()
    for k in ("fnok", "fnno", "hide"):
        del fakes.calls[k][:]
    pg = open_page()
    cur, _n = click(pg, "hub:fnok")
    K.check(fakes.calls["fnok"] == [u] and not list(E.CM.lines), "%s: another tab opens through its bridge Function (called with the UUID, no command)" % what)
    pg = open_page()
    cur, _n = click(pg, "hub:fnno")
    K.check(fakes.calls["fnno"] == [u] and [str(x) for x in E.CM.lines] == ["fakeno"],
            "%s: a Function that answers FALSE -> the command fallback ran as the player (%s)" % (what, list(E.CM.lines)))
    E.CM.lines.clear()
    for k in ("fnok", "fnno", "hide"):
        del fakes.calls[k][:]
    for k, why in (("hide", "hidden"), ("nothere", "missing")):
        pg = open_page()
        cur, n0 = click(pg, "hub:" + k)
        txt = E.strs_of(P, n0)
        K.check(E.same(cur, pg) and not list(E.CM.lines) and (fail_text is None or fail_text in txt),
                "%s: a %s tab -> the page stays and says it could not open" % (what, why))
    K.check(bool(fakes.calls["hide"]) and not fakes.calls["fnno"], "%s: the hidden tab's visible Function was asked (its open Function never)" % what)
    pg = open_page()
    E.bridge.remove("config:def:SkyyMenu")
    cur, _n = click(pg, "hub:back")
    K.check(cur is None and not list(E.CM.lines), "%s: < Menu without SkyyMenu closes the page" % what)
    pg = open_page()
    E.bridge.put("config:def:SkyyMenu", "stand-in")
    cur, _n = click(pg, "hub:back")
    K.check([str(x) for x in E.CM.lines] == ["skymenu"], "%s: < Menu with SkyyMenu runs /skymenu as the player (%s)" % (what, list(E.CM.lines)))
    E.bridge.remove("config:def:SkyyMenu")
    E.CM.lines.clear()
    pg = open_page()
    cur, _n = click(pg, "hub:close")
    K.check(cur is None, "%s: the X closes the page" % what)
