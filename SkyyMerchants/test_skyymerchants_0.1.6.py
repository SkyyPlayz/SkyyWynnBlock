"""Harness for SkyyMerchants 0.1.6 (MENU PATTERN sweep S2: the Market > Merchants rumours page on the kit 1.7 hub page; tools/merchants_0_1_6_patch.py).
Build first: python tools/merchants_0_1_6_patch.py && python SkyyMerchants/build_skyymerchants_0.1.6.py

    python SkyyMerchants/test_skyymerchants_0.1.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.5 -> 0.1.6 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyMerchants, AA engine-access audit) with the PAGE check re-aimed at kit 1.7 (this
file's page_check17 replaces the kit 1.5 one: the shared harness still describes the 1.5 shell): the REAL page built into a REAL
UICommandBuilder / UIEventBuilder passes SUI.assert_menu_page (1600 x 980, row 1 + row 2 with Merchants selected, no sub row, no back /
< Menu / pager text, the content fits), check_page, check_sky_paths, every b.set / binding names an element that exists, the hub title in
the title bar, hub:last remembers the tab. Plus (as 0.1.5):
  VIS   MerchHubVis = MerchCfg.ON: the merchants switched off -> no Merchants tab
  PAGE  a world WITH zones: one line per zone = MerchCore.rumoursText (the /merchants lines), in order; the hint in the footer; a short
        list = a bigger row tier (rule 7; 40 lines = normal rows is a build-time check); a world without zones: the one "No traveling merchants" line
  CLICK the Merchants tab itself redraws; Refresh redraws; row 1: Home runs /skymenu (answered), the own hub (hub:h:market) redraws,
        another hub goes to its tab (its Function)
Exit code 1 on any failure.
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.1.6"
PKG = "com.skyy.merchants."


def page_check17(K, E, S, P, page, hb, what):
    """kit 1.7: build the page into REAL builders and check it as a hub page; returns (cmds, events)"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = H.cmds_of(b)
    evs = H.events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))

    def unq(d):
        try:
            v = json.loads(d)
        except Exception:
            return str(d)
        if isinstance(v, dict) and len(v) == 1:
            v = list(v.values())[0]
        return v if isinstance(v, str) else str(d)
    try:
        info = SUI.assert_menu_page(apps, hub=S.hub, what=what, sets=[(s, unq(d)) for s, d in sets])
        K.check(info["rows"] == 2 and info["subs"] == 0, "%s: assert_menu_page (1600 x 980, rows 1 + 2, no sub row, no back / < Menu / pager text, %d texts)" % (what, info["texts"]))
    except Exception as e:
        K.check(False, "%s: assert_menu_page: %s" % (what, e))
    try:
        SUI.check_page(apps, S.idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        K.check({"Header", "HeaderOrnament", "Close", SUI.HUB_FRAME[S.hub]} <= set(els), "%s: the Sky Window hub page (%s)" % (what, sorted(set(els))))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    K.check(apps[0][0] is None and apps[0][1].startswith("Group #%s " % S.prefix), "%s: the root is the hub page #%s" % (what, S.prefix))
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk], "%s: no kit 1.5 < Menu / tab strip" % what)
    barmk = [mk for p, mk in apps if p == S.prefix + "Bar" and "#%sTitle " % S.prefix in mk]
    K.check(len(barmk) == 1 and ('Text: "%s"' % SUI.hub_title_now(S.hub)) in barmk[0], "%s: the hub title %s in the title bar" % (what, SUI.hub_title_now(S.hub)))
    tabs = [mk for p, mk in apps if p == S.prefix + "BigTabs" and mk.startswith("Button")]
    n = len(list(hb.tabs(S.hub, P.pr.getUuid())))
    K.check(len(tabs) == n and n >= 1, "%s: row 2 = one big tab per visible %s tab (%d)" % (what, S.hub, n))
    labs = [mk for p, mk in apps if (p or "").startswith(S.prefix + "BigT") and p != S.prefix + "BigTabs" and mk.startswith("Label")]
    K.check(any(('Text: "%s"' % S.label) in mk for mk in labs), "%s: row 2 shows %s" % (what, S.label))
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % S.prefix), "%s: the X = hub:close" % what)
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in H.DECL_RE.finditer(mk))
    bs = [s for s, _t in evs if s]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == S.tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, S.tab))
    return cmds, evs


