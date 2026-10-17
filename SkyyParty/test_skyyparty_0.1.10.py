"""Harness for SkyyParty 0.1.10 (MENU PATTERN sweep S3: the party page on the kit 1.7 hub_page, 1600 x 980, rows 1 + 2, the kit footer, rows
that grow; tools/party_0_1_10_patch.py). Build first: python SkyyCore/build_skyycore_1.0.0.py (if its jar is missing),
python tools/party_0_1_10_patch.py && python SkyyParty/build_skyyparty_0.1.10.py

    python SkyyParty/test_skyyparty_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the SkyyCore jar on its class path (SKYY_HARNESS_CP). The OLD jar everywhere is the LIVE 0.1.9 (the SET pin).
  A        every class loads + initialises with -Xverify:all (Core on the class path)
  C        class compare 0.1.9 -> 0.1.10: added HubBar (the page's own kit 1.7 copy); changed exactly PartyPage (build, hubClick, the GROWHS
           tiers) - every other class byte-identical (PartyStore, PartyFn, PartyStats, every command, PartyAdmin, the plugin ...)
  KITBYTES no kit art in the jar; manifest = stable name SkyyParty 0.1.10, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0
  HUB      tools/hub_tab_harness.py on SkyyCore's HubBar (owner SkyyParty): REG / PAGE / CLICK / DROP + Refresh. PAGE = the KIT 1.7 check:
           the REAL built page: check_page, kit textures only, the root 1600 x 980, SUI.assert_menu_page on the REAL commands (rows 1 + 2, no
           sub row, no kit 1.5 bar, no back / < Menu text, no pager), the X = hub:close, row 2 one tab per visible Social tab, every b.set /
           binding names an element, hub:last; + a party of two (leader view: rows grown to 112, Kick on the member's row, the footer
           order Leave / Disband / Refresh / Close) and a party of 10 (normal 56 px rows, the list scrolls)
  D        two opens of the page on a scratch COPY of the live Skyy_SkyyParty (nothing written)
  (no KIT phase: both 0.1.9 and 0.1.10 run the Server Setup kit from SkyyCore, and CfgData / PartyAdmin / every command class are
           byte-identical in the class compare C)
  PAGE     text parity: the REAL PartyPage of each jar (alone, leader of two, member of two, Refresh, /partyadmin answers): every page
           TEXT (each b.set Text) and every non-hub binding the same in 0.1.9 and 0.1.10 (the layout changed on purpose)
  FEAT     the old features on the 0.1.10 page, clicked: invite by the typed name, the pending invite (Accept / Decline), accept, the stats
           (party:stats -> Health / Stamina / Mana texts + bars), promote, kick, leave, disband, Refresh, an unknown payload; the bridge keys
           SkyyHud reads (party:fn:members, party:leader:<uuid>, party:name:<uuid>); row 1 (with SkyyMenu's hub defs): another hub runs its
           command (answered), the own hub answers, Home runs /skymenu, the X closes; assert_menu_page after every click
  AA       engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.1.10"
PKG = "com.skyy.party."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyParty-0.1.9.jar")
CORE_JAR = os.path.join(ROOT, "SkyyCore", "SkyyCore-1.0.0.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS3", "party", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyParty")
_s = importlib.util.spec_from_file_location("tb0114", os.path.join(ROOT, "SkyyBank", "test_skyybank_0.1.14.py"))
TB = importlib.util.module_from_spec(_s)
_s.loader.exec_module(TB)          # SkyyBank 0.1.14's harness: kit_parity / page_dump (sets SKYY_HARNESS_CP = Core)
os.environ["SKYY_HARNESS_CP"] = CORE_JAR
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")

EXPECT = {      # the class compare 0.1.9 -> 0.1.10
    "PartyPage": ["+<clinit>", "+f GROWHS", "+f confirm", "+f confirmUntil", "~m build", "~m handleDataEvent", "~m hubClick"],
                 # the kit 1.7 hub page (page17, growSize) + HubBar.route + the two-click Disband (critic fix)
    "SkyyPartyPlugin": ["~m setup"],                                      # the ready line (the version)
}


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


def built(P, page):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    return H.cmds_of(b), H.events_of(ev)


def page_check17(K, E, S, P, page, hb, what):
    """the KIT 1.7 page check (replaces hub_tab_harness.page_check, which checks the kit 1.5 bar)"""
    cmds, evs = built(P, page)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, S.idp)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    root = apps[0][1]
    K.check(apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980); }" % S.prefix), "%s: the root #%s is 1600 x 980" % (what, S.prefix))
    try:
        info = SUI.assert_menu_page(apps, hub=S.hub, what=what, sets=[(s, unq(d)) for s, d in sets], pager_ok=False)
        K.check(info["rows"] == 2 and info["subs"] == 0, "%s: assert_menu_page (1600 x 980, rows 1 + 2, no sub row, no back / < Menu, no pager)" % what)
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk or '"< Menu"' in mk], "%s: no kit 1.5 bar (no < Menu, no small tab strip)" % what)
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % S.prefix), "%s: the X = hub:close" % what)
    vis = [str(r[0]) for r in hb.tabs(S.hub, P.pr.getUuid())]
    tabs = [mk for p, mk in apps if p == S.prefix + "BigTabs" and mk.startswith("Button")]
    K.eq(len(tabs), len(vis), "%s: row 2 = one tab per visible Social tab %s" % (what, vis))
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (S.prefix, k)), "%s: row 2 tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    last = E.br.get("hub:last:" + str(P.pr.getUuid()))
    K.check(last is not None and str(last.get(S.hub)) == S.tab, "%s: hub:last remembers %s -> %s" % (what, S.hub, S.tab))
    return cmds, evs


H.page_check = page_check17      # run_hub calls H.page_check: the kit 1.7 check from now on


def prep(E, J, home):
    from jpype import JClass
    J("PartyStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyParty")


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "PartyPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the party page")


def row_heights(cmds):
    return [int(m.group(1)) for ty, s, t, d in cmds if t for m in [re.match(r"Group #SkyyPRow\d+ \{ Anchor: \(Height: (\d+)", t)] if m]


def foot_order(cmds):
    return [m.group(1) for ty, s, t, d in cmds if t and s == "#SkyyPFFoot" for m in [re.match(r"\s*(?:TextButton|Label) #(\w+)", t)] if m]


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    PS = J("PartyStore")
    PS.join(W.O.pr.getUuid(), W.P.pr.getUuid())
    lo = PS.listOf(W.O.pr.getUuid())
    K.check(lo is not None and int(lo.size()) == 2, "PAGE: a party of the two harness players (the op leads)")
    J("PartyHubOpen").register()
    HB = JClass("com.skyy.core.ui.HubBar")
    pg = J("PartyPage")(W.O.pr)
    W.O.pm.openCustomPage(W.O.ref, W.O.st, pg)
    E.pump(W.O)
    cm, evs = page_check17(K, E, S, W.O, pg, HB, "PAGE leader of two")
    K.check(cm[0][2].startswith("Group #SkyyPF { Anchor: (Width: 1600, Height: 980); }") and any(c[2] and "#SkyyPFBigTabs " in c[2] for c in cm),
            "PAGE: the leader's page is the kit 1.7 hub page")
    K.check(any(c[2] and "#SkyyPRow1 " in c[2] for c in cm) and any(c[2] and "#SkyyPKick1 " in c[2] for c in cm),
            "PAGE: the leader's member list (2 rows, Kick on the member's row)")
    K.eq(row_heights(cm), [112, 112], "PAGE: rule 7 - a party of two grows its rows to the 2x tier")
    K.eq(foot_order(cm), ["SkyyPInfo", "SkyyPLeave", "SkyyPDisband", "SkyyPRefresh", "SkyyPClose"], "PAGE: the footer = info line, Leave, Disband, Refresh, Close")
    ft = [t for _ty, s_, t, _d in cm if s_ == "#SkyyPFFoot"]
    k = next(i for i, t in enumerate(ft) if "#SkyyPDisband " in t)
    K.check(ft[k + 1].startswith("Group { Anchor: (Width: 40") and ft[k + 2].startswith("Group { Anchor: (Width: 10") and "#SkyyPRefresh " in ft[k + 3],
            "PAGE: a 50 px gap between Disband and Refresh (critic fix)")
    want = "Party 2 / %d players.  " % int(PS.MAX)
    K.check(any(c[1] and "SkyyPInfo" in c[1] and c[3] and want in str(c[3]) for c in cm), "PAGE: the info line leads with the party size + cap")
    # a party of 10 (the most maxSize allows): normal rows, the list scrolls
    mx = int(PS.MAX)
    PS.MAX = 10
    UUID = JClass("java.util.UUID")
    extra = [UUID.randomUUID() for _ in range(8)]
    for u in extra:
        PS.join(W.O.pr.getUuid(), u)
    cm10, _e = page_check17(K, E, S, W.O, pg, HB, "PAGE leader of ten")
    K.eq(row_heights(cm10), [56] * 10, "PAGE: rule 7 - a party of 10 keeps the normal 56 px rows (the list scrolls)")
    for u in extra:
        PS.removeMember(u)
    PS.MAX = mx
    data = zipfile.ZipFile(JAR).read("com/skyy/party/SkyyPartyPlugin.class")
    K.check(b"SkyyCore " in data, "PAGE: the ready line names the SkyyCore version")
    HB.removeAll("SkyyParty")


def party_scenario(K, W, E, J, HB, home):
    from jpype import JClass
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.join(home, "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyParty"), exist_ok=True)
    J("PartyStore").loadConfig(Paths.get(os.path.join(mods, "Skyy_SkyyParty")))
    J("CfgData").kit().start(Paths.get(mods), None)
    J("PartyHubOpen").register()
    dumps = []

    def page(nm, X):
        r = str(HB.open(X.pr, X.pr.getUuid(), "social", "party"))
        E.pump(X)
        pg = X.pm.getCustomPage()
        K.check(r == "bridge" and pg is not None, "PAGE %s opened through the hub bar (%s)" % (nm, r))
        b, ev = UCB(), UEB()
        pg.build(X.ref, b, ev, X.st)
        dumps.append((nm, H.cmds_of(b), H.events_of(ev)))
        n0 = len(E.sent(X))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"refresh"}'))
        E.pump(X)
        dumps.append((nm + " refresh", [[k] for k in E.kinds(X, n0)], []))
    page("alone", W.P)
    J("PartyStore").join(W.O.pr.getUuid(), W.P.pr.getUuid())
    page("leader of two", W.O)
    page("member of two", W.P)
    A = J("PartyAdmin")
    dumps.append(("partyadmin", [[str(A.status())], [str(A.set(W.O.pr, "maxSize", "7"))], [str(A.status())],
                                 [str(A.set(W.O.pr, "maxSize", "default"))], [str(A.reload(W.O.pr))], [str(A.status())]], []))
    return dumps


def texts_compare(out, scratch, a, b):
    """PAGE: 0.1.9 vs 0.1.10 - every b.set Text of the content (not the hub rows) and every non-hub binding the same, step by step"""
    K = HK.Child(out)
    da = json.load(open(os.path.join(scratch, "page-%s.json" % a)))
    db = json.load(open(os.path.join(scratch, "page-%s.json" % b)))
    K.eq([d[0] for d in db], [d[0] for d in da], "PAGE: the same scenario steps")
    for x, y in zip(da, db):
        if x[0].endswith(" refresh") or x[0] == "partyadmin":
            K.check(x[1] == y[1], "PAGE %s: the same answers / packet kinds (%d)" % (x[0], len(x[1])))
            continue
        tx = lambda d: [(c[1], c[3]) for c in d[1] if c[0] == "Set" and c[1] and c[1].endswith(".Text") and not c[1].startswith("#SkyyPF")]
        bx = lambda d: sorted(tuple(e) for e in d[2] if "hub:" not in e[1])
        K.check(tx(x) == tx(y) and len(tx(x)) > 5, "PAGE %s: the same %d page texts (0.1.9) / %d (0.1.10)%s" % (
            x[0], len(tx(x)), len(tx(y)), "" if tx(x) == tx(y) else ": %s" % sorted(set(tx(x)) ^ set(tx(y)))[:4]))
        K.check(bx(x) == bx(y) and len(bx(x)) > 2, "PAGE %s: the same %d content bindings%s" % (
            x[0], len(bx(x)), "" if bx(x) == bx(y) else ": %s" % sorted(set(bx(x)) ^ set(bx(y)))[:4]))
    K.save()


def run_feat(out, jar, scratch, _home):
    import jpype
    from jpype import JClass
    K = HK.Child(out)
    W = H.boot(scratch, jar, "feat")
    E = W.E
    J = lambda n: JClass(PKG + n)
    HB = JClass("com.skyy.core.ui.HubBar")
    E.br = HB.map()
    home = os.path.join(scratch, "feat_home")
    os.makedirs(os.path.join(home, "Skyy_SkyyParty"), exist_ok=True)
    prep(E, J, home)
    PS = J("PartyStore")
    PS.loadConfig(JClass("java.nio.file.Paths").get(os.path.join(home, "Skyy_SkyyParty")))
    E.br.put("party:fn:members", J("PartyFn")())
    K.eq(int(J("PartyHubOpen").register()), 1, "FEAT: the Party tab is put")
    P, O = W.P, W.O
    pu, ou = P.pr.getUuid(), O.pr.getUuid()
    for X in (P, O):
        E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())

    def open_(X):
        r = str(HB.open(X.pr, X.pr.getUuid(), "social", "party"))
        E.pump(X)
        return X.pm.getCustomPage(), r

    def click(X, d):
        n0 = len(E.sent(X))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, json.dumps(d)))
        E.pump(X)
        return X.pm.getCustomPage(), n0

    def texts(X, pg):
        cm, ev = built(X, pg)
        return dict((c[1], unq(c[3])) for c in cm if c[0] == "Set"), cm, ev

    def chk(X, pg, what):
        page_check17(K, E, S, X, pg, HB, "FEAT " + what)
    pgO, r = open_(O)
    K.check(pgO is not None and r == "bridge", "FEAT: the op opens the party page through the Party tab (%s)" % r)
    chk(O, pgO, "op alone")
    # invite by the typed name (Enter / the Invite button carry @InviteName)
    pgO, n = click(O, {"a": "invite", "@InviteName": "SkyyPlain"})
    inv = PS.INVITES.get(pu)
    K.check(inv is not None and str(inv[0]) == str(ou) and "Invited SkyyPlain" in str(pgO.info), "FEAT invite: the typed name invites SkyyPlain (%s)" % pgO.info)
    pgO, n = click(O, {"a": "invite", "@InviteName": "Nobody12"})
    K.check("Nobody called Nobody12" in str(pgO.info) and len(E.sent(O)) > n, "FEAT invite: an unknown name is answered on the page (%s)" % pgO.info)
    pgP, r = open_(P)
    st, cm, ev = texts(P, pgP)
    K.check(any(s == "#SkyyPAccept" for s, _t in ev) and "SkyyOp invited you" in str(st.get("#SkyyPPendTxt.Text")), "FEAT pending: the invite shows Accept / Decline (%s)" % st.get("#SkyyPPendTxt.Text"))
    chk(P, pgP, "invite pending")
    pgP, n = click(P, {"a": "decline"})
    K.check(PS.INVITES.get(pu) is None and PS.listOf(pu) is None and "Declined" in str(pgP.info), "FEAT decline: the invite is gone (%s)" % pgP.info)
    click(O, {"a": "invite", "@InviteName": "SkyyPlain"})
    pgP, n = click(P, {"a": "accept"})
    lo = PS.listOf(pu)
    K.check(lo is not None and int(lo.size()) == 2 and str(lo.get(0)) == str(ou) and "You joined" in str(pgP.info), "FEAT accept: SkyyPlain joins the op's party (%s)" % pgP.info)
    # the bridge keys SkyyHud reads
    mem = E.br.get("party:fn:members").apply(pu)
    K.check(mem is not None and len(mem) == 2 and str(mem[0]) == str(ou), "FEAT bridge: party:fn:members = [leader, member]")
    K.check(str(E.br.get("party:leader:" + str(pu))) == str(ou) and str(E.br.get("party:leader:" + str(ou))) == str(ou), "FEAT bridge: party:leader:<uuid> for both")
    K.check(E.br.get("party:name:" + str(pu)) is not None and str(E.br.get("party:name:" + str(ou))) == "SkyyOp", "FEAT bridge: party:name:<uuid> published")
    # stats: party:stats -> the row texts + bar fills
    E.br.put("party:stats:" + str(pu), "18,20,5,10,3,7,default")
    st, cm, ev = texts(O, pgO)
    K.check(st.get("#SkyyPHp1T.Text") == "Health  18 / 20" and st.get("#SkyyPSt1T.Text") == "Stamina  5 / 10" and st.get("#SkyyPMp1T.Text") == "Mana  3 / 7",
            "FEAT stats: the member's Health / Stamina / Mana texts (%s)" % [st.get("#SkyyPHp1T.Text"), st.get("#SkyyPSt1T.Text"), st.get("#SkyyPMp1T.Text")])
    K.check(any(s == "#SkyyPHp1B" and t and "Width: 144" in t for _ty, s, t, _d in cm), "FEAT stats: the Health bar fill 144 px (18 / 20 of 160)")
    pgO, n = click(O, {"a": "refresh"})
    chk(O, pgO, "leader after Refresh")
    # promote, kick, leave, disband (the leader's row actions + footer)
    pgO, n = click(O, {"a": "promote:" + str(pu)})
    K.check(str(PS.listOf(pu).get(0)) == str(pu), "FEAT promote: SkyyPlain leads now (%s)" % pgO.info)
    pgP, n = click(P, {"a": "kick:" + str(ou)})
    K.check(PS.listOf(ou) is None and PS.listOf(pu) is None, "FEAT kick: the new leader kicks the op (a party of one ends) (%s)" % pgP.info)
    click(O, {"a": "invite", "@InviteName": "SkyyPlain"})
    click(P, {"a": "accept"})
    pgP, n = click(P, {"a": "leave"})
    K.check(PS.listOf(pu) is None and PS.listOf(ou) is None, "FEAT leave: the member leaves (%s)" % pgP.info)
    click(O, {"a": "invite", "@InviteName": "SkyyPlain"})
    click(P, {"a": "accept"})
    K.check(PS.listOf(pu) is not None, "FEAT: the party again")
    # critic fix: Disband is two-click ("Click again to disband" within 10 s; any other click clears it)
    dis_txt = lambda X, pg: [t for _ty, s_, t, _d in built(X, pg)[0] if t and "#SkyyPDisband " in t]
    pgP, n = click(P, {"a": "disband"})
    K.check(PS.listOf(pu) is not None and "Only the party leader" in str(pgP.info), "FEAT disband: a member's click is refused at once (%s)" % pgP.info)
    pgO, n = click(O, {"a": "disband"})
    K.check(PS.listOf(ou) is not None and "again within 10 s" in str(pgO.info) and len(E.sent(O)) > n, "FEAT disband: the first click only arms (%s)" % pgO.info)
    K.check(any('"Click again to disband"' in t for t in dis_txt(O, pgO)), "FEAT disband: the armed button says Click again to disband")
    chk(O, pgO, "leader, Disband armed")
    pgO, n = click(O, {"a": "refresh"})
    K.check(PS.listOf(ou) is not None and any('"Disband party"' in t for t in dis_txt(O, pgO)), "FEAT disband: Refresh clears the armed Disband")
    pgO, n = click(O, {"a": "disband"})
    pgO, n = click(O, {"a": "hub:party"})
    pgO, n = click(O, {"a": "disband"})
    K.check(PS.listOf(ou) is not None and "again within 10 s" in str(pgO.info), "FEAT disband: a hub click clears it too (the next Disband only arms)")
    pgO.confirmUntil = 1
    pgO, n = click(O, {"a": "disband"})
    K.check(PS.listOf(ou) is not None and "again within 10 s" in str(pgO.info), "FEAT disband: after 10 s the second click only re-arms")
    pgO, n = click(O, {"a": "disband"})
    K.check(PS.listOf(pu) is None and PS.listOf(ou) is None and E.br.get("party:leader:" + str(pu)) is None, "FEAT disband: the second click within 10 s disbands, party:leader removed (%s)" % pgO.info)
    K.check(any('"Disband party"' in t for t in dis_txt(O, pgO)) is False, "FEAT disband: no Disband button once the party is gone")

    pgO, n = click(O, {"a": "zzz"})
    K.check(pgO is not None and len(E.sent(O)) > n, "FEAT: an unknown payload is answered")
    # row 1 (SkyyMenu's hub defs): every click routes through this jar's HubBar.route and is answered
    ObjA = lambda xs: jpype.JArray(JClass("java.lang.Object"))(xs)
    E.br.put("hub:def:home", ObjA(["Home", "skymenu", "Skyy_Menu", None]))
    for _h in SUI.HUBS:
        E.br.put("hub:def:" + _h, ObjA([SUI.hub_title_now(_h), "zz" + _h, "Skyy_Menu", None]))
    cm1, ev1 = page_check17(K, E, S, O, pgO, HB, "ROW1 party page (with SkyyMenu's hub defs)")
    rowb = [s for s, t in ev1 if s and s.startswith("#SkyyPFBig") and "hub:h:" in t]
    K.eq(len(rowb), 1 + len(SUI.HUBS), "ROW1: one row-1 button per hub + Home, each bound to hub:h:<id>")
    mark = "#SkyyPFTitle.Text"
    same = lambda a, b_: a is not None and b_ is not None and int(JClass("java.lang.System").identityHashCode(a)) == int(JClass("java.lang.System").identityHashCode(b_))
    for a, cmd, what in (("hub:h:market", "zzmarket", "another hub (no tab loaded) runs its hub command"), ("hub:h:social", None, "the page's own hub answers"),
                         ("hub:h:home", "skymenu", "Home runs /skymenu"), ("hub:party", None, "the page's own tab answers")):
        E.CM.lines.clear()
        p3, n = click(O, {"a": a})
        K.check(same(p3, pgO) and mark in E.strs_of(O, n) and (cmd is None or cmd in [str(x) for x in E.CM.lines]),
                "ROW1: %s, the page is answered (%s)" % (what, list(E.CM.lines)))
    p3, n = click(O, {"a": "close"})
    K.check(p3 is None, "FEAT: the footer Close closes the page")
    pgO, r = open_(O)
    p3, n = click(O, {"a": "hub:close"})
    K.check(p3 is None, "FEAT: the X closes the page")
    HB.removeAll("SkyyParty")
    K.save()


S = H.Spec(name="SkyyParty", version=VERSION, pkg=PKG, hub="social", tab="party", mod="SkyyParty", open_cls="PartyHubOpen", vis_cls=None,
           page_cls="PartyPage", prefix="SkyyPF", idp="SkyyP", plugin_cls="SkyyPartyPlugin", register_call="PartyHubOpen.register",
           register=lambda J: J("PartyHubOpen").register(), prep=prep, clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           hub_class="com.skyy.core.ui.HubBar", hub_owner="SkyyParty", kit_in_jar=False,
           added=["HubBar"], removed=[], expect=EXPECT,
           extra_phases=[
                         ("pageold", lambda out, jar, scratch, home: TB.page_dump(out, S, OLD_JAR, scratch, "old", True, party_scenario)),
                         ("pagenew", lambda out, jar, scratch, home: TB.page_dump(out, S, jar, scratch, "new", True, party_scenario)),
                         ("pagecmp", lambda out, jar, scratch, home: texts_compare(out, scratch, "old", "new")),
                         ("feat", run_feat)])

if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        # 0.1.9 -> 0.1.10: neither jar ships kit art, so only manifest.json changes (the hub harness's compare expects the H3 kit add)
        HK.run(name=S.name, version=S.version, jar=S.jar, old_jar=S.old_jar, pkg=S.pkg, scratch=S.scratch, expect=S.expect, added=S.added,
               phases=[], script=S.script, removed=S.removed)
    else:
        H.run(S)
