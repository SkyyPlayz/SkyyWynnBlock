"""Harness for SkyyGuilds 0.1.11 (MENU PATTERN sweep S3: every view on the kit 1.7 hub_page - 1600 x 980, row 1 + row 2, the guild views'
ONE sub-tab row MEMBERS | BANK | BANK LOG, scroll lists that grow, no Back / pager; tools/guilds_0_1_11_patch.py) = the 0.1.10 harness
(tools/hub_tab_harness.py phases) with the kit 1.5 page check replaced by the KIT 1.7 one, compare 0.1.10 -> 0.1.11, plus:
  PAGE17  a guild made for the op; EVERY view built through the REAL builders and checked (check_page, kit paths, the root 1600 x 980,
          SUI.assert_menu_page on the REAL commands: rows 1 + 2, ONE sub row on the guild views / none on 'not in a guild', no kit 1.5
          bar, no back / < Menu text, no pager; every b.set / binding names an element): Members (Leader, Admin, Member), Bank (Leader /
          Member), Bank log (empty, with moves, past 200 moves), not in a guild (with an invite waiting)
  SUB     the sub row = the kit's sub_tab_markup byte for byte, the selected one unbound, the others bound members / bank / expand; the
          clicks switch the view; the old 'back' still opens Members; no #SkyyGNav / #SkyyGBack / #SkyyGExpand / #SkyyGBottom any more
  GROW    MEM_HS / LOG_HS = the kit's grow_row_sizes; HubBar.growSize = SUI.grow_pick for 1-40 rows; the built rows have the picked height
          (1 member = 80 px, 7 = 58 px, 12 = 40 px; the log the same with 37 / 53 / 74)
  FLOW    on the page (handleDataEvent, as the client sends): invite x11 (+ accept), promote, kick (Sure twice), demote; deposit 500 = purse
          -500 / bank +500 / one log line (exactly once), withdraw 200; the limits; Leave armed (Click again); guild chat (GuildStore.chat);
          the log past 200 kept moves draws 200 + Show more, Show more draws the rest
  ROW1    with SkyyMenu's hub defs: row 1 Home runs /skymenu, row 1 Social keeps the page (answered), row 2 Guild keeps the page
  NAMES   the 0.1.10 NAMES phase (symbol names) on the 0.1.11 jar
Build first:
python tools/guilds_0_1_11_patch.py && python SkyyGuilds/build_skyyguilds_0.1.11.py

    python SkyyGuilds/test_skyyguilds_0.1.11.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 page, the sub row, the grown rows, the sky footer.
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.1.11"
PKG = "com.skyy.guilds."
PFX = "SkyyGuildF"
SUBS = [("Members", "members"), ("Bank", "bank"), ("Bank log", "expand")]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T10 = tmod("test_skyyguilds_0.1.10.py", "test_skyyguilds_0_1_10")
prep, live_player, names = T10.prep, T10.live_player, T10.names


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


LAST = {}


def page_check17(K, E, S, P, page, hb, what):
    """the KIT 1.7 page check (replaces hub_tab_harness.page_check, which checks the kit 1.5 bar); returns (cmds, events)"""
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    cmds = H.cmds_of(b)
    evs = H.events_of(ev)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, S.idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')] and {"Header", "HeaderOrnament", SUI.HUB_FRAME["social"], "Close"} <= set(els),
                "%s: the Sky Window paths, none leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    K.check(apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980); }" % S.prefix), "%s: the root #%s is 1600 x 980" % (what, S.prefix))
    inguild = JClass(S.pkg + "GuildStore").snapshot(P.pr.getUuid()) is not None
    want_subs = 1 if inguild else 0
    try:
        info = SUI.assert_menu_page(apps, hub=S.hub, what=what, sets=[(s, unq(d)) for s, d in sets], pager_ok=False)
        K.check(info["rows"] == 2 and info["subs"] == want_subs, "%s: assert_menu_page (1600 x 980, rows 1 + 2, %d sub row, no back / < Menu, no pager)" % (what, want_subs))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk or '"< Menu"' in mk], "%s: no kit 1.5 bar (no < Menu, no small tab strip)" % what)
    gone = [i for i in ("SkyyGNav", "SkyyGLNav", "SkyyGBack", "SkyyGExpand", "SkyyGBottom", "SkyyGPrev", "SkyyGNext", "SkyyGLPrev", "SkyyGLNext")
            if [mk for p, mk in apps if ("#%s " % i) in mk]]
    K.check(not gone, "%s: no pager / back / Expand / old footer row (%s)" % (what, gone))
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % S.prefix), "%s: the X = hub:close" % what)
    vis = [str(r[0]) for r in hb.tabs(S.hub, P.pr.getUuid())]
    tabs = [mk for p, mk in apps if p == S.prefix + "BigTabs" and mk.startswith("Button")]
    K.eq(len(tabs), len(vis), "%s: row 2 = one tab per visible Social tab %s" % (what, vis))
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (S.prefix, k)), "%s: row 2 tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in H.DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == S.tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, S.tab))
    LAST["apps"], LAST["sets"], LAST["evs"] = apps, dict((s, unq(d)) for s, d in sets), evs
    return cmds, evs


H.page_check = page_check17      # run_hub calls H.page_check: the kit 1.7 check from now on


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "GuildPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the guild page")


def extra_hub(K, W, J):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JInt
    E = W.E
    GS, HB, PG = J("GuildStore"), J("HubBar"), J("GuildPage")
    O = W.O
    u = O.pr.getUuid()
    Str, Long, TRUE, FALSE = JClass("java.lang.String"), JClass("java.lang.Long"), JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    # row 1 as SkyyMenu publishes it: hub:def:<hub> = {title, command, icon item} for Home + every hub
    for hid in SUI.HUB_ROW_IDS:
        title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
        cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
        E.br.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
    # stand-in SkyyCoins purses (coins:fn:get / take / add / flush / sameacct - the contract GuildStore 0.1.8 calls)
    PURSE = {}

    @JImplements("java.util.function.Function")
    class CGet:
        @JOverride
        def apply(self, o):
            return Long(PURSE.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class CTake:
        @JOverride
        def apply(self, o):
            k, n = str(o[0]), int(o[1])
            if PURSE.get(k, 0) < n:
                return FALSE
            PURSE[k] = PURSE.get(k, 0) - n
            return TRUE

    @JImplements("java.util.function.Function")
    class CAdd:
        @JOverride
        def apply(self, o):
            k, n = str(o[0]), int(o[1])
            PURSE[k] = PURSE.get(k, 0) + n
            return Long(PURSE[k])

    @JImplements("java.util.function.Function")
    class CFlush:
        @JOverride
        def apply(self, o):
            return JClass("java.lang.Integer")(0)

    @JImplements("java.util.function.Function")
    class CSame:
        @JOverride
        def apply(self, o):
            return FALSE
    for k_, f_ in (("get", CGet()), ("take", CTake()), ("add", CAdd()), ("flush", CFlush()), ("sameacct", CSame())):
        E.br.put("coins:fn:" + k_, f_)
    PURSE[str(u)] = 100000

    r = str(GS.create(u, "SkyyOp", "Harness Guild"))
    K.check(GS.snapshot(u) is not None, "PAGE17: a guild made for the op (%s)" % r)
    J("GuildHubOpen").register()
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    rr = str(HB.open(O.pr, u, "social", "guild"))
    E.pump(O)
    pg = O.pm.getCustomPage()
    K.check(rr == "bridge" and pg is not None and str(pg.getClass().getSimpleName()) == "GuildPage", "PAGE17: the guild page opens through the tab (%s)" % rr)

    def click(X, p, data):
        n0 = len(list(E.sent(X)))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, data))
        E.pump(X)
        return X.pm.getCustomPage(), E.strs_of(X, n0)

    def kids(apps, parent):
        return [mk for p_, mk in apps if p_ == parent]

    def bound(evs, sel):
        return [t for s_, t in evs if s_ == sel]

    def hgt(mk):
        m = re.search(r"Height: (\d+)", mk)
        return int(m.group(1)) if m else None

    def subrow(what, sel):
        apps, evs = LAST["apps"], LAST["evs"]
        btns = [mk for mk in kids(apps, PFX + "Sub") if mk.startswith("TextButton")]
        want = [SUI.sub_tab_markup(PFX, i, lab, i == sel) for i, (lab, _a) in enumerate(SUBS)]
        K.check(btns == want, "SUB %s: the sub row = MEMBERS | BANK | BANK LOG, the kit's sub_tab_markup byte for byte, %s selected" % (what, SUBS[sel][0]))
        okb = all((not bound(evs, "#%sSub%d" % (PFX, i))) if i == sel else any(('"%s"' % a) in t for t in bound(evs, "#%sSub%d" % (PFX, i)))
                  for i, (_l, a) in enumerate(SUBS))
        K.check(okb, "SUB %s: the selected sub-tab is unbound, the others bound members / bank / expand" % what)

    def rows_of(apps, parent, rx):
        return [mk for p_, mk in apps if p_ == parent and re.match(rx, mk)]

    # ---------------------------------------------------------------- GROW: the tiers
    MHS, LHS = [int(x) for x in PG.MEM_HS], [int(x) for x in PG.LOG_HS]
    K.eq(MHS, SUI.grow_row_sizes(482 - 8, 40, gap=3), "GROW: MEM_HS = the kit's grow_row_sizes for the 482 px member list (%s)" % MHS)
    K.eq(LHS, SUI.grow_row_sizes(547 - 8, 37, gap=3), "GROW: LOG_HS = the kit's grow_row_sizes for the 547 px log list (%s)" % LHS)
    bad = []
    for n in range(1, 41):
        for av, hs in ((474, MHS), (539, LHS)):
            if int(HB.growSize(n, av, JArray(JInt)(hs), 3)) != SUI.grow_pick(n, av, hs, gap=3):
                bad.append((n, av))
    K.check(not bad, "GROW: HubBar.growSize = SUI.grow_pick for 1-40 rows in both lists %s" % bad[:3])

    # ---------------------------------------------------------------- MEMBERS (the Leader alone)
    page_check17(K, E, S, O, pg, HB, "PAGE17 members (Leader alone)")
    subrow("members", 0)
    apps, st = LAST["apps"], LAST["sets"]
    sub = st.get("#SkyyGSub.Text", "")
    K.check(sub.startswith("Harness Guild") and "Guild level" in sub, "PAGE17 members: the guild name leads #SkyyGSub (%s)" % sub[:60])
    lw = [mk for mk in apps if False] + [mk for p_, mk in apps if mk.startswith("Group #SkyyGList ")]
    K.check(len(lw) == 1 and "TopScrolling" in lw[0] and "Height: 482" in lw[0], "PAGE17 members: ONE scroll list well, 482 high (%s)" % (lw[0][:90] if lw else None))
    r0 = rows_of(apps, "SkyyGList", r"Group #SkyyGRow\d+ ")
    K.check(len(r0) == 1 and hgt(r0[0]) == MHS[2], "GROW: 1 member = the biggest rows (%s px)" % (hgt(r0[0]) if r0 else None))
    K.check(st.get("#SkyyGInvHint.Text", "").startswith("Invite:") and [mk for p_, mk in apps if mk.startswith("TextButton #SkyyGInviteBtn ")],
            "PAGE17 members: the Leader has the invite box + Invite + the hint")
    # ---------------------------------------------------------------- FLOW: invites on the page
    others = []
    for k in range(11):
        X = W.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001%02d" % k), "HarnMate%d" % k)
        others.append(X)
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
        pg, txt = click(O, pg, json.dumps({"a": "invite", "@GInvite": "HarnMate%d" % k}))
        acc = str(GS.accept(X.pr.getUuid(), "HarnMate%d" % k))
        if k == 0:
            K.check("HarnMate0" in str(pg.info) and str(pg.info).startswith("+") and acc.startswith("+"),
                    "FLOW: Invite on the page -> the invite (%s); accept joins (%s)" % (str(pg.info)[:50], acc[:50]))
        if k == 5:
            page_check17(K, E, S, O, pg, HB, "PAGE17 members (7 members)")
            r7 = rows_of(LAST["apps"], "SkyyGList", r"Group #SkyyGRow\d+ ")
            K.check(len(r7) == 7 and all(hgt(m) == MHS[1] for m in r7), "GROW: 7 members = the middle rows (%s px)" % sorted(set(hgt(m) for m in r7)))
    snap = GS.snapshot(u)
    K.eq(len(snap[5]), 12, "FLOW: 12 members after 11 page invites + accepts")
    page_check17(K, E, S, O, pg, HB, "PAGE17 members (12 members, Leader)")
    apps, evs = LAST["apps"], LAST["evs"]
    r12 = rows_of(apps, "SkyyGList", r"Group #SkyyGRow\d+ ")
    K.check(len(r12) == 12 and all(hgt(m) == MHS[0] for m in r12), "GROW: 12 members = normal rows, the list scrolls (%s px)" % sorted(set(hgt(m) for m in r12)))
    K.check(not [mk for p_, mk in apps if "#SkyyGMore " in mk], "PAGE17 members: no Show more under 200 members")
    ids = [str(x) for x in pg.rowIds]
    ia = ids.index(str(others[0].pr.getUuid()))
    ib = ids.index(str(others[1].pr.getUuid()))
    K.check(bound(evs, "#SkyyGPro%d" % ia) and bound(evs, "#SkyyGKick%d" % ia) and bound(evs, "#SkyyGLead%d" % ia), "FLOW: the Leader's row actions are bound (Promote / Kick / Make leader)")
    pg, _t = click(O, pg, '{"a":"promote:%d"}' % ia)
    rk = dict((str(r_[0]), str(r_[2])) for r_ in GS.snapshot(u)[5])
    K.eq(rk.get(str(others[0].pr.getUuid())), "1", "FLOW: Promote on the page -> Admin")
    pg, t1 = click(O, pg, '{"a":"kick:%d"}' % ib)
    K.check(len(GS.snapshot(u)[5]) == 12 and "Sure" in str(pg.info), "FLOW: the first Kick only arms 'Sure' (nothing removed: %s)" % str(pg.info)[:60])
    page_check17(K, E, S, O, pg, HB, "PAGE17 members (a Kick armed)")
    K.check([mk for p_, mk in LAST["apps"] if mk.startswith("TextButton #SkyyGKick%d " % ib) and 'Text: "Sure"' in mk], "FLOW: the armed row shows Sure")
    pg, _t = click(O, pg, '{"a":"kick:%d"}' % ib)
    K.eq(len(GS.snapshot(u)[5]), 11, "FLOW: Kick twice on the page -> the member is removed")
    # an Admin's and a Member's own page
    for X, nm, rank in ((others[0], "Admin", 1), (others[2], "Member", 0)):
        HB.open(X.pr, X.pr.getUuid(), "social", "guild")
        E.pump(X)
        px = X.pm.getCustomPage()
        page_check17(K, E, S, X, px, HB, "PAGE17 members (%s)" % nm)
        sx = LAST["sets"]
        hint = sx.get("#SkyyGInvHint.Text", "")
        K.check((hint.startswith("Invite:") if rank else hint.startswith("Only the Leader")) and not [mk for p_, mk in LAST["apps"] if "#SkyyGDisband " in mk],
                "PAGE17 members (%s): the invite row by rank (%s), no Disband" % (nm, hint[:40]))
        pb, _t = click(X, px, '{"a":"bank"}')
        page_check17(K, E, S, X, px, HB, "PAGE17 bank (%s)" % nm)
        K.check(LAST["sets"].get("#SkyyGLimNo.Text", "").startswith("Only the Leader"), "PAGE17 bank (%s): the Leader sets the limits" % nm)
    # ---------------------------------------------------------------- BANK (the Leader): deposit / withdraw exactly once
    pg, _t = click(O, pg, '{"a":"bank"}')
    K.eq(int(pg.view), 2, "SUB: the BANK sub-tab -> the Bank view (view 2)")
    page_check17(K, E, S, O, pg, HB, "PAGE17 bank (Leader)")
    subrow("bank", 1)
    apps, st = LAST["apps"], LAST["sets"]
    K.check([mk for p_, mk in apps if mk.startswith("TextButton #SkyyGDep ")] and [mk for p_, mk in apps if mk.startswith("TextButton #SkyyGWd ")]
            and [mk for p_, mk in apps if mk.startswith("TextButton #SkyyGLimA ")], "PAGE17 bank (Leader): Deposit, Withdraw and the limit row")
    b0, p0, l0 = int(GS.snapshot(u)[3]), PURSE[str(u)], len(GS.snapshot(u)[6])
    pg, _t = click(O, pg, json.dumps({"a": "deposit", "@GAmount": "500"}))
    b1, p1, l1 = int(GS.snapshot(u)[3]), PURSE[str(u)], len(GS.snapshot(u)[6])
    K.check((b1 - b0, p0 - p1, l1 - l0) == (500, 500, 1), "FLOW: Deposit 500 on the page = bank +500, purse -500, one log line (%s)" % ((b1 - b0, p0 - p1, l1 - l0),))
    pg, _t = click(O, pg, json.dumps({"a": "amount", "@GAmount": "500"}))
    K.check((int(GS.snapshot(u)[3]), PURSE[str(u)]) == (b1, p1), "FLOW: Enter in the amount box moves nothing")
    pg, _t = click(O, pg, json.dumps({"a": "withdraw", "@GAmount": "200"}))
    K.check((int(GS.snapshot(u)[3]) - b1, PURSE[str(u)] - p1, len(GS.snapshot(u)[6]) - l1) == (-200, 200, 1), "FLOW: Withdraw 200 on the page = bank -200, purse +200, one log line")
    K.eq(int(pg.view), 2, "FLOW: the page stays on Bank after a bank move")
    pg, _t = click(O, pg, json.dumps({"a": "limmember", "@GLimit": "5k"}))
    K.eq(int(GS.snapshot(u)[12]), 5000, "FLOW: Set Member limit 5k on the page")
    page_check17(K, E, S, O, pg, HB, "PAGE17 bank (after the moves)")
    logl = [v for k_, v in LAST["sets"].items() if re.match(r"#SkyyGLog\d+\.Text", k_)]
    K.check(len(logl) == 3 and "set the Member daily limit" in logl[0], "PAGE17 bank: the newest moves in the well, newest first (%s)" % [x[:30] for x in logl])
    # ---------------------------------------------------------------- BANK LOG
    pg, _t = click(O, pg, '{"a":"expand"}')
    K.eq(int(pg.view), 1, "SUB: the BANK LOG sub-tab -> the log view (view 1)")
    page_check17(K, E, S, O, pg, HB, "PAGE17 bank log (3 moves)")
    subrow("bank log", 2)
    apps = LAST["apps"]
    lr = rows_of(apps, "SkyyGLList", r"Group #SkyyGLRow\d+ ")
    K.check(len(lr) == 3 and all(hgt(m) == LHS[2] for m in lr), "GROW: 3 log moves = the biggest log rows (%s px)" % sorted(set(hgt(m) for m in lr)))
    lw = [mk for p_, mk in apps if mk.startswith("Group #SkyyGLList ")]
    K.check(len(lw) == 1 and "TopScrolling" in lw[0] and "Height: 547" in lw[0], "PAGE17 bank log: ONE scroll list well, 547 high")
    J("GCfg").LOG_KEEP = 300
    PURSE[str(u)] = 10 ** 9
    for _k in range(205):
        GS.deposit(u, "SkyyOp", "1")
    n_log = len(GS.snapshot(u)[6])
    page_check17(K, E, S, O, pg, HB, "PAGE17 bank log (%d moves)" % n_log)
    apps, evs = LAST["apps"], LAST["evs"]
    lr = rows_of(apps, "SkyyGLList", r"Group #SkyyGLRow\d+ ")
    K.check(n_log == 208 and len(lr) == 200 and all(hgt(m) == LHS[0] for m in lr) and bound(evs, "#SkyyGLMore"),
            "FLOW: past 200 moves the log draws 200 normal rows + Show more (bound lmore) (%d kept, %d drawn)" % (n_log, len(lr)))
    pg, _t = click(O, pg, '{"a":"lmore"}')
    page_check17(K, E, S, O, pg, HB, "PAGE17 bank log (Show more)")
    lr = rows_of(LAST["apps"], "SkyyGLList", r"Group #SkyyGLRow\d+ ")
    K.check(len(lr) == n_log and not bound(LAST["evs"], "#SkyyGLMore"), "FLOW: Show more draws the rest (%d rows, no Show more)" % len(lr))
    J("GCfg").LOG_KEEP = 200
    # ---------------------------------------------------------------- SUB: back to Members; the old 'back'
    pg, _t = click(O, pg, '{"a":"members"}')
    K.eq(int(pg.view), 0, "SUB: the MEMBERS sub-tab -> Members (view 0)")
    pg.view = 1
    pg, _t = click(O, pg, '{"a":"back"}')
    K.eq(int(pg.view), 0, "SUB: the old 'back' click still opens Members")
    # ---------------------------------------------------------------- ROW1 / row 2 / the X
    n0 = len(list(E.sent(O)))
    p2, _t = click(O, pg, '{"a":"hub:h:social"}')
    _id = JClass("java.lang.System").identityHashCode
    K.check(p2 is not None and int(_id(p2)) == int(_id(pg)), "ROW1: row 1 Social keeps the guild page")
    K.check(("#%sTitle.Text" % PFX) in E.strs_of(O, n0), "ROW1: ... and answers it (hubAck)")
    E.CM.lines.clear()
    p3, _t = click(O, pg, '{"a":"hub:h:home"}')
    K.check("skymenu" in [str(x) for x in E.CM.lines], "ROW1: row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    p4, _t = click(O, p3 or pg, '{"a":"hub:guild"}')
    K.check(p4 is not None and str(p4.getClass().getSimpleName()) == "GuildPage", "ROW1: row 2 Guild keeps the guild page")
    pg = p4
    # ---------------------------------------------------------------- Leave armed / chat / not in a guild
    X = others[3]
    HB.open(X.pr, X.pr.getUuid(), "social", "guild")
    E.pump(X)
    px = X.pm.getCustomPage()
    px, t5 = click(X, px, '{"a":"leave"}')
    page_check17(K, E, S, X, px, HB, "PAGE17 members (Leave armed)")
    K.check([mk for p_, mk in LAST["apps"] if mk.startswith("TextButton #SkyyGLeave ") and 'Text: "Click again to leave"' in mk]
            and len(GS.snapshot(u)[5]) == 11, "FLOW: the first Leave only arms 'Click again to leave' (still a member)")
    px, t6 = click(X, px, '{"a":"leave"}')
    K.check(len(GS.snapshot(u)[5]) == 10 and GS.snapshot(X.pr.getUuid()) is None, "FLOW: Leave twice on the page -> left the guild")
    page_check17(K, E, S, X, px, HB, "PAGE17 not in a guild (after leaving)")
    K.check(not [mk for p_, mk in LAST["apps"] if p_ == PFX + "Sub" or ("#%sSub " % PFX) in mk], "PAGE17 not in a guild: no sub row")
    GS.invite(u, "SkyyOp", X.pr.getUsername())
    page_check17(K, E, S, X, px, HB, "PAGE17 not in a guild (an invite waiting)")
    K.check(bound(LAST["evs"], "#SkyyGAccept") and bound(LAST["evs"], "#SkyyGDecline") and "Invite to Harness Guild" in LAST["sets"].get("#SkyyGInvTxt.Text", ""),
            "PAGE17 not in a guild: the invite row (Accept / Decline bound)")
    px, _t = click(X, px, '{"a":"accept"}')
    K.check(GS.snapshot(X.pr.getUuid()) is not None, "FLOW: Accept on the page joins the guild")
    cr = GS.chat(u, "SkyyOp", "hello guild")
    K.check(cr is None or not str(cr).startswith("-"), "FLOW: guild chat (GuildStore.chat) answers (%s)" % cr)
    gen = open(os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'GUILD_PAGE_CHECKED = "([0-9a-f]{12})"', gen)
    data = zipfile.ZipFile(S.jar).read("com/skyy/guilds/SkyyGuildsPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "PAGE17: the built page id = GUILD_PAGE_CHECKED %s (the ready line)" % (m and m.group(1)))
    K.check("SUI.hub_shell(" not in gen and "SUI.pager(" not in gen and gen.count("SUI.hub_page(") == 1, "SCRIPT: no kit 1.5 hub_shell / pager; one hub_page builder")
    for k_ in list(E.br.keySet()):
        if str(k_).startswith("coins:fn:"):
            E.br.remove(k_)
    J("HubBar").removeAll()
    names(K, J, GS, O)


EXPECT_HUBBAR = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES"] + ["+m " + m for m in (     # the kit 1.7 members (row / sub / big / page)
    "bigLab", "bigRow", "bigRowFill", "bigTabLab", "bigTabsFill", "build2", "buildRow", "def4", "defOf", "defTab", "goHub", "growSize",
    "hasArt", "hostOf", "hostShown", "hostTab", "hubs", "iconOf", "okIcon", "okItem", "openSub", "page17", "pickTab", "putIcon", "putSub",
    "route", "rowLab", "rowStyle", "rowWidth", "selOf", "subIcon", "subTab", "subTabs", "tabBStyle", "tabLab", "titleOf")]

S = H.Spec(name="SkyyGuilds", version=VERSION, pkg=PKG, hub="social", tab="guild", mod="SkyyGuilds", open_cls="GuildHubOpen", vis_cls=None,
           page_cls="GuildPage", prefix=PFX, idp="SkyyG", plugin_cls="SkyyGuildsPlugin", register_call="GuildHubOpen.register",
           register=lambda J: J("GuildHubOpen").register(), prep=prep, live_player=live_player,
           clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyGuilds-0.1.10.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS3", "guilds", "harness"))), script=__file__,
           added=[],
           expect={"GuildPage": ["+<clinit>", "+f LOG_HS", "+f MEM_HS", "+f logCap", "+f memCap", "~c ", "+m buildBank", "~m build",
                                 "~m buildGuild", "~m buildLog", "~m buildNone", "~m handleDataEvent", "~m hubClick",
                                 "+m infoLabel", "-m infoLabel"],      # infoLabel(b) -> infoLabel(b, int iw): the footer width
                   "HubBar": EXPECT_HUBBAR,
                   "SkyyGuildsPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "GCfg": ["~m load"]})
H.KIT_FILES = []   # 0.1.10 -> 0.1.11: the 59 kit files are already in 0.1.10 (byte-equal), so only manifest.json changes

if __name__ == "__main__":
    H.run(S)