H.page_check = page_check17   # kit 1.7 (the shared harness's PAGE phase calls H.page_check)
H.KIT_FILES = []              # the 59 kit files are already in the 0.1.5 jar, byte-identical: C sees only manifest.json change (KITBYTES checks them)


def prep(E, J, home):
    from jpype import JClass
    J("MerchLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyMerchants")
    mods = os.path.dirname(home) if os.path.basename(home) == "Skyy_SkyyMerchants" else os.path.join(home, "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    J("MerchCfg").load(E.Paths.get(mods))
    J("MerchReg").DIR = E.Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "merchants"))


def vis_cases(K, E, J, vis, u):
    from jpype import JClass
    FALSE = JClass("java.lang.Boolean").FALSE
    J("MerchCfg").ON = False
    K.check(vis.apply(u) == FALSE and len(list(J("HubBar").tabs("market", u))) == 0, "VIS: merchants switched off -> no Merchants tab")
    K.eq(str(J("HubBar").open(None, u, "market", "merchants")), "hidden", "VIS: switched off -> HubBar.open answers hidden")
    J("MerchCfg").ON = True


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "MerchRumPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) redraws the rumours page")


def built(W, pg):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(W.P.ref, b, ev, W.P.st)
    cm = H.cmds_of(b)
    sets = []
    for ty, s, t, d in cm:
        if ty == "Set":
            v = json.loads(d)
            sets.append((s, str(v.get("0", v)) if isinstance(v, dict) else str(v)))
    return cm, sets


def extra_hub(K, W, J):
    import jpype
    from jpype import JClass, JImplements, JOverride
    E = W.E
    Z = J("MerchCfg").ZONES
    K.check(len(Z) > 0, "PAGE: the default config has zones (%d)" % len(Z))
    if len(Z) == 0:
        return
    wn = str(Z[0].world)
    pg = J("MerchRumPage")(W.P.pr, wn)
    cm, sets = built(W, pg)
    want = str(J("MerchCore").rumoursText(wn, JClass("java.lang.System").currentTimeMillis())).split("\n")
    got = [v for s, v in sets if s.startswith("#SkyyMcRL")]
    K.check(len(got) == len(want) and [g.split(":")[0] for g in got] == [w.split(":")[0] for w in want] and len(got) >= 1,
            "PAGE: a zone world shows one line per zone = /merchants (%d lines: %s)" % (len(got), [g[:30] for g in got]))
    K.check(all(any(s == "#SkyyMcRL%d.Text" % i for s, v in sets) for i in range(len(got))), "PAGE: the zone lines are #SkyyMcRL0..%d" % (len(got) - 1))
    K.check(any(s == "#SkyyMcRHint.Text" and "press F" in v for s, v in sets), "PAGE: the hint line (the footer)")
    hs = [int(x) for x in J("MerchRumPage").RHS]
    lines = [t for ty, s, t, d in cm if s == "#SkyyMcRList" and t and t.startswith("Label #SkyyMcRL")]
    hts = sorted(set(int(m.group(1)) for m in (re.search(r"Height: (\d+)", t) for t in lines) if m))
    K.check(len(lines) == len(got) and len(hts) == 1, "PAGE: every zone line is one row size (%s)" % hts)
    if len(got) <= 6:
        K.check(hts == [hs[2]] or hts == [hs[1]], "PAGE: rule 7 - %d lines = bigger rows (%s of %s)" % (len(got), hts, hs))
    pg2 = J("MerchRumPage")(W.P.pr, "no_such_world")
    cm2, s2 = built(W, pg2)
    s2l = [v for s, v in s2 if s == "#SkyyMcRL0.Text"]
    K.check(len(s2l) == 1 and "No traveling merchants roam this world" in s2l[0], "PAGE: a world without zones: the one no-merchants line")
    gen = open(os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION), encoding="utf8").read()
    K.check('if (r.equals("self")) { rebuild(); return; }' in gen and "HubBar.route(this.playerRef, data" in gen, "CLICK: route first; the Merchants tab itself redraws")
    # row 1 (kit 1.7): Home = /skymenu (answered), the own hub = redraw, another hub = its tab's Function
    P_ = W.P

    def click(a):
        P_.pm.handleLegacyCustomPageEvent(P_.ref, P_.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        E.pump(P_)
        return P_.pm.getCustomPage()
    HB = J("HubBar")
    K.eq(int(J("MerchHubOpen").register()), 1, "ROW1: the tab is put again (DROP removed it)")
    r = str(HB.open(P_.pr, P_.pr.getUuid(), "market", "merchants"))
    E.pump(P_)
    pgo = P_.pm.getCustomPage()
    K.check(r == "bridge" and pgo is not None and str(pgo.getClass().getSimpleName()) == "MerchRumPage", "ROW1: the page is open (%s)" % r)
    same = lambda a, b_: a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))
    E.br.put("hub:def:home", jpype.JArray(JClass("java.lang.Object"))(["Home", "skymenu", "Skyy_Menu", None]))
    E.br.put("hub:def:market", jpype.JArray(JClass("java.lang.Object"))(["Market", "market", "Skyy_Menu", None]))
    E.br.put("config:def:SkyyMenu", "x")
    E.CM.lines.clear()
    n0 = len(E.sent(P_))
    p1 = click("hub:h:home")
    K.check("skymenu" in [str(x) for x in E.CM.lines] and same(p1, pgo) and len(E.sent(P_)) > n0, "ROW1: Home runs /skymenu, the page is answered (%s)" % list(E.CM.lines))
    n1 = len(E.sent(P_))
    p2 = click("hub:h:market")
    K.check(same(p2, pgo) and len(E.sent(P_)) > n1, "ROW1: the own hub (Market) redraws this page")

    @JImplements("java.util.function.Function")
    class Rec:
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return JClass("java.lang.Boolean").TRUE
    rc = Rec()
    E.br.put("hub:def:storage", jpype.JArray(JClass("java.lang.Object"))(["Storage", "storage", "Skyy_Menu", "requip"]))
    E.br.put("hub:tab:storage:requip", jpype.JArray(JClass("java.lang.Object"))(["SkyyWardrobe", "Requip", JClass("java.lang.Integer")(20), "requip", rc, None]))
    click("hub:h:storage")
    K.check(rc.calls == [str(P_.pr.getUuid())], "ROW1: another hub (Storage) opens its default tab through its Function (%s)" % rc.calls)
    for k_ in ("hub:def:home", "hub:def:market", "hub:def:storage", "hub:tab:storage:requip", "config:def:SkyyMenu"):
        E.br.remove(k_)
    K.eq(int(HB.removeAll()), 1, "ROW1: removeAll removes our tab again")


S = H.Spec(name="SkyyMerchants", version=VERSION, pkg=PKG, hub="market", tab="merchants", mod="SkyyMerchants", open_cls="MerchHubOpen",
           vis_cls="MerchHubVis", page_cls="MerchRumPage", prefix="SkyyMcRF", idp="SkyyMc", plugin_cls="SkyyMerchantsPlugin",
           register_call="MerchHubOpen.register", register=lambda J: J("MerchHubOpen").register(), prep=prep, vis_cases=vis_cases,
           self_redraw=True, clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION))),
           old_jar=os.path.join(HERE, "SkyyMerchants-0.1.5.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS2", "wdmerch", "m016"))), script=__file__,
           added=[],
           expect={"HubBar": ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES", "+m bigLab", "+m bigRow", "+m bigRowFill", "+m bigTabLab", "+m bigTabsFill",
                              "+m build2", "+m buildRow", "+m def4", "+m defOf", "+m defTab", "+m goHub", "+m growSize", "+m hasArt", "+m hostOf",
                              "+m hostShown", "+m hostTab", "+m hubs", "+m iconOf", "+m okIcon", "+m okItem", "+m openSub", "+m page17", "+m pickTab",
                              "+m putIcon", "+m putSub", "+m route", "+m rowLab", "+m rowStyle", "+m rowWidth", "+m selOf", "+m subIcon", "+m subTab",
                              "+m subTabs", "+m tabBStyle", "+m tabLab", "+m titleOf"],   # kit 1.7 = only ADDED members (row / big / sub / page)
                   "SkyyMerchantsPlugin": ["~m setup"], "CfgFn": ["~m opExport"],   # the version string
                   "MerchRumPage": ["+f RHS", "~<clinit>", "~m build", "~m handleDataEvent"],
                   # MerchCfg.seed / applyAll + CfgRows <clinit>: the config.properties header names the version ("# SkyyMerchants 0.1.6 - ...")
                   "CfgRows": ["~<clinit>", "~m header"], "MerchCfg": ["~m applyAll", "~m seed"]})

if __name__ == "__main__":
    H.run(S)
